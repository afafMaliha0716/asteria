
import pygame
import sys
import random

# Game Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 3
CELL_SIZE = 150
GRID_OFFSET_X = (WIDTH - GRID_SIZE * CELL_SIZE) // 2
GRID_OFFSET_Y = (HEIGHT - GRID_SIZE * CELL_SIZE) // 2
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
DARK_BLUE = (0, 0, 128)
PURPLE = (128, 0, 128)

# Game States
MENU_STATE = 0
PLAYING_STATE = 1
GAME_OVER_STATE = 2

# Player Marker
PLAYER_MARKER = 1
AI_MARKER = -1
EMPTY_CELL = 0

# Power-ups
GRAVITON_BOOST = 1
COSMIC_REVERSAL = 2

# Game Class
class CosmicGridlock:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Cosmic Gridlock")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)

        self.game_state = MENU_STATE
        self.board = [[EMPTY_CELL for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.current_player = PLAYER_MARKER
        self.player_score = 0
        self.ai_score = 0
        self.warp_shift_used = False
        self.powerup_active = None
        self.powerup_timer = 0
        self.powerup_type = None
        self.last_move = None
        self.possible_moves = []

        self.player_pos = [100, 100]
        self.ai_pos = [600, 100]
        self.obstacles = [
            {"rect": pygame.Rect(350, 250, 70, 70), "type": "asteroid_field"},
            {"rect": pygame.Rect(100, 400, 40, 40), "type": "debris"}
        ]
        self.powerups = [
            {"rect": pygame.Rect(450, 150, 30, 30), "type": GRAVITON_BOOST, "collected": False}
        ]
        self.ai_logic = BasicAI()

        self.reset_game()

    def reset_game(self):
        self.board = [[EMPTY_CELL for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.current_player = PLAYER_MARKER
        self.warp_shift_used = False
        self.powerup_active = None
        self.powerup_timer = 0
        self.powerup_type = None
        self.last_move = None
        self.possible_moves = []

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.game_state == MENU_STATE:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.game_state = PLAYING_STATE
                        self.reset_game()
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            elif self.game_state == PLAYING_STATE:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        self.player_pos[1] -= 50
                    if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        self.player_pos[1] += 50
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        self.player_pos[0] -= 50
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        self.player_pos[0] += 50

                    if event.key == pygame.K_SPACE:
                        self.try_place_marker()
                    if event.key == pygame.K_z and not self.warp_shift_used:
                        self.warp_shift_used = True
                        self.initiate_warp_shift()
                    if event.key == pygame.K_x and self.last_move:
                        self.undo_last_move()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.try_place_marker()
                        if self.powerup_type == COSMIC_REVERSAL and self.last_move:
                            self.undo_last_move()
                            self.powerup_active = None
                            self.powerup_type = None

            elif self.game_state == GAME_OVER_STATE:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.game_state = MENU_STATE
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

    def clamp_player_pos(self):
        self.player_pos[0] = max(GRID_OFFSET_X, min(self.player_pos[0], GRID_OFFSET_X + (GRID_SIZE - 1) * CELL_SIZE))
        self.player_pos[1] = max(GRID_OFFSET_Y, min(self.player_pos[1], GRID_OFFSET_Y + (GRID_SIZE - 1) * CELL_SIZE))

    def get_grid_coords(self, pos):
        if GRID_OFFSET_X <= pos[0] < GRID_OFFSET_X + GRID_SIZE * CELL_SIZE and \
           GRID_OFFSET_Y <= pos[1] < GRID_OFFSET_Y + GRID_SIZE * CELL_SIZE:
            col = (pos[0] - GRID_OFFSET_X) // CELL_SIZE
            row = (pos[1] - GRID_OFFSET_Y) // CELL_SIZE
            return row, col
        return None, None

    def is_cell_occupied(self, row, col):
        return self.board[row][col] != EMPTY_CELL

    def is_valid_move(self, row, col):
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE and not self.is_cell_occupied(row, col):
            for obstacle in self.obstacles:
                obstacle_rect = obstacle["rect"]
                cell_x = GRID_OFFSET_X + col * CELL_SIZE
                cell_y = GRID_OFFSET_Y + row * CELL_SIZE
                cell_rect = pygame.Rect(cell_x, cell_y, CELL_SIZE, CELL_SIZE)
                if obstacle_rect.colliderect(cell_rect):
                    return False
            return True
        return False

    def try_place_marker(self):
        row, col = self.get_grid_coords(self.player_pos)
        if row is not None and col is not None and self.current_player == PLAYER_MARKER:
            if self.is_valid_move(row, col):
                self.board[row][col] = self.current_player
                self.last_move = (row, col, self.current_player)
                self.check_win()
                self.switch_player()

    def switch_player(self):
        if self.current_player == PLAYER_MARKER:
            self.current_player = AI_MARKER
        else:
            self.current_player = PLAYER_MARKER
            self.ai_logic.last_player_move = self.last_move
            self.ai_logic.board = [row[:] for row in self.board] # Pass a copy
            self.possible_moves = self.get_available_moves()


    def check_win(self):
        for row in range(GRID_SIZE):
            if self.board[row][0] == self.board[row][1] == self.board[row][2] != EMPTY_CELL:
                return self.board[row][0]
        for col in range(GRID_SIZE):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != EMPTY_CELL:
                return self.board[0][col]
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != EMPTY_CELL:
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != EMPTY_CELL:
            return self.board[0][2]

        if not any(EMPTY_CELL in row for row in self.board):
            return 0 # Draw

        return None

    def get_available_moves(self):
        moves = []
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.is_valid_move(r, c):
                    moves.append((r, c))
        return moves

    def ai_make_move(self):
        if self.current_player == AI_MARKER:
            move = self.ai_logic.get_move(self.board, AI_MARKER, PLAYER_MARKER, self.get_available_moves())
            if move:
                row, col = move
                self.board[row][col] = AI_MARKER
                self.last_move = (row, col, AI_MARKER)
                self.check_win()
                self.switch_player()

    def initiate_warp_shift(self):
        if not self.warp_shift_used:
            self.player_state_for_warp = "selecting_first"
            self.selecting_marker_pos = None
            self.selecting_target_pos = None
            self.warp_shift_active = True

    def handle_warp_shift(self):
        if self.warp_shift_active:
            if self.player_state_for_warp == "selecting_first":
                row, col = self.get_grid_coords(self.player_pos)
                if row is not None and col is not None and self.board[row][col] == PLAYER_MARKER:
                    self.selecting_marker_pos = (row, col)
                    self.player_state_for_warp = "selecting_second"
                    self.warp_shift_active = False # Temporarily disable main input handling
            elif self.player_state_for_warp == "selecting_second":
                row, col = self.get_grid_coords(self.player_pos)
                if row is not None and col is not None and self.board[row][col] == EMPTY_CELL:
                    self.selecting_target_pos = (row, col)
                    self.execute_warp_shift()
                    self.player_state_for_warp = None
                    self.warp_shift_active = False

    def execute_warp_shift(self):
        if self.selecting_marker_pos and self.selecting_target_pos:
            r1, c1 = self.selecting_marker_pos
            r2, c2 = self.selecting_target_pos

            self.board[r1][c1], self.board[r2][c2] = self.board[r2][c2], self.board[r1][c1]

            self.last_move = ("warp", (r1, c1), (r2, c2)) # Store warp shift as last_move for undo

            self.selecting_marker_pos = None
            self.selecting_target_pos = None
            self.warp_shift_active = False
            self.current_player = AI_MARKER # Next player's turn

    def undo_last_move(self):
        if self.last_move:
            if self.last_move[0] == "warp":
                _, (r1, c1), (r2, c2) = self.last_move
                self.board[r1][c1], self.board[r2][c2] = self.board[r2][c2], self.board[r1][c1]
            else:
                row, col, marker = self.last_move
                self.board[row][col] = EMPTY_CELL
            self.last_move = None
            self.switch_player() # Switch back to the player who made the move before the undo
            self.warp_shift_used = False # Reset warp shift usage for the turn

    def collect_powerup(self):
        for powerup in self.powerups:
            if not powerup["collected"]:
                player_rect = pygame.Rect(self.player_pos[0], self.player_pos[1], 30, 30) # Assuming player marker size
                if player_rect.colliderect(powerup["rect"]):
                    powerup["collected"] = True
                    self.powerup_type = powerup["type"]
                    self.powerup_timer = pygame.time.get_ticks()
                    if self.powerup_type == GRAVITON_BOOST:
                        self.powerup_active = True
                    if self.powerup_type == COSMIC_REVERSAL:
                        self.powerup_active = True
                        self.last_move = ("undoable",) # Mark that a cosmic reversal is available

    def activate_powerups(self):
        if self.powerup_active:
            current_time = pygame.time.get_ticks()
            if self.powerup_type == GRAVITON_BOOST:
                if current_time - self.powerup_timer > 5000: # 5 seconds duration
                    self.powerup_active = False
                    self.powerup_type = None
            elif self.powerup_type == COSMIC_REVERSAL:
                # Cosmic Reversal is used by pressing 'X'
                pass

    def draw_menu(self):
        self.screen.fill(BLACK)
        title_text = self.font.render("Cosmic Gridlock", True, WHITE)
        self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))

        start_text = self.small_font.render("Press ENTER to Start", True, WHITE)
        self.screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2))

        quit_text = self.small_font.render("Press ESC to Quit", True, WHITE)
        self.screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 50))

        pygame.display.flip()

    def draw_playing(self):
        self.screen.fill(DARK_BLUE)

        # Draw Grid
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                cell_x = GRID_OFFSET_X + c * CELL_SIZE
                cell_y = GRID_OFFSET_Y + r * CELL_SIZE
                pygame.draw.rect(self.screen, PURPLE, (cell_x, cell_y, CELL_SIZE, CELL_SIZE), 2)

                if self.board[r][c] == PLAYER_MARKER:
                    center_x = cell_x + CELL_SIZE // 2
                    center_y = cell_y + CELL_SIZE // 2
                    pygame.draw.circle(self.screen, RED, (center_x, center_y), CELL_SIZE // 3, 5)
                elif self.board[r][c] == AI_MARKER:
                    center_x = cell_x + CELL_SIZE // 2
                    center_y = cell_y + CELL_SIZE // 2
                    pygame.draw.circle(self.screen, BLUE, (center_x, center_y), CELL_SIZE // 3, 5)

        # Draw Player Cursor
        pygame.draw.rect(self.screen, GREEN, (self.player_pos[0], self.player_pos[1], 30, 30))

        # Draw Obstacles
        for obstacle in self.obstacles:
            pygame.draw.rect(self.screen, GRAY, obstacle["rect"])

        # Draw Powerups
        for powerup in self.powerups:
            if not powerup["collected"]:
                pygame.draw.rect(self.screen, YELLOW, powerup["rect"])

        # Draw UI Elements (Score, Turn, etc.)
        score_text = self.small_font.render(f"Player: {self.player_score} | AI: {self.ai_score}", True, WHITE)
        self.screen.blit(score_text, (20, 20))

        turn_text = self.small_font.render(f"Turn: {'Player' if self.current_player == PLAYER_MARKER else 'AI'}", True, WHITE)
        self.screen.blit(turn_text, (WIDTH - turn_text.get_width() - 20, 20))

        if self.warp_shift_used:
            warp_text = self.small_font.render("Warp Shift Used", True, GRAY)
            self.screen.blit(warp_text, (20, 60))

        if self.powerup_type == COSMIC_REVERSAL and self.last_move:
            undo_text = self.small_font.render("Press X to Undo", True, YELLOW)
            self.screen.blit(undo_text, (20, 100))

        if self.powerup_active and self.powerup_type == GRAVITON_BOOST:
            self.highlight_winning_lines()


        pygame.display.flip()

    def highlight_winning_lines(self):
        winning_lines = self.find_winning_lines()
        for line in winning_lines:
            for r, c in line:
                cell_x = GRID_OFFSET_X + c * CELL_SIZE
                cell_y = GRID_OFFSET_Y + r * CELL_SIZE
                pygame.draw.rect(self.screen, YELLOW, (cell_x, cell_y, CELL_SIZE, CELL_SIZE), 3)

    def find_winning_lines(self):
        lines = []
        # Horizontal
        for r in range(GRID_SIZE):
            if self.board[r][0] == self.board[r][1] == self.board[r][2] != EMPTY_CELL:
                lines.append([(r, 0), (r, 1), (r, 2)])
        # Vertical
        for c in range(GRID_SIZE):
            if self.board[0][c] == self.board[1][c] == self.board[2][c] != EMPTY_CELL:
                lines.append([(0, c), (1, c), (2, c)])
        # Diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != EMPTY_CELL:
            lines.append([(0, 0), (1, 1), (2, 2)])
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != EMPTY_CELL:
            lines.append([(0, 2), (1, 1), (2, 0)])
        return lines


    def draw_game_over(self):
        self.screen.fill(BLACK)
        winner = self.check_win()
        if winner == PLAYER_MARKER:
            message = "You Win!"
            self.player_score += 1
        elif winner == AI_MARKER:
            message = "AI Wins!"
            self.ai_score -= 1
        else:
            message = "It's a Draw!"

        win_text = self.font.render(message, True, WHITE)
        self.screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, 100))

        score_text = self.small_font.render(f"Score: Player {self.player_score} | AI {self.ai_score}", True, WHITE)
        self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 200))

        restart_text = self.small_font.render("Press ENTER to Play Again", True, WHITE)
        self.screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2))

        quit_text = self.small_font.render("Press ESC to Quit", True, WHITE)
        self.screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 50))

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_input()

            if self.game_state == PLAYING_STATE:
                self.clamp_player_pos()
                self.collect_powerup()
                self.activate_powerups()

                if self.current_player == AI_MARKER:
                    self.ai_make_move()

                win = self.check_win()
                if win is not None:
                    self.game_state = GAME_OVER_STATE

            if self.game_state == MENU_STATE:
                self.draw_menu()
            elif self.game_state == PLAYING_STATE:
                self.draw_playing()
            elif self.game_state == GAME_OVER_STATE:
                self.draw_game_over()

            self.clock.tick(60)

