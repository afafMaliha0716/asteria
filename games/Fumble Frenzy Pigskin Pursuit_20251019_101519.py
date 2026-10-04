
# --- TEMPLATE: A_CORE_SETUP ---
import pygame
import sys

# --- Core Setup ---
pygame.init()

# --- Constants ---
# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Color definitions (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# --- LLM_INJECT_CUSTOM_CONSTANTS ---
# Game-specific colors
PIGSKIN_COLOR = (255, 220, 150)  # Pastry-like
ENDZONE_COLOR = (100, 200, 100)  # Green field
WALL_COLOR = (150, 75, 0)       # Brown for walls
CRATE_COLOR = (120, 60, 0)      # Darker brown for crates
ROCK_COLOR = (100, 100, 100)    # Grey for rocks
TREE_COLOR = (34, 139, 34)      # Forest green for trees
ENEMY_HAMBURGLAR_COLOR = (200, 50, 50) # Reddish-brown
ENEMY_SAUSAGE_COLOR = (255, 100, 0)   # Orange-red
POWERUP_HEALTH_COLOR = (255, 200, 200) # Pinkish, like sprinkles
POWERUP_SPEED_COLOR = (0, 255, 255)    # Cyan for speed burst
PLAYER_COLOR = (0, 0, 255)             # Default player color
TACKLE_COLOR = (255, 255, 0)           # Yellow for tackle effect
PIGSKIN_THROW_COLOR = (200, 200, 255)  # Light blue for throw trajectory
STICKY_PATCH_COLOR = (150, 100, 200) # Gooey Gummy Bear sticky patch color

# Player and Ability Constants
PLAYER_BASE_SPEED = 4
PLAYER_DASH_SPEED_MULTIPLIER = 2.0
PLAYER_DASH_DURATION_MS = 150
PLAYER_DASH_COOLDOWN_MS = 1500
PLAYER_TACKLE_RANGE = 70 # Distance from player center
PLAYER_TACKLE_WIDTH = 60 # Width of tackle hitbox
PLAYER_TACKLE_DURATION_MS = 200
PLAYER_TACKLE_COOLDOWN_MS = 1000
PIGSKIN_THROW_SPEED = 8
PIGSKIN_THROW_COOLDOWN_MS = 500
PLAYER_MAX_HP = 100

# Enemy Constants
ENEMY_HAMBURGLAR_HP = 30
ENEMY_HAMBURGLAR_SPEED = 3
ENEMY_SAUSAGE_HP = 20
ENEMY_SAUSAGE_SPEED = 5
ENEMY_SAUSAGE_ROLL_DURATION_MS = 1000
ENEMY_STUN_DURATION_MS = 1500
ENEMY_DAMAGE_PLAYER = 10 # Damage an enemy inflicts on player
GOOEY_GUMMY_BEAR_HP = 40
GOOEY_GUMMY_BEAR_SPEED = 2
STICKY_PATCH_DURATION_MS = 5000
STICKY_PATCH_SLOW_FACTOR = 0.5 # Player speed is multiplied by this

# Powerup Constants
POWERUP_SPRINKLE_SPEED_DURATION_MS = 5000
POWERUP_WHIPPED_CREAM_SHIELD_DURATION_MS = 3000
POWERUP_EXTRA_CHEESE_TOSS_DURATION_MS = 7000

# Scoring Constants
SCORE_TOUCHDOWN = 6
SCORE_FUMBLE_RECOVERY = 2
SCORE_COMBO_TACKLE_PER_ENEMY = 1

# Game Object Sizes (default for basic shapes)
PLAYER_SIZE = 40
PIGSKIN_SIZE = 30
ENEMY_SIZE = 45
TARGET_ZONE_SIZE = 80
POWERUP_SIZE = 25
# --- END LLM_INJECT_CUSTOM_CONSTANTS ---

# --- Initialization ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# --- LLM_INJECT_GAME_TITLE_CAPTION ---
pygame.display.set_caption("Fumble Frenzy: Pigskin Pursuit")
# --- END LLM_INJECT_GAME_TITLE_CAPTION ---
clock = pygame.time.Clock()

# --- Game Variables ---
# --- LLM_INJECT_INITIAL_GAME_VARIABLES ---
score = 0
current_level_num = 1
game_over = False
level_timer_start_time = 0
level_time_limit_seconds = 180 # From Level 1 design

# Placeholder for actual game state management (will be handled by F_GAME_STATES more robustly)
game_is_running = True # Simple boolean for this template, not full state machine
# --- END LLM_INJECT_INITIAL_GAME_VARIABLES ---

# --- LLM_INJECT_PLACEHOLDER_OBJECT_REPLACEMENT ---
# The original placeholder objects and their drawing/update are removed
# as actual game objects will be managed by classes in other templates.
# --- END LLM_INJECT_PLACEHOLDER_OBJECT_REPLACEMENT ---

# --- Main Game Loop ---
running = True
while running:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Optional: Handle other inputs like key presses (if not using continuous movement)
        # if event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_SPACE:
        #         print("Space bar pressed!")

    # 2. Update Game Logic (This is where movement, collision, etc., would go)
    # In this template, we just keep the placeholder in place
    pass

    # 3. Drawing
    screen.fill(BLACK) # Clear the screen
    
    # Draw a placeholder object
    # Removed as per LLM_INJECT_PLACEHOLDER_OBJECT_REPLACEMENT
    
    # Update the full display surface to the screen
    pygame.display.flip()

    # 4. Cap the frame rate
    clock.tick(FPS)

# --- Cleanup ---
pygame.quit()
sys.exit()


# --- TEMPLATE: D_HEALTH_DAMAGE ---
import pygame
import math # Needed for vector math in Player/Pigskin throw

# --- Constants & Initialization (Assumed from A) ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
FPS = 60
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# --- Game-specific Constants (Duplicated for template isolation, would be shared in a full game) ---
PIGSKIN_COLOR = (255, 220, 150)
ENDZONE_COLOR = (100, 200, 100)
WALL_COLOR = (150, 75, 0)
CRATE_COLOR = (120, 60, 0)
ROCK_COLOR = (100, 100, 100)
TREE_COLOR = (34, 139, 34)
ENEMY_HAMBURGLAR_COLOR = (200, 50, 50)
ENEMY_SAUSAGE_COLOR = (255, 100, 0)
POWERUP_HEALTH_COLOR = (255, 200, 200)
POWERUP_SPEED_COLOR = (0, 255, 255)
PLAYER_COLOR = (0, 0, 255)
TACKLE_COLOR = (255, 255, 0)
PIGSKIN_THROW_COLOR = (200, 200, 255)
STICKY_PATCH_COLOR = (150, 100, 200)

PLAYER_BASE_SPEED = 4
PLAYER_DASH_SPEED_MULTIPLIER = 2.0
PLAYER_DASH_DURATION_MS = 150
PLAYER_DASH_COOLDOWN_MS = 1500
PLAYER_TACKLE_RANGE = 70
PLAYER_TACKLE_WIDTH = 60
PLAYER_TACKLE_DURATION_MS = 200
PLAYER_TACKLE_COOLDOWN_MS = 1000
PIGSKIN_THROW_SPEED = 8
PIGSKIN_THROW_COOLDOWN_MS = 500
PLAYER_MAX_HP = 100

ENEMY_HAMBURGLAR_HP = 30
ENEMY_HAMBURGLAR_SPEED = 3
ENEMY_SAUSAGE_HP = 20
ENEMY_SAUSAGE_SPEED = 5
ENEMY_SAUSAGE_ROLL_DURATION_MS = 1000
ENEMY_STUN_DURATION_MS = 1500
ENEMY_DAMAGE_PLAYER = 10
GOOEY_GUMMY_BEAR_HP = 40
GOOEY_GUMMY_BEAR_SPEED = 2
STICKY_PATCH_DURATION_MS = 5000
STICKY_PATCH_SLOW_FACTOR = 0.5

POWERUP_SPRINKLE_SPEED_DURATION_MS = 5000
POWERUP_WHIPPED_CREAM_SHIELD_DURATION_MS = 3000
POWERUP_EXTRA_CHEESE_TOSS_DURATION_MS = 7000

SCORE_TOUCHDOWN = 6
SCORE_FUMBLE_RECOVERY = 2
SCORE_COMBO_TACKLE_PER_ENEMY = 1

PLAYER_SIZE = 40
PIGSKIN_SIZE = 30
ENEMY_SIZE = 45
TARGET_ZONE_SIZE = 80
POWERUP_SIZE = 25
OBSTACLE_DEFAULT_SIZE = 50 # For objects like walls, crates, etc.

# --- Entity Class with Health System ---
class Entity(pygame.sprite.Sprite):
    def __init__(self, color, size, max_hp, position):
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = position
        
        # Health Variables
        self.max_health = max_hp
        self.current_health = max_hp
        self.is_alive = True
        self.last_hit_time = 0
        self.invulnerable_duration = 500 # milliseconds after taking damage

        self.stun_timer = 0

    def take_damage(self, amount):
        if not self.is_alive or (pygame.time.get_ticks() - self.last_hit_time < self.invulnerable_duration):
            return
        
        self.current_health -= amount
        # print(f"{self.__class__.__name__} took damage: {amount}. Current HP: {self.current_health}")
        self.last_hit_time = pygame.time.get_ticks()
        
        if self.current_health <= 0:
            self.current_health = 0
            self.die()

    def heal(self, amount):
        if not self.is_alive:
            return
            
        self.current_health += amount
        self.current_health = min(self.current_health, self.max_health)
        # print(f"{self.__class__.__name__} healed: {amount}. Current HP: {self.current_health}")

    def die(self):
        self.is_alive = False
        # print(f"{self.__class__.__name__} died!")
        self.kill() # Removes the sprite from all groups

    def draw_health_bar(self, surface):
        if not self.is_alive or self.max_health <= 0: # Only draw for entities with health
            return

        # Health bar dimensions and position relative to the entity
        BAR_WIDTH = self.rect.width
        BAR_HEIGHT = 5
        BAR_X = self.rect.x
        BAR_Y = self.rect.y - 10 # Position 10 pixels above the entity

        # Calculate health ratio
        health_ratio = self.current_health / self.max_health
        fill_width = int(BAR_WIDTH * health_ratio)

        # Draw background (Red)
        background_rect = pygame.Rect(BAR_X, BAR_Y, BAR_WIDTH, BAR_HEIGHT)
        pygame.draw.rect(surface, RED, background_rect)

        # Draw foreground (Green)
        fill_rect = pygame.Rect(BAR_X, BAR_Y, fill_width, BAR_HEIGHT)
        pygame.draw.rect(surface, GREEN, fill_rect)

    def update(self):
        # Handle stun
        if self.stun_timer > 0:
            self.stun_timer -= clock.get_time()
            if self.stun_timer <= 0:
                self.stun_timer = 0
                # print(f"{self.__class__.__name__} is no longer stunned.")
        pass

