
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
BLUE = (50, 150, 255)
DARK_BLUE = (0, 0, 100)
GREEN = (0, 200, 0)
LIGHT_GREEN = (100, 255, 100)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
CYAN = (0, 255, 255)
PURPLE = (128, 0, 128)
PINK = (255, 192, 203)

# Player properties
PLAYER_SPEED = 3
PLAYER_DASH_SPEED = 8
PLAYER_DASH_DURATION = 15  # frames
PLAYER_DASH_COOLDOWN = 30  # frames
PLAYER_SHELL_TUCK_DURATION = 30  # frames
PLAYER_SHELL_TUCK_COOLDOWN = 60  # frames
PLAYER_SONAR_RANGE = 150
PLAYER_SONAR_DURATION = 120 # frames

# Enemy properties
PUFFERFISH_SPEED = 1.5
PUFFERFISH_SPINE_SPEED = 5
PUFFERFISH_SPINE_DURATION = 60  # frames
JELLYFISH_SPEED = 1
JELLYFISH_SWIM_PATTERN_LENGTH = 100 # frames
SHARK_SPEED = 4
SHARK_SIGHT_RANGE = 200

# Powerup properties
KELP_BOOST_DURATION = 180  # frames
PEARL_SHIELD_DURATION = 120  # frames

# Game States
MENU = 0
PLAYING = 1
GAME_OVER = 2
LEVEL_COMPLETE = 3

# --- Classes ---

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, ORANGE, (10, 10), 10)
        pygame.draw.circle(self.image, BROWN, (10, 10), 8)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.speed = PLAYER_SPEED
        self.dash_speed = PLAYER_DASH_SPEED
        self.dash_timer = 0
        self.dash_cooldown_timer = 0
        self.is_dashing = False
        self.shell_tuck_timer = 0
        self.shell_tuck_cooldown_timer = 0
        self.is_shell_tucking = False
        self.sonar_timer = 0
        self.is_sonar_active = False
        self.sonar_radius = 0
        self.score = 0
        self.health = 3
        self.max_health = 3
        self.has_sonar = False

    def update(self, obstacles, hazards, enemies, currents):
        if self.dash_timer > 0:
            self.dash_timer -= 1
            if self.dash_timer == 0:
                self.is_dashing = False
                self.vel *= 0.5 # Slow down after dash
        else:
            self.dash_cooldown_timer -= 1

        if self.shell_tuck_timer > 0:
            self.shell_tuck_timer -= 1
            if self.shell_tuck_timer == 0:
                self.is_shell_tucking = False
                self.speed = PLAYER_SPEED # Reset speed after shell tuck
        else:
            self.shell_tuck_cooldown_timer -= 1

        if self.sonar_timer > 0:
            self.sonar_timer -= 1
            self.sonar_radius = PLAYER_SONAR_RANGE * (1 - (PLAYER_SONAR_DURATION - self.sonar_timer) / PLAYER_SONAR_DURATION)
            if self.sonar_timer == 0:
                self.is_sonar_active = False
                self.sonar_radius = 0
        else:
            self.is_sonar_active = False
            self.sonar_radius = 0

        keys = pygame.key.get_pressed()
        self.vel = pygame.math.Vector2(0, 0)

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vel.x = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vel.x = 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.vel.y = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.vel.y = 1

        if self.vel.length() > 0:
            self.vel.normalize_ip()

        if not self.is_dashing and not self.is_shell_tucking:
            self.pos += self.vel * self.speed
        elif self.is_dashing:
            self.pos += self.vel * self.dash_speed
        elif self.is_shell_tucking:
            self.pos += self.vel * (self.speed * 0.5) # Slower movement while tucking

        # Apply currents
        for current in currents:
            if self.rect.colliderect(current.rect):
                if current.direction == "up":
                    self.pos.y -= current.strength
                elif current.direction == "down":
                    self.pos.y += current.strength
                elif current.direction == "left":
                    self.pos.x -= current.strength
                elif current.direction == "right":
                    self.pos.x += current.strength

        self.rect.center = (int(self.pos.x), int(self.pos.y))

        # Keep player on screen
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)
        self.pos = pygame.math.Vector2(self.rect.center)

        # Collision with obstacles
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                if self.vel.x > 0 and self.rect.right > obstacle.rect.left and self.rect.left < obstacle.rect.left:
                    self.pos.x = obstacle.rect.left - self.rect.width / 2
                if self.vel.x < 0 and self.rect.left < obstacle.rect.right and self.rect.right > obstacle.rect.right:
                    self.pos.x = obstacle.rect.right + self.rect.width / 2
                if self.vel.y > 0 and self.rect.bottom > obstacle.rect.top and self.rect.top < obstacle.rect.top:
                    self.pos.y = obstacle.rect.top - self.rect.height / 2
                if self.vel.y < 0 and self.rect.top < obstacle.rect.bottom and self.rect.bottom > obstacle.rect.bottom:
                    self.pos.y = obstacle.rect.bottom + self.rect.height / 2
                self.rect.center = (int(self.pos.x), int(self.pos.y))

        # Collision with enemies
        if not self.is_shell_tucking:
            for enemy in enemies:
                if self.rect.colliderect(enemy.rect):
                    if isinstance(enemy, Pufferfish) and enemy.spines_active:
                        self.take_damage()
                        enemy.spines_active = False # Consume spines on hit
                    elif isinstance(enemy, Jellyfish):
                        self.take_damage()
                    elif isinstance(enemy, Shark):
                        self.take_damage()
                    elif isinstance(enemy, CuriousCrab):
                        self.take_damage() # Crabs also hurt on contact


    def dash(self):
        if not self.is_dashing and self.dash_cooldown_timer <= 0:
            self.is_dashing = True
            self.dash_timer = PLAYER_DASH_DURATION
            self.dash_cooldown_timer = PLAYER_DASH_COOLDOWN
            self.vel.normalize_ip() # Ensure dash direction is set

    def shell_tuck(self):
        if not self.is_shell_tucking and self.shell_tuck_cooldown_timer <= 0:
            self.is_shell_tucking = True
            self.shell_tuck_timer = PLAYER_SHELL_TUCK_DURATION
            self.shell_tuck_cooldown_timer = PLAYER_SHELL_TUCK_COOLDOWN
            self.speed *= 0.5 # Slow down movement
            self.vel = pygame.math.Vector2(0,0) # Stop movement during tuck

    def sonar_pulse(self):
        if self.has_sonar and self.sonar_timer <= 0 and not self.is_sonar_active:
            self.is_sonar_active = True
            self.sonar_timer = PLAYER_SONAR_DURATION
            self.sonar_radius = 0 # Will be calculated in update

    def take_damage(self):
        if not self.is_shell_tucking:
            self.health -= 1
            if self.health < 0:
                self.health = 0

    def heal(self):
        if self.health < self.max_health:
            self.health += 1

    def add_score(self, amount):
        self.score += amount

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color, type):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.type = type

