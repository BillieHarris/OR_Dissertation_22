# Conducting a combined experiment to determine the number of sudoku puzzles within a dataset whose feasible
# regions when solved by LP contain only a single point (sorted by whether it is solved to integer by LP 
# (both when presolve is called and when it is not) or not).

# Initially, for the one million sudoku puzzles, a sudoku was considered to have integer solutions only if it was solved to 
# integer when presolve was on (as this is the default setting for Gurobi). However, this interpretation changed after 
# studying puzzles from Data Set 1. Hence, now this experiment only considers a sudoku puzzle to have integer solutions when 
# it has integer solutions to both when presolve is on and off. 


import numpy as np
import gurobipy as gp
from gurobipy import GRB

def check_if_integer(sol,m,integer_count):
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
    integer_count: Binary variable - will return 0 if the solution contains fractions, and 
                   1 if solution is integer.
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
        integer_count = 0

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
    
    # Calls the function check_if_integer to verify if the solution is integer or not. 
    if model.status != GRB.Status.INFEASIBLE:
        solution = model.getAttr('X', x)
        integer_count = check_if_integer(solution,m,integer_count)

        
    return(integer_count)

def presolve_check_if_integer(sol,m,grid,integer_count):
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
    
    # If at least one fractional value has beeen found, the puzzle is outputed to the user and 
    # sets the value of integer count to 0.                  
    if is_integer == False:
        integer_count =0
        
    return(integer_count)

def presolve_off_LP_solver(grid,m):
    
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
            # Set upper and lower bounds for remaining variables.    
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
                    for c in range(p)), name='Box')

    # Each cell within the grid must have a number assigned to it. 
    model.addConstrs((x.sum(i, j, '*') == 1 for i in range(m) for j in range(m)), name='Square')

    # Since it is a constraint satisfaction (or feasibility) problem, no objective function is required.
    model.optimize()
    
    # Calls function presolve_check_if_integer to verify if the solution is integer or not.  
    if model.status != GRB.Status.INFEASIBLE:
        solution = model.getAttr('X', x)
        integer_count = presolve_check_if_integer(solution,m,grid,integer_count)
        
    return(integer_count)

def IP_Solver(grid,m):
    '''
    Finds the integer solution for the sudoku problem. As it has already been determined that these sudoku are proper, 
    the number of valid solutions to this problem does not need to be calculated. 
    
    Inputs:
    grid: A list of lists representing the starting state of the sudoku puzzle to be solved.
    m: Integer representing the number of digits 1,...,m placed within the grid, 
       as well as the number of rows, columns and boxes in the grid.
       
    Outputs:
    solution: The integer soluotion to the IP problem. 
    '''

    # Number of rows and columns in a box.
    p = int(np.sqrt(m))

    # Creating an empty model. 
    model = gp.Model('Sudoku Solver')

    # Turns off printing to console. 
    # This line can be commented out if further details about the model are required.
    model.Params.LogToConsole = 0
    
    # Updates the above parameter of the model.
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

    # Only one of each number can be found in a box. 
    # Here, the bounds are changed to account for the fact that indexing in python starts at 0 and not 1. 
    model.addConstrs((sum(x[i, j, k] for i in range(r*p, (r+1)*p)
                    for j in range(c*p, (c+1)*p)) == 1 for k in range(m) for r in range(p)
                    for c in range(p)), name='Box')

    # Each cell within the grid must have only one digit assigned to it. 
    model.addConstrs((x.sum(i, j, '*') == 1 for i in range(m) for j in range(m)), name='Cell')

    # Since it is a constraint satisfaction (or feasibility) problem, no objective function is required.
    model.optimize()

    solution = model.getAttr('X', x)
    
    return(solution)

