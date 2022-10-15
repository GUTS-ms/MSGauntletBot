import math
import socket
import time
import random
import numpy as np
import heapq

from mpltlibstyle import *

# function to find the start row and column
def find_start(x):
    start = x-1 if x-1 >= 0 else 0
    return start

# function to find the end row and column
def find_end(x, shape):
    end = x+1 if x+1 <= shape else shape
    return end

def find_neighbors(a, i, j):
    neighbors = []
    row_start, row_end = find_start(i), find_end(i, a.shape[0])
    col_start, col_end = find_start(j), find_end(j, a.shape[1])

    for y in range(a.shape[0]):
        for z in range(a.shape[1]):
            if y >= row_start and y <= row_end:
                if z >= col_start and z <= col_end:
                    neighbors.append((a[y][z],y,z))
    return neighbors

def find_unexp(arr):
    for pos, x in np.ndenumerate(arr):
        if x == 0:
            neighb=find_neighbors(arr, pos[0], pos[1])
            for y in neighb:
                if y[0] == 2:
                    print("found unexplored at " + str(y[1]) +" " + str(y[2]))
                    return (y[1], y[2])
    print("no unexplored found")

def find_player_neighbors(x, y):
    neighb = []
    for i in range(-1,1):
        for j in range(-1,1):
            neighb.append((x+i, y+j))
    return neighb

msgFromClient       = "requestjoin:mydisplayname"
name = "mydisplayname"

bytesToSend         = str.encode(msgFromClient)

serverAddressPort   = ("127.0.0.1", 11000)

bufferSize          = 1024

#bunch of timers and intervals for executing some sample commands
moveInterval = 5
timeSinceMove = time.time()

fireInterval = 5
timeSinceFire = time.time()

stopInterval = 30
timeSinceStop = time.time()

directionMoveInterval = 15
timeSinceDirectionMove = time.time()

directionFaceInterval = 9
timeSinceDirectionFace = time.time()

directions = ["n","s","e","w","nw","sw","ne","se"]


# Create a UDP socket
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Send to server using created UDP socket
UDPClientSocket.sendto(bytesToSend, serverAddressPort)

seen_walls=[]
seen_floors=[]
botmap = np.full((50,50),0)
prev = [0,0]
setup(botmap)


def SendMessage(requestmovemessage):
    bytesToSend = str.encode(requestmovemessage)
    UDPClientSocket.sendto(bytesToSend, serverAddressPort)

def heuristic(a, b):
        return np.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)

def make_step(posx,posy):
    start = (posy,posx)
    goal = (50,50)
    route = astar(botmap, start, goal)
    route = route + [start]
    route = route[::-1]
    print(route)
    x_coords = []
    y_coords = []

    for i in (range(0,len(route))):
        x = route[i][0]
        y = route[i][1]
        x_coords.append(x)
        y_coords.append(y)

        # plot map and path
    fig, ax = plt.subplots(figsize=(20,20))
    ax.imshow(botmap, cmap=plt.cm.Dark2)
    ax.scatter(start[1],start[0], marker = "*", color = "yellow", s = 200)
    ax.scatter(goal[1],goal[0], marker = "*", color = "red", s = 200)
    ax.plot(y_coords,x_coords, color = "black")
    plt.show()

def astar(array, start, goal):
    neighbors = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
    close_set = set()
    came_from = {}
    gscore = {start:0}
    fscore = {start:heuristic(start, goal)}
    oheap = []
    heapq.heappush(oheap, (fscore[start], start))

    while oheap:
        current = heapq.heappop(oheap)[1]
        if current == goal:
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            return data
        close_set.add(current)

        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            tentative_g_score = gscore[current] + heuristic(current, neighbor)
            if 0 <= neighbor[0] < array.shape[0]:
                if 0 <= neighbor[1] < array.shape[1]:                
                    if array[neighbor[0]][neighbor[1]] == 1:
                        continue
                else:
                    # array bound y walls
                    continue
            else:
                # array bound x walls
                continue
    
            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                continue

            if  tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1]for i in oheap]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(oheap, (fscore[neighbor], neighbor))

    return []

startcount = 0

while True:

    msgFromServer = UDPClientSocket.recvfrom(bufferSize)[0].decode('ascii')
    
    ##uncomment to see message format from server
    ##print(msgFromServer)
    if "playerupdate" in msgFromServer:
        pos = msgFromServer.split(":")[1]
        posSplit = pos.split(",")
        posx = round(float(posSplit[0]))
        posy = round(float(posSplit[1]))
        if startcount == 0:
            while(int(posx)%8 != 0):
                posx -= 1
            while(int(posy)%8 != 0):
                posy -= 1
            startcount += 1
            requestmovemessage = "moveto:" + str(posx)  + "," + str(posy)
            SendMessage(requestmovemessage)
        if prev[0] != int(int(posy)/8) or prev[1] != int(int(posx)/8):
            botmap[int(int(posy)/8),int(int(posx)/8)]=8
            botmap[prev[0], prev[1]] = 2
            prev[0], prev[1] = int(int(posy)/8),int(int(posx)/8)
            show(botmap)
            print("round: ")
            print(int(int(posy) / 8), int(int(posx) / 8))
            print("O G  : ")
            print(int(posy), int(posx))
        posxby8 = posx/8
        posyby8 = posy/8

    if "nearbywalls" in msgFromServer:
        walls = msgFromServer.split(":")[1]
        wallsSplit = walls.split(",")
        wallcoords = []
        for i in range (0,len(wallsSplit)-1, 2):
            wallcoords.append((wallsSplit[i],wallsSplit[i+1]))
        for coords in wallcoords:
            if coords not in seen_walls:
                seen_walls.append(coords)
                botmap[int(int(coords[1])/8),int(int(coords[0])/8)]=1
        # show(botmap)
        
    if "nearbyfloors" in msgFromServer:
        print(msgFromServer)
        floors = msgFromServer.split(":")[1]
        floorsSplit = floors.split(",")
        floorscoords = []
        for i in range (0,len(floorsSplit)-1, 2):
            floorscoords.append((floorsSplit[i],floorsSplit[i+1]))
        for coords in floorscoords:
            if coords not in seen_floors:
                if coords in find_player_neighbors(posxby8,posyby8):
                    seen_floors.append(coords)
                    botmap[int(int(coords[1])/8),int(int(coords[0])/8)]=2
        show(botmap)
    now = time.time()

    #every few seconds, request to move to a random point nearby. No pathfinding, server will 
    #attempt to move in straight line.
    if (now - timeSinceMove) > moveInterval:
        find_unexp(botmap)
        make_step(posyby8,posxby8)