class Hazard(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color, type, direction, strength=1.5):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.type = type
        self.direction = direction
        self.strength = strength

class Powerup(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.type = type
        if type == "coin":
            self.image = pygame.Surface((15, 15))
            pygame.draw.circle(self.image, YELLOW, (7.5, 7.5), 7.5)
            self.rect = self.image.get_rect(center=(x, y))
        elif type == "health":
            self.image = pygame.Surface((20, 20))
            pygame.draw.circle(self.image, RED, (10, 10), 10)
            pygame.draw.line(self.image, WHITE, (10, 5), (10, 15), 2)
            pygame.draw.line(self.image, WHITE, (5, 10), (15, 10), 2)
            self.rect = self.image.get_rect(center=(x, y))
        elif type == "kelp_boost":
            self.image = pygame.Surface((25, 25))
            pygame.draw.rect(self.image, GREEN, (0, 0, 25, 25))
            pygame.draw.rect(self.image, LIGHT_GREEN, (5, 5, 15, 15))
            self.rect = self.image.get_rect(center=(x, y))
        elif type == "pearl_shield":
            self.image = pygame.Surface((20, 20))
            pygame.draw.circle(self.image, PINK, (10, 10), 10)
            self.rect = self.image.get_rect(center=(x, y))

class Pufferfish(pygame.sprite.Sprite):
    def __init__(self, x, y, patrol_path):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 140, 0), (15, 15), 15)
        pygame.draw.circle(self.image, (200, 110, 0), (15, 15), 12)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        self.patrol_path = [pygame.math.Vector2(p) for p in patrol_path]
        self.current_path_index = 0
        self.speed = PUFFERFISH_SPEED
        self.behavior = "wandering" # "wandering", "patrolling"
        self.spines = []
        self.spines_active = False
        self.swell_timer = 0
        self.swell_duration = 30
        self.attack_cooldown = 120
        self.attack_timer = 0

    def update(self, player, obstacles):
        if self.attack_timer > 0:
            self.attack_timer -= 1

        if self.behavior == "wandering":
            # Simple wandering behavior
            if random.randint(0, 100) < 5:
                self.vel = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * self.speed
            self.pos += self.vel
            self.rect.center = (int(self.pos.x), int(self.pos.y))

            # Bounce off screen edges and obstacles
            if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
                self.pos.x -= self.vel.x * 2 # Reverse direction
                self.vel.x *= -1
            if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
                self.pos.y -= self.vel.y * 2 # Reverse direction
                self.vel.y *= -1
            for obstacle in obstacles:
                if self.rect.colliderect(obstacle.rect):
                    if self.vel.x > 0 and self.rect.right > obstacle.rect.left:
                        self.pos.x = obstacle.rect.left - self.rect.width / 2
                        self.vel.x *= -1
                    if self.vel.x < 0 and self.rect.left < obstacle.rect.right:
                        self.pos.x = obstacle.rect.right + self.rect.width / 2
                        self.vel.x *= -1
                    if self.vel.y > 0 and self.rect.bottom > obstacle.rect.top:
                        self.pos.y = obstacle.rect.top - self.rect.height / 2
                        self.vel.y *= -1
                    if self.vel.y < 0 and self.rect.top < obstacle.rect.bottom:
                        self.pos.y = obstacle.rect.bottom + self.rect.height / 2
                        self.vel.y *= -1
            self.rect.center = (int(self.pos.x), int(self.pos.y))

        elif self.behavior == "patrolling":
            target_pos = self.patrol_path[self.current_path_index]
            direction = target_pos - self.pos
            if direction.length() > 1:
                direction.normalize_ip()
                self.pos += direction * self.speed
            else:
                self.current_path_index = (self.current_path_index + 1) % len(self.patrol_path)
            self.rect.center = (int(self.pos.x), int(self.pos.y))

        # Attack logic
        distance_to_player = self.pos.distance_to(player.pos)
        if distance_to_player < 100 and self.attack_timer <= 0:
            self.swell_timer = self.swell_duration
            self.attack_timer = self.attack_cooldown

        if self.swell_timer > 0:
            self.swell_timer -= 1
            if self.swell_timer == 0:
                self.shoot_spines(player)

        for spine in self.spines[:]:
            spine.update()
            if not 0 <= spine.rect.centerx < SCREEN_WIDTH or not 0 <= spine.rect.centery < SCREEN_HEIGHT:
                self.spines.remove(spine)
            if player.rect.colliderect(spine.rect) and not player.is_shell_tucking:
                player.take_damage()
                self.spines.remove(spine)


    def shoot_spines(self, player):
        self.spines_active = True
        for _ in range(5): # Shoot multiple spines
            angle = math.atan2(player.pos.y - self.pos.y, player.pos.x - self.pos.x)
            offset_x = random.uniform(-15, 15)
            offset_y = random.uniform(-15, 15)
            spine_vel = pygame.math.Vector2(math.cos(angle + offset_x/50), math.sin(angle + offset_y/50)) * PUFFERFISH_SPINE_SPEED
            self.spines.append(PufferfishSpine(self.rect.centerx, self.rect.centery, spine_vel))

