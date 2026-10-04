
import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Shellbound Odyssey"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# Game States
MENU = 0
PLAYING = 1
GAME_OVER = 2
WIN = 3

# Player Properties
PLAYER_SPEED = 4
PLAYER_DIVE_SPEED = 6
PLAYER_DIVE_DURATION = 3000  # milliseconds
PLAYER_SHELL_RETREAT_DURATION = 1500  # milliseconds
PLAYER_STAMINA_MAX = 100
PLAYER_STAMINA_REGEN_RATE = 1
PLAYER_STAMINA_CONSUMPTION_SPRINT = 0.5
PLAYER_STAMINA_CONSUMPTION_DIVE = 1

# Enemy Properties
PUFFERFISH_SPEED = 2
SEAGULL_SPEED = 5
CRAB_SPEED = 3
SHARK_PUP_SPEED = 6

# Powerup Properties
KELP_BOOST_AMOUNT = 30
BARNACLE_ARMOR_USES = 1
CURRENT_RIDER_DURATION = 3000  # milliseconds

# Scoring
POINTS_PER_KELP = 10
POINTS_PER_STARFISH = 50
TIME_BONUS_PER_SECOND = 5
PERFECTION_BONUS = 200

# Level Data (for Level 1)
level_data = {
    "level_number": 1,
    "name": "The Whispering Kelp Forest",
    "size": {"width": 800, "height": 600},
    "spawn_points": [{"x": 50, "y": 50, "type": "player"}],
    "obstacles": [
        {"x": 150, "y": 100, "width": 70, "height": 70, "type": "pushable_rock"},
        {"x": 300, "y": 200, "width": 100, "height": 30, "type": "seaweed_barrier"},
        {"x": 550, "y": 350, "width": 60, "height": 60, "type": "pushable_rock"},
        {"x": 700, "y": 200, "width": 50, "height": 150, "type": "seaweed_barrier"}
    ],
    "environmental_features": [
        {"x": 400, "y": 450, "direction": "right", "strength": 0.5, "type": "current"},
        {"x": 650, "y": 100, "direction": "down", "strength": 0.3, "type": "current"}
    ],
    "resources": [
        {"x": 250, "y": 180, "type": "kelp"},
        {"x": 400, "y": 250, "type": "kelp"},
        {"x": 180, "y": 350, "type": "barnacle_shell"},
        {"x": 500, "y": 500, "type": "barnacle_shell"},
        {"x": 720, "y": 480, "type": "starfish"} # Hidden starfish for scoring
    ],
    "enemies": [
        {"type": "hermit_crab", "x": 370, "y": 150, "patrol_path": [[370, 150], [450, 150], [450, 200], [370, 200]]},
        {"type": "pufferfish", "x": 600, "y": 300, "patrol_path": [[600, 300], [550, 300], [550, 350]]},
        {"type": "hermit_crab", "x": 100, "y": 450, "patrol_path": [[100, 450], [150, 450], [150, 400], [100, 400]]}
    ],
    "objectives": [
        {"type": "collect", "target": "kelp", "count": 5, "description": "Gather 5 strands of nutritious kelp."},
        {"type": "defeat", "target": "hermit_crab", "count": 2, "description": "Defeat the territorial hermit crabs."},
        {"type": "reach", "location": {"x": 750, "y": 550}, "description": "Find the exit to the next area."}
    ],
    "difficulty": "easy",
    "time_limit": 180
}

