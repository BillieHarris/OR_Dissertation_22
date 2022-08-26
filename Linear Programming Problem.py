# LP solver to find solutions for sudoku problems contained within a text file. 
# Sudoku should be compressed to one line with empty spaces within the grid displayed as ".". 

# The purpose for this program is to determine if solutions found by the LP problem are integer and outputs
# the number of sudoku problems from the file that do not have integer solutions. 

import numpy as np
import gurobipy as gp
from gurobipy import GRB

def check_if_integer(sol,m,integer_count):
    '''
    Determines if the solution to the sudoku puzzle when solved via linear programming is integer or not
    (hence determining if linear programming is sufficient for this sudoku puzzle or not).

    Inputs: 
    sol: The solution to the sudoku puzzle found by linear programming.
    m: Integer representing the number of digits 1,...,m placed within the grid, 
       as well as the number of rows, columns and boxes in the grid. 
    integer_count: Binary value indicating if the solution contains fractions or not. 
                   Currently set to 0 as it has not yet been determined if the solution 
                   contains fractional values or not.

    Outputs:
    integer_count: Binary variable - will return 1 if the solution contains fractions, and 
                   0 if solution is integer.
    '''
    is_integer = True

    # Verifies that all variables within the solution are integer.
    # If any are fractional then the loops are broken and no more variables' values are considered.
    for i in range(m):
        for j in range(m):
            for k in range(m):
                if 0 < sol[i,j,k] < 1:
                    is_integer = False
                    break

    # If at least one fractional value has beeen found, the puzzle is outputed to the user and 
    # increments the value of integer count to 1.                                  
    if is_integer == False:
        print("Following sudoku does not have integer solutions when solved by Linear Programming:")
        print(line.strip())

        integer_count = 1

    return(integer_count)

def LP_solver(grid,m):
    '''
    Solves the sudoku puzzle inputted using linear program. The function check_if_integr is
    then called to determine if linear programming is sufficient for solving this sudoku puzzle 
    or not (if the solution only contains integers or not.)

    Inputs:
    grid: A list of lists representing the starting state of the sudoku puzzle to be solved.
    m: Integer representing the number of digits 1,...,m placed within the grid, 
       as well as the number of rows, columns and boxes in the grid.
       
    Outputs:
    integer_count: Binary variable - will return 1 if the solution contains fractions, and 
                   0 if solution is integer. 
    '''

    integer_count = 0

    # Number of rows and columns in a box.
    p = int(np.sqrt(m))

    # Creating an empty model. 
    model = gp.Model('Sudoku Solver')

    # Turns off printing to console. 
    # This line can be commented out if further details about the model are required.
    model.Params.LogToConsole = 0
    
    # Updates the above parameter of the model.
    model.update()
    
    # Defining the decision variables.
    x = model.addVars(m, m, m, vtype=GRB.CONTINUOUS, name='x')
    
    # Assign givens of the problem to their positions.
    # This is done by adjusting the lower bound
    for i in range(m):
        for j in range(m):
            if grid[i][j] != '.':
                # Must subtract by 1 to account for the fact that indexing starts at 0. 
                k = int(grid[i][j]) - 1
                x[i, j, k].lb = 1

    # Do not need to set the upper and lower bounds of the other variables for the problem as these 
    # are controlled for by the constraints below. 

    # Only one of each number can be found in a row.
    model.addConstrs((x.sum(i, '*', k) == 1 for i in range(m) for k in range(m)), name='Row')

    # Only one of each number can be found in a column.
    model.addConstrs((x.sum('*', j, k) == 1 for j in range(m) for k in range(m)), name='Column')

    # Only one of each number can be found in a box. 
    # Here, we change the bounds to account for the fact that indexing in python starts at 0 and not 1. 
    model.addConstrs((sum(x[i, j, k] for i in range(r*p, (r+1)*p)
                    for j in range(c*p, (c+1)*p)) == 1 for k in range(m) for r in range(p)
                    for c in range(p)), name='Box')

    # Each cell within the grid must have a number assigned to it. 
    model.addConstrs((x.sum(i, j, '*') == 1 for i in range(m) for j in range(m)), name='Cell')

    # Since it is a constraint satisfaction (or feasibility) problem, no objective function is required.
    model.optimize()
    
    # Calls the function check_if_integer to verify id the solution is   
    if model.status != GRB.Status.INFEASIBLE:
        solution = model.getAttr('X', x)
        integer_count = check_if_integer(solution,m,integer_count)
        #print(solution)
        
    return(integer_count)
        
#=============================== Driver Code ======================================

# To open the text file containing the sudoku puzzles.
f = open("Easy Sudokus.txt")

# To count the total number of sudoku puzzles within the file that do not have integer solutions to LP. 
count = 0 

while True:
    line = f.readline()
    
    #  # Terminates the loop when all sudokus have been solved. 
    if not line:
        print("Completed.")
        break
    
    # Converting the sudoku to a list where each element is the starting state of a cell within the sudoku grid.
    initial_sudoku = list(line.strip())
    
    # The digits 1,...,m are those that need to be placed within the grid. 
    m = int(np.sqrt(len(initial_sudoku)))
    
    # Converts the sudoku to a list where each element represents a row of the sudoku puzzle. 
    sudoku = [initial_sudoku[i:i + m] for i in range(0, len(initial_sudoku), m)]
    
    count += LP_solver(sudoku,m)
    
    
print("Number of sudokus that cannot be solved to integer with LP:", count)