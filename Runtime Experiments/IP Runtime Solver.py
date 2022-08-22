# Linear Programming Problem adapted to calculate the time required to solve each sudoku puzzle.

import gurobipy as gp
from gurobipy import GRB
import numpy as np
from numpy import mean

# Integer Programming model, as used for other experiments.
def IP_Solver(grid,m):
    '''
    Solves the sudoku puzzle via integer programming and records the time taken for the model to solve the sudoku 
	(exluding the time to re-congigure the sudoku and define the objective function, constraints and bounds for the problem). 
	
	Inputs:
	grid: A list of lists representing the starting state of the sudoku puzzle to be solved. 
	m : Integer representing the number of digits 1,...,m placed within the grid,
	    as well as the number of rows, columns and boxes in the grid. 
	    
	Outputs:
	model.runtime: Float detailing how long Gurobi took to find a solution to a problem.
    '''

    # Number of rows and columns in a box.
    p = int(np.sqrt(m))

    # Creating an empty model. 
    model = gp.Model('Sudoku Solver')
    
    # Turns off printing to console.
    # This line can be commented out if further details about the model are required.
    model.Params.LogToConsole = 0
    
    # As these sudoku are all proper, there is no requirement for the MIP solver to try and find multiple solutions, and could increase the time taken by the model to find a solution.

    # Updates the above parameter of the model.
    model.update()

    # Defining the binary decision variables.
    x = model.addVars(m, m, m, vtype=GRB.BINARY, name='x')

    # Assign givens of the problem to their positions. 
    # This is done by adjusting the lower bound. 
    for i in range(m):
        for j in range(m):
            if grid[i][j] != '0':
                # Must subtract by 1 to account for the fact that indexing starts at 0. 
                k = int(grid[i][j]) - 1
                x[i, j, k].lb = 1

    # Only one of each number can be found in a row.
    model.addConstrs((x.sum(i, '*', k) == 1 for i in range(m) for k in range(m)), name='Row')

    # Only one of each number can be found in a column.
    model.addConstrs((x.sum('*', j, k) == 1 for j in range(m) for k in range(m)), name='Column')

    # Only one of each number can be found in a box. 
    # Here, we change the bounds to account for the fact that indexing in python starts at 0 and not 1. 
    model.addConstrs((sum(x[i, j, k] for i in range(r*p, (r+1)*p)
                    for j in range(c*p, (c+1)*p)) == 1 for k in range(m) for r in range(p)
                    for c in range(p)), name='Sub_Matrix')

    # Each cell within the grid must have a number assigned to it. 
    model.addConstrs((x.sum(i, j, '*') == 1 for i in range(m) for j in range(m)), name='Square')

    # Since it is a constraint satisfaction (or feasibility) problem, no objective function is required.
    model.optimize()
    
    # Function returns the amount of time taken to solve the sudoku problem (in seconds). 
    return(model.runtime)
    
    
# ============================================= Driver Code =====================================================

# To open the text file containing the sudoku puzzles.
f = open('Easy Sudokus.txt')

while True:
    line = f.readline()
    
    # Terminates the loop when all sudokus have been solved.
    if not line:
        print("Completed.")
        break
        
    # Converts the sudoku to a list where each element is the starting state of a cell within the sudoku grid.    
    initial_sudoku = list(line.strip())
    
    # The digits 1,...,m are those that need to be placed within the grid. 
    m = int(np.sqrt(len(initial_sudoku)))
    
    # Converts the sudoku to a list where each element represents a row of the sudoku puzzle. 
    sudoku = [initial_sudoku[i:i + 9] for i in range(0, len(initial_sudoku), 9)]
    
    # Initialize a counter to ensure that each sudoku puzzle is solved 10 times to ensure measurability and repeatability.
    repeat = 0

    # Stores the time taken to solve the sudoku puzzles 10 times.
    one_sudoku_IP_time = 0
    
    while repeat < 10:
    	
    	# Adds the time taken to solve this sudoku puzzle once to the total time for the previous times this sudoku puzzle was solved.
    	one_sudoku_IP_time += IP_Solver(sudoku,m)
    	
    	repeat += 1 
    
    # Calculates the average time taken to solve one sudoku puzzle to the terminal. 
    one_sudoku_average_IP_time = one_sudoku_IP_time/10
    
    # Outputs the avergae time taken to solve one sudoku puzzle to the terminal. 
    print(one_sudoku_average_IP_time)



