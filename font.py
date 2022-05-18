import time
import boardV2 as main

if(main.realBoard):
    import realGrid as grid
else:
    import tKinterGrid as grid


letters = [[]for __ in range(27)]
letters[3] = [(3, 2), (3, 1), (4, 0), (5, 0), (6, 0), (7, 2), (7, 1)]  # C
letters[8] = [(3, 2), (3, 0), (4, 2), (4, 0), (5, 2), (5, 1),
              (5, 0), (6, 2), (6, 0), (7, 2), (7, 0)]  # H
letters[19] = [(3, 2), (3, 1), (3, 0), (4, 2), (5, 2), (5, 1),
               (5, 0), (6, 0), (7, 2), (7, 1), (7, 0)]  # S
digits = [[(3, 2), (3, 1), (3, 0), (4, 2), (4, 0), (5, 2), (5, 0), (6, 2), (6, 0), (7, 2), (7, 1), (7, 0)],
          [(3, 2), (3, 1), (3, 0), (4, 1), (5, 1), (6, 1), (6, 0), (7, 1)],
          [(3, 2), (3, 1), (3, 0), (4, 0), (5, 1), (6, 2), (7, 2), (7, 1), (7, 0)],
          [(3, 2), (3, 1), (3, 0), (4, 2), (5, 2),
           (5, 1), (6, 2), (7, 2), (7, 1), (7, 0)],
          [(3, 2), (4, 2), (5, 2), (5, 1), (5, 0), (6, 2), (6, 0), (7, 2), (7, 0)],
          [(3, 2), (3, 1), (3, 0), (4, 2), (5, 2), (5, 1),
           (5, 0), (6, 0), (7, 2), (7, 1), (7, 0)],
          [(3, 2), (3, 1), (3, 0), (4, 2), (4, 0), (5, 2),
           (5, 1), (5, 0), (6, 0), (7, 2), (7, 1), (7, 0)],
          [(3, 1), (4, 1), (5, 1), (6, 2), (7, 2), (7, 1), (7, 0)],
          [(3, 2), (3, 1), (3, 0), (4, 2), (4, 0), (5, 2), (5, 1),
           (5, 0), (6, 2), (6, 0), (7, 2), (7, 1), (7, 0)],
          [(3, 2), (3, 1), (3, 0), (4, 2), (5, 2), (5, 1),
           (5, 0), (6, 2), (6, 0), (7, 2), (7, 1), (7, 0)]
          ]


def rotDigits():
    for i, digit in enumerate(letters):
        for j, coord in enumerate(digit):
            x, y = coord
            letters[i][j] = (7-y, x)
    print(letters)


def drawNum(num, col):
    """prints a 2 digit number to the screen in the specified color. Numbers are clamped to 0-99"""
    if(num > 99):
        num = 99
    elif(num < 0):
        num = 0
    for x, y in digits[int(num/10)]:
        grid.drawPixel(x-1, y+1, col)
    for x, y in digits[num % 10]:
        grid.drawPixel(x-1, y+5, col)


def drawString(str, col):
    """Draws a 1-2 char string to the grid."""
    if(len(str) > 2):
        return
    if(len(str) == 1):
        str = " " + str
    str = str.upper()
    for x, y in letters[ord(str[0])-0x40]:
        grid.drawPixel(x-1, y+1, col)
    for x, y in letters[ord(str[1])-0x40]:
        grid.drawPixel(x-1, y+5, col)


def fontInput():
    """used to input new characters, enter them in top 5x3, (1,1) clears (one up and over from bottom left)"""
    drawInterval = 1/40
    # 8x8 grid, color index for each pixel
    pixelGrid = [[0 for x in range(8)] for y in range(8)]
    while(True):
        nextDrawTime = time.time()+drawInterval
        kDownEvents = grid.readKeys()[0]
        if(main.modeBtn in kDownEvents):
            return
        if((1, 1) in kDownEvents):
            k = []
            for y, row in enumerate(pixelGrid):
                for x, val in enumerate(row):
                    if(val != 0):
                        k.append((7-x, 7-y))
            if((6, 6) in k):
                k.remove((6, 6))
            print(k)
            # 8x8 grid, color index for each pixel
            pixelGrid = [[0 for x in range(8)] for y in range(8)]
        for x, y in kDownEvents:
            colInd = main.colors.index(pixelGrid[y][x])  # get current col ind
            colInd = (colInd + 1) % 2  # increment color ind
            # set new color
            pixelGrid[y][x] = main.colors["red"] if colInd == 0 else 0
        grid.drawGrid(pixelGrid)
        while(time.time() < nextDrawTime):
            pass


def testDigits():
    """testing for digits, increments on click"""
    drawString("hs", main.colors["red"])
    grid.stripShow()
    time.sleep(2)
    rotDigits()
    i = 0
    grid.setCol()
    while(True):
        drawNum(i, main.colors["red"])
        grid.stripShow()
        keys = []
        while(not keys):
            keys = grid.readKeys()[0]
        if(main.modeBtn in keys):
            return
        i = (i + 1)
        grid.setCol()
