# Experiment to determine if any sudoku solving techniques (or a combination of any sudoku solving techniques) have an effect
# on the sufficiency of linear programming. 

# To be run on files within Data Set 3.

import numpy as np
import gurobipy as gp
from gurobipy import GRB

def check_if_integer(sol,m,grid,count):
    '''
    Determines if the solution to the sudoku puzzle when solved via linear programming is integer or not.
    
    Inputs: 
    sol: The solution to the sudoku puzzle found by linear programming.
    m: Integer representing the number of digits 1,...,m placed within the grid, 
       as well as the number of rows, columns and boxes in the grid. 
    count: Binary value indicating if the solution contains fractions or not. 
           Currently set to 0 as it has not yet been determined if the solution 
           contains fractional values or not.
                   
    Outputs:
    count: Binary variable - will return 1 if the solution contains fractions, and 
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

    # If at least one fractional value has been found, count is set to 1.                
    if is_integer == False:
        count = 1
    
    return(count)


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
    count: Binary variable - will return 1 if the solution contains fractions, and 
                   0 if solution is integer. 
    '''
    count = 0

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
        count = check_if_integer(solution,m,grid,count)
        
    return(count)


def presolve_check_if_integer(sol,m,grid,integer_count):
    '''
    Determines if the solution to the sudoku puzzle when solved via linear programming
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
    integer_count: Binary variable - will return 1 if the solution contains fractions, and 
                   0 if solution is integer.
    '''

    # Verifies that all cells only have one digit assigned to them. 
    # If not, then the solution must be fractional and so the loops are broken and no more cells are considered.
    is_integer = True
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
    # sets the value of integer count to 1.                  
    if is_integer == False:
        integer_count =1
        
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
        integer_count = presolve_check_if_integer(solution,m,grid,integer_count)
        
    return(integer_count)


#============================================Driver Code======================================================

# To open the text file containing the sudoku puzzles.
f = open("Expert Sudokus Correct.txt")

# Stores total number of sudokus that don't have integer solutions when solved via LP. 
total_count = 0

# Stores total number of sudokus that don't have integer solutions when solved via LP
# that require each technique.
singles_count = 0
hidden_singles_count = 0 
naked_pairs_count = 0
hidden_pairs_count = 0
pointing_pairs_triples_count = 0
box_line_intersections_count = 0
guesses_count = 0

# Stores the total number of sudokus that don't have integer solutions when solved via LP.
# Technique 1 = Hidden Singles
# Technique 2 = Naked Pairs
# Technique 3 = Hidden Pairs
# Technique 4 = Pointing Pairs/Triples
# Technique 5 = Box/Line Intersections. 
# All sudoku within the dataset require Singles. 
# Whether sudoku requires Guessing or not is dependent on what text file it is in. 
# Expert requires guessing, intermediate does not.
count_1 = 0
count_2 = 0
count_3 = 0
count_4 = 0
count_5 = 0
count_12 = 0
count_13 = 0
count_14 = 0
count_15 = 0
count_23 = 0
count_24 = 0
count_25 = 0
count_34 = 0
count_35 = 0
count_45 = 0
count_123 = 0
count_124 = 0
count_125 = 0
count_134 = 0
count_135 = 0
count_145 = 0
count_234 = 0
count_235 = 0
count_245 = 0
count_345 = 0
count_1234 = 0
count_1235 = 0
count_1245 = 0
count_1345 = 0
count_2345 = 0
count_12345 = 0
count_none = 0