# --- Game Objects ---

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 20))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.x_vel = 0
        self.y_vel = 0
        self.speed = PLAYER_SPEED
        self.is_diving = False
        self.dive_timer = 0
        self.is_retreating = False
        self.retreat_timer = 0
        self.stamina = PLAYER_STAMINA_MAX
        self.max_stamina = PLAYER_STAMINA_MAX
        self.stamina_regen_rate = PLAYER_STAMINA_REGEN_RATE
        self.stamina_consumption_sprint = PLAYER_STAMINA_CONSUMPTION_SPRINT
        self.stamina_consumption_dive = PLAYER_STAMINA_CONSUMPTION_DIVE
        self.barnacle_armor_uses = 0
        self.invincible = False
        self.invincible_timer = 0

    def update(self, walls, currents, seaweed_barriers, pushable_rocks):
        if self.is_retreating:
            self.retreat_timer -= 10
            if self.retreat_timer <= 0:
                self.is_retreating = False
                self.invincible = False
                self.image.fill(BROWN) # Reset color
            return

        if self.is_diving:
            self.dive_timer -= 10
            if self.dive_timer <= 0:
                self.is_diving = False
                self.speed = PLAYER_SPEED # Return to normal speed
            self.rect.y += self.y_vel * self.speed # Slower movement when diving

        # Apply stamina consumption
        if self.stamina > 0:
            if abs(self.x_vel) > 0 or abs(self.y_vel) > 0: # If moving
                if self.is_diving:
                    self.stamina -= self.stamina_consumption_dive
                else:
                    self.stamina -= self.stamina_consumption_sprint
            self.stamina = max(0, self.stamina)
        else:
            self.speed = PLAYER_SPEED # Cannot sprint if out of stamina

        # Stamina regeneration
        if self.stamina < self.max_stamina:
            self.stamina += self.stamina_regen_rate

        # Current effects
        for current in currents:
            if self.rect.colliderect(current.rect):
                self.x_vel += current.direction_x * current.strength
                self.y_vel += current.direction_y * current.strength

        # Apply velocity to position
        self.rect.x += self.x_vel * self.speed
        self.x_vel = 0 # Reset velocity after applying it

        # Collision with walls
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if self.x_vel > 0:
                    self.rect.right = wall.rect.left
                if self.x_vel < 0:
                    self.rect.left = wall.rect.right
                self.x_vel = 0

        self.rect.y += self.y_vel * self.speed
        self.y_vel = 0 # Reset velocity after applying it

        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if self.y_vel > 0:
                    self.rect.bottom = wall.rect.top
                if self.y_vel < 0:
                    self.rect.top = wall.rect.bottom
                self.y_vel = 0

        # Collision with seaweed barriers
        for barrier in seaweed_barriers:
            if self.rect.colliderect(barrier.rect):
                if self.x_vel > 0:
                    self.rect.right = barrier.rect.left
                if self.x_vel < 0:
                    self.rect.left = barrier.rect.right
                self.x_vel = 0
                if self.y_vel > 0:
                    self.rect.bottom = barrier.rect.top
                if self.y_vel < 0:
                    self.rect.top = barrier.rect.bottom
                self.y_vel = 0

        # Collision with pushable rocks
        for rock in pushable_rocks:
            if self.rect.colliderect(rock.rect):
                if self.x_vel > 0:
                    rock.rect.x += 10
                    if rock.rect.collidelist([w for w in walls]) != -1:
                        rock.rect.x -= 10
                        self.rect.right = rock.rect.left
                if self.x_vel < 0:
                    rock.rect.x -= 10
                    if rock.rect.collidelist([w for w in walls]) != -1:
                        rock.rect.x += 10
                        self.rect.left = rock.rect.right
                if self.y_vel > 0:
                    rock.rect.y += 10
                    if rock.rect.collidelist([w for w in walls]) != -1:
                        rock.rect.y -= 10
                        self.rect.bottom = rock.rect.top
                if self.y_vel < 0:
                    rock.rect.y -= 10
                    if rock.rect.collidelist([w for w in walls]) != -1:
                        rock.rect.y += 10
                        self.rect.top = rock.rect.bottom
                self.x_vel = 0
                self.y_vel = 0


        # Keep player within screen bounds
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)

        if self.invincible:
            self.invincible_timer -= 10
            if self.invincible_timer <= 0:
                self.invincible = False
                self.image.fill(BROWN) # Reset color


    def move_left(self):
        self.x_vel = -1
    def move_right(self):
        self.x_vel = 1
    def move_up(self):
        self.y_vel = -1
    def move_down(self):
        self.y_vel = 1

    def dive(self):
        if not self.is_diving and self.stamina >= 50: # Requires some stamina to start
            self.is_diving = True
            self.dive_timer = PLAYER_DIVE_DURATION
            self.speed = PLAYER_DIVE_SPEED
            self.stamina -= 50 # Initial stamina cost
            self.image.fill(CYAN) # Change color when diving

    def shell_retreat(self):
        if not self.is_retreating:
            self.is_retreating = True
            self.retreat_timer = PLAYER_SHELL_RETREAT_DURATION
            self.invincible = True
            self.image.fill(PURPLE) # Change color when retreating
            self.x_vel = 0
            self.y_vel = 0

    def apply_barnacle_armor(self):
        self.barnacle_armor_uses += 1
        self.invincible = True
        self.invincible_timer = PLAYER_SHELL_RETREAT_DURATION # Use a similar duration for invincibility

    def take_damage(self):
        if self.invincible:
            return False # Invincible, no damage

        if self.barnacle_armor_uses > 0:
            self.barnacle_armor_uses -= 1
            self.invincible = True
            self.invincible_timer = PLAYER_SHELL_RETREAT_DURATION
            return False # Absorbed hit with barnacle armor

        return True # Take actual damage

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=BLUE):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class PushableRock(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(BROWN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class SeaweedBarrier(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Current(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, strength):
        super().__init__()
        self.direction = direction
        self.strength = strength
        self.direction_x = 0
        self.direction_y = 0
        if direction == "right":
            self.direction_x = 1
        elif direction == "left":
            self.direction_x = -1
        elif direction == "up":
            self.direction_y = -1
        elif direction == "down":
            self.direction_y = 1

        self.image = pygame.Surface((50, 50))
        self.image.set_alpha(100) # Make it semi-transparent
        self.image.fill(CYAN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Kelp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((15, 40))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class BarnacleShell(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(ORANGE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Starfish(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((25, 25))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Pufferfish(pygame.sprite.Sprite):
    def __init__(self, x, y, patrol_path):
        super().__init__()
        self.image = pygame.Surface((25, 25))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.patrol_path = patrol_path
        self.current_waypoint = 0
        self.speed = PUFFERFISH_SPEED
        self.direction = 1 # 1 for forward, -1 for backward

    def update(self, walls):
        target_x, target_y = self.patrol_path[self.current_waypoint]
        dx = target_x - self.rect.x
        dy = target_y - self.rect.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance < self.speed:
            self.current_waypoint = (self.current_waypoint + 1) % len(self.patrol_path)
        else:
            self.rect.x += dx / distance * self.speed
            self.rect.y += dy / distance * self.speed

        # Collision with walls
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                # Simple push back logic
                if self.rect.centerx < wall.rect.centerx:
                    self.rect.right = wall.rect.left
                else:
                    self.rect.left = wall.rect.right
                if self.rect.centery < wall.rect.centery:
                    self.rect.bottom = wall.rect.top
                else:
                    self.rect.top = wall.rect.bottom

class HermitCrab(pygame.sprite.Sprite):
    def __init__(self, x, y, patrol_path):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.patrol_path = patrol_path
        self.current_waypoint = 0
        self.speed = CRAB_SPEED

    def update(self, walls):
        target_x, target_y = self.patrol_path[self.current_waypoint]
        dx = target_x - self.rect.x
        dy = target_y - self.rect.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance < self.speed:
            self.current_waypoint = (self.current_waypoint + 1) % len(self.patrol_path)
        else:
            self.rect.x += dx / distance * self.speed
            self.rect.y += dy / distance * self.speed

        # Collision with walls
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                # Simple push back logic
                if self.rect.centerx < wall.rect.centerx:
                    self.rect.right = wall.rect.left
                else:
                    self.rect.left = wall.rect.right
                if self.rect.centery < wall.rect.centery:
                    self.rect.bottom = wall.rect.top
                else:
                    self.rect.top = wall.rect.bottom

class Seagull(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((35, 25))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = SEAGULL_SPEED
        self.state = "circling" # circling, swooping
        self.target = None
        self.patrol_radius = 100
        self.angle = random.uniform(0, 360)
        self.center_x = x
        self.center_y = y

    def update(self, player):
        if self.state == "circling":
            self.angle += 0.05 # Rotate around
            self.rect.x = self.center_x + self.patrol_radius * math.cos(math.radians(self.angle))
            self.rect.y = self.center_y + self.patrol_radius * math.sin(math.radians(self.angle))

            # Decide to swoop
            if player.rect.y < self.rect.y - 50 and random.random() < 0.005: # If player is below and chance
                self.state = "swooping"
                self.target = player.rect.center
                self.image.fill(RED) # Indicate attack

        elif self.state == "swooping":
            if self.target:
                dx = self.target[0] - self.rect.centerx
                dy = self.target[1] - self.rect.centery
                distance = math.sqrt(dx**2 + dy**2)

                if distance < self.speed:
                    self.state = "circling"
                    self.image.fill(WHITE) # Reset color
                    self.patrol_radius = random.randint(80, 150) # Change patrol radius
                    self.center_x = self.rect.x
                    self.center_y = self.rect.y
                    self.angle = random.uniform(0, 360)
                else:
                    self.rect.x += dx / distance * self.speed
                    self.rect.y += dy / distance * self.speed

class SharkPup(pygame.sprite.Sprite):
    def __init__(self, x, y, patrol_path):
        super().__init__()
        self.image = pygame.Surface((40, 20))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.patrol_path = patrol_path
        self.current_waypoint = 0
        self.speed = SHARK_PUP_SPEED
        self.state = "patrolling" # patrolling, lunging

    def update(self, player, walls):
        if self.state == "patrolling":
            target_x, target_y = self.patrol_path[self.current_waypoint]
            dx = target_x - self.rect.x
            dy = target_y - self.rect.y
            distance = math.sqrt(dx**2 + dy**2)

            if distance < self.speed:
                self.current_waypoint = (self.current_waypoint + 1) % len(self.patrol_path)
            else:
                self.rect.x += dx / distance * self.speed
                self.rect.y += dy / distance * self.speed

            # Detect player and lunge
            if player.rect.colliderect(self.rect.inflate(150, 150)) and not player.is_diving:
                self.state = "lunging"
                self.image.fill(ORANGE) # Indicate lunge

        elif self.state == "lunging":
            if player.rect: # Ensure player still exists
                dx = player.rect.centerx - self.rect.centerx
                dy = player.rect.centery - self.rect.centery
                distance = math.sqrt(dx**2 + dy**2)

                if distance < self.speed:
                    self.state = "patrolling"
                    self.image.fill(RED) # Reset color
                    self.current_waypoint = (self.current_waypoint + 1) % len(self.patrol_path) # Go to next patrol point
                else:
                    self.rect.x += dx / distance * self.speed
                    self.rect.y += dy / distance * self.speed

        # Collision with walls
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if self.rect.centerx < wall.rect.centerx:
                    self.rect.right = wall.rect.left
                else:
                    self.rect.left = wall.rect.right
                if self.rect.centery < wall.rect.centery:
                    self.rect.bottom = wall.rect.top
                else:
                    self.rect.top = wall.rect.bottom
                # If hitting a wall during lunge, revert to patrol
                if self.state == "lunging":
                    self.state = "patrolling"
                    self.image.fill(RED)


# --- Game Logic ---

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(SCREEN_TITLE)
        self.clock = pygame.time.Clock()
        self.game_state = MENU

        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.environmental_features = pygame.sprite.Group()
        self.resources = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.collectible_kelp = pygame.sprite.Group()
        self.collectible_shells = pygame.sprite.Group()
        self.collectible_starfish = pygame.sprite.Group()

        self.player = None
        self.level_data = None
        self.current_level = 1

        self.score = 0
        self.time_remaining = 0
        self.level_start_time = 0

        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)

        self.load_menu_assets()

    def load_menu_assets(self):
        pass # No specific assets needed for this simple menu

    def load_level(self, level_data):
        self.all_sprites.empty()
        self.walls.empty()
        self.obstacles.empty()
        self.environmental_features.empty()
        self.resources.empty()
        self.enemies.empty()
        self.collectible_kelp.empty()
        self.collectible_shells.empty()
        self.collectible_starfish.empty()

        self.level_data = level_data
        self.time_remaining = level_data["time_limit"]
        self.level_start_time = pygame.time.get_ticks()

        # Create boundaries as walls
        self.walls.add(Wall(0, 0, SCREEN_WIDTH, 10)) # Top
        self.walls.add(Wall(0, SCREEN_HEIGHT - 10, SCREEN_WIDTH, 10)) # Bottom
        self.walls.add(Wall(0, 0, 10, SCREEN_HEIGHT)) # Left
        self.walls.add(Wall(SCREEN_WIDTH - 10, 0, 10, SCREEN_HEIGHT)) # Right

        for obj_data in level_data["obstacles"]:
            if obj_data["type"] == "pushable_rock":
                rock = PushableRock(obj_data["x"], obj_data["y"], obj_data["width"], obj_data["height"])
                self.obstacles.add(rock)
                self.all_sprites.add(rock)
            elif obj_data["type"] == "seaweed_barrier":
                barrier = SeaweedBarrier(obj_data["x"], obj_data["y"], obj_data["width"], obj_data["height"])
                self.obstacles.add(barrier)
                self.all_sprites.add(barrier)

        for feature_data in level_data["environmental_features"]:
            if feature_data["type"] == "current":
                current = Current(feature_data["x"], feature_data["y"], feature_data["direction"], feature_data["strength"])
                self.environmental_features.add(current)
                self.all_sprites.add(current)

        for res_data in level_data["resources"]:
            if res_data["type"] == "kelp":
                kelp = Kelp(res_data["x"], res_data["y"])
                self.resources.add(kelp)
                self.collectible_kelp.add(kelp)
                self.all_sprites.add(kelp)
            elif res_data["type"] == "barnacle_shell":
                shell = BarnacleShell(res_data["x"], res_data["y"])
                self.resources.add(shell)
                self.collectible_shells.add(shell)
                self.all_sprites.add(shell)
            elif res_data["type"] == "starfish":
                starfish = Starfish(res_data["x"], res_data["y"])
                self.resources.add(starfish)
                self.collectible_starfish.add(starfish)
                self.all_sprites.add(starfish)

        for enemy_data in level_data["enemies"]:
            if enemy_data["type"] == "hermit_crab":
                crab = HermitCrab(enemy_data["x"], enemy_data["y"], enemy_data["patrol_path"])
                self.enemies.add(crab)
                self.all_sprites.add(crab)
            elif enemy_data["type"] == "pufferfish":
                pufferfish = Pufferfish(enemy_data["x"], enemy_data["y"], enemy_data["patrol_path"])
                self.enemies.add(pufferfish)
                self.all_sprites.add(pufferfish)
            elif enemy_data["type"] == "seagull":
                seagull = Seagull(enemy_data["x"], enemy_data["y"])
                self.enemies.add(seagull)
                self.all_sprites.add(seagull)
            elif enemy_data["type"] == "shark_pup":
                shark = SharkPup(enemy_data["x"], enemy_data["y"], enemy_data["patrol_path"])
                self.enemies.add(shark)
                self.all_sprites.add(shark)

        for spawn in level_data["spawn_points"]:
            if spawn["type"] == "player":
                self.player = Player(spawn["x"], spawn["y"])
                self.all_sprites.add(self.player)

        self.objective_manager = ObjectiveManager(level_data["objectives"])

    def reset_level(self):
        self.load_level(self.level_data) # Reload the current level

    def start_next_level(self):
        # In a real game, you'd load the next level's data here
        # For now, we'll just reset to level 1 for demonstration
        print("Moving to next level...")
        self.current_level += 1
        if self.current_level > 1: # Simulate reaching the end
            self.game_state = WIN
        else:
            self.reset_level() # Reload level 1 for now

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0 # Delta time in seconds

            if self.game_state == MENU:
                running = self.handle_menu_events()
                self.draw_menu()
            elif self.game_state == PLAYING:
                running = self.handle_playing_events()
                self.update_playing(dt)
                self.draw_playing()
            elif self.game_state == GAME_OVER:
                running = self.handle_game_over_events()
                self.draw_game_over()
            elif self.game_state == WIN:
                running = self.handle_win_events()
                self.draw_win()

            pygame.display.flip()

    def handle_menu_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.load_level(level_data) # Load level 1
                    self.game_state = PLAYING
                if event.key == pygame.K_ESCAPE:
                    return False
        return True

    def draw_menu(self):
        self.screen.fill(BLUE)
        title_text = self.large_font.render(SCREEN_TITLE, True, WHITE)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 4))

        start_text = self.font.render("Press ENTER to Start", True, WHITE)
        self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2))

        quit_text = self.font.render("Press ESC to Quit", True, WHITE)
        self.screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

    def handle_playing_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game_state = MENU
                if event.key == pygame.K_SPACE:
                    self.player.dive()
                if event.key == pygame.K_RSHIFT or event.key == pygame.K_LSHIFT:
                    self.player.shell_retreat()

        keys = pygame.key.get_pressed()
        self.player.x_vel = 0
        self.player.y_vel = 0
        if keys[pygame.K_w]:
            self.player.move_up()
        if keys[pygame.K_s]:
            self.player.move_down()
        if keys[pygame.K_a]:
            self.player.move_left()
        if keys[pygame.K_d]:
            self.player.move_right()

        # Sprinting logic (hold shift)
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.player.stamina > 0:
            self.player.speed = PLAYER_SPEED * 2 # Sprinting speed
        else:
            self.player.speed = PLAYER_SPEED # Default speed

        return True

    def update_playing(self, dt):
        self.all_sprites.update(self.walls, self.environmental_features, self.obstacles, self.obstacles) # Pass relevant groups

        # Player resource collection
        kelp_collected = pygame.sprite.spritecollide(self.player, self.collectible_kelp, True)
        for _ in kelp_collected:
            self.player.stamina = min(self.player.max_stamina, self.player.stamina + KELP_BOOST_AMOUNT)
            self.score += POINTS_PER_KELP
            self.objective_manager.update_objective("collect", "kelp")

        shells_collected = pygame.sprite.spritecollide(self.player, self.collectible_shells, True)
        for _ in shells_collected:
            self.player.apply_barnacle_armor()
            # Each collected shell adds one use of barnacle armor
            self.score += 10 # Small score for shells

        starfish_collected = pygame.sprite.spritecollide(self.player, self.collectible_starfish, True)
        for _ in starfish_collected:
            self.score += POINTS_PER_STARFISH

        # Player enemy collisions
        for enemy in self.enemies:
            if pygame.sprite.collide_rect(self.player, enemy):
                if self.player.take_damage():
                    # Player takes damage
                    self.player.rect.x -= (enemy.rect.centerx - self.player.rect.centerx) * 0.3
                    self.player.rect.y -= (enemy.rect.centery - self.player.rect.centery) * 0.3
                    self.lose_life() # Implement losing a life or game over

        # Enemy interaction with player
        for enemy in self.enemies:
            if isinstance(enemy, HermitCrab) or isinstance(enemy, Pufferfish):
                if enemy.rect.colliderect(self.player.rect):
                    if self.player.take_damage():
                        self.lose_life()

        # Update time
        elapsed_time = (pygame.time.get_ticks() - self.level_start_time) / 1000
        self.time_remaining = max(0, self.level_data["time_limit"] - elapsed_time)

        if self.time_remaining == 0:
            self.game_state = GAME_OVER

        # Check objectives
        if self.objective_manager.check_completion():
            # All objectives met, check for reach objective
            if self.objective_manager.is_reach_objective_completed():
                self.start_next_level()

        # Check if player reached the exit
        for obj in self.level_data["objectives"]:
            if obj["type"] == "reach":
                reach_location = obj["location"]
                if math.dist((self.player.rect.centerx, self.player.rect.centery), (reach_location["x"], reach_location["y"])) < 50:
                    self.objective_manager.update_objective("reach", None) # Mark reach objective as done


    def lose_life(self):
        # In a more complex game, this would reduce lives. For now, it's game over.
        self.game_state = GAME_OVER

    def draw_playing(self):
        self.screen.fill(BLACK) # Background

        # Draw level elements
        for wall in self.walls:
            self.screen.blit(wall.image, wall.rect)
        for obstacle in self.obstacles:
            self.screen.blit(obstacle.image, obstacle.rect)
        for feature in self.environmental_features:
            self.screen.blit(feature.image, feature.rect)
        for resource in self.resources:
            self.screen.blit(resource.image, resource.rect)
        for enemy in self.enemies:
            self.screen.blit(enemy.image, enemy.rect)
        if self.player:
            self.screen.blit(self.player.image, self.player.rect)

        # Draw UI
        self.draw_ui()

    def draw_ui(self):
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Time remaining
        time_text = self.font.render(f"Time: {int(self.time_remaining)}", True, WHITE)
        self.screen.blit(time_text, (SCREEN_WIDTH - time_text.get_width() - 10, 10))

        # Stamina bar
        stamina_bar_width = 100
        stamina_bar_height = 10
        stamina_ratio = self.player.stamina / self.player.max_stamina
        pygame.draw.rect(self.screen, WHITE, (10, 40, stamina_bar_width, stamina_bar_height))
        pygame.draw.rect(self.screen, YELLOW, (10, 40, stamina_bar_width * stamina_ratio, stamina_bar_height))

        # Objectives
        objective_y = 60
        for obj_display in self.objective_manager.get_display_objectives():
            obj_text = self.font.render(obj_display, True, WHITE)
            self.screen.blit(obj_text, (10, objective_y))
            objective_y += 20

    def handle_game_over_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.game_state = MENU # Go back to menu
                if event.key == pygame.K_ESCAPE:
                    return False
        return True

    def draw_game_over(self):
        self.screen.fill(BLACK)
        game_over_text = self.large_font.render("GAME OVER", True, RED)
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 3))

        final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        self.screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2))

        retry_text = self.font.render("Press ENTER to return to Menu", True, WHITE)
        self.screen.blit(retry_text, (SCREEN_WIDTH // 2 - retry_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

        quit_text = self.font.render("Press ESC to Quit", True, WHITE)
        self.screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 80))

    def handle_win_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.game_state = MENU # Go back to menu
                if event.key == pygame.K_ESCAPE:
                    return False
        return True

    def draw_win(self):
        self.screen.fill(CYAN) # A bit of color for winning
        win_text = self.large_font.render("YOU REACHED PARADISE!", True, YELLOW)
        self.screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 3))

        final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        self.screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2))

        return_to_menu_text = self.font.render("Press ENTER to return to Menu", True, WHITE)
        self.screen.blit(return_to_menu_text, (SCREEN_WIDTH // 2 - return_to_menu_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

        quit_text = self.font.render("Press ESC to Quit", True, WHITE)
        self.screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 80))

