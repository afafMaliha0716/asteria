# --- START GENERATED GAME CODE TEMPLATE ---

# --- TEMPLATE: A_CORE_SETUP ---
import pygame
import sys
import os # Added for resource_path
from enum import Enum # Added for GameState enum
import math # For distance calculations

# --- Core Setup ---
pygame.init()

# --- Constants ---
# Screen dimensions
SCREEN_WIDTH = 900 # From Level 1 design
SCREEN_HEIGHT = 700 # From Level 1 design
FPS = 60

# Color definitions (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
FIELD_GREEN = (50, 150, 50)
ENDZONE_RED = (200, 50, 50)
PLAYER_COLOR = (0, 0, 200) # Darker blue for QB
ENEMY_COLOR = (200, 0, 0) # Darker red for enemies
OBSTACLE_COLOR = (100, 100, 100) # Grey for obstacles
POWERUP_COLOR_SPEED = (0, 200, 200) # Cyan for speed
POWERUP_COLOR_POWER = (255, 200, 0) # Orange for power
STAR_TOKEN_COLOR = (255, 255, 0) # Yellow for tokens
TEXT_COLOR = WHITE
POWER_METER_BG_COLOR = (50, 50, 50)
POWER_METER_FILL_COLOR = (0, 255, 255) # Cyan for power meter

# Game-specific constants
PLAYER_BASE_SPEED = 4
PLAYER_DODGE_SPEED_MULTIPLIER = 2.5
PLAYER_DODGE_DURATION = 0.3 # seconds, duration of quick movement
PLAYER_INVINCIBILITY_DURATION = 0.5 # seconds, invincibility after dodge/spin
PLAYER_SPIN_COST = 30
PLAYER_HUT_COST = 50
PLAYER_BURST_COST = 40
POWER_METER_MAX = 100
POWER_GAIN_PASSIVE_PER_SECOND = 5 # Passive gain
POWER_GAIN_ON_DODGE = 10
POWER_GAIN_ON_ADVANCE = 5 # Per "zone" advanced towards endzone
POWER_GAIN_ON_TOKEN = 15

ENEMY_LURKER_SPEED = 2
ENEMY_CHARGER_SPEED = 3.5 # Not used in L1
ENEMY_BLITZ_SPEED = 5 # Not used in L1
ENEMY_TACKLE_RANGE = 20 # Distance for a tackle to register (not used in current collision check but good to have)

POWERUP_SPEED_DURATION = 5 # seconds
POWERUP_INVINCIBILITY_DURATION = 3 # seconds (from shield, not in L1)
POWERUP_REFILL_AMOUNT = 40

HUT_CALL_DURATION = 2.5 # seconds
SIDELINE_BURST_DURATION = 3 # seconds
SIDELINE_BURST_SPEED_MULTIPLIER = 2

TIME_LIMIT_DEFAULT = 90 # seconds (from L1 design)

# --- Game States Enum ---
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3
    LEVEL_COMPLETE = 4

current_state = GameState.MENU

# --- Initialization ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Touchdown Tempest")
clock = pygame.time.Clock()

# --- Fonts ---
pygame.font.init()
FONT_LARGE = pygame.font.Font(None, 74)
FONT_MEDIUM = pygame.font.Font(None, 48)
FONT_SMALL = pygame.font.Font(None, 36)
FONT_TINY = pygame.font.Font(None, 24)

# --- Asset Path Handler (copied from G_ASSET_PATH_HANDLER template) ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS 
        return os.path.join(base_path, 'assets', relative_path)
    except Exception:
        base_path = os.path.abspath(".") 
        return os.path.join(base_path, 'assets', relative_path)

# Placeholder for GameManager and level data
game_manager = None 
level1_data = {}

# --- Main Game Loop ---
running = True
while running:
    # 1. Event Handling
    events = pygame.event.get() # Collect all events for this frame
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    # 2. Update Game Logic (This is where movement, collision, etc., would go)
    dt = clock.tick(FPS) / 1000.0 # Delta time in seconds

    if current_state == GameState.MENU:
        run_menu(events)
    elif current_state == GameState.PLAYING:
        run_playing(events, dt)
    elif current_state == GameState.GAME_OVER:
        run_game_over(events)
    elif current_state == GameState.LEVEL_COMPLETE:
        run_level_complete(events)

    # 3. Drawing
    # Drawing handled within state functions

    # Update the full display surface to the screen
    pygame.display.flip()

    # 4. Cap the frame rate
    # clock.tick(FPS) is already called to calculate dt

