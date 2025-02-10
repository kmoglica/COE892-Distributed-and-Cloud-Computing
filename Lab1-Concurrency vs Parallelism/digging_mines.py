# sequential section:

import requests #Handles HTTP requests to fetch rover commands
import json #Parses JSON data from HTTP responses
from hashlib import sha256 #Used for generating sha256 hashes
import random #Generates random numbers used to create PINs for mines
import threading
from threading import Thread #Enables threading for parallel execution later
from time import sleep, perf_counter



def moveForward(array):
    try:
        if (roverDirectionState == 'North'):
            if (roverPosition[1] == 0): #roverPosition at y (height), y increases as you go down
                print("Command Ignored: At the top edge");
                return #if it returns here, the rest after this is discarded:

             # format: array representing minefield[row][cell string] == 1
            """if (array[roverPosition[1] - 1][roverPosition[0]] == '1'):

                print("Mine was Ahead, Exploded");
                roverState = "Dead"
                return roverState"""

            roverPosition[1] = roverPosition[1] - 1;

        elif (roverDirectionState == 'South'):
            if (roverPosition[1] == rows):
                print("Command Ignored: At the bottom edge");
                return
            """if (array[roverPosition[1] + 1][roverPosition[0]] == '1'):
                print("Mine Ahead, Exploded");
                roverState = "Dead"
                return roverState"""

            roverPosition[1] = roverPosition[1] + 1;

        elif (roverDirectionState == 'East'):
            if (roverPosition[0] == columns):
                print("Command Ignored: At the right edge");
                return

            """if (array[roverPosition[1]][roverPosition[0] + 1] == '1'):
                print("Mine Ahead, Exploded");
                roverState = "Dead"
                return roverState"""


            roverPosition[0] = roverPosition[0] + 1;

        elif (roverDirectionState == 'West'):
            if (roverPosition[0] == 0):
                print("Command Ignored: At the left edge");
                return
            """if (array[roverPosition[1]][roverPosition[0] - 1] == '1'):
                print("Mine Ahead, Exploded");
                roverState = "Dead"
                return roverState"""

            roverPosition[0] = roverPosition[0] - 1;

    except IndexError:
        print("index out of range")


def turnLeft(roverDirectionState):
    if (roverDirectionState == 'North'):
        roverDirectionState = 'West'
    elif (roverDirectionState == 'East'):
        roverDirectionState = 'North'
    elif (roverDirectionState == 'South'):
        roverDirectionState = 'East'
    elif (roverDirectionState == 'West'):
        roverDirectionState = 'South'
    return roverDirectionState


def turnRight(roverDirectionState):
    if (roverDirectionState == 'North'):
        roverDirectionState = 'East'
    elif (roverDirectionState == 'East'):
        roverDirectionState = 'South'
    elif (roverDirectionState == 'South'):
        roverDirectionState = 'West'
    elif (roverDirectionState == 'West'):
        roverDirectionState = 'North'
    return roverDirectionState


start_time = perf_counter()


def createArray(): #Load the minefield from 'mines.txt'
    with open("mines.txt", "r") as f: # f closes automatically after block's execution
        rowsAndColumns = f.readline().split()  #split() splits the line into a list of strings

        global rows
        rows = rowsAndColumns[0] #remember row is in string form

        global columns
        columns = rowsAndColumns[1]

        print(rows + " " + columns)

        array = [] # defining an empty list
        for line in f: #object f is a file, and files gets iterated line by line
            array.insert(len(array), line.split())  # .split() takes the line string and splits it into list of strings
            #so a list of strings is inserted into the last position of the list named array
            #print(line.split())
        print(array)

    return array


# get moves
def getMoves():
    response = requests.get('https://coe892.reev.dev/lab1/rover/1')

    data = response.text # response.text refers to the content of the HTTP response as a JSO-formatted string
    print(data)

    parse_json = json.loads(data) # .loads() takes in a JSON-formatted string as a parameter and returns python dictionary
    print(parse_json)

    moves = parse_json['data']['moves'] # moves is a string
    print(moves)
    # moves = 'MMMMRMLRRRLRMLMRMLMMMLMMRMMLDMLMMMMMLRLLRDMMMLDMLRDMRLMRMRMRRMLRLLRMDRMRDLMDLM'
    print("moves(string) from api are: " + moves)

    return moves

# THESE ARE 3 GLOBAL VARIABLES:
roverState = "Alive"
roverDirectionState = 'South'
roverPosition = [0, 0]  # x, y(height) starting position of rover
#roverPosition is a variable of type list

