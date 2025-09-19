import sys, pandas as pd, time, csv

# Read in command line arguments
cl_arguments = len(sys.argv)

# Check for correct arguments
if cl_arguments != 3:
    print("ERROR: Not enough/too many/illegal input arguments.")
    exit()

# Read in first arguments
file_name = sys.argv[0]
search = sys.argv[1]
puzzle_file_name = sys.argv[2]


# Read in from the csv file to a dataframe
sudoku = pd.read_csv(puzzle_file_name, header=None)


# Initialize variables, domains, and constraints
variables = [] # A list of values
domains = [] # A list of lists of possible values for a variable
# Constraint function to check correctness of the entire board
def constraints(variables):
    # Iterate over the rows to check for similar values
    start_row = 0
    for end_row in range(9, 82, 9):
        for i in range(start_row, end_row):
            for j in range(i + 1, end_row):
                if variables[i] == 'X' or variables[j] == 'X':
                    continue
                if variables[i] == variables[j]:
                    return False
        start_row = end_row
    
    # Check for a failed constraint by converting into a column into a set
    variable_set = set()
    count = 0
    for i in range(0, 9):
        for j in range(i, i + 73, 9):
            if variables[i] == 'X' or variables[j] == 'X':
                    continue
            variable_set.add(variables[j])
            count += 1
        if len(variable_set) != count:
            return False
        count = 0
        variable_set.clear()

    # Check for the subgrid of 3x3 for similarities
    variable_set.clear()
    count = 0
    # Check for the first 3 subgrids
    for i in range(0, 7, 3):
        next_row = 0
        for j in range(0, 9):
            index = i + next_row
            if variables[index] != 'X':
                variable_set.add(variables[index])
                count += 1
            next_row += 1
            if next_row == 3:
                i += 9
                next_row = 0
    
        if len(variable_set) != count:
            return False
        
        variable_set.clear()
        count = 0
    
    # Check for the second 3 subgrids
    variable_set.clear()
    count = 0
    for i in range(27, 34, 3):
        next_row = 0
        for j in range(0, 9):
            index = i + next_row
            if variables[index] != 'X':
                variable_set.add(variables[index])
                count += 1
            next_row += 1
            if next_row == 3:
                i += 9
                next_row = 0
    
        if len(variable_set) != count:
            return False   
        
        variable_set.clear()
        count = 0
         

    # Check for the 3rd 3 subgrids
    variable_set.clear()
    count = 0     
    for i in range(54, 61, 3):
        next_row = 0
        for j in range(0, 9):
            index = i + next_row
            if variables[index] != 'X':
                variable_set.add(variables[index])
                count += 1
            next_row += 1
            if next_row == 3:
                i += 9
                next_row = 0
    
        if len(variable_set) != count:
            return False  
          
        variable_set.clear()
        count = 0

    return True

# Fill the list of variables according to the dataframe while converting the numbers to integer type
for index, row in sudoku.iterrows():
    for element in row:
            variables.append(element)

# Convert the digits from the pd to integer type
for index in range(len(variables)):
    if variables[index] != 'X':
        variables[index] = int(variables[index])

# Fill the domain values according to the given puzzle
for index in range(len(variables)):
    if variables[index] == 'X':
        domains.append( [1,2,3,4,5,6,7,8,9] )
    else:
        domains.append([ int(variables[index]) ])


# Function to display the sudoku board
def board_display(variables):
    count = 1
    final_value = 1
    for variable in variables:
        if final_value == 81:
            print(variable)
            break
        print(variable, end=', ')
        if count == 9:
            print()
            count = 0
        count += 1
        final_value += 1
    print()

# Global variable to keep count of tree nodes expanded
node_count = 0

# Implementation of brute force algo
def brute_force(variables, domains, index = 0):
    # Global variable tree node count
    global node_count
    # Use index argument for assigning the current variable in the variables list
    # If the end of the board has been reached return
    if index == 81:
        return
    # Given a value in the variables list, and the corresponding domain for that variables (zipped)
    for value in domains[index]:
        # Assign the value to the variable
        variables[index] = value
        # Keep count of the search tree nodes (excluding the given values)
        if len(domains[index]) != 1:
            node_count += 1
        # Backtrack by recursive calling and index + 1 for the next element to assign
        brute_force(variables, domains, index + 1)
        # Once all of the values have filled, through recursive calls, check if the constraints are satisfied
        # If constraints function returns true, then return the variables list as a solution
        if constraints(variables): 
            return variables
    return False


# Implementation of the csp w/ backtracking solution
def csp_search(variables, domains, index = 0):
    # Set global variables for node expansion count
    global node_count
    # Check for complete assignment, the board is filled with numeric values
    if all(isinstance(value, int) for value in variables):
        return variables
    # for each value in the domain of that variable
    for value in domains[index]:
        # Assign domain value and check for consistency between variables the have integer values
        variables[index] = value
        # Increment tree count for values not given by the puzzle
        if len(domains[index]) != 1:
            node_count += 1
        if constraints(variables):
            # Result will either be failure or the updated variables
            result = csp_search(variables, domains, index + 1)
            # If the result is not a failure, then return the variables list of completed csp
            if result != False:
                return variables
    if len(domains[index]) != 1:
        variables[index] = 'X'
    return False