# --- LLM_INJECT_ENTITY_CLASS_ENHANCEMENTS ---
class Player(Entity):
    def __init__(self, position):
        super().__init__(PLAYER_COLOR, (PLAYER_SIZE, PLAYER_SIZE), PLAYER_MAX_HP, position)
        self.base_speed = PLAYER_BASE_SPEED
        self.speed = self.base_speed
        self.dx, self.dy = 0, 0
        self.old_x, self.old_y = position

        self.has_pigskin = False
        self.pigskin_ref = None # Reference to the Pigskin object

        # Abilities
        self.dash_active = False
        self.dash_start_time = 0
        self.dash_cooldown_timer = 0
        
        self.tackle_active = False
        self.tackle_start_time = 0
        self.tackle_cooldown_timer = 0
        self.tackle_direction = (0, 0)

        self.throw_cooldown_timer = 0

        # Power-up effects
        self.speed_boost_timer = 0
        self.invulnerable_shield_timer = 0 # Whipped Cream Shield
        self.extra_cheese_toss_timer = 0 # For powerful/homing throw

        self.current_direction = (0, 1) # Default to facing down

    def handle_input(self, keys):
        if self.stun_timer > 0:
            self.dx, self.dy = 0, 0
            return

        self.dx, self.dy = 0, 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.dx = -self.speed
            self.current_direction = (-1, 0)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.dx = self.speed
            self.current_direction = (1, 0)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.dy = -self.speed
            self.current_direction = (0, -1)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.dy = self.speed
            self.current_direction = (0, 1)

        # Diagonal movement
        if self.dx != 0 and self.dy != 0:
            self.dx /= math.sqrt(2)
            self.dy /= math.sqrt(2)
            self.current_direction = (self.dx / self.speed, self.dy / self.speed) # Normalize for direction

    def activate_dash(self):
        if self.dash_cooldown_timer <= 0 and not self.dash_active:
            self.dash_active = True
            self.dash_start_time = pygame.time.get_ticks()
            self.speed *= PLAYER_DASH_SPEED_MULTIPLIER
            self.dash_cooldown_timer = PLAYER_DASH_COOLDOWN_MS
            # print("Dash activated!")

    def activate_tackle(self):
        if self.tackle_cooldown_timer <= 0 and not self.tackle_active:
            self.tackle_active = True
            self.tackle_start_time = pygame.time.get_ticks()
            self.tackle_cooldown_timer = PLAYER_TACKLE_COOLDOWN_MS
            # Use current movement direction, or a default if stationary
            if self.dx == 0 and self.dy == 0:
                self.tackle_direction = self.current_direction
            else:
                self.tackle_direction = (self.dx / self.speed, self.dy / self.speed) # Normalize current movement
            # print(f"Tackle activated! Direction: {self.tackle_direction}")

    def throw_pigskin(self, pigskin_group, target_zone_sprite):
        if self.has_pigskin and self.pigskin_ref and self.throw_cooldown_timer <= 0:
            # print("Throwing pigskin!")
            self.pigskin_ref.is_held = False
            self.pigskin_ref.is_thrown = True
            self.pigskin_ref.thrower = self # Player threw it
            self.pigskin_ref.rect.center = self.rect.center # Detach from player

            # Calculate throw direction towards the target zone
            if target_zone_sprite:
                target_pos = target_zone_sprite.rect.center
            else: # If no target zone, throw in current player direction
                target_pos = (self.rect.centerx + self.current_direction[0] * 200,
                              self.rect.centery + self.current_direction[1] * 200)

            start_pos = pygame.math.Vector2(self.rect.center)
            end_pos = pygame.math.Vector2(target_pos)
            direction_vector = (end_pos - start_pos).normalize()
            
            self.pigskin_ref.vel_x = direction_vector.x * PIGSKIN_THROW_SPEED
            self.pigskin_ref.vel_y = direction_vector.y * PIGSKIN_THROW_SPEED
            
            self.has_pigskin = False
            self.pigskin_ref = None
            self.throw_cooldown_timer = PIGSKIN_THROW_COOLDOWN_MS
            # Add to pigskin group if not already there
            if self.pigskin_ref not in pigskin_group:
                pigskin_group.add(self.pigskin_ref)

    def update(self, obstacles_group=None):
        super().update() # Call parent update for stun timer

        dt = clock.get_time() # Delta time for cooldowns and durations

        # Update cooldown timers
        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= dt
        if self.tackle_cooldown_timer > 0:
            self.tackle_cooldown_timer -= dt
        if self.throw_cooldown_timer > 0:
            self.throw_cooldown_timer -= dt
        
        # Handle dash state
        if self.dash_active:
            if pygame.time.get_ticks() - self.dash_start_time > PLAYER_DASH_DURATION_MS:
                self.dash_active = False
                self.speed = self.base_speed # Revert speed
                # print("Dash ended.")
        
        # Handle tackle state
        if self.tackle_active:
            if pygame.time.get_ticks() - self.tackle_start_time > PLAYER_TACKLE_DURATION_MS:
                self.tackle_active = False
                # print("Tackle ended.")

        # Handle power-up timers
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= dt
            if self.speed_boost_timer <= 0:
                self.speed_boost_timer = 0
                self.speed = self.base_speed # Revert to base speed
                # print("Speed boost ended.")
        
        if self.invulnerable_shield_timer > 0:
            self.invulnerable_shield_timer -= dt
            if self.invulnerable_shield_timer <= 0:
                self.invulnerable_shield_timer = 0
                # print("Whipped Cream Shield ended.")
        
        if self.extra_cheese_toss_timer > 0:
            self.extra_cheese_toss_timer -= dt
            if self.extra_cheese_toss_timer <= 0:
                self.extra_cheese_toss_timer = 0
                # print("Extra Cheese Toss ended.")

        # Apply speed boost if active
        if self.speed_boost_timer > 0 and not self.dash_active: # Dash overrides boost
             self.speed = self.base_speed * 1.5 # Example boost value, could be a constant

        # Movement only if not stunned
        if self.stun_timer <= 0:
            self.old_x, self.old_y = self.rect.x, self.rect.y
            self.rect.x += self.dx
            self.rect.y += self.dy

            # Keep player within screen bounds
            self.rect.left = max(0, self.rect.left)
            self.rect.right = min(SCREEN_WIDTH, self.rect.right)
            self.rect.top = max(0, self.rect.top)
            self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)

        # If holding pigskin, it follows the player
        if self.has_pigskin and self.pigskin_ref:
            self.pigskin_ref.rect.center = self.rect.center

    def draw(self, surface):
        # Draw player
        pygame.draw.rect(surface, self.image.get_at((0,0)), self.rect) # Use player's fill color

        # Draw tackle range visualization if active
        if self.tackle_active:
            tackle_center = self.rect.center
            tackle_end_x = tackle_center[0] + self.tackle_direction[0] * (PLAYER_TACKLE_RANGE // 2)
            tackle_end_y = tackle_center[1] + self.tackle_direction[1] * (PLAYER_TACKLE_RANGE // 2)
            
            # Create a rectangle for the tackle hitbox
            tackle_rect_width = PLAYER_TACKLE_WIDTH if abs(self.tackle_direction[0]) > 0 else PLAYER_TACKLE_RANGE
            tackle_rect_height = PLAYER_TACKLE_WIDTH if abs(self.tackle_direction[1]) > 0 else PLAYER_TACKLE_RANGE
            
            # Adjust if diagonal tackle. Simpler to visualize as a circle for now if direction is complex.
            # For simpler axis-aligned tackles:
            if self.tackle_direction[0] != 0 or self.tackle_direction[1] != 0:
                # Calculate the center of the tackle effect for drawing
                tackle_effect_center = (self.rect.centerx + self.tackle_direction[0] * PLAYER_TACKLE_RANGE / 2,
                                        self.rect.centery + self.tackle_direction[1] * PLAYER_TACKLE_RANGE / 2)
                tackle_effect_rect = pygame.Rect(0,0, PLAYER_TACKLE_WIDTH, PLAYER_TACKLE_WIDTH)
                tackle_effect_rect.center = tackle_effect_center
                pygame.draw.rect(surface, TACKLE_COLOR, tackle_effect_rect, 2) # Draw outline

        if self.invulnerable_shield_timer > 0:
            pygame.draw.circle(surface, WHITE, self.rect.center, self.rect.width // 2 + 5, 2) # Shield effect

        self.draw_health_bar(surface)


class Pigskin(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image = pygame.Surface((PIGSKIN_SIZE, PIGSKIN_SIZE))
        self.image.fill(PIGSKIN_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.is_held = False
        self.is_thrown = False
        self.vel_x = 0
        self.vel_y = 0
        self.thrower = None # Who threw it

    def update(self):
        if self.is_thrown:
            self.rect.x += self.vel_x
            self.rect.y += self.vel_y
            # Simple friction/slowdown for thrown pigskin
            self.vel_x *= 0.98
            self.vel_y *= 0.98
            if abs(self.vel_x) < 0.1 and abs(self.vel_y) < 0.1:
                self.is_thrown = False
                self.vel_x = 0
                self.vel_y = 0
                # print("Pigskin stopped moving after throw.")
            
            # Keep within bounds, bounce off for simplicity
            if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
                self.vel_x *= -1
            if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
                self.vel_y *= -1

    def draw(self, surface):
        pygame.draw.rect(surface, PIGSKIN_COLOR, self.rect)


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, obj_type="wall", color=WALL_COLOR):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.type = obj_type
        
        # Customize color based on type, or use provided color
        if obj_type == "wall": self.image.fill(WALL_COLOR)
        elif obj_type == "crate": self.image.fill(CRATE_COLOR)
        elif obj_type == "rock": self.image.fill(ROCK_COLOR)
        elif obj_type == "tree": self.image.fill(TREE_COLOR)
        else: self.image.fill(color)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class TargetZone(pygame.sprite.Sprite):
    def __init__(self, x, y, width=TARGET_ZONE_SIZE, height=TARGET_ZONE_SIZE):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(ENDZONE_COLOR)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, pu_type):
        super().__init__()
        self.type = pu_type
        self.image = pygame.Surface((POWERUP_SIZE, POWERUP_SIZE))
        
        if self.type == "health":
            self.image.fill(POWERUP_HEALTH_COLOR)
        elif self.type == "speed_boost":
            self.image.fill(POWERUP_SPEED_COLOR)
        elif self.type == "shield":
            self.image.fill(WHITE) # Example, could be more thematic
        elif self.type == "cheese_toss":
            self.image.fill(TACKLE_COLOR) # Example
        else:
            self.image.fill(WHITE) # Default
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class HungryHamburglar(Entity):
    def __init__(self, position, patrol_path=None):
        super().__init__(ENEMY_HAMBURGLAR_COLOR, (ENEMY_SIZE, ENEMY_SIZE), ENEMY_HAMBURGLAR_HP, position)
        self.speed = ENEMY_HAMBURGLAR_SPEED
        self.patrol_path = [pygame.math.Vector2(p) for p in patrol_path] if patrol_path else []
        self.current_patrol_index = 0
        self.target_position = None
        self.is_chasing = False
        self.vision_range = 200 # How far it can see the player
        self.last_player_pos = None

    def update(self, player_pos):
        super().update() # Handle stun timer
        if not self.is_alive or self.stun_timer > 0:
            return

        current_pos_vec = pygame.math.Vector2(self.rect.center)
        player_pos_vec = pygame.math.Vector2(player_pos)
        distance_to_player = current_pos_vec.distance_to(player_pos_vec)

        if distance_to_player < self.vision_range:
            self.is_chasing = True
            self.target_position = player_pos_vec
            self.last_player_pos = player_pos_vec
        elif self.is_chasing and self.last_player_pos and current_pos_vec.distance_to(self.last_player_pos) < self.speed:
            # If player is out of range, but enemy reached last known player position, revert to patrol
            self.is_chasing = False
            self.target_position = None
            self.last_player_pos = None
        
        if self.is_chasing and self.target_position:
            move_direction = (self.target_position - current_pos_vec).normalize()
            self.rect.x += move_direction.x * self.speed
            self.rect.y += move_direction.y * self.speed
        elif self.patrol_path:
            if not self.target_position: # Set new patrol target if none
                self.target_position = self.patrol_path[self.current_patrol_index]
            
            if current_pos_vec.distance_to(self.target_position) < self.speed:
                self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_path)
                self.target_position = self.patrol_path[self.current_patrol_index]
            
            move_direction = (self.target_position - current_pos_vec).normalize()
            self.rect.x += move_direction.x * self.speed
            self.rect.y += move_direction.y * self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, self.image.get_at((0,0)), self.rect)
        self.draw_health_bar(surface)


class SpicySausage(Entity):
    def __init__(self, position, patrol_path=None):
        super().__init__(ENEMY_SAUSAGE_COLOR, (ENEMY_SIZE, ENEMY_SIZE), ENEMY_SAUSAGE_HP, position)
        self.base_speed = ENEMY_SAUSAGE_SPEED
        self.speed = self.base_speed
        self.patrol_path = [pygame.math.Vector2(p) for p in patrol_path] if patrol_path else []
        self.current_patrol_index = 0
        self.target_position = None
        self.is_rolling = False
        self.roll_target = None
        self.roll_start_time = 0
        self.vision_range = 150 # How far it can spot the player

    def start_roll(self, player_pos):
        if not self.is_rolling:
            self.is_rolling = True
            self.roll_start_time = pygame.time.get_ticks()
            self.roll_target = pygame.math.Vector2(player_pos)
            # Calculate direction for roll
            current_pos_vec = pygame.math.Vector2(self.rect.center)
            direction_vector = (self.roll_target - current_pos_vec).normalize()
            self.roll_vel_x = direction_vector.x * (self.speed * 1.5) # Faster while rolling
            self.roll_vel_y = direction_vector.y * (self.speed * 1.5)
            # print("Spicy Sausage started rolling!")

    def update(self, player_pos):
        super().update() # Handle stun timer
        if not self.is_alive or self.stun_timer > 0:
            return

        current_pos_vec = pygame.math.Vector2(self.rect.center)
        player_pos_vec = pygame.math.Vector2(player_pos)
        distance_to_player = current_pos_vec.distance_to(player_pos_vec)

        if self.is_rolling:
            if pygame.time.get_ticks() - self.roll_start_time > ENEMY_SAUSAGE_ROLL_DURATION_MS:
                self.is_rolling = False
                self.roll_target = None
                self.roll_vel_x, self.roll_vel_y = 0, 0
                # print("Spicy Sausage stopped rolling.")
            else:
                self.rect.x += self.roll_vel_x
                self.rect.y += self.roll_vel_y
                return # Stop further movement logic for this update

        # If not rolling and sees player, start rolling
        if distance_to_player < self.vision_range and not self.is_rolling:
            self.start_roll(player_pos)
        
        # Patrol if not rolling and no target
        elif self.patrol_path and not self.is_rolling:
            if not self.target_position:
                self.target_position = self.patrol_path[self.current_patrol_index]
            
            if current_pos_vec.distance_to(self.target_position) < self.speed:
                self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_path)
                self.target_position = self.patrol_path[self.current_patrol_index]
            
            move_direction = (self.target_position - current_pos_vec).normalize()
            self.rect.x += move_direction.x * self.speed
            self.rect.y += move_direction.y * self.speed
            
    def draw(self, surface):
        pygame.draw.rect(surface, self.image.get_at((0,0)), self.rect)
        self.draw_health_bar(surface)

