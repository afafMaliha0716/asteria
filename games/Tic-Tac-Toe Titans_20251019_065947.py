
import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 3
BIG_GRID_SIZE = 5
CELL_SIZE = 150
BIG_CELL_SIZE = 100
BUTTON_COLOR = (100, 100, 255)
BUTTON_HOVER_COLOR = (150, 150, 255)
TEXT_COLOR = (255, 255, 255)
BACKGROUND_COLOR = (50, 50, 50)
BOARD_LINE_COLOR = (0, 0, 0)
PLAYER_X_COLOR = (255, 0, 0)
PLAYER_O_COLOR = (0, 0, 255)
ENEMY_COLOR = (0, 255, 0)
POWERUP_COLOR = (255, 255, 0)
OBSTACLE_COLOR = (128, 128, 128)

# Game States
MENU = 0
PLAYING = 1
GAME_OVER = 2

# Player and Enemy Types
PLAYER_X = 'X'
PLAYER_O = 'O'

# Powerups
SPARK_OF_INSIGHT = 'spark_of_insight'
SHIELD_OF_STONE = 'shield_of_stone'
WILDCARD = 'wildcard'

# AI Difficulty Levels
EASY = 'easy'
MEDIUM = 'medium'
HARD = 'hard'
EXPERT = 'expert'

