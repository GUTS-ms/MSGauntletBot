import math
import socket
import time
import random
import numpy as np

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

def find_player_neighbors(posx, posy):
    neighb = []
    for i in range(-1,1):
        for j in range(-1,1):
            neighb.append((posx+i, posy+j))
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
        print(msgFromServer)
        walls = msgFromServer.split(":")[1]
        wallsSplit = walls.split(",")
        wallcoords = []
        for i in range (0,len(wallsSplit)-1, 2):
            wallcoords.append((wallsSplit[i],wallsSplit[i+1]))
        for coords in wallcoords:
            if coords not in seen_walls:
                if coords in find_player_neighbors(posxby8,posyby8):
                    seen_walls.append(coords)
                    botmap[int(int(coords[1])/8),int(int(coords[0])/8)]=1
        show(botmap)
        
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

    def make_step():
        #print(int(int(posy)/8),int(int(posx)/8))
        if botmap[(int(int(posy)/8))-1][int(int(posx)/8)] != 1:
            requestmovemessage = "moveto:" + str(posx - 8)  + "," + str(posy)
            SendMessage(requestmovemessage)
        elif botmap[int(int(posy)/8)][(int(int(posx)/8))-1] != 1:
            requestmovemessage = "moveto:" + str(posx)  + "," + str(posy-8)
            SendMessage(requestmovemessage)
        elif botmap[(int(int(posy)/8))+1][int(int(posx)/8)] != 1:
            requestmovemessage = "moveto:" + str(posx + 8)  + "," + str(posy)
            SendMessage(requestmovemessage)
        elif botmap[int(int(posy)/8)][(int(int(posx)/8))+1] != 1:
            requestmovemessage = "moveto:" + str(posx)  + "," + str(posy + 8)
            SendMessage(requestmovemessage)
        else:
            randomDirection = random.choice(directions)
            directionMoveMessage = "movedirection:" + randomDirection
            SendMessage(directionMoveMessage)
    now = time.time()

    #every few seconds, request to move to a random point nearby. No pathfinding, server will 
    #attempt to move in straight line.
    if (now - timeSinceMove) > moveInterval:
        find_unexp(botmap)
        make_step()
