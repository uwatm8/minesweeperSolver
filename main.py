import pyautogui
from PIL import Image
import win32api, win32con
import time
import numpy as np

START_X = 670
START_Y = 273

STEP_SIZE = 20

WIDTH = 30
HEIGHT = 16

UNKNOWN_SQUARE = " "
MINE = 10

ORIGINAL_MOUSE_POSITION = pyautogui.position()

# 0 = empty
OFFSET = {
    0: {'x':-5, 'y':-5},
    1: {'x':0, 'y':-4},
    2: {'x':1, 'y':0},
    3: {'x':1, 'y':0},
    4: {'x':1, 'y':0},
    5: {'x':1, 'y':0},
    6: {'x':1, 'y':0},
    7: {'x':1, 'y':0},
}

COLOR = {
    0: (218, 218, 218),
    1: (0,0,255),
    2: (51,149,51),
    3: (251,27,27),
    4: (61,61,153),
    5: (186,140,140),
    6: (110,173,173),
    7: (184,184,184),
}

print(" ")
print(" ------------------ STARTING SOLVER ------------------ ")


# solving: https://www.chiark.greenend.org.uk/~sgtatham/puzzles/js/mines.html#16x16n40#295541034604532
# type: 170 mines

# init with correct size
board = [ [-2]*HEIGHT for i in range(WIDTH)]

img = None

def getNumberAt(xCord, yCord):

    #convert to pixel cordinates
    x = START_X + xCord * STEP_SIZE
    y = START_Y + yCord * STEP_SIZE

    screen[x, y] = (0,0,0,0)

    for i in range(len(OFFSET)-1):
        # take 0 case in the end
        i=i+1

        if screen[x + OFFSET[i]['x'], y + OFFSET[i]['y']] == COLOR[i]:
            return i

    if screen[x + OFFSET[0]['x'], y + OFFSET[0]['y']] == COLOR[0]:
        return 0

    return UNKNOWN_SQUARE

def getScreenshot():
    # move mouse out of the way
    time.sleep(0.4)
    win32api.SetCursorPos((1600, 2000))
    myScreenshot = pyautogui.screenshot()
    myScreenshot.save(r'.\screen.png')
    img = myScreenshot
    image = myScreenshot.load()

    return myScreenshot
    #return image


def click(x, y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

def rightClick(x, y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,x,y,0,0)

def clickSquare(x, y):
    click(START_X + x*STEP_SIZE, START_Y + y*STEP_SIZE)

def markMine(x,y):
    rightClick(START_X + x*STEP_SIZE, START_Y + y*STEP_SIZE)

def printBoard():
    for j in range(HEIGHT):
        row = ""
        for i in range(WIDTH):
            row += " " + str(board[i][j])
        print(row)

def resetGame():
    click(750, 220)
    click(750, 358)


resetGame()
clickSquare(10,10)

screenshot = getScreenshot()
screen = screenshot.load()


for i in range(WIDTH):
    for j in range(HEIGHT):
        board[i][j] = getNumberAt(i,j)


printBoard()

# reset mouse to original position and click
click(ORIGINAL_MOUSE_POSITION[0], ORIGINAL_MOUSE_POSITION[1])


screenshot.save('state.png')
