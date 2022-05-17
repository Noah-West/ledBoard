import tkinter as tk
import threading

newKeys = []
heldKeys = []
keyLock = threading.Lock()
memGrid = [[0 for i in range(8)]for i in range(8)]


bttnGrid = [[]for i in range(8)]


def startup():
    global bttnGrid, canvas

    window = tk.Tk()
    window.title("YS LED Board Emulator")
    # window.geometry("400x400")

    bttnGrid = [[0 for x in range(8)] for y in range(8)]
    canvas = tk.Canvas(width=400, height=400, bg="blue")

    for y in range(8):
        for x in range(8):
            bttnGrid[x][y] = canvas.create_rectangle(
                x*50, (7-y)*50, x*50+50, (7-y)*50+50, fill='#000000', outline='#FFFFFF')
    canvas.bind("<Button-1>", lambda a: bttnPress(a))
    canvas.bind("<ButtonRelease-1>", lambda a: bttnRelease(a))
    canvas.pack()


def block():
    try:
        tk.mainloop()
    except KeyboardInterrupt:
        setCol()


def cleanupGrid():
    global heldKeys, newKeys
    with keyLock:
        heldKeys = []
        newKeys = []

# key input functions


def bttnPress(a):
    with keyLock:
        newKeys.append((7-int(a.y/50), int(a.x/50)))
        heldKeys.append((7-int(a.y/50), int(a.x/50)))


def bttnRelease(a):
    with keyLock:
        global heldKeys
        heldKeys = []


def readKeys():
    """Returns newly pressed keys, as well as all keys being held
    (List newKeys, List pressedKeys)"""
    with keyLock:
        global newKeys
        locNewKeys = newKeys
        newKeys = []
        return(locNewKeys, heldKeys)

# drawing functions


def drawGrid(grid):
    for y, row in enumerate(grid):
        for x, val in enumerate(row):
            drawPixel(x, y, val)
    stripShow()


def drawPixel(x, y, c):
    memGrid[y][x] = c

def setCol(c=0, n=range(384)):
    for x in range(8):
        for y in range(8):
            drawPixel(x, y, c)
    stripShow()


def stripShow():
    global canvas
    for y, row in enumerate(memGrid):
        for x, val in enumerate(row):
            canvas.itemconfigure(bttnGrid[y][x], fill="#{:06x}".format(val))

