import pyautogui
from PIL import Image
import win32api, win32con
import time
import numpy as np

START_X = 670
START_Y = 273

GAMES = 1
gamesPlayed = 0

MAX_TRIES = 100
tries = 0

STEP_SIZE = 20

WIDTH = 30
HEIGHT = 16

TOTAL_BOMBS = 170
foundBombs = 0

# seconds
NO_CHANGE_TIMEOUT = 2

UNKNOWN_SQUARE = '.'
MINE_SQUARE = '*'

ORIGINAL_MOUSE_POSITION = pyautogui.position()


START_OPEN_X = 14
START_OPEN_Y = 7

latestopenX = START_OPEN_X
latestopenY = START_OPEN_Y

latestOpen = time.time()

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
board = [ [UNKNOWN_SQUARE]*HEIGHT for i in range(WIDTH)]
unknownAround = [[0]*HEIGHT for i in range(WIDTH)]
minesAround = [[0]*HEIGHT for i in range(WIDTH)]
hasOpened = [[False]*HEIGHT for i in range(WIDTH)]
remainder = [[9]*HEIGHT for i in range(WIDTH)]

productiveStepsIteration = 0

img = None

def getNumberAt(xCord, yCord):

    #convert to pixel cordinates
    x = START_X + xCord * STEP_SIZE
    y = START_Y + yCord * STEP_SIZE

    screen[x, y] = (0,0,0,0)

    # take 0 case in the end, start at 1
    for i in range(1, len(OFFSET)):
        if screen[x + OFFSET[i]['x'], y + OFFSET[i]['y']] == COLOR[i]:
            return i

    if screen[x + OFFSET[0]['x'], y + OFFSET[0]['y']] == COLOR[0]:
        return 0

    return UNKNOWN_SQUARE


def isOpen(xCord, yCord):
    x = START_X + xCord * STEP_SIZE
    y = START_Y + yCord * STEP_SIZE

    if screen[x + OFFSET[0]['x'], y + OFFSET[0]['y']] == COLOR[0]:
        return True
    return False

def getScreenshot():
    # move mouse out of the way
    time.sleep(1)
    win32api.SetCursorPos((1600, 2000))
    myScreenshot = pyautogui.screenshot()
    #myScreenshot.save(r'.\screen.png')
    img = myScreenshot
    image = myScreenshot.load()

    return myScreenshot

def click(x, y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)
    time.sleep(0.05)

def rightClick(x, y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,x,y,0,0)
    time.sleep(0.05)

def clickSquare(x, y):
    click(START_X + x*STEP_SIZE-5, START_Y + y*STEP_SIZE-5)

def openSquare(x,y):
    global productiveStepsIteration
    latestopenX = x
    latestopenY = y

    latestOpen = time.time()


    #print("opening square")
    if not hasOpened[x][y]:
        click(START_X + x*STEP_SIZE-5, START_Y + y*STEP_SIZE-5)
        hasOpened[x][y] = True
        productiveStepsIteration += 1

def markMine(x,y):
    global productiveStepsIteration
    global foundBombs
    rightClick(START_X + x*STEP_SIZE, START_Y + y*STEP_SIZE)
    board[x][y] = MINE_SQUARE

    productiveStepsIteration += 1

    for square in getSquaresAround(x,y):
        minesAround[square['x']][square['y']] += 1

    foundBombs += 1

def isInBound(x,y):
    if x > -1 and x < WIDTH and y > -1 and y < HEIGHT:
        return True
    return False

def addPossibleSquare(x,y,squares):
    if isInBound(x,y):
        squares.append({'x':x,'y':y})

def getUnknownSquaresAround(x,y):
    squaresAround = getSquaresAround(x,y)

    total = 0

    if False:

        print(" ")
        print("x",x)
        print("y",y)
        print("board", board[x][y])
        print(" ")

    for square in squaresAround:
        cellX = square['x']
        cellY = square['y']

        if False:
            print("cell x", cellX)
            print("cell y", cellY)
            print("board",  board[cellX][cellY])
            print(board[cellX][cellY] == UNKNOWN_SQUARE)

        if board[cellX][cellY] == UNKNOWN_SQUARE:
            total += 1

    return total


