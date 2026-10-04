
# --- START GENERATED GAME CODE TEMPLATE ---

# --- TEMPLATE: A_CORE_SETUP ---
import pygame
import sys
import os
import math # Needed for vine swinging physics
from enum import Enum # Needed for game states

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
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
LIGHT_BLUE = (173, 216, 230)
BROWN = (139, 69, 19)
DARK_GREEN = (0, 100, 0)
PURPLE = (128, 0, 128) # For Glow Bud

# --- LLM_INJECT_A_GAME_SPECIFIC_CONSTANTS ---
# Game-specific Constants for Canopy Caper

# Player (Milo) Properties
PLAYER_SIZE = 30 # Milo's visual size (square for now)
PLAYER_MAX_HEALTH = 100
PLAYER_MAX_STAMINA = 100
PLAYER_STAMINA_REGEN_RATE = 0.2 # Stamina regenerated per frame when not consuming
PLAYER_GROUND_SPEED = 3
PLAYER_AIR_SPEED = 2 # Slower horizontal movement in air
PLAYER_DASH_SPEED_BOOST = 8 # Additional speed during a dash
PLAYER_DASH_DURATION = 15 # Frames
PLAYER_DASH_STAMINA_COST = 20
PLAYER_SWING_PUMP_FORCE = 0.005 # How much up/down keys influence swing speed
PLAYER_SWING_DETACH_MIN_SPEED = 5 # Minimum speed for a meaningful detach jump
PLAYER_ATTACH_RADIUS = 70 # How close Milo needs to be to a vine node to attach

# Physics Constants
GRAVITY_ACCEL = 0.5 # Pixels per frame per frame for airborne
SWING_GRAVITY_FACTOR = 0.0005 # Factor applied to sine of swing angle

# Environmental Hazards & Objects
CRUMBLING_PLATFORM_COLLAPSE_TIME = 90 # Frames (1.5 seconds)
HAZARD_THORNY_DAMAGE = 5 # Damage per tick for thorny bushes
WATER_CURRENT_DAMAGE_PER_TICK = 2 # Damage per tick for water current
SLOTH_DEFLECT_FORCE = 10 # Force applied to player if hitting sloth with momentum

# Power-ups
GOLDEN_BANANA_HEALTH_RESTORE = 50
NECTAR_DROP_HEALTH_RESTORE = 10 # Minor restore for this level
GLOW_BUD_COLLECT_POINTS = 100 # Not directly a powerup, but a collectible

# Score
SCORE_BANANA_COLLECT = 10
SCORE_GOLDEN_BANANA_COLLECT = 100
SCORE_FLAWLESS_LEVEL_BONUS = 500
SCORE_COMBO_MULTIPLIER_INCREMENT = 0.1 # Example

# Game States
class GameState(Enum):
    TITLE_SCREEN = 1
    PLAYING_LEVEL_1 = 2
    LEVEL_COMPLETE = 3
    GAME_OVER = 4

# --- Initialization ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Canopy Caper")
clock = pygame.time.Clock()

# --- Game Variables ---
# Example: a placeholder object position
player_x = SCREEN_WIDTH // 2
player_y = SCREEN_HEIGHT // 2
player_size = 50

