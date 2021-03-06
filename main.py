# check README for info

import pyautogui
from PIL import Image
import win32api, win32con
import time
import numpy as np
import autopy
import threading
import keyboard

#pyautogui.PAUSE = 0.0001
pyautogui.MINIMUM_DURATION = 0
pyautogui.MINIMUM_SLEEP = 0
pyautogui.PAUSE = 0

START_X = 670
START_Y = 273

GAMES = 10
gamesPlayed = 0

screenshotLock = False

MAX_TRIES = 75
tries = 0

STEP_SIZE = 20

WIDTH = 30
HEIGHT = 16

TOTAL_BOMBS = 170
foundBombs = 0

# seconds
NO_CHANGE_TIMEOUT = 1
daemonShouldStop = False

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
    2: {'x':1, 'y':-5},
    3: {'x':1, 'y':-4},
    4: {'x':1, 'y':0},
    5: {'x':1, 'y':0},
    6: {'x':1, 'y':0},
    7: {'x':1, 'y':0},
}

COLOR = {
    0: (218, 218, 218),
    1: (0,0,255),
    2: (26,139,26),
    3: (242,77,77),
    4: (61,61,153),
    5: (186,140,140),
    6: (110,173,173),
    7: (184,184,184),
}

print(" ")
print(" ------------------ STARTING SOLVER ------------------ ")



# init with correct size
board = [[UNKNOWN_SQUARE]*HEIGHT for i in range(WIDTH)]
nUnknownAround = [[0]*HEIGHT for i in range(WIDTH)]
minesAround = [[0]*HEIGHT for i in range(WIDTH)]
hasOpened = [[False]*HEIGHT for i in range(WIDTH)]
remainder = [[9]*HEIGHT for i in range(WIDTH)]
unknownAround = [[' ']*HEIGHT for i in range(WIDTH)]

allMatch = [[' ']*HEIGHT for i in range(WIDTH)]

productiveStepsIteration = 0

img = None

def screenshotDaemon(name):
    global screen
    global board

    print("STARTING SCREENSHOT DAEMON")

    while not daemonShouldStop:
        #print("Taking screenshot")
        if not screenshotLock:
            screen = getGreedyScreenshot().load()

    print("STOPPING SCREENSHOT DAEMON")

def getNumberAt(xCord, yCord):

    #convert to pixel cordinates
    x = START_X + xCord * STEP_SIZE
    y = START_Y + yCord * STEP_SIZE

    screen[x, y] = (0,0,0,0)

    isZero = False

    # take 0 case in the end, start at 1
    for i in range(1, len(OFFSET)):
        if screen[x + OFFSET[i]['x'], y + OFFSET[i]['y']] == COLOR[i]:
            return i


    if screen[x + OFFSET[0]['x'], y + OFFSET[0]['y']] == COLOR[0]:
        #print("returning 0")
        isZero = True

    # try again if 0 is found, due to async issues with screenshot daemon
    for i in range(1, len(OFFSET)):
        if screen[x + OFFSET[i]['x'], y + OFFSET[i]['y']] == COLOR[i]:
            print("ASYNC BULLSHIT")
            print("ASYNC BULLSHIT")
            print("ASYNC BULLSHIT")
            print("ASYNC BULLSHIT")
            print("ASYNC BULLSHIT")
            print("ASYNC BULLSHIT")
            print("ASYNC BULLSHIT")
            print("ASYNC BULLSHIT")
            print("ASYNC BULLSHIT")
            print("ASYNC BULLSHIT")
            print("ASYNC BULLSHIT")
            print("ASYNC BULLSHIT")
            return i

    if isZero:
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
    time.sleep(0.3)
    win32api.SetCursorPos((1600, 2000))
    myScreenshot = pyautogui.screenshot()
    #myScreenshot.save(r'.\screen.png')
    img = myScreenshot
    image = myScreenshot.load()

    return myScreenshot

def getGreedyScreenshot():
    myScreenshot = pyautogui.screenshot()

    return myScreenshot


def click(x, y):
    #win32api.SetCursorPos((x,y))
    #win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    #win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

    pyautogui.click(int(x),int(y))

def rightClick(x, y):
    #win32api.SetCursorPos((x,y))
    #win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,x,y,0,0)
    #win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,x,y,0,0)
    #time.sleep(0.011)
    pyautogui.rightClick(int(x),int(y))


