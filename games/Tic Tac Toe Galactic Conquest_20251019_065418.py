
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
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
LIGHT_BLUE = (100, 100, 200)

# Player
PLAYER_SPEED = 5
PLAYER_SIZE = 20

# Tic Tac Toe
GRID_SIZE = 3
CELL_SIZE = 100
TIC_TAC_TOE_WIDTH = GRID_SIZE * CELL_SIZE
TIC_TAC_TOE_HEIGHT = GRID_SIZE * CELL_SIZE
MARK_THICKNESS = 10
X_COLOR = RED
O_COLOR = BLUE

# Star Map
PLANET_SIZE = 30
CONNECTION_COLOR = LIGHT_BLUE
CONNECTION_THICKNESS = 2

# Enemies
ENEMY_SIZE = 15
ENEMY_SPEED = 2
TURRET_RANGE = 150
TURRET_FIRE_RATE = 60 # frames per shot

# Powerups
POWERUP_SIZE = 15

# Game States
STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2
STATE_TIC_TAC_TOE = 3

# --- Game Classes ---

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.score = 0
        self.wins = 0
        self.powerups = {"shield": 0, "quantum_shift": 0}
        self.current_health = 100 # For potential future combat on star map
        self.max_health = 100

    def move(self, dx, dy):
        self.rect.x += dx * PLAYER_SPEED
        self.rect.y += dy * PLAYER_SPEED

        # Keep player on screen
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)

    def use_powerup(self, powerup_type, tic_tac_toe_grid=None, current_player_mark=None):
        if powerup_type == "shield" and self.powerups["shield"] > 0:
            print("Shield activated!")
            self.powerups["shield"] -= 1
            return "shielded"
        if powerup_type == "quantum_shift" and self.powerups["quantum_shift"] > 0:
            print("Quantum Shift ready! Click on two of your marks to swap.")
            self.powerups["quantum_shift"] -= 1
            return "quantum_shift_ready"
        return None

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type, patrol_path=[]):
        super().__init__()
        self.enemy_type = enemy_type
        self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.patrol_path = patrol_path
        self.current_waypoint = 0
        self.speed = ENEMY_SPEED
        self.attack_range = 0
        self.shoot_timer = 0
        self.target = None

        if enemy_type == "basic_pirate":
            self.image.fill(RED)
            self.speed = ENEMY_SPEED
        elif enemy_type == "turret":
            self.image.fill(GRAY)
            self.image = pygame.Surface((ENEMY_SIZE * 2, ENEMY_SIZE * 2))
            self.rect = self.image.get_rect(center=(x, y))
            self.attack_range = TURRET_RANGE
            self.speed = 0
        else:
            self.image.fill(YELLOW)

    def update(self, player_rect, all_sprites):
        if self.enemy_type == "basic_pirate":
            if self.patrol_path:
                target_pos = self.patrol_path[self.current_waypoint]
                dx = target_pos[0] - self.rect.centerx
                dy = target_pos[1] - self.rect.centery
                dist = math.hypot(dx, dy)

                if dist < self.speed:
                    self.rect.center = target_pos
                    self.current_waypoint = (self.current_waypoint + 1) % len(self.patrol_path)
                else:
                    self.rect.centerx += (dx / dist) * self.speed
                    self.rect.centery += (dy / dist) * self.speed
            else:
                # Basic chase behavior if no patrol path
                dx = player_rect.centerx - self.rect.centerx
                dy = player_rect.centery - self.rect.centery
                dist = math.hypot(dx, dy)
                if dist > 0:
                    self.rect.centerx += (dx / dist) * self.speed
                    self.rect.centery += (dy / dist) * self.speed

        elif self.enemy_type == "turret":
            self.shoot_timer += 1
            if self.shoot_timer >= TURRET_FIRE_RATE:
                # Check if player is in range
                dx = player_rect.centerx - self.rect.centerx
                dy = player_rect.centery - self.rect.centery
                dist = math.hypot(dx, dy)
                if dist < self.attack_range:
                    self.target = player_rect
                    self.shoot_timer = 0
                    # Return a bullet instance (or handle bullet creation in main loop)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        if self.enemy_type == "turret":
            pygame.draw.circle(surface, RED, self.rect.center, self.attack_range, 1)


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, obstacle_type):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.obstacle_type = obstacle_type

        if obstacle_type == "asteroid_field":
            self.image.fill(DARK_GRAY)
        elif obstacle_type == "derelict_ship":
            self.image.fill(GRAY)
        else:
            self.image.fill(YELLOW)

