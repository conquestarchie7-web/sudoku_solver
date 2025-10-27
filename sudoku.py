import pandas as pd
import numpy as np
import random
import time  
import csv 
import os

class SudokuSolver:
    
    def __init__(self, filepath):
        
        # Constructor: Initializes the solver, keeps a copy of the original board
        self.filepath = filepath
        self.board = self.load_puzzle(filepath)
        self.original_board = self.board.copy() 
        
        # Metrics
        self.start_time = 0
        self.end_time = 0
        self.recursive_calls = 0
        self.backtracks = 0

    def load_puzzle(self, filepath):
        """
        Loads a puzzle from a .txt or .csv file
        0, ' ', or '.' are treated as empty
        Iterates through file and appends to board list
        """
        board = []
        try:
            with open(filepath, 'r') as f:
                # First determine file type, start with CSV
                if filepath.endswith('.csv'):
                    reader = csv.reader(f)
                    for row in reader:
                        board.append([int(c) if c.isdigit() and c != '0' else 0 for c in row])
                else: # Assume .txt
                    for line in f:
                        line = line.strip()
                        if not line: continue
                        # Handle comma-separated or just characters
                        cells = line.split(',') if ',' in line else list(line)
                        row = [int(c.strip()) if c.strip().isdigit() and c.strip() != '0' else 0 for c in cells]
                        if len(row) == 9:
                            board.append(row)
            
            # Validating board size
            if len(board) != 9 or any(len(r) != 9 for r in board):
                raise ValueError("Puzzle must be a 9x9 grid.")
            
            print(f"Successfully loaded puzzle from: {filepath}")
            # Convert to numpy array
            return np.array(board, dtype=int)

        except FileNotFoundError:
            print(f"Error: File not found at {filepath}")
            exit(1)
        except Exception as e:
            print(f"Error loading puzzle: {e}")
            exit(1)

    def print_board(self, board=None):
        # Prints the board in a readable format
        if board is None:
            board = self.board
            
        print("\n+-------+-------+-------+")
        for i in range(9):
            if i % 3 == 0 and i != 0:
                print("|-------+-------+-------|")
            row_str = "| "
            for j in range(9):
                if j % 3 == 0 and j != 0:
                    row_str += "| "
                cell = str(board[i, j]) if board[i, j] != 0 else '.'
                row_str += cell + " "
            row_str += "|"
            print(row_str)
        print("+-------+-------+-------+")
    
    def is_valid_placement(self, grid, row, col, num):
        """Checks if placing 'num' at (row, col) is valid"""
        # Check Row
        if num in grid[row, :]:
            return False
        # Check Column
        if num in grid[:, col]:
            return False
        # Check 3x3 Box
        r_start = (row // 3) * 3
        c_start = (col // 3) * 3
        if num in grid[r_start:r_start+3, c_start:c_start+3]:
            return False
        return True

    def find_empty_cell(self, grid):
        """Finds the next empty cell (0)"""
        for r in range(9):
            for c in range(9):
                if grid[r, c] == 0:
                    return r, c
        return None
    
    def _solve_backtracking(self):
        """Recursive solver"""
        
        # Metric 1: Count recursive calls
        self.recursive_calls += 1

        empty_cell = self.find_empty_cell(self.board)
        if not empty_cell:
            return True  # Base case: Solved

        row, col = empty_cell

        for num in range(1, 10):
            if self.is_valid_placement(self.board, row, col, num):
                self.board[row, col] = num

                if self._solve_backtracking():  
                    return True # Solution found

                # Metric 2: Count backtracks
                self.backtracks += 1
                self.board[row, col] = 0 # Backtrack

        return False # Triggers backtracking

    def solve(self):
        """Public method to run the solver and print metrics"""
        print("Initial Board:")
        self.print_board(self.original_board)
        
        # Metric 3: Track execution time
        self.start_time = time.perf_counter()
        
        if self._solve_backtracking():
            self.end_time = time.perf_counter()
            print("\n--- Sudoku Solved! ---")
            self.print_board(self.board)
        else:
            self.end_time = time.perf_counter()
            print("\n--- No solution exists for this puzzle. ---")
            
        self.print_metrics()

    def print_metrics(self):
        """Prints all collected performance metrics."""
        total_time_ms = (self.end_time - self.start_time) * 1000
        print("\n--- Solver Metrics ---")
        print(f"Total Execution Time: {total_time_ms:.4f} ms")
        print(f"Total Recursive Calls: {self.recursive_calls}")
        print(f"Total Backtracks:      {self.backtracks}")


# EXECUTION CODE

# 1. Create a puzzle
puzzle_content = """
5,3,0,0,7,0,0,0,0
6,0,0,1,9,5,0,0,0
0,9,8,0,0,0,0,6,0
8,0,0,0,6,0,0,0,3
4,0,0,8,0,3,0,0,1
7,0,0,0,2,0,0,0,6
0,6,0,0,0,0,2,8,0
0,0,0,4,1,9,0,0,5
0,0,0,0,8,0,0,7,9
"""

# Create file
try:
    with open("puzzle.txt", "w") as f:
        f.write(puzzle_content.strip())
except IOError as e:
    print(f"Could not write puzzle file: {e}")

# 2. Run the solver
if __name__ == "__main__":
    
    # You can point this to any compatible .txt or .csv file 
    puzzle_file = "puzzle.txt" 
    
    # Check if file exists and Execute solver
    if os.path.exists(puzzle_file):
        solver = SudokuSolver(puzzle_file)
        solver.solve()
    else:
        print(f"Sample file '{puzzle_file}' not found. Please create it.")
