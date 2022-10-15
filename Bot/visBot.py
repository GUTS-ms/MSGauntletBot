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
                    print("found unexplored at " + str(y[2]) +" " + str(y[1]))
                    return (y[2], y[1])
    print("no unexplored found")

def find_player_neighbors(x, y):
    neighb = []
    for i in range(-1,2):
        for j in range(-1,2):
            neighb.append((int((x+i)*8), int((y+j)*8)))
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

plotInterval = 5
timeSincePlot = time.time()

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
seen_items=[]
botmap = np.full((50,50),0)
prev = None


def SendMessage(requestmovemessage):
    bytesToSend = str.encode(requestmovemessage)
    UDPClientSocket.sendto(bytesToSend, serverAddressPort)

def heuristic(a, b):
        return np.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)

def make_step(posx,posy,next_move,botmap):
    start = (posy,posx)

    goal = next_move
    route = astar(botmap, start, goal)
    route = route + [start]
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
        print(new_x_pos)
        print(new_y_pos)
        requestmovemessage = "moveto:" + str(int(new_y_pos))  + "," + str(int(new_x_pos))
        #print(requestmovemessage)
        SendMessage(requestmovemessage)
        x_coords.append(x)
        y_coords.append(y)

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
                    if array[int(neighbor[0]),int(neighbor[1])] == 1:
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
                if (int(coords[0]), int(coords[1])) in player_neighb:
                    seen_walls.append(coords)
                    botmap[int(int(coords[1])/8),int(int(coords[0])/8)]=1
        
    if "nearbyfloors" in msgFromServer:
        # print(msgFromServer)
        floors = msgFromServer.split(":")[1]
        floorsSplit = floors.split(",")
        floorscoords = []
        for i in range (0,len(floorsSplit)-1, 2):
            floorscoords.append((floorsSplit[i],floorsSplit[i+1]))
        for coords in floorscoords:
            if (int(coords[0]), int(coords[1])) not in seen_floors:
                if (int(coords[0]), int(coords[1])) in player_neighb:
                    seen_floors.append(coords)
                    botmap[int(int(coords[1])/8),int(int(coords[0])/8)]=2

    # nearbyplayers

    # Warrior - Red == 16
    # Elf - Green == 17
    # Wizard - Yellow == 18
    # Valkyrie - Blue == 19

    if "nearbyplayer" in msgFromServer:
        players = msgFromServer.split(":")[1]
        playersSplit = players.split(",")
        playerCoords = []
        for i in range(0, len(playersSplit) - 1, 3):
            playerCoords.append([playersSplit[i], playersSplit[i + 1], playersSplit[i + 2]])
        for coords in playerCoords:
            if (int(coords[1]), int(coords[2])) in player_neighb:
                player = coords[0].lower()
                print("player is: " + player)
                if player == "warrior" or player == "red":
                    botmap[int(int(coords[1]) / 8), int(int(coords[2]) / 8)] = 16
                if player == "elf" or player == "green":
                    botmap[int(int(coords[1]) / 8), int(int(coords[2]) / 8)] = 17
                if player == "wizard" or player == "yellow":
                    botmap[int(int(coords[1]) / 8), int(int(coords[2]) / 8)] = 18
                if player == "valkyrie" or player == "blue":
                    botmap[int(int(coords[1]) / 8), int(int(coords[2]) / 8)] = 19

    # possible items
    # 3 == Treasure
    # 4 == Food
    # 5 == Ammo
    # 12 == redkey
    # 13 == greenkey
    # 14 == yellowkey
    # 15 == bluekey

    if "nearbyitem" in msgFromServer:
        items = msgFromServer.split(":")[1]
        itemsSplit = items.split(",")
        itemCoords = []
        for i in range(0, len(itemsSplit) - 1, 3):
            itemCoords.append([itemsSplit[i], itemsSplit[i + 1], itemsSplit[i + 2]])
        for coords in itemCoords:
            if (int(coords[1]), int(coords[2])) not in seen_items:
                if (int(coords[1]), int(coords[2])) in player_neighb:
                    seen_items.append((int(coords[1]), int(coords[2])))
                    item = coords[0].lower()
                    print("item is: " + item)
                    if item == "treasure":
                        botmap[int(int(coords[1]) / 8), int(int(coords[2]) / 8)] = 3
                    if item == "food":
                        botmap[int(int(coords[1]) / 8), int(int(coords[2]) / 8)] = 4
                    if item == "ammo":
                        botmap[int(int(coords[1]) / 8), int(int(coords[2]) / 8)] = 5
                    if item == "redkey":
                        botmap[int(int(coords[1]) / 8), int(int(coords[2]) / 8)] = 12
                    if item == "greenkey":
                        botmap[int(int(coords[1]) / 8), int(int(coords[2]) / 8)] = 13
                    if item == "yellowkey":
                        botmap[int(int(coords[1]) / 8), int(int(coords[2]) / 8)] = 14
                    if item == "bluekey":
                        botmap[int(int(coords[1]) / 8), int(int(coords[2]) / 8)] = 15
    now = time.time()

    #every few seconds, request to move to a random point nearby. No pathfinding, server will 
    #attempt to move in straight line.
    if (now - timeSinceMove) > moveInterval:
        next_move = find_unexp(botmap)
        plot(botmap)
        make_step(posyby8,posxby8,next_move,botmap)
        timeSinceMove = time.time()

    #if (now - timeSincePlot) > plotInterval:
    #    plot(botmap)
    #    timeSincePlot = time.time()