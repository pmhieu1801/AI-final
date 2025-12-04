class SudokuGrid:
    """
    Represents the Sudoku Board state.
    """
    def __init__(self, matrix=None):
        # 0 represents an empty cell
        if matrix:
            self.grid = matrix
        else:
            self.grid = [[0 for _ in range(9)] for _ in range(9)]

    def __str__(self):
        return str(self.grid)

class VariableMapper:
    """
    Handles mapping between Sudoku logic (row, col, value)
    and SAT variable IDs (1 to 729).

    Variable ID = (row * 81) + (col * 9) + (val - 1) + 1
    """
    @staticmethod
    def to_var(r, c, v):
        """
        r: 0-8 (row)
        c: 0-8 (col)
        v: 1-9 (value)
        Returns: Integer ID >= 1
        """
        return (r * 9 + c) * 9 + (v - 1) + 1

    @staticmethod
    def to_rcv(var_id):
        """
        Returns (row, col, val) tuple from variable ID.
        """
        adjusted = var_id - 1
        val = (adjusted % 9) + 1
        c = (adjusted // 9) % 9
        r = (adjusted // 81)
        return r, c, val
