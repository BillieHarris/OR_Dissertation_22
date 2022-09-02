# Determining if sudoku have integer solutions to LP problem when presolve is not called.

import numpy as np
import gurobipy as gp
from gurobipy import GRB

def check_if_integer(sol,m,grid,lp_int_count):
    '''
    Determines if the solution to the sudoku puzzle when solved via linear programming is integer or not.
    
    Inputs: 
    sol: The solution to the sudoku puzzle found by linear programming.
    m: Integer representing the number of digits 1,...,m placed within the grid, 
       as well as the number of rows, columns and boxes in the grid. 
    integer_count: Binary value indicating if the solution contains fractions or not. 
                   Currently set to 0 as it has not yet been determined if the solution 
                   contains fractional values or not.
                   
    Outputs:
    non_integer_count: Binary variable - will return 0 if the solution contains fractions, and 
                   1 if solution is integer.
    '''
    
    # Verifies that all cells only have one digit assigned to them. 
    # If not, then the solution must be fractional and so the loops are broken and no more cells are considered.
    is_integer = True
    for i in range(m):
        for j in range(m):
            for k in range(m):
                if 0 < sol[i,j,k] < 1:
                    is_integer = False
                    break
                    
    # If at least one fractional value has beeen found, the value of lp_int_count is set to 0.                      
    if is_integer == False:
        lp_int_count = 0
        
    return(lp_int_count)

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
    lp_int_count: Binary variable - will return 0 if the solution contains fractions, and 
                   1 if solution is integer. 
    '''
    lp_int_count = 1
    
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
    x = model.addVars(m, m, m, vtype=GRB.CONTINUOUS, name='x',lb = 0,ub = 1)
    
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

    # Only one of each number can be found in a box. 
    # Here, we change the bounds to account for the fact that indexing in python starts at 0 and not 1. 
    model.addConstrs((sum(x[i, j, k] for i in range(r*p, (r+1)*p)
                    for j in range(c*p, (c+1)*p)) == 1 for k in range(m) for r in range(p)
                    for c in range(p)), name='Sub_Matrix')

    # Each cell within the grid must have a number assigned to it. 
    model.addConstrs((x.sum(i, j, '*') == 1 for i in range(m) for j in range(m)), name='Square')

    # Since it is a constraint satisfaction (or feasibility) problem, no objective function is required.
    model.optimize()
    
    # Calls the function check_if_integer to verify if the solution is integer or not. 
    if model.status != GRB.Status.INFEASIBLE:
        solution = model.getAttr('X', x)
        lp_int_count = check_if_integer(solution,m,grid,lp_int_count)
        
    return(lp_int_count)

def presolve_check_if_integer(sol,m,integer_count):
    '''
    Determines if the solution to the sudoku puzzle when solved via linear programming (without presolve) 
    is integer or not.
    
    Due to the Gurobi's tolerance level, a slightly different method must be used to search for fractional solutions
    when presolve is turned off. 
    
    Inputs: 
    sol: The solution to the sudoku puzzle found by linear programming.
    m: Integer representing the number of digits 1,...,m placed within the grid, 
       as well as the number of rows, columns and boxes in the grid. 
    integer_count: Binary value indicating if the solution contains fractions or not. 
                   Currently set to 0 as it has not yet been determined if the solution 
                   contains fractional values or not.
                   
    Outputs:
    integer_count: Binary variable - will return 0 if the solution contains fractions, and 
                   1 if solution is integer.
    '''
    is_integer = True
    
    # Verifies that all cells only have one digit assigned to them. 
    # If not, then the solution must be fractional and so the loops are broken and no more cells are considered.
    for i in range(m):
        for j in range(m):
            count = 0
            for k in range(m):
                if sol[i,j,k] >0:
                    count+=1
            if count != 1:
                is_integer = False
                break
                
    # If at least one fractional value has beeen found, the value of integer_count is set to 0.                            
    if is_integer == False:
        integer_count = 0
        
    return(integer_count)

def presolve_off_LP_solver(grid,m):
    '''
    Determines if the solution to the sudoku puzzle when solved via linear programming (without presolve) 
    is integer or not.
    
    Inputs: 
    grid: A list of lists representing the starting state of the sudoku puzzle to be solved.
    m: Integer representing the number of digits 1,...,m placed within the grid, 
       as well as the number of rows, columns and boxes in the grid. 
                   
    Outputs:
    integer_count: Binary variable - will return 0 if the solution contains fractions, and 
                   1 if solution is integer.
    '''
    integer_count = 1

    # Number of rows and columns in a box.
    p = int(np.sqrt(m))

    # Creating an empty model. 
    model = gp.Model('Sudoku Solver')
    
    # Turns off printing to console.
    # This line can be commented out if further details about the model are required.
    model.Params.LogToConsole = 0
   
    # Turning presolve off.
    model.params.Presolve = 0
    
    # Updates the above parameters of the model.
    model.update()

    # Defining the decision variables.
    x = model.addVars(m, m, m, vtype=GRB.CONTINUOUS, name='x')

    # Assign givens of the problem to their positions.
    # This is done by adjusting the lower bound.
    for i in range(m):
        for j in range(m):
            if grid[i][j] != '.':
                # Must subtract by 1 to account for the fact that indexing starts at 0. 
                k = int(grid[i][j]) - 1
                x[i, j, k].lb = 1
            # Set upper and lower bounds for remaining positions    
            else:
                for k in range(m):
                    x[i, j, k].lb = 0
                    x[i, j, k].ub = 1
                
                
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
    
    # Calls function presolve_check_if_integer to verify if the solution is integer or not.
    if model.status != GRB.Status.INFEASIBLE:
        solution = model.getAttr('X', x)
        integer_count = presolve_check_if_integer(solution,m,integer_count)
        
    return(integer_count)

#=================================== Driver Code ======================================

# To open the text file containing the sudoku puzzles.
f = open('Easy Sudokus.txt')

# Initializes variables that will store the total number sudokus within each category. 
total_integer_and_int_off_count = 0 
total_integer_and_no_int_off_count = 0
total_no_int_and_int_off_count = 0
total_no_int_and_no_int_count = 0

# Loops through all sudoku puzzles within the file. 
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
    sudoku = [initial_sudoku[i:i + 9] for i in range(0, len(initial_sudoku), 9)]
    
    integer_count = LP_solver(sudoku,m)
    presolve_off_integer_count = presolve_off_LP_solver(sudoku,m)
    
    # Increments the correct variable by one depending on results from the functions.
    if integer_count ==1 and presolve_off_integer_count ==1:
        total_integer_and_int_off_count += 1
    elif integer_count ==1 and presolve_off_integer_count ==0:
        total_integer_and_no_int_off_count += 1
    elif integer_count ==0 and presolve_off_integer_count ==1:
        total_no_int_and_int_off_count += 1
    else:
        total_no_int_and_no_int_count +=1
        
print("Number of sudoku solved to integer with and without presolve:",total_integer_and_int_off_count)
print("Number of sudoku solved to integer with presolve but not without:",total_integer_and_no_int_off_count)
print("Number of sudoku not solved to integer with presolve but is without:",total_no_int_and_int_off_count)
print("Number of sudoku not solved to integer with or without presolve:",total_no_int_and_no_int_count)