# --- Cleanup ---
pygame.quit()
sys.exit()


# --- TEMPLATE: D_HEALTH_DAMAGE ---
import pygame

# --- Constants & Initialization (Assumed from A) ---
# pygame.init()
# SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
# screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# clock = pygame.time.Clock()
# FPS = 60
# WHITE = (255, 255, 255)
# RED = (255, 0, 0)
# GREEN = (0, 255, 0)
# BLUE = (0, 0, 255)

# --- Entity Class with Health System ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, level_width, level_height):
        super().__init__()
        self.image = pygame.Surface([40, 40])
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect(center=(x, y))
        self.level_width = level_width
        self.level_height = level_height

        self.base_speed = PLAYER_BASE_SPEED
        self.current_speed = self.base_speed
        self.dx, self.dy = 0, 0
        self.old_x, self.old_y = self.rect.x, self.rect.y # For collision resolution

        self.power_meter = 0
        self.max_power = POWER_METER_MAX

        self.is_invincible = False
        self.invincibility_timer = 0.0

        self.is_spinning = False
        self.spin_move_timer = 0.0

        self.is_bursting = False
        self.sideline_burst_timer = 0.0

        self.speed_boost_active = False
        self.speed_boost_timer = 0.0

        self.last_tackle_evade_time = 0.0 # To track successful dodges for objective, prevent rapid double counts

    def handle_input(self, keys):
        self.dx, self.dy = 0, 0

        # Continuous movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.dx = -self.current_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.dx = self.current_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.dy = -self.current_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.dy = self.current_speed

        # Diagonal movement normalization
        if self.dx != 0 and self.dy != 0:
            magnitude = math.sqrt(self.dx**2 + self.dy**2)
            if magnitude > 0: # Avoid division by zero
                self.dx = (self.dx / magnitude) * self.current_speed
                self.dy = (self.dy / magnitude) * self.current_speed

    def activate_dodge(self):
        # Dodge is a quick burst of invincibility and speed
        if not self.is_invincible and not self.is_spinning: # Can't dodge if already invincible or spinning
            self.is_invincible = True
            self.invincibility_timer = PLAYER_INVINCIBILITY_DURATION
            self.gain_power(POWER_GAIN_ON_DODGE)
            # Apply temporary speed boost for the dodge animation/feel
            self.current_speed = self.base_speed * PLAYER_DODGE_SPEED_MULTIPLIER

    def activate_spin_move(self):
        if self.power_meter >= PLAYER_SPIN_COST and not self.is_spinning:
            self.power_meter -= PLAYER_SPIN_COST
            self.is_spinning = True
            self.is_invincible = True # Spin move also grants invincibility
            self.spin_move_timer = PLAYER_DODGE_DURATION # Short duration for spin visual/effect
            self.invincibility_timer = PLAYER_INVINCIBILITY_DURATION # Invincibility lasts a bit longer
            self.current_speed = self.base_speed * PLAYER_DODGE_SPEED_MULTIPLIER # Spin burst speed
            return True
        return False

    def activate_hut_call(self, enemies):
        if self.power_meter >= PLAYER_HUT_COST:
            self.power_meter -= PLAYER_HUT_COST
            for enemy in enemies:
                enemy.is_frozen_by_hut = True
                enemy.hut_freeze_timer = HUT_CALL_DURATION
            return True
        return False

    def activate_sideline_burst(self):
        if self.power_meter >= PLAYER_BURST_COST and not self.is_bursting:
            self.power_meter -= PLAYER_BURST_COST
            self.is_bursting = True
            self.sideline_burst_timer = SIDELINE_BURST_DURATION
            self.current_speed = self.base_speed * SIDELINE_BURST_SPEED_MULTIPLIER
            return True
        return False

    def apply_speed_boost(self, duration, multiplier):
        self.speed_boost_active = True
        self.speed_boost_timer = duration
        # Apply the boost, but ensure it doesn't override temporary dodge/spin speed
        if not self.is_invincible and not self.is_bursting:
            self.current_speed = self.base_speed * multiplier

    def apply_invincibility_powerup(self, duration): # For powerup, not dodge
        self.is_invincible = True
        self.invincibility_timer = max(self.invincibility_timer, duration) # Extend if already invincible

    def gain_power(self, amount):
        self.power_meter += amount
        self.power_meter = min(self.power_meter, self.max_power)

    def update(self, dt): # Removed enemies from here, hut call is handled immediately
        # Store old position before movement
        self.old_x, self.old_y = self.rect.x, self.rect.y

        # Apply movement
        self.rect.x += self.dx * dt * FPS
        self.rect.y += self.dy * dt * FPS

        # Keep player within screen bounds
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(self.level_width, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(self.level_height, self.rect.bottom)

        # Update timers
        if self.invincibility_timer > 0:
            self.invincibility_timer -= dt
            if self.invincibility_timer <= 0:
                self.is_invincible = False
                # If no other active speed buffs, revert to base speed
                if not self.speed_boost_active and not self.is_bursting:
                    self.current_speed = self.base_speed

        if self.spin_move_timer > 0:
            self.spin_move_timer -= dt
            if self.spin_move_timer <= 0:
                self.is_spinning = False

        if self.sideline_burst_timer > 0:
            self.sideline_burst_timer -= dt
            if self.sideline_burst_timer <= 0:
                self.is_bursting = False
                # If no other active speed buffs, revert to base speed
                if not self.speed_boost_active and not self.is_invincible:
                    self.current_speed = self.base_speed

        if self.speed_boost_active:
            self.speed_boost_timer -= dt
            if self.speed_boost_timer <= 0:
                self.speed_boost_active = False
                # If no other active speed buffs, revert to base speed
                if not self.is_invincible and not self.is_bursting:
                    self.current_speed = self.base_speed

        # Passive power gain
        self.gain_power(POWER_GAIN_PASSIVE_PER_SECOND * dt)

    def get_tackled(self):
        # This function would trigger game over in GameManager
        pass # Actual handling is in GameManager

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, color, size=(35, 35)):
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.base_speed = speed
        self.current_speed = speed
        self.is_frozen_by_hut = False
        self.hut_freeze_timer = 0.0

    def update(self, dt, player_pos=None):
        if self.is_frozen_by_hut:
            self.hut_freeze_timer -= dt
            if self.hut_freeze_timer <= 0:
                self.is_frozen_by_hut = False
            return # Do not move if frozen

        # Specific enemy behaviors implemented in subclasses
        # This base class update just handles the freeze timer