def inference(variables, domains, index, given_indexes, option):
    value = variables[index]
    # Loop through row and remove the value from the domain
    start_row = int(index / 9) * 9
    end_row = start_row + 9
    for i in range(start_row, end_row):
        if option == True:
            if value in domains[i]:
                domains[i].remove(value)
        if option == False:
            if i not in given_indexes and value not in domains[i]:
                domains[i].append(value)

    # Loop through the corresponding column
    start = index
    while start >= 9:
        start -= 9
    end = 73 + start
    for i in range(start, end, 9):
        if option == True:
            if value in domains[i]:
                domains[i].remove(value)
        if option == False:
            if i not in given_indexes and value not in domains[i]:
                domains[i].append(value)


def select_variable(variables, domains, visited):
    # Select variable w/ the smallest domain size not in visited set
    possible_variables = []
    for index in range(len(variables)):
        if index not in visited:
            possible_variables.append(domains[index])

    # Find the minimum possible_variables for the ones not visited
    min_domain = min(possible_variables, key=len)
    for index in range(len(variables)):
        if index not in visited and min_domain == domains[index]:
            visited.append(index)
            return index
    #Don't forget to remove from the visited and restore to X after all domain values have been traversed

def forward_checking_mrv(variables, domains):
    # Keep track of the indexes of given values
    given_indexes = []
    for index in range(len(variables)):
        if variables[index] != 'X':
            given_indexes.append(index)
    return _forward_checking_mrv(variables, domains, given_indexes, [])
    
def _forward_checking_mrv(variables, domains, given_indexes, visited):
    global node_count
    # Check if all of the variables have assignment
    if all(isinstance(value, int) for value in variables):
        return variables
    # Check for the next value to assign
    index = select_variable(variables, domains, visited)
    # If the domains is empty, return
    if len(domains[index]) == 0:
        return False
    for value in domains[index]:
        variables[index] = value
        # Increase node count if not a given index
        if index not in given_indexes:
            node_count += 1
        # If constraints don't pass go to the next domain
        if not constraints(variables):
            continue
        # If constraints pass, apply the inference to the other neighboring varibles row and col'n
        inference(variables, domains, index, given_indexes, True)
        result = _forward_checking_mrv(variables, domains, given_indexes, visited)
        if result != False:
            return variables
        # Take out the inference if there is failure
        inference(variables, domains, index, given_indexes, False)
    # After all values in domain have been traversed, reassign the X for non given values, and take index out of visited set
    if index not in given_indexes:
        visited.remove(index)
        variables[index] = 'X'
    return False

# Implementation to test the solution
def test_solution(variables):
    print("Solution:\n")
    board_display(variables)
    if constraints(variables):
        print("This is a valid, solved, Sudoku puzzle.")
    else:
        print("ERROR: This is NOT a solved Sudoku puzzle.")


# Print the initial sudoku board w/ information
print("Haider, Mazin, A20422384 solution:")
print("Input file:", puzzle_file_name)

# Call the right algorithm based on the command line argument
if search == '1':
    print("Algorithm: Brute Force\n")
    print("Input puzzle:\n")
    board_display(variables)
    time_start = time.time()
    brute_force(variables, domains)
    time_end = time.time()
    print(f"Number of search tree nodes generated: {node_count}")
    print(f"Search time: {time_end - time_start} seconds\n")
    print("Solved puzzle:\n")
    board_display(variables)
elif search == '2':
    print("Algorithm: CSP backtracking search\n")
    print("Input puzzle:\n")
    board_display(variables)
    time_start = time.time()
    csp_search(variables, domains)
    time_end = time.time()
    print(f"Number of search tree nodes generated: {node_count}")
    print(f"Search time: {time_end - time_start} seconds\n")
    print("Solved puzzle:\n")
    board_display(variables)
elif search == '3':
    print("Algorithm: CSP with forward-checking and MRV heuristics\n")
    print("Input puzzle:\n")
    board_display(variables)
    time_start = time.time()
    forward_checking_mrv(variables, domains)
    time_end = time.time()
    print(f"Number of search tree nodes generated: {node_count}")
    print(f"Search time: {time_end - time_start} seconds\n")
    print("Solved puzzle:\n")
    board_display(variables)
elif search == '4':
    test_solution(variables)

# Update board into the csv file to test for the solution
if search == '1' or search == '2' or search == '3':
    sudoku_row = []
    sudoku_row_count = 0
    out_file_name = f"{puzzle_file_name[:-4]}_solution.csv"
    file = open(out_file_name, 'w', newline='')
    writer = csv.writer(file)
    for value in variables:
        sudoku_row.append(value)
        sudoku_row_count += 1
        if sudoku_row_count == 9:
            writer.writerow(sudoku_row)
            sudoku_row = []
            sudoku_row_count = 0
    file.close()