# Function to parse level data and create sprites
def load_level_data(level_data):
    # Clear existing groups (if reloading a level)
    global all_sprites, player_sprite, pigskin_sprite, target_zone_sprite
    global enemy_sprites, obstacle_sprites, powerup_sprites, sticky_patches_sprites

    all_sprites = pygame.sprite.Group()
    player_sprite = pygame.sprite.GroupSingle()
    pigskin_sprite = pygame.sprite.GroupSingle()
    target_zone_sprite = pygame.sprite.GroupSingle()
    enemy_sprites = pygame.sprite.Group()
    obstacle_sprites = pygame.sprite.Group()
    powerup_sprites = pygame.sprite.Group()
    sticky_patches_sprites = pygame.sprite.Group() # Gummy bear mechanic, not in Level 1 but good to have

    # Player spawn
    player_spawn = level_data["spawn_points"][0] # Assuming first is player
    player_instance = Player((player_spawn["x"], player_spawn["y"]))
    player_sprite.add(player_instance)
    all_sprites.add(player_instance)

    # Pigskin (will spawn at player start for Level 1 objective)
    pigskin_instance = Pigskin((player_spawn["x"] + 20, player_spawn["y"])) # Offset slightly
    pigskin_sprite.add(pigskin_instance)
    all_sprites.add(pigskin_instance)

    # Target zone
    target_zone_data = next((sp for sp in level_data["spawn_points"] if sp["type"] == "target_zone"), None)
    if target_zone_data:
        tz_instance = TargetZone(target_zone_data["x"], target_zone_data["y"])
        target_zone_sprite.add(tz_instance)
        all_sprites.add(tz_instance)

    # Obstacles
    for obs_data in level_data["obstacles"]:
        obs_instance = Obstacle(obs_data["x"], obs_data["y"], obs_data["width"], obs_data["height"], obs_data["type"])
        obstacle_sprites.add(obs_instance)
        all_sprites.add(obs_instance)

    # Powerups
    for pu_data in level_data["powerups"]:
        pu_instance = PowerUp(pu_data["x"], pu_data["y"], pu_data["type"])
        powerup_sprites.add(pu_instance)
        all_sprites.add(pu_instance)

    # Enemies
    for enemy_data in level_data["enemies"]:
        enemy_type = enemy_data["type"]
        pos = (enemy_data["x"], enemy_data["y"])
        patrol_path = enemy_data.get("patrol_path")

        if enemy_type == "blocker": # Map to HungryHamburglar
            enemy_instance = HungryHamburglar(pos, patrol_path)
        elif enemy_type == "chaser": # Map to SpicySausage
            enemy_instance = SpicySausage(pos, patrol_path)
        else: # Default or raise error
            print(f"Unknown enemy type: {enemy_type}")
            continue
        
        enemy_sprites.add(enemy_instance)
        all_sprites.add(enemy_instance)
    
    return player_instance, pigskin_instance, target_zone_sprite.sprite, enemy_sprites, obstacle_sprites, powerup_sprites
# --- END LLM_INJECT_ENTITY_CLASS_ENHANCEMENTS ---

# --- Game Setup ---
# --- LLM_INJECT_GAME_SETUP_CUSTOM_CLASSES ---
# Level 1 data (from JSON provided in prompt)
level_1_data = {
  "level_number": 1,
  "name": "The Rookie Ruckus",
  "description": "Welcome to Fumble Frenzy! Your first challenge is to navigate a small, open field, learning the basics of movement and passing. Dodge the initial few blockers and secure the pigskin to reach the endzone!",
  "size": {
    "width": 800,
    "height": 600
  },
  "spawn_points": [
    {
      "x": 100,
      "y": 100,
      "type": "player"
    },
    {
      "x": 700,
      "y": 500,
      "type": "target_zone"
    }
  ],
  "obstacles": [
    {
      "x": 200,
      "y": 200,
      "width": 50,
      "height": 50,
      "type": "wall"
    },
    {
      "x": 300,
      "y": 300,
      "width": 60,
      "height": 40,
      "type": "crate"
    },
    {
      "x": 500,
      "y": 400,
      "width": 30,
      "height": 30,
      "type": "rock"
    },
    {
      "x": 400,
      "y": 150,
      "width": 40,
      "height": 60,
      "type": "tree"
    }
  ],
  "powerups": [
    {
      "x": 300,
      "y": 150,
      "type": "health"
    },
    {
      "x": 650,
      "y": 550,
      "type": "speed_boost"
    }
  ],
  "enemies": [
    {
      "x": 350,
      "y": 250,
      "type": "blocker",
      "patrol_path": [
        [
          350,
          250
        ],
        [
          420,
          250
        ],
        [
          420,
          280
        ],
        [
          350,
          280
        ]
      ]
    },
    {
      "x": 550,
      "y": 200,
      "type": "blocker",
      "patrol_path": [
        [
          550,
          200
        ],
        [
          550,
          270
        ],
        [
          580,
          270
        ],
        [
          580,
          200
        ]
      ]
    },
    {
      "x": 150,
      "y": 450,
      "type": "chaser",
      "patrol_path": [
        [
          150,
          450
        ],
        [
          220,
          450
        ]
      ]
    }
  ],
  "objectives": [
    {
      "type": "reach_zone",
      "target": "target_zone",
      "count": 1
    },
    {
      "type": "collect",
      "target": "pigskin",
      "count": 1
    }
  ],
  "difficulty": "easy",
  "time_limit": 180
}

player_instance, pigskin_instance, target_zone_instance, enemy_sprites, obstacle_sprites, powerup_sprites = load_level_data(level_1_data)

# Game global variables needed for interactions
global_score = 0
global_player_has_pigskin = False
global_level_complete = False
global_game_over = False

# --- END LLM_INJECT_GAME_SETUP_CUSTOM_CLASSES ---

