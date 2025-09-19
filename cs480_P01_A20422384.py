import sys, pandas as pd, time 
from queue import PriorityQueue

# Counts the number of terminal arguments
numberArgumentsCL = len(sys.argv)

# Check for correct argument numbers
if numberArgumentsCL != 3:
    print("Error: Not enough or too many input arguments.")
    exit()

# First argument passed (file name)
scriptName = sys.argv[0]
#print("Script Name:", scriptName)
# Second argument passed (goal state)
goalState = sys.argv[1]
# Third argument passed (initial state)
initialState = sys.argv[2]

print("Haider, Mazin, A20422384 solution:")
print("Initial state:", initialState)
print("Goal state:", goalState)

# Input data from the csv files for the heuristic and the path cost
# index_col arugment sets which column to be the index_col
dataFrameStraightLine = pd.read_csv('straightline.csv', index_col= 'STATE')
dataFrameDrivingPath = pd.read_csv('driving_.csv', index_col= 'STATE')

def noSolutionMessage():
    print("Solution: NO SOLUTION FOUND")
    print("Number of stops on a path:", 0)
    print("Execution time: 0 seconds")
    print("Complete path cost:", 0)

# Returns the list of neighboring states to a current state
def neighborStates(state):
    neighbors = []
    # Loop through all of the columns in dataFrame of the state and append whichever state that distance is not -1
    for distance in dataFrameDrivingPath[state]:
        if distance != -1 and distance != 0:
            # Append the states that neighbors the current one
            neighbor = dataFrameDrivingPath.index[dataFrameDrivingPath[state] == distance][0]
            neighbors.append((neighbor, distance))

    return neighbors

# Execute the GBFS algo
def greedyBestFirstSearch(initialState, goalState):
    # Handle the time of the search
    timeStart = time.time()
    # List for the total path of the traversal
    path = []
    path_cost = 0
    # Create the fronter list and the reached dictionary
    frontier = {} 
    reached = {} 
    try:
        # Initialize the node to append to the frontier
        frontier[initialState] = dataFrameStraightLine[initialState][goalState]
        reached[initialState] = dataFrameDrivingPath[initialState][initialState]
        # Loop through the frontier until a goal state is found or until the frontier is empty
        while len(frontier) != 0:
            node = next(iter(frontier.keys()))
            #h, node = frontier.get()
            path_cost = reached[node]
            frontier.pop(node)
            # Add the node to be expanded to the path
            path.append(node)
            #path.append(node)
            if node == goalState:
                # End and search time
                timeEnd = time.time()
                time_gbfs = timeEnd - timeStart
                # Return the path, cost, and search time
                return path, path_cost, time_gbfs, len(reached)
            # Set a boolean for dead_end
            dead_end = True
            pop_next = False
            # Loop through the neighbers of the current state
            for (neighbor, cost) in neighborStates(node):
                if neighbor not in reached or (path_cost + cost) < reached[neighbor]:
                    dead_end = False
                    # Append on to the reached table
                    reached[neighbor] = path_cost + cost
                    # Add child to the frontier
                    frontier[neighbor] = dataFrameStraightLine[neighbor][goalState]
                    # Sort the frontier dictionary smallest to largest based on key
                    frontier = dict(sorted(frontier.items(), key = lambda x:x[1]))
                    val = next(iter(frontier.keys()))
                    if val == neighbor:
                        pop_next = True

            if dead_end and not pop_next:
                path.pop()
    except:
        noSolutionMessage()
        exit()

    return None
    
# Execute the a* algorithm
def aStarAlgorithm(initialState, goalState):
    # Start the time for the algo
    timeStart = time.time()
    # List for the total path of the traversal
    path = []
    path_cost = 0
    # Create the fronter list and the reached dictionary
    frontier = {}
    reached = {}
    try:
        # Initialize the frontier and the reached tables
        frontier[initialState] = dataFrameStraightLine[initialState][goalState]
        reached[initialState] = dataFrameDrivingPath[initialState][initialState]
        # Loop through the frontier until a goal state is found or until the frontier is empty
        while len(frontier) != 0:
            node = next(iter(frontier.keys()))
            path_cost = reached[node]
            frontier.pop(node)
            path.append(node)
            if node == goalState:
                # End the search time and calculate the total time
                timeEnd = time.time()
                timeAStar = timeEnd - timeStart
                # Return the path, cost, and the search time
                return path, path_cost, timeAStar, len(reached)
            # Loop through the neighbers of the current state
            dead_end = True
            pop_next = False
            for (neighbor, cost) in neighborStates(node):
                if neighbor not in reached or (path_cost + cost) < reached[neighbor]:
                    dead_end = False
                    reached[neighbor] = path_cost + cost
                    frontier[neighbor] = path_cost + cost + dataFrameStraightLine[neighbor][goalState]
                    frontier = dict(sorted(frontier.items(), key = lambda x:x[1]))
                    val = next(iter(frontier.keys()))
                    if val == neighbor:
                        pop_next = True

            if dead_end and not pop_next:
                path.pop()
    except:
        noSolutionMessage()
        exit()

    return None

# Output for the program
path, path_cost, elapsedTime, visited_states = greedyBestFirstSearch(initialState, goalState)

print()
print("Greedy Best First Search")
print(f"Path: {path}")
print(f"Path Cost: {path_cost}")
print(f"Visited States: {visited_states}")
print(f"Elapsed Time: {elapsedTime} seconds")
print()

path, path_cost, elapsedTime, visited_states = aStarAlgorithm(initialState, goalState)
print("A* Search")
print(f"Path: {path}")
print(f"Path Cost: {path_cost}")
print(f"Visited States: {visited_states}")
print(f"Elapsed Time: {elapsedTime} seconds")
print()

# What is left: Handle dead ends, handle the no solution cases, count the visited states