# Basic AI Class
class BasicAI:
    def __init__(self):
        self.board = None
        self.my_marker = None
        self.opponent_marker = None
        self.last_player_move = None # For simple blocking

    def get_move(self, board, my_marker, opponent_marker, available_moves):
        self.board = board
        self.my_marker = my_marker
        self.opponent_marker = opponent_marker

        # 1. Check if AI can win
        for move in available_moves:
            r, c = move
            temp_board = [row[:] for row in self.board]
            temp_board[r][c] = self.my_marker
            if self.check_win_on_board(temp_board, self.my_marker):
                return move

        # 2. Check if player can win and block
        for move in available_moves:
            r, c = move
            temp_board = [row[:] for row in self.board]
            temp_board[r][c] = self.opponent_marker
            if self.check_win_on_board(temp_board, self.opponent_marker):
                return move

        # 3. Take the center if available
        if (1, 1) in available_moves:
            return (1, 1)

        # 4. Take opposite corners if player has one
        corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
        for corner in corners:
            if corner in available_moves:
                # Check if opponent has occupied the opposite corner
                opposite_corner = None
                if corner == (0, 0): opposite_corner = (2, 2)
                elif corner == (0, 2): opposite_corner = (2, 0)
                elif corner == (2, 0): opposite_corner = (0, 2)
                elif corner == (2, 2): opposite_corner = (0, 0)

                if opposite_corner and self.board[opposite_corner[0]][opposite_corner[1]] == self.opponent_marker:
                    return corner

        # 5. Take any available corner
        available_corners = [move for move in available_moves if move in corners]
        if available_corners:
            return random.choice(available_corners)

        # 6. Take any available side
        available_sides = [move for move in available_moves if move not in corners and move != (1,1)]
        if available_sides:
            return random.choice(available_sides)

        # Fallback: return any available move
        return random.choice(available_moves) if available_moves else None


    def check_win_on_board(self, board_state, marker):
        grid_size = len(board_state)
        # Horizontal
        for r in range(grid_size):
            if all(board_state[r][c] == marker for c in range(grid_size)):
                return True
        # Vertical
        for c in range(grid_size):
            if all(board_state[r][c] == marker for r in range(grid_size)):
                return True
        # Diagonals
        if all(board_state[i][i] == marker for i in range(grid_size)):
            return True
        if all(board_state[i][grid_size - 1 - i] == marker for i in range(grid_size)):
            return True
        return False

if __name__ == "__main__":
    game = CosmicGridlock()
    game.run()