class PufferfishSpine(pygame.sprite.Sprite):
    def __init__(self, x, y, vel):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = vel
        self.timer = PUFFERFISH_SPINE_DURATION

    def update(self):
        self.rect.move_ip(self.vel)
        self.timer -= 1
        if self.timer <= 0:
            self.kill()

class Jellyfish(pygame.sprite.Sprite):
    def __init__(self, x, y, patrol_path):
        super().__init__()
        self.image = pygame.Surface((25, 40), pygame.SRCALPHA)
        pygame.draw.circle(self.image, CYAN, (12.5, 15), 12.5)
        pygame.draw.line(self.image, CYAN, (12.5, 25), (12.5, 40), 3)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        self.patrol_path = [pygame.math.Vector2(p) for p in patrol_path]
        self.current_path_index = 0
        self.speed = JELLYFISH_SPEED
        self.swim_timer = 0

    def update(self):
        if self.swim_timer < JELLYFISH_SWIM_PATTERN_LENGTH:
            target_pos = self.patrol_path[self.current_path_index]
            direction = target_pos - self.pos
            if direction.length() > 1:
                direction.normalize_ip()
                self.pos += direction * self.speed
            else:
                self.current_path_index = (self.current_path_index + 1) % len(self.patrol_path)
            self.swim_timer += 1
        else:
            self.swim_timer = 0
            self.current_path_index = random.randint(0, len(self.patrol_path) - 1) # Move to a random point for variation

        self.rect.center = (int(self.pos.x), int(self.pos.y))

