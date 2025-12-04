import math
from state import BLACK, WHITE, EMPTY
from node import Node

class Agent:
    def __init__(self):
        pass

class MinimaxAgent(Agent):
    def __init__(self, problem, depth=3):
        super().__init__()
        self.problem = problem
        self.depth_limit = depth

    def get_best_move(self, state):
        # Optimization: Center move if empty
        if all(row.count(EMPTY) == state.size for row in state.board):
            return (state.size // 2, state.size // 2)

        best_val = -math.inf
        best_move = None
        moves = self.problem.actions(state)

        if not moves:
            return None

        # --- PASS CHECK LOGIC ---
        # If opponent passed, we check if our best move actually gains anything.
        # If not, we pass to end the game.
        current_state_val = self.heuristic(state)
        # ------------------------

        alpha = -math.inf
        beta = math.inf

        for move in moves:
            next_state = self.problem.result(state, move)
            val = self.min_value(next_state, self.depth_limit - 1, alpha, beta)

            if val > best_val:
                best_val = val
                best_move = move

            alpha = max(alpha, best_val)

        # Heuristic Pass decision:
        if state.last_move_was_pass:
            if best_val < current_state_val + 0.5:
                return None

        return best_move

    def max_value(self, state, depth, alpha, beta):
        if depth == 0 or self.problem.is_terminal(state):
            return self.heuristic(state)

        v = -math.inf
        moves = self.problem.actions(state)
        if not moves: return self.heuristic(state)

        for move in moves:
            v = max(v, self.min_value(self.problem.result(state, move), depth - 1, alpha, beta))
            if v >= beta: return v
            alpha = max(alpha, v)
        return v

    def min_value(self, state, depth, alpha, beta):
        if depth == 0 or self.problem.is_terminal(state):
            return self.heuristic(state)

        v = math.inf
        moves = self.problem.actions(state)
        if not moves: return self.heuristic(state)

        for move in moves:
            v = min(v, self.max_value(self.problem.result(state, move), depth - 1, alpha, beta))
            if v <= alpha: return v
            beta = min(beta, v)
        return v

    def heuristic(self, state):
        return 0


class RobustMinimaxAgent(MinimaxAgent):
    def __init__(self, problem, depth=2, ai_color=WHITE):
        super().__init__(problem, depth)
        self.ai_color = ai_color

    def heuristic(self, state):
        black_score = state.captures[BLACK] * 10
        white_score = state.captures[WHITE] * 10
        black_liberties = 0
        white_liberties = 0
        stones_diff = 0

        for r in range(state.size):
            for c in range(state.size):
                cell = state.board[r][c]
                if cell == BLACK:
                    stones_diff += 1
                    black_liberties += state.count_liberties(state.board, r, c)
                elif cell == WHITE:
                    stones_diff -= 1
                    white_liberties += state.count_liberties(state.board, r, c)

        # Heuristic: Material + Territory Proxy + Shape Health
        val = (black_score - white_score) + (stones_diff * 1.0) + (black_liberties - white_liberties) * 0.2

        # In Minimax, the value is always calculated from MAX's perspective.
        if self.ai_color == WHITE:
            return -val
        return val
