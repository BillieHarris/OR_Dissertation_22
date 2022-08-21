# IP Solver for many 9 x 9 sudoku problems contained within a text file. 
# Sudoku should be compressed to one line with empty spaces within the grid displayed as ".". 

# The purpose for this program is to determine if sudoku are proper, and will only display an output for sudoku 
# where this is not the case. 
# However, this can be adapted as indicated by comments throughout the code. 

# Code adapted from Gurobi Optimizer's example Sudoku solver: https://www.gurobi.com/documentation/9.5/examples/sudoku_py.html . 

import numpy as np
import gurobipy as gp
from gurobipy import GRB

def display_solution(sol,m):
    '''
    Displays an easy to read solution of the sudoku puzzle.
     
    Inputs:
    sol: A valid solution to the sudoku puzzle found by integer programming. 
    m: Integer representing the number of digits 1,...,m placed within the grid, 
       as well as the number of rows, columns and boxes in the grid. 
    
    Output:
    A representation of the solution to the sudoku puzzle tha replicates how sudoku problems are usually presented. 
    '''
    
    print('\nSolution:\n')
    
    for i in range(m):
        if i in [3,6]:
            to_print = '------+-------+-------\n'
        else:
            to_print = ''
        for j in range(m):
            for k in range(m):
                if sol[i, j, k] > 0:
                    if j in [3,6]:
                        to_print += '| '+ str(k+1)+' '
                    else:
                        to_print += str(k+1)+' '
        print(to_print)
        
def IP_Solver(grid,m):
    '''
    Finds the number of valid solution(s) to the sudoku puzzle which can be used to determine if it is proper or not.
    
    The function is restricted to finding a maximum of 2 valid solutions as this is sufficient to determine if the sudoku
    is proper or not. If the number of solutions is 0 (the problem is infeasible) and no valid solutions to the sudoku exist. 
    If the number of solutions is 1 then it is proper and if the number of solutions found is 2 then the sudoku has multiple 
    valid solutions (although exactly how many is unknown as the solver is restricted to finding a maximum of 2 solutions).
    
    Inputs:
    grid: A list of lists representing the starting state of the sudoku puzzle to be solved.
    m: Integer representing the number of digits 1,...,m placed within the grid, 
       as well as the number of rows, columns and boxes in the grid.
       
    Outputs:
    num_of_solutions: Integer containing the number of valid solutions the sudoku has.
    '''

    # Number of rows and columns in a box.
    p = int(np.sqrt(m))

    # Creating an empty model. 
    model = gp.Model('Sudoku Solver')

    # Turns off printing to console. 
    # This line can be commented out if further details about the model are required.
    model.Params.LogToConsole = 0
    
    # Prevents the solver from finding more than 2 solutions.
    model.params.PoolSolutions = 2
    
    # Setting the IP solver to try and find the number of solutions set by the PoolSolutions parameter.
    model.params.PoolSearchMode = 2
    
    # Updates the above three parameters of the model.
    model.update()

    # Defining the binary decision variables.
    x = model.addVars(m, m, m, vtype=GRB.BINARY)

    # Assign givens of the problem to their positions.
    # This is done by adjusting the lower bound
    for i in range(m):
        for j in range(m):
            if grid[i][j] != '.':
                # Must subtract by 1 to account for the fact that indexing starts at 0. 
                k = int(grid[i][j]) - 1
                x[i, j, k].lb = 1

    # Only one of each number can be found in a row.
    model.addConstrs((x.sum(i, '*', k) == 1 for i in range(m) for k in range(m)), name='Row')

    # Only one of each number can be found in a column.
    model.addConstrs((x.sum('*', j, k) == 1 for j in range(m) for k in range(m)), name='Column')

    # Only one of each number can be found in a submatrix. 
    # Here, the bounds are changed to account for the fact that indexing in python starts at 0 and not 1. 
    model.addConstrs((sum(x[i, j, k] for i in range(r*p, (r+1)*p)
                    for j in range(c*p, (c+1)*p)) == 1 for k in range(m) for r in range(p)
                    for c in range(p)), name='Box')

    # Each cell within the grid must have only one digit assigned to it. 
    model.addConstrs((x.sum(i, j, '*') == 1 for i in range(m) for j in range(m)), name='Cell')

    # Since it is a constraint satisfaction (or feasibility) problem, no objective function is required.
    model.optimize()

    #Stores the number of solutions to the sudoku problem. 
    num_of_solutions = model.SolCount
    
    # Change to true if a visualisation of the solution(s) is required. 
    print_solution = False
    
    # If the user wishes to visualise any solution(s) that exist then the 
    if print_solution == True and model.status != GRB.Status.INFEASIBLE:
        if num_of_solutions > 1:
            for n in range(num_of_solutions):
                model.setParam(GRB.Param.SolutionNumber, n)
                solution = model.getAttr('Xn',x)
                display_solution(solution,m)
        else:
            solution = model.getAttr('X', x)
            display_solution(solution,m)
            
    return(num_of_solutions)

#=============================== Driver Code ======================================

# To open the text file containing the sudoku puzzles.
f = open("Easy Sudokus.txt")

while True:
    line = f.readline()
    
    # Terminates the loop when all sudokus have been solved. 
    if not line:
        print("Completed.")
        break
    
    # Converting the sudoku to a list where each element is the starting state of a cell within the sudoku grid.
    initial_sudoku = list(line.strip())
    
    # The digits 1,...,m are those that need to be placed within the grid. 
    m = int(np.sqrt(len(initial_sudoku)))
    
    # Converts the sudoku to a list where each element represents a row of the sudoku puzzle. 
    sudoku = [initial_sudoku[i:i + m] for i in range(0, len(initial_sudoku), m)]
    
    number_of_solutions = IP_Solver(sudoku)
    
    # Displays if the sudoku is not proper (as a result of having no valid solutions or multiple solutions.)
    if number_of_solutions == 0:
        print("Sudoku is invalid: ", line.strip())
    elif num_of_solutions > 1:
        print("Sudoku has multiple solutions: ", line.strip())