# --- Test Events (Simulating Damage/Heal) ---
# --- LLM_INJECT_GAME_LOGIC_AND_INTERACTIONS ---
def game_update_logic():
    global global_score, global_player_has_pigskin, global_level_complete, global_game_over

    player = player_instance.sprite # Get the single player sprite

    if global_game_over or global_level_complete:
        return

    # Handle Player Input
    keys = pygame.key.get_pressed()
    player.handle_input(keys)

    if keys[pygame.K_SPACE]: # Dash
        player.activate_dash()
    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]: # Tackle
        player.activate_tackle()
    if keys[pygame.K_e]: # Throw Pigskin (Pass)
        player.throw_pigskin(pigskin_sprite, target_zone_instance)

    # Update all game objects
    player.update(obstacle_sprites)
    pigskin_instance.update()
    
    for enemy in enemy_sprites:
        enemy.update(player.rect.center)
    
    # --- Collision Detection and Resolution ---
    # Player-Obstacle Collision
    # Store old position before movement
    player.old_x, player.old_y = player.rect.x, player.rect.y
    player.rect.x += player.dx
    player.rect.y += player.dy

    # Resolve X-axis collisions
    for obstacle in pygame.sprite.spritecollide(player, obstacle_sprites, False):
        if player.dx > 0: # Moving right, hit left side of obstacle
            player.rect.right = obstacle.rect.left
        elif player.dx < 0: # Moving left, hit right side of obstacle
            player.rect.left = obstacle.rect.right
        player.dx = 0 # Stop horizontal movement

    # Resolve Y-axis collisions
    for obstacle in pygame.sprite.spritecollide(player, obstacle_sprites, False):
        if player.dy > 0: # Moving down, hit top side of obstacle
            player.rect.bottom = obstacle.rect.top
        elif player.dy < 0: # Moving up, hit bottom side of obstacle
            player.rect.top = obstacle.rect.bottom
        player.dy = 0 # Stop vertical movement

    # Revert to original position if still overlapping after both axis checks (shouldn't happen with proper resolution)
    # A simpler resolution is to revert fully if any collision, but axis-by-axis is better
    # If a very complex collision, might just revert player.rect.x = player.old_x; player.rect.y = player.old_y

    # Pigskin-Obstacle Collision (simple bounce for now)
    if pigskin_instance.sprite and pigskin_instance.sprite.is_thrown:
        for obstacle in pygame.sprite.spritecollide(pigskin_instance.sprite, obstacle_sprites, False):
            # Simple bounce logic
            if abs(pigskin_instance.sprite.vel_x) > abs(pigskin_instance.sprite.vel_y):
                pigskin_instance.sprite.vel_x *= -1
            else:
                pigskin_instance.sprite.vel_y *= -1
            # Adjust position to prevent sticking
            if pigskin_instance.sprite.rect.colliderect(obstacle.rect):
                if pigskin_instance.sprite.vel_x < 0: # Moving left
                    pigskin_instance.sprite.rect.left = obstacle.rect.right
                elif pigskin_instance.sprite.vel_x > 0: # Moving right
                    pigskin_instance.sprite.rect.right = obstacle.rect.left
                if pigskin_instance.sprite.vel_y < 0: # Moving up
                    pigskin_instance.sprite.rect.top = obstacle.rect.bottom
                elif pigskin_instance.sprite.vel_y > 0: # Moving down
                    pigskin_instance.sprite.rect.bottom = obstacle.rect.top

    # Player-Pigskin interaction
    if not player.has_pigskin and pigskin_instance.sprite and not pigskin_instance.sprite.is_thrown:
        if pygame.sprite.collide_rect(player, pigskin_instance.sprite):
            player.has_pigskin = True
            player.pigskin_ref = pigskin_instance.sprite
            pigskin_instance.sprite.is_held = True
            # print("Player picked up pigskin!")
            # Objective: collect pigskin, bonus points
            # This is hardcoded for first objective being collecting pigskin
            if "collect" in [obj["type"] for obj in level_1_data["objectives"]]:
                # Assume objective is met by picking up
                pass # Already handled by player.has_pigskin, no extra score here

    # Player-Enemy collision (Player takes damage, enemy might be stunned)
    if not player.invulnerable_shield_timer > 0:
        collided_enemies = pygame.sprite.spritecollide(player, enemy_sprites, False)
        for enemy in collided_enemies:
            if enemy.stun_timer <= 0: # Only if enemy is not already stunned
                player.take_damage(ENEMY_DAMAGE_PLAYER)
                # print(f"Player hit by {enemy.__class__.__name__}! HP: {player.current_health}")
                # Simple knockback for player (optional)
                direction = pygame.math.Vector2(player.rect.center) - pygame.math.Vector2(enemy.rect.center)
                if direction.length() > 0:
                    direction = direction.normalize()
                    player.rect.x += direction.x * 20
                    player.rect.y += direction.y * 20
                if player.current_health <= 0:
                    global_game_over = True
    
    # Player Tackle-Enemy collision
    if player.tackle_active:
        tackle_rect_center = (player.rect.centerx + player.tackle_direction[0] * (PLAYER_TACKLE_RANGE // 2),
                              player.centery + player.tackle_direction[1] * (PLAYER_TACKLE_RANGE // 2))
        tackle_hitbox = pygame.Rect(0, 0, PLAYER_TACKLE_WIDTH, PLAYER_TACKLE_WIDTH)
        tackle_hitbox.center = tackle_rect_center

        tackled_enemies = pygame.sprite.spritecollide(tackle_hitbox, enemy_sprites, False)
        num_tackled = 0
        for enemy in tackled_enemies:
            if enemy.stun_timer <= 0: # Can only tackle unstunned enemies
                enemy.stun_timer = ENEMY_STUN_DURATION_MS
                enemy.take_damage(10) # Tackle inflicts damage
                num_tackled += 1
                # print(f"{enemy.__class__.__name__} tackled and stunned!")
        if num_tackled > 0:
            global_score += SCORE_COMBO_TACKLE_PER_ENEMY * num_tackled
    
    # Player-PowerUp collision
    powerup_hits = pygame.sprite.spritecollide(player, powerup_sprites, True)
    for powerup in powerup_hits:
        if powerup.type == "health":
            player.heal(25) # Example heal amount
            # print("Player collected Health powerup!")
        elif powerup.type == "speed_boost":
            player.speed_boost_timer = POWERUP_SPRINKLE_SPEED_DURATION_MS
            # print("Player collected Speed Boost powerup!")
        elif powerup.type == "shield":
            player.invulnerable_shield_timer = POWERUP_WHIPPED_CREAM_SHIELD_DURATION_MS
            # print("Player collected Whipped Cream Shield powerup!")
        elif powerup.type == "cheese_toss":
            player.extra_cheese_toss_timer = POWERUP_EXTRA_CHEESE_TOSS_DURATION_MS
            # print("Player collected Extra Cheese Toss powerup!")

    # Pigskin-Target Zone collision (Touchdown!)
    if pigskin_instance.sprite and not pigskin_instance.sprite.is_held:
        if pygame.sprite.collide_rect(pigskin_instance.sprite, target_zone_instance):
            global_score += SCORE_TOUCHDOWN
            global_player_has_pigskin = False # Pigskin is scored
            pigskin_instance.sprite.kill() # Remove pigskin
            global_level_complete = True
            # print(f"Touchdown! Score: {global_score}")

    # Check player health for Game Over
    if player.current_health <= 0:
        global_game_over = True

# --- END LLM_INJECT_GAME_LOGIC_AND_INTERACTIONS ---

# --- Main Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            # Press 'H' to heal the player (for testing)
            if event.key == pygame.K_h:
                player_instance.sprite.heal(10)
            # Press 'P' to simulate pigskin toss (for testing)
            if event.key == pygame.K_p and player_instance.sprite.has_pigskin:
                player_instance.sprite.throw_pigskin(pigskin_sprite, target_zone_instance)
            # Press 'K' to simulate player taking damage
            if event.key == pygame.K_k:
                player_instance.sprite.take_damage(20)


    # 1. Update
    game_update_logic() # Call the main game logic function

    # 2. Drawing
    screen.fill(WHITE)
    
    # Draw target zone first so objects can be on top
    if target_zone_instance:
        target_zone_instance.draw(screen)

    # Draw all sprites managed by groups
    for sprite in all_sprites:
        # Custom draw for player to include abilities/health bar
        if isinstance(sprite, Player):
            sprite.draw(screen)
        elif isinstance(sprite, Pigskin):
            sprite.draw(screen)
        elif isinstance(sprite, Obstacle):
            sprite.draw(screen)
        elif isinstance(sprite, PowerUp):
            sprite.draw(screen)
        elif isinstance(sprite, Entity): # Generic enemies
            sprite.draw(screen) # Entity.draw is placeholder, subclasses should override
            sprite.draw_health_bar(screen)

    # Display score (simple)
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {global_score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    if global_level_complete:
        win_text = font.render("LEVEL COMPLETE!", True, BLUE)
        screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2))
    elif global_game_over:
        game_over_text = font.render("GAME OVER!", True, RED)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()


# --- TEMPLATE: E_BASIC_COLLISION ---
import pygame
import math # Needed for player direction/tackle

# --- Constants & Initialization (Assumed from A) ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
FPS = 60
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# --- Game-specific Constants (Duplicated for template isolation) ---
PIGSKIN_COLOR = (255, 220, 150)
ENDZONE_COLOR = (100, 200, 100)
WALL_COLOR = (150, 75, 0)
CRATE_COLOR = (120, 60, 0)
ROCK_COLOR = (100, 100, 100)
TREE_COLOR = (34, 139, 34)
ENEMY_HAMBURGLAR_COLOR = (200, 50, 50)
TACKLE_COLOR = (255, 255, 0)

PLAYER_BASE_SPEED = 4
PLAYER_DASH_SPEED_MULTIPLIER = 2.0
PLAYER_DASH_DURATION_MS = 150
PLAYER_DASH_COOLDOWN_MS = 1500
PLAYER_TACKLE_RANGE = 70
PLAYER_TACKLE_WIDTH = 60
PLAYER_TACKLE_DURATION_MS = 200
PLAYER_TACKLE_COOLDOWN_MS = 1000
PIGSKIN_THROW_SPEED = 8
PIGSKIN_THROW_COOLDOWN_MS = 500

PLAYER_SIZE = 40
PIGSKIN_SIZE = 30
ENEMY_SIZE = 45
TARGET_ZONE_SIZE = 80
# --- END Game-specific Constants ---

# --- Player Class with Collision Memory ---
# --- LLM_INJECT_PLAYER_CLASS_ENHANCEMENTS ---
class Player(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image = pygame.Surface([PLAYER_SIZE, PLAYER_SIZE])
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.base_speed = PLAYER_BASE_SPEED
        self.speed = self.base_speed
        self.dx = 0 # Delta X for current frame
        self.dy = 0 # Delta Y for current frame
        self.old_x = position[0]
        self.old_y = position[1]

        self.current_direction = (0, 1) # Default to facing down

        # Abilities
        self.dash_active = False
        self.dash_start_time = 0
        self.dash_cooldown_timer = 0
        
        self.tackle_active = False
        self.tackle_start_time = 0
        self.tackle_cooldown_timer = 0
        self.tackle_direction = (0, 0) # Direction of the tackle

        self.has_pigskin = False
        self.pigskin_ref = None # Reference to the Pigskin object

    def handle_input(self, keys):
        self.dx, self.dy = 0, 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.dx = -self.speed
            self.current_direction = (-1, 0)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.dx = self.speed
            self.current_direction = (1, 0)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.dy = -self.speed
            self.current_direction = (0, -1)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.dy = self.speed
            self.current_direction = (0, 1)
        
        # Diagonal movement
        if self.dx != 0 and self.dy != 0:
            self.dx /= math.sqrt(2)
            self.dy /= math.sqrt(2)
            self.current_direction = (self.dx / self.speed, self.dy / self.speed) # Normalize for direction


    def activate_dash(self):
        if self.dash_cooldown_timer <= 0 and not self.dash_active:
            self.dash_active = True
            self.dash_start_time = pygame.time.get_ticks()
            self.speed *= PLAYER_DASH_SPEED_MULTIPLIER
            self.dash_cooldown_timer = PLAYER_DASH_COOLDOWN_MS
            # print("Dash activated!")

    def activate_tackle(self):
        if self.tackle_cooldown_timer <= 0 and not self.tackle_active:
            self.tackle_active = True
            self.tackle_start_time = pygame.time.get_ticks()
            self.tackle_cooldown_timer = PLAYER_TACKLE_COOLDOWN_MS
            # Use current movement direction, or a default if stationary
            if self.dx == 0 and self.dy == 0:
                self.tackle_direction = self.current_direction
            else:
                self.tackle_direction = (self.dx / self.speed, self.dy / self.speed) # Normalize current movement
            # print(f"Tackle activated! Direction: {self.tackle_direction}")

    def update(self):
        dt = clock.get_time() # Delta time for cooldowns and durations

        # Update cooldown timers
        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= dt
        if self.tackle_cooldown_timer > 0:
            self.tackle_cooldown_timer -= dt
        
        # Handle dash state
        if self.dash_active:
            if pygame.time.get_ticks() - self.dash_start_time > PLAYER_DASH_DURATION_MS:
                self.dash_active = False
                self.speed = self.base_speed # Revert speed
                # print("Dash ended.")
        
        # Handle tackle state
        if self.tackle_active:
            if pygame.time.get_ticks() - self.tackle_start_time > PLAYER_TACKLE_DURATION_MS:
                self.tackle_active = False
                # print("Tackle ended.")

        self.handle_input(pygame.key.get_pressed())
        
        # Store old position before movement
        self.old_x = self.rect.x
        self.old_y = self.rect.y
        
        # Apply movement
        self.rect.x += self.dx
        self.rect.y += self.dy
        
        # Keep player within screen bounds (simple boundary checking)
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)

        # If holding pigskin, it follows the player
        if self.has_pigskin and self.pigskin_ref:
            self.pigskin_ref.rect.center = self.rect.center

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        
        # Draw tackle visualization if active
        if self.tackle_active:
            tackle_center = self.rect.center
            # Calculate the center of the tackle effect for drawing
            tackle_effect_center = (self.rect.centerx + self.tackle_direction[0] * PLAYER_TACKLE_RANGE / 2,
                                    self.rect.centery + self.tackle_direction[1] * PLAYER_TACKLE_RANGE / 2)
            tackle_effect_rect = pygame.Rect(0,0, PLAYER_TACKLE_WIDTH, PLAYER_TACKLE_WIDTH)
            tackle_effect_rect.center = tackle_effect_center
            pygame.draw.rect(surface, TACKLE_COLOR, tackle_effect_rect, 2) # Draw outline
# --- END LLM_INJECT_PLAYER_CLASS_ENHANCEMENTS ---

# --- Wall Class (Solid Object) ---
# --- LLM_INJECT_WALL_CLASS_ENHANCEMENTS ---
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, obj_type="wall", color=WALL_COLOR):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.type = obj_type
        
        if obj_type == "wall": self.image.fill(WALL_COLOR)
        elif obj_type == "crate": self.image.fill(CRATE_COLOR)
        elif obj_type == "rock": self.image.fill(ROCK_COLOR)
        elif obj_type == "tree": self.image.fill(TREE_COLOR)
        else: self.image.fill(color)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
# --- END LLM_INJECT_WALL_CLASS_ENHANCEMENTS ---

# --- Game-specific classes for this template's context ---
class Pigskin(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image = pygame.Surface((PIGSKIN_SIZE, PIGSKIN_SIZE))
        self.image.fill(PIGSKIN_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.is_held = False

    def update(self):
        pass # No complex logic needed for this template example

class Enemy(pygame.sprite.Sprite): # Generic enemy for collision test
    def __init__(self, position):
        super().__init__()
        self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
        self.image.fill(ENEMY_HAMBURGLAR_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = position

    def update(self):
        pass

# --- Collision Functions ---
# --- LLM_INJECT_COLLISION_FUNCTION_ENHANCEMENTS ---
def check_and_resolve_player_obstacle_collision(player_sprite, obstacle_group):
    """
    Checks for collision and resolves it by reverting the player's position
    for each axis independently.
    """
    player_sprite.rect.x += player_sprite.dx
    # Check for X-axis collisions
    hit_obstacles = pygame.sprite.spritecollide(player_sprite, obstacle_group, False)
    for obstacle in hit_obstacles:
        if player_sprite.dx > 0: # Moving right, hit left side of obstacle
            player_sprite.rect.right = obstacle.rect.left
        elif player_sprite.dx < 0: # Moving left, hit right side of obstacle
            player_sprite.rect.left = obstacle.rect.right
        player_sprite.dx = 0 # Stop horizontal movement

    player_sprite.rect.y += player_sprite.dy
    # Check for Y-axis collisions
    hit_obstacles = pygame.sprite.spritecollide(player_sprite, obstacle_group, False)
    for obstacle in hit_obstacles:
        if player_sprite.dy > 0: # Moving down, hit top side of obstacle
            player_sprite.rect.bottom = obstacle.rect.top
        elif player_sprite.dy < 0: # Moving up, hit bottom side of obstacle
            player_sprite.rect.top = obstacle.rect.bottom
        player_sprite.dy = 0 # Stop vertical movement

def check_player_pigskin_collision(player_sprite, pigskin_sprite_group):
    """
    Checks if player collides with pigskin and picks it up.
    """
    if not player_sprite.has_pigskin:
        collided_pigskins = pygame.sprite.spritecollide(player_sprite, pigskin_sprite_group, False)
        for pigskin in collided_pigskins:
            player_sprite.has_pigskin = True
            player_sprite.pigskin_ref = pigskin
            pigskin.is_held = True
            # print("Player picked up pigskin!")
            break

def check_player_tackle_enemy_collision(player_sprite, enemy_group):
    """
    Checks if an active player tackle hits any enemies.
    """
    if player_sprite.tackle_active:
        tackle_rect_center = (player_sprite.rect.centerx + player_sprite.tackle_direction[0] * (PLAYER_TACKLE_RANGE // 2),
                              player_sprite.rect.centery + player_sprite.tackle_direction[1] * (PLAYER_TACKLE_RANGE // 2))
        tackle_hitbox = pygame.Rect(0, 0, PLAYER_TACKLE_WIDTH, PLAYER_TACKLE_WIDTH)
        tackle_hitbox.center = tackle_rect_center

        tackled_enemies = pygame.sprite.spritecollide(tackle_hitbox, enemy_group, False)
        if tackled_enemies:
            # print(f"Player tackled {len(tackled_enemies)} enemy(s)!")
            # In a full game, enemies would be stunned/damaged here.
            pass # Just detect for this template.
# --- END LLM_INJECT_COLLISION_FUNCTION_ENHANCEMENTS ---

# --- Game Setup ---
# --- LLM_INJECT_GAME_SETUP_CUSTOM_CLASSES ---
# Level 1 data (from JSON provided in prompt)
level_1_data = {
  "level_number": 1,
  "name": "The Rookie Ruckus",
  "description": "Welcome to Fumble Frenzy! Your first challenge is to navigate a small, open field, learning the basics of movement and passing. Dodge the initial few blockers and secure the pigskin to reach the endzone!",
  "size": {
    "width": 800,
    "height": 600
  },
  "spawn_points": [
    {
      "x": 100,
      "y": 100,
      "type": "player"
    }
  ],
  "obstacles": [
    {
      "x": 200,
      "y": 200,
      "width": 50,
      "height": 50,
      "type": "wall"
    },
    {
      "x": 300,
      "y": 300,
      "width": 60,
      "height": 40,
      "type": "crate"
    },
    {
      "x": 500,
      "y": 400,
      "width": 30,
      "height": 30,
      "type": "rock"
    },
    {
      "x": 400,
      "y": 150,
      "width": 40,
      "height": 60,
      "type": "tree"
    }
  ],
  "powerups": [
    {
      "x": 300,
      "y": 150,
      "type": "health"
    },
    {
      "x": 650,
      "y": 550,
      "type": "speed_boost"
    }
  ],
  "enemies": [
    {
      "x": 350,
      "y": 250,
      "type": "blocker",
      "patrol_path": [
        [
          350,
          250
        ],
        [
          420,
          250
        ],
        [
          420,
          280
        ],
        [
          350,
          280
        ]
      ]
    },
    {
      "x": 550,
      "y": 200,
      "type": "blocker",
      "patrol_path": [
        [
          550,
          200
        ],
        [
          550,
          270
        ],
        [
          580,
          270
        ],
        [
          580,
          200
        ]
      ]
    },
    {
      "x": 150,
      "y": 450,
      "type": "chaser",
      "patrol_path": [
        [
          150,
          450
        ],
        [
          220,
          450
        ]
      ]
    }
  ],
  "objectives": [
    {
      "type": "reach_zone",
      "target": "target_zone",
      "count": 1
    },
    {
      "type": "collect",
      "target": "pigskin",
      "count": 1
    }
  ],
  "difficulty": "easy",
  "time_limit": 180
}

all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.GroupSingle()
obstacle_sprites = pygame.sprite.Group()
pigskin_sprites = pygame.sprite.Group()
enemy_sprites = pygame.sprite.Group() # For tackle collision test

# Player spawn
player_spawn_data = level_1_data["spawn_points"][0]
player = Player((player_spawn_data["x"], player_spawn_data["y"]))
player_group.add(player)
all_sprites.add(player)

# Obstacles
for obs_data in level_1_data["obstacles"]:
    obs_instance = Obstacle(obs_data["x"], obs_data["y"], obs_data["width"], obs_data["height"], obs_data["type"])
    obstacle_sprites.add(obs_instance)
    all_sprites.add(obs_instance)

# Pigskin (spawned near player for collection)
pigskin = Pigskin((player_spawn_data["x"] + 20, player_spawn_data["y"]))
pigskin_sprites.add(pigskin)
all_sprites.add(pigskin)

# Enemies (just a couple for tackle collision test)
enemy1 = Enemy((350, 250))
enemy2 = Enemy((550, 200))
enemy_sprites.add(enemy1, enemy2)
all_sprites.add(enemy1, enemy2)

# --- END LLM_INJECT_GAME_SETUP_CUSTOM_CLASSES ---

# --- Main Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE: # Dash ability
                player.activate_dash()
            if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT: # Tackle ability
                player.activate_tackle()

    # 1. Update
    # --- LLM_INJECT_GAME_LOGIC_AND_INTERACTIONS ---
    all_sprites.update()
    
    # Handle Player abilities via input (already done in player.update, but here for clarity)
    # player.handle_input(pygame.key.get_pressed())

    # 2. Collision Check and Resolution
    check_and_resolve_player_obstacle_collision(player, obstacle_sprites)
    check_player_pigskin_collision(player, pigskin_sprites)
    check_player_tackle_enemy_collision(player, enemy_sprites)
    # --- END LLM_INJECT_GAME_LOGIC_AND_INTERACTIONS ---

    # 3. Drawing
    screen.fill(WHITE)
    
    # Draw player with its custom draw method
    for sprite in all_sprites:
        if isinstance(sprite, Player):
            sprite.draw(screen)
        else:
            screen.blit(sprite.image, sprite.rect)
    
    # Display whether player has pigskin
    font = pygame.font.Font(None, 30)
    pigskin_status = font.render(f"Has Pigskin: {player.has_pigskin}", True, BLACK)
    screen.blit(pigskin_status, (10, 10))
    dash_cd_text = font.render(f"Dash CD: {max(0, player.dash_cooldown_timer / 1000):.1f}s", True, BLACK)
    screen.blit(dash_cd_text, (10, 40))
    tackle_cd_text = font.render(f"Tackle CD: {max(0, player.tackle_cooldown_timer / 1000):.1f}s", True, BLACK)
    screen.blit(tackle_cd_text, (10, 70))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()


# --- TEMPLATE: F_GAME_STATES ---
import pygame
import sys
from enum import Enum
import os
import math # Needed for vector math

# --- Constants & Initialization (Assumed from A) ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fumble Frenzy: Game States")
clock = pygame.time.Clock()
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0) # Added missing constant definition
FONT = pygame.font.Font(None, 74)
SMALL_FONT = pygame.font.Font(None, 36)

# --- Game-specific Constants (Duplicated for template isolation, but ideally imported from A) ---
PIGSKIN_COLOR = (255, 220, 150)
ENDZONE_COLOR = (100, 200, 100)
WALL_COLOR = (150, 75, 0)
CRATE_COLOR = (120, 60, 0)
ROCK_COLOR = (100, 100, 100)
TREE_COLOR = (34, 139, 34)
ENEMY_HAMBURGLAR_COLOR = (200, 50, 50)
ENEMY_SAUSAGE_COLOR = (255, 100, 0)
POWERUP_HEALTH_COLOR = (255, 200, 200)
POWERUP_SPEED_COLOR = (0, 255, 255)
PLAYER_COLOR = (0, 0, 255)
TACKLE_COLOR = (255, 255, 0)
PIGSKIN_THROW_COLOR = (200, 200, 255)
STICKY_PATCH_COLOR = (150, 100, 200)

PLAYER_BASE_SPEED = 4
PLAYER_DASH_SPEED_MULTIPLIER = 2.0
PLAYER_DASH_DURATION_MS = 150
PLAYER_DASH_COOLDOWN_MS = 1500
PLAYER_TACKLE_RANGE = 70
PLAYER_TACKLE_WIDTH = 60
PLAYER_TACKLE_DURATION_MS = 200
PLAYER_TACKLE_COOLDOWN_MS = 1000
PIGSKIN_THROW_SPEED = 8
PIGSKIN_THROW_COOLDOWN_MS = 500
PLAYER_MAX_HP = 100

ENEMY_HAMBURGLAR_HP = 30
ENEMY_HAMBURGLAR_SPEED = 3
ENEMY_SAUSAGE_HP = 20
ENEMY_SAUSAGE_SPEED = 5
ENEMY_SAUSAGE_ROLL_DURATION_MS = 1000
ENEMY_STUN_DURATION_MS = 1500
ENEMY_DAMAGE_PLAYER = 10
GOOEY_GUMMY_BEAR_HP = 40
GOOEY_GUMMY_BEAR_SPEED = 2
STICKY_PATCH_DURATION_MS = 5000
STICKY_PATCH_SLOW_FACTOR = 0.5

POWERUP_SPRINKLE_SPEED_DURATION_MS = 5000
POWERUP_WHIPPED_CREAM_SHIELD_DURATION_MS = 3000
POWERUP_EXTRA_CHEESE_TOSS_DURATION_MS = 7000

SCORE_TOUCHDOWN = 6
SCORE_FUMBLE_RECOVERY = 2
SCORE_COMBO_TACKLE_PER_ENEMY = 1

PLAYER_SIZE = 40
PIGSKIN_SIZE = 30
ENEMY_SIZE = 45
TARGET_ZONE_SIZE = 80
POWERUP_SIZE = 25
OBSTACLE_DEFAULT_SIZE = 50

# --- Game States Enum ---
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3
# --- LLM_INJECT_GAME_STATES_ENUM_ENHANCEMENTS ---
    PAUSED = 4
    LEVEL_COMPLETE = 5
# --- END LLM_INJECT_GAME_STATES_ENUM_ENHANCEMENTS ---

# --- State Management ---
current_state = GameState.MENU

# --- LLM_INJECT_GLOBAL_GAME_OBJECTS_SETUP ---
# Global variables for game objects and state
player_instance = None
pigskin_instance = None
target_zone_instance = None # This is a single sprite, not a group
all_sprites = pygame.sprite.Group()
player_sprite_group = pygame.sprite.GroupSingle() # Use GroupSingle for player for direct access
pigskin_sprite_group = pygame.sprite.GroupSingle() # Use GroupSingle for pigskin
enemy_sprites = pygame.sprite.Group()
obstacle_sprites = pygame.sprite.Group()
powerup_sprites = pygame.sprite.Group()
sticky_patches_sprites = pygame.sprite.Group() # For Gooey Gummy Bear

game_score = 0
level_start_time = 0
level_time_limit = 0 # Will be set by level data
player_has_pigskin = False

# Asset Path Handler (copied from G_ASSET_PATH_HANDLER)
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Placeholder image loading (since real files don't exist)
def load_assets():
    # Example: Player image
    global player_img, pigskin_img, hamburglar_img
    try:
        player_img_path = resource_path(os.path.join('assets', 'player.png'))
        if os.path.exists(player_img_path):
            player_img = pygame.image.load(player_img_path).convert_alpha()
            player_img = pygame.transform.scale(player_img, (PLAYER_SIZE, PLAYER_SIZE))
        else:
            player_img = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
            player_img.fill(PLAYER_COLOR)
    except Exception as e:
        player_img = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        player_img.fill(PLAYER_COLOR)
        print(f"Error loading player image: {e}. Using placeholder.")

    try:
        pigskin_img_path = resource_path(os.path.join('assets', 'pigskin.png'))
        if os.path.exists(pigskin_img_path):
            pigskin_img = pygame.image.load(pigskin_img_path).convert_alpha()
            pigskin_img = pygame.transform.scale(pigskin_img, (PIGSKIN_SIZE, PIGSKIN_SIZE))
        else:
            pigskin_img = pygame.Surface((PIGSKIN_SIZE, PIGSKIN_SIZE))
            pigskin_img.fill(PIGSKIN_COLOR)
    except Exception as e:
        pigskin_img = pygame.Surface((PIGSKIN_SIZE, PIGSKIN_SIZE))
        pigskin_img.fill(PIGSKIN_COLOR)
        print(f"Error loading pigskin image: {e}. Using placeholder.")
    
    try:
        hamburglar_img_path = resource_path(os.path.join('assets', 'hamburglar.png'))
        if os.path.exists(hamburglar_img_path):
            hamburglar_img = pygame.image.load(hamburglar_img_path).convert_alpha()
            hamburglar_img = pygame.transform.scale(hamburglar_img, (ENEMY_SIZE, ENEMY_SIZE))
        else:
            hamburglar_img = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
            hamburglar_img.fill(ENEMY_HAMBURGLAR_COLOR)
    except Exception as e:
        hamburglar_img = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
        hamburglar_img.fill(ENEMY_HAMBURGLAR_COLOR)
        print(f"Error loading hamburglar image: {e}. Using placeholder.")

# Call to load assets once at startup
load_assets()


# --- Classes (Consolidated from D_HEALTH_DAMAGE and E_BASIC_COLLISION) ---
class Entity(pygame.sprite.Sprite):
    def __init__(self, size, max_hp, position, image=None):
        super().__init__()
        if image:
            self.image = image
        else:
            self.image = pygame.Surface(size)
            self.image.fill(BLACK) # Default if no image/color specified
        self.rect = self.image.get_rect()
        self.rect.center = position
        
        self.max_health = max_hp
        self.current_health = max_hp
        self.is_alive = True
        self.last_hit_time = 0
        self.invulnerable_duration = 500 # ms after taking damage

        self.stun_timer = 0

    def take_damage(self, amount):
        if not self.is_alive or (pygame.time.get_ticks() - self.last_hit_time < self.invulnerable_duration):
            return
        
        self.current_health -= amount
        # print(f"{self.__class__.__name__} took damage: {amount}. Current HP: {self.current_health}")
        self.last_hit_time = pygame.time.get_ticks()
        
        if self.current_health <= 0:
            self.current_health = 0
            self.die()

    def heal(self, amount):
        if not self.is_alive:
            return
            
        self.current_health += amount
        self.current_health = min(self.current_health, self.max_health)
        # print(f"{self.__class__.__name__} healed: {amount}. Current HP: {self.current_health}")

    def die(self):
        self.is_alive = False
        # print(f"{self.__class__.__name__} died!")
        self.kill()

    def draw_health_bar(self, surface):
        if not self.is_alive or self.max_health <= 0:
            return

        BAR_WIDTH = self.rect.width
        BAR_HEIGHT = 5
        BAR_X = self.rect.x
        BAR_Y = self.rect.y - 10

        health_ratio = self.current_health / self.max_health
        fill_width = int(BAR_WIDTH * health_ratio)

        background_rect = pygame.Rect(BAR_X, BAR_Y, BAR_WIDTH, BAR_HEIGHT)
        pygame.draw.rect(surface, RED, background_rect)

        fill_rect = pygame.Rect(BAR_X, BAR_Y, fill_width, BAR_HEIGHT)
        pygame.draw.rect(surface, GREEN, fill_rect)

    def update(self):
        if self.stun_timer > 0:
            self.stun_timer -= clock.get_time()
            if self.stun_timer <= 0:
                self.stun_timer = 0

class Player(Entity):
    def __init__(self, position):
        super().__init__((PLAYER_SIZE, PLAYER_SIZE), PLAYER_MAX_HP, position, image=player_img)
        self.base_speed = PLAYER_BASE_SPEED
        self.speed = self.base_speed
        self.dx, self.dy = 0, 0
        self.old_x, self.old_y = position

        self.has_pigskin = False
        self.pigskin_ref = None

        self.dash_active = False
        self.dash_start_time = 0
        self.dash_cooldown_timer = 0
        
        self.tackle_active = False
        self.tackle_start_time = 0
        self.tackle_cooldown_timer = 0
        self.tackle_direction = (0, 0)

        self.throw_cooldown_timer = 0

        self.speed_boost_timer = 0
        self.invulnerable_shield_timer = 0
        self.extra_cheese_toss_timer = 0

        self.current_direction = (0, 1)

    def handle_input(self, keys):
        if self.stun_timer > 0:
            self.dx, self.dy = 0, 0
            return

        self.dx, self.dy = 0, 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.dx = -self.speed
            self.current_direction = (-1, 0)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.dx = self.speed
            self.current_direction = (1, 0)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.dy = -self.speed
            self.current_direction = (0, -1)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.dy = self.speed
            self.current_direction = (0, 1)

        if self.dx != 0 and self.dy != 0:
            self.dx /= math.sqrt(2)
            self.dy /= math.sqrt(2)
            self.current_direction = (self.dx / self.speed, self.dy / self.speed)

    def activate_dash(self):
        if self.dash_cooldown_timer <= 0 and not self.dash_active:
            self.dash_active = True
            self.dash_start_time = pygame.time.get_ticks()
            self.speed *= PLAYER_DASH_SPEED_MULTIPLIER
            self.dash_cooldown_timer = PLAYER_DASH_COOLDOWN_MS

    def activate_tackle(self):
        if self.tackle_cooldown_timer <= 0 and not self.tackle_active:
            self.tackle_active = True
            self.tackle_start_time = pygame.time.get_ticks()
            self.tackle_cooldown_timer = PLAYER_TACKLE_COOLDOWN_MS
            if self.dx == 0 and self.dy == 0:
                self.tackle_direction = self.current_direction
            else:
                current_move_vec = pygame.math.Vector2(self.dx, self.dy)
                if current_move_vec.length() > 0:
                    self.tackle_direction = current_move_vec.normalize()
                else: # Fallback if for some reason dx/dy are zero but we try to tackle
                    self.tackle_direction = self.current_direction

    def throw_pigskin(self, target_zone_sprite):
        if self.has_pigskin and self.pigskin_ref and self.throw_cooldown_timer <= 0:
            self.pigskin_ref.is_held = False
            self.pigskin_ref.is_thrown = True
            self.pigskin_ref.thrower = self
            self.pigskin_ref.rect.center = self.rect.center

            target_pos = target_zone_sprite.rect.center if target_zone_sprite else \
                         (self.rect.centerx + self.current_direction[0] * 200,
                          self.rect.centery + self.current_direction[1] * 200)

            start_pos = pygame.math.Vector2(self.rect.center)
            end_pos = pygame.math.Vector2(target_pos)
            direction_vector = (end_pos - start_pos).normalize()
            
            self.pigskin_ref.vel_x = direction_vector.x * PIGSKIN_THROW_SPEED
            self.pigskin_ref.vel_y = direction_vector.y * PIGSKIN_THROW_SPEED
            
            self.has_pigskin = False
            self.pigskin_ref = None
            self.throw_cooldown_timer = PIGSKIN_THROW_COOLDOWN_MS
            pigskin_sprite_group.add(self.pigskin_ref) # Re-add to group if it was temporarily removed

    def update(self, obstacles_group=None):
        super().update()

        dt = clock.get_time()

        if self.dash_cooldown_timer > 0: self.dash_cooldown_timer -= dt
        if self.tackle_cooldown_timer > 0: self.tackle_cooldown_timer -= dt
        if self.throw_cooldown_timer > 0: self.throw_cooldown_timer -= dt
        
        if self.dash_active:
            if pygame.time.get_ticks() - self.dash_start_time > PLAYER_DASH_DURATION_MS:
                self.dash_active = False
                self.speed = self.base_speed
        
        if self.tackle_active:
            if pygame.time.get_ticks() - self.tackle_start_time > PLAYER_TACKLE_DURATION_MS:
                self.tackle_active = False

        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= dt
            if self.speed_boost_timer <= 0:
                self.speed_boost_timer = 0
                self.speed = self.base_speed
        
        if self.invulnerable_shield_timer > 0:
            self.invulnerable_shield_timer -= dt
            if self.invulnerable_shield_timer <= 0:
                self.invulnerable_shield_timer = 0
        
        if self.extra_cheese_toss_timer > 0:
            self.extra_cheese_toss_timer -= dt
            if self.extra_cheese_toss_timer <= 0:
                self.extra_cheese_toss_timer = 0

        if self.speed_boost_timer > 0 and not self.dash_active:
             self.speed = self.base_speed * 1.5

        if self.stun_timer <= 0:
            self.old_x, self.old_y = self.rect.x, self.rect.y
            self.rect.x += self.dx
            self.rect.y += self.dy

            self.rect.left = max(0, self.rect.left)
            self.rect.right = min(SCREEN_WIDTH, self.rect.right)
            self.rect.top = max(0, self.rect.top)
            self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)

        if self.has_pigskin and self.pigskin_ref:
            self.pigskin_ref.rect.center = self.rect.center

    def draw(self, surface):
        surface.blit(self.image, self.rect)

        if self.tackle_active:
            tackle_effect_center = (self.rect.centerx + self.tackle_direction[0] * PLAYER_TACKLE_RANGE / 2,
                                    self.rect.centery + self.tackle_direction[1] * PLAYER_TACKLE_RANGE / 2)
            tackle_effect_rect = pygame.Rect(0,0, PLAYER_TACKLE_WIDTH, PLAYER_TACKLE_WIDTH)
            tackle_effect_rect.center = tackle_effect_center
            pygame.draw.rect(surface, TACKLE_COLOR, tackle_effect_rect, 2)

        if self.invulnerable_shield_timer > 0:
            pygame.draw.circle(surface, WHITE, self.rect.center, self.rect.width // 2 + 5, 2)

        self.draw_health_bar(surface)

class Pigskin(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image = pigskin_img
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.is_held = False
        self.is_thrown = False
        self.vel_x = 0
        self.vel_y = 0
        self.thrower = None

    def update(self):
        if self.is_thrown:
            self.rect.x += self.vel_x
            self.rect.y += self.vel_y
            self.vel_x *= 0.98
            self.vel_y *= 0.98
            if abs(self.vel_x) < 0.1 and abs(self.vel_y) < 0.1:
                self.is_thrown = False
                self.vel_x = 0
                self.vel_y = 0
            
            if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
                self.vel_x *= -1
            if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
                self.vel_y *= -1

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, obj_type="wall", color=None):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.type = obj_type
        
        if obj_type == "wall": self.image.fill(WALL_COLOR)
        elif obj_type == "crate": self.image.fill(CRATE_COLOR)
        elif obj_type == "rock": self.image.fill(ROCK_COLOR)
        elif obj_type == "tree": self.image.fill(TREE_COLOR)
        elif color: self.image.fill(color)
        else: self.image.fill(BLACK)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class TargetZone(pygame.sprite.Sprite):
    def __init__(self, x, y, width=TARGET_ZONE_SIZE, height=TARGET_ZONE_SIZE):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(ENDZONE_COLOR)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, pu_type):
        super().__init__()
        self.type = pu_type
        self.image = pygame.Surface((POWERUP_SIZE, POWERUP_SIZE))
        
        if self.type == "health": self.image.fill(POWERUP_HEALTH_COLOR)
        elif self.type == "speed_boost": self.image.fill(POWERUP_SPEED_COLOR)
        elif self.type == "shield": self.image.fill(WHITE)
        elif self.type == "cheese_toss": self.image.fill(TACKLE_COLOR)
        else: self.image.fill(WHITE)
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class HungryHamburglar(Entity):
    def __init__(self, position, patrol_path=None):
        super().__init__((ENEMY_SIZE, ENEMY_SIZE), ENEMY_HAMBURGLAR_HP, position, image=hamburglar_img)
        self.speed = ENEMY_HAMBURGLAR_SPEED
        self.patrol_path = [pygame.math.Vector2(p) for p in patrol_path] if patrol_path else []
        self.current_patrol_index = 0
        self.target_position = None
        self.is_chasing = False
        self.vision_range = 200
        self.last_player_pos = None

    def update(self, player_pos):
        super().update()
        if not self.is_alive or self.stun_timer > 0:
            return

        current_pos_vec = pygame.math.Vector2(self.rect.center)
        player_pos_vec = pygame.math.Vector2(player_pos)
        distance_to_player = current_pos_vec.distance_to(player_pos_vec)

        if distance_to_player < self.vision_range:
            self.is_chasing = True
            self.target_position = player_pos_vec
            self.last_player_pos = player_pos_vec
        elif self.is_chasing and self.last_player_pos and current_pos_vec.distance_to(self.last_player_pos) < self.speed:
            self.is_chasing = False
            self.target_position = None
            self.last_player_pos = None
        
        if self.is_chasing and self.target_position:
            move_direction = (self.target_position - current_pos_vec).normalize()
            self.rect.x += move_direction.x * self.speed
            self.rect.y += move_direction.y * self.speed
        elif self.patrol_path:
            if not self.target_position or current_pos_vec.distance_to(self.target_position) < self.speed:
                self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_path)
                self.target_position = self.patrol_path[self.current_patrol_index]
            
            move_direction = (self.target_position - current_pos_vec).normalize()
            self.rect.x += move_direction.x * self.speed
            self.rect.y += move_direction.y * self.speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        self.draw_health_bar(surface)

class SpicySausage(Entity):
    def __init__(self, position, patrol_path=None):
        super().__init__((ENEMY_SIZE, ENEMY_SIZE), ENEMY_SAUSAGE_HP, position, image=pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))) # No specific image for sausage
        self.image.fill(ENEMY_SAUSAGE_COLOR)
        self.base_speed = ENEMY_SAUSAGE_SPEED
        self.speed = self.base_speed
        self.patrol_path = [pygame.math.Vector2(p) for p in patrol_path] if patrol_path else []
        self.current_patrol_index = 0
        self.target_position = None
        self.is_rolling = False
        self.roll_target = None
        self.roll_start_time = 0
        self.vision_range = 150

    def start_roll(self, player_pos):
        if not self.is_rolling:
            self.is_rolling = True
            self.roll_start_time = pygame.time.get_ticks()
            self.roll_target = pygame.math.Vector2(player_pos)
            current_pos_vec = pygame.math.Vector2(self.rect.center)
            direction_vector = (self.roll_target - current_pos_vec).normalize()
            self.roll_vel_x = direction_vector.x * (self.speed * 1.5)
            self.roll_vel_y = direction_vector.y * (self.speed * 1.5)

    def update(self, player_pos):
        super().update()
        if not self.is_alive or self.stun_timer > 0:
            return

        current_pos_vec = pygame.math.Vector2(self.rect.center)
        player_pos_vec = pygame.math.Vector2(player_pos)
        distance_to_player = current_pos_vec.distance_to(player_pos_vec)

        if self.is_rolling:
            if pygame.time.get_ticks() - self.roll_start_time > ENEMY_SAUSAGE_ROLL_DURATION_MS:
                self.is_rolling = False
                self.roll_target = None
                self.roll_vel_x, self.roll_vel_y = 0, 0
            else:
                self.rect.x += self.roll_vel_x
                self.rect.y += self.roll_vel_y
                return
        
        if distance_to_player < self.vision_range and not self.is_rolling:
            self.start_roll(player_pos)
        
        elif self.patrol_path and not self.is_rolling:
            if not self.target_position or current_pos_vec.distance_to(self.target_position) < self.speed:
                self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_path)
                self.target_position = self.patrol_path[self.current_patrol_index]
            
            move_direction = (self.target_position - current_pos_vec).normalize()
            self.rect.x += move_direction.x * self.speed
            self.rect.y += move_direction.y * self.speed
            
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        self.draw_health_bar(surface)

# Level data (from JSON provided in prompt)
level_1_data_json = {
  "level_number": 1,
  "name": "The Rookie Ruckus",
  "description": "Welcome to Fumble Frenzy! Your first challenge is to navigate a small, open field, learning the basics of movement and passing. Dodge the initial few blockers and secure the pigskin to reach the endzone!",
  "size": {
    "width": 800,
    "height": 600
  },
  "spawn_points": [
    {
      "x": 100,
      "y": 100,
      "type": "player"
    },
    {
      "x": 700,
      "y": 500,
      "type": "target_zone"
    }
  ],
  "obstacles": [
    {
      "x": 200,
      "y": 200,
      "width": 50,
      "height": 50,
      "type": "wall"
    },
    {
      "x": 300,
      "y": 300,
      "width": 60,
      "height": 40,
      "type": "crate"
    },
    {
      "x": 500,
      "y": 400,
      "width": 30,
      "height": 30,
      "type": "rock"
    },
    {
      "x": 400,
      "y": 150,
      "width": 40,
      "height": 60,
      "type": "tree"
    }
  ],
  "powerups": [
    {
      "x": 300,
      "y": 150,
      "type": "health"
    },
    {
      "x": 650,
      "y": 550,
      "type": "speed_boost"
    }
  ],
  "enemies": [
    {
      "x": 350,
      "y": 250,
      "type": "blocker",
      "patrol_path": [
        [
          350,
          250
        ],
        [
          420,
          250
        ],
        [
          420,
          280
        ],
        [
          350,
          280
        ]
      ]
    },
    {
      "x": 550,
      "y": 200,
      "type": "blocker",
      "patrol_path": [
        [
          550,
          200
        ],
        [
          550,
          270
        ],
        [
          580,
          270
        ],
        [
          580,
          200
        ]
      ]
    },
    {
      "x": 150,
      "y": 450,
      "type": "chaser",
      "patrol_path": [
        [
          150,
          450
        ],
        [
          220,
          450
        ]
      ]
    }
  ],
  "objectives": [
    {
      "type": "reach_zone",
      "target": "target_zone",
      "count": 1
    },
    {
      "type": "collect",
      "target": "pigskin",
      "count": 1
    }
  ],
  "difficulty": "easy",
  "time_limit": 180
}


def load_level(level_data):
    global player_instance, pigskin_instance, target_zone_instance, game_score, player_has_pigskin, level_time_limit, level_start_time

    all_sprites.empty()
    player_sprite_group.empty()
    pigskin_sprite_group.empty()
    enemy_sprites.empty()
    obstacle_sprites.empty()
    powerup_sprites.empty()
    sticky_patches_sprites.empty() # No gummy bear in level 1, but keeps group clean

    # Reset game state for new level
    game_score = 0
    player_has_pigskin = False
    level_time_limit = level_data["time_limit"]
    level_start_time = pygame.time.get_ticks()

    player_spawn = level_data["spawn_points"][0]
    player_instance = Player((player_spawn["x"], player_spawn["y"]))
    player_sprite_group.add(player_instance)
    all_sprites.add(player_instance)

    pigskin_instance = Pigskin((player_spawn["x"] + 20, player_spawn["y"]))
    pigskin_sprite_group.add(pigskin_instance)
    all_sprites.add(pigskin_instance)

    target_zone_data = next((sp for sp in level_data["spawn_points"] if sp["type"] == "target_zone"), None)
    if target_zone_data:
        target_zone_instance = TargetZone(target_zone_data["x"], target_zone_data["y"])
        all_sprites.add(target_zone_instance)
    else:
        target_zone_instance = None


    for obs_data in level_data["obstacles"]:
        obs_instance = Obstacle(obs_data["x"], obs_data["y"], obs_data["width"], obs_data["height"], obs_data["type"])
        obstacle_sprites.add(obs_instance)
        all_sprites.add(obs_instance)

    for pu_data in level_data["powerups"]:
        pu_instance = PowerUp(pu_data["x"], pu_data["y"], pu_data["type"])
        powerup_sprites.add(pu_instance)
        all_sprites.add(pu_instance)

    for enemy_data in level_data["enemies"]:
        enemy_type = enemy_data["type"]
        pos = (enemy_data["x"], enemy_data["y"])
        patrol_path = enemy_data.get("patrol_path")

        if enemy_type == "blocker":
            enemy_instance = HungryHamburglar(pos, patrol_path)
        elif enemy_type == "chaser":
            enemy_instance = SpicySausage(pos, patrol_path)
        else:
            continue
        
        enemy_sprites.add(enemy_instance)
        all_sprites.add(enemy_instance)

# --- END LLM_INJECT_GLOBAL_GAME_OBJECTS_SETUP ---

# --- LLM_INJECT_STATE_SPECIFIC_RESET_LOGIC ---
def reset_game():
    global current_state, game_score, player_has_pigskin
    game_score = 0
    player_has_pigskin = False
    current_state = GameState.MENU

def start_level_1():
    global current_state, level_start_time
    load_level(level_1_data_json)
    level_start_time = pygame.time.get_ticks()
    current_state = GameState.PLAYING
# --- END LLM_INJECT_STATE_SPECIFIC_RESET_LOGIC ---

# --- State Functions ---
# --- LLM_INJECT_STATE_FUNCTIONS_IMPLEMENTATION ---
def run_menu(events):
    global current_state
    
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                start_level_1()
    
    screen.fill(BLACK)
    title_text = FONT.render("FUMBLE FRENZY: PIGSKIN PURSUIT", True, WHITE)
    start_text = SMALL_FONT.render("PRESS SPACE TO START", True, WHITE)
    
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))


