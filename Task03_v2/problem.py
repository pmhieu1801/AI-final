from model import VariableMapper
import itertools

class SudokuClauseGenerator:
    """
    Generates CNF clauses for the Sudoku CSP.
    """
    def __init__(self):
        self.clauses = []

    def _add_cell_constraints(self):
        """
        1. Definedness: Each cell has at least one value (1-9).
        2. Uniqueness: Each cell has at most one value.
        """
        for r in range(9):
            for c in range(9):
                # Definedness: (X_rc1 v X_rc2 ... v X_rc9)
                self.clauses.append([VariableMapper.to_var(r, c, v) for v in range(1, 10)])

                # Uniqueness: (~X_rcj v ~X_rck) for j != k
                # If cell has val j, it cannot have val k
                for j in range(1, 10):
                    for k in range(j + 1, 10):
                        self.clauses.append([
                            -VariableMapper.to_var(r, c, j),
                            -VariableMapper.to_var(r, c, k)
                        ])

    def _add_line_constraints(self):
        """
        Each value (1-9) appears at most once in each Row and Column.
        """
        for v in range(1, 10):
            # Row constraints
            for r in range(9):
                for c1 in range(9):
                    for c2 in range(c1 + 1, 9):
                        self.clauses.append([
                            -VariableMapper.to_var(r, c1, v),
                            -VariableMapper.to_var(r, c2, v)
                        ])

            # Column constraints
            for c in range(9):
                for r1 in range(9):
                    for r2 in range(r1 + 1, 9):
                        self.clauses.append([
                            -VariableMapper.to_var(r1, c, v),
                            -VariableMapper.to_var(r2, c, v)
                        ])

    def _add_box_constraints(self):
        """
        Each value (1-9) appears at most once in each 3x3 Box.
        """
        for v in range(1, 10):
            for box_r in range(0, 9, 3):
                for box_c in range(0, 9, 3):
                    # Collect cells in this 3x3 box
                    cells = []
                    for r in range(3):
                        for c in range(3):
                            cells.append((box_r + r, box_c + c))

                    # Pairwise constraints within box
                    for i in range(len(cells)):
                        for j in range(i + 1, len(cells)):
                            r1, c1 = cells[i]
                            r2, c2 = cells[j]
                            self.clauses.append([
                                -VariableMapper.to_var(r1, c1, v),
                                -VariableMapper.to_var(r2, c2, v)
                            ])

    def _add_prefilled_constraints(self, grid):
        """
        Enforces the constraints provided by the initial puzzle state.
        Clause: (X_rcv) must be True.
        """
        for r in range(9):
            for c in range(9):
                val = grid.grid[r][c]
                if val != 0:
                    self.clauses.append([VariableMapper.to_var(r, c, val)])

    def get_cnf(self, initial_grid):
        """
        Generates all constraints and returns list of clauses.
        """
        self.clauses = [] # Reset
        self._add_cell_constraints()
        self._add_line_constraints()
        self._add_box_constraints()
        self._add_prefilled_constraints(initial_grid)
        return self.clauses