class Shark(pygame.sprite.Sprite):
    def __init__(self, x, y, patrol_path):
        super().__init__()
        self.image = pygame.Surface((50, 20), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, GRAY, [(0, 10), (50, 10), (45, 0), (50, 20)])
        pygame.draw.polygon(self.image, (150, 150, 150), [(0, 10), (40, 10), (45, 5), (40, 15)])
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        self.patrol_path = [pygame.math.Vector2(p) for p in patrol_path]
        self.current_path_index = 0
        self.speed = SHARK_SPEED
        self.chase_mode = False
        self.chase_target = None
        self.sight_range = SHARK_SIGHT_RANGE

    def update(self, player):
        if not self.chase_mode:
            target_pos = self.patrol_path[self.current_path_index]
            direction = target_pos - self.pos
            if direction.length() > 1:
                direction.normalize_ip()
                self.pos += direction * self.speed
            else:
                self.current_path_index = (self.current_path_index + 1) % len(self.patrol_path)
            self.rect.center = (int(self.pos.x), int(self.pos.y))

            # Check for player in sight
            if self.pos.distance_to(player.pos) < self.sight_range:
                self.chase_mode = True
                self.chase_target = player
        else:
            if self.chase_target:
                direction = self.chase_target.pos - self.pos
                if direction.length() > 1:
                    direction.normalize_ip()
                    self.pos += direction * self.speed
                self.rect.center = (int(self.pos.x), int(self.pos.y))

                # If player is out of sight, return to patrol
                if self.pos.distance_to(self.chase_target.pos) > self.sight_range * 1.5:
                    self.chase_mode = False
                    self.chase_target = None
                    self.current_path_index = random.randint(0, len(self.patrol_path) - 1) # Go to random patrol point
            else:
                self.chase_mode = False
                self.current_path_index = random.randint(0, len(self.patrol_path) - 1)