def feasible_direction_test(grid,m,sol):
    '''
    Determines if a feasible direction from the known integer point within the feasible direction exists or not. 
    
    Inputs:
    grid: A list of lists representing the starting state of the sudoku puzzle to be solved.
    m: Integer representing the number of digits 1,...,m placed within the grid, 
       as well as the number of rows, columns and boxes in the grid.
    sol: Solution to the sudoku problem when solved via integer programming. 
    
    Outputs:
    direction: Binary variable - will return 0 if no feasible direction is found, and 1 if 
               a feasible direction does exist. 
    '''
    direction = 0
    
    # Number of rows and columns in a box.
    p = int(np.sqrt(m))
    
    # Creating an empty model. 
    d_model = gp.Model('Direction Model')
    
    # Turn off printing to the console. 
    # This line can be commented out if further details about the model are required.              
    d_model.Params.LogToConsole = 0
    
    # Updates this parameter of the model. 
    d_model.update()
    
    # Defining the continous decision variables. 
    d = d_model.addVars(m,m,m,vtype = GRB.CONTINUOUS, name = 'direction')

    for j in range(m):
        for k in range(m):
            # Ensuring that the givens remain fixed. 
            if grid[i][j] != '.':
            # Must subtract by 1 to account for the fact that indexing starts at 0. 
                if k == int(grid[i][j]) - 1:
                    d[i, j, k].lb = 0
                    d[i ,j ,k].ub = 0
                        
                # Otherwise we just need to set bounds on d to ensure we are 
                # searching in the correct direction to see if another feasible point exists.
            else:
                if sol[i,j,k]<0.5:
                    # As d must be non-negative if x = 0.
                    d[i,j,k].lb = 0
                    d[i,j,k].ub = 1
                    
                else: 
                    # As d must be non-positive if x = 1.
                    d[i,j,k].ub = 0
                    d[i,j,k].lb = -1
                        
            
                    
    #Constraints ensuring that Ad = 0. 
    d_model.addConstrs((d.sum(i, '*', k) == 0 for i in range(m) for k in range(m)), name='Row')
    
    d_model.addConstrs((d.sum('*', j, k) == 0 for j in range(m) for k in range(m)), name='Column')
    
    d_model.addConstrs((sum(d[i, j, k] for i in range(r*p, (r+1)*p)
                    for j in range(c*p, (c+1)*p)) == 0 for k in range(m) for r in range(p)
                    for c in range(p)), name='Sub_Matrix')
    
    d_model.addConstrs((d.sum(i, j, '*') == 0 for i in range(m) for j in range(m)), name='Square')
    
                
                
    # The additional constraint to rule out d = 0. 
    # To do this we set norm of d to be 1.
    d_norm = d_model.addVar()
    d_model.addConstr(d_norm == gp.norm(d,1.0))
    d_norm.lb = 1
    d_norm.ub = 1
    
    # This is a feasibility problem and hence no objective function is required. 
    d_model.optimize()
    
    # If the problem is not infeasible then a feasible direction has been found. 
    # Hence, the value of the direction variable is incremented by 1.
    if d_model.Status != GRB.Status.INFEASIBLE:
        direction +=1
        
    return(direction)

#===============================Driver Code===============================

# To open the text file containing the sudoku puzzles.
f = open('Easy Sudokus.txt')

# Initializes variables that will store the total number sudokus within each category. 
total_integer_and_d_count = 0 
total_integer_and_no_d_count = 0
total_no_integer_and_d_count = 0
total_no_integer_and_no_d_count = 0

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
    
    lp_integer_count = LP_solver(sudoku,m)
    presolve_off_integer_count = presolve_off_LP_solver(sudoku,m)
    IP_sol = IP_solver(sudoku,m)
    d_count = feasible_direction_test(sudoku,m,IP_sol)
    
    # If the puzzle has integer solutions to the LP problem when both presolve is on and off,
    # the puzzle is determined to have integer solutions. 
    if (lp_integer_count + presolve_off_integer_count) == 2:
        integer_count = 1
    else:
        integer_count = 0
     
    # Increments the correct variable by one depending on results from the functions.
    if integer_count == 1 and d_count == 1:
        total_integer_and_d_count += 1
    elif integer_count == 1 and d_count == 0:
        total_integer_and_no_d_count += 1
    elif integer_count == 0 and d_count == 1:
        total_no_integer_and_d_count += 1
    else: 
        total_no_integer_and_no_d_count +=1
        
print("Number of sudoku solved to integer and have a feasible direction:",total_integer_and_d_count)
print("Number of sudoku solved to integer and do not have a feasible direction:",total_integer_and_no_d_count)
print("Number of sudoku not solved to integer and have a feasible direction:",total_no_integer_and_d_count)
print("Number of sudoku not solved to integer and do not have a feasible direction:",total_no_integer_and_no_d_count)