# Loops through all sudoku puzzles within the file. 
while True:
    line = f.readline()
    
    # Terminates the loop when all sudokus have been solved. 
    if not line:
        print("Completed.")
        break
    
    # Storing each part of the sudoku and its required techniques.
    line.strip()
    new_line = line.split(",")
    puzzle = new_line[0]
    givens = int(new_line[1])
    singles = int(new_line[2])
    hidden_singles = int(new_line[3])
    naked_pairs = int(new_line[4])
    hidden_pairs = int(new_line[5])
    pointing_pairs_triples = int(new_line[6])
    box_line_intersections = int(new_line[7])
    guesses = int(new_line[8])
    backtracks = int(new_line[9])
    
    # Converting the sudoku to a list where each element is the starting state of a cell within the sudoku grid.
    initial_sudoku = list(puzzle)
    
    # The digits 1,...,m are those that need to be placed within the grid. 
    m = int(np.sqrt(len(initial_sudoku)))
    
    # Converts the sudoku to a list where each element represents a row of the sudoku puzzle. 
    sudoku = [initial_sudoku[i:i + 9] for i in range(0, len(initial_sudoku), 9)]
    
    lp_count = LP_solver(sudoku,m)
    without_presolve = presolve_off_LP_solver(sudoku,m)

    # If sudoku has fractional solutions when presolve is on or off,
    # then the total number of sudoku without integer solutions is increased by 1. 
    if lp_count == 1 or without_presolve == 1:
        count = 1
    else:
        count = 0
    total_count += count
    
    # If the sudoku does not have an integer solution, the counter specifying which combiantion of techniques it
    # requires is increased by one.
    if count == 1:
        
        if singles > 0:
            singles_count += 1
        if hidden_singles > 0:
            hidden_singles_count += 1
        if naked_pairs > 0:
            naked_pairs_count += 1
        if hidden_pairs > 0:
            hidden_pairs_count += 1
        if pointing_pairs_triples > 0:
            pointing_pairs_triples_count += 1
        if box_line_intersections > 0:
            box_line_intersections_count += 1
        if guesses > 0:
            guesses_count += 1
            
            
        if hidden_singles > 0 and naked_pairs == 0 and hidden_pairs == 0 and pointing_pairs_triples == 0 and box_line_intersections == 0:
            count_1 += 1
        elif hidden_singles == 0 and naked_pairs > 0 and hidden_pairs == 0 and pointing_pairs_triples == 0 and box_line_intersections == 0:
            count_2 += 1
        elif hidden_singles == 0 and naked_pairs == 0 and hidden_pairs > 0 and pointing_pairs_triples == 0 and box_line_intersections == 0:
            count_3 += 1
        elif hidden_singles == 0 and naked_pairs == 0 and hidden_pairs == 0 and pointing_pairs_triples > 0 and box_line_intersections == 0:
            count_4 += 1
        elif hidden_singles == 0 and naked_pairs == 0 and hidden_pairs == 0 and pointing_pairs_triples == 0 and box_line_intersections > 0:
            count_5 += 1
        elif hidden_singles > 0 and naked_pairs > 0 and hidden_pairs == 0 and pointing_pairs_triples == 0 and box_line_intersections == 0:
            count_12 += 1
        elif hidden_singles > 0 and naked_pairs == 0 and hidden_pairs > 0 and pointing_pairs_triples == 0 and box_line_intersections == 0:
            count_13 += 1
        elif hidden_singles > 0 and naked_pairs == 0 and hidden_pairs == 0 and pointing_pairs_triples > 0 and box_line_intersections == 0:
            count_14 += 1
        elif hidden_singles > 0 and naked_pairs == 0 and hidden_pairs == 0 and pointing_pairs_triples == 0 and box_line_intersections > 0:
            count_15 += 1
        elif hidden_singles == 0 and naked_pairs > 0 and hidden_pairs > 0 and pointing_pairs_triples == 0 and box_line_intersections == 0:
            count_23 += 1
        elif hidden_singles == 0 and naked_pairs > 0 and hidden_pairs == 0 and pointing_pairs_triples > 0 and box_line_intersections == 0:
            count_24 += 1
        elif hidden_singles == 0 and naked_pairs > 0 and hidden_pairs == 0 and pointing_pairs_triples == 0 and box_line_intersections > 0:
            count_25 += 1
        elif hidden_singles == 0 and naked_pairs == 0 and hidden_pairs > 0 and pointing_pairs_triples > 0 and box_line_intersections == 0:
            count_34 += 1
        elif hidden_singles == 0 and naked_pairs == 0 and hidden_pairs > 0 and pointing_pairs_triples == 0 and box_line_intersections > 0:
            count_35 += 1
        elif hidden_singles == 0 and naked_pairs == 0 and hidden_pairs == 0 and pointing_pairs_triples > 0 and box_line_intersections > 0:
            count_45 += 1
        elif hidden_singles > 0 and naked_pairs > 0 and hidden_pairs > 0 and pointing_pairs_triples == 0 and box_line_intersections == 0:
            count_123 += 1  
        elif hidden_singles > 0 and naked_pairs > 0 and hidden_pairs == 0 and pointing_pairs_triples > 0 and box_line_intersections == 0:
            count_124 += 1
        elif hidden_singles > 0 and naked_pairs > 0 and hidden_pairs == 0 and pointing_pairs_triples == 0 and box_line_intersections > 0:
            count_125 += 1
        elif hidden_singles > 0 and naked_pairs == 0 and hidden_pairs > 0 and pointing_pairs_triples > 0 and box_line_intersections == 0:
            count_134 += 1
        elif hidden_singles > 0 and naked_pairs == 0 and hidden_pairs > 0 and pointing_pairs_triples == 0 and box_line_intersections > 0:
            count_135 += 1
        elif hidden_singles > 0 and naked_pairs == 0 and hidden_pairs == 0 and pointing_pairs_triples > 0 and box_line_intersections > 0:
            count_145 += 1
        elif hidden_singles == 0 and naked_pairs > 0 and hidden_pairs > 0 and pointing_pairs_triples > 0 and box_line_intersections == 0:
            count_234 += 1
        elif hidden_singles == 0 and naked_pairs > 0 and hidden_pairs > 0 and pointing_pairs_triples == 0 and box_line_intersections > 0:
            count_235 += 1
        elif hidden_singles == 0 and naked_pairs > 0 and hidden_pairs == 0 and pointing_pairs_triples > 0 and box_line_intersections > 0:
            count_245 += 1
        elif hidden_singles == 0 and naked_pairs == 0 and hidden_pairs > 0 and pointing_pairs_triples > 0 and box_line_intersections > 0:
            count_345 += 1
        elif hidden_singles > 0 and naked_pairs > 0 and hidden_pairs > 0 and pointing_pairs_triples > 0 and box_line_intersections == 0:
            count_1234 += 1
        elif hidden_singles > 0 and naked_pairs > 0 and hidden_pairs > 0 and pointing_pairs_triples == 0 and box_line_intersections > 0:
            count_1235 += 1
        elif hidden_singles > 0 and naked_pairs > 0 and hidden_pairs == 0 and pointing_pairs_triples > 0 and box_line_intersections > 0:
            count_1245 += 1
        elif hidden_singles > 0 and naked_pairs == 0 and hidden_pairs > 0 and pointing_pairs_triples > 0 and box_line_intersections > 0:
            count_1345 += 1
        elif hidden_singles == 0 and naked_pairs > 0 and hidden_pairs > 0 and pointing_pairs_triples > 0 and box_line_intersections > 0:
            count_2345 += 1
        elif hidden_singles > 0 and naked_pairs > 0 and hidden_pairs > 0 and pointing_pairs_triples > 0 and box_line_intersections > 0:
            count_12345 += 1
        else:
            count_none += 1
        
    
