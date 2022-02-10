import math
import random
import tkinter as tk
import time
import threading
from tKinterGrid import *

colors = []
colors.append(0) #Black
colors.append(Color(255, 0, 0)) #red
colors.append(Color(0,255,0)) #blue
colors.append(Color(0,0,255)) #green
colors.append(Color(200,200,0)) #yellow-green
colors.append(Color(255, 140, 10)) #orange
colors.append(Color(200, 200, 200)) #white
colors.append(Color(255, 0, 200)) #violet

redMask = 0xFF<<16
greenMask = 0xFF<<8 
blueMask = 0xFF

modeBtn = (0,0)

#util functions for drawing
def sumColors(a, b):
    rSum = min((a & redMask) + (b & redMask), redMask)
    gSum = min((a & greenMask) + (b & greenMask), greenMask)
    bSum = min((a & blueMask) + (b & blueMask), blueMask)
    return rSum + gSum + bSum 
def multColor(col, mult): # 
    rVal = min(int((col&redMask)  * mult), redMask  ) & redMask
    gVal = min(int((col&greenMask)* mult), greenMask) & greenMask
    bVal = min(int((col&blueMask) * mult), blueMask ) & blueMask
    return rVal+gVal+bVal    

def heatCol(amt):
    red = int(min(amt*1.5,255))
    green = max(2*amt-300,0)
    blue = int(max(255-2*amt,0)+green)
    return (red<<16)+(green<<8)+blue
def testHeat():
    for x in range(8):
        for y in range(8):
            drawPixel(x, y, heatCol(x*32))
def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)
lastKeys = []

# Define functions which animate LEDs in various ways.
def calcWavePoint(grid, point):
    """Adds the wave values for a specific seed point, outputing back to grid"""
    for y, row in enumerate(grid):
        for x, val in enumerate(row):
            err = math.sqrt((point[0]-x)**2+(point[1]-y)**2)-point[2]
            weightErr = .95-.8*err**2
            mult = max(0, max(min(weightErr,1),0))
            grid[y][x] = sumColors(val, multColor(point[3], mult)) #add the color, multiplied by ramping 

def wave():
    seedPoints = []
    drawInterval = 1/40

    while(True):
        nextDrawTime = time.time()+drawInterval
        pixelGrid = [[0 for x in range(8)] for y in range(8)] #8x8 grid, rgb vals for each pixel
        kDownEvents = readKeys()[0]

        if modeBtn in kDownEvents:
            return #go back to mode switch

        for key in kDownEvents:
            col = colors[random.randint(1,len(colors)-1)]
            seedPoints.append([key[0], key[1], 0.0, col]) ##add
            kDownEvents.remove(key)
        for i, seed in enumerate(seedPoints):
            if seed[2]>10:
                seedPoints.remove(seed)
                continue
            seedPoints[i][2] = seedPoints[i][2]*1.02+.05
            calcWavePoint(pixelGrid, seedPoints[i])
        drawGrid(pixelGrid)

        while(time.time()<nextDrawTime):
            pass
    
def pressCol():
    drawInterval = 1/40
    pixelGrid = [[0 for x in range(8)] for y in range(8)] #8x8 grid, color index for each pixel
    while(True):
        nextDrawTime = time.time()+drawInterval
        kDownEvents = readKeys()[0]
        if(modeBtn in kDownEvents):
            return
        for x,y in kDownEvents:
            colInd = colors.index(pixelGrid[y][x]) #get current col ind
            colInd = (colInd + 1)%len(colors) #increment color ind
            pixelGrid[y][x] = colors[colInd] #set new color
        
        drawGrid(pixelGrid)
        
        while(time.time()<nextDrawTime):
            pass    

def holdCol():
    """cycles through color wheel while button is held"""
    drawInterval = 1/40
    pixelGrid = [[0 for x in range(8)] for y in range(8)] #8x8 grid, rgb vals for each pixel
    while(True):
        nextDrawTime = time.time()+drawInterval
        
        heldKeys = readKeys()[1]
        if(modeBtn in heldKeys):
            return
        for x,y in heldKeys: #find new key presses
            pixelGrid[y][x] = (pixelGrid[y][x]+3)&255    
        for y, row in enumerate(pixelGrid):
                for x, val in enumerate(row):
                    drawPixel(x,y,multColor(wheel(val), .7))
        # strip.show()
        while(time.time()<nextDrawTime):
            pass