def clickSquare(x, y):
    click(START_X + x*STEP_SIZE-5, START_Y + y*STEP_SIZE-5)

def shouldContinue():
    global latestOpen

    if keyboard.is_pressed('q'):
        exit()

    return time.time() - latestOpen < NO_CHANGE_TIMEOUT and tries < MAX_TRIES



def openSquare(x, y, markOpened):
    global latestOpen
    global productiveStepsIteration

    if not hasOpened[x][y]:
        if len(getUnknownSquaresAround(x,y)) > 0 or not markOpened:
            click(START_X + x*STEP_SIZE-5, START_Y + y*STEP_SIZE-5)

        latestOpen = time.time()

    if markOpened:
        productiveStepsIteration += 1
        hasOpened[x][y] = True

def markMine(x,y):
    global productiveStepsIteration
    global foundBombs

    rightClick(START_X + x*STEP_SIZE, START_Y + y*STEP_SIZE)

    board[x][y] = MINE_SQUARE

    productiveStepsIteration += 1

    for square in getCellsAround(x,y):
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
    squaresAround = getCellsAround(x,y)

    total = 0

    unknown = []

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
            unknown.append({'x':cellX, 'y':cellY})
            total += 1

    return unknown #total


def markSimpleUnknown(x,y):
    squaresAround = getCellsAround(x,y)

    total = nUnknownAround[x][y]

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

def markComplexUnknown(x,y):

    if remainder[x][y] == ' ' or remainder[x][y] == '.':
        return

    squaresAround = getCellsAround(x,y)

    total = nUnknownAround[x][y]

    cellsAround = getCellsAround(x,y)
    nCellsAround = len(cellsAround)

    thisUnknownCells = unknownAround[x][y]
    thisRemainder = remainder[x][y]


    for cell in cellsAround:
        # should only count opened cells
        if not cell in thisUnknownCells:
            matchingCells = []

            otherUnkownCells = unknownAround[cell['x']][cell['y']]
            nOtherUnkownCells = len(otherUnkownCells)

            otherRemainder = remainder[cell['x']][cell['y']]

            matches = 0
            if str(otherRemainder).isnumeric():
                for thisUnknownCell in thisUnknownCells:
                    if thisUnknownCell in otherUnkownCells:
                        matchingCells.append(thisUnknownCell)
                        matches += 1

                    if otherRemainder > 0 and len(matchingCells) > thisRemainder:
                        if matches == nOtherUnkownCells - 1:
                            #print("------------")
                            if nOtherUnkownCells == otherRemainder + 1:
                                #print("11")
                                for otherCell in otherUnkownCells:
                                    if not otherCell in matchingCells:
                                        #time.sleep(1)
                                        #printState()
                                        if board[otherCell['x']][otherCell['y']] != MINE_SQUARE:

                                            if thisRemainder > 1:
                                                #print("MINING SPECIAL")
                                                markMine(otherCell['x'], otherCell['y'])
                                                #time.sleep(5)
                                            else:
                                                markMine(otherCell['x'], otherCell['y'])


                        # TODO sometimes there is repeat opens (probably because board state is not up to date)
                        #print("potential match")
                        for otherCell in thisUnknownCells:
                            if not otherCell in matchingCells and str(board[otherCell['x']][otherCell['y']].isnumeric()):
                                if nOtherUnkownCells == otherRemainder + 1:
                                    #printState()

                                    #remainder[otherCell['x']][otherCell['y']] = '@'
                                    #remainder[cell['x']][cell['y']] = 'T'
                                    #remainder[x][y] = 'O'
                                    #printRemainder()

                                    #time.sleep(1)

                                    #do twice


                                    if thisRemainder > 1:
                                        openSquare(otherCell['x'], otherCell['y'], False)
                                    else:
                                        openSquare(otherCell['x'], otherCell['y'], False)

                    if otherRemainder > 0 and len(matchingCells) > thisRemainder and len(matchingCells) > otherRemainder and thisRemainder > 0 and matches == nOtherUnkownCells:
                        for thisCell in cellsAround:
                            if not thisCell in matchingCells:
                                if len(thisUnknownCells) > thisRemainder:
                                    if board[thisCell['x']][thisCell['y']] == UNKNOWN_SQUARE:
                                        openSquare(thisCell['x'], thisCell['y'], False)
                                        #hasOpened[thisCell['x']][thisCell['y']] = False

    if str(board[x][y]).isnumeric() and False:
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

def getCellsAround(x,y):
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

