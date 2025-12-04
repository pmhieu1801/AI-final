# main.py
import pygame
import sys
from state import GoState, BLACK, WHITE, EMPTY, BOARD_SIZE
from problem import GoProblem
from agent import RobustMinimaxAgent

# UI Constants
CELL_SIZE = 60
MARGIN = 40
WINDOW_SIZE = CELL_SIZE * (BOARD_SIZE - 1) + 2 * MARGIN
BG_COLOR = (220, 179, 92)
LINE_COLOR = (0, 0, 0)


class GoGameUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + 80))
        pygame.display.set_caption("Go (9x9) - AI")
        self.clock = pygame.time.Clock()

        self.state = GoState(BOARD_SIZE)
        self.problem = GoProblem(self.state)
        self.mode = "PvP"
        self.ai_agent = None

        # Scoring vars
        self.scoring_mode = False
        self.dead_stones = set()
        self.score_result = None

        self.font = pygame.font.SysFont('Arial', 18)
        self.large_font = pygame.font.SysFont('Arial', 24, bold=True)

        self.in_menu = True
        center_x = WINDOW_SIZE // 2
        self.btn_pvp = pygame.Rect(center_x - 100, 150, 200, 50)
        self.btn_pvc = pygame.Rect(center_x - 100, 220, 200, 50)

    def draw_menu(self):
        self.screen.fill(BG_COLOR)
        # Title
        title = self.large_font.render("Go (9x9) Game", True, (0, 0, 0))
        self.screen.blit(title, (WINDOW_SIZE // 2 - title.get_width() // 2, 50))

        # Buttons
        pygame.draw.rect(self.screen, (50, 50, 50), self.btn_pvp)
        pygame.draw.rect(self.screen, (50, 50, 50), self.btn_pvc)

        txt_pvp = self.font.render("Human vs Human", True, (255, 255, 255))
        txt_pvc = self.font.render("Human vs AI", True, (255, 255, 255))

        self.screen.blit(txt_pvp, (self.btn_pvp.centerx - txt_pvp.get_width() // 2, self.btn_pvp.centery - txt_pvp.get_height() // 2))
        self.screen.blit(txt_pvc, (self.btn_pvc.centerx - txt_pvc.get_width() // 2, self.btn_pvc.centery - txt_pvc.get_height() // 2))

        # Instructions
        instr_y = 300
        instructions = [
            "INSTRUCTIONS:",
            " - PLAY: Click to place stone.",
            " - PASS: Press 'P' to pass.",
            " - END: Two consecutive passes end the game.",
            " - SCORING: Click stones to mark DEAD."
        ]
        for line in instructions:
            t = self.font.render(line, True, (0, 0, 0))
            self.screen.blit(t, (50, instr_y))
            instr_y += 30

    def handle_menu_click(self, pos):
        if self.btn_pvp.collidepoint(pos):
            self.mode = "PvP"
            self.in_menu = False
        elif self.btn_pvc.collidepoint(pos):
            self.mode = "PvC"
            self.ai_agent = RobustMinimaxAgent(self.problem, depth=2, ai_color=WHITE)
            self.in_menu = False

    def draw_board(self):
        self.screen.fill(BG_COLOR)

        # Draw Grid
        for i in range(BOARD_SIZE):
            pygame.draw.line(self.screen, LINE_COLOR, (MARGIN, MARGIN + i * CELL_SIZE),
                             (WINDOW_SIZE - MARGIN, MARGIN + i * CELL_SIZE), 2)
            pygame.draw.line(self.screen, LINE_COLOR, (MARGIN + i * CELL_SIZE, MARGIN),
                             (MARGIN + i * CELL_SIZE, WINDOW_SIZE - MARGIN), 2)

        # Draw Territory Markers (Only in Scoring Mode)
        if self.scoring_mode and self.score_result:
            # Draw Black Territory
            for r, c in self.score_result['black_territory']:
                x = MARGIN + c * CELL_SIZE
                y = MARGIN + r * CELL_SIZE
                pygame.draw.rect(self.screen, (0, 0, 0), (x - 8, y - 8, 16, 16))
            # Draw White Territory
            for r, c in self.score_result['white_territory']:
                x = MARGIN + c * CELL_SIZE
                y = MARGIN + r * CELL_SIZE
                pygame.draw.rect(self.screen, (255, 255, 255), (x - 8, y - 8, 16, 16))
                pygame.draw.rect(self.screen, (0, 0, 0), (x - 8, y - 8, 16, 16), 1)

        # Draw Stones
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                cell = self.state.board[r][c]
                x = MARGIN + c * CELL_SIZE
                y = MARGIN + r * CELL_SIZE

                # Check if stone is marked dead
                is_dead = (r, c) in self.dead_stones

                if cell != EMPTY:
                    color = (0, 0, 0) if cell == BLACK else (255, 255, 255)
                    alpha_color = (*color, 100) if is_dead else color

                    if is_dead:
                        # Ghost stone
                        s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                        pygame.draw.circle(s, alpha_color, (CELL_SIZE // 2, CELL_SIZE // 2), CELL_SIZE // 2 - 2)
                        self.screen.blit(s, (x - CELL_SIZE // 2, y - CELL_SIZE // 2))
                        # Red X
                        pygame.draw.line(self.screen, (200, 0, 0), (x - 10, y - 10), (x + 10, y + 10), 3)
                        pygame.draw.line(self.screen, (200, 0, 0), (x + 10, y - 10), (x - 10, y + 10), 3)
                    else:
                        pygame.draw.circle(self.screen, color, (x, y), CELL_SIZE // 2 - 2)
                        if cell == WHITE:
                            pygame.draw.circle(self.screen, LINE_COLOR, (x, y), CELL_SIZE // 2 - 2, 1)

        # Draw UI info
        if self.scoring_mode:
            self.draw_scoring_info()
        else:
            turn_str = f"{'Black' if self.state.current_player == BLACK else 'White'}'s Turn"
            t_surf = self.font.render(turn_str + " (Press 'P' to Pass)", True, (0, 0, 128))
            self.screen.blit(t_surf, (10, 5))

            cap_str = f"Captures -> Black: {self.state.captures[BLACK]}  White: {self.state.captures[WHITE]}"
            c_surf = self.font.render(cap_str, True, (0, 0, 0))
            self.screen.blit(c_surf, (10, WINDOW_SIZE + 10))

    def draw_scoring_info(self):
        # Always recalculate to keep UI fresh
        self.score_result = self.state.calculate_score(self.dead_stones)
        res = self.score_result

        pygame.draw.rect(self.screen, (50, 50, 50), (0, WINDOW_SIZE, WINDOW_SIZE, 80))

        txt1 = self.font.render("SCORING: Click Dead Stones. Territory is marked with squares.", True, (255, 200, 0))
        self.screen.blit(txt1, (10, WINDOW_SIZE + 5))

        score_str = f"Black: {res[BLACK]}   vs   White: {res[WHITE]} (Komi {6.5})"
        txt2 = self.large_font.render(score_str, True, (255, 255, 255))
        self.screen.blit(txt2, (10, WINDOW_SIZE + 35))

        res_str = "Winner: Black" if res['winner'] == BLACK else "Winner: White"
        txt3 = self.large_font.render(res_str, True, (0, 255, 0))
        self.screen.blit(txt3, (WINDOW_SIZE - 180, WINDOW_SIZE + 35))

    def handle_click(self, pos):
        x, y = pos
        c = round((x - MARGIN) / CELL_SIZE)
        r = round((y - MARGIN) / CELL_SIZE)

        if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
            return

        if not self.scoring_mode:
            # PLAY MODE
            if self.problem.is_valid_move(self.state, r, c):
                self.state = self.problem.result(self.state, (r, c))
                return True
        else:
            # SCORING MODE
            if self.state.board[r][c] != EMPTY:
                group = self.state.get_group(self.state.board, r, c)
                if (r, c) in self.dead_stones:
                    # Revive
                    for s in group:
                        if s in self.dead_stones: self.dead_stones.remove(s)
                else:
                    # Kill
                    for s in group:
                        self.dead_stones.add(s)
                return True
        return False

    def run(self):
        while True:
            if self.in_menu:
                self.draw_menu()
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.handle_menu_click(event.pos)
                continue

            # Auto-switch to scoring
            if self.state.game_over and not self.scoring_mode:
                self.scoring_mode = True
                print("Game Over. Entering Scoring Mode.")

            self.draw_board()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit();
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.scoring_mode:
                        self.handle_click(event.pos)
                    elif self.mode == "PvP" or (self.mode == "PvC" and self.state.current_player == BLACK):
                        self.handle_click(event.pos)

                if event.type == pygame.KEYDOWN and not self.scoring_mode:
                    if event.key == pygame.K_p:
                        print(f"Player ({'Black' if self.state.current_player == BLACK else 'White'}) passed.")
                        self.state = self.problem.result(self.state, None)

            # AI TURN
            if not self.scoring_mode and self.mode == "PvC" and self.state.current_player == WHITE:
                self.draw_board()
                pygame.display.flip()
                pygame.time.wait(100)

                move = self.ai_agent.get_best_move(self.state)
                if move:
                    print(f"AI plays {move}")
                    self.state = self.problem.result(self.state, move)
                else:
                    print("AI Passes.")
                    self.state = self.problem.result(self.state, None)

            self.clock.tick(30)


if __name__ == "__main__":
    game = GoGameUI()
    game.run()