def heatMap():
    """Turns board into heatmap, pushing a button 'heats' it, then disperses to neighbors"""
    pixelGrid = [[0 for x in range(8)] for y in range(8)] #8x8 grid, rgb vals for each pixel
    #list of adjacent pixels for each pixel
    adjGrid = [[[] for __ in range(8)] for __ in range(8)]
    for y in range(8):
        for x in range(8):
            if(0<=x+1<8 and 0<=y<8):
                adjGrid[y][x].append((x+1,y))
            if(0<=x-1<8 and 0<=y<8):
                adjGrid[y][x].append((x-1,y))
            if(0<=x<8 and 0<=y+1<8):
                adjGrid[y][x].append((x,y+1))
            if(0<=x<8 and 0<=y-1<8):
                adjGrid[y][x].append((x,y-1))

    cHeatTrans = .15 #constant for heat transfer between cells
    cHeatLoss = 0.99   #heat lost per cell per loop
    cHeatAdd = .1    #heat added per button per loop
    
    drawInterval = 1/40
    while(True):
        nextDrawTime = time.time()+drawInterval
        
        heldKeys = readKeys()[1]
        if(modeBtn in heldKeys):
            return
        for x,y in heldKeys:
            pixelGrid[y][x] += cHeatAdd*(1000-pixelGrid[y][x])
        newGrid = pixelGrid.copy()
        
        #calculate heat transfer
        for y in range(8):
            for x in range(8):
                for ax, ay in adjGrid[y][x]:
                    newGrid[y][x] += cHeatTrans*(pixelGrid[ay][ax] - pixelGrid[y][x]) #weighted average with neighbor
                newGrid[y][x] *= cHeatLoss #gradually loose heat, to prevent saturation
                newGrid[y][x] = min(max(0,newGrid[y][x]),255)
                drawPixel(x,y,heatCol(round(newGrid[y][x])))
        pixelGrid = newGrid
        # strip.show()
        # for row in newGrid:
        #     print(" ".join(["{:02X}".format(int(round(i))) for i in row]))
        
        while(time.time()<nextDrawTime):
            pass
        
def simon():
    """Plays the simon game"""
    drawInterval = 1
    sColors = []
    sColors.append(Color(255, 0, 0)) #red
    sColors.append(Color(0,255,0)) #blue
    sColors.append(Color(0,0,255)) #green
    sColors.append(Color(200,200,0)) #yellow-green

    simonSequence = []
    grid4 = [(x,y) for y in range(4) for x in range(4)]
    print(grid4)
    restart = False
    while(True):
        nextDrawTime = time.time()+drawInterval

        simonSequence.append((random.randint(0,1), random.randint(0,1)))
        print(simonSequence)
        #showing the sequence
        for cx, cy in simonSequence:
            for x,y in grid4:
                drawPixel(cx*4 + x, cy*4 + y, sColors[cy*2+cx])
            # strip.show()
            time.sleep(1)
            setCol(c = 0)
            # strip.show()
            time.sleep(.5) 
        
        for cx, cy in simonSequence:
            #waiting for keypress
            while(True):
                keys = readKeys()[0]
                if(keys):
                    #lose if key not in right region
                    x,y = keys[0]
                    if(math.floor(x/4)!=cx or math.floor(y/4)!=cy):
                        restart = True
                        break
                    else: #move to next in sequence for correct keypress
                        for x,y in grid4:
                            drawPixel(cx*4 + x, cy*4 + y, sColors[cy*2+cx])
                        # strip.show()
                        while((x,y) in readKeys()[1]):
                            time.sleep(.1)
                        setCol(0)
                        # strip.show()
            if(restart): #break for cx...
                break
        if(restart):#restart game
            simonSequence = []
            
        while(time.time()<nextDrawTime):
            pass
def testKeys():
    while(True):
        print(readKeys())
        time.sleep(1)
def funcDispatch():
    print("Dispatch")
    mode = 0
    modes = [heatMap, wave, holdCol, pressCol]
    while(True):
        print("Entering mode {}".format(mode))
        modes[mode]()
        print("exit mode {}".format(mode))
        mode = (mode+1)%len(modes)
        setCol()
        cleanupGrid()
        time.sleep(1) 


if __name__ == '__main__':
    #init either board or tkinter
    startup()
    
