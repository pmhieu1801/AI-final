from pysat.solvers import Glucose3
from model import SudokuGrid, VariableMapper
from problem import SudokuClauseGenerator

class SudokuAgent:
    """
    The Agent that takes a Sudoku matrix and returns a solution.
    """
    def solve(self, matrix):
        # 1. Create Grid Model
        input_grid = SudokuGrid(matrix)

        # 2. Generate CSP/CNF Clauses
        generator = SudokuClauseGenerator()
        clauses = generator.get_cnf(input_grid)

        # 3. Initialize Solver (Glucose3)
        solver = Glucose3()
        for clause in clauses:
            solver.add_clause(clause)

        # 4. Solve
        is_satisfiable = solver.solve()

        if not is_satisfiable:
            print("No solution found.")
            return None

        # 5. Extract Model
        model_vars = solver.get_model()

        # 6. Convert SAT Model back to Sudoku Grid
        solution_matrix = [[0]*9 for _ in range(9)]

        for var_id in model_vars:
            if var_id > 0: # Only True variables matter
                r, c, v = VariableMapper.to_rcv(var_id)
                solution_matrix[r][c] = v

        solver.delete()
        return SudokuGrid(solution_matrix)