def printNumberUnknown():
    for j in range(HEIGHT):
        row = ""
        for i in range(WIDTH):
            if nUnknownAround[i][j] == 0:
                row += " " + ' '
            else:
                if board[i][j] == MINE_SQUARE or board[i][j] == UNKNOWN_SQUARE:
                    row += " " + ' '
                else:
                    row += " " + str(nUnknownAround[i][j])
        print(row)

def printRemainder():
    for j in range(HEIGHT):
        row = ""
        for i in range(WIDTH):
            if remainder[i][j] == 9:
                if board[i][j] == '*':
                    row += " " + ' '
                else:
                    row += " " + '.'
            else:
                row += " " + str(remainder[i][j])
        print(row)

def printHasOpened():
    for j in range(HEIGHT):
        row = ""
        for i in range(WIDTH):
            if hasOpened[i][j] == True:
                row += " " + '#'
            else:
                row += " " + ' '
        print(row)

def printState():
    print("")
    print("BOARD")
    printBoard()
    print("")
    print("UNKNOWN AROUND")
    printNumberUnknown()
    print("")
    print("REMAINDER")
    printRemainder()
    print("")
    if False:
        print("OPENED")
        printHasOpened()
        print("")
    print("")

def resetGame():
    global board
    global nUnknownAround
    global minesAround
    global hasOpened
    global remainder
    global tries


    click(750, 220)
    click(750, 338) # EASIER
    #click(750, 358) # HARD


    board = [[UNKNOWN_SQUARE]*HEIGHT for i in range(WIDTH)]
    nUnknownAround = [ [0]*HEIGHT for i in range(WIDTH)]
    minesAround = [ [0]*HEIGHT for i in range(WIDTH)]
    hasOpened = [ [False]*HEIGHT for i in range(WIDTH)]
    remainder = [[9]*HEIGHT for i in range(WIDTH)]
    unknownAround = [[' ']*HEIGHT for i in range(WIDTH)]

    allMatch = [[' ']*HEIGHT for i in range(WIDTH)]
    tries = 0

screenshotDaemon = threading.Thread(target=screenshotDaemon, args=(1,), daemon=True)
screenshotDaemon.start()

while gamesPlayed < GAMES:
    gamesPlayed += 1

    resetGame()
    clickSquare(START_OPEN_X, START_OPEN_Y)

    screenshot = getScreenshot()
    screen = screenshot.load()

    productiveStepsIteration = 1

    latestOpen = time.time()


    while shouldContinue():
        productiveStepsIteration = 0
        tries += 1

        #screenshot = getGreedyScreenshot()
        #screen = screenshot.load()


        screenshotLock = True

        for x in range(WIDTH):
            for y in range(HEIGHT):
                if board[x][y] == UNKNOWN_SQUARE:
                    old = board[x][y]
                    new = getNumberAt(x,y)

                    if str(old).isnumeric() and str(new).isnumeric():

                        if old > new:
                            print("BRUUUUUUUUUUUUUUUUUUH")
                    board[x][y] = getNumberAt(x,y)

        screenshotLock = False

        for x in range(WIDTH):
            for y in range(HEIGHT):
                nUnknownAround[x][y] = len(getUnknownSquaresAround(x,y))

        for x in range(WIDTH):
            for y in range(HEIGHT):
                unknownAround[x][y] = getUnknownSquaresAround(x,y)

        for x in range(WIDTH):
            for y in range(HEIGHT):
                markSimpleUnknown(x,y)


        for x in range(WIDTH):
            for y in range(HEIGHT):
                markComplexUnknown(x,y)

        for x in range(WIDTH):
            for y in range(HEIGHT):
                boardVal = board[x][y]

                if str(boardVal).isnumeric():
                    remainder[x][y] = boardVal - minesAround[x][y]
                    if remainder[x][y] == 0:
                        remainder[x][y] = ' '
                elif nUnknownAround[x][y] == 0:
                    remainder[x][y] = ' '
                else:
                    remainder[x][y] = 9

        for x in range(WIDTH):
            for y in range(HEIGHT):
                #open if all mines are found
                if minesAround[x][y] == board[x][y] and board[x][y] != 0:
                    openSquare(x, y, True)

    #printState()

daemonShouldStop = True
# reset mouse to original position and click
click(ORIGINAL_MOUSE_POSITION[0], ORIGINAL_MOUSE_POSITION[1])

#screenshot.save('state.png')
