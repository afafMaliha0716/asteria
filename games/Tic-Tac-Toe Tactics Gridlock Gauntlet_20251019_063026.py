
import pygame
import sys
import random
import math

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 3
CELL_SIZE = 80
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_SIZE * CELL_SIZE) // 2
GRID_OFFSET_Y = (SCREEN_HEIGHT - GRID_SIZE * CELL_SIZE) // 2
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
NEON_GREEN = (50, 255, 50)
NEON_BLUE = (50, 50, 255)
NEON_RED = (255, 50, 50)

# Game States
MENU = 0
PLAYING = 1
GAME_OVER = 2
WIN = 3

# Player Marker
PLAYER_MARKER = 'X'
AI_MARKER = 'O'

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5
        self.marker = PLAYER_MARKER
        self.abilities = {
            "quick_place": {"cooldown": 180, "current_cooldown": 0, "active": False},
            "marker_swap": {"cooldown": 300, "current_cooldown": 0, "active": False},
            "grid_freeze": {"cooldown": 480, "current_cooldown": 0, "active": False}
        }
        self.current_ability = None

    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        self.rect.x = max(0, min(SCREEN_WIDTH - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(SCREEN_HEIGHT - self.rect.height, self.rect.y))

    def update_cooldowns(self):
        for ability_name, ability_data in self.abilities.items():
            if ability_data["current_cooldown"] > 0:
                ability_data["current_cooldown"] -= 1
            if ability_data["active"]:
                ability_data["active_timer"] -= 1
                if ability_data["active_timer"] <= 0:
                    ability_data["active"] = False

    def can_use_ability(self, ability_name):
        return self.abilities[ability_name]["current_cooldown"] == 0 and not self.abilities[ability_name]["active"]

    def use_ability(self, ability_name, game_state):
        if self.can_use_ability(ability_name):
            self.abilities[ability_name]["current_cooldown"] = self.abilities[ability_name]["cooldown"]
            if ability_name == "quick_place":
                self.abilities[ability_name]["active"] = True
                self.abilities[ability_name]["active_timer"] = 30 # Quick place lasts for 30 frames
            elif ability_name == "marker_swap":
                self.abilities[ability_name]["active"] = True
                self.abilities[ability_name]["active_timer"] = 120 # Marker swap lasts for 2 seconds
                self.current_ability = "marker_swap"
            elif ability_name == "grid_freeze":
                self.abilities[ability_name]["active"] = True
                self.abilities[ability_name]["active_timer"] = 180 # Grid freeze lasts for 3 seconds
                game_state["grid_frozen"] = True
                game_state["grid_freeze_timer"] = 180
            return True
        return False

class AI(pygame.sprite.Sprite):
    def __init__(self, x, y, color, behavior, game_state):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3
        self.marker = AI_MARKER
        self.behavior = behavior
        self.game_state = game_state
        self.strategy_timer = 0

    def update(self, grid):
        self.strategy_timer -= 1
        if self.strategy_timer <= 0:
            self.make_move(grid)
            self.strategy_timer = random.randint(30, 90) # Recalculate move every 0.5 to 1.5 seconds

    def make_move(self, grid):
        if self.behavior == "basic_ai":
            self.basic_ai_move(grid)
        elif self.behavior == "disruptor":
            self.disruptor_ai_move(grid)
        elif self.behavior == "mastermind":
            self.mastermind_ai_move(grid)

    def basic_ai_move(self, grid):
        # Prioritize blocking player win, then creating own win
        best_move = self.find_best_move(grid, AI_MARKER)
        if best_move:
            grid[best_move[0]][best_move[1]] = self.marker
            return

        best_move = self.find_best_move(grid, PLAYER_MARKER)
        if best_move:
            grid[best_move[0]][best_move[1]] = self.marker
            return

        # Random move if no strategic move found
        empty_cells = []
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if grid[r][c] == "":
                    empty_cells.append((r, c))
        if empty_cells:
            move = random.choice(empty_cells)
            grid[move[0]][move[1]] = self.marker

    def disruptor_ai_move(self, grid):
        # Basic AI + interaction with arena elements (placeholder for now)
        self.basic_ai_move(grid)
        # Simulate environmental interaction for disruptor
        if random.random() < 0.1: # 10% chance to trigger an arena element
            self.trigger_arena_element()

    def mastermind_ai_move(self, grid):
        # More advanced AI, considers future moves (simplified minimax)
        best_score = -math.inf
        best_move = None
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if grid[r][c] == "":
                    grid[r][c] = self.marker
                    score = self.minimax(grid, False, 0)
                    grid[r][c] = ""
                    if score > best_score:
                        best_score = score
                        best_move = (r, c)

        if best_move:
            grid[best_move[0]][best_move[1]] = self.marker

    def find_best_move(self, grid, marker_to_check):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if grid[r][c] == "":
                    grid[r][c] = marker_to_check
                    if self.check_win(grid, marker_to_check):
                        grid[r][c] = "" # backtrack
                        return (r, c)
                    grid[r][c] = "" # backtrack
        return None

    def check_win(self, grid, marker):
        # Check rows
        for r in range(GRID_SIZE):
            if all(grid[r][c] == marker for c in range(GRID_SIZE)):
                return True
        # Check columns
        for c in range(GRID_SIZE):
            if all(grid[r][c] == marker for r in range(GRID_SIZE)):
                return True
        # Check diagonals
        if all(grid[i][i] == marker for i in range(GRID_SIZE)):
            return True
        if all(grid[i][GRID_SIZE - 1 - i] == marker for i in range(GRID_SIZE)):
            return True
        return False

    def is_board_full(self, grid):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if grid[r][c] == "":
                    return False
        return True

    def evaluate_board(self, grid):
        if self.check_win(grid, self.marker):
            return 10
        if self.check_win(grid, PLAYER_MARKER):
            return -10
        return 0

    def minimax(self, grid, is_maximizing, depth):
        score = self.evaluate_board(grid)
        if score == 10:
            return score - depth
        if score == -10:
            return score + depth
        if self.is_board_full(grid):
            return 0

        if is_maximizing:
            max_eval = -math.inf
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    if grid[r][c] == "":
                        grid[r][c] = self.marker
                        eval = self.minimax(grid, False, depth + 1)
                        grid[r][c] = ""
                        max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = math.inf
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    if grid[r][c] == "":
                        grid[r][c] = PLAYER_MARKER
                        eval = self.minimax(grid, True, depth + 1)
                        grid[r][c] = ""
                        min_eval = min(min_eval, eval)
            return min_eval

    def trigger_arena_element(self):
        # Placeholder for disruptor specific actions
        pass

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

class InteractiveElement(pygame.sprite.Sprite):
    def __init__(self, x, y, element_type, effect, color):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.type = element_type
        self.effect = effect
        self.activated = False
        self.activation_timer = 0

    def activate(self):
        if not self.activated:
            self.activated = True
            self.activation_timer = 120 # Element is active for 2 seconds
            return True
        return False

    def update(self):
        if self.activated:
            self.activation_timer -= 1
            if self.activation_timer <= 0:
                self.activated = False

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, powerup_type, color):
        super().__init__()
        self.image = pygame.Surface((25, 25))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.type = powerup_type

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tic-Tac-Toe Tactics: Gridlock Gauntlet")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)

        self.game_state = MENU
        self.score = 0
        self.current_level_data = None
        self.level_number = 1
        self.matches_won_in_level = 0
        self.total_matches_to_win = 3 # Example: Win 3 matches to clear a level

        self.player = None
        self.ai_opponent = None
        self.obstacles = pygame.sprite.Group()
        self.interactive_elements = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()

        self.tic_tac_toe_grid = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.cursor_pos = [0, 0] # Grid coordinates for cursor
        self.cursor_render_pos = [GRID_OFFSET_X + self.cursor_pos[1] * CELL_SIZE + CELL_SIZE // 2,
                                  GRID_OFFSET_Y + self.cursor_pos[0] * CELL_SIZE + CELL_SIZE // 2]
        self.cursor_color = NEON_GREEN

        self.round_time_limit = 90
        self.current_round_time = 0
        self.round_timer_active = False

        self.level_configs = {
            1: {
                "level_number": 1,
                "name": "The Training Grid",
                "description": "Welcome to the Gridlock Gauntlet! This introductory level will teach you the basics of dynamic grid placement and timed rounds. Focus on understanding the grid and your opponent.",
                "size": {"width": SCREEN_WIDTH, "height": SCREEN_HEIGHT},
                "spawn_points": [{"x": 400, "y": 300, "type": "player_center"}, {"x": 400, "y": 300, "type": "enemy_center"}],
                "obstacles": [{"x": 200, "y": 150, "width": 400, "height": 20, "type": "static_barrier", "description": "A sturdy barrier that blocks movement and placement directly through it. You'll need to go around."}],
                "interactive_elements": [{"x": 350, "y": 450, "type": "shifting_tile_activator", "description": "Activating this will temporarily shift a tile in the tic-tac-toe grid, changing its position.", "effect": "shift_tile_at_grid_position_2_1"},
                                         {"x": 450, "y": 450, "type": "shifting_tile_activator", "description": "Activating this will temporarily shift another tile in the tic-tac-toe grid.", "effect": "shift_tile_at_grid_position_2_1"}],
                "powerups": [],
                "enemies": [{"x": 400, "y": 300, "type": "basic_ai", "description": "A simple opponent that will try to block your wins and create their own.", "patrol_path": []}],
                "objectives": [{"type": "win_tic_tac_toe", "description": "Achieve a tic-tac-toe win on the 3x3 grid against the basic AI."}],
                "difficulty": "easy",
                "time_limit": 90
            }
            # Add more levels here
        }

        self.load_level(1)

    def reset_game(self):
        self.score = 0
        self.level_number = 1
        self.matches_won_in_level = 0
        self.load_level(self.level_number)

    def load_level(self, level_num):
        if level_num not in self.level_configs:
            print(f"Error: Level {level_num} not found.")
            return

        self.current_level_data = self.level_configs[level_num]
        self.round_time_limit = self.current_level_data["time_limit"]
        self.matches_won_in_level = 0 # Reset matches won for the new level
        self.total_matches_to_win = 3 # Reset for each level

        # Clear existing sprites
        self.obstacles.empty()
        self.interactive_elements.empty()
        self.powerups.empty()
        self.all_sprites.empty()

        # Create player
        player_spawn = next(s for s in self.current_level_data["spawn_points"] if s["type"] == "player_center")
        self.player = Player(player_spawn["x"], player_spawn["y"], NEON_GREEN)
        self.all_sprites.add(self.player)

        # Create AI opponent(s)
        ai_spawn = next(s for s in self.current_level_data["spawn_points"] if s["type"] == "enemy_center")
        for enemy_data in self.current_level_data["enemies"]:
            ai_color = NEON_RED
            if enemy_data["type"] == "disruptor":
                ai_color = MAGENTA
            elif enemy_data["type"] == "mastermind":
                ai_color = BLUE
            self.ai_opponent = AI(ai_spawn["x"], ai_spawn["y"], ai_color, enemy_data["type"], {"grid_frozen": False, "grid_freeze_timer": 0})
            self.all_sprites.add(self.ai_opponent)

        # Create obstacles
        for obs_data in self.current_level_data["obstacles"]:
            obstacle = Obstacle(obs_data["x"], obs_data["y"], obs_data["width"], obs_data["height"], (100, 100, 100))
            self.obstacles.add(obstacle)
            self.all_sprites.add(obstacle)

        # Create interactive elements
        for ie_data in self.current_level_data["interactive_elements"]:
            color = YELLOW
            if ie_data["type"] == "shifting_tile_activator":
                color = CYAN
            element = InteractiveElement(ie_data["x"], ie_data["y"], ie_data["type"], ie_data["effect"], color)
            self.interactive_elements.add(element)
            self.all_sprites.add(element)

        # Create powerups
        for pu_data in self.current_level_data["powerups"]:
            color = YELLOW
            if pu_data["type"] == "time_warp":
                color = YELLOW
            elif pu_data["type"] == "strategic_insight":
                color = MAGENTA
            powerup = PowerUp(pu_data["x"], pu_data["y"], pu_data["type"], color)
            self.powerups.add(powerup)
            self.all_sprites.add(powerup)

        self.reset_tic_tac_toe_grid()
        self.cursor_pos = [0, 0]
        self.update_cursor_render_pos()
        self.current_round_time = self.round_time_limit
        self.round_timer_active = True
        self.ai_opponent.strategy_timer = random.randint(30, 90) # Initialize AI strategy timer

    def reset_tic_tac_toe_grid(self):
        self.tic_tac_toe_grid = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    def update_cursor_render_pos(self):
        self.cursor_render_pos[0] = GRID_OFFSET_X + self.cursor_pos[1] * CELL_SIZE + CELL_SIZE // 2
        self.cursor_render_pos[1] = GRID_OFFSET_Y + self.cursor_pos[0] * CELL_SIZE + CELL_SIZE // 2

    def check_tic_tac_toe_win(self, board, marker):
        # Check rows
        for r in range(GRID_SIZE):
            if all(board[r][c] == marker for c in range(GRID_SIZE)):
                return True
        # Check columns
        for c in range(GRID_SIZE):
            if all(board[r][c] == marker for r in range(GRID_SIZE)):
                return True
        # Check diagonals
        if all(board[i][i] == marker for i in range(GRID_SIZE)):
            return True
        if all(board[i][GRID_SIZE - 1 - i] == marker for i in range(GRID_SIZE)):
            return True
        return False

    def is_tic_tac_toe_board_full(self, board):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if board[r][c] == "":
                    return False
        return True

    def handle_event(self, event):
        if self.game_state == MENU:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.reset_game()
                    self.game_state = PLAYING
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        elif self.game_state == PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    self.player.move(-1, 0)
                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    self.player.move(1, 0)
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    self.player.move(0, -1)
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    self.player.move(0, 1)

                if event.key == pygame.K_RETURN: # Place marker
                    if self.tic_tac_toe_grid[self.cursor_pos[0]][self.cursor_pos[1]] == "":
                        self.tic_tac_toe_grid[self.cursor_pos[0]][self.cursor_pos[1]] = self.player.marker
                        self.round_timer_active = True # Reset timer on player move
                        self.score += 10 # Simple score for placing marker
                        self.check_round_end()

                if event.key == pygame.K_1: # Ability 1: Quick Place
                    self.player.use_ability("quick_place", {"grid_frozen": False, "grid_freeze_timer": 0})
                    self.cursor_color = NEON_GREEN # Indicate ability is active
                if event.key == pygame.K_2: # Ability 2: Marker Swap
                    self.player.use_ability("marker_swap", {"grid_frozen": False, "grid_freeze_timer": 0})
                    self.cursor_color = NEON_BLUE
                if event.key == pygame.K_3: # Ability 3: Grid Freeze
                    self.player.use_ability("grid_freeze", {"grid_frozen": False, "grid_freeze_timer": 0})
                    self.cursor_color = NEON_RED

                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    # Update cursor visual position based on grid movement
                    self.update_cursor_render_pos()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check for interaction with interactive elements
                for element in self.interactive_elements:
                    if element.rect.collidepoint(event.pos):
                        if element.activate():
                            self.process_interactive_element_effect(element.effect)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w or event.key == pygame.K_UP or \
                   event.key == pygame.K_s or event.key == pygame.K_DOWN or \
                   event.key == pygame.K_a or event.key == pygame.K_LEFT or \
                   event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    self.player.speed = 5 # Reset speed

        elif self.game_state == GAME_OVER or self.game_state == WIN:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.reset_game()
                    self.game_state = PLAYING
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    def process_interactive_element_effect(self, effect):
        if effect == "shift_tile_at_grid_position_2_1":
            # Example: Shift the tile at row 2, column 1 to a random empty spot
            if self.tic_tac_toe_grid[2][1] != "":
                original_marker = self.tic_tac_toe_grid[2][1]
                self.tic_tac_toe_grid[2][1] = ""
                empty_cells = []
                for r in range(GRID_SIZE):
                    for c in range(GRID_SIZE):
                        if self.tic_tac_toe_grid[r][c] == "":
                            empty_cells.append((r, c))
                if empty_cells:
                    new_pos = random.choice(empty_cells)
                    self.tic_tac_toe_grid[new_pos[0]][new_pos[1]] = original_marker
                    print(f"Tile shifted to {new_pos}")

    def update(self):
        self.player.update_cooldowns()
        self.interactive_elements.update()

        if self.game_state == PLAYING:
            self.ai_opponent.update(self.tic_tac_toe_grid)
            self.check_round_end()

            if self.round_timer_active:
                self.current_round_time -= 1 / FPS
                if self.current_round_time <= 0:
                    self.lose_round()

            if self.player.abilities["grid_freeze"]["active"]:
                if self.ai_opponent:
                    self.ai_opponent.strategy_timer = max(0, self.ai_opponent.strategy_timer - 1) # Slow down AI decision making

            if "grid_frozen" in self.ai_opponent.game_state and self.ai_opponent.game_state["grid_frozen"]:
                self.ai_opponent.game_state["grid_freeze_timer"] -= 1
                if self.ai_opponent.game_state["grid_freeze_timer"] <= 0:
                    self.ai_opponent.game_state["grid_frozen"] = False
                    self.player.abilities["grid_freeze"]["active"] = False # Deactivate player ability too

            # Check for powerup collection
            collected_powerup = pygame.sprite.spritecollideany(self.player, self.powerups)
            if collected_powerup:
                self.collect_powerup(collected_powerup)
                collected_powerup.kill()

            # Collision with obstacles
            for obstacle in self.obstacles:
                if pygame.sprite.collide_rect(self.player, obstacle):
                    # Simple push-back logic (can be improved)
                    if self.player.rect.centery < obstacle.rect.centery:
                        self.player.rect.bottom = obstacle.rect.top
                    if self.player.rect.centery > obstacle.rect.centery:
                        self.player.rect.top = obstacle.rect.bottom
                    if self.player.rect.centerx < obstacle.rect.centerx:
                        self.player.rect.right = obstacle.rect.left
                    if self.player.rect.centerx > obstacle.rect.centerx:
                        self.player.rect.left = obstacle.rect.right

    def check_round_end(self):
        if self.check_tic_tac_toe_win(self.tic_tac_toe_grid, self.player.marker):
            self.win_round()
        elif self.check_tic_tac_toe_win(self.tic_tac_toe_grid, self.ai_opponent.marker):
            self.lose_round()
        elif self.is_tic_tac_toe_board_full(self.tic_tac_toe_grid):
            self.draw_round() # Or treat as loss for simplicity

    def win_round(self):
        self.score += 50
        self.matches_won_in_level += 1
        print(f"Round Won! Matches won: {self.matches_won_in_level}/{self.total_matches_to_win}")
        self.round_timer_active = False
        if self.matches_won_in_level >= self.total_matches_to_win:
            self.game_state = WIN
            print("Level Cleared!")
        else:
            self.load_level(self.level_number) # Reload same level for next match
            self.player.abilities["quick_place"]["active"] = False # Reset abilities
            self.player.abilities["marker_swap"]["active"] = False
            self.player.abilities["grid_freeze"]["active"] = False
            self.player.current_ability = None
            self.cursor_color = NEON_GREEN


    def lose_round(self):
        self.score -= 20
        self.round_timer_active = False
        print("Round Lost!")
        self.game_state = GAME_OVER # For now, losing one round ends the game. Can be adjusted for multiple lives.
        self.player.abilities["quick_place"]["active"] = False # Reset abilities
        self.player.abilities["marker_swap"]["active"] = False
        self.player.abilities["grid_freeze"]["active"] = False
        self.player.current_ability = None
        self.cursor_color = NEON_GREEN


    def draw_round(self):
        self.score += 5
        print("Round Draw!")
        self.round_timer_active = False
        self.load_level(self.level_number) # Reload same level for next match
        self.player.abilities["quick_place"]["active"] = False # Reset abilities
        self.player.abilities["marker_swap"]["active"] = False
        self.player.abilities["grid_freeze"]["active"] = False
        self.player.current_ability = None
        self.cursor_color = NEON_GREEN

    def collect_powerup(self, powerup):
        self.score += 25
        if powerup.type == "time_warp":
            self.current_round_time = min(self.round_time_limit, self.current_round_time + 30) # Add 30 seconds
            print("Powerup: Time Warp!")
        elif powerup.type == "strategic_insight":
            print("Powerup: Strategic Insight! (Highlighting not implemented visually)")
            # Visual highlighting of win lines could be implemented here
        elif powerup.type == "quick_place_boost": # Example of another powerup
            self.player.abilities["quick_place"]["cooldown"] = max(60, self.player.abilities["quick_place"]["cooldown"] - 60)
            print("Powerup: Quicker Quick Place!")

    def draw(self):
        self.screen.fill(BLACK)

        if self.game_state == MENU:
            self.draw_menu()
        elif self.game_state == PLAYING:
            self.draw_playing()
        elif self.game_state == GAME_OVER:
            self.draw_game_over()
        elif self.game_state == WIN:
            self.draw_win()

        pygame.display.flip()

    def draw_menu(self):
        title_text = self.large_font.render("Tic-Tac-Toe Tactics", True, NEON_GREEN)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(title_text, title_rect)

        start_text = self.font.render("Press SPACE to Start", True, WHITE)
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(start_text, start_rect)

        quit_text = self.font.render("Press ESC to Quit", True, WHITE)
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(quit_text, quit_rect)

    def draw_playing(self):
        # Draw background elements (obstacles, interactive elements)
        self.obstacles.draw(self.screen)
        self.interactive_elements.draw(self.screen)
        self.powerups.draw(self.screen)

        # Draw the tic-tac-toe grid
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                cell_x = GRID_OFFSET_X + c * CELL_SIZE
                cell_y = GRID_OFFSET_Y + r * CELL_SIZE
                pygame.draw.rect(self.screen, (50, 50, 50), (cell_x, cell_y, CELL_SIZE, CELL_SIZE), 2)

                marker = self.tic_tac_toe_grid[r][c]
                if marker == PLAYER_MARKER:
                    color = NEON_GREEN
                    pygame.draw.line(self.screen, color, (cell_x + 15, cell_y + 15), (cell_x + CELL_SIZE - 15, cell_y + CELL_SIZE - 15), 5)
                    pygame.draw.line(self.screen, color, (cell_x + 15, cell_y + CELL_SIZE - 15), (cell_x + CELL_SIZE - 15, cell_y + 15), 5)
                elif marker == AI_MARKER:
                    color = NEON_RED
                    pygame.draw.circle(self.screen, color, (cell_x + CELL_SIZE // 2, cell_y + CELL_SIZE // 2), CELL_SIZE // 3, 5)

        # Draw player cursor
        pygame.draw.circle(self.screen, self.cursor_color, self.cursor_render_pos, 15, 3)

        # Draw sprites (player and AI)
        self.all_sprites.draw(self.screen)

        # Draw HUD
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (20, 20))

        time_left = int(self.current_round_time)
        time_text = self.font.render(f"Time: {time_left}", True, WHITE)
        self.screen.blit(time_text, (SCREEN_WIDTH - 100, 20))

        level_text = self.font.render(f"Level: {self.level_number} ({self.matches_won_in_level}/{self.total_matches_to_win})", True, WHITE)
        self.screen.blit(level_text, (20, 60))

        # Draw ability cooldowns
        ability_y_offset = 100
        for ability_name, ability_data in self.player.abilities.items():
            text = f"{ability_name.replace('_', ' ').title()}: "
            if ability_data["current_cooldown"] > 0:
                cooldown_percent = (ability_data["cooldown"] - ability_data["current_cooldown"]) / ability_data["cooldown"]
                text += f"[{'#' * int(10 * cooldown_percent)}{'-' * int(10 * (1 - cooldown_percent))}]"
            elif ability_data["active"]:
                text += "[ACTIVE]"
            else:
                text += "[READY]"
            ability_surface = self.font.render(text, True, WHITE)
            self.screen.blit(ability_surface, (20, ability_y_offset))
            ability_y_offset += 30

    def draw_game_over(self):
        game_over_text = self.large_font.render("Game Over", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(game_over_text, game_over_rect)

        final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(final_score_text, final_score_rect)

        restart_text = self.font.render("Press ENTER to Restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)

        quit_text = self.font.render("Press ESC to Quit", True, WHITE)
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(quit_text, quit_rect)

    def draw_win(self):
        win_text = self.large_font.render("Level Complete!", True, GREEN)
        win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(win_text, win_rect)

        final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(final_score_text, final_score_rect)

        restart_text = self.font.render("Press ENTER to Continue to Next Level (if any)", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)

        quit_text = self.font.render("Press ESC to Quit", True, WHITE)
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(quit_text, quit_rect)


    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.handle_event(event)

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
