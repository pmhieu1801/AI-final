import copy
from state import GoState, BLACK, WHITE, EMPTY, BOARD_SIZE

class Problem:
    """The abstract class for a formal problem."""
    def __init__(self, initial_state):
        self.initial_state = initial_state

    def actions(self, state):
        raise NotImplementedError

    def result(self, state, action):
        raise NotImplementedError

    def is_terminal(self, state):
        return False

    def utility(self, state):
        return 0

class GoProblem(Problem):
    def __init__(self, initial_state=None):
        if initial_state is None:
            initial_state = GoState(BOARD_SIZE)
        super().__init__(initial_state)

    def actions(self, state):
        """Returns a list of legal moves (r, c)."""
        if state.game_over: return []
        moves = []
        for r in range(state.size):
            for c in range(state.size):
                if state.board[r][c] == EMPTY:
                    if self.is_valid_move(state, r, c):
                        moves.append((r, c))
        return moves

    def is_valid_move(self, state, r, c):
        if not (0 <= r < state.size and 0 <= c < state.size): return False
        if state.board[r][c] != EMPTY: return False

        # Simulate move on a temp board
        temp_board = copy.deepcopy(state.board)
        temp_board[r][c] = state.current_player
        opponent = WHITE if state.current_player == BLACK else BLACK

        # We need to use state's helper methods, but on the temp_board
        captured = state.remove_dead_stones(temp_board, r, c, opponent)

        # Check suicide rule
        if not captured and state.count_liberties(temp_board, r, c) == 0:
            return False

        # Check Ko/Superko
        new_hash = tuple(tuple(row) for row in temp_board)
        if new_hash in state.history:
            return False
        return True

    def result(self, state, action):
        """Return the state that results from executing the given action in the given state."""
        new_state = state.copy()
        opponent = WHITE if state.current_player == BLACK else BLACK

        if action is None:
            # Pass move
            if new_state.last_move_was_pass:
                new_state.game_over = True
            new_state.last_move_was_pass = True
            new_state.current_player = opponent
            return new_state

        r, c = action
        new_state.board[r][c] = state.current_player
        new_state.last_move_was_pass = False

        # Remove dead stones
        captured = new_state.remove_dead_stones(new_state.board, r, c, opponent)
        new_state.captures[state.current_player] += len(captured)

        new_state.history.add(new_state.get_board_hash())
        new_state.current_player = opponent
        return new_state

    def is_terminal(self, state):
        return state.game_over
