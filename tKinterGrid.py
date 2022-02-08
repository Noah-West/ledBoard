import time

def cleanup():
    setCol()
    global heldKeys, newKeys, keyLock
    with keyLock:
        heldKeys = []
        newKeys = []
    time.sleep(1) 

def bttnPress(a):
  with keyLock:
    global heldKeys, newKeys
    newKeys.append((int(a.x/50),int(a.y/50)))
    heldKeys.append((int(a.x/50),int(a.y/50)))
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