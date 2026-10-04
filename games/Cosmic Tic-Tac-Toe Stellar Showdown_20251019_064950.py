
import pygame
import sys
import random
import math

# Game Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 3
CELL_SIZE = 150
GRID_OFFSET_X = (WIDTH - GRID_SIZE * CELL_SIZE) // 2
GRID_OFFSET_Y = (HEIGHT - GRID_SIZE * CELL_SIZE) // 2

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)

# Game States
MENU = 0
PLAYING = 1
GAME_OVER = 2

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5
        self.symbol = 'X'  # Default symbol
        self.powerups = {'cosmic_shield': 0}

    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

        # Keep player within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def set_symbol(self, symbol):
        self.symbol = symbol
        if symbol == 'X':
            self.image.fill(RED)
        elif symbol == 'O':
            self.image.fill(GREEN)

class Grid:
    def __init__(self):
        self.board = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.symbols = {} # Stores sprites for placed symbols

    def get_cell_coords(self, row, col):
        x = GRID_OFFSET_X + col * CELL_SIZE + CELL_SIZE // 2
        y = GRID_OFFSET_Y + row * CELL_SIZE + CELL_SIZE // 2
        return x, y

    def is_valid_move(self, row, col):
        return 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE and self.board[row][col] == ''

    def place_symbol(self, row, col, symbol, symbol_sprite):
        if self.is_valid_move(row, col):
            self.board[row][col] = symbol
            self.symbols[(row, col)] = symbol_sprite
            return True
        return False

    def reset(self):
        self.board = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        for sprite in self.symbols.values():
            sprite.kill()
        self.symbols = {}

    def check_win(self, symbol):
        # Check rows
        for row in range(GRID_SIZE):
            if all(self.board[row][col] == symbol for col in range(GRID_SIZE)):
                return True
        # Check columns
        for col in range(GRID_SIZE):
            if all(self.board[row][col] == symbol for row in range(GRID_SIZE)):
                return True
        # Check diagonals
        if all(self.board[i][i] == symbol for i in range(GRID_SIZE)):
            return True
        if all(self.board[i][GRID_SIZE - 1 - i] == symbol for i in range(GRID_SIZE)):
            return True
        return False

    def is_full(self):
        return all(self.board[row][col] != '' for row in range(GRID_SIZE) for col in range(GRID_SIZE))

    def get_available_moves(self):
        moves = []
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.board[row][col] == '':
                    moves.append((row, col))
        return moves

class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y, type, color=RED):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.type = type
        self.health = 1
        self.speed = 2
        self.target_row, self.target_col = -1, -1
        self.grid_interaction = False # Does it interact with the grid?
        self.corrupt_chance = 0.3

    def update(self, grid, player_sprite):
        pass

    def attempt_corrupt(self, grid):
        if random.random() < self.corrupt_chance:
            # Try to corrupt a random occupied grid cell
            occupied_cells = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if grid.board[r][c] != '']
            if occupied_cells:
                row, col = random.choice(occupied_cells)
                corrupted_sprite = CorruptedSymbol(row, col, grid)
                grid.symbols[(row, col)] = corrupted_sprite
                self.corrupt_chance *= 0.8 # Reduce chance after successful corruption
                return True
        return False

