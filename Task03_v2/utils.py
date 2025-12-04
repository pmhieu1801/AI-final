class Visualizer:
    @staticmethod
    def display(grid_obj):
        if not grid_obj:
            print("No grid to display.")
            return

        board = grid_obj.grid
        print("-" * 25)
        for i in range(9):
            line = "| "
            for j in range(9):
                val = board[i][j]
                line += (str(val) if val != 0 else ".") + " "
                if (j + 1) % 3 == 0:
                    line += "| "
            print(line)
            if (i + 1) % 3 == 0:
                print("-" * 25)
