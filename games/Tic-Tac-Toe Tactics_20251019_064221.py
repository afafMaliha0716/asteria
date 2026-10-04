
import pygame
import sys
import random
import math

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

# Game States
MENU = 0
PLAYING = 1
GAME_OVER = 2
WIN_SCREEN = 3

# Player & Enemy Properties
PLAYER_SPEED = 3
ENEMY_SPEED = 2
PLAYER_SIZE = 30
ENEMY_SIZE = 30
POWERUP_SIZE = 20

# Tic-Tac-Toe Grid
GRID_SIZE = 3
CELL_SIZE = 100
GRID_OFFSET_X = (SCREEN_WIDTH - (GRID_SIZE * CELL_SIZE)) // 2
GRID_OFFSET_Y = (SCREEN_HEIGHT - (GRID_SIZE * CELL_SIZE)) // 2

# Abilities
TELEPORT_MARKER_COST = 1
BLOCKER_BEAM_COST = 1
DOUBLE_MARK_COST = 1

# Power-ups
GRID_SHIFT_COST = 2
MARKER_ERASE_COST = 2

# --- Classes ---

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.x = x
        self.y = y
        self.score = 0
        self.abilities = {
            "Teleport Marker": {"count": 1, "cost": TELEPORT_MARKER_COST},
            "Blocker Beam": {"count": 1, "cost": BLOCKER_BEAM_COST},
            "Double Mark": {"count": 1, "cost": DOUBLE_MARK_COST}
        }
        self.tokens = 0

    def move(self, dx, dy):
        self.x += dx * PLAYER_SPEED
        self.y += dy * PLAYER_SPEED
        self.rect.center = (self.x, self.y)

        # Keep player within screen bounds
        if self.x < PLAYER_SIZE // 2:
            self.x = PLAYER_SIZE // 2
        if self.x > SCREEN_WIDTH - PLAYER_SIZE // 2:
            self.x = SCREEN_WIDTH - PLAYER_SIZE // 2
        if self.y < PLAYER_SIZE // 2:
            self.y = PLAYER_SIZE // 2
        if self.y > SCREEN_HEIGHT - PLAYER_SIZE // 2:
            self.y = SCREEN_HEIGHT - PLAYER_SIZE // 2

    def collect_powerup(self, powerup_type):
        if powerup_type == "strategist_token":
            self.tokens += 1
            print("Collected Strategist Token")
        elif powerup_type == "reinforcement_card":
            self.tokens += 1
            print("Collected Reinforcement Card")
        elif powerup_type == "health_pack":
            print("Collected Health Pack (not implemented)")

    def use_ability(self, ability_name, *args):
        if ability_name in self.abilities and self.abilities[ability_name]["count"] > 0 and self.tokens >= self.abilities[ability_name]["cost"]:
            self.abilities[ability_name]["count"] -= 1
            self.tokens -= self.abilities[ability_name]["cost"]
            print(f"Used {ability_name}")
            return True
        return False

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type):
        super().__init__()
        self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
        if enemy_type == "basic":
            self.image.fill(RED)
        else:
            self.image.fill(GREEN) # Placeholder for future types
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.patrol_path = None
        self.patrol_index = 0
        self.target_x = x
        self.target_y = y
        self.behavior = None

        if enemy_type == "basic":
            self.behavior = self.basic_behavior

    def set_patrol_path(self, path):
        self.patrol_path = path
        self.target_x, self.target_y = path[0]

    def basic_behavior(self):
        if self.patrol_path:
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = math.hypot(dx, dy)

            if distance < ENEMY_SPEED:
                self.patrol_index = (self.patrol_index + 1) % len(self.patrol_path)
                self.target_x, self.target_y = self.patrol_path[self.patrol_index]
            else:
                move_x = (dx / distance) * ENEMY_SPEED
                move_y = (dy / distance) * ENEMY_SPEED
                self.x += move_x
                self.y += move_y
                self.rect.center = (self.x, self.y)

    def update(self):
        if self.behavior:
            self.behavior()

