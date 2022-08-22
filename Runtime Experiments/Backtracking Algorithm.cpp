// Backtracking algorithm created and taken from: https://www.geeksforgeeks.org/sudoku-backtracking-7/
// Driver code has been edited to take in sudoku of the form found in the dataset of the 4000 sudoku
// and additions were made to calculate the length of time taken for the solver to find a solution to each sudoku puzzle. 

#include <iostream>
#include <vector>
#include <algorithm>
#include <memory>
#include <fstream> 
#include <ctime>
#include <bits/stdc++.h>
#include <list>
#include <stdio.h>
#include <time.h>
#include <chrono>
using namespace std;

// UNASSIGNED is used for empty
// cells in sudoku grid
#define UNASSIGNED 0

// N is used for the size of Sudoku grid.
// Size will be NxN
#define N 9

// This function finds an entry in grid
// that is still unassigned
bool FindUnassignedLocation(int grid[N][N],
							int& row, int& col);

// Checks whether it will be legal
// to assign num to the given row, col
bool isSafe(int grid[N][N], int row,
			int col, int num);

/* Takes a partially filled-in grid and attempts
to assign values to all unassigned locations in
such a way to meet the requirements for
Sudoku solution (non-duplication across rows,
columns, and boxes) */
bool SolveSudoku(int grid[N][N])
{
	int row, col;

	// If there is no unassigned location,
	// we are done
	if (!FindUnassignedLocation(grid, row, col))
		// success!
		return true;

	// Consider digits 1 to 9
	for (int num = 1; num <= 9; num++)
	{
		
		// Check if looks promising
		if (isSafe(grid, row, col, num))
		{
			
			// Make tentative assignment
			grid[row][col] = num;

			// Return, if success
			if (SolveSudoku(grid))
				return true;

			// Failure, unmake & try again
			grid[row][col] = UNASSIGNED;
		}
	}
	
	// This triggers backtracking
	return false;
}

/* Searches the grid to find an entry that is
still unassigned. If found, the reference
parameters row, col will be set the location
that is unassigned, and true is returned.
If no unassigned entries remain, false is returned. */
bool FindUnassignedLocation(int grid[N][N],
							int& row, int& col)
{
	for (row = 0; row < N; row++)
		for (col = 0; col < N; col++)
			if (grid[row][col] == UNASSIGNED)
				return true;
	return false;
}

/* Returns a boolean which indicates whether
an assigned entry in the specified row matches
the given number. */
bool UsedInRow(int grid[N][N], int row, int num)
{
	for (int col = 0; col < N; col++)
		if (grid[row][col] == num)
			return true;
	return false;
}

/* Returns a boolean which indicates whether
an assigned entry in the specified column
matches the given number. */
bool UsedInCol(int grid[N][N], int col, int num)
{
	for (int row = 0; row < N; row++)
		if (grid[row][col] == num)
			return true;
	return false;
}

/* Returns a boolean which indicates whether
an assigned entry within the specified 3x3 box
matches the given number. */
bool UsedInBox(int grid[N][N], int boxStartRow,
			int boxStartCol, int num)
{
	for (int row = 0; row < 3; row++)
		for (int col = 0; col < 3; col++)
			if (grid[row + boxStartRow]
					[col + boxStartCol] ==
									num)
				return true;
	return false;
}

/* Returns a boolean which indicates whether
it will be legal to assign num to the given
row, col location. */
bool isSafe(int grid[N][N], int row,
			int col, int num)
{
	/* Check if 'num' is not already placed in
	current row, current column
	and current 3x3 box */
	return !UsedInRow(grid, row, num)
		&& !UsedInCol(grid, col, num)
		&& !UsedInBox(grid, row - row % 3,
						col - col % 3, num)
		&& grid[row][col] == UNASSIGNED;
}

/* A utility function to print grid */
void printGrid(int grid[N][N])
{
	for (int row = 0; row < N; row++)
	{
		for (int col = 0; col < N; col++)
			cout << grid[row][col] << " ";
		cout << endl;
	}
}

// ==================================== Driver Code ===============================================
int main()
{
    
    // Opening the text file containing the sudoku puzzles to be solved. 
    file_to_open.open("Diabolical Sudokus.txt",ios::in);
    
    string line;
    
	while(getline(file_to_open,line)){
	    
	    // ================Setting up one sudoku grid. ======================	    
	    
	    // Existing code to convert input from file and convert to an array to be solved. 
	    int sudoku_grid[9][9];
    
            for (int r = 0; r < 9; r++) //Outer loop for rows
            {
            	for (int c = 0; c < 9; c++) //inner loop for columns
            	{
                	int index = (r*9)+c;
                	
                	sudoku_grid[r][c] = stoi(line.substr(index,1));  //Take input from file and put into array
            
            	}
            }	
	
	    
            // Initialize a counter to ensure that each sudoku puzzle is solved 10 times to ensure measurability and repeatability.
            int loop = 0;
        
            // Stores the time taken to solve the sudoku puzzles 10 times. 
            double one_sudoku_time = 0;

            while (loop < 10)
            {
        
            	// Declare clock_t type variable to store current time at the START of the function.
            	clock_t start;
            
            	// Declare clock_t type variable to store current time at the END of the function.
            	clock_t end;
        
            	// Declare the time between start and end of the function.
            	double length;

            	// Store the time at the START of the function.
            	start = clock();
        
        	// Calls the function to solve the sudoku puzzle.
            	SolveSudoku(sudoku_grid);
    
            	// Store the time at the END of the function.
            	end = clock();
            
            // Calculating the time in seconds for which the function took to solve the sudoku puzzle.
            length = (end - start) / (double) CLOCKS_PER_SEC;

            // Adding the time taken to solve this sudoku puzzle once to the total time for the previous times this sudoku puzzle was solved.
            one_sudoku_time += length;
            
            loop += 1;
        }
	
	// Outputs the average time taken to solve one sudoku puzzle to the terminal. 
        cout << fixed <<one_sudoku_time/10 << endl;

        
        }
	

	return 0;
}