class NebulaSwamer(Alien):
    def __init__(self, x, y):
        super().__init__(x, y, "nebula_swarmer", CYAN)
        self.grid_interaction = True
        self.corrupt_chance = 0.4

    def update(self, grid, player_sprite):
        if self.rect.centerx != WIDTH // 2 + GRID_OFFSET_X and self.rect.centery != HEIGHT // 2 + GRID_OFFSET_Y:
            angle = math.atan2(HEIGHT // 2 + GRID_OFFSET_Y - self.rect.centery, WIDTH // 2 + GRID_OFFSET_X - self.rect.centerx)
            self.rect.x += self.speed * math.cos(angle)
            self.rect.y += self.speed * math.sin(angle)

        if pygame.sprite.collide_rect(self, player_sprite) and self.grid_interaction:
             if self.attempt_corrupt(grid):
                 self.kill() # Swarmer is removed after successful corruption

class CometRaider(Alien):
    def __init__(self, x, y):
        super().__init__(x, y, "comet_raider", ORANGE)
        self.health = 2
        self.speed = 3
        self.target_line = None # 'row', 'col', 'diag1', 'diag2'
        self.target_index = -1
        self.blocking = False

    def update(self, grid, player_sprite):
        if not self.blocking:
            if random.random() < 0.01: # Chance to start blocking
                self.blocking = True
                self.choose_target(grid)

        if self.blocking and self.target_line:
            self.move_along_target_line(grid)

    def choose_target(self, grid):
        lines = ['row', 'col', 'diag1', 'diag2']
        self.target_line = random.choice(lines)
        if self.target_line == 'row':
            self.target_index = random.randint(0, GRID_SIZE - 1)
        elif self.target_line == 'col':
            self.target_index = random.randint(0, GRID_SIZE - 1)
        elif self.target_line == 'diag1':
            self.target_index = 0 # Main diagonal
        elif self.target_line == 'diag2':
            self.target_index = 0 # Anti-diagonal

    def move_along_target_line(self, grid):
        if self.target_line == 'row':
            target_x = GRID_OFFSET_X + self.target_index * CELL_SIZE + CELL_SIZE // 2
            target_y = GRID_OFFSET_Y + random.randint(0, GRID_SIZE - 1) * CELL_SIZE + CELL_SIZE // 2
            angle = math.atan2(target_y - self.rect.centery, target_x - self.rect.centerx)
            self.rect.x += self.speed * math.cos(angle)
            self.rect.y += self.speed * math.sin(angle)

            # Check if it's close to a grid cell on the row
            for col in range(GRID_SIZE):
                cell_x, cell_y = grid.get_cell_coords(self.target_index, col)
                if abs(self.rect.centerx - cell_x) < CELL_SIZE // 4 and abs(self.rect.centery - cell_y) < CELL_SIZE // 4:
                    if grid.board[self.target_index][col] == '':
                        grid.board[self.target_index][col] = 'ALIEN_BLOCK' # Placeholder for alien block
                        self.blocking = False
                        self.kill()
                        return
        # Similar logic for other target lines (col, diag1, diag2)
        # For simplicity, we'll just focus on row for this example.
        # In a full game, implement movement for all lines.

class BlackHoleBlob(Alien):
    def __init__(self, x, y):
        super().__init__(x, y, "black_hole_blob", PURPLE)
        self.health = 5
        self.speed = 0.5
        self.expansion_rate = 1.05
        self.max_size = CELL_SIZE * 1.5
        self.current_size = 30
        self.image = pygame.Surface((self.current_size, self.current_size))
        self.image.fill(PURPLE)
        self.rect = self.image.get_rect(center=(x, y))
        self.grid_interaction = True
        self.expansion_delay = 60 # frames before expansion

    def update(self, grid, player_sprite):
        if self.expansion_delay > 0:
            self.expansion_delay -= 1
        else:
            if self.current_size < self.max_size:
                self.current_size *= self.expansion_rate
                self.image = pygame.Surface((int(self.current_size), int(self.current_size)))
                self.image.fill(PURPLE)
                self.rect = self.image.get_rect(center=self.rect.center)

            # Mark grid cells within the black hole as unplayable
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    cell_x, cell_y = grid.get_cell_coords(row, col)
                    if math.dist((cell_x, cell_y), self.rect.center) < self.current_size / 2:
                        if grid.board[row][col] == '':
                            grid.board[row][col] = 'UNPLAYABLE'

class CorruptedSymbol(pygame.sprite.Sprite):
    def __init__(self, row, col, grid):
        super().__init__()
        self.image = pygame.Surface((CELL_SIZE - 20, CELL_SIZE - 20))
        self.image.fill(GRAY)
        self.rect = self.image.get_rect(center=grid.get_cell_coords(row, col))
        self.original_row, self.original_col = row, col
        self.duration = 120 # frames it remains corrupted
        self.grid = grid

    def update(self):
        self.duration -= 1
        if self.duration <= 0:
            self.uncorrupt()

    def uncorrupt(self):
        self.grid.board[self.original_row][self.original_col] = ''
        self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, type, color):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.type = type

class SymbolBoostPowerup(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, "symbol_boost", YELLOW)

class ShieldOrbPowerup(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, "shield_orb", CYAN)

class NovaBurstPowerup(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, "nova_burst", RED)