class LinebackerLurker(Enemy):
    def __init__(self, x, y, patrol_path, speed=ENEMY_LURKER_SPEED):
        super().__init__(x, y, speed, ENEMY_COLOR, size=(40, 40))
        self.patrol_path = [pygame.math.Vector2(p) for p in patrol_path]
        self.current_path_index = 0
        self.target_pos = self.patrol_path[self.current_path_index]
        self.rect.center = self.patrol_path[0] # Ensure starting at first point

    def update(self, dt, player_pos=None):
        super().update(dt, player_pos)
        if self.is_frozen_by_hut:
            return

        # Simple patrol logic: move to next point, then cycle
        move_vector = self.target_pos - pygame.math.Vector2(self.rect.center)
        distance = move_vector.length()

        if distance < self.current_speed * dt * FPS: # If close enough to target
            self.rect.center = self.target_pos
            self.current_path_index = (self.current_path_index + 1) % len(self.patrol_path)
            self.target_pos = self.patrol_path[self.current_path_index]
        else:
            move_vector.normalize_ip()
            self.rect.center += move_vector * self.current_speed * dt * FPS

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=OBSTACLE_COLOR):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, type_str, color):
        super().__init__()
        self.type = type_str
        size = 25
        self.image = pygame.Surface([size, size])
        self.image.fill(color) # For now, just a colored square
        self.rect = self.image.get_rect(center=(x, y))

    def apply_effect(self, player):
        if self.type == "speed":
            player.apply_speed_boost(POWERUP_SPEED_DURATION, 3.0) # Triples speed
        elif self.type == "invincibility":
            player.apply_invincibility_powerup(POWERUP_INVINCIBILITY_DURATION)
        elif self.type == "power_boost":
            player.gain_power(POWERUP_REFILL_AMOUNT)
        self.kill() # Remove power-up after collection