class TicTacToeGrid:
    def __init__(self, x_offset, y_offset, cell_size):
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.cell_size = cell_size
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.player_marker = 'X'
        self.enemy_marker = 'O'
        self.player_turn = True
        self.blocker_beam_active = False
        self.blocker_beam_pos = None
        self.blocker_beam_timer = 0
        self.available_cells = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)]

    def draw(self, surface):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                rect = pygame.Rect(self.x_offset + c * self.cell_size,
                                   self.y_offset + r * self.cell_size,
                                   self.cell_size, self.cell_size)
                pygame.draw.rect(surface, GRAY, rect, 2)

                marker = self.grid[r][c]
                if marker == self.player_marker:
                    pygame.draw.line(surface, BLUE, rect.topleft, rect.bottomright, 5)
                    pygame.draw.line(surface, BLUE, rect.topright, rect.bottomleft, 5)
                elif marker == self.enemy_marker:
                    pygame.draw.circle(surface, RED, rect.center, self.cell_size // 3, 5)

                if self.blocker_beam_active and self.blocker_beam_pos == (r, c):
                    beam_rect = pygame.Rect(self.x_offset + c * self.cell_size,
                                            self.y_offset + r * self.cell_size,
                                            self.cell_size, self.cell_size)
                    pygame.draw.rect(surface, MAGENTA, beam_rect, 5)

    def get_cell_from_mouse(self, mouse_pos):
        mx, my = mouse_pos
        if (self.x_offset <= mx < self.x_offset + GRID_SIZE * self.cell_size and
                self.y_offset <= my < self.y_offset + GRID_SIZE * self.cell_size):
            col = (mx - self.x_offset) // self.cell_size
            row = (my - self.y_offset) // self.cell_size
            return row, col
        return None

    def place_marker(self, row, col, marker):
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE and self.grid[row][col] is None:
            if self.blocker_beam_active and self.blocker_beam_pos == (row, col):
                print("Cell is blocked by Blocker Beam!")
                return False
            self.grid[row][col] = marker
            self.available_cells.remove((row, col))
            return True
        return False

    def check_win(self, marker):
        # Check rows
        for r in range(GRID_SIZE):
            if all(self.grid[r][c] == marker for c in range(GRID_SIZE)):
                return True
        # Check columns
        for c in range(GRID_SIZE):
            if all(self.grid[r][c] == marker for r in range(GRID_SIZE)):
                return True
        # Check diagonals
        if all(self.grid[i][i] == marker for i in range(GRID_SIZE)):
            return True
        if all(self.grid[i][GRID_SIZE - 1 - i] == marker for i in range(GRID_SIZE)):
            return True
        return False

    def is_full(self):
        return len(self.available_cells) == 0

    def reset_grid(self):
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.player_turn = True
        self.blocker_beam_active = False
        self.blocker_beam_pos = None
        self.blocker_beam_timer = 0
        self.available_cells = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)]

    def update_blocker_beam(self):
        if self.blocker_beam_active:
            self.blocker_beam_timer -= 1
            if self.blocker_beam_timer <= 0:
                self.blocker_beam_active = False
                self.blocker_beam_pos = None

    def shuffle_grid(self):
        all_markers = [marker for row in self.grid for marker in row if marker is not None]
        random.shuffle(all_markers)
        current_index = 0
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if current_index < len(all_markers):
                    self.grid[r][c] = all_markers[current_index]
                    current_index += 1
                else:
                    self.grid[r][c] = None
        self.available_cells = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if self.grid[r][c] is None]


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.image = pygame.Surface((POWERUP_SIZE, POWERUP_SIZE))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.type = type

        if type == "strategist_token":
            self.image.fill(YELLOW)
        elif type == "reinforcement_card":
            self.image.fill(CYAN)
        elif type == "health_pack":
            self.image.fill(GREEN)
        else:
            self.image.fill(WHITE)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tic-Tac-Toe Tactics")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.game_state = MENU
        self.player = None
        self.enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.tic_tac_toe_grid = TicTacToeGrid(GRID_OFFSET_X, GRID_OFFSET_Y, CELL_SIZE)
        self.level_data = {
            "level_number": 1,
            "name": "The Grand Opening Gambit",
            "description": "Welcome to Tic-Tac-Toe Tactics! This introductory level will guide you through the core mechanics. Your objective is to outwit the opponent by strategically placing your markers and utilizing your unique abilities. Collect the scattered power-ups and learn to adapt your strategy to overcome the initial challenges.",
            "size": {"width": 800, "height": 600},
            "spawn_points": [
                {"x": 100, "y": 100, "type": "player"},
                {"x": 600, "y": 500, "type": "enemy"}
            ],
            "obstacles": [
                {"x": 250, "y": 250, "width": 80, "height": 80, "type": "block"},
                {"x": 550, "y": 150, "width": 50, "height": 50, "type": "rock"}
            ],
            "powerups": [
                {"x": 300, "y": 150, "type": "strategist_token"},
                {"x": 500, "y": 450, "type": "reinforcement_card"},
                {"x": 150, "y": 400, "type": "health_pack"}
            ],
            "enemies": [
                {"x": 400, "y": 300, "type": "basic", "patrol_path": [[400, 300], [400, 350], [450, 350], [450, 300]]},
                {"x": 200, "y": 450, "type": "basic", "patrol_path": [[200, 450], [250, 450]]}
            ],
            "objectives": [
                {"type": "defeat", "target": "enemies", "count": 2},
                {"type": "win_round", "target": "tic_tac_toe", "count": 1}
            ],
            "difficulty": "easy",
            "time_limit": 180
        }
        self.current_objective_count = {}
        self.time_remaining = 0

    def reset_game(self):
        self.enemies.empty()
        self.powerups.empty()
        self.all_sprites.empty()
        self.tic_tac_toe_grid.reset_grid()
        self.current_objective_count = {}
        self.time_remaining = 0

    def load_level(self, level_data):
        self.reset_game()

        # Player and Enemy Spawn Points
        player_spawn = next(s for s in level_data["spawn_points"] if s["type"] == "player")
        self.player = Player(player_spawn["x"], player_spawn["y"])
        self.all_sprites.add(self.player)

        for enemy_data in level_data["enemies"]:
            enemy = Enemy(enemy_data["x"], enemy_data["y"], enemy_data["type"])
            if "patrol_path" in enemy_data:
                enemy.set_patrol_path(enemy_data["patrol_path"])
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

        # Power-ups
        for powerup_data in level_data["powerups"]:
            powerup = PowerUp(powerup_data["x"], powerup_data["y"], powerup_data["type"])
            self.powerups.add(powerup)
            self.all_sprites.add(powerup)

        # Objectives
        for obj in level_data["objectives"]:
            if obj["type"] == "defeat":
                self.current_objective_count[obj["target"]] = 0
            elif obj["type"] == "win_round":
                self.current_objective_count[obj["target"]] = 0

        self.time_remaining = level_data["time_limit"]

    def handle_menu(self):
        self.screen.fill(BLACK)
        title_text = self.font.render("Tic-Tac-Toe Tactics", True, WHITE)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))

        start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 25, 200, 50)
        pygame.draw.rect(self.screen, BLUE, start_button_rect)
        start_text = self.font.render("Start Game", True, WHITE)
        self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2 - start_text.get_height() // 2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button_rect.collidepoint(event.pos):
                    self.load_level(self.level_data)
                    self.game_state = PLAYING

    def handle_playing(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.tic_tac_toe_grid.player_turn:
                    row, col = self.tic_tac_toe_grid.get_cell_from_mouse(event.pos)
                    if row is not None and col is not None:
                        if self.tic_tac_toe_grid.place_marker(row, col, self.tic_tac_toe_grid.player_marker):
                            self.tic_tac_toe_grid.player_turn = False
                            if self.tic_tac_toe_grid.check_win(self.tic_tac_toe_grid.player_marker):
                                self.game_state = WIN_SCREEN
                            elif self.tic_tac_toe_grid.is_full():
                                self.game_state = GAME_OVER # Draw

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.use_ability("Teleport Marker")
                if event.key == pygame.K_2:
                    self.use_ability("Blocker Beam")
                if event.key == pygame.K_3:
                    self.use_ability("Double Mark")
                if event.key == pygame.K_4:
                    self.use_powerup("Grid Shift")
                if event.key == pygame.K_5:
                    self.use_powerup("Marker Erase")

        # Player Movement
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
        self.player.move(dx, dy)

        # Enemy AI (Basic)
        if not self.tic_tac_toe_grid.player_turn:
            for enemy in self.enemies:
                enemy.update()

            # Simple AI to make a move after player turn
            if not self.tic_tac_toe_grid.player_turn and not self.tic_tac_toe_grid.blocker_beam_active:
                if not self.tic_tac_toe_grid.is_full():
                    enemy_move_made = False
                    # Try to win
                    for r in range(GRID_SIZE):
                        for c in range(GRID_SIZE):
                            if self.tic_tac_toe_grid.grid[r][c] is None:
                                temp_grid = [row[:] for row in self.tic_tac_toe_grid.grid]
                                temp_grid[r][c] = self.tic_tac_toe_grid.enemy_marker
                                if self.check_win_on_grid(temp_grid, self.tic_tac_toe_grid.enemy_marker):
                                    if self.tic_tac_toe_grid.place_marker(r, c, self.tic_tac_toe_grid.enemy_marker):
                                        enemy_move_made = True
                                        break
                        if enemy_move_made: break

                    if not enemy_move_made:
                        # Try to block player win
                        for r in range(GRID_SIZE):
                            for c in range(GRID_SIZE):
                                if self.tic_tac_toe_grid.grid[r][c] is None:
                                    temp_grid = [row[:] for row in self.tic_tac_toe_grid.grid]
                                    temp_grid[r][c] = self.tic_tac_toe_grid.player_marker
                                    if self.check_win_on_grid(temp_grid, self.tic_tac_toe_grid.player_marker):
                                        if self.tic_tac_toe_grid.place_marker(r, c, self.tic_tac_toe_grid.enemy_marker):
                                            enemy_move_made = True
                                            break
                            if enemy_move_made: break

                    if not enemy_move_made:
                        # Random move
                        available = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if self.tic_tac_toe_grid.grid[r][c] is None]
                        if available:
                            r, c = random.choice(available)
                            if self.tic_tac_toe_grid.place_marker(r, c, self.tic_tac_toe_grid.enemy_marker):
                                enemy_move_made = True

                    if enemy_move_made:
                        self.tic_tac_toe_grid.player_turn = True
                        if self.tic_tac_toe_grid.check_win(self.tic_tac_toe_grid.enemy_marker):
                            self.game_state = GAME_OVER
                        elif self.tic_tac_toe_grid.is_full():
                            self.game_state = GAME_OVER # Draw

        # Power-up collection
        self.powerups.update() # For any sprite animations or logic
        hit_powerups = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for powerup in hit_powerups:
            self.player.collect_powerup(powerup.type)
            self.update_objectives(f"{powerup.type}_collected")


        self.tic_tac_toe_grid.update_blocker_beam()

        # Time Limit
        self.time_remaining -= 1 / FPS
        if self.time_remaining <= 0:
            self.game_state = GAME_OVER # Time's up

        self.check_level_completion()

        # Drawing
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        self.tic_tac_toe_grid.draw(self.screen)

        # UI Elements
        score_text = self.font.render(f"Score: {self.player.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        tokens_text = self.font.render(f"Tokens: {self.player.tokens}", True, WHITE)
        self.screen.blit(tokens_text, (10, 50))

        time_text = self.font.render(f"Time: {int(self.time_remaining)}", True, WHITE)
        self.screen.blit(time_text, (SCREEN_WIDTH - time_text.get_width() - 10, 10))

        # Display abilities and their counts
        ability_y = 10
        for name, data in self.player.abilities.items():
            text = self.small_font.render(f"{name} ({data['count']}) - Cost: {data['cost']}", True, WHITE)
            self.screen.blit(text, (10, ability_y))
            ability_y += 25

        # Display objectives
        obj_x = SCREEN_WIDTH - 200
        obj_y = 10
        obj_title = self.small_font.render("Objectives:", True, WHITE)
        self.screen.blit(obj_title, (obj_x, obj_y))
        obj_y += 25

        for obj in self.level_data["objectives"]:
            target = obj["target"]
            current = self.current_objective_count.get(target, 0)
            required = obj["count"]
            text_str = f"{target.replace('_', ' ').title()}: {current}/{required}"
            color = WHITE
            if current < required:
                color = YELLOW

            obj_text = self.small_font.render(text_str, True, color)
            self.screen.blit(obj_text, (obj_x, obj_y))
            obj_y += 25


    def handle_game_over(self):
        self.screen.fill(BLACK)
        game_over_text = self.font.render("Game Over!", True, RED)
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))

        restart_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50)
        pygame.draw.rect(self.screen, BLUE, restart_button_rect)
        restart_text = self.font.render("Restart", True, WHITE)
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 65))

        menu_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 120, 200, 50)
        pygame.draw.rect(self.screen, BLUE, menu_button_rect)
        menu_text = self.font.render("Main Menu", True, WHITE)
        self.screen.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2, SCREEN_HEIGHT // 2 + 135))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button_rect.collidepoint(event.pos):
                    self.load_level(self.level_data)
                    self.game_state = PLAYING
                if menu_button_rect.collidepoint(event.pos):
                    self.game_state = MENU

    def handle_win_screen(self):
        self.screen.fill(BLACK)
        win_text = self.font.render("Victory!", True, GREEN)
        self.screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))

        next_level_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50)
        pygame.draw.rect(self.screen, BLUE, next_level_button_rect)
        next_level_text = self.font.render("Next Level", True, WHITE)
        self.screen.blit(next_level_text, (SCREEN_WIDTH // 2 - next_level_text.get_width() // 2, SCREEN_HEIGHT // 2 + 65))

        menu_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 120, 200, 50)
        pygame.draw.rect(self.screen, BLUE, menu_button_rect)
        menu_text = self.font.render("Main Menu", True, WHITE)
        self.screen.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2, SCREEN_HEIGHT // 2 + 135))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if next_level_button_rect.collidepoint(event.pos):
                    # TODO: Implement loading next level
                    print("Loading next level...")
                    self.game_state = MENU # For now, return to menu
                if menu_button_rect.collidepoint(event.pos):
                    self.game_state = MENU

    def use_ability(self, ability_name):
        if self.player.use_ability(ability_name):
            if ability_name == "Teleport Marker":
                # Simple implementation: find two of player's markers and swap them
                player_markers = []
                for r in range(GRID_SIZE):
                    for c in range(GRID_SIZE):
                        if self.tic_tac_toe_grid.grid[r][c] == self.tic_tac_toe_grid.player_marker:
                            player_markers.append((r, c))
                if len(player_markers) >= 2:
                    pos1 = random.choice(player_markers)
                    player_markers.remove(pos1)
                    pos2 = random.choice(player_markers)
                    self.tic_tac_toe_grid.grid[pos1[0]][pos1[1]] = self.tic_tac_toe_grid.enemy_marker
                    self.tic_tac_toe_grid.grid[pos2[0]][pos2[1]] = self.tic_tac_toe_grid.player_marker
                    self.tic_tac_toe_grid.available_cells = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if self.tic_tac_toe_grid.grid[r][c] is None]
            elif ability_name == "Blocker Beam":
                # Prompt player to select a cell to block
                def select_block_cell():
                    self.screen.fill(BLACK)
                    prompt_text = self.font.render("Select a cell to block for one turn:", True, WHITE)
                    self.screen.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, 50))
                    self.tic_tac_toe_grid.draw(self.screen)
                    pygame.display.flip()

                    while True:
                        for event in pygame.event.get():
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                row, col = self.tic_tac_toe_grid.get_cell_from_mouse(event.pos)
                                if row is not None and col is not None:
                                    if self.tic_tac_toe_grid.grid[row][col] is None:
                                        self.tic_tac_toe_grid.blocker_beam_active = True
                                        self.tic_tac_toe_grid.blocker_beam_pos = (row, col)
                                        self.tic_tac_toe_grid.blocker_beam_timer = 1 * FPS # 1 second
                                        return True
                                    else:
                                        print("Cannot block occupied cell.")
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_ESCAPE:
                                    return False # Cancelled
                        self.clock.tick(FPS)
                select_block_cell()

            elif ability_name == "Double Mark":
                if self.tic_tac_toe_grid.player_turn: # Can only use if it's player's turn
                    row, col = self.select_placement_cell("Choose first cell to place double marker:")
                    if row is not None and col is not None:
                        if self.tic_tac_toe_grid.place_marker(row, col, self.tic_tac_toe_grid.player_marker):
                            row2, col2 = self.select_placement_cell("Choose second cell to place double marker:")
                            if row2 is not None and col2 is not None:
                                if self.tic_tac_toe_grid.place_marker(row2, col2, self.tic_tac_toe_grid.player_marker):
                                    if self.tic_tac_toe_grid.check_win(self.tic_tac_toe_grid.player_marker):
                                        self.game_state = WIN_SCREEN
                                    elif self.tic_tac_toe_grid.is_full():
                                        self.game_state = GAME_OVER
                                else:
                                    # If second placement failed, revert first
                                    self.tic_tac_toe_grid.grid[row][col] = None
                                    self.tic_tac_toe_grid.available_cells.append((row, col))
                                    self.tic_tac_toe_grid.available_cells.sort() # Maintain order
                            else:
                                # If second placement cancelled, revert first
                                self.tic_tac_toe_grid.grid[row][col] = None
                                self.tic_tac_toe_grid.available_cells.append((row, col))
                                self.tic_tac_toe_grid.available_cells.sort()
                        self.tic_tac_toe_grid.player_turn = False # End turn after double mark
                        return # Double mark handled, exit function
                    else:
                        # If first placement cancelled, don't use ability
                        self.player.abilities[ability_name]["count"] += 1 # Refund cost
                        self.player.tokens += self.player.abilities[ability_name]["cost"]
                        return

    def use_powerup(self, powerup_name):
        if powerup_name == "Grid Shift":
            if self.player.tokens >= GRID_SHIFT_COST:
                self.player.tokens -= GRID_SHIFT_COST
                self.tic_tac_toe_grid.shuffle_grid()
                print("Used Grid Shift")
        elif powerup_name == "Marker Erase":
            if self.player.tokens >= MARKER_ERASE_COST:
                self.player.tokens -= MARKER_ERASE_COST
                # Prompt player to select an opponent marker to erase
                def select_erase_cell():
                    self.screen.fill(BLACK)
                    prompt_text = self.font.render("Select an opponent marker to erase:", True, WHITE)
                    self.screen.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, 50))
                    self.tic_tac_toe_grid.draw(self.screen)
                    pygame.display.flip()

                    while True:
                        for event in pygame.event.get():
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                row, col = self.tic_tac_toe_grid.get_cell_from_mouse(event.pos)
                                if row is not None and col is not None:
                                    if self.tic_tac_toe_grid.grid[row][col] == self.tic_tac_toe_grid.enemy_marker:
                                        self.tic_tac_toe_grid.grid[row][col] = None
                                        self.tic_tac_toe_grid.available_cells.append((row, col))
                                        self.tic_tac_toe_grid.available_cells.sort()
                                        print("Used Marker Erase")
                                        return True
                                    else:
                                        print("Not an opponent marker.")
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_ESCAPE:
                                    return False # Cancelled
                        self.clock.tick(FPS)
                select_erase_cell()

    def select_placement_cell(self, prompt_message):
        """Helper function to prompt the player to select a cell for placement."""
        self.screen.fill(BLACK)
        prompt_text = self.font.render(prompt_message, True, WHITE)
        self.screen.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, 50))
        self.tic_tac_toe_grid.draw(self.screen)
        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    row, col = self.tic_tac_toe_grid.get_cell_from_mouse(event.pos)
                    if row is not None and col is not None:
                        if self.tic_tac_toe_grid.grid[row][col] is None:
                            return row, col
                        else:
                            print("Cell is already occupied.")
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None, None # Cancelled
            self.clock.tick(FPS)

    def check_win_on_grid(self, grid_state, marker):
        """Checks for win condition on a given grid state."""
        for r in range(GRID_SIZE):
            if all(grid_state[r][c] == marker for c in range(GRID_SIZE)):
                return True
        for c in range(GRID_SIZE):
            if all(grid_state[r][c] == marker for r in range(GRID_SIZE)):
                return True
        if all(grid_state[i][i] == marker for i in range(GRID_SIZE)):
            return True
        if all(grid_state[i][GRID_SIZE - 1 - i] == marker for i in range(GRID_SIZE)):
            return True
        return False

    def update_objectives(self, event_type):
        for obj in self.level_data["objectives"]:
            if obj["type"] == "defeat" and obj["target"] == "enemies":
                if event_type.startswith("enemy_defeated_"):
                    self.current_objective_count[obj["target"]] += 1
            elif obj["type"] == "win_round" and obj["target"] == "tic_tac_toe":
                if event_type == "tic_tac_toe_win":
                    self.current_objective_count[obj["target"]] += 1
            elif obj["type"] == "collect" and obj["target"] in event_type:
                 self.current_objective_count[obj["target"]] = min(self.current_objective_count.get(obj["target"], 0) + 1, obj["count"])


    def check_level_completion(self):
        all_objectives_met = True
        for obj in self.level_data["objectives"]:
            target = obj["target"]
            required = obj["count"]
            current = self.current_objective_count.get(target, 0)
            if current < required:
                all_objectives_met = False
                break

        if all_objectives_met:
            # Award score and potentially unlock next level/abilities
            print("Level Objectives Met!")
            self.player.score += 100 # Example score
            self.game_state = WIN_SCREEN


    def run(self):
        running = True
        while running:
            if self.game_state == MENU:
                self.handle_menu()
            elif self.game_state == PLAYING:
                self.handle_playing()
            elif self.game_state == GAME_OVER:
                self.handle_game_over()
            elif self.game_state == WIN_SCREEN:
                self.handle_win_screen()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