class GravitationalPullPowerup(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, "gravitational_pull", GREEN)

class WormholeWarpPowerup(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, "wormhole_warp", PURPLE)

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color, type):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.type = type

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Cosmic Tic-Tac-Toe: Stellar Showdown")
        self.clock = pygame.time.Clock()
        self.state = MENU

        # Game objects
        self.player = Player(WIDTH // 4, HEIGHT // 2)
        self.grid = Grid()
        self.all_sprites = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.corrupted_symbols = pygame.sprite.Group()

        # Game stats
        self.score = 0
        self.level_data = None
        self.current_level = 1
        self.player_symbol_choice = 'X'
        self.alien_waves = []
        self.current_alien_wave_index = 0
        self.alien_spawn_timer = 0
        self.alien_spawn_interval = 120 # frames

        self.load_level(self.current_level)

    def load_level(self, level_num):
        # Reset game objects for a new level
        self.all_sprites.empty()
        self.aliens.empty()
        self.powerups.empty()
        self.obstacles.empty()
        self.corrupted_symbols.empty()
        self.grid.reset()

        # Placeholder for level data - replace with actual level loading
        self.level_data = {
            "level_number": 1,
            "name": "Nebula Nurturing Grounds",
            "description": "Welcome to your first cosmic challenge! Learn the basics of Stellar Showdown by navigating through a peaceful nebula, gathering resources, and fending off some early alien scouts. Your strategic placement on the 3x3 grid is key!",
            "size": {"width": 800, "height": 600},
            "spawn_points": [
                {"x": 100, "y": 100, "type": "player"},
                {"x": 700, "y": 500, "type": "enemy_spawn"}
            ],
            "obstacles": [
                {"x": 200, "y": 200, "width": 80, "height": 80, "type": "asteroid_field", "color": GRAY},
                {"x": 500, "y": 300, "width": 60, "height": 60, "type": "cosmic_dust", "color": DARK_GRAY}
            ],
            "powerups": [
                {"x": 300, "y": 150, "type": "symbol_boost"},
                {"x": 600, "y": 450, "type": "shield_orb"}
            ],
            "enemies": [
                {"x": 400, "y": 300, "type": "alien_scout", "color": RED},
                {"x": 150, "y": 450, "type": "alien_scout", "color": RED},
                {"x": 650, "y": 100, "type": "alien_scout", "color": RED}
            ],
            "alien_waves": [
                [{"type": "nebula_swarmer", "x": 50, "y": 50, "color": CYAN}, {"type": "nebula_swarmer", "x": 750, "y": 550, "color": CYAN}],
                [{"type": "comet_raider", "x": 100, "y": 100, "color": ORANGE}]
            ],
            "objectives": [
                {"type": "place_symbols", "target": "stars", "count": 3, "description": "Place 3 of your chosen symbols on the grid."},
                {"type": "defeat", "target": "alien_scout", "count": 3, "description": "Defeat all the initial alien scouts."}
            ],
            "difficulty": "easy",
            "time_limit": 180
        }

        # Add obstacles
        for obs_data in self.level_data["obstacles"]:
            obstacle = Obstacle(obs_data["x"], obs_data["y"], obs_data["width"], obs_data["height"], obs_data["color"], obs_data["type"])
            self.obstacles.add(obstacle)
            self.all_sprites.add(obstacle)

        # Add initial enemies
        for enemy_data in self.level_data["enemies"]:
            if enemy_data["type"] == "alien_scout":
                alien = NebulaSwamer(enemy_data["x"], enemy_data["y"]) # Using Swarmer as basic scout for level 1
                alien.health = 1 # Specific health for this type
                self.aliens.add(alien)
                self.all_sprites.add(alien)

        # Add powerups
        for powerup_data in self.level_data["powerups"]:
            if powerup_data["type"] == "symbol_boost":
                powerup = SymbolBoostPowerup(powerup_data["x"], powerup_data["y"])
            elif powerup_data["type"] == "shield_orb":
                powerup = ShieldOrbPowerup(powerup_data["x"], powerup_data["y"])
            else:
                continue # Skip unknown powerup types
            self.powerups.add(powerup)
            self.all_sprites.add(powerup)

        self.all_sprites.add(self.player)
        self.alien_waves = self.level_data["alien_waves"]
        self.current_alien_wave_index = 0
        self.alien_spawn_timer = 0

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.state == MENU:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.state = PLAYING
                        self.player.set_symbol(self.player_symbol_choice)
                    elif event.key == pygame.K_x:
                        self.player_symbol_choice = 'X'
                    elif event.key == pygame.K_o:
                        self.player_symbol_choice = 'O'

            elif self.state == PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        self.player.move(0, -1)
                    elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        self.player.move(0, 1)
                    elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        self.player.move(-1, 0)
                    elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        self.player.move(1, 0)
                    elif event.key == pygame.K_SPACE:
                        # Try to place symbol
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        clicked_row, clicked_col = self.get_grid_cell_from_mouse(mouse_x, mouse_y)
                        if clicked_row is not None and clicked_col is not None:
                            if self.grid.is_valid_move(clicked_row, clicked_col):
                                symbol_sprite_img = None
                                if self.player.symbol == 'X':
                                    symbol_sprite_img = pygame.Surface((CELL_SIZE - 40, CELL_SIZE - 40))
                                    symbol_sprite_img.fill(RED)
                                elif self.player.symbol == 'O':
                                    symbol_sprite_img = pygame.Surface((CELL_SIZE - 40, CELL_SIZE - 40))
                                    symbol_sprite_img.fill(GREEN)

                                if symbol_sprite_img:
                                    symbol_sprite = pygame.sprite.Sprite()
                                    symbol_sprite.image = symbol_sprite_img
                                    symbol_sprite.rect = symbol_sprite.image.get_rect(center=self.grid.get_cell_coords(clicked_row, clicked_col))
                                    self.all_sprites.add(symbol_sprite)

                                    if self.grid.place_symbol(clicked_row, clicked_col, self.player.symbol, symbol_sprite):
                                        # Check for win conditions after placement
                                        if self.grid.check_win(self.player.symbol):
                                            self.state = GAME_OVER
                                            self.win_message = "You Win!"
                                        elif self.grid.is_full():
                                            self.state = GAME_OVER
                                            self.win_message = "It's a Draw!"
                                        else:
                                            # Switch player turn after a successful placement
                                            self.switch_player_turn()

                    elif event.key == pygame.K_1: # Symbol shift to Stars (X)
                        self.player.set_symbol('X')
                    elif event.key == pygame.K_2: # Symbol shift to Galaxies (O)
                        self.player.set_symbol('O')
                    elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT: # Cosmic Shield powerup
                        if self.player.powerups['cosmic_shield'] > 0:
                            self.player.powerups['cosmic_shield'] -= 1
                            # Implement cosmic shield logic here (e.g., prevent alien from occupying a cell)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left click
                        mouse_x, mouse_y = event.pos
                        clicked_row, clicked_col = self.get_grid_cell_from_mouse(mouse_x, mouse_y)

                        if clicked_row is not None and clicked_col is not None:
                            # Check if clicking on an alien to attack
                            for alien in self.aliens:
                                if alien.rect.collidepoint(mouse_x, mouse_y) and alien.health > 0:
                                    alien.health -= 1
                                    if alien.health <= 0:
                                        alien.kill()
                                        self.score += 10 # Scoring for defeating aliens
                                    return # Prevent symbol placement if alien was clicked

                            # Try to place symbol if space is available and not clicked on alien
                            if self.grid.is_valid_move(clicked_row, clicked_col):
                                symbol_sprite_img = None
                                if self.player.symbol == 'X':
                                    symbol_sprite_img = pygame.Surface((CELL_SIZE - 40, CELL_SIZE - 40))
                                    symbol_sprite_img.fill(RED)
                                elif self.player.symbol == 'O':
                                    symbol_sprite_img = pygame.Surface((CELL_SIZE - 40, CELL_SIZE - 40))
                                    symbol_sprite_img.fill(GREEN)

                                if symbol_sprite_img:
                                    symbol_sprite = pygame.sprite.Sprite()
                                    symbol_sprite.image = symbol_sprite_img
                                    symbol_sprite.rect = symbol_sprite.image.get_rect(center=self.grid.get_cell_coords(clicked_row, clicked_col))
                                    self.all_sprites.add(symbol_sprite)

                                    if self.grid.place_symbol(clicked_row, clicked_col, self.player.symbol, symbol_sprite):
                                        # Check for win conditions after placement
                                        if self.grid.check_win(self.player.symbol):
                                            self.state = GAME_OVER
                                            self.win_message = "You Win!"
                                        elif self.grid.is_full():
                                            self.state = GAME_OVER
                                            self.win_message = "It's a Draw!"
                                        else:
                                            # Switch player turn after a successful placement
                                            self.switch_player_turn()

            elif self.state == GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_m:
                        self.state = MENU

    def get_grid_cell_from_mouse(self, mouse_x, mouse_y):
        if GRID_OFFSET_X <= mouse_x < GRID_OFFSET_X + GRID_SIZE * CELL_SIZE and \
           GRID_OFFSET_Y <= mouse_y < GRID_OFFSET_Y + GRID_SIZE * CELL_SIZE:
            col = (mouse_x - GRID_OFFSET_X) // CELL_SIZE
            row = (mouse_y - GRID_OFFSET_Y) // CELL_SIZE
            return row, col
        return None, None

    def switch_player_turn(self):
        # In a single-player game against AI, this would switch to AI's turn.
        # For this example, we'll just ensure the AI acts after player's move.
        pass

    def update_game(self):
        if self.state == PLAYING:
            self.player.update()
            self.aliens.update(self.grid, self.player)
            self.corrupted_symbols.update()

            # Powerup collection
            powerup_collisions = pygame.sprite.spritecollide(self.player, self.powerups, True)
            for powerup in powerup_collisions:
                if powerup.type == "symbol_boost":
                    self.score += 5
                    # Apply symbol boost effect (e.g., temporary symbol change)
                elif powerup.type == "shield_orb":
                    self.player.powerups['cosmic_shield'] += 1
                    self.score += 5
                elif powerup.type == "nova_burst":
                    # Implement Nova Burst powerup logic
                    self.score += 10
                elif powerup.type == "gravitational_pull":
                    # Implement Gravitational Pull powerup logic
                    self.score += 10
                elif powerup.type == "wormhole_warp":
                    # Implement Wormhole Warp powerup logic
                    self.score += 10

            # Alien spawning
            self.alien_spawn_timer += 1
            if self.alien_spawn_timer >= self.alien_spawn_interval and self.current_alien_wave_index < len(self.alien_waves):
                wave = self.alien_waves[self.current_alien_wave_index]
                for alien_data in wave:
                    alien_type = alien_data["type"]
                    x, y = alien_data["x"], alien_data["y"]
                    color = alien_data.get("color", RED)
                    alien = None
                    if alien_type == "nebula_swarmer":
                        alien = NebulaSwamer(x, y)
                    elif alien_type == "comet_raider":
                        alien = CometRaider(x, y)
                    elif alien_type == "black_hole_blob":
                        alien = BlackHoleBlob(x, y)
                    
                    if alien:
                        alien.image.fill(color) # Apply color if specified
                        self.aliens.add(alien)
                        self.all_sprites.add(alien)
                self.current_alien_wave_index += 1
                self.alien_spawn_timer = 0
                self.alien_spawn_interval = max(30, self.alien_spawn_interval - 5) # Increase spawn rate

            # Check for game over conditions
            if self.grid.is_full() and not self.grid.check_win(self.player.symbol):
                self.state = GAME_OVER
                self.win_message = "It's a Draw!"

            # Basic AI turn (for now, just if player places a symbol)
            if self.grid.check_win('X') or self.grid.check_win('O') or self.grid.is_full():
                if self.grid.check_win(self.player.symbol):
                    self.state = GAME_OVER
                    self.win_message = "You Win!"
                elif self.grid.check_win('O'): # Assuming AI plays as 'O'
                    self.state = GAME_OVER
                    self.win_message = "AI Wins!"
                elif self.grid.is_full():
                    self.state = GAME_OVER
                    self.win_message = "It's a Draw!"
                return

            # AI move logic (simplified for now)
            if not any(alien.health > 0 for alien in self.aliens): # If no active aliens
                if random.random() < 0.1: # Chance for AI to make a move
                    available_moves = self.grid.get_available_moves()
                    if available_moves:
                        row, col = random.choice(available_moves)
                        symbol_sprite_img = pygame.Surface((CELL_SIZE - 40, CELL_SIZE - 40))
                        symbol_sprite_img.fill(GREEN) # AI plays as 'O'
                        symbol_sprite = pygame.sprite.Sprite()
                        symbol_sprite.image = symbol_sprite_img
                        symbol_sprite.rect = symbol_sprite.image.get_rect(center=self.grid.get_cell_coords(row, col))
                        self.all_sprites.add(symbol_sprite)

                        if self.grid.place_symbol(row, col, 'O', symbol_sprite):
                            if self.grid.check_win('O'):
                                self.state = GAME_OVER
                                self.win_message = "AI Wins!"
                            elif self.grid.is_full():
                                self.state = GAME_OVER
                                self.win_message = "It's a Draw!"

    def draw_menu(self):
        self.screen.fill(BLACK)
        font = pygame.font.Font(None, 74)
        title_text = font.render("Cosmic Tic-Tac-Toe", True, WHITE)
        self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))

        font = pygame.font.Font(None, 50)
        instruction1 = font.render("Press ENTER to Start", True, WHITE)
        self.screen.blit(instruction1, (WIDTH // 2 - instruction1.get_width() // 2, 250))

        instruction2 = font.render("Choose Symbol: X (Press X) or O (Press O)", True, WHITE)
        self.screen.blit(instruction2, (WIDTH // 2 - instruction2.get_width() // 2, 320))

        current_choice_text = font.render(f"Current Symbol: {self.player_symbol_choice}", True, YELLOW)
        self.screen.blit(current_choice_text, (WIDTH // 2 - current_choice_text.get_width() // 2, 390))

    def draw_playing(self):
        self.screen.fill(DARK_GRAY) # Cosmic background

        # Draw grid lines
        for row in range(GRID_SIZE + 1):
            pygame.draw.line(self.screen, CYAN, (GRID_OFFSET_X, GRID_OFFSET_Y + row * CELL_SIZE),
                             (GRID_OFFSET_X + GRID_SIZE * CELL_SIZE, GRID_OFFSET_Y + row * CELL_SIZE), 2)
        for col in range(GRID_SIZE + 1):
            pygame.draw.line(self.screen, CYAN, (GRID_OFFSET_X + col * CELL_SIZE, GRID_OFFSET_Y),
                             (GRID_OFFSET_X + col * CELL_SIZE, GRID_OFFSET_Y + GRID_SIZE * CELL_SIZE), 2)

        # Draw player and AI symbols already placed on the grid
        for (row, col), sprite in self.grid.symbols.items():
            self.screen.blit(sprite.image, sprite.rect)

        self.all_sprites.draw(self.screen)

        # Draw UI elements
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        level_text = font.render(f"Level: {self.current_level}", True, WHITE)
        self.screen.blit(level_text, (10, 50))

        symbol_text = font.render(f"Your Symbol: {self.player.symbol}", True, WHITE)
        self.screen.blit(symbol_text, (WIDTH - symbol_text.get_width() - 10, 10))

        shield_text = font.render(f"Shields: {self.player.powerups['cosmic_shield']}", True, WHITE)
        self.screen.blit(shield_text, (WIDTH - shield_text.get_width() - 10, 50))


    def draw_game_over(self):
        self.screen.fill(BLACK)
        font = pygame.font.Font(None, 74)
        win_text = font.render(self.win_message, True, YELLOW)
        self.screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, 200))

        font = pygame.font.Font(None, 50)
        restart_text = font.render("Press R to Restart", True, WHITE)
        self.screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 300))

        menu_text = font.render("Press M to return to Menu", True, WHITE)
        self.screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, 370))

    def reset_game(self):
        self.player = Player(WIDTH // 4, HEIGHT // 2)
        self.grid.reset()
        self.all_sprites.empty()
        self.aliens.empty()
        self.powerups.empty()
        self.obstacles.empty()
        self.corrupted_symbols.empty()
        self.score = 0
        self.current_level = 1
        self.player_symbol_choice = 'X'
        self.load_level(self.current_level)
        self.all_sprites.add(self.player)
        self.state = PLAYING

    def run(self):
        running = True
        while running:
            self.handle_input()
            self.update_game()

            if self.state == MENU:
                self.draw_menu()
            elif self.state == PLAYING:
                self.draw_playing()
            elif self.state == GAME_OVER:
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
