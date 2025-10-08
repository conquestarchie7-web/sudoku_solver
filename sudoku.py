"""
Implementation of Sudoku Solver 

Plan: 
    1. Load CSV with 1 million sudoku puzzles and choose one at random.
    2.  First use efficient but limited Single candidate method.
     - For each cell in the sudoku grid, create a node with its value (null or given) and possible values.
     - Iterate for each cell, check row, column and box for existing values and remove from possible values.
     - If a cell has only one possible value remaining, set it to that value.
    3. Once iterated until solved or algorithm can no longer make progress, use brute force backtracking to solve the rest.
     
"""


# Import pandas and numpy for data handling, random for random puzzle selection
import pandas as pd
import numpy as np
import random 

# Define the CSV file name 
FILE_NAME = 'sudoku.csv'
PUZZLE_COLUMN_NAME = 'quizzes'

# CONVERSION FUNCTION 
def string_to_grid(puzzle_string):
    """Converts an 81-digit string into a 9x9 NumPy array of integers."""
    return np.array(list(puzzle_string), dtype=int).reshape(9, 9)

# ATTEMPT TO LOAD A RANDOM PUZZLE, CONVERT TO GRID AND APPLY SINGLE CANDIDATE ALGORITHM
try:
    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(FILE_NAME)
    total_puzzles = len(df)

    # Select a random index number between 0 and (total_puzzles - 1)
    random_index = random.randint(0, total_puzzles - 1)

    # Get the single puzzle string using the random index
    random_puzzle_string = df[PUZZLE_COLUMN_NAME].iloc[random_index]
    # random_puzzle_string = '800000000003600000070090200050007000000045700000100030001000090000050100400000000' # For testing purposes

    # Convert the string into a 9x9 NumPy array, we will call it 'grid'
    grid = string_to_grid(random_puzzle_string)

    # Print the result 
    print(f"Successfully loaded a random puzzle (Index: {random_index} of {total_puzzles - 1}):")
    print("\n--- Random Puzzle ---")
    print(grid)

    # HELPER FUNCTION FOR BOX START INDEX
    def get_box_start(index):
        """ Calculates the starting row or column index of a 3x3 box. """
        return (index // 3) * 3

    # SIMPLE SUDOKU SOLVING ALGORITHM (SINGLE CANDIDATE METHOD)
    def simple_algorithm(grid):
        """ A simple Sudoku solving algorithm that fills in cells with only one possible value. """

        grid_changed = False
    
        # Continuously loop until a full pass results in no changes
        while True:
            # We assume no change is made in this pass
            made_a_placement = False
            
            # --- Step 1 & 2: Calculate Possible Values (Candidates) for all empty cells ---
            # This structure acts as your "node with possible values"
            candidates = {}  # candidates[(r, c)] = set of possible values
            
            # Iterate over all 81 cells
            for r in range(9):
                for c in range(9):
                    if grid[r, c] == 0:  # If the cell is empty
                        
                        # Start with all possible values (1 to 9)
                        possible_values = set(range(1, 10))
                        
                        # Check Row: Remove existing values from possible_values
                        # The grid[r, :] slice is the entire row
                        possible_values.difference_update(grid[r, :])
                        
                        # Check Column: Remove existing values
                        # The grid[:, c] slice is the entire column
                        possible_values.difference_update(grid[:, c])
                        
                        # Check 3x3 Box: Remove existing values
                        r_start = get_box_start(r)
                        c_start = get_box_start(c)
                        box = grid[r_start:r_start+3, c_start:c_start+3]
                        possible_values.difference_update(box.flatten())
                        
                        # Store the remaining candidates
                        candidates[(r, c)] = possible_values
            
            # --- Step 3: Check for Naked Singles (Only one candidate for a cell) ---
            for (r, c), possible_values in candidates.items():
                if len(possible_values) == 1:
                    # Found a Naked Single!
                    value = possible_values.pop()
                    grid[r, c] = value
                    made_a_placement = True
                    grid_changed = True
                    
            # If we made a change, we break this inner loop and start the process over 
            # to re-evaluate all candidates based on the new number placed.
            if made_a_placement:
                continue
                
            # --- Check for Hidden Singles (Only one cell in a unit can hold a value) ---
            # If no Naked Singles were found, we look for Hidden Singles
            for value in range(1, 10):
                # Check Rows
                for r in range(9):
                    # Get all empty cells in this row
                    empty_cells = [(r, c) for c in range(9) if grid[r, c] == 0]
                    
                    # Check which of these empty cells can accept 'value'
                    can_hold_value = [(r, c) for r_cell, c_cell in empty_cells if value in candidates[(r_cell, c_cell)]]

                    if len(can_hold_value) == 1:
                        # Found a Hidden Single in the row!
                        r_place, c_place = can_hold_value[0]
                        grid[r_place, c_place] = value
                        made_a_placement = True
                        grid_changed = True
                        
                # Check Columns (similar logic)
                for c in range(9):
                    empty_cells = [(r, c) for r in range(9) if grid[r, c] == 0]
                    can_hold_value = [(r, c) for r_cell, c_cell in empty_cells if value in candidates[(r_cell, c_cell)]]
                    if len(can_hold_value) == 1:
                        r_place, c_place = can_hold_value[0]
                        grid[r_place, c_place] = value
                        made_a_placement = True
                        grid_changed = True
                        
                # Check Boxes (similar logic)
                for r_start in range(0, 9, 3):
                    for c_start in range(0, 9, 3):
                        # Find all empty cells in this box
                        box_empty_cells = []
                        for r in range(r_start, r_start + 3):
                            for c in range(c_start, c_start + 3):
                                if grid[r, c] == 0:
                                    box_empty_cells.append((r, c))
                        
                        # Check which of these empty cells can accept 'value'
                        can_hold_value = [(r, c) for r_cell, c_cell in box_empty_cells if value in candidates[(r_cell, c_cell)]]

                        if len(can_hold_value) == 1:
                            r_place, c_place = can_hold_value[0]
                            grid[r_place, c_place] = value
                            made_a_placement = True
                            grid_changed = True
            
            # If we made a placement in either the Naked or Hidden Single checks, 
            # restart the whole candidate generation loop
            if made_a_placement:
                continue
            else:
                # If no placements were made in an entire pass, the puzzle is either 
                # solved, or we need advanced techniques.
                break

        return grid, grid_changed


    # Apply the simple algorithm
    solved_SC_grid, solved_fully = simple_algorithm(grid.copy()) # Use .copy() to avoid modifying the original

    print("\n--- Partially/Fully Solved Grid (Single Candidate Method) ---")
    print(solved_SC_grid)

    print("\nWould you like to BRUTE FORCE puzzle to solutution? (y to continue, any other key to exit)")
    BF_response = input()
    if(BF_response == 'y'):
        print("Beginning now...")
    else:
        print("Exiting program.")
        exit()

except FileNotFoundError:
    print(f"Error: The file '{FILE_NAME}' was not found. Please ensure the CSV is in the same folder.")
except KeyError:
    print(f"Error: Column '{PUZZLE_COLUMN_NAME}' not found in the CSV. Check the column name in your file.")