print("Number of sudokus that cannot be solved to integer with LP:", total_count)
print("\nNumber of sudokus that cannot be solved to integer with LP requiring \"Singles\":", singles_count)
print("Number of sudokus that cannot be solved to integer with LP requiring \"Hidden Singles\":", hidden_singles_count)
print("Number of sudokus that cannot be solved to integer with LP requiring \"Naked Pairs\":", naked_pairs_count)
print("Number of sudokus that cannot be solved to integer with LP requiring \"Hidden Pairs\":", hidden_pairs_count)
print("Number of sudokus that cannot be solved to integer with LP requiring \"Pointing Pairs/Triples\":", pointing_pairs_triples_count)
print("Number of sudokus that cannot be solved to integer with LP requiring \"Box/Line Intersections\":", box_line_intersections_count)
print("Number of sudokus that cannot be solved to integer with LP requiring \"Guessing\":", guesses_count)

print("Number of sudoku that can't be solved and have properties:")
print("1:",count_1)
print("2:",count_2)
print("3:",count_3)
print("4:",count_4)
print("5:",count_5)
print("12:",count_12)
print("13:",count_13)
print("14:",count_14)
print("15:",count_15)
print("23:",count_23)
print("24:",count_24)
print("25:",count_25)
print("34:",count_34)
print("35:",count_35)
print("45:",count_45)
print("123:",count_123)
print("124:",count_124)
print("125:",count_125)
print("134:",count_134)
print("135:",count_135)
print("145:",count_145)
print("234:",count_234)
print("235:",count_235)
print("245:",count_245)
print("345:",count_345)
print("1234:",count_1234)
print("1235:",count_1235)
print("1245:",count_1245)
print("1345:",count_1345)
print("2345:",count_2345)
print("12345:",count_12345)
print("None (just singles):",count_none)