def run_playing(events):
    global current_state, game_score, player_has_pigskin, level_start_time, level_time_limit

    player = player_instance # Player object directly, not group

    # Event handling for player abilities
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p: # Pause
                current_state = GameState.PAUSED
            if event.key == pygame.K_SPACE: # Dash
                player.activate_dash()
            if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT: # Tackle
                player.activate_tackle()
            if event.key == pygame.K_e: # Throw Pigskin (Pass)
                if player.has_pigskin and target_zone_instance:
                    player.throw_pigskin(target_zone_instance)
                elif player.has_pigskin: # Fallback if no target zone
                    player.throw_pigskin(None)

    # Handle continuous player input
    keys = pygame.key.get_pressed()
    player.handle_input(keys)

    # --- Update Logic ---
    player.update(obstacle_sprites)
    
    if pigskin_instance:
        pigskin_instance.update()
    
    for enemy in enemy_sprites:
        enemy.update(player.rect.center)
    
    # --- Collision Detection and Resolution ---
    # Player-Obstacle Collision
    player.old_x, player.old_y = player.rect.x, player.rect.y
    player.rect.x += player.dx
    for obstacle in pygame.sprite.spritecollide(player, obstacle_sprites, False):
        if player.dx > 0: player.rect.right = obstacle.rect.left
        elif player.dx < 0: player.rect.left = obstacle.rect.right
        player.dx = 0
    player.rect.y += player.dy
    for obstacle in pygame.sprite.spritecollide(player, obstacle_sprites, False):
        if player.dy > 0: player.rect.bottom = obstacle.rect.top
        elif player.dy < 0: player.rect.top = obstacle.rect.bottom
        player.dy = 0

    # Pigskin-Obstacle Collision
    if pigskin_instance and pigskin_instance.is_thrown:
        for obstacle in pygame.sprite.spritecollide(pigskin_instance, obstacle_sprites, False):
            if abs(pigskin_instance.vel_x) > abs(pigskin_instance.vel_y): pigskin_instance.vel_x *= -1
            else: pigskin_instance.vel_y *= -1
            if pigskin_instance.rect.colliderect(obstacle.rect): # Adjust position to prevent sticking
                if pigskin_instance.vel_x < 0: pigskin_instance.rect.left = obstacle.rect.right
                elif pigskin_instance.vel_x > 0: pigskin_instance.rect.right = obstacle.rect.left
                if pigskin_instance.vel_y < 0: pigskin_instance.rect.top = obstacle.rect.bottom
                elif pigskin_instance.vel_y > 0: pigskin_instance.rect.bottom = obstacle.rect.top

    # Player-Pigskin interaction
    if not player.has_pigskin and pigskin_instance and not pigskin_instance.is_thrown and pigskin_instance.is_alive:
        if pygame.sprite.collide_rect(player, pigskin_instance):
            player.has_pigskin = True
            player.pigskin_ref = pigskin_instance
            pigskin_instance.is_held = True
            game_score += SCORE_FUMBLE_RECOVERY # Fumble recovery points

    # Player-Enemy collision (Player takes damage, enemy might be stunned)
    if not player.invulnerable_shield_timer > 0:
        collided_enemies = pygame.sprite.spritecollide(player, enemy_sprites, False)
        for enemy in collided_enemies:
            if enemy.stun_timer <= 0:
                player.take_damage(ENEMY_DAMAGE_PLAYER)
                # Simple knockback
                direction = pygame.math.Vector2(player.rect.center) - pygame.math.Vector2(enemy.rect.center)
                if direction.length() > 0:
                    direction = direction.normalize()
                    player.rect.x += direction.x * 20
                    player.rect.y += direction.y * 20
                if not player.is_alive: current_state = GameState.GAME_OVER
    
    # Player Tackle-Enemy collision
    if player.tackle_active:
        tackle_rect_center = (player.rect.centerx + player.tackle_direction[0] * (PLAYER_TACKLE_RANGE // 2),
                              player.rect.centery + player.tackle_direction[1] * (PLAYER_TACKLE_RANGE // 2))
        tackle_hitbox = pygame.Rect(0, 0, PLAYER_TACKLE_WIDTH, PLAYER_TACKLE_WIDTH)
        tackle_hitbox.center = tackle_rect_center

        tackled_enemies = pygame.sprite.spritecollide(tackle_hitbox, enemy_sprites, False)
        num_tackled = 0
        for enemy in tackled_enemies:
            if enemy.stun_timer <= 0:
                enemy.stun_timer = ENEMY_STUN_DURATION_MS
                enemy.take_damage(10)
                num_tackled += 1
        if num_tackled > 0:
            game_score += SCORE_COMBO_TACKLE_PER_ENEMY * num_tackled
    
    # Player-PowerUp collision
    powerup_hits = pygame.sprite.spritecollide(player, powerup_sprites, True)
    for powerup in powerup_hits:
        if powerup.type == "health": player.heal(25)
        elif powerup.type == "speed_boost": player.speed_boost_timer = POWERUP_SPRINKLE_SPEED_DURATION_MS
        elif powerup.type == "shield": player.invulnerable_shield_timer = POWERUP_WHIPPED_CREAM_SHIELD_DURATION_MS
        elif powerup.type == "cheese_toss": player.extra_cheese_toss_timer = POWERUP_EXTRA_CHEESE_TOSS_DURATION_MS

    # Pigskin-Target Zone collision (Touchdown!)
    if pigskin_instance and not pigskin_instance.is_held and pigskin_instance.is_alive and target_zone_instance:
        if pygame.sprite.collide_rect(pigskin_instance, target_zone_instance):
            game_score += SCORE_TOUCHDOWN
            player_has_pigskin = False
            pigskin_instance.kill()
            current_state = GameState.LEVEL_COMPLETE

    # Check player health for Game Over
    if not player.is_alive:
        current_state = GameState.GAME_OVER
    
    # Check Time Limit
    elapsed_time = (pygame.time.get_ticks() - level_start_time) // 1000
    if elapsed_time >= level_time_limit:
        current_state = GameState.GAME_OVER
    
    # --- Drawing ---
    screen.fill((50, 100, 50)) # Green field background
    
    if target_zone_instance:
        target_zone_instance.draw(screen)

    for sprite in all_sprites:
        if isinstance(sprite, Player): sprite.draw(screen)
        elif isinstance(sprite, Pigskin): sprite.draw(screen)
        elif isinstance(sprite, Obstacle): sprite.draw(screen)
        elif isinstance(sprite, PowerUp): sprite.draw(screen)
        elif isinstance(sprite, HungryHamburglar) or isinstance(sprite, SpicySausage):
            sprite.draw(screen)
            sprite.draw_health_bar(screen) # Draw health for enemies

    score_text = SMALL_FONT.render(f"Score: {game_score}", True, WHITE)
    time_left = max(0, level_time_limit - elapsed_time)
    timer_text = SMALL_FONT.render(f"Time: {time_left}s", True, WHITE)
    player_hp_text = SMALL_FONT.render(f"HP: {player.current_health}/{player.max_health}", True, WHITE)
    
    screen.blit(score_text, (10, 10))
    screen.blit(timer_text, (SCREEN_WIDTH - timer_text.get_width() - 10, 10))
    screen.blit(player_hp_text, (10, 40))


def run_game_over(events):
    global current_state
    
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_game()
    
    screen.fill(BLACK)
    over_text = FONT.render("GAME OVER", True, RED)
    final_score_text = SMALL_FONT.render(f"Final Score: {game_score}", True, WHITE)
    restart_text = SMALL_FONT.render("Press 'R' to return to Menu", True, WHITE)
    
    screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))

def run_level_complete(events):
    global current_state
    
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_n: # N for Next Level (or just restart to menu for this template)
                reset_game()
    
    screen.fill((0, 50, 100)) # Dark blue for win screen
    complete_text = FONT.render("LEVEL COMPLETE!", True, GREEN)
    level_score_text = SMALL_FONT.render(f"Score: {game_score}", True, WHITE)
    next_level_text = SMALL_FONT.render("Press 'N' to continue to Menu", True, WHITE) # Adjusted for single level template
    
    screen.blit(complete_text, (SCREEN_WIDTH // 2 - complete_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(level_score_text, (SCREEN_WIDTH // 2 - level_score_text.get_width() // 2, SCREEN_HEIGHT // 2))
    screen.blit(next_level_text, (SCREEN_WIDTH // 2 - next_level_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))

def run_paused(events):
    global current_state
    
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p: # Resume
                current_state = GameState.PLAYING
    
    screen.fill(BLACK)
    pause_text = FONT.render("PAUSED", True, WHITE)
    resume_text = SMALL_FONT.render("Press 'P' to Resume", True, WHITE)
    
    screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
# --- END LLM_INJECT_STATE_FUNCTIONS_IMPLEMENTATION ---

# --- Main Game Loop ---
running = True
while running:
    # 1. Event Handling (Collects all events for the current frame)
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
            
    # 2. State Logic (Calls the appropriate function based on the current state)
    if current_state == GameState.MENU:
        run_menu(events)
    elif current_state == GameState.PLAYING:
        run_playing(events)
    elif current_state == GameState.GAME_OVER:
        run_game_over(events)
    elif current_state == GameState.PAUSED:
        run_paused(events)
    elif current_state == GameState.LEVEL_COMPLETE:
        run_level_complete(events)
    
    # 3. Drawing
    pygame.display.flip()
    
    # 4. Cap the frame rate
    clock.tick(FPS)

# --- Cleanup ---
pygame.quit()
sys.exit()


# --- TEMPLATE: G_ASSET_PATH_HANDLER ---
import os
import sys
import pygame

# --- Constants & Initialization (Assumed from A) ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Template G: Asset Path Handler")
clock = pygame.time.Clock()
FPS = 60
WHITE = (255, 255, 255)
RED = (255, 0, 0)
FONT = pygame.font.Font(None, 36)

# --- Asset Path Handler Function ---
def resource_path(relative_path):
    """
    Get the absolute path to resource, works for dev and for PyInstaller.
    
    During development, it returns the path relative to the script.
    When compiled by PyInstaller, it returns the path inside the bundled MEIPASS folder.
    """
    try:
        # PyInstaller creates a temporary folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Not running as a compiled executable, use the current script directory
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- Placeholder Asset Usage ---
# NOTE: This example requires you to create a dummy 'assets' folder with a 'test.txt' 
# and a 'player.png' file in the same directory as this script for the paths to work in dev mode.

# Example 1: Load a text file (using the handler)
asset_status_text = "Asset Path Status: Loading..."
try:
    # Assume we are trying to load an asset located at 'assets/test.txt'
    text_file_path = resource_path(os.path.join('assets', 'test.txt'))
    
    # Check if the path points to an existing file (optional, but good for debugging)
    if os.path.exists(text_file_path):
        with open(text_file_path, 'r') as f:
            content = f.read().strip()
            asset_status_text = f"Text Asset Loaded: '{content}'"
    else:
        # If running in dev mode, this path won't exist until you create the 'assets' folder/file
        asset_status_text = "Asset Path Handler OK. Placeholder file not found."

except Exception as e:
    asset_status_text = f"Error loading asset: {e}"


# Example 2: Load an image (using the handler)
# Creating a dummy image surface since we can't guarantee 'player.png' exists
# --- LLM_INJECT_PLACEHOLDER_ASSET_LOADING ---
player_img_path = resource_path(os.path.join('assets', 'player.png'))
pigskin_img_path = resource_path(os.path.join('assets', 'pigskin.png'))
enemy_hamburglar_img_path = resource_path(os.path.join('assets', 'hamburglar.png'))

player_img = None
pigskin_img = None
enemy_hamburglar_img = None

try:
    if os.path.exists(player_img_path):
        player_img = pygame.image.load(player_img_path).convert_alpha()
        player_img = pygame.transform.scale(player_img, (50, 50)) # Scale for display
    else:
        player_img = pygame.Surface((50, 50))
        player_img.fill((0, 0, 255)) # Default blue
        asset_status_text += "\nPlayer image not found, using placeholder."
except Exception:
    player_img = pygame.Surface((50, 50))
    player_img.fill((0, 0, 255))
    asset_status_text += "\nError loading player image, using placeholder."

try:
    if os.path.exists(pigskin_img_path):
        pigskin_img = pygame.image.load(pigskin_img_path).convert_alpha()
        pigskin_img = pygame.transform.scale(pigskin_img, (40, 40)) # Scale for display
    else:
        pigskin_img = pygame.Surface((40, 40))
        pigskin_img.fill((255, 220, 150)) # Pigskin color
        asset_status_text += "\nPigskin image not found, using placeholder."
except Exception:
    pigskin_img = pygame.Surface((40, 40))
    pigskin_img.fill((255, 220, 150))
    asset_status_text += "\nError loading pigskin image, using placeholder."

try:
    if os.path.exists(enemy_hamburglar_img_path):
        enemy_hamburglar_img = pygame.image.load(enemy_hamburglar_img_path).convert_alpha()
        enemy_hamburglar_img = pygame.transform.scale(enemy_hamburglar_img, (60, 60)) # Scale for display
    else:
        enemy_hamburglar_img = pygame.Surface((60, 60))
        enemy_hamburglar_img.fill((200, 50, 50)) # Hamburglar color
        asset_status_text += "\nHamburglar image not found, using placeholder."
except Exception:
    enemy_hamburglar_img = pygame.Surface((60, 60))
    enemy_hamburglar_img.fill((200, 50, 50))
    asset_status_text += "\nError loading hamburglar image, using placeholder."
    
player_rect = player_img.get_rect(center=(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
pigskin_rect = pigskin_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
enemy_rect = enemy_hamburglar_img.get_rect(center=(SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2))
# --- END LLM_INJECT_PLACEHOLDER_ASSET_LOADING ---

# --- Main Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 1. Update
    
    # 2. Drawing
    screen.fill(WHITE)
    
    # --- LLM_INJECT_ASSET_DISPLAY_LOGIC ---
    # Draw the loaded (or placeholder) images
    if player_img:
        screen.blit(player_img, player_rect)
    if pigskin_img:
        screen.blit(pigskin_img, pigskin_rect)
    if enemy_hamburglar_img:
        screen.blit(enemy_hamburglar_img, enemy_rect)
    
    # Display the status of the asset path handler
    status_surface = FONT.render(asset_status_text, True, (0, 0, 0))
    path_info = FONT.render(f"Path Check: {'_MEIPASS' in sys.modules and sys.frozen}", True, (0, 0, 0))
    
    screen.blit(status_surface, (50, 50))
    screen.blit(path_info, (50, 100 + status_surface.get_height())) # Adjust position
    
    # Add labels for images
    player_label = SMALL_FONT.render("Player", True, BLACK)
    pigskin_label = SMALL_FONT.render("Pigskin", True, BLACK)
    enemy_label = SMALL_FONT.render("Enemy", True, BLACK)
    
    screen.blit(player_label, (player_rect.x, player_rect.y - 20))
    screen.blit(pigskin_label, (pigskin_rect.x, pigskin_rect.y - 20))
    screen.blit(enemy_label, (enemy_rect.x, enemy_rect.y - 20))
    # --- END LLM_INJECT_ASSET_DISPLAY_LOGIC ---
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()


# --- TEMPLATE: B_MOVEMENT_TOPDOWN ---
import pygame
import math # Needed for player direction/tackle

# --- Constants & Initialization (Assumed from A) ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
FPS = 60
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# --- Game-specific Constants (Duplicated for template isolation) ---
PIGSKIN_COLOR = (255, 220, 150)
ENEMY_HAMBURGLAR_COLOR = (200, 50, 50)
TACKLE_COLOR = (255, 255, 0)

PLAYER_BASE_SPEED = 4
PLAYER_DASH_SPEED_MULTIPLIER = 2.0
PLAYER_DASH_DURATION_MS = 150
PLAYER_DASH_COOLDOWN_MS = 1500
PLAYER_TACKLE_RANGE = 70
PLAYER_TACKLE_WIDTH = 60
PLAYER_TACKLE_DURATION_MS = 200
PLAYER_TACKLE_COOLDOWN_MS = 1000
PIGSKIN_THROW_SPEED = 8
PIGSKIN_THROW_COOLDOWN_MS = 500

PLAYER_SIZE = 50 # Default from template, use for consistency in this template
PIGSKIN_SIZE = 30
ENEMY_SIZE = 45
# --- END Game-specific Constants ---

# --- Player Class for Top-Down Movement ---
# --- LLM_INJECT_PLAYER_CLASS_ENHANCEMENTS ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([PLAYER_SIZE, PLAYER_SIZE])
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        self.base_speed = PLAYER_BASE_SPEED
        self.speed = self.base_speed
        self.current_direction = (0, 1) # Default to facing down

        self.has_pigskin = False
        self.pigskin_ref = None # Reference to the Pigskin object

        # Abilities
        self.dash_active = False
        self.dash_start_time = 0
        self.dash_cooldown_timer = 0
        
        self.tackle_active = False
        self.tackle_start_time = 0
        self.tackle_cooldown_timer = 0
        self.tackle_direction = (0, 0)

        self.throw_cooldown_timer = 0

    def activate_dash(self):
        if self.dash_cooldown_timer <= 0 and not self.dash_active:
            self.dash_active = True
            self.dash_start_time = pygame.time.get_ticks()
            self.speed *= PLAYER_DASH_SPEED_MULTIPLIER
            self.dash_cooldown_timer = PLAYER_DASH_COOLDOWN_MS
            # print("Dash activated!")

    def activate_tackle(self):
        if self.tackle_cooldown_timer <= 0 and not self.tackle_active:
            self.tackle_active = True
            self.tackle_start_time = pygame.time.get_ticks()
            self.tackle_cooldown_timer = PLAYER_TACKLE_COOLDOWN_MS
            # Use current movement direction, or a default if stationary
            keys = pygame.key.get_pressed()
            dx_input, dy_input = 0, 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx_input = -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx_input = 1
            if keys[pygame.K_UP] or keys[pygame.K_w]: dy_input = -1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy_input = 1

            if dx_input == 0 and dy_input == 0:
                self.tackle_direction = self.current_direction
            else:
                input_vec = pygame.math.Vector2(dx_input, dy_input).normalize()
                self.tackle_direction = (input_vec.x, input_vec.y)
            # print(f"Tackle activated! Direction: {self.tackle_direction}")

    def throw_pigskin(self, pigskin_group):
        if self.has_pigskin and self.pigskin_ref and self.throw_cooldown_timer <= 0:
            # print("Throwing pigskin!")
            self.pigskin_ref.is_held = False
            self.pigskin_ref.is_thrown = True
            self.pigskin_ref.thrower = self # Player threw it
            self.pigskin_ref.rect.center = self.rect.center # Detach from player

            # Throw in current player direction
            self.pigskin_ref.vel_x = self.current_direction[0] * PIGSKIN_THROW_SPEED
            self.pigskin_ref.vel_y = self.current_direction[1] * PIGSKIN_THROW_SPEED
            
            self.has_pigskin = False
            self.pigskin_ref = None
            self.throw_cooldown_timer = PIGSKIN_THROW_COOLDOWN_MS
            if self.pigskin_ref not in pigskin_group: # Ensure pigskin is in a group
                pigskin_group.add(self.pigskin_ref)


    def update(self):
        dt = clock.get_time()
        
        # Update cooldown timers
        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= dt
        if self.tackle_cooldown_timer > 0:
            self.tackle_cooldown_timer -= dt
        if self.throw_cooldown_timer > 0:
            self.throw_cooldown_timer -= dt
        
        # Handle dash state
        if self.dash_active:
            if pygame.time.get_ticks() - self.dash_start_time > PLAYER_DASH_DURATION_MS:
                self.dash_active = False
                self.speed = self.base_speed # Revert speed
                # print("Dash ended.")
        
        # Handle tackle state
        if self.tackle_active:
            if pygame.time.get_ticks() - self.tackle_start_time > PLAYER_TACKLE_DURATION_MS:
                self.tackle_active = False
                # print("Tackle ended.")

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -self.speed
            self.current_direction = (-1, 0)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.speed
            self.current_direction = (1, 0)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -self.speed
            self.current_direction = (0, -1)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = self.speed
            self.current_direction = (0, 1)

        # Diagonal movement
        if dx != 0 and dy != 0:
            dx /= math.sqrt(2)
            dy /= math.sqrt(2)
            self.current_direction = (dx / self.speed, dy / self.speed)

        # Update position
        self.rect.x += dx
        self.rect.y += dy
        
        # Keep player within screen bounds (simple boundary checking)
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)

        # If holding pigskin, it follows the player
        if self.has_pigskin and self.pigskin_ref:
            self.pigskin_ref.rect.center = self.rect.center

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        # Draw tackle range visualization if active
        if self.tackle_active:
            tackle_effect_center = (self.rect.centerx + self.tackle_direction[0] * (PLAYER_TACKLE_RANGE / 2),
                                    self.rect.centery + self.tackle_direction[1] * (PLAYER_TACKLE_RANGE / 2))
            tackle_effect_rect = pygame.Rect(0,0, PLAYER_TACKLE_WIDTH, PLAYER_TACKLE_WIDTH)
            tackle_effect_rect.center = tackle_effect_center
            pygame.draw.rect(surface, TACKLE_COLOR, tackle_effect_rect, 2) # Draw outline
# --- END LLM_INJECT_PLAYER_CLASS_ENHANCEMENTS ---

# --- Game-specific classes for this template's context ---
class Pigskin(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image = pygame.Surface((PIGSKIN_SIZE, PIGSKIN_SIZE))
        self.image.fill(PIGSKIN_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.is_held = False
        self.is_thrown = False
        self.vel_x = 0
        self.vel_y = 0
        self.thrower = None

    def update(self):
        if self.is_thrown:
            self.rect.x += self.vel_x
            self.rect.y += self.vel_y
            # Simple friction/slowdown for thrown pigskin
            self.vel_x *= 0.98
            self.vel_y *= 0.98
            if abs(self.vel_x) < 0.1 and abs(self.vel_y) < 0.1:
                self.is_thrown = False
                self.vel_x = 0
                self.vel_y = 0
            
            # Keep within bounds, simple bounce for now
            if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
                self.vel_x *= -1
            if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
                self.vel_y *= -1

class Enemy(pygame.sprite.Sprite): # Generic enemy for collision/tackle test
    def __init__(self, position):
        super().__init__()
        self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
        self.image.fill(ENEMY_HAMBURGLAR_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = position

    def update(self):
        pass # No complex logic needed for this template example


# --- Game Setup ---
# --- LLM_INJECT_GAME_SETUP_CUSTOM_CLASSES ---
all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

pigskin = Pigskin((SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2)) # Spawn pigskin near player
all_sprites.add(pigskin)
pigskin_sprites = pygame.sprite.GroupSingle(pigskin) # Group for pigskin

enemy = Enemy((SCREEN_WIDTH * 3 // 4, SCREEN_HEIGHT // 2)) # Spawn an enemy for tackle test
all_sprites.add(enemy)
enemy_sprites = pygame.sprite.GroupSingle(enemy) # Group for enemies (single for this example)

# --- END LLM_INJECT_GAME_SETUP_CUSTOM_CLASSES ---

# --- Main Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE: # Dash ability
                player.activate_dash()
            if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT: # Tackle ability
                player.activate_tackle()
            if event.key == pygame.K_e: # Throw Pigskin (Pass)
                player.throw_pigskin(pigskin_sprites)
            if event.key == pygame.K_p and not player.has_pigskin: # Pick up pigskin for testing
                # For this template, pick up if nearby or simulate
                if pygame.sprite.collide_rect(player, pigskin):
                    player.has_pigskin = True
                    player.pigskin_ref = pigskin
                    pigskin.is_held = True
                    # print("Player picked up pigskin for test.")


    # 1. Update (The player's position and abilities are updated here)
    # --- LLM_INJECT_GAME_LOGIC_AND_INTERACTIONS ---
    all_sprites.update()

    # Player-Pigskin interaction
    if not player.has_pigskin and pigskin.is_alive and not pigskin.is_thrown:
        if pygame.sprite.collide_rect(player, pigskin):
            player.has_pigskin = True
            player.pigskin_ref = pigskin
            pigskin.is_held = True
            # print("Player picked up pigskin!")

    # Player Tackle-Enemy collision
    if player.tackle_active:
        tackle_rect_center = (player.rect.centerx + player.tackle_direction[0] * (PLAYER_TACKLE_RANGE / 2),
                              player.rect.centery + player.tackle_direction[1] * (PLAYER_TACKLE_RANGE / 2))
        tackle_hitbox = pygame.Rect(0, 0, PLAYER_TACKLE_WIDTH, PLAYER_TACKLE_WIDTH)
        tackle_hitbox.center = tackle_rect_center

        if pygame.sprite.spritecollide(tackle_hitbox, enemy_sprites, False):
            # print("Player tackled an enemy!")
            # In a full game, enemy would be stunned/damaged
            pass

    # Pigskin movement (if thrown)
    if pigskin.is_thrown:
        pigskin.update()
    # --- END LLM_INJECT_GAME_LOGIC_AND_INTERACTIONS ---

    # 2. Drawing
    screen.fill(WHITE)
    
    # Use custom draw for player to show ability effects
    for sprite in all_sprites:
        if isinstance(sprite, Player):
            sprite.draw(screen)
        else:
            screen.blit(sprite.image, sprite.rect)

    # Display status
    font = pygame.font.Font(None, 30)
    dash_cd_text = font.render(f"Dash CD: {max(0, player.dash_cooldown_timer / 1000):.1f}s (SPACE)", True, BLACK)
    screen.blit(dash_cd_text, (10, 10))
    tackle_cd_text = font.render(f"Tackle CD: {max(0, player.tackle_cooldown_timer / 1000):.1f}s (SHIFT)", True, BLACK)
    screen.blit(tackle_cd_text, (10, 40))
    throw_cd_text = font.render(f"Throw CD: {max(0, player.throw_cooldown_timer / 1000):.1f}s (E)", True, BLACK)
    screen.blit(throw_cd_text, (10, 70))
    pigskin_status = font.render(f"Has Pigskin: {player.has_pigskin}", True, BLACK)
    screen.blit(pigskin_status, (10, 100))
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