# Game Class
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tic-Tac-Toe Titans")
        self.clock = pygame.time.Clock()
        self.game_state = MENU
        self.score = 0
        self.current_level = 0
        self.levels = [
            {
                "name": "The First Gambit",
                "grid_size": 3,
                "opponent": {
                    "name": "Grumble the Goblin",
                    "behavior": EASY,
                    "token": PLAYER_O
                },
                "arena_color": (100, 150, 100),
                "powerups": [SPARK_OF_INSIGHT, WILDCARD],
                "background_elements": []
            },
            {
                "name": "The Sprite's Secret",
                "grid_size": 3,
                "opponent": {
                    "name": "Sly the Sprite",
                    "behavior": MEDIUM,
                    "token": PLAYER_O
                },
                "arena_color": (150, 100, 150),
                "powerups": [SHIELD_OF_STONE, WILDCARD],
                "background_elements": []
            },
            {
                "name": "Golem's Gauntlet",
                "grid_size": 3,
                "opponent": {
                    "name": "Boulder the Golem",
                    "behavior": HARD,
                    "token": PLAYER_O
                },
                "arena_color": (120, 120, 120),
                "powerups": [SPARK_OF_INSIGHT, SHIELD_OF_STONE],
                "background_elements": []
            },
            {
                "name": "The Eldritch Grid",
                "grid_size": 5,
                "opponent": {
                    "name": "The Eldritch Abomination",
                    "behavior": EXPERT,
                    "token": PLAYER_O
                },
                "arena_color": (80, 40, 120),
                "powerups": [SPARK_OF_INSIGHT, SHIELD_OF_STONE, WILDCARD],
                "background_elements": []
            }
        ]
        self.player_token = PLAYER_X
        self.current_level_data = None
        self.board = []
        self.turn = PLAYER_X
        self.game_over = False
        self.winner = None
        self.player_abilities = {
            SPARK_OF_INSIGHT: 1,
            SHIELD_OF_STONE: 1,
            WILDCARD: 1
        }
        self.available_powerups = []
        self.show_strategic_foresight = False
        self.blocking_move = None

        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)

    def reset_game(self):
        self.board = [['' for _ in range(self.current_level_data["grid_size"])] for _ in range(self.current_level_data["grid_size"])]
        self.turn = PLAYER_X
        self.game_over = False
        self.winner = None
        self.show_strategic_foresight = False
        self.blocking_move = None
        self.player_abilities = {
            SPARK_OF_INSIGHT: 1,
            SHIELD_OF_STONE: 1,
            WILDCARD: 1
        }
        self.available_powerups = random.sample(self.current_level_data["powerups"], min(len(self.current_level_data["powerups"]), 2))

    def start_level(self, level_index):
        self.current_level = level_index
        self.current_level_data = self.levels[self.current_level]
        self.reset_game()
        self.game_state = PLAYING

    def handle_menu_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            play_button_rect = pygame.Rect(300, 250, 200, 50)
            quit_button_rect = pygame.Rect(300, 350, 200, 50)

            if play_button_rect.collidepoint(mouse_pos):
                self.start_level(0)
            elif quit_button_rect.collidepoint(mouse_pos):
                pygame.quit()
                sys.exit()

    def handle_playing_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.game_over:
                mouse_x, mouse_y = event.pos
                grid_size = self.current_level_data["grid_size"]
                cell_size = CELL_SIZE if grid_size == 3 else BIG_CELL_SIZE
                board_offset_x = (SCREEN_WIDTH - grid_size * cell_size) // 2
                board_offset_y = (SCREEN_HEIGHT - grid_size * cell_size) // 2

                if board_offset_x <= mouse_x <= board_offset_x + grid_size * cell_size and \
                   board_offset_y <= mouse_y <= board_offset_y + grid_size * cell_size:
                    col = (mouse_x - board_offset_x) // cell_size
                    row = (mouse_y - board_offset_y) // cell_size

                    if 0 <= row < grid_size and 0 <= col < grid_size and self.board[row][col] == '':
                        if self.turn == PLAYER_X:
                            self.board[row][col] = PLAYER_X
                            self.turn = PLAYER_O
                            self.check_win()
                        elif self.turn == PLAYER_O and self.current_level_data["opponent"]["behavior"] != EASY:
                             # Player can only place 'X' directly
                             pass

        if event.type == pygame.KEYDOWN:
            if not self.game_over:
                if event.key == pygame.K_1: # Spark of Insight
                    if self.player_abilities[SPARK_OF_INSIGHT] > 0:
                        self.player_abilities[SPARK_OF_INSIGHT] -= 1
                        self.show_strategic_foresight = True
                elif event.key == pygame.K_2: # Shield of Stone
                    if self.player_abilities[SHIELD_OF_STONE] > 0:
                        self.player_abilities[SHIELD_OF_STONE] -= 1
                        self.use_defensive_block()
                elif event.key == pygame.K_3: # Wildcard
                    if self.player_abilities[WILDCARD] > 0:
                        self.player_abilities[WILDCARD] -= 1
                        # Wildcard functionality needs mouse click to select target square
                        pass
            else:
                if event.key == pygame.K_RETURN: # Next Level
                    if self.winner == PLAYER_X:
                        self.score += 100 # Basic scoring
                        if self.current_level < len(self.levels) - 1:
                            self.start_level(self.current_level + 1)
                        else:
                            self.game_state = GAME_OVER
                    elif self.winner == PLAYER_O:
                        self.score -= 50
                        self.reset_game() # Retry current level
                    elif self.winner is None: # Draw
                        self.score += 25
                        self.reset_game() # Retry current level

                elif event.key == pygame.K_r: # Restart Game
                    self.current_level = 0
                    self.score = 0
                    self.start_level(0)


    def handle_game_over_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            restart_button_rect = pygame.Rect(300, 450, 200, 50)
            menu_button_rect = pygame.Rect(300, 520, 200, 50)

            if restart_button_rect.collidepoint(mouse_pos):
                self.current_level = 0
                self.score = 0
                self.start_level(0)
            elif menu_button_rect.collidepoint(mouse_pos):
                self.game_state = MENU

    def update(self):
        if self.game_state == PLAYING and not self.game_over:
            if self.turn == PLAYER_O:
                opponent_behavior = self.current_level_data["opponent"]["behavior"]
                if opponent_behavior == EASY:
                    self.ai_move_random()
                elif opponent_behavior == MEDIUM:
                    self.ai_move_medium()
                elif opponent_behavior == HARD:
                    self.ai_move_hard()
                elif opponent_behavior == EXPERT:
                    self.ai_move_expert()
                self.check_win()

            if self.show_strategic_foresight:
                self.show_strategic_foresight = False # Use only once per activation

    def draw_menu(self):
        self.screen.fill(BACKGROUND_COLOR)
        title_text = self.font.render("Tic-Tac-Toe Titans", True, TEXT_COLOR)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))

        play_button_rect = pygame.Rect(300, 250, 200, 50)
        quit_button_rect = pygame.Rect(300, 350, 200, 50)

        mouse_pos = pygame.mouse.get_pos()
        if play_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, BUTTON_HOVER_COLOR, play_button_rect)
        else:
            pygame.draw.rect(self.screen, BUTTON_COLOR, play_button_rect)
        play_text = self.small_font.render("Play", True, TEXT_COLOR)
        self.screen.blit(play_text, (play_button_rect.centerx - play_text.get_width() // 2, play_button_rect.centery - play_text.get_height() // 2))

        if quit_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, BUTTON_HOVER_COLOR, quit_button_rect)
        else:
            pygame.draw.rect(self.screen, BUTTON_COLOR, quit_button_rect)
        quit_text = self.small_font.render("Quit", True, TEXT_COLOR)
        self.screen.blit(quit_text, (quit_button_rect.centerx - quit_text.get_width() // 2, quit_button_rect.centery - quit_text.get_height() // 2))

    def draw_playing(self):
        self.screen.fill(self.current_level_data["arena_color"])
        grid_size = self.current_level_data["grid_size"]
        cell_size = CELL_SIZE if grid_size == 3 else BIG_CELL_SIZE
        board_offset_x = (SCREEN_WIDTH - grid_size * cell_size) // 2
        board_offset_y = (SCREEN_HEIGHT - grid_size * cell_size) // 2

        # Draw board lines
        for i in range(1, grid_size):
            pygame.draw.line(self.screen, BOARD_LINE_COLOR, (board_offset_x + i * cell_size, board_offset_y), (board_offset_x + i * cell_size, board_offset_y + grid_size * cell_size), 3)
            pygame.draw.line(self.screen, BOARD_LINE_COLOR, (board_offset_x, board_offset_y + i * cell_size), (board_offset_x + grid_size * cell_size, board_offset_y + i * cell_size), 3)

        # Draw tokens
        for r in range(grid_size):
            for c in range(grid_size):
                x = board_offset_x + c * cell_size + cell_size // 2
                y = board_offset_y + r * cell_size + cell_size // 2
                if self.board[r][c] == PLAYER_X:
                    self.draw_x(x, y, cell_size // 2 - 10, PLAYER_X_COLOR)
                elif self.board[r][c] == PLAYER_O:
                    self.draw_o(x, y, cell_size // 2 - 10, PLAYER_O_COLOR)

        # Draw powerups
        for pu in self.available_powerups:
            pu_x, pu_y = self.get_powerup_position(pu)
            pygame.draw.circle(self.screen, POWERUP_COLOR, (pu_x, pu_y), 15)
            powerup_text = self.small_font.render(pu[0].upper(), True, (0,0,0))
            self.screen.blit(powerup_text, (pu_x - powerup_text.get_width() // 2, pu_y - powerup_text.get_height() // 2))

        # Draw UI elements
        opponent_name_text = self.small_font.render(f"Opponent: {self.current_level_data['opponent']['name']}", True, TEXT_COLOR)
        self.screen.blit(opponent_name_text, (20, 20))

        score_text = self.small_font.render(f"Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (20, 60))

        level_text = self.small_font.render(f"Level: {self.current_level_data['name']}", True, TEXT_COLOR)
        self.screen.blit(level_text, (20, 100))

        turn_text = self.small_font.render(f"Turn: {self.turn}", True, TEXT_COLOR)
        self.screen.blit(turn_text, (SCREEN_WIDTH - turn_text.get_width() - 20, 20))

        self.draw_player_abilities()

        # Draw Game Over overlay
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            win_text_str = ""
            if self.winner == PLAYER_X:
                win_text_str = "VICTORY!"
                win_color = (0, 255, 0)
            elif self.winner == PLAYER_O:
                win_text_str = "DEFEAT!"
                win_color = (255, 0, 0)
            else:
                win_text_str = "DRAW!"
                win_color = (255, 255, 0)

            win_text = self.font.render(win_text_str, True, win_color)
            self.screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))

            if self.winner == PLAYER_X and self.current_level < len(self.levels) - 1:
                next_level_text = self.small_font.render("Press ENTER for Next Level", True, TEXT_COLOR)
                self.screen.blit(next_level_text, (SCREEN_WIDTH // 2 - next_level_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
            elif self.winner == PLAYER_O or (self.winner is None and self.current_level == len(self.levels) - 1):
                 retry_text = self.small_font.render("Press ENTER to Retry", True, TEXT_COLOR)
                 self.screen.blit(retry_text, (SCREEN_WIDTH // 2 - retry_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
            else:
                next_level_text = self.small_font.render("Press ENTER for Next Level", True, TEXT_COLOR)
                self.screen.blit(next_level_text, (SCREEN_WIDTH // 2 - next_level_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))


            restart_button_rect = pygame.Rect(300, 450, 200, 50)
            menu_button_rect = pygame.Rect(300, 520, 200, 50)

            mouse_pos = pygame.mouse.get_pos()
            if restart_button_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, BUTTON_HOVER_COLOR, restart_button_rect)
            else:
                pygame.draw.rect(self.screen, BUTTON_COLOR, restart_button_rect)
            restart_text = self.small_font.render("Restart Game", True, TEXT_COLOR)
            self.screen.blit(restart_text, (restart_button_rect.centerx - restart_text.get_width() // 2, restart_button_rect.centery - restart_text.get_height() // 2))

            if menu_button_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, BUTTON_HOVER_COLOR, menu_button_rect)
            else:
                pygame.draw.rect(self.screen, BUTTON_COLOR, menu_button_rect)
            menu_text = self.small_font.render("To Menu", True, TEXT_COLOR)
            self.screen.blit(menu_text, (menu_button_rect.centerx - menu_text.get_width() // 2, menu_button_rect.centery - menu_text.get_height() // 2))

        # Draw Strategic Foresight highlights
        if self.show_strategic_foresight and not self.game_over:
            grid_size = self.current_level_data["grid_size"]
            cell_size = CELL_SIZE if grid_size == 3 else BIG_CELL_SIZE
            board_offset_x = (SCREEN_WIDTH - grid_size * cell_size) // 2
            board_offset_y = (SCREEN_HEIGHT - grid_size * cell_size) // 2

            potential_wins = self.find_potential_wins(PLAYER_X)
            for r, c in potential_wins:
                highlight_rect = pygame.Rect(board_offset_x + c * cell_size, board_offset_y + r * cell_size, cell_size, cell_size)
                pygame.draw.rect(self.screen, (255, 255, 0, 100), highlight_rect)

    def draw_game_over(self):
        self.screen.fill(BACKGROUND_COLOR)
        final_score_text = self.font.render("Game Over", True, TEXT_COLOR)
        self.screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, 150))

        score_display_text = self.small_font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_display_text, (SCREEN_WIDTH // 2 - score_display_text.get_width() // 2, 250))

        restart_button_rect = pygame.Rect(300, 350, 200, 50)
        menu_button_rect = pygame.Rect(300, 450, 200, 50)

        mouse_pos = pygame.mouse.get_pos()
        if restart_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, BUTTON_HOVER_COLOR, restart_button_rect)
        else:
            pygame.draw.rect(self.screen, BUTTON_COLOR, restart_button_rect)
        restart_text = self.small_font.render("Restart", True, TEXT_COLOR)
        self.screen.blit(restart_text, (restart_button_rect.centerx - restart_text.get_width() // 2, restart_button_rect.centery - restart_text.get_height() // 2))

        if menu_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, BUTTON_HOVER_COLOR, menu_button_rect)
        else:
            pygame.draw.rect(self.screen, BUTTON_COLOR, menu_button_rect)
        menu_text = self.small_font.render("Menu", True, TEXT_COLOR)
        self.screen.blit(menu_text, (menu_button_rect.centerx - menu_text.get_width() // 2, menu_button_rect.centery - menu_text.get_height() // 2))

    def draw_x(self, x, y, size, color):
        pygame.draw.line(self.screen, color, (x - size, y - size), (x + size, y + size), 5)
        pygame.draw.line(self.screen, color, (x + size, y - size), (x - size, y + size), 5)

    def draw_o(self, x, y, radius, color):
        pygame.draw.circle(self.screen, color, (x, y), radius, 5)

    def draw_player_abilities(self):
        ability_keys = list(self.player_abilities.keys())
        ability_map = {
            SPARK_OF_INSIGHT: "1: Insight",
            SHIELD_OF_STONE: "2: Block",
            WILDCARD: "3: Wildcard"
        }
        for i, ability in enumerate(ability_keys):
            text = f"{ability_map[ability]} ({self.player_abilities[ability]})"
            ability_text = self.small_font.render(text, True, TEXT_COLOR)
            self.screen.blit(ability_text, (SCREEN_WIDTH - ability_text.get_width() - 20, 70 + i * 30))

    def get_powerup_position(self, powerup_type):
        grid_size = self.current_level_data["grid_size"]
        cell_size = CELL_SIZE if grid_size == 3 else BIG_CELL_SIZE
        board_offset_x = (SCREEN_WIDTH - grid_size * cell_size) // 2
        board_offset_y = (SCREEN_HEIGHT - grid_size * cell_size) // 2

        # Simple placement for now - could be more sophisticated
        if powerup_type == self.available_powerups[0]:
            return board_offset_x + cell_size // 2, board_offset_y + grid_size * cell_size - cell_size // 2
        elif powerup_type == self.available_powerups[1]:
            return board_offset_x + grid_size * cell_size - cell_size // 2, board_offset_y + cell_size // 2
        return 0, 0 # Default

    def check_win(self):
        grid_size = len(self.board)
        # Check rows
        for r in range(grid_size):
            if self.board[r][0] != '' and self.board[r][0] == self.board[r][1] == self.board[r][2]:
                self.game_over = True
                self.winner = self.board[r][0]
                return

        # Check columns
        for c in range(grid_size):
            if self.board[0][c] != '' and self.board[0][c] == self.board[1][c] == self.board[2][c]:
                self.game_over = True
                self.winner = self.board[0][c]
                return

        # Check diagonals
        if self.board[0][0] != '' and self.board[0][0] == self.board[1][1] == self.board[2][2]:
            self.game_over = True
            self.winner = self.board[0][0]
            return
        if self.board[0][2] != '' and self.board[0][2] == self.board[1][1] == self.board[2][0]:
            self.game_over = True
            self.winner = self.board[0][2]
            return

        # Check for draw
        if all(self.board[r][c] != '' for r in range(grid_size) for c in range(grid_size)):
            self.game_over = True
            self.winner = None
            return

    def find_winning_move(self, token):
        grid_size = len(self.board)
        for r in range(grid_size):
            for c in range(grid_size):
                if self.board[r][c] == '':
                    self.board[r][c] = token
                    if self.check_win_condition(token):
                        self.board[r][c] = '' # backtrack
                        return r, c
                    self.board[r][c] = '' # backtrack
        return None

    def find_defensive_move(self, opponent_token):
        grid_size = len(self.board)
        for r in range(grid_size):
            for c in range(grid_size):
                if self.board[r][c] == '':
                    self.board[r][c] = opponent_token
                    if self.check_win_condition(opponent_token):
                        self.board[r][c] = '' # backtrack
                        return r, c
                    self.board[r][c] = '' # backtrack
        return None

    def check_win_condition(self, token):
        grid_size = len(self.board)
        # Check rows
        for r in range(grid_size):
            if all(self.board[r][c] == token for c in range(grid_size)):
                return True
        # Check columns
        for c in range(grid_size):
            if all(self.board[r][c] == token for r in range(grid_size)):
                return True
        # Check diagonals
        if all(self.board[i][i] == token for i in range(grid_size)):
            return True
        if all(self.board[i][grid_size - 1 - i] == token for i in range(grid_size)):
            return True
        return False

    def ai_move_random(self):
        grid_size = len(self.board)
        empty_cells = [(r, c) for r in range(grid_size) for c in range(grid_size) if self.board[r][c] == '']
        if empty_cells:
            r, c = random.choice(empty_cells)
            self.board[r][c] = PLAYER_O
            self.turn = PLAYER_X

    def ai_move_medium(self):
        grid_size = len(self.board)
        # Try to win
        win_move = self.find_winning_move(PLAYER_O)
        if win_move:
            self.board[win_move[0]][win_move[1]] = PLAYER_O
            self.turn = PLAYER_X
            return

        # Try to block player
        block_move = self.find_defensive_move(PLAYER_X)
        if block_move:
            self.board[block_move[0]][block_move[1]] = PLAYER_O
            self.turn = PLAYER_X
            return

        # Random move
        self.ai_move_random()

    def ai_move_hard(self):
        grid_size = len(self.board)
        best_score = -math.inf
        best_move = None
        
        # Check if there's a move that guarantees a win or draw
        # This is a simplified minimax implementation for Tic-Tac-Toe
        def minimax(board, depth, is_maximizing):
            if self.check_win_condition(PLAYER_O):
                return 10 - depth
            if self.check_win_condition(PLAYER_X):
                return depth - 10
            if all(board[r][c] != '' for r in range(grid_size) for c in range(grid_size)):
                return 0

            if is_maximizing:
                max_eval = -math.inf
                for r in range(grid_size):
                    for c in range(grid_size):
                        if board[r][c] == '':
                            board[r][c] = PLAYER_O
                            eval = minimax(board, depth + 1, False)
                            board[r][c] = '' # backtrack
                            max_eval = max(max_eval, eval)
                return max_eval
            else:
                min_eval = math.inf
                for r in range(grid_size):
                    for c in range(grid_size):
                        if board[r][c] == '':
                            board[r][c] = PLAYER_X
                            eval = minimax(board, depth + 1, True)
                            board[r][c] = '' # backtrack
                            min_eval = min(min_eval, eval)
                return min_eval

        for r in range(grid_size):
            for c in range(grid_size):
                if self.board[r][c] == '':
                    self.board[r][c] = PLAYER_O
                    # Create a copy of the board for minimax to modify
                    temp_board = [row[:] for row in self.board]
                    score = minimax(temp_board, 0, False)
                    self.board[r][c] = '' # backtrack

                    if score > best_score:
                        best_score = score
                        best_move = (r, c)
        
        if best_move:
            self.board[best_move[0]][best_move[1]] = PLAYER_O
            self.turn = PLAYER_X
        else: # Should not happen if there are empty cells
            self.ai_move_random()

    def ai_move_expert(self):
        # The Eldritch Abomination uses a 5x5 grid and advanced prediction.
        # This is a simplified implementation using a more extensive minimax.
        grid_size = len(self.board)
        best_score = -math.inf
        best_move = None
        
        def minimax(board, depth, is_maximizing):
            if self.check_win_condition(PLAYER_O):
                return 10 - depth
            if self.check_win_condition(PLAYER_X):
                return depth - 10
            if all(board[r][c] != '' for r in range(grid_size) for c in range(grid_size)):
                return 0

            if is_maximizing:
                max_eval = -math.inf
                for r in range(grid_size):
                    for c in range(grid_size):
                        if board[r][c] == '':
                            board[r][c] = PLAYER_O
                            eval = minimax(board, depth + 1, False)
                            board[r][c] = '' # backtrack
                            max_eval = max(max_eval, eval)
                return max_eval
            else:
                min_eval = math.inf
                for r in range(grid_size):
                    for c in range(grid_size):
                        if board[r][c] == '':
                            board[r][c] = PLAYER_X
                            eval = minimax(board, depth + 1, True)
                            board[r][c] = '' # backtrack
                            min_eval = min(min_eval, eval)
                return min_eval

        for r in range(grid_size):
            for c in range(grid_size):
                if self.board[r][c] == '':
                    self.board[r][c] = PLAYER_O
                    temp_board = [row[:] for row in self.board]
                    score = minimax(temp_board, 0, False)
                    self.board[r][c] = '' # backtrack

                    if score > best_score:
                        best_score = score
                        best_move = (r, c)
        
        if best_move:
            self.board[best_move[0]][best_move[1]] = PLAYER_O
            self.turn = PLAYER_X
        else:
            self.ai_move_random()

    def use_defensive_block(self):
        grid_size = len(self.board)
        # Check if player has an immediate winning move
        for r in range(grid_size):
            for c in range(grid_size):
                if self.board[r][c] == '':
                    self.board[r][c] = PLAYER_X
                    if self.check_win_condition(PLAYER_X):
                        self.board[r][c] = '' # backtrack
                        self.board[r][c] = PLAYER_O # Block it
                        self.turn = PLAYER_X
                        return True
                    self.board[r][c] = '' # backtrack
        return False

    def find_potential_wins(self, token):
        grid_size = len(self.board)
        potential_lines = []

        # Check rows
        for r in range(grid_size):
            if self.board[r].count(token) == grid_size - 1 and '' in self.board[r]:
                c = self.board[r].index('')
                potential_lines.append((r, c))

        # Check columns
        for c in range(grid_size):
            col_tokens = [self.board[r][c] for r in range(grid_size)]
            if col_tokens.count(token) == grid_size - 1 and '' in col_tokens:
                r = col_tokens.index('')
                potential_lines.append((r, c))

        # Check diagonals
        diag1_tokens = [self.board[i][i] for i in range(grid_size)]
        if diag1_tokens.count(token) == grid_size - 1 and '' in diag1_tokens:
            r = diag1_tokens.index('')
            potential_lines.append((r, r))

        diag2_tokens = [self.board[i][grid_size - 1 - i] for i in range(grid_size)]
        if diag2_tokens.count(token) == grid_size - 1 and '' in diag2_tokens:
            r = diag2_tokens.index('')
            potential_lines.append((r, grid_size - 1 - r))
        
        return list(set(potential_lines)) # Remove duplicates

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if self.game_state == MENU:
                    self.handle_menu_events(event)
                elif self.game_state == PLAYING:
                    self.handle_playing_events(event)
                elif self.game_state == GAME_OVER:
                    self.handle_game_over_events(event)

            if self.game_state == PLAYING:
                self.update()

            if self.game_state == MENU:
                self.draw_menu()
            elif self.game_state == PLAYING:
                self.draw_playing()
            elif self.game_state == GAME_OVER:
                self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