# start traversing minefield
def startTraverse():
    array = createArray() #local variable array, also array is passed by reference (mutable list)
    #print("hello")
    #print(type(array))

    # Strings are immutable, so they are passed by value
    moves = getMoves() #local variable moves, also moves is passed by value (immutable string)

    global roverDirectionState #referring to the already existing global variable

    for i in range(len(moves)): #length of string
        if (moves[i] == 'M'):  # move forward
            state = moveForward(array) # local variable (state of class NoneType, bc that’s what moveForward() returns)
            #state assigned value of None since moveForward() implicitly returns None
            # bc standard case doesn't explicitly return anyth, only returns string in specific cases

            #print("see below:")
            #print(type(state)) # None is the return value of functions when they don't return anything

            if state == "Dead": # it went into one of the specific cases here
                roverState = "Dead"
                break #used to exit loop, bc we stop traversing if rover is dead

                #We would only be able to continue traversing if the mine was disarmed

        elif (moves[i] == 'L'):  # turn left
            roverDirectionState = turnLeft(roverDirectionState)
        elif (moves[i] == 'R'):  # turn right
            roverDirectionState = turnRight(roverDirectionState)

        elif (moves[i] == 'D'): #DIG FOR A MINE
            try:
                print("we are inside a dig instruction now")
                print(array)
                print(roverPosition)
                print("digging procedure: ", array[roverPosition[1]][roverPosition[0]]) #prints the cell in minemap

                if (array[roverPosition[1]][roverPosition[0]] == '1'):
                    print("mine is here") #if theres a mine, we need to "disarm" it
                    number = random.randint(1000, 9999) #Generates a random 4-digit number (PIN)
                    temp_mine_key = str(number) + array[roverPosition[1]][roverPosition[0]] #concat 4 dig number with 1
                    print("TEMP MINE KEY: ", temp_mine_key)

                    #sha256 (and most other cryptographic algorithms) work with bytes, not strings
                    #The encode('utf-8') method used to convert a string into a sequence of bytes
                    hash = sha256(temp_mine_key.encode('utf-8')).hexdigest() #Hashes the PIN + mine data
                    #print(type(hash))
                    print(temp_mine_key.encode('utf-8'))
                    print(sha256(temp_mine_key.encode('utf-8')))

                    #hash object needed to be converted to usable format (like a hexadecimal string) - via .hexdigest()
                    print("HASH: ", hash)

                    # I am not going to do it this way it takes way too long -->
                    # while hash[:6] != '000000':  # Check the first 6 six characters of the hash to escape while loop
                    while hash[0] != '0': # Just checking the first of the 6 characters, this is the same idea, just
                        #less time consuming
                        print("pin invalid, try again")

                        # BRUTE FORCE: create a new hash value over and over until it starts with a '0'
                        number = random.randint(1000, 9999)
                        temp_mine_key = str(number) + array[roverPosition[1]][roverPosition[0]];
                        # print("TEMP MINE KEY: ", temp_mine_key)
                        hash = sha256(temp_mine_key.encode('utf-8')).hexdigest()
                        # print("HASH: ", hash)

                    print("pin valid, disarm mine")
                else:
                    print("mine is not here")
            except IndexError:
                print("IndexError")
        print("Direction: " + roverDirectionState)
        print("Position: ", roverPosition)
        print("---------")


#program main logic starts:

start_time = perf_counter() #start timer

createArray() #Step 1: Load the minefield from 'mines.txt'
getMoves() #Step 2: Fetch the move instructions from the server
startTraverse() #Step 3: Start moving the rover

end_time = perf_counter() #end timer

print(f'It took {end_time - start_time : 0.2f} second(s) to complete.')
print("seq program done....")
seq_done = 1;





# parallel section:

def createArray_Thr():
    with open("mines.txt", "r") as f:
        rowsAndColumns = f.readline().split();
        global rows
        rows = rowsAndColumns[0]
        global columns
        columns = rowsAndColumns[1]

        print(rows + " " + columns)

        array = []
        for line in f:
            array.insert(len(array), line.split())

        print(array)

    return array

def getMoves_Thr():
    response = requests.get('https://coe892.reev.dev/lab1/rover/' + '1')

    data = response.text

    parse_json = json.loads(data);

    moves = parse_json['data']['moves']

    moves = 'MMMMRMLRRRLRMLMRMLMMMLMMRMMLDMLMMMMMLRLLRDMMMLDMLRDMRLMRMRMRRMLRLLRMDRMRDLMDLM' # manual input

    print("moves: " + moves)

    return moves

def startTraverse_Thr():
    array = createArray()
    moves = getMoves()
    global roverDirectionState

    for i in range(len(moves)):
        if (moves[i] == 'M'):  # move forward
            state = moveForward(array)
            if (state == "Dead"):
                roverState = "Dead"
                break

        elif (moves[i] == 'L'):  # turn left
            roverDirectionState = turnLeft(roverDirectionState)
        elif (moves[i] == 'R'):  # turn right
            roverDirectionState = turnRight(roverDirectionState)

        elif (moves[i] == 'D'):
            try:
                print(array)


                print("digging procedure: ", array[roverPosition[1]][roverPosition[0]])


                if (array[roverPosition[1]][roverPosition[0]] == '1'):

                    number = random.randint(1000, 9999)
                    temp_mine_key = str(number) + array[roverPosition[1]][roverPosition[0]];
                    print("TEMP MINE KEY: ", temp_mine_key)
                    hash = sha256(temp_mine_key.encode('utf-8')).hexdigest()
                    print("HASH: ", hash)
                    while (hash[0] != '0'):
                        print("pin invalid")
                        number = random.randint(1000, 9999)
                        temp_mine_key = str(number) + array[roverPosition[1]][roverPosition[0]];
                        # print("TEMP MINE KEY: ", temp_mine_key)
                        hash = sha256(temp_mine_key.encode('utf-8')).hexdigest()
                        # print("HASH: ", hash)

                    print("pin valid, disarm mine")
                else:
                    print("mine is not here")
            except IndexError:
                print("IndexError")
        print("Direction: " + roverDirectionState)
        print("Position: ", roverPosition)
        print("---------")


if(seq_done): #any non-zero number, non-empty string, non-empty list, or any object that isn't None considered truthy

    roverState = "Alive"
    roverDirectionState = 'South'
    roverPosition = [0, 0]  # x, y

    start_time = perf_counter()

    #creates 3 separate threads:
    t1 = Thread(target=createArray_Thr) #t1 → Reads minefield.
    t2 = Thread(target=getMoves_Thr) #t2 → Fetches movements.
    t3 = Thread(target=startTraverse_Thr) #t3 → Starts moving the rover.

    # run the threads simultaneously
    t1.start()
    t2.start()
    t3.start()

    # using .join() to prevent race conditions
    t1.join()
    t2.join()
    t3.join()

    end_time = perf_counter()

    print(f'It took {end_time- start_time: 0.2f} second(s) to complete.')

    print(type(seq_done))


