#!/usr/bin/env python3
# rpi_ws281x library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.

from math import floor
from rpi_ws281x import *
from neopixel import *
import digitalio
import adafruit_matrixkeypad
import board


# LED strip configuration:
LED_COUNT = 384       # Number of LED pixels.
LED_PIN = 18      # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
# True to invert the signal (when using NPN transistor level shift)
LED_INVERT = False
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

cols = [digitalio.DigitalInOut(x) for x in (
    board.D23, board.D24, board.D25, board.D8, board.D7, board.D12, board.D16, board.D20)]
rows = [digitalio.DigitalInOut(x) for x in (
    board.D4, board.D17, board.D27, board.D22, board.D10, board.D6, board.D11, board.D5)]
keys = ((0,  1,  2,  3,  4,  5,  6,  7),
        (8,  9, 10, 11, 12, 13, 14, 15),
        (16, 17, 18, 19, 20, 21, 22, 23),
        (24, 25, 26, 27, 28, 29, 30, 31),
        (32, 33, 34, 35, 36, 37, 38, 39),
        (40, 41, 42, 43, 44, 45, 46, 47),
        (48, 49, 50, 51, 52, 53, 54, 55),
        (56, 57, 58, 59, 60, 61, 62, 63))
keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)

# util functions


def startup():
    """Create NeoPixel object with appropriate configuration."""
    global strip, _run
    strip = Adafruit_NeoPixel(
        LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()


def block():
    """Block Thread until keyboard interrupt. TKinter needs this to start its GUI listener"""
    try:
        while(True):
            pass
    except KeyboardInterrupt:
        setCol()


def cleanupGrid():
    """Tidy up board variables"""
    pixelGrid = [[0 for x in range(8)] for y in range(8)]  # wipe pixel grid
    global lastKeys
    lastKeys = []

# functions for interfacing with drawing


def drawGrid(grid):
    """Writes RGB color values in <grid> to actual hardware"""
    for y, row in enumerate(grid):
        for x, val in enumerate(row):
            drawPixel(x, y, val)
    strip.show()


def drawPixel(x, y, c):
    """Writes RGB value to a specific pixel in the board buffer.
    stripShow MUST be called after to actually send colors to the board."""
    tStart = y*48-x*3+45
    bStart = y*48+x*3
    strip.setPixelColor(bStart, c)
    strip.setPixelColor(bStart+1, c)
    strip.setPixelColor(bStart+2, c)
    strip.setPixelColor(tStart, c)
    strip.setPixelColor(tStart+1, c)
    strip.setPixelColor(tStart+2, c)


def setCol(c=0, n=range(384)):
    for i in n:
        strip.setPixelColor(i, c)
    strip.show()


def stripShow():
    strip.show()


# get keypresses
lastKeys = []


def readKeys():
    """Returns newly pressed keys, as well as all keys being held
    (List newKeys, List pressedKeys)"""
    global lastKeys
    keys = keypad.pressed_keys
    # print(keys)
    heldKeys = []
    for k in keys:  # find new key presses
        heldKeys.append((k % 8, int(k/8)))
    newKeys = [i for i in heldKeys if i not in lastKeys]
    lastKeys = heldKeys
    return (newKeys, heldKeys)
