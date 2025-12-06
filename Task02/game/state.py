import copy

# Constants
EMPTY = 0
BLACK = 1
WHITE = 2
BOARD_SIZE = 9
KOMI = 6.5

class GoState:
    def __init__(self, size=BOARD_SIZE):
        self.size = size
        self.board = [[EMPTY for _ in range(size)] for _ in range(size)]
        self.current_player = BLACK
        self.captures = {BLACK: 0, WHITE: 0}

        # Superko History
        self.history = set()
        self.history.add(self.get_board_hash())

        self.last_move_was_pass = False
        self.game_over = False

    def get_board_hash(self):
        return tuple(tuple(row) for row in self.board)

    def copy(self):
        return copy.deepcopy(self)

    def calculate_score(self, dead_stones_set=None):
        if dead_stones_set is None: dead_stones_set = set()

        score_board = copy.deepcopy(self.board)

        extra_black_captures = 0
        extra_white_captures = 0

        # Remove dead stones
        for r, c in dead_stones_set:
            if score_board[r][c] == BLACK:
                extra_white_captures += 1
            elif score_board[r][c] == WHITE:
                extra_black_captures += 1
            score_board[r][c] = EMPTY

        black_territory_pts = []
        white_territory_pts = []

        visited = set()
        for r in range(self.size):
            for c in range(self.size):
                if score_board[r][c] == EMPTY and (r, c) not in visited:
                    territory, owners = self.flood_fill_territory(score_board, r, c, visited)
                    if len(owners) == 1:
                        owner = list(owners)[0]
                        if owner == BLACK:
                            black_territory_pts.extend(territory)
                        else:
                            white_territory_pts.extend(territory)

        final_black = self.captures[BLACK] + extra_black_captures + len(black_territory_pts)
        final_white = self.captures[WHITE] + extra_white_captures + len(white_territory_pts) + KOMI

        winner = BLACK if final_black > final_white else WHITE

        return {
            BLACK: final_black,
            WHITE: final_white,
            'winner': winner,
            'black_territory': black_territory_pts,
            'white_territory': white_territory_pts
        }

    def flood_fill_territory(self, board, start_r, start_c, visited):
        stack = [(start_r, start_c)]
        region = []
        owners = set()
        visited.add((start_r, start_c))

        while stack:
            r, c = stack.pop()
            region.append((r, c))

            for nr, nc in self.get_neighbors(r, c):
                if board[nr][nc] == EMPTY:
                    if (nr, nc) not in visited:
                        visited.add((nr, nc))
                        stack.append((nr, nc))
                else:
                    owners.add(board[nr][nc])
        return region, owners

    def remove_dead_stones(self, board, r, c, color_to_check):
        dead_stones = []
        neighbors = self.get_neighbors(r, c)
        checked_groups = set()
        for nr, nc in neighbors:
            if board[nr][nc] == color_to_check:
                group = self.get_group(board, nr, nc)
                gid = tuple(sorted(list(group)))
                if gid in checked_groups: continue
                checked_groups.add(gid)
                if self.has_zero_liberties(board, group):
                    for dr, dc in group:
                        board[dr][dc] = EMPTY
                        dead_stones.append((dr, dc))
        return dead_stones

    def get_group(self, board, r, c):
        color = board[r][c]
        group = set()
        stack = [(r, c)]
        while stack:
            cr, cc = stack.pop()
            if (cr, cc) in group: continue
            group.add((cr, cc))
            for nr, nc in self.get_neighbors(cr, cc):
                if board[nr][nc] == color: stack.append((nr, nc))
        return group

    def count_liberties(self, board, r, c):
        group = self.get_group(board, r, c)
        liberties = set()
        for gr, gc in group:
            for nr, nc in self.get_neighbors(gr, gc):
                if board[nr][nc] == EMPTY: liberties.add((nr, nc))
        return len(liberties)

    def has_zero_liberties(self, board, group):
        for r, c in group:
            for nr, nc in self.get_neighbors(r, c):
                if board[nr][nc] == EMPTY: return False
        return True

    def get_neighbors(self, r, c):
        n = []
        if r > 0: n.append((r - 1, c))
        if r < self.size - 1: n.append((r + 1, c))
        if c > 0: n.append((r, c - 1))
        if c < self.size - 1: n.append((r, c + 1))
        return n
