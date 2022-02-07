#!/usr/bin/env python3
# rpi_ws281x library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.

from asyncore import read
from math import floor
from pdb import Restart
import time 
from rpi_ws281x import *
import argparse
from neopixel import *
import digitalio
import adafruit_matrixkeypad
import board
import random




# LED strip configuration:
LED_COUNT      = 384       # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

cols = [digitalio.DigitalInOut(x) for x in (board.D23, board.D24, board.D25, board.D8, board.D7, board.D12, board.D16, board.D20)]
rows = [digitalio.DigitalInOut(x) for x in (board.D4, board.D17, board.D27, board.D22, board.D10, board.D6, board.D11, board.D5)]

#rows = [digitalio.DigitalInOut(x) for x in (board.D4, board.D17, board.D27, board.D22, board.D10, board.D9, board.D11, board.D5)]
keys = ((0, 1, 2, 3, 4, 5, 6, 7),
        (8, 9, 10, 11, 12, 13, 14, 15),
        (16, 17, 18, 19, 20, 21, 22, 23),      
        (24, 25, 26, 27, 28, 29, 30, 31),
        (32, 33, 34, 35, 36, 37, 38, 39),
        (40, 41, 42, 43, 44, 45, 46, 47),
        (48, 49, 50, 51, 52, 53, 54, 55),
        (56, 57, 58, 59, 60, 61, 62, 63))
# keys = ((x*8+y for y in range(8))for x in range(8)) #should replace above mess
keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)
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
def drawGrid(grid):
#     print()
    for y, row in enumerate(grid):
#         print(row)
        for x, val in enumerate(row):
            drawPixel(x,y,val)
    strip.show()
def drawPixel(x, y, c):
    tStart = y*48-x*3+45
    bStart = y*48+x*3
    strip.setPixelColor(bStart, c)
    strip.setPixelColor(bStart+1,c)
    strip.setPixelColor(bStart+2,c)
    strip.setPixelColor(tStart, c)
    strip.setPixelColor(tStart+1,c)
    strip.setPixelColor(tStart+2,c)
def setCol(c = 0, n = range(384)):
    for i in n:
        strip.setPixelColor(i, c)
    strip.show()
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
def readKeys():
    """Returns newly pressed keys, as well as all keys being held
    (List newKeys, List pressedKeys)"""
    global lastKeys
    keys = keypad.pressed_keys
    heldKeys = []
    for k in keys: #find new key presses
        heldKeys.append((k%8, int(k/8)))
    newKeys = [i for i in heldKeys if i not in lastKeys]
#     for x,y in keys: #find new key presses
#       if k not in lastKeys:
#         dx = k%8
#         dy = int(k/8)
#         kEvents.append((dx, dy))
    lastKeys = heldKeys
    return (newKeys, heldKeys)

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
        strip.show()
        while(time.time()<nextDrawTime):
            pass

def rainbow(wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    drawInterval = 1/40
    rainbowOffset = 0
    while(True):
        nextDrawTime = time.time()+drawInterval
        
        k = readKeys()[1]
        if(modeBtn in k):
            return
            
        rainbowOffset = (rainbowOffset + 2) & 0xFF
        for i in range(16):
            col = wheel((i*16+rainbowOffset) & 255)
            for j in range(24):
                strip.setPixelColor(i*24+j, col)
        strip.show()
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
        for y, row in enumerate(pixelGrid):
            for x, val in enumerate(pixelGrid):
                for ax, ay in adjGrid[y][x]:
                    newGrid[y][x] += cHeatTrans*(pixelGrid[ay][ax] - pixelGrid[y][x]) #weighted average with neighbor
                newGrid[y][x] *= cHeatLoss #gradually loose heat, to prevent saturation
                newGrid[y][x] = min(max(0,newGrid[y][x]),255)
                drawPixel(x,y,heatCol(round(newGrid[y][x])))
        pixelGrid = newGrid
        strip.show()
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
            strip.show()
            time.sleep(1)
            setCol(c = 0)
            strip.show()
            time.sleep(.5) 
        
        for cx, cy in simonSequence:
            #waiting for keypress
            while(True):
                keys = readKeys()[0]
                if(keys):
                    #lose if key not in right region
                    x,y = keys[0]
                    if(floor(x/4)!=cx or floor(y/4)!=cy):
                        restart = True
                        break
                    else: #move to next in sequence for correct keypress
                        for x,y in grid4:
                            drawPixel(cx*4 + x, cy*4 + y, sColors[cy*2+cx])
                        strip.show()
                        while((x,y) in readKeys()[1]):
                            time.sleep(.1)
                        setCol(0)
                        strip.show()
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
# Main program logic follows:
if __name__ == '__main__':
        
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()
    
    print ('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')
    print("Ready")
   
    mode = 0
    modeBtn = (0,0)
    modePressTime = 0
    modeLight = 0
    modes =  [pressCol, rainbow, wave, heatMap, holdCol, pressCol]
    try:
        while True:
            #drawing loop    
            #call mode function
            modes[mode]() 
            #clearing/incrementing mode
            setCol(0)
            drawPixel(modeBtn[1], modeBtn[0], 0xFFFFFF)
            strip.show()
            mode = (mode + 1) % len(modes)
            pixelGrid = [[0 for x in range(8)] for y in range(8)] #wipe pixel grid
            strip.show()
            time.sleep(1)
            
    except KeyboardInterrupt:
        #if args.clear:
        setCol()
