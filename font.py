import time
import boardV2 as main

if(main.realGridSelect):
    import realGrid as grid
else:
    import tKinterGrid as grid
letters =  [[]for __ in range(27)]
letters[3] = [(2, 4), (1, 4), (0, 3), (0, 2), (0, 1), (2, 0), (1, 0)] #C
letters[8] = [(2, 4), (0, 4), (2, 3), (0, 3), (2, 2), (1, 2), (0, 2), (2, 1), (0, 1), (2, 0), (0, 0)] #H
letters[19] = [(2, 4), (1, 4), (0, 4), (2, 3), (2, 2), (1, 2), (0, 2), (0, 1), (2, 0), (1, 0), (0, 0)] #S
digits = [
    [(2, 4), (1, 4), (0, 4), (2, 3), (0, 3), (2, 2), (0, 2), (2, 1), (0, 1), (2, 0), (1, 0), (0, 0)],
    [(2, 4), (1, 4), (0, 4), (1, 3), (1, 2), (1, 1), (0, 1), (1, 0)],
    [(2, 4), (1, 4), (0, 4), (0, 3), (1, 2), (2, 1), (2, 0), (1, 0), (0, 0)],
    [(2, 4), (1, 4), (0, 4), (2, 3), (2, 2), (1, 2), (2, 1), (2, 0), (1, 0), (0, 0)],
    [(2, 4), (2, 3), (2, 2), (1, 2), (0, 2), (2, 1), (0, 1), (2, 0), (0, 0)],
    [(2, 4), (1, 4), (0, 4), (2, 3), (2, 2), (1, 2), (0, 2), (0, 1), (2, 0), (1, 0), (0, 0)],
    [(2, 4), (1, 4), (0, 4), (2, 3), (0, 3), (2, 2), (1, 2), (0, 2), (0, 1), (2, 0), (1, 0), (0, 0)],
    [(1, 4), (1, 3), (1, 2), (2, 1), (2, 0), (1, 0), (0, 0)],
    [(2, 4), (1, 4), (0, 4), (2, 3), (0, 3), (2, 2), (1, 2), (0, 2), (2, 1), (0, 1), (2, 0), (1, 0), (0, 0)],
    [(2, 4), (1, 4), (0, 4), (2, 3), (2, 2), (1, 2), (0, 2), (2, 1), (0, 1), (2, 0), (1, 0), (0, 0)]
]
def drawNum(num, col):
    """prints a 2 digit number to the screen in the specified color. Numbers are clamped to 0-99"""
    if(num>99):
        num = 99
    elif(num<0):
        num = 0
    for x,y in digits[int(num/10)]:
        grid.drawPixel(6-x, 7-y, col)
    for x,y in digits[num%10]:
        grid.drawPixel(2-x,7-y,col)
def drawString(str, col):
    """Draws a 1-2 char string to the grid."""
    if(len(str)>2):
        return
    if(len(str)==1):
        str = " " + str
    str = str.upper()
    for x,y in letters[ord(str[0])-0x40]:
        grid.drawPixel(6-x, 7-y, col)
    for x,y in letters[ord(str[1])-0x40]:
        grid.drawPixel(2-x,7-y,col)
def fontInput():
    """used to input new characters, enter them in top 5x3, (1,1) clears (one up and over from bottom left)"""
    drawInterval = 1/40
    pixelGrid = [[0 for x in range(8)] for y in range(8)] #8x8 grid, color index for each pixel
    while(True):
        nextDrawTime = time.time()+drawInterval
        kDownEvents = grid.readKeys()[0]
        if(main.modeBtn in kDownEvents):
            return
        if((1,1) in kDownEvents):
            k = []
            for y, row in enumerate(pixelGrid):
                for x, val in enumerate(row):
                    if(val != 0):
                        k.append((7-x,7-y))
            if((6,6) in k):
                k.remove((6,6))
            print(k)
            pixelGrid = [[0 for x in range(8)] for y in range(8)] #8x8 grid, color index for each pixel
        for x,y in kDownEvents:
            colInd = main.colors.index(pixelGrid[y][x]) #get current col ind
            colInd = (colInd + 1)%2 #increment color ind
            pixelGrid[y][x] = main.colors[colInd] #set new color
        grid.drawGrid(pixelGrid)
        while(time.time()<nextDrawTime):
            pass
def testDigits():
    """testing for digits, increments on click"""
    drawString("hs", main.colors[1])
    time.sleep(2)
    i = 0
    grid.setCol()
    while(True):
        drawNum(i, main.colors[1])
        keys = []
        while(not keys):
            keys = grid.readKeys()[0]
        if(main.modeBtn in keys):
            return
        i = (i + 1)
        grid.setCol()