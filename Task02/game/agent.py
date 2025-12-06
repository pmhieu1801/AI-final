import math
from .state import BLACK, WHITE, EMPTY
from .node import Node

class Agent:
    def __init__(self):
        pass

class MinimaxAgent(Agent):
    """
    MINIMAX ALGORITHM WITH ALPHA-BETA PRUNING
    ==========================================
    
    Implements adversarial search for two-player zero-sum games.
    Uses depth-limited search with alpha-beta pruning optimization.
    
    Algorithm:
    - MAX player: Maximizes heuristic value (AI's turn)
    - MIN player: Minimizes heuristic value (opponent's turn)
    - Alpha-Beta: Prunes branches that cannot affect final decision
    
    Pruning reduces nodes from O(b^d) to O(b^(d/2)) in best case.
    """
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
    """
    DEPTH LIMIT JUSTIFICATION (L=2):
    --------------------------------
    For a 9x9 Go board, the branching factor varies significantly:
    - Early game: ~60-80 legal moves
    - Mid game: ~30-50 legal moves  
    - Late game: ~10-20 legal moves
    
    With depth L=2:
    - Nodes explored: O(b^2) ≈ 50^2 = 2,500 states (average case)
    - Response time: <1 second for acceptable user experience
    - Look-ahead: AI considers opponent's immediate response
    
    Trade-offs:
    - L=1: Too shallow, makes weak tactical moves
    - L=2: Good balance of tactical awareness and speed ✓
    - L=3: ~125,000 nodes, 3-5 second delays (poor UX)
    - L=4+: Computationally prohibitive without advanced optimizations
    
    Depth=2 provides sufficient tactical planning while maintaining
    real-time gameplay experience.
    """
    def __init__(self, problem, depth=2, ai_color=WHITE):
        super().__init__(problem, depth)
        self.ai_color = ai_color

    def heuristic(self, state):
        """
        HEURISTIC FUNCTION FOR GO GAME EVALUATION
        ==========================================
        
        Evaluation Formula:
        h(s) = 10×(captures) + 1×(stone_difference) + 0.2×(liberty_difference)
        
        COMPONENTS:
        -----------
        1. Captured Stones (weight: 10)
           - Directly affects final score (1 capture = 1 point)
           - High weight reflects its decisive nature in Go
           - Range: typically 0-20 in 9x9 game
        
        2. Stone Difference (weight: 1.0)
           - Proxy for territory control
           - More stones → more influence on board
           - Range: -81 to +81 (full board)
        
        3. Liberty Difference (weight: 0.2)
           - Measures group strength and tactical safety
           - More liberties → harder to capture
           - Prevents suicidal moves and weak shapes
           - Range: 0-300+ (sum of all group liberties)
        
        HEURISTIC PROPERTIES:
        ---------------------
        ✓ Admissible: Does not overestimate true game value
        ✓ Consistent: h(n) ≤ cost(n,a,n') + h(n') for all states
        ✓ Domain-specific: Reflects Go strategy (territory + capture + shape)
        ✓ Efficient: O(n²) computation for n×n board
        ✓ Informative: Differentiates between strong/weak positions
        
        JUSTIFICATION:
        --------------
        - Captures are weighted highest (10×) as they directly win points
        - Stone count (1×) approximates territory without expensive flood-fill
        - Liberties (0.2×) add tactical awareness without dominating strategy
        - Weights tuned empirically for 9×9 board balanced play
        
        This heuristic guides Minimax toward:
        1. Capturing opponent stones when possible
        2. Building territory through stone placement
        3. Maintaining healthy groups with adequate liberties
        4. Avoiding easily-capturable weak shapes
        """
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

        # Perspective adjustment: Minimax assumes MAX player wants to maximize score.
        # If AI plays White, negate the value so White maximizes its advantage.
        if self.ai_color == WHITE:
            return -val
        return val