def markSimpleUnknown(x,y):
    squaresAround = getSquaresAround(x,y)

    total = getUnknownSquaresAround(x,y)

    if str(board[x][y]).isnumeric():
        # take into consideration the already marked mines
        boardValue = board[x][y] - minesAround[x][y]

        #print("total", total, " , board", board[x][y] )

        if total == boardValue and boardValue != 0:
            for square in squaresAround:
                cellX = square['x']
                cellY = square['y']
                if board[cellX][cellY] == UNKNOWN_SQUARE:
                    markMine(cellX, cellY)
    return total


def getSquaresAround(x,y):
    squares = []

    addPossibleSquare(x-1, y, squares)
    addPossibleSquare(x+1, y, squares)
    addPossibleSquare(x-1, y-1, squares)
    addPossibleSquare(x+1, y-1, squares)
    addPossibleSquare(x-1, y+1, squares)
    addPossibleSquare(x+1, y+1, squares)
    addPossibleSquare(x, y-1, squares)
    addPossibleSquare(x, y+1, squares)

    return squares

def printBoard():
    for j in range(HEIGHT):
        row = ""
        for i in range(WIDTH):
            row += " " + str(board[i][j])
        print(row)

def printUnknown():
    for j in range(HEIGHT):
        row = ""
        for i in range(WIDTH):
            row += " " + str(unknownAround[i][j])
        print(row)

def printRemainder():
    for j in range(HEIGHT):
        row = ""
        for i in range(WIDTH):
            row += " " + str(remainder[i][j])
        print(row)

def printState():
    print("")
    printBoard()
    print("")
    printUnknown()
    print("")
    printRemainder()
    print("")

def resetGame():
    global board
    global unknownAround
    global minesAround
    global hasOpened
    global remainder
    global tries


    click(750, 220)
    #click(750, 358) # HARD

    click(750, 338) # EASIER

    board = [[UNKNOWN_SQUARE]*HEIGHT for i in range(WIDTH)]
    unknownAround = [ [0]*HEIGHT for i in range(WIDTH)]
    minesAround = [ [0]*HEIGHT for i in range(WIDTH)]
    hasOpened = [ [False]*HEIGHT for i in range(WIDTH)]
    remainder = [[9]*HEIGHT for i in range(WIDTH)]
    tries = 0

while gamesPlayed < GAMES:
    gamesPlayed += 1

    time.sleep(2)
    resetGame()
    clickSquare(START_OPEN_X, START_OPEN_Y)
    time.sleep(1)

    screenshot = getScreenshot()
    screen = screenshot.load()

    productiveStepsIteration = 1
    while tries < MAX_TRIES and productiveStepsIteration > 0:
    #while time.time() - latestOpen < NO_CHANGE_TIMEOUT:
        productiveStepsIteration = 0
        tries += 1
        print("iteration: ", tries)

        screenshot = getScreenshot()
        screen = screenshot.load()

        printState()


        for x in range(WIDTH):
            for y in range(HEIGHT):
                if board[x][y] != '*':
                    board[x][y] = getNumberAt(x,y)

        for x in range(WIDTH):
            for y in range(HEIGHT):
                unknownAround[x][y] = getUnknownSquaresAround(x,y)

        for x in range(WIDTH):
            for y in range(HEIGHT):
                unknownAround[x][y] = markSimpleUnknown(x,y)

        for x in range(WIDTH):
            for y in range(HEIGHT):
                boardVal = board[x][y]

                if str(boardVal).isnumeric():
                    remainder[x][y] = boardVal - minesAround[x][y]
                elif unknownAround[x][y] == 0:
                    remainder[x][y] = ' '
                else:
                    remainder[x][y] = 9

        for x in range(WIDTH):
            for y in range(HEIGHT):
                #open if all mines are found
                if minesAround[x][y] == board[x][y] and board[x][y] != 0:
                    openSquare(x,y)
    printState()
# reset mouse to original position and click
click(ORIGINAL_MOUSE_POSITION[0], ORIGINAL_MOUSE_POSITION[1])

#screenshot.save('state.png')
