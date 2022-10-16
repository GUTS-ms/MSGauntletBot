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

def find_player_neighbors(x, y):
    neighb = []
    for i in range(-1,2):
        for j in range(-1,2):
            if i == 0 and j == 0:
                continue
            else:
                neighb.append((int((x+i)), int((y+j))))
    return neighb

msgFromClient       = "requestjoin:BestBot"
name = "BestBot"

bytesToSend         = str.encode(msgFromClient)

serverAddressPort   = ("127.0.0.1", 11000)

bufferSize          = 1024

#bunch of timers and intervals for executing some sample commands
moveInterval = 2
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
floor_connections = {}
botmap = np.full((100,100),0)
prev = None
floors_done = False


def SendMessage(requestmovemessage):
    bytesToSend = str.encode(requestmovemessage)
    UDPClientSocket.sendto(bytesToSend, serverAddressPort)

def heuristic(a, b):
        return np.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)




def make_step(posx,posy,botmap):
    start = (int(posy),int(posx))
    route = []
    best_coords = []
    for k in sorted(floor_connections, key=lambda k: len(floor_connections[k]), reverse=True):
            best_coords.append(k)
    counter = 0
    while route == []:
        goal = best_coords[counter]
        goal = (goal[1],goal[0])
        route = astar(botmap, start, goal)
        counter += 1

    route = route[::-1]
    print(route)
    x_coords = []
    y_coords = []

    for i in (range(1,len(route))):
        x = route[i][1]
        y = route[i][0]
        x_move_direction = int(posx - x)
        y_move_direction = int(posy - y)
        new_x_pos = int((posx*8) - (x_move_direction*8))
        new_y_pos = int((posy*8) - (y_move_direction*8))
        requestmovemessage = "moveto:" + str(int(new_x_pos))  + "," + str(int(new_y_pos))

        SendMessage(requestmovemessage)
        time.sleep(0.25)
        x_coords.append(x)
        y_coords.append(y)


        

    #fig, ax = plt.subplots(figsize=(20,20))

    #ax.imshow(botmap, cmap=plt.cm.Dark2)

    #ax.scatter(start[0],start[1], marker = "*", color = "yellow", s = 200)

    #ax.scatter(goal[0],goal[1], marker = "*", color = "red", s = 200)

    #ax.plot(x_coords,y_coords, color = "black")

    #plt.show()

def astar(array, start, goal):
    neighbors = [(0,1),(0,-1),(1,0),(-1,0)]
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
                data.append((current[1],current[0]))
                current = came_from[current]
            return data
        close_set.add(current)

        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            tentative_g_score = gscore[current] + heuristic(current, neighbor)
            if 0 <= neighbor[0] < array.shape[0]:
                if 0 <= neighbor[1] < array.shape[1]:                
                    if array[int(neighbor[1]),int(neighbor[0])] != 2:
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

def nearestX(num, x):
  d = num // x
  a = d * x
  b = a + x
  if b - num <= num - a:
    return b
  else:
    return a

while True:

    msgFromServer = UDPClientSocket.recvfrom(bufferSize)[0].decode('ascii')
    
    ##uncomment to see message format from server
    ##print(msgFromServer)
    if "playerupdate" in msgFromServer:
        pos = msgFromServer.split(":")[1]
        
        posSplit = pos.split(",")
        posx = round(float(posSplit[0]))
        posy = round(float(posSplit[1]))
        posx = nearestX(posx,8)
        posy = nearestX(posy,8)
        ammo = int(posSplit[2])

        if prev:
            if prev[0] != int(int(posy)/8) or prev[1] != int(int(posx)/8):
                botmap[int(int(posy)/8),int(int(posx)/8)]=8
                botmap[prev[0], prev[1]] = 2
                prev[0], prev[1] = int(int(posy)/8),int(int(posx)/8)
                # print("round: ")
                # print(int(int(posy) / 8), int(int(posx) / 8))
                # print("O G  : ")
                # print(int(posy), int(posx))
        else:
            botmap[int(int(posy)/8),int(int(posx)/8)]=8
        posxby8 = posx/8
        posyby8 = posy/8
        player_neighb = find_player_neighbors(posxby8,posyby8)

    if "nearbywalls" in msgFromServer:
        walls = msgFromServer.split(":")[1]
        wallsSplit = walls.split(",")
        wallcoords = []
        for i in range (0,len(wallsSplit)-1, 2):
            wallcoords.append((wallsSplit[i],wallsSplit[i+1]))
        for coords in wallcoords:
            if (int(coords[0]), int(coords[1])) not in seen_walls:
                seen_walls.append(coords)
                botmap[int(int(coords[1])/8),int(int(coords[0])/8)]=1
        

    if 'nearbyplayer' in msgFromServer:
        opponentx = msgFromServer.split(":")[1].split(',')[2]
        opponenty = msgFromServer.split(":")[1].split(',')[3]
        opponentx = nearestX(round(float(opponentx)), 8)
        opponenty = nearestX(round(float(opponenty)), 8)

        if (posx == opponentx) or (posy == opponenty) or (abs(posx-opponentx)==abs(posy-opponenty)):
            requestmovemessage = "moveto:" + str(int(opponentx))  + "," + str(int(opponenty))
            SendMessage(requestmovemessage)
       
            if ammo<2:
                fireMessage = "fire:"
                SendMessage(fireMessage)
                tempammo -= 1
            
        

    if "nearbyfloors" in msgFromServer:
        # print(msgFromServer)
        floors = msgFromServer.split(":")[1]
        floorsSplit = floors.split(",")
        floorscoords = []
        for i in range (0,len(floorsSplit)-1, 2):
            floorscoords.append((floorsSplit[i],floorsSplit[i+1]))
        for coords in floorscoords:
            if (int(coords[0]), int(coords[1])) not in seen_floors:
                seen_floors.append(coords)
                botmap[int(int(coords[1])/8),int(int(coords[0])/8)]=2
            if floors_done == False:
                coords_8 = (int(int(coords[1])/8),int(int(coords[0])/8))
                floor_connections[coords_8] = []
                for floortile in floor_connections.keys():
                    tile_neighbours_list = find_player_neighbors(floortile[0],floortile[1])
                    for neighbour in tile_neighbours_list:
                        if botmap[neighbour[0]][neighbour[1]] == 0:
                            if neighbour not in floor_connections[floortile]:
                                floor_connections[floortile].append(neighbour)
        floors_done = False
    now = time.time()

    #every few seconds, request to move to a random point nearby. No pathfinding, server will 
    #attempt to move in straight line.
    if (now - timeSinceMove) > moveInterval:
        plot(botmap)
        if floor_connections != {}:
            make_step(posyby8,posxby8,botmap)
        timeSinceMove = time.time()