class CuriousCrab(pygame.sprite.Sprite):
    def __init__(self, x, y, patrol_path):
        super().__init__()
        self.image = pygame.Surface((25, 20))
        self.image.fill(BROWN)
        pygame.draw.circle(self.image, (160, 82, 45), (12.5, 10), 10)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        self.patrol_path = [pygame.math.Vector2(p) for p in patrol_path]
        self.current_path_index = 0
        self.speed = 1.5

    def update(self):
        target_pos = self.patrol_path[self.current_path_index]
        direction = target_pos - self.pos
        if direction.length() > 1:
            direction.normalize_ip()
            self.pos += direction * self.speed
        else:
            self.current_path_index = (self.current_path_index + 1) % len(self.patrol_path)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Shell Shocked Splashdown")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)
        self.game_state = MENU

        self.player = None
        self.obstacles = pygame.sprite.Group()
        self.hazards = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.currents = pygame.sprite.Group()

        self.level_data = self.load_level(1)
        self.current_level = 1
        self.max_levels = 3

        self.kelp_boost_active = False
        self.kelp_boost_timer = 0
        self.pearl_shield_active = False
        self.pearl_shield_timer = 0

        self.objective_progress = {}

    def load_level(self, level_num):
        # Level data dictionary - can be expanded for more levels
        levels = {
            1: {
                "size": {"width": 800, "height": 600},
                "spawn_points": [{"x": 100, "y": 100, "type": "player"}],
                "obstacles": [
                    {"x": 250, "y": 180, "width": 70, "height": 50, "type": "coral_cluster"},
                    {"x": 500, "y": 250, "width": 60, "height": 60, "type": "rock_formation"},
                    {"x": 650, "y": 400, "width": 80, "height": 40, "type": "seaweed_patch"},
                    {"x": 150, "y": 400, "width": 40, "height": 70, "type": "urchin_bed"}
                ],
                "hazards": [
                    {"x": 400, "y": 100, "width": 200, "height": 30, "type": "gentle_current", "direction": "down", "strength": 1.5},
                    {"x": 700, "y": 300, "width": 30, "height": 200, "type": "gentle_current", "direction": "left", "strength": 1.5}
                ],
                "powerups": [
                    {"x": 300, "y": 150, "type": "coin"},
                    {"x": 580, "y": 180, "type": "coin"},
                    {"x": 120, "y": 350, "type": "coin"},
                    {"x": 450, "y": 450, "type": "coin"},
                    {"x": 700, "y": 550, "type": "coin"},
                    {"x": 350, "y": 500, "type": "health"},
                    {"x": 50, "y": 50, "type": "kelp_boost"},
                    {"x": 750, "y": 50, "type": "pearl_shield"}
                ],
                "enemies": [
                    {"x": 400, "y": 300, "type": "slow_pufferfish", "patrol_path": [[400, 300], [450, 300], [450, 350], [400, 350]], "behavior": "wandering"},
                    {"x": 600, "y": 150, "type": "curious_crab", "patrol_path": [[600, 150], [630, 150]], "behavior": "patrolling"},
                    {"x": 180, "y": 500, "type": "slow_pufferfish", "patrol_path": [[180, 500], [220, 500], [220, 470], [180, 470]], "behavior": "wandering"}
                ],
                "objectives": [
                    {"type": "collect", "target": "coin", "count": 5},
                    {"type": "defeat", "target": "enemy", "count": 3}
                ],
                "difficulty": "easy",
                "time_limit": 120
            },
            2: {
                "size": {"width": 1000, "height": 800},
                "spawn_points": [{"x": 50, "y": 50, "type": "player"}],
                "obstacles": [
                    {"x": 200, "y": 200, "width": 150, "height": 100, "type": "coral_reef"},
                    {"x": 700, "y": 400, "width": 100, "height": 100, "type": "rock_formation"},
                    {"x": 300, "y": 600, "width": 120, "height": 60, "type": "seaweed_forest"},
                    {"x": 800, "y": 150, "width": 80, "height": 80, "type": "urchin_patch"}
                ],
                "hazards": [
                    {"x": 0, "y": 300, "width": 1000, "height": 50, "type": "strong_current", "direction": "right", "strength": 2},
                    {"x": 500, "y": 0, "width": 50, "height": 800, "type": "strong_current", "direction": "down", "strength": 2}
                ],
                "powerups": [
                    {"x": 150, "y": 250, "type": "coin"},
                    {"x": 600, "y": 300, "type": "coin"},
                    {"x": 400, "y": 550, "type": "coin"},
                    {"x": 900, "y": 700, "type": "coin"},
                    {"x": 50, "y": 750, "type": "coin"},
                    {"x": 750, "y": 550, "type": "health"},
                    {"x": 100, "y": 100, "type": "kelp_boost"},
                    {"x": 900, "y": 100, "type": "pearl_shield"}
                ],
                "enemies": [
                    {"x": 500, "y": 250, "type": "jellyfish", "patrol_path": [[500, 250], [550, 280], [500, 310], [450, 280]], "behavior": "patrolling"},
                    {"x": 850, "y": 300, "type": "shark", "patrol_path": [[850, 300], [750, 350], [850, 400]], "behavior": "patrolling"},
                    {"x": 350, "y": 450, "type": "pufferfish", "patrol_path": [[350, 450], [400, 450]], "behavior": "wandering"},
                    {"x": 700, "y": 600, "type": "jellyfish", "patrol_path": [[700, 600], [730, 620], [700, 640], [670, 620]], "behavior": "patrolling"}
                ],
                "objectives": [
                    {"type": "collect", "target": "coin", "count": 5},
                    {"type": "defeat", "target": "enemy", "count": 4}
                ],
                "difficulty": "medium",
                "time_limit": 180
            },
            3: { # Nesting Beach
                "size": {"width": 800, "height": 600},
                "spawn_points": [{"x": 50, "y": 300, "type": "player"}],
                "obstacles": [
                    {"x": 150, "y": 100, "width": 100, "height": 50, "type": "rock_outcropping"},
                    {"x": 300, "y": 400, "width": 80, "height": 120, "type": "seaweed_bed"},
                    {"x": 600, "y": 200, "width": 70, "height": 70, "type": "coral_formation"}
                ],
                "hazards": [
                    {"x": 0, "y": 250, "width": 800, "height": 50, "type": "strong_current", "direction": "right", "strength": 3}
                ],
                "powerups": [
                    {"x": 200, "y": 150, "type": "coin"},
                    {"x": 500, "y": 300, "type": "coin"},
                    {"x": 700, "y": 450, "type": "coin"},
                    {"x": 400, "y": 50, "type": "health"},
                    {"x": 100, "y": 500, "type": "kelp_boost"},
                    {"x": 700, "y": 100, "type": "pearl_shield"}
                ],
                "enemies": [
                    {"x": 400, "y": 200, "type": "shark", "patrol_path": [[400, 200], [500, 250], [400, 300]], "behavior": "patrolling"},
                    {"x": 250, "y": 350, "type": "jellyfish", "patrol_path": [[250, 350], [280, 380], [250, 410], [220, 380]], "behavior": "patrolling"},
                    {"x": 650, "y": 350, "type": "pufferfish", "patrol_path": [[650, 350], [700, 350]], "behavior": "wandering"},
                    {"x": 550, "y": 500, "type": "shark", "patrol_path": [[550, 500], [600, 550]], "behavior": "patrolling"}
                ],
                "objectives": [
                    {"type": "reach_destination", "target": "nesting_beach"},
                    {"type": "collect", "target": "coin", "count": 3},
                    {"type": "defeat", "target": "enemy", "count": 4}
                ],
                "difficulty": "hard",
                "time_limit": 150
            }
        }
        return levels.get(level_num)

    def reset_level(self):
        self.player = None
        self.obstacles.empty()
        self.hazards.empty()
        self.powerups.empty()
        self.enemies.empty()
        self.all_sprites.empty()
        self.currents.empty()
        self.objective_progress = {}

        self.kelp_boost_active = False
        self.kelp_boost_timer = 0
        self.pearl_shield_active = False
        self.pearl_shield_timer = 0

    def setup_level(self):
        level_data = self.level_data
        SCREEN_WIDTH = level_data["size"]["width"]
        SCREEN_HEIGHT = level_data["size"]["height"]

        # Player
        spawn_point = level_data["spawn_points"][0]
        self.player = Player(spawn_point["x"], spawn_point["y"])
        self.all_sprites.add(self.player)

        # Obstacles
        for obs_data in level_data["obstacles"]:
            color = GRAY
            if obs_data["type"] == "coral_cluster":
                color = (255, 100, 100)
            elif obs_data["type"] == "rock_formation":
                color = BROWN
            elif obs_data["type"] == "seaweed_patch":
                color = GREEN
            elif obs_data["type"] == "urchin_bed":
                color = PURPLE
            elif obs_data["type"] == "coral_reef":
                color = (255, 100, 100)
            elif obs_data["type"] == "seaweed_forest":
                color = GREEN
            elif obs_data["type"] == "urchin_patch":
                color = PURPLE
            elif obs_data["type"] == "rock_outcropping":
                color = BROWN
            elif obs_data["type"] == "seaweed_bed":
                color = GREEN
            elif obs_data["type"] == "coral_formation":
                color = (255, 100, 100)


            obstacle = Obstacle(obs_data["x"], obs_data["y"], obs_data["width"], obs_data["height"], color, obs_data["type"])
            self.obstacles.add(obstacle)
            self.all_sprites.add(obstacle)

        # Hazards (Currents)
        for haz_data in level_data["hazards"]:
            color = CYAN
            if haz_data["type"] == "gentle_current":
                color = (100, 150, 255)
            elif haz_data["type"] == "strong_current":
                color = (50, 100, 200)

            hazard = Hazard(haz_data["x"], haz_data["y"], haz_data["width"], haz_data["height"], color, haz_data["type"], haz_data["direction"], haz_data["strength"])
            self.hazards.add(hazard)
            self.currents.add(hazard)
            self.all_sprites.add(hazard)


        # Powerups
        for pow_data in level_data["powerups"]:
            powerup = Powerup(pow_data["x"], pow_data["y"], pow_data["type"])
            self.powerups.add(powerup)
            self.all_sprites.add(powerup)

        # Enemies
        for ene_data in level_data["enemies"]:
            enemy = None
            if ene_data["type"] == "slow_pufferfish":
                enemy = Pufferfish(ene_data["x"], ene_data["y"], ene_data["patrol_path"])
                enemy.behavior = ene_data["behavior"]
            elif ene_data["type"] == "jellyfish":
                enemy = Jellyfish(ene_data["x"], ene_data["y"], ene_data["patrol_path"])
            elif ene_data["type"] == "shark":
                enemy = Shark(ene_data["x"], ene_data["y"], ene_data["patrol_path"])
            elif ene_data["type"] == "curious_crab":
                enemy = CuriousCrab(ene_data["x"], ene_data["y"], ene_data["patrol_path"])

            if enemy:
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)

        # Objectives
        for obj in level_data["objectives"]:
            self.objective_progress[obj["type"] + "_" + obj.get("target", "")] = obj["count"] if "count" in obj else obj["target"]

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if self.game_state == MENU:
                    if event.key == pygame.K_RETURN:
                        self.game_state = PLAYING
                        self.reset_level()
                        self.setup_level()
                        self.start_time = pygame.time.get_ticks()
                    if event.key == pygame.K_ESCAPE:
                        return False
                elif self.game_state == PLAYING:
                    if event.key == pygame.K_SPACE:
                        self.player.dash()
                    if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                        self.player.shell_tuck()
                    if event.key == pygame.K_x:
                        self.player.sonar_pulse()
                    if event.key == pygame.K_RETURN: # For next level
                        if self.check_level_complete():
                            self.next_level()
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = MENU
                elif self.game_state == GAME_OVER or self.game_state == LEVEL_COMPLETE:
                    if event.key == pygame.K_RETURN:
                        self.game_state = MENU
                        self.reset_level()
                    if event.key == pygame.K_ESCAPE:
                        return False
        return True

    def update_powerups(self):
        if self.kelp_boost_active:
            self.kelp_boost_timer -= 1
            if self.kelp_boost_timer <= 0:
                self.kelp_boost_active = False
                self.player.speed = PLAYER_SPEED

        if self.pearl_shield_active:
            self.pearl_shield_timer -= 1
            if self.pearl_shield_timer <= 0:
                self.pearl_shield_active = False

    def update_game_state(self):
        if self.game_state == PLAYING:
            if self.player.health <= 0:
                self.game_state = GAME_OVER
                return

            if self.check_level_complete():
                self.game_state = LEVEL_COMPLETE
                return

            elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
            if elapsed_time > self.level_data["time_limit"]:
                self.game_state = GAME_OVER # Time out
                return

            self.update_powerups()

            self.player.update(self.obstacles, self.hazards, self.enemies, self.currents)
            self.enemies.update(self.player) # Enemies need player for AI
            self.all_sprites.update(self.obstacles, self.hazards, self.enemies, self.currents) # Pass relevant groups if needed

            # Collision with powerups
            for powerup in pygame.sprite.spritecollide(self.player, self.powerups, True):
                if powerup.type == "coin":
                    self.player.add_score(10)
                    self.update_objective("collect_coin", 1)
                elif powerup.type == "health":
                    self.player.heal()
                elif powerup.type == "kelp_boost":
                    self.kelp_boost_active = True
                    self.kelp_boost_timer = KELP_BOOST_DURATION
                    self.player.speed *= 1.5 # Temporarily increase speed
                elif powerup.type == "pearl_shield":
                    self.pearl_shield_active = True
                    self.pearl_shield_timer = PEARL_SHIELD_DURATION


            # Enemy Spine collision handling (moved to Pufferfish update)

            # Objective tracking
            for enemy in self.enemies:
                if enemy in self.enemies: # Check if enemy is still alive
                    pass # Already handled by collecting/defeating

            # Check for defeat objectives
            for obj_key, obj_val in self.objective_progress.items():
                if "defeat_enemy" in obj_key and isinstance(obj_val, int) and obj_val <= 0:
                    self.objective_progress[obj_key] = 0 # Mark as completed

            # Check for reach destination objective
            if "reach_destination_nesting_beach" in self.objective_progress:
                nesting_beach_rect = pygame.Rect(self.level_data["size"]["width"] - 50, 0, 50, self.level_data["size"]["height"]) # Example nesting beach area
                if self.player.rect.colliderect(nesting_beach_rect):
                    self.update_objective("reach_destination_nesting_beach", 1)


    def update_objective(self, obj_type, amount):
        if obj_type in self.objective_progress:
            if isinstance(self.objective_progress[obj_type], int):
                self.objective_progress[obj_type] -= amount
                if self.objective_progress[obj_type] < 0:
                    self.objective_progress[obj_type] = 0

    def check_level_complete(self):
        all_objectives_met = True
        if not self.objective_progress: # If no specific objectives, just reaching the end is enough
            return True

        for obj_key, obj_val in self.objective_progress.items():
            if isinstance(obj_val, int) and obj_val > 0:
                all_objectives_met = False
                break
            elif isinstance(obj_val, str) and obj_val != "nesting_beach": # For reach destination type
                all_objectives_met = False
                break
        return all_objectives_met

    def next_level(self):
        self.current_level += 1
        if self.current_level <= self.max_levels:
            self.reset_level()
            self.level_data = self.load_level(self.current_level)
            self.setup_level()
            self.game_state = PLAYING
            self.start_time = pygame.time.get_ticks()
        else:
            # Game completed
            pass # Transition to a game completion screen or back to menu

    def draw(self):
        self.screen.fill(BLUE) # Background for ocean

        if self.game_state == MENU:
            self.draw_menu()
        elif self.game_state == PLAYING:
            self.draw_playing()
        elif self.game_state == GAME_OVER:
            self.draw_game_over()
        elif self.game_state == LEVEL_COMPLETE:
            self.draw_level_complete()

        pygame.display.flip()

    def draw_menu(self):
        title_text = self.large_font.render("Shell Shocked Splashdown", True, WHITE)
        start_text = self.font.render("Press ENTER to Start", True, WHITE)
        quit_text = self.font.render("Press ESC to Quit", True, WHITE)

        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 150))
        self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 300))
        self.screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, 350))

    def draw_playing(self):
        level_data = self.level_data
        self.screen.fill(BLUE) # Default ocean background

        # Draw background elements based on level theme
        if self.current_level == 1: # Sandy Shores (Beach)
            self.screen.fill((240, 230, 140)) # Sandy color
            pygame.draw.rect(self.screen, (139, 69, 19), (0, 0, SCREEN_WIDTH, 50)) # Beach
            for i in range(0, SCREEN_WIDTH, 40):
                pygame.draw.line(self.screen, (255, 255, 150), (i, 50), (i+20, 70), 2) # Waves

        elif self.current_level == 2: # Coral Currents (Ocean Depths)
            self.screen.fill(DARK_BLUE)
            # Add some bioluminescent flora (simple pulsing circles)
            for _ in range(10):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                radius = random.randint(5, 15)
                color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
                pygame.draw.circle(self.screen, color, (x, y), radius)

        elif self.current_level == 3: # Return to the Nest (Returning Beach)
            self.screen.fill((240, 230, 140)) # Sandy color
            pygame.draw.rect(self.screen, (139, 69, 19), (0, 0, SCREEN_WIDTH, 50)) # Beach
            for i in range(0, SCREEN_WIDTH, 40):
                pygame.draw.line(self.screen, (255, 255, 150), (i, 50), (i+20, 70), 2) # Waves
            pygame.draw.rect(self.screen, (100, 80, 50), (SCREEN_WIDTH - 100, 0, 100, SCREEN_HEIGHT)) # Nesting beach area (example)


        # Draw sprites
        self.all_sprites.draw(self.screen)

        # Draw currents
        for hazard in self.currents:
            if hazard.type == "gentle_current" or hazard.type == "strong_current":
                alpha = 100
                if hazard.type == "strong_current":
                    alpha = 150
                overlay = pygame.Surface((hazard.rect.width, hazard.rect.height), pygame.SRCALPHA)
                overlay.fill((255, 255, 255, alpha)) # White with transparency
                self.screen.blit(overlay, (hazard.rect.x, hazard.rect.y))

        # Draw Pufferfish spines
        for enemy in self.enemies:
            if isinstance(enemy, Pufferfish):
                for spine in enemy.spines:
                    self.screen.blit(spine.image, spine.rect)

        # Draw Sonar Pulse
        if self.player.is_sonar_active and self.player.sonar_radius > 0:
            sonar_surface = pygame.Surface((self.player.sonar_radius * 2, self.player.sonar_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(sonar_surface, (0, 200, 200, 100), (self.player.sonar_radius, self.player.sonar_radius), self.player.sonar_radius)
            self.screen.blit(sonar_surface, (self.player.rect.centerx - self.player.sonar_radius, self.player.rect.centery - self.player.sonar_radius))


        # Draw UI
        self.draw_ui()

    def draw_ui(self):
        # Score
        score_text = self.font.render(f"Score: {self.player.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Health
        for i in range(self.player.max_health):
            pygame.draw.circle(self.screen, RED, (SCREEN_WIDTH - 40 - i * 30, 25), 10)
            if i >= self.player.health:
                pygame.draw.line(self.screen, WHITE, (SCREEN_WIDTH - 45 - i * 30, 20), (SCREEN_WIDTH - 35 - i * 30, 30), 2)
                pygame.draw.line(self.screen, WHITE, (SCREEN_WIDTH - 35 - i * 30, 20), (SCREEN_WIDTH - 45 - i * 30, 30), 2)

        # Time remaining
        elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
        time_left = max(0, self.level_data["time_limit"] - elapsed_time)
        time_text = self.font.render(f"Time: {int(time_left)}", True, WHITE)
        self.screen.blit(time_text, (SCREEN_WIDTH - time_text.get_width() - 10, 10))

        # Objectives
        y_offset = 50
        for obj_key, obj_val in self.objective_progress.items():
            text = ""
            if "collect" in obj_key:
                target = obj_key.split("_")[1]
                text = f"Collect {target}: {obj_val}"
            elif "defeat" in obj_key:
                target = obj_key.split("_")[1]
                text = f"Defeat {target}: {obj_val}"
            elif "reach_destination" in obj_key:
                target = obj_key.split("_")[2]
                text = f"Reach {target}: {obj_val if isinstance(obj_val, int) else ''}"

            if text:
                obj_text = self.font.render(text, True, WHITE)
                self.screen.blit(obj_text, (10, y_offset))
                y_offset += 30

        # Powerup indicators
        if self.kelp_boost_active:
            boost_text = self.font.render("Kelp Boost", True, LIGHT_GREEN)
            self.screen.blit(boost_text, (SCREEN_WIDTH // 2 - boost_text.get_width() // 2, 10))
        if self.pearl_shield_active:
            shield_text = self.font.render("Shielded", True, PINK)
            self.screen.blit(shield_text, (SCREEN_WIDTH // 2 - shield_text.get_width() // 2, 40))

    def draw_game_over(self):
        game_over_text = self.large_font.render("Game Over", True, RED)
        final_score_text = self.font.render(f"Final Score: {self.player.score}", True, WHITE)
        restart_text = self.font.render("Press ENTER to return to Menu", True, WHITE)

        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 150))
        self.screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, 300))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 350))

    def draw_level_complete(self):
        level_complete_text = self.large_font.render(f"Level {self.current_level} Complete!", True, GREEN)
        score_text = self.font.render(f"Score: {self.player.score}", True, WHITE)
        next_level_text = self.font.render("Press ENTER for Next Level", True, WHITE)
        menu_text = self.font.render("Press ESC to return to Menu", True, WHITE)


        self.screen.blit(level_complete_text, (SCREEN_WIDTH // 2 - level_complete_text.get_width() // 2, 150))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 300))

        if self.current_level < self.max_levels:
            self.screen.blit(next_level_text, (SCREEN_WIDTH // 2 - next_level_text.get_width() // 2, 350))
        else:
            final_score_text = self.font.render("You completed the game!", True, YELLOW)
            self.screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, 350))

        self.screen.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2, 400))


    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update_game_state()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