class StarToken(pygame.sprite.Sprite):
    def __init__(self, x, y, size=20, color=STAR_TOKEN_COLOR):
        super().__init__()
        self.image = pygame.Surface([size, size], pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size // 2, size // 2), size // 2)
        self.rect = self.image.get_rect(center=(x, y))

class EndZone(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=ENDZONE_RED):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

# --- Game Setup ---
class GameManager:
    def __init__(self):
        self.player = None
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.star_tokens = pygame.sprite.Group()
        self.endzone = None

        self.score = 0
        self.time_left = 0.0
        self.level_number = 0
        self.level_data = {}
        self.successful_dodges = 0
        self.star_tokens_collected = 0
        self.advances_made = 0
        self.last_player_x_zone = 0 # To track progress towards endzone for power gain/objectives

    def load_level(self, level_data):
        self.level_data = level_data

        # Clear existing sprites
        self.all_sprites.empty()
        self.enemies.empty()
        self.obstacles.empty()
        self.powerups.empty()
        self.star_tokens.empty()
        self.endzone = None

        # Set level dimensions (used for player bounds)
        level_width = level_data["size"]["width"]
        level_height = level_data["size"]["height"]

        # Player setup
        player_spawn = level_data["spawn_points"][0]
        self.player = Player(player_spawn["x"], player_spawn["y"], level_width, level_height)
        self.all_sprites.add(self.player)
        self.last_player_x_zone = int(self.player.rect.centerx / (level_width / 5)) # Divide into 5 conceptual zones

        # Obstacles
        for obs_data in level_data["obstacles"]:
            obstacle = Obstacle(obs_data["x"], obs_data["y"], obs_data["width"], obs_data["height"])
            self.obstacles.add(obstacle)
            self.all_sprites.add(obstacle)

        # Powerups
        for pu_data in level_data["powerups"]:
            color = POWERUP_COLOR_SPEED if pu_data["type"] == "speed" else POWERUP_COLOR_POWER
            powerup = PowerUp(pu_data["x"], pu_data["y"], pu_data["type"], color)
            self.powerups.add(powerup)
            self.all_sprites.add(powerup)

        # Enemies (only Linebacker Lurkers for Level 1 as per design)
        for enemy_data in level_data["enemies"]:
            if enemy_data["type"] == "tackler" or enemy_data["type"] == "line_backer": # Mapping to Linebacker Lurker
                enemy = LinebackerLurker(enemy_data["x"], enemy_data["y"], enemy_data["patrol_path"])
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)

        # Endzone (located on the right side of the screen)
        # Assuming endzone is the full height on the right edge
        endzone_width = 50 
        self.endzone = EndZone(level_width - endzone_width, 0, endzone_width, level_height)
        self.all_sprites.add(self.endzone)

        # Star Tokens (for collect objective) - need to generate positions if not in level_data,
        # For L1, I'll place them based on the objective (3 tokens)
        token_positions = [(250, 600), (450, 150), (750, 450)] # Hardcoded for L1 objectives
        for pos in token_positions:
            token = StarToken(pos[0], pos[1])
            self.star_tokens.add(token)
            self.all_sprites.add(token)

        # Reset game state
        self.score = 0
        self.time_left = float(level_data.get("time_limit", TIME_LIMIT_DEFAULT))
        self.level_number = level_data.get("level_number", 1)
        self.successful_dodges = 0
        self.star_tokens_collected = 0
        self.advances_made = 0

        # Reset player state
        self.player.power_meter = 0 
        self.player.is_invincible = False
        self.player.invincibility_timer = 0.0
        self.player.is_spinning = False
        self.player.spin_move_timer = 0.0
        self.player.is_bursting = False
        self.player.sideline_burst_timer = 0.0
        self.player.speed_boost_active = False
        self.player.speed_boost_timer = 0.0
        self.player.current_speed = self.player.base_speed


    def update_playing(self, dt):
        global current_state

        # Player movement and abilities
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.update(dt)

        # Enemies update
        for enemy in self.enemies:
            enemy.update(dt, self.player.rect.center) # Pass player position for AI

        # Collision checks
        self.check_collisions(dt)

        # Update time
        self.time_left -= dt
        if self.time_left <= 0:
            self.time_left = 0
            current_state = GameState.GAME_OVER # Time's up!

        # Check for player progress towards endzone (for objectives/power gain)
        # Divide the field into 5 zones for 'advance' objective
        field_zone_width = self.level_data["size"]["width"] / 5
        player_current_x_zone = int(self.player.rect.centerx / field_zone_width)
        if player_current_x_zone > self.last_player_x_zone:
            # Player advanced a zone
            zone_diff = player_current_x_zone - self.last_player_x_zone
            self.advances_made += zone_diff
            self.player.gain_power(POWER_GAIN_ON_ADVANCE * zone_diff)
            self.last_player_x_zone = player_current_x_zone


        # Win condition: Player reaches endzone
        if pygame.sprite.collide_rect(self.player, self.endzone):
            self.score_touchdown()
            current_state = GameState.LEVEL_COMPLETE

    def check_collisions(self, dt):
        # Player-Obstacle collision
        hit_obstacles = pygame.sprite.spritecollide(self.player, self.obstacles, False)
        if hit_obstacles:
            # Revert player position
            self.player.rect.x = self.player.old_x
            self.player.rect.y = self.player.old_y

        # Player-Enemy collision (tackle)
        hit_enemies = pygame.sprite.spritecollide(self.player, self.enemies, False)
        if hit_enemies:
            if not self.player.is_invincible: # This covers invincibility from dodge, spin, or powerup
                # Player gets tackled, Game Over
                self.player.get_tackled() # Call player's method, it will notify GameManager
                global current_state
                current_state = GameState.GAME_OVER
            elif self.player.is_invincible: 
                # If invincible (from dodge, spin, or powerup), ignore tackle
                # For L1 objective "evade 2 tacklers", this counts as an evade
                current_time = pygame.time.get_ticks() / 1000.0
                if current_time - self.player.last_tackle_evade_time > 0.5: # Small cooldown to avoid multiple evades from one collision
                    self.successful_dodges += 1
                    self.player.last_tackle_evade_time = current_time

        # Player-Powerup collision
        collected_powerups = pygame.sprite.spritecollide(self.player, self.powerups, True) # True to remove powerup
        for powerup in collected_powerups:
            powerup.apply_effect(self.player)
            self.all_sprites.remove(powerup)

        # Player-StarToken collision
        collected_tokens = pygame.sprite.spritecollide(self.player, self.star_tokens, True)
        for token in collected_tokens:
            self.star_tokens_collected += 1
            self.player.gain_power(POWER_GAIN_ON_TOKEN)
            self.all_sprites.remove(token)


    def score_touchdown(self):
        self.score += 1000 # Base points for touchdown
        self.score += int(self.time_left * 10) # Bonus for remaining time
        self.score += self.successful_dodges * 50 # Bonus for dodges
        self.score += self.star_tokens_collected * 75 # Bonus for tokens
        # Check objectives and add bonus
        # Advance objective (reached endzone already, so 1 advance is met implicitly)
        # Collect 3 Star Tokens
        if self.star_tokens_collected >= 3:
            self.score += 150 # Bonus for collecting tokens
        # Evade 2 Tacklers
        if self.successful_dodges >= 2:
            self.score += 100 # Bonus for evading tacklers

        print(f"Touchdown! Score: {self.score}")

    def draw_hud(self, surface):
        # Time Left
        time_text = FONT_MEDIUM.render(f"TIME: {int(self.time_left)}", True, TEXT_COLOR)
        surface.blit(time_text, (SCREEN_WIDTH - time_text.get_width() - 20, 10))

        # Score
        score_text = FONT_MEDIUM.render(f"SCORE: {self.score}", True, TEXT_COLOR)
        surface.blit(score_text, (20, 10))

        # Power Meter
        bar_x, bar_y = 20, 50
        bar_width, bar_height = 200, 20
        pygame.draw.rect(surface, POWER_METER_BG_COLOR, (bar_x, bar_y, bar_width, bar_height))
        fill_width = int(bar_width * (self.player.power_meter / self.player.max_power))
        pygame.draw.rect(surface, POWER_METER_FILL_COLOR, (bar_x, bar_y, fill_width, bar_height))
        power_text = FONT_TINY.render(f"POWER: {int(self.player.power_meter)}/{self.player.max_power}", True, TEXT_COLOR)
        surface.blit(power_text, (bar_x + bar_width + 10, bar_y))

        # Ability Status (Instructions for use)
        ability_1_text = FONT_TINY.render(f"1-Spin ({PLAYER_SPIN_COST})", True, TEXT_COLOR)
        ability_2_text = FONT_TINY.render(f"2-Hut ({PLAYER_HUT_COST})", True, TEXT_COLOR)
        ability_3_text = FONT_TINY.render(f"3-Burst ({PLAYER_BURST_COST})", True, TEXT_COLOR)
        dodge_text = FONT_TINY.render("SPACE-Dodge", True, TEXT_COLOR)

        surface.blit(dodge_text, (bar_x, bar_y + bar_height + 5))
        surface.blit(ability_1_text, (bar_x + dodge_text.get_width() + 10, bar_y + bar_height + 5))
        surface.blit(ability_2_text, (bar_x + dodge_text.get_width() + ability_1_text.get_width() + 20, bar_y + bar_height + 5))
        surface.blit(ability_3_text, (bar_x + dodge_text.get_width() + ability_1_text.get_width() + ability_2_text.get_width() + 30, bar_y + bar_height + 5))

        # Invincibility/Speed Boost status
        status_y = bar_y + bar_height + 30
        if self.player.is_invincible:
            inv_text = FONT_TINY.render("INVINCIBLE!", True, WHITE)
            surface.blit(inv_text, (SCREEN_WIDTH // 2 - inv_text.get_width() // 2, status_y))
            status_y += 20
        if self.player.speed_boost_active or self.player.is_bursting:
            speed_text = FONT_TINY.render("SPEED BOOST!", True, WHITE)
            surface.blit(speed_text, (SCREEN_WIDTH // 2 - speed_text.get_width() // 2, status_y))

    def draw_playing(self, surface):
        surface.fill(FIELD_GREEN) # Field color
        self.endzone.draw(surface) # Draw endzone first if it's not in all_sprites but rather a background element
        self.all_sprites.draw(surface)
        self.draw_hud(surface)

game_manager = GameManager()

# --- Test Events (Simulating Damage/Heal) ---
def simulate_interaction():
    pass

# --- Main Game Loop ---
# Loop handled in A_CORE_SETUP
#   for event in pygame.event.get():
#       if event.type == pygame.QUIT:
#           running = False
#       if event.type == pygame.KEYDOWN:
#           # Press 'H' to heal the player
#           if event.key == pygame.K_h:
#               player.heal(10)

# 1. Update
#    simulate_interaction()
#    all_sprites.update()

# 2. Drawing
#    screen.fill(WHITE)
#    all_sprites.draw(screen)

# MANDATORY: Draw health bars AFTER drawing sprites
#    if player.is_alive:
#        player.draw_health_bar(screen)
#    if enemy.is_alive:
#        enemy.draw_health_bar(screen)

#    pygame.display.flip()
#    clock.tick(FPS)

# pygame.quit()


# --- TEMPLATE: E_BASIC_COLLISION ---
import pygame

# --- Constants & Initialization (Assumed from A) ---
# pygame.init()
# SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
# screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# clock = pygame.time.Clock()
# FPS = 60
# WHITE = (255, 255, 255)
# GREEN = (0, 255, 0)
# RED = (255, 0, 0)

# --- Player Class with Collision Memory ---
pass # Player class already defined in D_HEALTH_DAMAGE_ENTITY_CLASS

# --- Wall Class (Solid Object) ---
pass # Obstacle class already defined in D_HEALTH_DAMAGE_ENTITY_CLASS

# --- Collision Functions ---
def check_and_resolve_collision(sprite, wall_group):
    """
    Collision logic is handled within GameManager.check_collisions().
    This placeholder function is not used.
    """
    pass

# --- Game Setup ---
# all_sprites = pygame.sprite.Group()
# walls = pygame.sprite.Group()

# player = Player()
# all_sprites.add(player)

# Create a wall in the center
# wall_1 = Wall(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT // 2 - 100, 50, 200)
# walls.add(wall_1)
# all_sprites.add(wall_1)

# --- Main Game Loop ---
# Loop handled in A_CORE_SETUP
#   for event in pygame.event.get():
#       if event.type == pygame.QUIT:
#           running = False

# 1. Update
#    all_sprites.update()

# 2. Collision Check and Resolution
#    check_and_resolve_collision(player, walls)

# 3. Drawing
#    screen.fill(WHITE)
#    all_sprites.draw(screen)

#    pygame.display.flip()
#    clock.tick(FPS)

# pygame.quit()


# --- TEMPLATE: F_GAME_STATES ---
import pygame
import sys
# from enum import Enum # Already imported in A_CORE_SETUP

# --- Constants & Initialization (Assumed from A) ---
# pygame.init()
# SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
# screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# pygame.display.set_caption("Template F: Game States")
# clock = pygame.time.Clock()
# FPS = 60
# BLACK = (0, 0, 0)
# WHITE = (255, 255, 255)
# RED = (255, 0, 0) # Added missing constant definition
# FONT = pygame.font.Font(None, 74)
# SMALL_FONT = pygame.font.Font(None, 36)

# --- Game States Enum ---
# class GameState(Enum):
#     MENU = 1
#     PLAYING = 2
#     GAME_OVER = 3

# --- State Management ---
# current_state = GameState.MENU # Handled in A_CORE_SETUP_PRE_LOOP

# --- State Functions ---
# Placeholder for GameManager definition and state functions
level1_data = {
  "level_number": 1,
  "name": "The Rookie's Kickoff",
  "description": "The stadium is buzzing as you step onto the field for your first game. Learn the ropes, dodge some tackles, and get a feel for the ball. Focus on building your momentum and understanding the flow of the game.",
  "size": {
    "width": 900,
    "height": 700
  },
  "spawn_points": [
    {
      "x": 50,
      "y": 350,
      "type": "player"
    }
  ],
  "obstacles": [
    {
      "x": 200,
      "y": 100,
      "width": 80,
      "height": 40,
      "type": "block"
    },
    {
      "x": 400,
      "y": 250,
      "width": 40,
      "height": 40,
      "type": "block"
    },
    {
      "x": 600,
      "y": 150,
      "width": 60,
      "height": 60,
      "type": "block"
    },
    {
      "x": 300,
      "y": 500,
      "width": 70,
      "height": 30,
      "type": "block"
    },
    {
      "x": 550,
      "y": 600,
      "width": 50,
      "height": 50,
      "type": "block"
    }
  ],
  "powerups": [
    {
      "x": 150,
      "y": 200,
      "type": "speed"
    },
    {
      "x": 700,
      "y": 300,
      "type": "power_boost"
    },
    {
      "x": 350,
      "y": 400,
      "type": "power_boost"
    }
  ],
  "enemies": [
    {
      "x": 300,
      "y": 150,
      "type": "tackler",
      "patrol_path": [
        [
          300,
          150
        ],
        [
          400,
          150
        ]
      ]
    },
    {
      "x": 550,
      "y": 350,
      "type": "tackler",
      "patrol_path": [
        [
          550,
          350
        ],
        [
          550,
          450
        ]
      ]
    },
    {
      "x": 700,
      "y": 500,
      "type": "tackler",
      "patrol_path": [
        [
          700,
          500
        ],
        [
          600,
          500
        ]
      ]
    },
    {
      "x": 200,
      "y": 400,
      "type": "line_backer",
      "patrol_path": [
        [
          200,
          400
        ],
        [
          150,
          400
        ]
      ]
    }
  ],
  "objectives": [
    {
      "type": "advance",
      "target": "endzone",
      "steps": 5,
      "description": "Advance the ball 5 times towards the endzone."
    },
    {
      "type": "collect",
      "target": "star_tokens",
      "count": 3,
      "description": "Collect 3 Star Tokens scattered across the field."
    },
    {
      "type": "defeat",
      "target": "tacklers",
      "count": 2,
      "description": "Successfully evade 2 Tacklers."
    }
  ],
  "difficulty": "easy",
  "time_limit": 90
}

def run_menu(events):
    global current_state
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game_manager.load_level(level1_data) # Load the level when starting game
                current_state = GameState.PLAYING

    screen.fill(BLACK)
    title_text = FONT_LARGE.render("TOUCHDOWN TEMPEST", True, TEXT_COLOR)
    play_text = FONT_MEDIUM.render("Press SPACE to Start", True, WHITE)
    desc_text_1 = FONT_SMALL.render("Guide your QB to the Endzone!", True, WHITE)
    desc_text_2 = FONT_SMALL.render("Avoid tackles and use abilities (1, 2, 3) & dodge (SPACE)", True, WHITE)

    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(play_text, (SCREEN_WIDTH // 2 - play_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
    screen.blit(desc_text_1, (SCREEN_WIDTH // 2 - desc_text_1.get_width() // 2, SCREEN_HEIGHT // 2 + 80))
    screen.blit(desc_text_2, (SCREEN_WIDTH // 2 - desc_text_2.get_width() // 2, SCREEN_HEIGHT // 2 + 120))


def run_playing(events, dt):
    global current_state

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game_manager.player.activate_dodge()
            if event.key == pygame.K_1: # Spin Move
                game_manager.player.activate_spin_move()
            if event.key == pygame.K_2: # Hut Call
                game_manager.player.activate_hut_call(game_manager.enemies)
            if event.key == pygame.K_3: # Sideline Burst
                game_manager.player.activate_sideline_burst()

    game_manager.update_playing(dt)
    game_manager.draw_playing(screen)


def run_game_over(events):
    global current_state
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: # Restart
                game_manager.load_level(level1_data) # Reload level state
                current_state = GameState.PLAYING
            if event.key == pygame.K_m: # Back to Menu
                current_state = GameState.MENU

    screen.fill(BLACK)
    game_over_text = FONT_LARGE.render("GAME OVER!", True, RED)
    reason_text = FONT_MEDIUM.render("You were tackled or ran out of time!", True, WHITE)
    score_text = FONT_MEDIUM.render(f"Final Score: {game_manager.score}", True, WHITE)
    restart_text = FONT_SMALL.render("Press 'R' to Restart or 'M' for Menu", True, WHITE)

    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(reason_text, (SCREEN_WIDTH // 2 - reason_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 120))


def run_level_complete(events):
    global current_state
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: # Restart (for now, would be next level)
                game_manager.load_level(level1_data)
                current_state = GameState.PLAYING
            if event.key == pygame.K_m: # Back to Menu
                current_state = GameState.MENU

    screen.fill(FIELD_GREEN)
    win_text = FONT_LARGE.render("TOUCHDOWN!", True, WHITE)
    score_text = FONT_MEDIUM.render(f"Total Score: {game_manager.score}", True, WHITE)
    next_level_text = FONT_SMALL.render("Press 'R' to Play Again (Level 1) or 'M' for Menu", True, WHITE)

    screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
    screen.blit(next_level_text, (SCREEN_WIDTH // 2 - next_level_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))


# --- Main Game Loop ---
# Loop handled in A_CORE_SETUP
# running = True
# while running:
#     # 1. Event Handling (Collects all events for the current frame)
#     events = pygame.event.get()
#     for event in events:
#         if event.type == pygame.QUIT:
#             running = False

#     # 2. State Logic (Calls the appropriate function based on the current state)
#     if current_state == GameState.MENU:
#         run_menu(events)
#     elif current_state == GameState.PLAYING:
#         run_playing(events)
#     elif current_state == GameState.GAME_OVER:
#         run_game_over(events)

#     # 3. Drawing
#     pygame.display.flip()

#     # 4. Cap the frame rate
#     clock.tick(FPS)

# --- Cleanup ---
# pygame.quit()
# sys.exit()


# --- TEMPLATE: G_ASSET_PATH_HANDLER ---
# --- TEMPLATE: G_ASSET_PATH_HANDLER ---

# import os
# import sys

# def resource_path(relative_path):
#     """
#     Get absolute path to resource, works for dev and for PyInstaller bundle.
#     This function must be called every time a resource file (like an image) is loaded.

#     CRITICAL NOTE: Assumes all assets are in a subfolder named 'assets' 
#     relative to the script's execution directory in both dev and bundled modes.
#     """
#     try:
#         # PyInstaller creates a temp folder and stores path in _MEIPASS
#         # We join the base path with the 'assets' subdirectory, then the relative path.
#         base_path = sys._MEIPASS 
#         return os.path.join(base_path, 'assets', relative_path)

#     except Exception:
#         # Not running as a compiled executable, use the current script directory
#         # We join the current directory with the relative path.
#         base_path = os.path.abspath(".") 
#         return os.path.join(base_path, 'assets', relative_path)

# --- END TEMPLATE: G_ASSET_PATH_HANDLER ---

# --- TEMPLATE: B_MOVEMENT_TOPDOWN ---
import pygame

# --- Constants & Initialization (Assumed from A) ---
# pygame.init()
# SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
# screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# clock = pygame.time.Clock()
# FPS = 60
# WHITE = (255, 255, 255)
# BLUE = (0, 0, 255)

# --- Player Class for Top-Down Movement ---
pass # Player class already defined in D_HEALTH_DAMAGE_ENTITY_CLASS

# --- Game Setup ---
# all_sprites = pygame.sprite.Group()
# player = Player()
# all_sprites.add(player)

# --- Main Game Loop ---
# Loop handled in A_CORE_SETUP
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False

#     # 1. Update (The player's position is updated here)
#     all_sprites.update()

#     # 2. Drawing
#     screen.fill(WHITE)
#     all_sprites.draw(screen)

#     pygame.display.flip()
#     clock.tick(FPS)

# pygame.quit()


# --- END GENERATED GAME CODE TEMPLATE ---