class Powerup(pygame.sprite.Sprite):
    def __init__(self, x, y, powerup_type):
        super().__init__()
        self.image = pygame.Surface((POWERUP_SIZE, POWERUP_SIZE))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.powerup_type = powerup_type

        if powerup_type == "shield_boost":
            self.image.fill(BLUE)
        elif powerup_type == "ammo_refill": # Placeholder for future use
            self.image.fill(YELLOW)
        elif powerup_type == "quantum_shift":
            self.image.fill(YELLOW)
        else:
            self.image.fill(GREEN)

class Planet:
    def __init__(self, x, y, name, size=PLANET_SIZE):
        self.x = x
        self.y = y
        self.name = name
        self.size = size
        self.faction = None # "player" or "enemy"
        self.tic_tac_toe_grid = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.tic_tac_toe_turn = 'X' # 'X' for player, 'O' for enemy
        self.tic_tac_toe_ai_difficulty = "easy"
        self.last_winner = None
        self.owner_mark = ''

    def draw(self, surface):
        color = WHITE
        if self.faction == "player":
            color = GREEN
        elif self.faction == "enemy":
            color = RED

        pygame.draw.circle(surface, color, (self.x, self.y), self.size)
        font = pygame.font.Font(None, 24)
        text = font.render(self.name, True, BLACK)
        text_rect = text.get_rect(center=(self.x, self.y))
        surface.blit(text, text_rect)

    def reset_tic_tac_toe(self):
        self.tic_tac_toe_grid = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.tic_tac_toe_turn = 'X'
        self.last_winner = None
        self.owner_mark = ''

    def check_tic_tac_toe_win(self):
        lines = []
        # Rows
        for row in self.tic_tac_toe_grid:
            lines.append(row)
        # Columns
        for col in range(GRID_SIZE):
            lines.append([self.tic_tac_toe_grid[row][col] for row in range(GRID_SIZE)])
        # Diagonals
        lines.append([self.tic_tac_toe_grid[i][i] for i in range(GRID_SIZE)])
        lines.append([self.tic_tac_toe_grid[i][GRID_SIZE - 1 - i] for i in range(GRID_SIZE)])

        for line in lines:
            if line[0] != '' and line[0] == line[1] == line[2]:
                return line[0] # Return winner ('X' or 'O')
        # Check for draw
        if all(cell != '' for row in self.tic_tac_toe_grid for cell in row):
            return "draw"
        return None

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tic Tac Toe: Galactic Conquest")
        self.clock = pygame.time.Clock()
        self.current_state = STATE_MENU
        self.font = pygame.font.Font(None, 50)
        self.small_font = pygame.font.Font(None, 30)

        self.player = None
        self.enemies = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()

        self.planets = []
        self.star_map_connections = []
        self.current_planet = None
        self.player_planet_target = None # For moving between planets

        self.tic_tac_toe_current_grid = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.tic_tac_toe_turn = 'X'
        self.tic_tac_toe_winner = None
        self.tic_tac_toe_ai_difficulty = "easy"
        self.tic_tac_toe_player_mark = 'X'
        self.tic_tac_toe_enemy_mark = 'O'
        self.current_tic_tac_toe_game_planet = None
        self.shielded_turn = False
        self.quantum_shift_active = False
        self.quantum_shift_selection = []

        self.level_data = {
            1: {
                "name": "Proxima Centauri Outpost",
                "size": {"width": SCREEN_WIDTH, "height": SCREEN_HEIGHT},
                "spawn_points": [{"x": 100, "y": 100, "type": "player"}, {"x": 400, "y": 300, "type": "enemy"}],
                "obstacles": [{"x": 250, "y": 150, "width": 70, "height": 70, "type": "asteroid_field"}, {"x": 550, "y": 200, "width": 40, "height": 40, "type": "derelict_ship"}, {"x": 180, "y": 450, "width": 50, "height": 50, "type": "asteroid_field"}],
                "powerups": [{"x": 300, "y": 500, "type": "shield_boost"}, {"x": 650, "y": 100, "type": "quantum_shift"}],
                "enemies": [{"x": 350, "y": 250, "type": "basic_pirate", "patrol_path": [[350, 250], [400, 250], [400, 300], [350, 300]]}, {"x": 150, "y": 450, "type": "basic_pirate", "patrol_path": [[150, 450], [200, 450]]}, {"x": 600, "y": 400, "type": "turret", "patrol_path": []}],
                "objectives": [{"type": "defeat", "target": "basic_pirate", "count": 2}, {"type": "destroy", "target": "turret", "count": 1}],
                "difficulty": "easy",
                "time_limit": 180
            }
        }
        self.current_level = 1
        self.level_objectives = {}
        self.objectives_completed = {}
        self.time_left = 0

        self.init_menu()

    def init_menu(self):
        self.planets = []
        self.enemies.empty()
        self.obstacles.empty()
        self.powerups.empty()
        self.all_sprites.empty()
        self.player = None
        self.star_map_connections = []
        self.current_planet = None
        self.current_level = 1
        self.level_objectives = {}
        self.objectives_completed = {}

        self.screen.fill(BLACK)
        title_text = self.font.render("Tic Tac Toe: Galactic Conquest", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(title_text, title_rect)

        start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50)
        pygame.draw.rect(self.screen, BLUE, start_button_rect)
        start_text = self.small_font.render("Start Game", True, WHITE)
        start_text_rect = start_text.get_rect(center=start_button_rect.center)
        self.screen.blit(start_text, start_text_rect)

        quit_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 70, 200, 50)
        pygame.draw.rect(self.screen, RED, quit_button_rect)
        quit_text = self.small_font.render("Quit", True, WHITE)
        quit_text_rect = quit_text.get_rect(center=quit_button_rect.center)
        self.screen.blit(quit_text, quit_text_rect)

        pygame.display.flip()

    def start_level(self, level_num):
        self.current_state = STATE_PLAYING
        self.screen.fill(BLACK)
        self.enemies.empty()
        self.obstacles.empty()
        self.powerups.empty()
        self.all_sprites.empty()
        self.planets = []
        self.star_map_connections = []
        self.current_planet = None
        self.player_planet_target = None

        level_data = self.level_data.get(level_num)
        if not level_data:
            print(f"Level {level_num} not found!")
            self.current_state = STATE_MENU
            return

        self.time_left = level_data.get("time_limit", 180)
        self.level_objectives = {obj["type"]: obj["count"] for obj in level_data.get("objectives", [])}
        self.objectives_completed = {obj["type"]: 0 for obj in level_data.get("objectives", [])}

        # Initialize player
        player_spawn = next((s for s in level_data["spawn_points"] if s["type"] == "player"), None)
        if player_spawn:
            self.player = Player(player_spawn["x"], player_spawn["y"])
            self.all_sprites.add(self.player)
        else:
            print("Player spawn point not found!")
            self.current_state = STATE_MENU
            return

        # Initialize obstacles
        for obs_data in level_data["obstacles"]:
            obstacle = Obstacle(obs_data["x"], obs_data["y"], obs_data["width"], obs_data["height"], obs_data["type"])
            self.obstacles.add(obstacle)
            self.all_sprites.add(obstacle)

        # Initialize powerups
        for pup_data in level_data["powerups"]:
            powerup = Powerup(pup_data["x"], pup_data["y"], pup_data["type"])
            self.powerups.add(powerup)
            self.all_sprites.add(powerup)

        # Initialize enemies
        for enemy_data in level_data["enemies"]:
            enemy = Enemy(enemy_data["x"], enemy_data["y"], enemy_data["type"], enemy_data.get("patrol_path", []))
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

        # Initialize planets (for the star map aspect - not fully implemented in level 1 as a map)
        # For level 1, we'll treat the whole screen as a star map for now, with planets being objectives
        # A true star map would involve a separate screen with interconnected planets
        planet_names = ["Proxima_Centauri_I"] # Example planet names
        planet_pos = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)] # Example planet positions
        for i, name in enumerate(planet_names):
            planet_x, planet_y = planet_pos[i]
            planet = Planet(planet_x, planet_y, name)
            self.planets.append(planet)
            if name == "Proxima_Centauri_I":
                self.current_planet = planet # Set initial planet


        # Setup initial objectives
        for obj_type, count in self.level_objectives.items():
            self.objectives_completed[obj_type] = 0


        pygame.display.flip()

    def handle_menu_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50)
            quit_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 70, 200, 50)

            if start_button_rect.collidepoint(event.pos):
                self.start_level(self.current_level)
            elif quit_button_rect.collidepoint(event.pos):
                pygame.quit()
                sys.exit()

    def handle_playing_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                self.player.move(0, -1)
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                self.player.move(0, 1)
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                self.player.move(-1, 0)
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                self.player.move(1, 0)

            if event.key == pygame.K_p: # Toggle powerup menu or activate
                if self.player.powerups["quantum_shift"] > 0:
                    self.quantum_shift_active = True
                    self.quantum_shift_selection = []
                    print("Quantum Shift active. Select first mark.")

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.quantum_shift_active:
                self.handle_quantum_shift_click(event.pos)
            elif self.current_state == STATE_PLAYING:
                # Check for interactions with planets or objectives if implemented on star map
                pass

    def handle_tic_tac_toe_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.current_tic_tac_toe_game_planet and self.current_tic_tac_toe_game_planet.tic_tac_toe_turn == self.tic_tac_toe_player_mark:
                if self.quantum_shift_active:
                    self.handle_quantum_shift_click(event.pos)
                    return

                mx, my = event.pos
                grid_x = (mx - (SCREEN_WIDTH - TIC_TAC_TOE_WIDTH) // 2) // CELL_SIZE
                grid_y = (my - (SCREEN_HEIGHT - TIC_TAC_TOE_HEIGHT) // 2) // CELL_SIZE

                if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                    if self.current_tic_tac_toe_game_planet.tic_tac_toe_grid[grid_y][grid_x] == '':
                        mark_to_place = self.tic_tac_toe_player_mark
                        shield_applied = False
                        if self.player.powerups["shield"] > 0:
                            shield_applied = True
                            self.player.powerups["shield"] -= 1
                            print("Shield used on this turn!")

                        self.current_tic_tac_toe_game_planet.tic_tac_toe_grid[grid_y][grid_x] = mark_to_place
                        self.current_tic_tac_toe_game_planet.tic_tac_toe_turn = self.tic_tac_toe_enemy_mark
                        self.tic_tac_toe_winner = self.current_tic_tac_toe_game_planet.check_tic_tac_toe_win()

                        if self.tic_tac_toe_winner:
                            self.handle_tic_tac_toe_win(self.tic_tac_tac_toe_winner)
                        else:
                            self.player.score += 1 # Simple score for each move made

            elif self.current_tic_tac_toe_game_planet and self.current_tic_tac_toe_game_planet.tic_tac_toe_turn == self.tic_tac_toe_enemy_mark:
                # AI's turn - will be handled in update
                pass

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q: # Quit Tic Tac Toe
                self.end_tic_tac_toe_game()

    def handle_quantum_shift_click(self, pos):
        mx, my = pos
        grid_x = (mx - (SCREEN_WIDTH - TIC_TAC_TOE_WIDTH) // 2) // CELL_SIZE
        grid_y = (my - (SCREEN_HEIGHT - TIC_TAC_TOE_HEIGHT) // 2) // CELL_SIZE

        if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
            clicked_cell_content = self.current_tic_tac_toe_game_planet.tic_tac_toe_grid[grid_y][grid_x]
            if clicked_cell_content == self.tic_tac_toe_player_mark:
                self.quantum_shift_selection.append((grid_x, grid_y))
                print(f"Selected mark at ({grid_x}, {grid_y})")

                if len(self.quantum_shift_selection) == 2:
                    x1, y1 = self.quantum_shift_selection[0]
                    x2, y2 = self.quantum_shift_selection[1]

                    # Swap the marks
                    self.current_tic_tac_toe_game_planet.tic_tac_toe_grid[y1][x1], self.current_tic_tac_toe_game_planet.tic_tac_toe_grid[y2][x2] = \
                        self.current_tic_tac_toe_game_planet.tic_tac_toe_grid[y2][x2], self.current_tic_tac_toe_game_planet.tic_tac_toe_grid[y1][x1]

                    print("Marks swapped!")
                    self.quantum_shift_active = False
                    self.quantum_shift_selection = []
                    self.tic_tac_toe_winner = self.current_tic_tac_toe_game_planet.check_tic_tac_toe_win()
                    if self.tic_tac_toe_winner:
                        self.handle_tic_tac_toe_win(self.tic_tac_tac_toe_winner)
                    else:
                        self.current_tic_tac_toe_game_planet.tic_tac_toe_turn = self.tic_tac_toe_enemy_mark # Let AI take turn
            else:
                print("Invalid selection. Select your own marks.")
                self.quantum_shift_selection = [] # Reset selection


    def update(self):
        if self.current_state == STATE_PLAYING:
            self.player.update()

            # Enemy updates
            for enemy in self.enemies:
                enemy.update(self.player.rect, self.all_sprites)

            # Collision detection
            # Player with powerups
            powerup_collisions = pygame.sprite.spritecollide(self.player, self.powerups, True)
            for powerup in powerup_collisions:
                if powerup.powerup_type == "shield_boost":
                    self.player.powerups["shield"] += 1
                    print("Shield powerup collected!")
                elif powerup.powerup_type == "quantum_shift":
                    self.player.powerups["quantum_shift"] += 1
                    print("Quantum Shift powerup collected!")

            # Player with enemies (for potential combat, not implemented fully)
            enemy_collisions = pygame.sprite.spritecollide(self.player, self.enemies, False)
            for enemy in enemy_collisions:
                if enemy.enemy_type == "basic_pirate":
                    self.player.current_health -= 10 # Example damage
                    if self.player.current_health <= 0:
                        self.current_state = STATE_GAME_OVER
                elif enemy.enemy_type == "turret":
                    pass # Turrets don't directly collide

            # Enemies with obstacles
            for enemy in self.enemies:
                if pygame.sprite.spritecollideany(enemy, self.obstacles):
                    # Basic push-back or stop behavior
                    pass

            # Check objectives
            self.check_level_objectives()

            # Time limit
            self.time_left -= 1
            if self.time_left <= 0:
                self.current_state = STATE_GAME_OVER

        elif self.current_state == STATE_TIC_TAC_TOE:
            if self.current_tic_tac_toe_game_planet:
                if self.current_tic_tac_toe_game_planet.tic_tac_toe_turn == self.tic_tac_toe_enemy_mark:
                    # AI move
                    if not self.tic_tac_toe_winner: # Only make move if game is ongoing
                        self.make_ai_move()

    def check_level_objectives(self):
        # Example objective checks
        num_basic_pirates_defeated = len(self.enemies) - len([e for e in self.enemies if e.enemy_type == "turret"])
        num_turrets_destroyed = len([e for e in self.enemies if e.enemy_type == "turret"])

        if "defeat" in self.level_objectives and self.level_objectives["defeat"] > 0 and "defeat" in self.objectives_completed:
            self.objectives_completed["defeat"] = min(self.level_objectives["defeat"], num_basic_pirates_defeated)

        if "destroy" in self.level_objectives and self.level_objectives["destroy"] > 0 and "destroy" in self.objectives_completed:
            self.objectives_completed["destroy"] = min(self.level_objectives["destroy"], num_turrets_destroyed)

        # Check for planet claim - this is done when winning Tic Tac Toe on the planet
        if self.current_planet and self.current_planet.faction == "player":
            if "claim_planet" in self.level_objectives and self.level_objectives["claim_planet"] > 0 and "claim_planet" in self.objectives_completed:
                self.objectives_completed["claim_planet"] = 1

        all_objectives_met = True
        for obj_type, required_count in self.level_objectives.items():
            if obj_type not in self.objectives_completed or self.objectives_completed[obj_type] < required_count:
                all_objectives_met = False
                break

        if all_objectives_met:
            print("All objectives met!")
            self.player.score += 100 # Bonus score for completing level objectives
            self.current_state = STATE_GAME_OVER # Or transition to next level/menu
            self.init_game_over_screen("Level Complete!")


    def make_ai_move(self):
        planet = self.current_tic_tac_toe_game_planet
        difficulty = planet.tic_tac_toe_ai_difficulty

        if difficulty == "easy":
            # Simple random move
            available_cells = []
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    if planet.tic_tac_toe_grid[r][c] == '':
                        available_cells.append((r, c))
            if available_cells:
                r, c = random.choice(available_cells)
                planet.tic_tac_toe_grid[r][c] = self.tic_tac_toe_enemy_mark
                planet.tic_tac_toe_turn = self.tic_tac_toe_player_mark
                self.tic_tac_toe_winner = planet.check_tic_tac_toe_win()
                if self.tic_tac_tac_toe_winner:
                    self.handle_tic_tac_toe_win(self.tic_tac_toe_winner)

        elif difficulty == "medium":
            # Prioritize winning, then blocking, then random
            move = self.get_medium_ai_move(planet)
            if move:
                r, c = move
                planet.tic_tac_toe_grid[r][c] = self.tic_tac_toe_enemy_mark
                planet.tic_tac_toe_turn = self.tic_tac_tac_toe_player_mark
                self.tic_tac_toe_winner = planet.check_tic_tac_toe_win()
                if self.tic_tac_tac_toe_winner:
                    self.handle_tic_tac_toe_win(self.tic_tac_tac_toe_winner)

        elif difficulty == "hard":
            # Minimax algorithm
            move = self.minimax(planet.tic_tac_toe_grid, True, self.tic_tac_toe_enemy_mark, self.tic_tac_tac_toe_player_mark)
            if move:
                r, c = move
                planet.tic_tac_toe_grid[r][c] = self.tic_tac_tac_toe_enemy_mark
                planet.tic_tac_toe_turn = self.tic_tac_tac_toe_player_mark
                self.tic_tac_tac_toe_winner = planet.check_tic_tac_toe_win()
                if self.tic_tac_tac_toe_winner:
                    self.handle_tic_tac_toe_win(self.tic_tac_tac_toe_winner)

    def get_medium_ai_move(self, planet):
        # Check for winning move
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if planet.tic_tac_toe_grid[r][c] == '':
                    temp_grid = [row[:] for row in planet.tic_tac_toe_grid]
                    temp_grid[r][c] = self.tic_tac_toe_enemy_mark
                    if self.check_line_win(temp_grid, self.tic_tac_tac_toe_enemy_mark):
                        return (r, c)

        # Check for blocking move
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if planet.tic_tac_toe_grid[r][c] == '':
                    temp_grid = [row[:] for row in planet.tic_tac_toe_grid]
                    temp_grid[r][c] = self.tic_tac_tac_toe_player_mark
                    if self.check_line_win(temp_grid, self.tic_tac_tac_toe_player_mark):
                        return (r, c)

        # Random move
        available_cells = []
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if planet.tic_tac_toe_grid[r][c] == '':
                    available_cells.append((r, c))
        if available_cells:
            return random.choice(available_cells)
        return None

    def check_line_win(self, grid, mark):
        lines = []
        # Rows
        for row in grid:
            lines.append(row)
        # Columns
        for col in range(GRID_SIZE):
            lines.append([grid[row][col] for row in range(GRID_SIZE)])
        # Diagonals
        lines.append([grid[i][i] for i in range(GRID_SIZE)])
        lines.append([grid[i][GRID_SIZE - 1 - i] for i in range(GRID_SIZE)])

        for line in lines:
            if line[0] == mark and line[0] == line[1] == line[2]:
                return True
        return False

    def minimax(self, board, is_maximizing_player, ai_mark, player_mark):
        result = self.evaluate_board(board, ai_mark, player_mark)
        if result != 0:
            return result

        if not any('' in row for row in board): # Draw
            return 0

        if is_maximizing_player:
            best_score = -math.inf
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    if board[r][c] == '':
                        board[r][c] = ai_mark
                        score = self.minimax(board, False, ai_mark, player_mark)
                        board[r][c] = '' # Undo move
                        best_score = max(best_score, score)
            return best_score
        else:
            best_score = math.inf
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    if board[r][c] == '':
                        board[r][c] = player_mark
                        score = self.minimax(board, True, ai_mark, player_mark)
                        board[r][c] = '' # Undo move
                        best_score = min(best_score, score)
            return best_score

    def evaluate_board(self, board, ai_mark, player_mark):
        # Check rows, columns, diagonals for win/loss
        lines = []
        for r in range(GRID_SIZE):
            lines.append(board[r])
        for c in range(GRID_SIZE):
            lines.append([board[r][c] for r in range(GRID_SIZE)])
        lines.append([board[i][i] for i in range(GRID_SIZE)])
        lines.append([board[i][GRID_SIZE - 1 - i] for i in range(GRID_SIZE)])

        for line in lines:
            if all(cell == ai_mark for cell in line):
                return 10
            if all(cell == player_mark for cell in line):
                return -10

        if not any('' in row for row in board): # Draw
            return 0
        return 0 # Game not over

    def get_best_move_minimax(self, board, ai_mark, player_mark):
        best_score = -math.inf
        best_move = None
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if board[r][c] == '':
                    board[r][c] = ai_mark
                    score = self.minimax(board, False, ai_mark, player_mark)
                    board[r][c] = '' # Undo move
                    if score > best_score:
                        best_score = score
                        best_move = (r, c)
        return best_move


    def handle_tic_tac_toe_win(self, winner):
        planet = self.current_tic_tac_toe_game_planet
        if winner == self.tic_tac_tac_toe_player_mark:
            planet.faction = "player"
            planet.owner_mark = self.tic_tac_tac_toe_player_mark
            self.player.wins += 1
            self.player.score += 50 # Bonus for winning a tic tac toe match
            print("Player wins Tic Tac Toe!")
        elif winner == self.tic_tac_tac_toe_enemy_mark:
            planet.faction = "enemy"
            planet.owner_mark = self.tic_tac_tac_toe_enemy_mark
            print("Enemy wins Tic Tac Toe!")
        else: # Draw
            print("Tic Tac Toe draw!")

        self.tic_tac_winner = winner
        self.current_planet = planet # Update current planet after win/loss
        self.end_tic_tac_toe_game(delay=1500) # Delay to show result

    def end_tic_tac_toe_game(self, delay=0):
        if delay > 0:
            pygame.time.wait(delay)
        self.current_state = STATE_PLAYING
        self.current_tic_tac_toe_game_planet = None
        self.tic_tac_toe_winner = None
        self.quantum_shift_active = False
        self.quantum_shift_selection = []

    def draw_star_map(self):
        self.screen.fill(BLACK)

        # Draw connections
        for p1, p2 in self.star_map_connections:
            pygame.draw.line(self.screen, CONNECTION_COLOR, (p1.x, p1.y), (p2.x, p2.y), CONNECTION_THICKNESS)

        # Draw planets
        for planet in self.planets:
            planet.draw(self.screen)

        # Draw player on the star map
        if self.player:
            pygame.draw.circle(self.screen, GREEN, self.player.rect.center, PLAYER_SIZE // 2)

        # Draw UI elements
        self.draw_ui()

        # Draw objectives status
        self.draw_objectives_status()

    def draw_ui(self):
        score_text = self.small_font.render(f"Score: {self.player.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        wins_text = self.small_font.render(f"Wins: {self.player.wins}", True, WHITE)
        self.screen.blit(wins_text, (10, 40))

        powerup_text = self.small_font.render(f"Shield: {self.player.powerups['shield']} | QS: {self.player.powerups['quantum_shift']}", True, WHITE)
        self.screen.blit(powerup_text, (10, 70))

        time_text = self.small_font.render(f"Time: {self.time_left}", True, WHITE)
        self.screen.blit(time_text, (SCREEN_WIDTH - time_text.get_width() - 10, 10))

    def draw_objectives_status(self):
        obj_y_offset = 10
        for obj_type, required_count in self.level_objectives.items():
            current_count = self.objectives_completed.get(obj_type, 0)
            status_text = f"{obj_type.replace('_', ' ').title()}: {current_count}/{required_count}"
            text_surface = self.small_font.render(status_text, True, WHITE)
            self.screen.blit(text_surface, (SCREEN_WIDTH - text_surface.get_width() - 10, 40 + obj_y_offset))
            obj_y_offset += 30


    def draw_tic_tac_toe_grid(self):
        self.screen.fill(BLACK) # Clear screen for Tic Tac Toe

        # Draw the Tic Tac Toe grid background
        grid_x_start = (SCREEN_WIDTH - TIC_TAC_TOE_WIDTH) // 2
        grid_y_start = (SCREEN_HEIGHT - TIC_TAC_TOE_HEIGHT) // 2

        for r in range(GRID_SIZE + 1):
            pygame.draw.line(self.screen, WHITE, (grid_x_start + r * CELL_SIZE, grid_y_start), (grid_x_start + r * CELL_SIZE, grid_y_start + TIC_TAC_TOE_HEIGHT), MARK_THICKNESS // 2)
            pygame.draw.line(self.screen, WHITE, (grid_x_start, grid_y_start + r * CELL_SIZE), (grid_x_start + TIC_TAC_TOE_WIDTH, grid_y_start + r * CELL_SIZE), MARK_THICKNESS // 2)

        # Draw the marks
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                cell_center_x = grid_x_start + c * CELL_SIZE + CELL_SIZE // 2
                cell_center_y = grid_y_start + r * CELL_SIZE + CELL_SIZE // 2
                mark = self.current_tic_tac_toe_game_planet.tic_tac_toe_grid[r][c]

                if mark == 'X':
                    pygame.draw.line(self.screen, X_COLOR, (cell_center_x - CELL_SIZE // 3, cell_center_y - CELL_SIZE // 3), (cell_center_x + CELL_SIZE // 3, cell_center_y + CELL_SIZE // 3), MARK_THICKNESS)
                    pygame.draw.line(self.screen, X_COLOR, (cell_center_x + CELL_SIZE // 3, cell_center_y - CELL_SIZE // 3), (cell_center_x - CELL_SIZE // 3, cell_center_y + CELL_SIZE // 3), MARK_THICKNESS)
                elif mark == 'O':
                    pygame.draw.circle(self.screen, O_COLOR, (cell_center_x, cell_center_y), CELL_SIZE // 3, MARK_THICKNESS)

        # Draw turn indicator
        turn_text = self.font.render(f"Turn: {self.current_tic_tac_toe_game_planet.tic_tac_toe_turn}", True, WHITE)
        self.screen.blit(turn_text, (20, 20))

        if self.quantum_shift_active:
            qs_text = self.small_font.render("Quantum Shift: Selecting marks...", True, YELLOW)
            self.screen.blit(qs_text, (20, SCREEN_HEIGHT - 50))

        # Draw winner if game over
        if self.tic_tac_toe_winner:
            if self.tic_tac_tac_toe_winner == "draw":
                winner_text = self.font.render("Draw!", True, WHITE)
            else:
                winner_text = self.font.render(f"{self.tic_tac_tac_toe_winner} Wins!", True, (X_COLOR if self.tic_tac_tac_toe_winner == 'X' else O_COLOR))
            winner_rect = winner_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            self.screen.blit(winner_text, winner_rect)

    def init_game_over_screen(self, message="Game Over"):
        self.current_state = STATE_GAME_OVER
        self.screen.fill(BLACK)
        game_over_text = self.font.render(message, True, WHITE)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(game_over_text, game_over_rect)

        score_text = self.small_font.render(f"Final Score: {self.player.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)

        restart_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 70, 200, 50)
        pygame.draw.rect(self.screen, BLUE, restart_button_rect)
        restart_text = self.small_font.render("Restart", True, WHITE)
        restart_text_rect = restart_text.get_rect(center=restart_button_rect.center)
        self.screen.blit(restart_text, restart_text_rect)

        menu_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 140, 200, 50)
        pygame.draw.rect(self.screen, GRAY, menu_button_rect)
        menu_text = self.small_font.render("Main Menu", True, WHITE)
        menu_text_rect = menu_text.get_rect(center=menu_button_rect.center)
        self.screen.blit(menu_text, menu_text_rect)

        pygame.display.flip()

    def handle_game_over_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            restart_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 70, 200, 50)
            menu_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 140, 200, 50)

            if restart_button_rect.collidepoint(event.pos):
                self.init_menu() # Go back to menu to restart
            elif menu_button_rect.collidepoint(event.pos):
                self.init_menu()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if self.current_state == STATE_MENU:
                    self.handle_menu_input(event)
                elif self.current_state == STATE_PLAYING:
                    self.handle_playing_input(event)
                elif self.current_state == STATE_TIC_TAC_TOE:
                    self.handle_tic_tac_toe_input(event)
                elif self.current_state == STATE_GAME_OVER:
                    self.handle_game_over_input(event)

            if self.current_state == STATE_PLAYING:
                self.update()
                self.draw_star_map()
                self.check_for_tic_tac_toe_encounters()

            elif self.current_state == STATE_TIC_TAC_TOE:
                self.update()
                self.draw_tic_tac_toe_grid()
            elif self.current_state == STATE_GAME_OVER:
                pass # Screen is already drawn and waits for input

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def check_for_tic_tac_toe_encounters(self):
        if self.current_planet:
            # Simple encounter logic: if player is on a planet, initiate Tic Tac Toe
            # In a real star map, this would be based on proximity to other planets or enemy ships
            if self.current_planet.faction is None: # If planet is neutral
                self.init_tic_tac_toe_game(self.current_planet)

    def init_tic_tac_toe_game(self, planet):
        self.current_state = STATE_TIC_TAC_TOE
        self.current_tic_tac_toe_game_planet = planet
        planet.reset_tic_tac_toe()

        # Determine who plays 'X' and 'O' and difficulty
        # For now, player is always 'X' and enemy is 'O'
        self.tic_tac_tac_toe_player_mark = 'X'
        self.tic_tac_tac_toe_enemy_mark = 'O'
        planet.tic_tac_toe_turn = 'X'
        planet.tic_tac_tac_toe_ai_difficulty = "easy" # Can be changed based on planet or level

        # Assign AI difficulty based on planet or level progression
        if self.current_level == 1:
            planet.tic_tac_tac_toe_ai_difficulty = "easy"
        elif self.current_level == 2: # Example for future levels
            planet.tic_tac_tac_toe_ai_difficulty = "medium"
        else:
            planet.tic_tac_tac_toe_ai_difficulty = "hard"

        print(f"Starting Tic Tac Toe on {planet.name} (AI: {planet.tic_tac_tac_toe_ai_difficulty})")


def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
