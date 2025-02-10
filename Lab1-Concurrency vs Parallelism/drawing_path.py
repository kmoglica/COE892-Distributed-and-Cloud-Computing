import requests
import json
import threading
from threading import Thread
from time import sleep, perf_counter

# get moves
def getMoves(number):
    response = requests.get('https://coe892.reev.dev/lab1/rover/' + str(number))
    #Fetch commands for each of the 10 robots from a provided API.

    print(response.text)
    data = response.text
    parse_json = json.loads(data); # .load() methods converts the raw JSON string into a Python dictionary

    print(parse_json)

    moves = parse_json['data']['moves']
    print("moves: " + moves)

    return moves #moves is a string containing each move the rover needs to take

# start traversing minefield
def startTraverse(num):
    global roverDirectionState
    global roverState
    global roverPosition
    roverState = "Alive"
    roverDirectionState = 'South'
    roverPosition = [0, 0]  # x, y

    #Opening a file to write path data
    f = open("path_" + str(num) + ".txt", "w+");

    arrayPath = array; #2D grid -- list of lists
    arrayPath[0][0] = "*"

    moves = getMoves(num)

    for i in range(len(moves)):
        if (moves[i] == 'M'):  # move forward
            state = moveForward()
            if (state == "Dead"):
                roverState = "Dead"
                break

        elif (moves[i] == 'L'):  # turn left
            roverDirectionState = turnLeft(roverDirectionState)
        elif (moves[i] == 'R'):  # turn right
            roverDirectionState = turnRight(roverDirectionState)
        elif (moves[i] == 'D'):
            if(arrayPath[roverPosition[1]][roverPosition[0]] == '1'): #arrayPath[row][col]
                print("mine is here, start digging")
            else:
                print("mine not here")
        print("Direction: " + roverDirectionState)
        print("Position: ", roverPosition)
        print("---------")

    #Saving the Path to a File created earlier:
    for row in arrayPath:
        f.write(" ".join(row) + "\n") #join makes multiple stings into one string


def moveForward():
    try:
        if (roverDirectionState == 'North'):
            if (roverPosition[1] == 0):
                print("Command Ignored: At the edge");
                return
            if (arrayPath[roverPosition[1] - 1][roverPosition[0]] == '1'):
                print("Mine Ahead, Exploded(assuming not disarmed)");
                roverState = "Dead"
                return roverState

            roverPosition[1] = roverPosition[1] - 1;
            arrayPath[roverPosition[1]][roverPosition[0]] = "*"
        elif (roverDirectionState == 'South'):
            if (roverPosition[1] == rows):
                print("Command Ignored: At the edge");
                return
            if (arrayPath[roverPosition[1] + 1][roverPosition[0]] == '1'):
                print("Mine Ahead, Exploded(assuming not disarmed)");
                roverState = "Dead"
                return roverState

            roverPosition[1] = roverPosition[1] + 1;
            arrayPath[roverPosition[1]][roverPosition[0]] = "*"
        elif (roverDirectionState == 'East'):
            if (roverPosition[0] == columns):
                print("Command Ignored: At the edge");
                return

            if (arrayPath[roverPosition[1]][roverPosition[0] + 1] == '1'):
                print("Mine Ahead, Exploded(assuming not disarmed)");
                roverState = "Dead"
                return roverState

            roverPosition[0] = roverPosition[0] + 1;
            arrayPath[roverPosition[1]][roverPosition[0]] = "*"
        elif (roverDirectionState == 'West'):
            if (roverPosition[0] == 0):
                print("Command Ignored: At the edge");
                return
            if (arrayPath[roverPosition[1]][roverPosition[0] - 1] == '1'):
                print("Mine Ahead, Exploded(assuming not disarmed)");
                roverState = "Dead"
                return roverState

            roverPosition[0] = roverPosition[0] - 1;
            arrayPath[roverPosition[1]][roverPosition[0]] = "*"
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



# Here we begin the main logic

start_time = perf_counter()

with open("map.txt", "r") as f: # with ensures File is automatically closed when the block ends
    rowsAndColumns = f.readline().split(); # .split() splits the line into a list of strings
    global rows
    rows = rowsAndColumns[0]
    global columns
    columns = rowsAndColumns[1]

    print(rows + " " + columns)

    array = [] #defining an empty list named array
    for line in f:
        array.insert(len(array), line.split()) #insert list of strings into final position of list "array"
        #We are making a list of lists(each line of a file)

print(array)



arrayPath = array;
arrayPath[0][0] = "*" #arrayPath[row][col]

for i in range(1, 11, 1): #Iterates through rover IDs from 1 to 10
    startTraverse(i)
    print("------------------- TRAVERSE " + str(i) + " COMPLETED -------------------")

end_time = perf_counter();

print(f'It took {end_time- start_time: 0.2f} second(s) to complete.')

print("seq program done....")
seq_done = 1


def createArray_thr():
    with open("map.txt", "r") as f:
        rowsAndColumns = f.readline().split();
        global rows
        rows = rowsAndColumns[0]
        global columns
        columns = rowsAndColumns[1]

        print(rows + " " + columns)

        array = []
        for line in f:
            array.insert(len(array), line.split()) # .split() creates list of strings from just one string line

    print(array)



def thr2():
    roverState = "Alive"
    roverDirectionState = 'South'
    roverPosition = [0, 0]  # x, y

    arrayPath = array;
    arrayPath[0][0] = "*"

    for i in range(1, 11, 1):
        startTraverse(i)



if seq_done == 1:
    val = input("Run multithreaded program? (y/n): ")

    if val == 'y':
        start_time = perf_counter()


        t1 = Thread(target=createArray_thr)
        t2 = Thread(target=thr2)

        t1.start()
        t2.start()

        # .join() ensures that the main thread waits for specific thread(s) to finish before proceeding its execution
        t1.join()
        t2.join()

        end_time = perf_counter()

        print(f"It took {end_time - start_time: 0.2f} second(s) to complete.")