# --- Asset Path Handler (Copied from G_ASSET_PATH_HANDLER for self-contained use) ---
def resource_path(relative_path):
    """
    Get the absolute path to resource, works for dev and for PyInstaller.
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

ASSET_DIR = "assets"

# Placeholder for assets - in a real game, these would be loaded properly
# For now, we'll use colored surfaces or simple shapes
def load_asset_placeholder(width, height, color):
    surf = pygame.Surface((width, height))
    surf.fill(color)
    return surf

# --- Main Game Loop ---
# This loop will be replaced by game state management later
running = True
# while running:
#     # 1. Event Handling
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
        
#     # 2. Update Game Logic
#     pass

#     # 3. Drawing
#     screen.fill(BLACK) 
#     pygame.draw.rect(screen, BLUE, (player_x, player_y, player_size, player_size))
#     pygame.display.flip()

#     # 4. Cap the frame rate
#     clock.tick(FPS)

# # --- Cleanup ---
# pygame.quit()
# sys.exit()

# --- TEMPLATE: D_HEALTH_DAMAGE ---
# The Entity class is provided in the template.
# We will create a Player class that extends Entity and adds stamina.

# --- LLM_INJECT_D_PLAYER_STAMINA_SYSTEM ---
class Entity(pygame.sprite.Sprite):
    def __init__(self, color, size, max_hp, position):
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = position
        
        self.max_health = max_hp
        self.current_health = max_hp
        self.is_alive = True
        self.invulnerable_timer = 0 # For temporary invulnerability

    def take_damage(self, amount):
        if not self.is_alive or self.invulnerable_timer > 0:
            return
        
        self.current_health -= amount
        self.current_health = max(0, self.current_health) # Ensure health doesn't go below 0
        # print(f"Damage taken: {amount}. Current HP: {self.current_health}")
        
        if self.current_health <= 0:
            self.die()
        else:
            self.invulnerable_timer = FPS * 1 # 1 second invulnerability

    def heal(self, amount):
        if not self.is_alive:
            return
            
        self.current_health += amount
        self.current_health = min(self.current_health, self.max_health)
        # print(f"Healed: {amount}. Current HP: {self.current_health}")

    def die(self):
        self.is_alive = False
        # print("Entity died!")
        self.kill()

    def draw_health_bar(self, surface):
        if not self.is_alive: return

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
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1

class Player(Entity): # Milo, inheriting from Entity
    def __init__(self, color, size, max_hp, max_stamina, position):
        super().__init__(color, size, max_hp, position)
        
        self.max_stamina = max_stamina
        self.current_stamina = max_stamina
        
        # Player-specific movement states (from C_MOVEMENT_PLATFORMER logic)
        self.current_state = PlayerState.GROUNDED
        self.vx = 0
        self.vy = 0
        self.dash_timer = 0
        self.attached_vine = None
        self.vine_length = 0
        self.swing_angle = 0 # Angle from vertical, clockwise positive
        self.swing_angular_velocity = 0
        self.last_grounded_pos = position # For respawning

        self.score = 0
        self.collected_glow_buds = 0
        self.defeated_sloths = 0
        self.combo_swing_count = 0
        self.combo_timer = 0 # Resets combo after a short time on ground/touching hazard

    def consume_stamina(self, amount):
        if self.current_stamina >= amount:
            self.current_stamina -= amount
            # print(f"Stamina consumed: {amount}. Current Stamina: {self.current_stamina}")
            return True
        # print("Not enough stamina!")
        return False

    def restore_stamina(self, amount):
        self.current_stamina += amount
        self.current_stamina = min(self.current_stamina, self.max_stamina)
        # print(f"Stamina restored: {amount}. Current Stamina: {self.current_stamina}")

    def draw_stamina_bar(self, surface):
        if not self.is_alive: return

        BAR_WIDTH = self.rect.width
        BAR_HEIGHT = 5
        BAR_X = self.rect.x
        BAR_Y = self.rect.y - 18 # Position 18 pixels above the entity (above health bar)

        stamina_ratio = self.current_stamina / self.max_stamina
        fill_width = int(BAR_WIDTH * stamina_ratio)

        background_rect = pygame.Rect(BAR_X, BAR_Y, BAR_WIDTH, BAR_HEIGHT)
        pygame.draw.rect(surface, BLACK, background_rect) # Dark background for stamina

        fill_rect = pygame.Rect(BAR_X, BAR_Y, fill_width, BAR_HEIGHT)
        pygame.draw.rect(surface, BLUE, fill_rect) # Blue for stamina

    def add_score(self, amount):
        self.score += amount
        # print(f"Score: {self.score}")

    def reset_combo(self):
        self.combo_swing_count = 0
        self.combo_timer = 0

    def start_combo_timer(self):
        if self.combo_swing_count > 0: # Only start if a combo is active
            self.combo_timer = FPS * 2 # 2 seconds to keep combo going

    def update(self):
        super().update() # Call parent's update for invulnerability

        # Stamina regeneration
        if self.current_stamina < self.max_stamina and self.dash_timer == 0:
            self.restore_stamina(PLAYER_STAMINA_REGEN_RATE)
        
        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer <= 0:
                self.reset_combo()
# --- END LLM_INJECT_D_PLAYER_STAMINA_SYSTEM ---


# --- TEMPLATE: E_BASIC_COLLISION ---
# The template provides a basic collision. We need to implement game-specific collision objects.

# --- LLM_INJECT_E_COMPLEX_COLLISION_TYPES ---
class PlayerState(Enum):
    GROUNDED = 0
    AIRBORNE = 1
    SWINGING = 2

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=BROWN, type="platform"):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.type = type

    def update(self):
        pass # Static platforms don't move

class CrumblingPlatform(Platform):
    def __init__(self, x, y, width, height, respawn_point):
        super().__init__(x, y, width, height, ORANGE, "crumbling_platform")
        self.original_y = y
        self.collapsed = False
        self.collapse_timer = 0
        self.respawn_point = respawn_point # Where player respawns if they fall

    def trigger_collapse(self):
        if not self.collapsed:
            self.collapse_timer = CRUMBLING_PLATFORM_COLLAPSE_TIME
            # print("Crumbling platform triggered!")

    def update(self):
        if self.collapse_timer > 0:
            self.collapse_timer -= 1
            if self.collapse_timer <= 0:
                self.collapsed = True
                self.rect.y = SCREEN_HEIGHT + 100 # Move off-screen
                # print("Crumbling platform collapsed!")
        if self.collapsed and self.collapse_timer <= 0: # Respawn after a longer delay, if needed
             if pygame.time.get_ticks() % (FPS * 5) == 0: # Respawn every 5 seconds for example
                 self.collapsed = False
                 self.rect.y = self.original_y
                 self.image.fill(ORANGE) # Reset color visually
                 # print("Crumbling platform respawned!")

class VineNode(pygame.sprite.Sprite):
    def __init__(self, x, y, radius, implied_length, color=VINE_BROWN):
        super().__init__()
        self.image = pygame.Surface([radius * 2, radius * 2], pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect(center=(x, y))
        self.radius = radius
        self.implied_length = implied_length
        self.type = "vine_node"

    def update(self):
        pass

class ThornyBush(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(DARK_GREEN) # Thorny bush color
        pygame.draw.rect(self.image, RED, self.image.get_rect(), 2) # Red outline for thorns
        self.rect = self.image.get_rect(topleft=(x, y))
        self.type = "thorny_bush"
        self.damage_on_touch = HAZARD_THORNY_DAMAGE

    def update(self):
        pass

class WaterCurrent(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, force_vector, respawn_point):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(LIGHT_BLUE)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.type = "water_current"
        self.force_vector = pygame.math.Vector2(force_vector['x'], force_vector['y'])
        self.respawn_point = respawn_point
        self.damage_on_touch = WATER_CURRENT_DAMAGE_PER_TICK

    def update(self):
        pass

class GlowBud(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([20, 20], pygame.SRCALPHA)
        pygame.draw.circle(self.image, PURPLE, (10,10), 8)
        pygame.draw.circle(self.image, YELLOW, (10,10), 4) # Inner glow
        self.rect = self.image.get_rect(center=(x, y))
        self.type = "glow_bud"
        self.collected = False

    def collect(self, player):
        if not self.collected:
            self.collected = True
            player.collected_glow_buds += 1
            player.add_score(GLOW_BUD_COLLECT_POINTS)
            self.kill() # Remove from all sprite groups

class NectarDrop(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([15, 15], pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (7,7), 7)
        self.rect = self.image.get_rect(center=(x, y))
        self.type = "nectar_drop"
        self.collected = False

    def collect(self, player):
        if not self.collected:
            self.collected = True
            player.heal(NECTAR_DROP_HEALTH_RESTORE)
            self.kill()

class SlumberingSloth(Entity):
    def __init__(self, x, y, patrol_path, behavior, hit_points):
        super().__init__(RED, (40, 40), hit_points, (x, y)) # Sloth is an Entity
        self.type = "slumbering_sloth"
        self.patrol_path = [pygame.math.Vector2(p[0], p[1]) for p in patrol_path]
        self.current_patrol_index = 0
        self.speed = 0.5 # Sloths are slow
        self.behavior = behavior
        self.hit_points = hit_points # For momentum impact
        self.initial_pos = pygame.math.Vector2(x, y) # For respawn/reset
        self.is_defeated = False

    def update(self):
        if self.is_alive and not self.is_defeated:
            if self.behavior == "slow_patrol" and len(self.patrol_path) > 1:
                target_pos = self.patrol_path[self.current_patrol_index]
                self_pos = pygame.math.Vector2(self.rect.center)
                direction = target_pos - self_pos
                
                if direction.length() < self.speed: # Reached target
                    self.rect.center = target_pos
                    self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_path)
                else:
                    direction.normalize_ip()
                    self.rect.center += direction * self.speed
        
        # Sloths don't take damage from player 'touch', only momentum_impact
        # Override take_damage if needed for other scenarios
        super().update()
    
    def take_momentum_damage(self, player_momentum_magnitude):
        if player_momentum_magnitude > PLAYER_SWING_DETACH_MIN_SPEED * 1.5: # Example threshold
            self.hit_points -= 1
            if self.hit_points <= 0:
                self.is_defeated = True
                self.kill() # Remove visually
                return True
        return False
        
    def reset(self):
        self.current_health = self.max_health # Reset health if it had any
        self.is_alive = True
        self.is_defeated = False
        self.rect.center = self.initial_pos
        self.current_patrol_index = 0
        # Re-add to groups if it was killed, needs to be handled in level reset


# --- Collision Functions (main game loop context) ---
def check_player_collisions(player, level_sprites):
    # Check for platform collision (landing)
    # Filter for solid platforms
    solid_platforms = [s for s in level_sprites if isinstance(s, Platform) and s.type != "water_current" and s.type != "thorny_bush"]

    # When airborne, check for landing on platforms
    if player.current_state == PlayerState.AIRBORNE and player.vy > 0:
        for platform in solid_platforms:
            if pygame.sprite.collide_rect(player, platform):
                # Check if player is falling onto the platform (and not from side/under)
                if player.rect.bottom - player.vy <= platform.rect.top:
                    player.rect.bottom = platform.rect.top
                    player.vy = 0
                    player.vx = 0 # Stop horizontal velocity on landing unless specified
                    player.current_state = PlayerState.GROUNDED
                    player.last_grounded_pos = player.rect.center # Update respawn point
                    player.reset_combo()
                    # Trigger crumbling platform
                    if isinstance(platform, CrumblingPlatform):
                        platform.trigger_collapse()
                    return

    # Keep player on platform if grounded
    if player.current_state == PlayerState.GROUNDED:
        on_platform = False
        for platform in solid_platforms:
            # A bit more tolerant check for being "on" a platform
            if platform.rect.collidepoint(player.rect.midbottom[0], player.rect.bottom + 1):
                on_platform = True
                player.rect.bottom = platform.rect.top # Snap to top of platform
                break
        if not on_platform:
            player.current_state = PlayerState.AIRBORNE
            player.vy = 0 # Start falling if not on a platform
            player.vx = 0 # Prevent sliding when falling off

    # Check for hazards (Thorny Bush, Water Current)
    for hazard in pygame.sprite.spritecollide(player, level_sprites, False):
        if isinstance(hazard, ThornyBush):
            if player.current_state != PlayerState.SWINGING: # Only if not swinging over
                player.take_damage(hazard.damage_on_touch)
                # Revert position slightly to prevent constant damage
                player.rect.x -= player.vx * 2
                player.rect.y -= player.vy * 2
        elif isinstance(hazard, WaterCurrent):
            if player.current_state != PlayerState.SWINGING and player.rect.bottom > hazard.rect.top: # Only if in the water
                player.take_damage(hazard.damage_on_touch)
                player.rect.x += hazard.force_vector.x # Apply current
                player.rect.y += hazard.force_vector.y
                # If player falls into water, respawn them
                if player.current_health > 0: # Only respawn if still alive
                    player.rect.center = hazard.respawn_point['x'], hazard.respawn_point['y']
                    player.vx, player.vy = 0, 0
                    player.current_state = PlayerState.AIRBORNE # Make them fall onto a platform

    # Check for collectibles (GlowBud, NectarDrop)
    for collectible in pygame.sprite.spritecollide(player, level_sprites, False):
        if isinstance(collectible, GlowBud) and not collectible.collected:
            collectible.collect(player)
        elif isinstance(collectible, NectarDrop) and not collectible.collected:
            collectible.collect(player)
            
    # Check for enemies (Slumbering Sloth)
    for enemy in pygame.sprite.spritecollide(player, level_sprites, False):
        if isinstance(enemy, SlumberingSloth) and not enemy.is_defeated:
            # If player hits sloth while swinging with momentum
            if player.current_state == PlayerState.SWINGING or player.dash_timer > 0:
                momentum_magnitude = math.sqrt(player.vx**2 + player.vy**2)
                if enemy.take_momentum_damage(momentum_magnitude):
                    player.defeated_sloths += 1
                    player.add_score(50) # Score for defeating enemy
                    # Push player back slightly after impact
                    player.vx = -player.vx * 0.5
                    player.vy = -player.vy * 0.5
            else: # If just walking/touching without momentum
                player.take_damage(10) # Sloth causes damage
                # Push player back
                if player.rect.x < enemy.rect.x: player.vx = -SLOTH_DEFLECT_FORCE
                else: player.vx = SLOTH_DEFLECT_FORCE
                player.vy = -SLOTH_DEFLECT_FORCE/2
                player.current_state = PlayerState.AIRBORNE

# --- END LLM_INJECT_E_COMPLEX_COLLISION_TYPES ---


# --- TEMPLATE: F_GAME_STATES ---
# This template is for game state management. We will implement the specific states for Canopy Caper.

# --- LLM_INJECT_F_GAME_STATE_LOGIC ---
# Already defined GameState Enum in A_CORE_SETUP
# class GameState(Enum):
#     TITLE_SCREEN = 1
#     PLAYING_LEVEL_1 = 2
#     LEVEL_COMPLETE = 3
#     GAME_OVER = 4

current_state = GameState.TITLE_SCREEN
level_data = None # Will store parsed level data

# --- Game Level Objects (for the current level) ---
player_sprite = None
all_sprites_group = pygame.sprite.Group() # All visible sprites
platforms_group = pygame.sprite.Group() # For player-platform collision
vine_nodes_group = pygame.sprite.Group() # For player-vine attachment
hazards_group = pygame.sprite.Group() # For player-hazard collision
enemies_group = pygame.sprite.Group() # For player-enemy interaction
collectibles_group = pygame.sprite.Group() # For player-collectible interaction
exit_platform_sprite = None # Reference to the exit platform

level_timer = 0
time_limit = 0
collected_glow_buds_needed = 0
defeated_sloths_needed = 0

def load_level(level_design_data):
    global player_sprite, all_sprites_group, platforms_group, vine_nodes_group, hazards_group, enemies_group, collectibles_group, exit_platform_sprite
    global level_timer, time_limit, collected_glow_buds_needed, defeated_sloths_needed

    # Clear all existing groups
    all_sprites_group.empty()
    platforms_group.empty()
    vine_nodes_group.empty()
    hazards_group.empty()
    enemies_group.empty()
    collectibles_group.empty()

    # Reset game state variables
    level_timer = 0
    time_limit = level_design_data["time_limit"]

    # Parse spawn points
    for spawn in level_design_data["spawn_points"]:
        if spawn["type"] == "player":
            player_sprite = Player(BLUE, (PLAYER_SIZE, PLAYER_SIZE), PLAYER_MAX_HEALTH, PLAYER_MAX_STAMINA, (spawn["x"], spawn["y"]))
            player_sprite.x = spawn["x"] # Initialize float position
            player_sprite.y = spawn["y"]
            all_sprites_group.add(player_sprite)

    # Parse obstacles
    for obs in level_design_data["obstacles"]:
        sprite = None
        if obs["type"] == "ground_platform" or obs["type"] == "platform":
            sprite = Platform(obs["x"], obs["y"], obs["width"], obs["height"])
            platforms_group.add(sprite)
        elif obs["type"] == "crumbling_platform":
            sprite = CrumblingPlatform(obs["x"], obs["y"], obs["width"], obs["height"], obs["respawn_point"])
            platforms_group.add(sprite)
        elif obs["type"] == "vine_node":
            sprite = VineNode(obs["x"], obs["y"], obs["radius"], obs["implied_length"])
            vine_nodes_group.add(sprite)
        elif obs["type"] == "thorny_bush":
            sprite = ThornyBush(obs["x"], obs["y"], obs["width"], obs["height"])
            hazards_group.add(sprite)
        elif obs["type"] == "water_current":
            sprite = WaterCurrent(obs["x"], obs["y"], obs["width"], obs["height"], obs["force_vector"], obs["respawn_point"])
            hazards_group.add(sprite)
        elif obs["type"] == "exit_platform":
            sprite = Platform(obs["x"], obs["y"], obs["width"], obs["height"], GREEN, "exit_platform")
            platforms_group.add(sprite)
            exit_platform_sprite = sprite # Store reference to exit

        if sprite:
            all_sprites_group.add(sprite)
    
    # Parse powerups/collectibles
    for pu in level_design_data["powerups"]:
        sprite = None
        if pu["type"] == "nectar_drop":
            sprite = NectarDrop(pu["x"], pu["y"])
            collectibles_group.add(sprite)
        elif pu["type"] == "glow_bud":
            sprite = GlowBud(pu["x"], pu["y"])
            collectibles_group.add(sprite)
        
        if sprite:
            all_sprites_group.add(sprite)

    # Parse enemies
    for enemy_data in level_design_data["enemies"]:
        sprite = None
        if enemy_data["type"] == "slumbering_sloth":
            sprite = SlumberingSloth(enemy_data["x"], enemy_data["y"], enemy_data["patrol_path"], enemy_data["behavior"], enemy_data["hit_points"])
            enemies_group.add(sprite)
        
        if sprite:
            all_sprites_group.add(sprite)

    # Parse objectives
    collected_glow_buds_needed = 0
    defeated_sloths_needed = 0
    for objective in level_design_data["objectives"]:
        if objective["type"] == "collect" and objective["target"] == "glow_buds":
            collected_glow_buds_needed = objective["count"]
        elif objective["type"] == "defeat" and objective["target"] == "slumbering_sloths":
            defeated_sloths_needed = objective["count"]

    # Re-add player last to ensure it's drawn on top
    all_sprites_group.add(player_sprite)
    
    # Reset player stats for the new level
    player_sprite.current_health = PLAYER_MAX_HEALTH
    player_sprite.current_stamina = PLAYER_MAX_STAMINA
    player_sprite.score = 0
    player_sprite.collected_glow_buds = 0
    player_sprite.defeated_sloths = 0
    player_sprite.reset_combo()
    player_sprite.is_alive = True
    player_sprite.current_state = PlayerState.GROUNDED # Ensure player starts grounded


def run_title_screen(events):
    global current_state, level_data
    
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Load Level 1 data
                level_data = {
                  "level_number": 1,
                  "name": "The First Ascent",
                  "description": "Welcome to the Canopy! Master basic vine swinging, navigate over small ground obstacles, and learn to harness momentum to reach new platforms. Collect the sparkling Glow Bud and bypass the sleepy Sloth to reach the final exit platform.",
                  "size": {
                    "width": 800,
                    "height": 600
                  },
                  "spawn_points": [
                    {
                      "x": 100,
                      "y": 500,
                      "type": "player"
                    }
                  ],
                  "obstacles": [
                    {
                      "x": 0,
                      "y": 550,
                      "width": 200,
                      "height": 50,
                      "type": "ground_platform",
                      "description": "Starting platform"
                    },
                    {
                      "x": 200,
                      "y": 450,
                      "width": 80,
                      "height": 60,
                      "type": "platform",
                      "description": "Safe landing platform"
                    },
                    {
                      "x": 300,
                      "y": 350,
                      "width": 70,
                      "height": 50,
                      "type": "platform",
                      "description": "Mid-level landing platform"
                    },
                    {
                      "x": 450,
                      "y": 200,
                      "width": 60,
                      "height": 40,
                      "type": "crumbling_platform",
                      "trigger_delay": 1.5,
                      "respawn_point": {
                        "x": 300,
                        "y": 350
                      }
                    },
                    {
                      "x": 700,
                      "y": 150,
                      "width": 100,
                      "height": 80,
                      "type": "exit_platform",
                      "description": "Final destination"
                    },
                    {
                      "x": 150,
                      "y": 400,
                      "type": "vine_node",
                      "radius": 10,
                      "implied_length": 100,
                      "description": "First vine, easy reach"
                    },
                    {
                      "x": 250,
                      "y": 300,
                      "type": "vine_node",
                      "radius": 10,
                      "implied_length": 110,
                      "description": "Second vine, for momentum practice"
                    },
                    {
                      "x": 380,
                      "y": 250,
                      "type": "vine_node",
                      "radius": 10,
                      "implied_length": 120,
                      "description": "Third vine, over the thorny bush"
                    },
                    {
                      "x": 500,
                      "y": 350,
                      "type": "vine_node",
                      "radius": 10,
                      "implied_length": 130,
                      "description": "Fourth vine, over the water current"
                    },
                    {
                      "x": 650,
                      "y": 250,
                      "type": "vine_node",
                      "radius": 10,
                      "implied_length": 140,
                      "description": "Final vine, requires good height/speed"
                    },
                    {
                      "x": 300,
                      "y": 200,
                      "width": 100,
                      "height": 80,
                      "type": "thorny_bush",
                      "damage_on_touch": 5,
                      "implied_height_clearance": 50,
                      "description": "Ground obstacle to swing over"
                    },
                    {
                      "x": 400,
                      "y": 400,
                      "width": 200,
                      "height": 100,
                      "type": "water_current",
                      "force_vector": {
                        "x": -0.5,
                        "y": 0
                      },
                      "respawn_point": {
                        "x": 300,
                        "y": 350
                      },
                      "description": "Slowly pushes Milo left if he falls in"
                    }
                  ],
                  "powerups": [
                    {
                      "x": 220,
                      "y": 420,
                      "type": "nectar_drop",
                      "description": "Minor health restore, easy to collect near first platform"
                    },
                    {
                      "x": 460,
                      "y": 170,
                      "type": "glow_bud",
                      "description": "Main collectible, on crumbling platform, requires precise swing"
                    }
                  ],
                  "enemies": [
                    {
                      "x": 550,
                      "y": 480,
                      "type": "slumbering_sloth",
                      "patrol_path": [
                        [
                          550,
                          480
                        ],
                        [
                          600,
                          480
                        ],
                        [
                          600,
                          530
                        ],
                        [
                          550,
                          530
                        ]
                      ],
                      "behavior": "slow_patrol",
                      "defeat_condition": "momentum_impact",
                      "hit_points": 1,
                      "description": "Slow, ground-based enemy. Can be defeated by swinging into it with momentum or easily bypassed by swinging over."
                    }
                  ],
                  "objectives": [
                    {
                      "type": "collect",
                      "target": "glow_buds",
                      "count": 1,
                      "description": "Collect the shimmering Glow Bud"
                    },
                    {
                      "type": "defeat",
                      "target": "slumbering_sloths",
                      "count": 1,
                      "description": "Defeat or bypass the Slumbering Sloth"
                    },
                    {
                      "type": "reach_area",
                      "target": "exit_platform",
                      "x": 700,
                      "y": 150,
                      "radius": 50,
                      "description": "Reach the final exit platform"
                    }
                  ],
                  "difficulty": "easy",
                  "time_limit": 180
                }
                load_level(level_data)
                current_state = GameState.PLAYING_LEVEL_1
    
    screen.fill(DARK_GREEN) # Jungle canopy background
    font_large = pygame.font.Font(None, 74)
    font_medium = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 36)

    title_text = font_large.render("CANOPY CAPER", True, YELLOW)
    desc_text = font_small.render("Swing, Leap, and Dash to find your way home!", True, WHITE)
    start_text = font_medium.render("Press SPACE to Start Level 1", True, WHITE)
    
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(desc_text, (SCREEN_WIDTH // 2 - desc_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
    screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2 + 80))


def run_playing_level_1(events):
    global current_state, level_timer

    for event in events:
        if event.type == pygame.QUIT:
            global running
            running = False
            return
        # Pass events to player for input
        if player_sprite:
            player_sprite.handle_input(event)
    
    # Update logic
    level_timer += 1
    if level_timer >= time_limit * FPS: # Check time limit
        current_state = GameState.GAME_OVER

    if player_sprite and not player_sprite.is_alive: # Player died
        current_state = GameState.GAME_OVER

    all_sprites_group.update()
    
    # Check all collisions
    if player_sprite:
        check_player_collisions(player_sprite, all_sprites_group)

        # Check for level objectives completion
        objectives_met = True
        if player_sprite.collected_glow_buds < collected_glow_buds_needed:
            objectives_met = False
        if player_sprite.defeated_sloths < defeated_sloths_needed:
            objectives_met = False
        
        # Check if player reached exit platform
        if exit_platform_sprite and pygame.sprite.collide_rect(player_sprite, exit_platform_sprite) and objectives_met:
            current_state = GameState.LEVEL_COMPLETE
            return # Exit early to prevent further updates for this frame

    # Drawing
    screen.fill((70, 130, 80)) # Lighter jungle background for playing
    all_sprites_group.draw(screen)

    # Draw player health and stamina bars (if player exists and is alive)
    if player_sprite and player_sprite.is_alive:
        player_sprite.draw_health_bar(screen)
        player_sprite.draw_stamina_bar(screen)

        # Draw current score and objectives
        font_small = pygame.font.Font(None, 24)
        score_text = font_small.render(f"Score: {player_sprite.score}", True, WHITE)
        health_text = font_small.render(f"Health: {player_sprite.current_health}/{PLAYER_MAX_HEALTH}", True, WHITE)
        stamina_text = font_small.render(f"Stamina: {int(player_sprite.current_stamina)}/{PLAYER_MAX_STAMINA}", True, WHITE)
        time_left_sec = (time_limit * FPS - level_timer) // FPS
        time_text = font_small.render(f"Time: {time_left_sec}", True, WHITE)

        obj_glow_bud_text = font_small.render(f"Glow Buds: {player_sprite.collected_glow_buds}/{collected_glow_buds_needed}", True, WHITE)
        obj_sloth_text = font_small.render(f"Sloths Defeated: {player_sprite.defeated_sloths}/{defeated_sloths_needed}", True, WHITE)


        screen.blit(score_text, (10, 10))
        screen.blit(health_text, (10, 30))
        screen.blit(stamina_text, (10, 50))
        screen.blit(time_text, (SCREEN_WIDTH - time_text.get_width() - 10, 10))
        screen.blit(obj_glow_bud_text, (SCREEN_WIDTH - obj_glow_bud_text.get_width() - 10, 30))
        screen.blit(obj_sloth_text, (SCREEN_WIDTH - obj_sloth_text.get_width() - 10, 50))


    # Draw the swing line if player is swinging
    if player_sprite and player_sprite.current_state == PlayerState.SWINGING:
        pygame.draw.line(screen, VINE_BROWN, player_sprite.attached_vine.rect.center, player_sprite.rect.center, 2)


def run_level_complete(events):
    global current_state, player_sprite

    final_score = player_sprite.score # Retrieve final score
    time_bonus = max(0, (time_limit * FPS - level_timer) // FPS) * 5 # 5 points per second left
    final_score += time_bonus
    
    # Flawless run check (simple example)
    flawless_bonus = 0
    if player_sprite.current_health == PLAYER_MAX_HEALTH: # No damage taken
        flawless_bonus = SCORE_FLAWLESS_LEVEL_BONUS
        final_score += flawless_bonus


    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: # Restart / return to menu
                current_state = GameState.TITLE_SCREEN
            if event.key == pygame.K_n: # Next level (placeholder)
                print("Proceed to next level (not implemented)")
                current_state = GameState.TITLE_SCREEN
    
    screen.fill(DARK_GREEN)
    font_large = pygame.font.Font(None, 74)
    font_medium = pygame.font.Font(None, 48)

    title_text = font_large.render("LEVEL COMPLETE!", True, YELLOW)
    score_text = font_medium.render(f"Final Score: {final_score}", True, WHITE)
    time_bonus_text = font_medium.render(f"Time Bonus: {time_bonus}", True, WHITE)
    flawless_text = font_medium.render(f"Flawless Run Bonus: {flawless_bonus}", True, YELLOW)
    restart_text = font_medium.render("Press 'R' for Title Screen", True, WHITE)
    
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 150))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(time_bonus_text, (SCREEN_WIDTH // 2 - time_bonus_text.get_width() // 2, SCREEN_HEIGHT // 2 ))
    if flawless_bonus > 0:
        screen.blit(flawless_text, (SCREEN_WIDTH // 2 - flawless_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 150))


def run_game_over(events):
    global current_state
    
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                current_state = GameState.TITLE_SCREEN
    
    screen.fill(BLACK)
    font_large = pygame.font.Font(None, 74)
    font_medium = pygame.font.Font(None, 48)

    over_text = font_large.render("GAME OVER", True, RED)
    restart_text = font_medium.render("Press 'R' to return to Title", True, WHITE)
    
    screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

# --- END LLM_INJECT_F_GAME_STATE_LOGIC ---


# --- TEMPLATE: G_ASSET_PATH_HANDLER ---
# This template is already largely defined in A_CORE_SETUP for self-containment.
# We will use its functions to load specific game assets.

# --- LLM_INJECT_G_ASSET_LOADING_EXAMPLES ---
# Using the resource_path function and asset_dir defined in A_CORE_SETUP

# Backgrounds (example - might be dynamic for a tilemap)
# For now, level background is filled with color.
# jungle_background_img = pygame.image.load(resource_path(os.path.join(ASSET_DIR, 'backgrounds', 'jungle_bg.png'))).convert() 

# Player sprites (using placeholders as no actual assets are provided)
# player_sprite_idle = pygame.image.load(resource_path(os.path.join(ASSET_DIR, 'player', 'milo_idle.png'))).convert_alpha()
# player_sprite_swing = pygame.image.load(resource_path(os.path.join(ASSET_DIR, 'player', 'milo_swing.png'))).convert_alpha()
# For now, player is a colored rectangle. `Player` class already handles `self.image`.

# Platform sprites
platform_img = load_asset_placeholder(50, 50, BROWN) # Generic platform
crumbling_platform_img = load_asset_placeholder(50, 50, ORANGE)

# Vine node sprite
vine_node_img = load_asset_placeholder(20, 20, VINE_BROWN)

# Hazard sprites
thorny_bush_img = load_asset_placeholder(100, 80, DARK_GREEN)
water_current_img = load_asset_placeholder(200, 100, LIGHT_BLUE)

# Collectible sprites
glow_bud_img = load_asset_placeholder(20, 20, PURPLE)
nectar_drop_img = load_asset_placeholder(15, 15, YELLOW)

# Enemy sprites
sloth_img = load_asset_placeholder(40, 40, RED)

# The individual sprite classes (Platform, VineNode, ThornyBush, etc.) defined in E
# would internally use these loaded assets for their `self.image`.
# For this template, they are currently using `pygame.Surface` and `fill()`.
# A real game would pass these loaded `pygame.Surface` objects to the sprite constructors.
# --- END LLM_INJECT_G_ASSET_LOADING_EXAMPLES ---


# --- TEMPLATE: C_MOVEMENT_PLATFORMER ---
# The existing Player class needs to be heavily refactored for top-down vine swinging.

# --- LLM_INJECT_C_PLAYER_VINE_SWING_LOGIC ---
# Player class defined in D_HEALTH_DAMAGE has been extended with movement states.
# We will add the core movement logic here.

# Add PlayerState Enum if it wasn't already (moved to A_CORE_SETUP)
# class PlayerState(Enum):
#     GROUNDED = 0
#     AIRBORNE = 1
#     SWINGING = 2

# Player class definition from D has been integrated into Player() class earlier.
# The update method for Player class:
def player_update_logic(player_self): # Use player_self to refer to 'self' in the class
    # Update dashing
    if player_self.dash_timer > 0:
        player_self.dash_timer -= 1
        if player_self.dash_timer == 0:
            player_self.vx = 0 # Stop dash boost, revert to normal speed
            # Note: if it's a "quick leap", vx/vy would persist slightly
    
    # Update position (x,y attributes)
    player_self.rect.x = int(player_self.x)
    player_self.rect.y = int(player_self.y)

    # Keep player within screen bounds horizontally
    player_self.x = max(0, min(SCREEN_WIDTH - player_self.rect.width, player_self.x))
    player_self.rect.x = int(player_self.x)

    # State-specific movement and physics
    if player_self.current_state == PlayerState.GROUNDED:
        # Ground movement
        keys = pygame.key.get_pressed()
        player_self.vx = 0
        if keys[pygame.K_LEFT]:
            player_self.vx = -PLAYER_GROUND_SPEED
        if keys[pygame.K_RIGHT]:
            player_self.vx = PLAYER_GROUND_SPEED
        
        player_self.x += player_self.vx

        # Gravity check for falling off
        # Handled by check_player_collisions now
        
    elif player_self.current_state == PlayerState.AIRBORNE:
        # Apply gravity
        player_self.vy += GRAVITY_ACCEL
        
        # Limit fall speed
        player_self.vy = min(player_self.vy, 10) # Max fall speed
        
        player_self.x += player_self.vx
        player_self.y += player_self.vy

    elif player_self.current_state == PlayerState.SWINGING:
        if player_self.attached_vine is None:
            player_self.current_state = PlayerState.AIRBORNE
            player_self.vx = 0
            player_self.vy = 0
            return

        vine_center = pygame.math.Vector2(player_self.attached_vine.rect.center)
        
        # Physics for circular motion
        # Gravitational force tangent to the arc
        gravity_tangent = SWING_GRAVITY_FACTOR * math.sin(player_self.swing_angle)
        
        player_self.swing_angular_velocity += gravity_tangent
        
        # Input for pumping the swing
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            player_self.swing_angular_velocity += PLAYER_SWING_PUMP_FORCE * abs(math.cos(player_self.swing_angle))
        if keys[pygame.K_DOWN]:
            player_self.swing_angular_velocity -= PLAYER_SWING_PUMP_FORCE * abs(math.cos(player_self.swing_angle))
        
        # Dampen angular velocity slightly to prevent endless swing
        player_self.swing_angular_velocity *= 0.99
        
        player_self.swing_angle += player_self.swing_angular_velocity
        
        # Calculate new position
        player_self.x = vine_center.x + player_self.vine_length * math.sin(player_self.swing_angle)
        player_self.y = vine_center.y + player_self.vine_length * math.cos(player_self.swing_angle)
        
        # Calculate current velocity based on swing
        player_self.vx = player_self.vine_length * player_self.swing_angular_velocity * math.cos(player_self.swing_angle)
        player_self.vy = -player_self.vine_length * player_self.swing_angular_velocity * math.sin(player_self.swing_angle)
        
        # Update combo timer
        player_self.start_combo_timer()


# Inject player_update_logic into the Player class
Player.update = lambda s: player_update_logic(s) # Lambda to pass self correctly

# Add Player-specific input handling
def player_handle_input(player_self, event):
    if player_self.is_alive:
        if event.type == pygame.KEYDOWN:
            if player_self.current_state == PlayerState.GROUNDED:
                if event.key == pygame.K_SPACE and player_self.dash_timer == 0:
                    player_self.dash()
                elif event.key == pygame.K_e or event.key == pygame.K_LSHIFT: # Action button to attach
                    player_self.attempt_attach()
            
            elif player_self.current_state == PlayerState.AIRBORNE:
                if event.key == pygame.K_SPACE and player_self.dash_timer == 0:
                    player_self.dash()
                elif event.key == pygame.K_e or event.key == pygame.K_LSHIFT: # Action button to attach
                    player_self.attempt_attach()

            elif player_self.current_state == PlayerState.SWINGING:
                if event.key == pygame.K_e or event.key == pygame.K_LSHIFT: # Action button to detach
                    player_self.detach()

# Inject player_handle_input into the Player class
Player.handle_input = lambda s, e: player_handle_input(s, e)


# Add new methods to the Player class
def player_dash(player_self):
    if player_self.current_stamina >= PLAYER_DASH_STAMINA_COST:
        if player_self.consume_stamina(PLAYER_DASH_STAMINA_COST):
            player_self.dash_timer = PLAYER_DASH_DURATION
            # Apply dash force
            keys = pygame.key.get_pressed()
            dash_vx = 0
            dash_vy = 0
            if keys[pygame.K_LEFT]: dash_vx = -PLAYER_DASH_SPEED_BOOST
            if keys[pygame.K_RIGHT]: dash_vx = PLAYER_DASH_SPEED_BOOST
            if keys[pygame.K_UP]: dash_vy = -PLAYER_DASH_SPEED_BOOST # Dash up
            if keys[pygame.K_DOWN]: dash_vy = PLAYER_DASH_SPEED_BOOST # Dash down
            
            # If no direction, default to current horizontal velocity or forward
            if dash_vx == 0 and dash_vy == 0:
                if player_self.current_state == PlayerState.SWINGING:
                    dash_vx = player_self.vx / 2 # Maintain swing direction
                    dash_vy = player_self.vy / 2
                else: # Default ground dash
                    dash_vx = PLAYER_DASH_SPEED_BOOST if player_self.vx >= 0 else -PLAYER_DASH_SPEED_BOOST

            player_self.vx += dash_vx
            player_self.vy += dash_vy
            
            # If swinging, detach for dash-leap
            if player_self.current_state == PlayerState.SWINGING:
                player_self.detach()
            player_self.current_state = PlayerState.AIRBORNE # Always airborne after a dash/leap

Player.dash = lambda s: player_dash(s)


def player_attempt_attach(player_self):
    # Find nearest vine node
    nearest_vine = None
    min_dist = PLAYER_ATTACH_RADIUS
    
    for vine in vine_nodes_group: # Assuming vine_nodes_group is accessible
        dist_vec = pygame.math.Vector2(player_self.rect.centerx, player_self.rect.centery) - pygame.math.Vector2(vine.rect.centerx, vine.rect.centery)
        distance = dist_vec.length()

        if distance < min_dist:
            nearest_vine = vine
            min_dist = distance

    if nearest_vine:
        player_self.attached_vine = nearest_vine
        player_self.current_state = PlayerState.SWINGING
        
        # Calculate vine length (distance from vine node to player)
        player_self.vine_length = (pygame.math.Vector2(player_self.x, player_self.y) - pygame.math.Vector2(nearest_vine.rect.centerx, nearest_vine.rect.centery)).length()
        # Cap vine length to its implied length if it was too long (e.g., from a jump)
        player_self.vine_length = min(player_self.vine_length, nearest_vine.implied_length)

        # Calculate initial swing angle
        dx = player_self.x - nearest_vine.rect.centerx
        dy = player_self.y - nearest_vine.rect.centery
        player_self.swing_angle = math.atan2(dx, dy) # Angle from vertical axis (y-axis)
        
        # Calculate initial angular velocity from current linear velocity
        # Projection of player's velocity onto the tangential direction
        tangential_x = -dy
        tangential_y = dx
        tangential_length = math.sqrt(tangential_x**2 + tangential_y**2)
        if tangential_length > 0:
            tangential_x /= tangential_length
            tangential_y /= tangential_length
            dot_product = player_self.vx * tangential_x + player_self.vy * tangential_y
            player_self.swing_angular_velocity = dot_product / player_self.vine_length
        else:
            player_self.swing_angular_velocity = 0

        player_self.vx = 0 # Reset linear velocities
        player_self.vy = 0
        player_self.combo_swing_count += 1
        player_self.start_combo_timer()


Player.attempt_attach = lambda s: player_attempt_attach(s)


def player_detach(player_self):
    if player_self.attached_vine:
        # Transfer current tangential velocity to linear velocity
        player_self.vx = player_self.vine_length * player_self.swing_angular_velocity * math.cos(player_self.swing_angle)
        player_self.vy = -player_self.vine_length * player_self.swing_angular_velocity * math.sin(player_self.swing_angle)
        
        player_self.attached_vine = None
        player_self.swing_angular_velocity = 0
        player_self.current_state = PlayerState.AIRBORNE
        
        # Optional: Add a slight boost on detach if at max swing speed
        if abs(player_self.vx) > PLAYER_SWING_DETACH_MIN_SPEED or abs(player_self.vy) > PLAYER_SWING_DETACH_MIN_SPEED:
            player_self.vx *= 1.1 # Small boost
            player_self.vy *= 1.1

Player.detach = lambda s: player_detach(s)

# --- END LLM_INJECT_C_PLAYER_VINE_SWING_LOGIC ---


# --- TEMPLATE: A_CORE_SETUP (Continuation of main game loop) ---
# Main Game Loop for the state machine
running = True
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
            
    if current_state == GameState.TITLE_SCREEN:
        run_title_screen(events)
    elif current_state == GameState.PLAYING_LEVEL_1:
        run_playing_level_1(events)
    elif current_state == GameState.LEVEL_COMPLETE:
        run_level_complete(events)
    elif current_state == GameState.GAME_OVER:
        run_game_over(events)
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