class ObjectiveManager:
    def __init__(self, objectives_data):
        self.objectives = []
        self.completed_objectives = {}
        for obj in objectives_data:
            if obj["type"] == "collect":
                self.objectives.append({
                    "type": obj["type"],
                    "target": obj["target"],
                    "count": obj["count"],
                    "current_count": 0,
                    "description": obj["description"]
                })
            elif obj["type"] == "defeat":
                self.objectives.append({
                    "type": obj["type"],
                    "target": obj["target"],
                    "count": obj["count"],
                    "current_count": 0,
                    "description": obj["description"]
                })
            elif obj["type"] == "reach":
                self.objectives.append({
                    "type": obj["type"],
                    "location": obj["location"],
                    "description": obj["description"],
                    "completed": False
                })
        self.update_display_objectives()

    def update_objective(self, obj_type, target_name):
        for obj in self.objectives:
            if obj["type"] == obj_type:
                if obj_type == "collect" and obj["target"] == target_name:
                    obj["current_count"] += 1
                elif obj_type == "defeat" and obj["target"] == target_name:
                    obj["current_count"] += 1
                elif obj_type == "reach":
                    obj["completed"] = True
        self.update_display_objectives()

    def check_completion(self):
        all_met = True
        for obj in self.objectives:
            if obj["type"] == "collect" or obj["type"] == "defeat":
                if obj["current_count"] < obj["count"]:
                    all_met = False
                    break
            elif obj["type"] == "reach":
                if not obj["completed"]:
                    all_met = False
                    break
        return all_met

    def is_reach_objective_completed(self):
        for obj in self.objectives:
            if obj["type"] == "reach":
                return obj["completed"]
        return False

    def update_display_objectives(self):
        self.display_objectives = []
        for obj in self.objectives:
            if obj["type"] == "collect" or obj["type"] == "defeat":
                status = f"{obj['current_count']}/{obj['count']}"
                self.display_objectives.append(f"{obj['description']} ({status})")
            elif obj["type"] == "reach":
                status = "DONE" if obj["completed"] else "PENDING"
                self.display_objectives.append(f"{obj['description']} ({status})")

    def get_display_objectives(self):
        return self.display_objectives


def main():
    game = Game()
    game.run()
    pygame.quit()

if __name__ == "__main__":
    main()
