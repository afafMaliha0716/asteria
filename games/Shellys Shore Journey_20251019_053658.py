Here's the complete Pygame code for "Shelly's Shore Journey" Level 1, incorporating all the specified game concepts, mechanics, and level design details.

The code uses simple colored shapes for all graphics and includes game states for the menu, playing, game over, and win screens. Dummy sound files are created using `numpy` and `scipy.io.wavfile` (if available) to avoid `FileNotFoundError` without requiring external asset downloads. If `numpy` isn't present, the sounds will be silent.

```python
import pygame
import sys
import math
from collections import deque # For enemy patrol paths

# Attempt to import numpy for dummy sound generation
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("Numpy not found. Cannot create dummy sounds. Sound effects will be silent.")

# Attempt to import scipy for dummy wav writing (optional, Pygame's sndarray is enough for in-memory)
try:
    from scipy.io.wavfile import write as write_wav
    HAS_SCIPY_WAV = True
except ImportError:
    HAS_SCIPY_WAV = False
    print("Scipy.io.wavfile not found. Will not write dummy WAV files to disk.")


# --- Constants ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
BROWN = (139, 69, 19)
LIGHT_BLUE = (173, 216, 230)
GRAY = (100, 100, 100)
DARK_GREEN = (0, 100, 0)
PURPLE = (128, 0, 128)
GOLD = (255, 215, 0)
SAND_COLOR = (244, 212, 96) # Beach background
OCEAN_COLOR = (0, 105, 148) # Ocean goal area

# Game States
MENU = 0
PLAYING = 1
GAME_OVER = 2
WIN = 3

# Player settings
PLAYER_SIZE = 20
PLAYER_COLOR = DARK_GREEN
PLAYER_SPEED = 100 # pixels per second
PLAYER_DASH_SPEED_MULTIPLIER = 2.5
PLAYER_DASH_DURATION = 0.5  # seconds
PLAYER_STAMINA_MAX = 100
PLAYER_STAMINA_REGEN_RATE = 20 # stamina per second
PLAYER_DASH_COST = 40 # stamina
PLAYER_SHELL_RETREAT_DURATION = 1.0 # seconds
PLAYER_SHELL_RETREAT_COOLDOWN = 3.0 # seconds
PLAYER_INVULNERABILITY_AFTER_HIT = 1.5 # seconds (separate from shell retreat)
PLAYER_HEALTH_MAX = 3

# Enemy settings
CRAB_SIZE = 25
CRAB_COLOR = RED
CRAB_ATTACK_DAMAGE = 1
CRAB_STUN_DURATION = 2.0 # seconds
CRAB_CHASE_SPEED_MULTIPLIER = 1.5

SEAGULL_SIZE = 40
SEAGULL_COLOR = GRAY
SEAGULL_SHADOW_SIZE = 100 # square shadow
SEAGULL_ALERT_TIME = 2.0 # seconds in shadow to trigger swoop
SEAGULL_SWOOP_SPEED_MULTIPLIER = 3.0
SEAGULL_ATTACK_DAMAGE = 1
SEAGULL_RECOVERY_TIME = 2.0 # Time after swoop before patrolling again

# Obstacle settings
ROCK_COLOR = GRAY
DRIFTWOOD_COLOR = BROWN
PUDDLE_COLOR = LIGHT_BLUE
LARGE_SHELL_COLOR = ORANGE

# Powerup settings
BERRY_SIZE = 15
BERRY_COLOR = PURPLE
BERRY_EFFECT_DURATION = 10.0 # seconds
BERRY_DASH_BONUS_MULTIPLIER = 1.5 # Dash speed multiplier becomes PLAYER_DASH_SPEED_MULTIPLIER * BERRY_DASH_BONUS_MULTIPLIER

SEAWEED_SIZE = 20
SEAWEED_COLOR = GREEN
SEAWEED_EFFECT_DURATION = 15.0 # seconds, or until one hit

STARFISH_SIZE = 15
STARFISH_COLOR = GOLD
STARFISH_SCORE_BONUS = 50

# Font
FONT_NAME = None # Default pygame font
FONT_SIZE_MENU = 72
FONT_SIZE_TITLE = 48
FONT_SIZE_UI = 24
FONT_SIZE_MESSAGE = 36

# --- Classes ---

class Shelly(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([PLAYER_SIZE, PLAYER_SIZE], pygame.SRCALPHA)
        pygame.draw.circle(self.image, PLAYER_COLOR, (PLAYER_SIZE // 2, PLAYER_SIZE // 2), PLAYER_SIZE // 2)
        self.rect = self.image.get_rect(center=(x, y))
        self.x = float(x)
        self.y = float(y)
        self.speed = PLAYER_SPEED
        self.current_speed_multiplier = 1.0

        self.health = PLAYER_HEALTH_MAX
        self.stamina = PLAYER_STAMINA_MAX
        self.score = 0
        
        self.is_dashing = False
        self.dash_timer = 0.0

        self.is_retracted = False
        self.shell_retreat_timer = 0.0
        self.shell_retreat_cooldown_timer = 0.0 # Allows retreat
        
        self.is_invulnerable = False # General invulnerability (shell, seaweed, post-hit)
        self.invulnerable_timer = 0.0 # For post-hit invulnerability

        self.protective_seaweed_active = False
        self.protective_seaweed_timer = 0.0
        self.seaweed_hits_left = 0

        self.berry_active = False
        self.berry_timer = 0.0

    def update(self, dt):
        # Update timers
        if self.dash_timer > 0:
            self.dash_timer -= dt
            if self.dash_timer <= 0:
                self.is_dashing = False
                self.current_speed_multiplier = 1.0 # Reset to base, then apply berry if active
                if self.berry_active:
                    self.current_speed_multiplier = BERRY_DASH_BONUS_MULTIPLIER

        if self.shell_retreat_timer > 0:
            self.shell_retreat_timer -= dt
            if self.shell_retreat_timer <= 0:
                self.is_retracted = False
                # Remove invulnerability if it was solely from shell retreat
                if not (self.protective_seaweed_active and self.seaweed_hits_left > 0) and self.invulnerable_timer <= 0:
                    self.is_invulnerable = False
                self.shell_retreat_cooldown_timer = PLAYER_SHELL_RETREAT_COOLDOWN # Start cooldown
        elif self.shell_retreat_cooldown_timer > 0:
            self.shell_retreat_cooldown_timer -= dt
        
        if self.invulnerable_timer > 0: # Post-hit invulnerability
            self.invulnerable_timer -= dt
            if self.invulnerable_timer <= 0:
                # Only remove invulnerability if not also protected by shell retreat or seaweed
                if not (self.is_retracted or (self.protective_seaweed_active and self.seaweed_hits_left > 0)):
                    self.is_invulnerable = False

        # Stamina regeneration
        if self.stamina < PLAYER_STAMINA_MAX:
            self.stamina += PLAYER_STAMINA_REGEN_RATE * dt
            self.stamina = min(self.stamina, PLAYER_STAMINA_MAX)

        # Powerup timers
        if self.protective_seaweed_active:
            self.protective_seaweed_timer -= dt
            if self.protective_seaweed_timer <= 0 or self.seaweed_hits_left <= 0:
                self.protective_seaweed_active = False
                self.seaweed_hits_left = 0
                # Remove invulnerability if it was solely from seaweed
                if not self.is_retracted and self.invulnerable_timer <= 0:
                    self.is_invulnerable = False
        
        if self.berry_active:
            self.berry_timer -= dt
            if self.berry_timer <= 0:
                self.berry_active = False
                if not self.is_dashing: # Only reset if not currently dashing from this berry boost
                    self.current_speed_multiplier = 1.0

        # Update actual position (rect is updated from x, y)
        self.rect.center = (int(self.x), int(self.y))

    def move(self, dx, dy, collidable_obstacles_group, objectives):
        if self.is_retracted: # Can't move while retracted
            return

        original_x, original_y = self.x, self.y
        move_speed = self.speed * self.current_speed_multiplier
        
        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            move_speed /= 1.414 # Approx sqrt(2)

        # --- Attempt X movement ---
        self.x += dx * move_speed * pygame.time.get_ticks() / 1000 # Use dt for smooth movement
        self.rect.centerx = int(self.x)

        collision_x_resolved = False
        for obj in collidable_obstacles_group:
            if obj.rect.colliderect(self.rect):
                if obj.pushable:
                    # Attempt to push the object. Push speed slightly higher than player speed.
                    push_success = obj.push(dx * move_speed * 1.05, 0, collidable_obstacles_group)
                    if not push_success: # Push failed (obj hit immovable), so player also stops
                        collision_x_resolved = True
                        break
                    else: # Push succeeded
                        if obj.id == "path_blocker_shell":
                            for objective in objectives:
                                if objective.type == "interact" and objective.target_id == "path_blocker_shell" and not objective.is_completed:
                                    objective.complete()
                                    print("Objective: Path blocker shell pushed!")
                else: # Immovable obstacle
                    collision_x_resolved = True
                    break
        
        if collision_x_resolved:
            self.x = original_x
            self.rect.centerx = int(self.x)

        # --- Attempt Y movement ---
        self.y += dy * move_speed * pygame.time.get_ticks() / 1000 # Use dt for smooth movement
        self.rect.centery = int(self.y)

        collision_y_resolved = False
        for obj in collidable_obstacles_group:
            if obj.rect.colliderect(self.rect):
                if obj.pushable:
                    push_success = obj.push(0, dy * move_speed * 1.05, collidable_obstacles_group)
                    if not push_success: # Push failed, so player also stops
                        collision_y_resolved = True
                        break
                    else: # Push succeeded
                        if obj.id == "path_blocker_shell":
                            for objective in objectives:
                                if objective.type == "interact" and objective.target_id == "path_blocker_shell" and not objective.is_completed:
                                    objective.complete()
                                    print("Objective: Path blocker shell pushed!")
                else: # Immovable obstacle
                    collision_y_resolved = True
                    break
        
        if collision_y_resolved:
            self.y = original_y
            self.rect.centery = int(self.y)

        # Keep Shelly within screen bounds
        self.x = max(PLAYER_SIZE // 2, min(self.x, SCREEN_WIDTH - PLAYER_SIZE // 2))
        self.y = max(PLAYER_SIZE // 2, min(self.y, SCREEN_HEIGHT - PLAYER_SIZE // 2))
        self.rect.center = (int(self.x), int(self.y))

    def dash(self, sfx_dash):
        if not self.is_dashing and self.stamina >= PLAYER_DASH_COST:
            self.is_dashing = True
            self.dash_timer = PLAYER_DASH_DURATION
            self.stamina -= PLAYER_DASH_COST
            self.current_speed_multiplier = PLAYER_DASH_SPEED_MULTIPLIER
            if self.berry_active:
                self.current_speed_multiplier *= BERRY_DASH_BONUS_MULTIPLIER
            sfx_dash.play()

    def shell_retreat(self, sfx_retreat):
        if not self.is_retracted and self.shell_retreat_cooldown_timer <= 0:
            self.is_retracted = True
            self.is_invulnerable = True
            self.shell_retreat_timer = PLAYER_SHELL_RETREAT_DURATION
            sfx_retreat.play()

    def take_damage(self, amount, sfx_hit, game_instance):
        if self.is_invulnerable:
            return

        if self.protective_seaweed_active and self.seaweed_hits_left > 0:
            self.seaweed_hits_left -= 1
            print("Protective Seaweed absorbed a hit!")
            if self.seaweed_hits_left == 0:
                self.protective_seaweed_active = False # Effect ends after 1 hit
                # Remove invulnerability if it was solely from seaweed
                if not self.is_retracted and self.invulnerable_timer <= 0:
                    self.is_invulnerable = False
            sfx_hit.play() # Still play hit sound to indicate protection used
            return

        self.health -= amount
        game_instance.player_hit_this_level = True # Mark for no-damage bonus
        self.is_invulnerable = True
        self.invulnerable_timer = PLAYER_INVULNERABILITY_AFTER_HIT
        print(f"Shelly took damage! Health: {self.health}")
        sfx_hit.play()

    def activate_seaweed(self):
        self.protective_seaweed_active = True
        self.protective_seaweed_timer = SEAWEED_EFFECT_DURATION
        self.seaweed_hits_left = 1 # Grants one hit protection
        self.is_invulnerable = True # Makes Shelly generally invulnerable while seaweed is active

    def activate_berry(self):
        self.berry_active = True
        self.berry_timer = BERRY_EFFECT_DURATION
        # Update current speed multiplier immediately if not dashing
        if not self.is_dashing:
             self.current_speed_multiplier = BERRY_DASH_BONUS_MULTIPLIER
        else: # If dashing, apply the additional boost
            self.current_speed_multiplier *= BERRY_DASH_BONUS_MULTIPLIER

    def draw(self, screen):
        # Draw body
        pygame.draw.circle(screen, PLAYER_COLOR, self.rect.center, PLAYER_SIZE // 2)

        # Draw shell if retracted
        if self.is_retracted:
            pygame.draw.circle(screen, BLACK, self.rect.center, PLAYER_SIZE // 2, 2) # Outline
            pygame.draw.circle(screen, GRAY, self.rect.center, PLAYER_SIZE // 4) # Inner shell
        
        # Draw invulnerability shimmer
        if self.is_invulnerable and not self.is_retracted: # Don't draw if already retracted (shell provides visual)
            alpha = int(128 + 127 * math.sin(pygame.time.get_ticks() / 100)) # Pulsating effect
            shimmer_color = (255, 255, 255, alpha)
            shimmer_surface = pygame.Surface((PLAYER_SIZE + 4, PLAYER_SIZE + 4), pygame.SRCALPHA)
            pygame.draw.circle(shimmer_surface, shimmer_color, (shimmer_surface.get_width() // 2, shimmer_surface.get_height() // 2), PLAYER_SIZE // 2 + 2)
            screen.blit(shimmer_surface, shimmer_surface.get_rect(center=self.rect.center))

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, type, pushable=False, obj_id=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.type = type
        self.pushable = pushable
        self.id = obj_id
        
        # Set color based on type
        if type == "rock":
            self.color = ROCK_COLOR
        elif type == "driftwood":
            self.color = DRIFTWOOD_COLOR
        elif type == "puddle": # Puddles are impassable like rocks for simplicity
            self.color = PUDDLE_COLOR
        elif type == "large_shell":
            self.color = LARGE_SHELL_COLOR
        else:
            self.color = GRAY # Default for unknown

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        if self.id: # Draw ID for debug/testing objectives
            font = pygame.font.Font(FONT_NAME, 16)
            text_surf = font.render(self.id, True, BLACK)
            screen.blit(text_surf, (self.rect.x, self.rect.y - 15))


class PushableObject(Obstacle):
    def __init__(self, x, y, width, height, type, obj_id=None):
        super().__init__(x, y, width, height, type, pushable=True, obj_id=obj_id)
        self.original_pos = (x, y) # Store original position for objective check if needed

    def push(self, dx, dy, all_collidable_objects):
        original_rect = self.rect.copy()
        
        # Tentatively move the pushable object
        self.rect.x += dx
        self.rect.y += dy

        # Check for collisions with other *immovable* objects (and itself for safety, though should be excluded)
        for obj in all_collidable_objects:
            if obj != self and obj.rect.colliderect(self.rect):
                if not obj.pushable: # If it hits an immovable object, cannot push
                    self.rect = original_rect # Revert position
                    return False
        
        # If no immovable collisions, the push is successful
        return True


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, enemy_type):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.speed = speed
        self.enemy_type = enemy_type
        self.stun_timer = 0.0
        self.is_stunned = False

    def update(self, dt, player_rect, player_is_retracted):
        if self.is_stunned:
            self.stun_timer -= dt
            if self.stun_timer <= 0:
                self.is_stunned = False
            return

    def stun(self, duration):
        self.is_stunned = True
        self.stun_timer = duration

    def draw(self, screen):
        raise NotImplementedError

    def get_rect(self):
        raise NotImplementedError

class ShoreCrab(Enemy):
    def __init__(self, x, y, patrol_path, speed, sight_range, alert_time):
        super().__init__(x, y, speed, "shore_crab")
        self.image = pygame.Surface([CRAB_SIZE, CRAB_SIZE], pygame.SRCALPHA)
        pygame.draw.circle(self.image, CRAB_COLOR, (CRAB_SIZE // 2, CRAB_SIZE // 2), CRAB_SIZE // 2)
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

        self.patrol_path = deque([(float(px), float(py)) for px, py in patrol_path])
        if len(self.patrol_path) > 1:
            self.patrol_path.append(self.patrol_path[0]) # Loop back to start
        self.current_patrol_target = self.patrol_path.popleft() if self.patrol_path else (self.x, self.y)

        self.sight_range = sight_range
        self.alert_time_max = alert_time # Time before charging
        self.alert_timer = 0.0
        self.state = "patrol" # "patrol", "alert", "chase", "stunned"
        self.chase_target = None # Player's last known position

    def update(self, dt, player_rect, player_is_retracted):
        super().update(dt, player_rect, player_is_retracted) # Handles stun logic
        if self.is_stunned:
            return

        player_distance = math.hypot(self.x - player_rect.centerx, self.y - player_rect.centery)

        if player_is_retracted and self.state == "chase":
            self.state = "patrol" # Shelly retracted, crab loses interest
            self.alert_timer = 0
            print("Crab foiled by Shell Retreat!")
            self.stun(CRAB_STUN_DURATION) # Stun crab if it was chasing

        if self.state == "patrol":
            if player_distance < self.sight_range and not player_is_retracted:
                self.alert_timer += dt
                if self.alert_timer >= self.alert_time_max:
                    self.state = "chase"
                    self.chase_target = player_rect.center
            else:
                self.alert_timer = 0 # Player out of sight or retracted

            # Patrol movement
            target_x, target_y = self.current_patrol_target
            dx = target_x - self.x
            dy = target_y - self.y
            dist = math.hypot(dx, dy)

            if dist < self.speed * dt: # Reached current target
                self.x, self.y = target_x, target_y
                if self.patrol_path: # Ensure path is not empty
                    self.current_patrol_target = self.patrol_path.popleft()
                    self.patrol_path.append(self.current_patrol_target) # Add back to end to loop
            elif dist > 0: # Move towards target
                self.x += (dx / dist) * self.speed * dt
                self.y += (dy / dist) * self.speed * dt

        elif self.state == "chase":
            if player_distance < self.sight_range * 1.5 and not player_is_retracted: # Keep chasing if player is somewhat nearby
                self.chase_target = player_rect.center
            else: # Lost sight
                self.state = "patrol"
                self.alert_timer = 0
                return

            target_x, target_y = self.chase_target
            dx = target_x - self.x
            dy = target_y - self.y
            dist = math.hypot(dx, dy)

            if dist > 0:
                self.x += (dx / dist) * self.speed * CRAB_CHASE_SPEED_MULTIPLIER * dt
                self.y += (dy / dist) * self.speed * CRAB_CHASE_SPEED_MULTIPLIER * dt
        
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, screen):
        color = self.color
        if self.is_stunned:
            color = BLUE # Stunned color
        
        pygame.draw.circle(screen, color, self.rect.center, CRAB_SIZE // 2)
        
        # Draw eyes (simple dots)
        eye_offset = CRAB_SIZE // 5
        eye_size = CRAB_SIZE // 8
        pygame.draw.circle(screen, BLACK, (self.rect.centerx - eye_offset, self.rect.centery - eye_offset), eye_size)
        pygame.draw.circle(screen, BLACK, (self.rect.centerx + eye_offset, self.rect.centery - eye_offset), eye_size)

        # Draw sight range (debug, optional)
        # pygame.draw.circle(screen, RED, self.rect.center, self.sight_range, 1)

class Seagull(Enemy):
    def __init__(self, x, y, speed, path_points, swoop_target_area):
        super().__init__(x, y, speed, "seagull")
        self.image = pygame.Surface([SEAGULL_SIZE, SEAGULL_SIZE], pygame.SRCALPHA)
        pygame.draw.circle(self.image, SEAGULL_COLOR, (SEAGULL_SIZE // 2, SEAGULL_SIZE // 2), SEAGULL_SIZE // 2)
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        self.shadow_rect = pygame.Rect(0, 0, SEAGULL_SHADOW_SIZE, SEAGULL_SHADOW_SIZE)

        self.patrol_path = deque([(float(px), float(py)) for px, py in path_points])
        if len(self.patrol_path) > 1:
            self.patrol_path.append(self.patrol_path[0])
        self.current_patrol_target = self.patrol_path.popleft() if self.patrol_path else (self.x, self.y)

        self.swoop_target_area = pygame.Rect(swoop_target_area[0], swoop_target_area[1], swoop_target_area[2], swoop_target_area[3])
        
        self.state = "patrol" # "patrol", "alerting", "swooping", "recovering"
        self.alert_timer = 0.0
        self.swoop_target_pos = None
        self.recovery_timer = 0.0

    def update(self, dt, player_rect, player_is_retracted):
        super().update(dt, player_rect, player_is_retracted)
        
        # If player retracts, seagull is foiled
        if player_is_retracted and (self.state == "alerting" or self.state == "swooping"):
            print("Seagull foiled by Shell Retreat!")
            self.state = "recovering"
            self.recovery_timer = SEAGULL_RECOVERY_TIME
            self.alert_timer = 0.0 # Reset alert timer
            return # Stop further update for this frame
        
        if self.state == "recovering":
            self.recovery_timer -= dt
            if self.recovery_timer <= 0:
                self.state = "patrol"
            return

        # Update shadow position
        # Let's assume shadow is slightly ahead or below the seagull as it flies
        self.shadow_rect.center = (int(self.x), int(self.y) + SEAGULL_SIZE // 2)

        if self.state == "patrol":
            # Patrol movement
            target_x, target_y = self.current_patrol_target
            dx = target_x - self.x
            dy = target_y - self.y
            dist = math.hypot(dx, dy)

            if dist < self.speed * dt: # Reached current target
                self.x, self.y = target_x, target_y
                if self.patrol_path:
                    self.current_patrol_target = self.patrol_path.popleft()
                    self.patrol_path.append(self.current_patrol_target)
            elif dist > 0:
                self.x += (dx / dist) * self.speed * dt
                self.y += (dy / dist) * self.speed * dt

            # Check if player enters shadow area that can trigger a swoop
            if player_rect.colliderect(self.shadow_rect) and not player_is_retracted:
                self.state = "alerting"
                self.alert_timer = 0.0
                print("Shelly entered seagull shadow!")

        elif self.state == "alerting":
            # Seagull continues its patrol movement while alerting
            target_x, target_y = self.current_patrol_target
            dx = target_x - self.x
            dy = target_y - self.y
            dist = math.hypot(dx, dy)
            if dist > 0:
                self.x += (dx / dist) * self.speed * dt
                self.y += (dy / dist) * self.speed * dt
            if dist < self.speed * dt and self.patrol_path:
                self.x, self.y = target_x, target_y
                self.current_patrol_target = self.patrol_path.popleft()
                self.patrol_path.append(self.current_patrol_target)

            if player_rect.colliderect(self.shadow_rect) and not player_is_retracted:
                self.alert_timer += dt
                if self.alert_timer >= SEAGULL_ALERT_TIME:
                    self.state = "swooping"
                    self.swoop_target_pos = player_rect.center # Swoop to where player was
                    print("Seagull swooping!")
            else:
                self.state = "patrol"
                self.alert_timer = 0.0


        elif self.state == "swooping":
            if self.swoop_target_pos:
                target_x, target_y = self.swoop_target_pos
                dx = target_x - self.x
                dy = target_y - self.y
                dist = math.hypot(dx, dy)

                if dist < self.speed * SEAGULL_SWOOP_SPEED_MULTIPLIER * dt:
                    self.x, self.y = target_x, target_y # Reached swoop point
                    self.state = "recovering"
                    self.recovery_timer = SEAGULL_RECOVERY_TIME
                    self.swoop_target_pos = None # Reset target
                elif dist > 0:
                    self.x += (dx / dist) * self.speed * SEAGULL_SWOOP_SPEED_MULTIPLIER * dt
                    self.y += (dy / dist) * self.speed * SEAGULL_SWOOP_SPEED_MULTIPLIER * dt
            else: # No swoop target, something went wrong, go back to patrol
                self.state = "patrol"
                self.alert_timer = 0.0
        
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, screen):
        # Draw seagull body (triangle for simple bird shape)
        points = [
            (self.rect.centerx, self.rect.top),
            (self.rect.left, self.rect.bottom),
            (self.rect.right, self.rect.bottom)
        ]
        pygame.draw.polygon(screen, SEAGULL_COLOR, points)
        
        # Draw shadow
        shadow_color = (0, 0, 0, 80) # Semi-transparent black
        shadow_surface = pygame.Surface((self.shadow_rect.width, self.shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, shadow_color, (0, 0, self.shadow_rect.width, self.shadow_rect.height))
        screen.blit(shadow_surface, self.shadow_rect)

        # Draw alert indicator if in alerting state
        if self.state == "alerting":
            alert_radius = int(10 + 5 * math.sin(pygame.time.get_ticks() / 100))
            pygame.draw.circle(screen, YELLOW, (self.rect.right + 10, self.rect.centery - 10), alert_radius)
            pygame.draw.circle(screen, ORANGE, (self.rect.right + 10, self.rect.centery - 10), alert_radius - 3)

class Powerup(pygame.sprite.Sprite):
    def __init__(self, x, y, size, color, powerup_type):
        super().__init__()
        self.image = pygame.Surface([size, size], pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size // 2, size // 2), size // 2)
        self.rect = self.image.get_rect(center=(x, y))
        self.type = powerup_type
        self.color = color

    def draw(self, screen):
        # Pulsating effect for powerups
        alpha = int(200 + 55 * math.sin(pygame.time.get_ticks() / 150))
        temp_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.circle(temp_surf, (*self.color, alpha), (self.rect.width // 2, self.rect.height // 2), self.rect.width // 2)
        screen.blit(temp_surf, self.rect)

class JuicyBerry(Powerup):
    def __init__(self, x, y):
        super().__init__(x, y, BERRY_SIZE, BERRY_COLOR, "juicy_berry")

class ProtectiveSeaweed(Powerup):
    def __init__(self, x, y):
        super().__init__(x, y, SEAWEED_SIZE, SEAWEED_COLOR, "protective_seaweed")

class ShinyStarfish(Powerup):
    def __init__(self, x, y):
        super().__init__(x, y, STARFISH_SIZE, STARFISH_COLOR, "shiny_starfish")
        # Draw a starfish shape instead of circle
        self.image = pygame.Surface([STARFISH_SIZE, STARFISH_SIZE], pygame.SRCALPHA)
        star_points = []
        num_points = 5
        outer_radius = STARFISH_SIZE // 2 - 1
        inner_radius = STARFISH_SIZE // 4 - 1
        center_x, center_y = STARFISH_SIZE // 2, STARFISH_SIZE // 2

        for i in range(num_points):
            angle = i * 2 * math.pi / num_points - math.pi / 2 # Start at top
            x_outer = center_x + outer_radius * math.cos(angle)
            y_outer = center_y + outer_radius * math.sin(angle)
            star_points.append((x_outer, y_outer))
            
            angle_inner = angle + math.pi / num_points
            x_inner = center_x + inner_radius * math.cos(angle_inner)
            y_inner = center_y + inner_radius * math.sin(angle_inner)
            star_points.append((x_inner, y_inner))
        
        if star_points: # Ensure points are generated
            pygame.draw.polygon(self.image, STARFISH_COLOR, star_points)
        self.rect = self.image.get_rect(center=(x, y))

class Objective:
    def __init__(self, type, description, target_id=None, target_x=None, target_y=None, target_area_radius=None):
        self.type = type
        self.description = description
        self.is_completed = False
        
        self.target_id = target_id
        self.target_x = target_x
        self.target_y = target_y
        self.target_area_radius = target_area_radius

    def check_completion(self, player_rect):
        if self.is_completed:
            return True

        # "interact" type objectives are completed by direct calls from player.move after a successful push
        # This method primarily checks "reach_destination"
        if self.type == "reach_destination":
            if self.target_x is not None and self.target_y is not None and self.target_area_radius is not None:
                distance = math.hypot(player_rect.centerx - self.target_x, player_rect.centery - self.target_y)
                if distance <= self.target_area_radius:
                    self.is_completed = True
                    print(f"Objective completed: {self.description}")
        return self.is_completed

    def complete(self):
        if not self.is_completed:
            self.is_completed = True
            print(f"Objective manually completed: {self.description}")

class Level:
    def __init__(self, level_data):
        self.title = level_data["title"] if "title" in level_data else "Untitled Level"
        self.description = level_data["description"]
        self.width = level_data["size"]["width"]
        self.height = level_data["size"]["height"]
        self.time_limit = level_data["time_limit"]
        self.player_spawn = level_data["spawn_points"][0] # Assuming one player spawn

        self.obstacles = pygame.sprite.Group()
        self.pushable_objects = pygame.sprite.Group() # A subgroup of obstacles
        self.enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.objectives = []
        
        self.load_level_data(level_data)

    def load_level_data(self, level_data):
        for obs_data in level_data["obstacles"]:
            if obs_data["pushable"]:
                obj = PushableObject(obs_data["x"], obs_data["y"], obs_data["width"], obs_data["height"], obs_data["type"], obs_data.get("id"))
                self.pushable_objects.add(obj)
                self.obstacles.add(obj)
            else:
                self.obstacles.add(Obstacle(obs_data["x"], obs_data["y"], obs_data["width"], obs_data["height"], obs_data["type"]))
        
        for enemy_data in level_data["enemies"]:
            if enemy_data["type"] == "shore_crab":
                self.enemies.add(ShoreCrab(enemy_data["x"], enemy_data["y"], enemy_data["patrol_path"], 
                                           enemy_data["speed"], enemy_data["sight_range"], enemy_data["alert_time"]))
            elif enemy_data["type"] == "seagull":
                self.enemies.add(Seagull(enemy_data["x"], enemy_data["y"], enemy_data["speed"], 
                                         enemy_data.get("patrol_path", []), enemy_data.get("swoop_target_area", (0,0,1,1))))

        for pu_data in level_data["powerups"]:
            if pu_data["type"] == "juicy_berry":
                self.powerups.add(JuicyBerry(pu_data["x"], pu_data["y"]))
            elif pu_data["type"] == "protective_seaweed" or pu_data["type"] == "health_leaf": # Use seaweed for health_leaf
                self.powerups.add(ProtectiveSeaweed(pu_data["x"], pu_data["y"]))
            elif pu_data["type"] == "shiny_starfish":
                self.powerups.add(ShinyStarfish(pu_data["x"], pu_data["y"]))
        
        for obj_data in level_data["objectives"]:
            self.objectives.append(Objective(obj_data["type"], obj_data["description"], 
                                             obj_data.get("target_id"), obj_data.get("target_x"), 
                                             obj_data.get("target_y"), obj_data.get("target_area_radius")))


class Game:
    def __init__(self, level_data):
        pygame.init()
        pygame.mixer.init() # For sound effects
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Shelly's Shore Journey")
        self.clock = pygame.time.Clock()
        self.font_ui = pygame.font.Font(FONT_NAME, FONT_SIZE_UI)
        self.font_menu = pygame.font.Font(FONT_NAME, FONT_SIZE_MENU)
        self.font_title = pygame.font.Font(FONT_NAME, FONT_SIZE_TITLE)
        self.font_message = pygame.font.Font(FONT_NAME, FONT_SIZE_MESSAGE)

        self.game_state = MENU
        self.level_data = level_data # Store raw level data
        self.current_level = None
        self.player = None
        self.all_sprites = pygame.sprite.Group() # Not strictly used for update, but good for management
        self.enemies = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.pushable_objects = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.objectives = []

        self.level_timer = 0.0
        self.total_score = 0
        self.player_hit_this_level = False # For 'No Damage' bonus

        self.background_music = None
        self.sfx_collect = None
        self.sfx_hit = None
        self.sfx_dash = None
        self.sfx_retreat = None

        self.load_assets()

    def create_dummy_sound(self, frequency, duration, volume):
        if not HAS_NUMPY:
            class DummySound:
                def play(self, loops=0): pass
                def set_volume(self, vol): pass
            return DummySound()
            
        samplerate = 44100
        t = np.linspace(0., duration, int(samplerate * duration), endpoint=False)
        amplitude = np.iinfo(np.int16).max * volume
        data = amplitude * np.sin(2 * np.pi * frequency * t)
        
        # Pygame's sndarray.make_sound handles numpy arrays
        sound = pygame.sndarray.make_sound(data.astype(np.int16))
        return sound

    def load_assets(self):
        # Create dummy sounds
        print("Loading/Creating dummy sound assets...")
        self.background_music = self.create_dummy_sound(frequency=220, duration=2.0, volume=0.3)
        self.sfx_collect = self.create_dummy_sound(frequency=1000, duration=0.1, volume=0.5)
        self.sfx_hit = self.create_dummy_sound(frequency=200, duration=0.2, volume=0.8)
        self.sfx_dash = self.create_dummy_sound(frequency=800, duration=0.1, volume=0.4)
        self.sfx_retreat = self.create_dummy_sound(frequency=600, duration=0.1, volume=0.4)
        print("Sound assets ready.")

    def load_level(self):
        self.current_level = Level(self.level_data)
        
        self.player = Shelly(self.current_level.player_spawn["x"], self.current_level.player_spawn["y"])
        
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.current_level.obstacles)
        self.all_sprites.add(self.current_level.enemies)
        self.all_sprites.add(self.current_level.powerups)

        self.obstacles = self.current_level.obstacles
        self.pushable_objects = self.current_level.pushable_objects
        self.enemies = self.current_level.enemies
        self.powerups = self.current_level.powerups
        self.objectives = self.current_level.objectives

        self.level_timer = self.current_level.time_limit
        self.total_score = 0 # Reset score for the level
        self.player_hit_this_level = False # Reset for No Damage bonus
        self.background_music.play(-1) # Loop indefinitely

    def reset_game(self):
        self.game_state = MENU # Back to menu after game over/win
        self.background_music.stop()

    def handle_input(self, event):
        if self.game_state == MENU:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.game_state = PLAYING
                    self.load_level() # Load the level when starting
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        elif self.game_state == PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.shell_retreat(self.sfx_retreat)
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    self.player.dash(self.sfx_dash)

        elif self.game_state == GAME_OVER or self.game_state == WIN:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.reset_game()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    def update(self, dt):
        if self.game_state == PLAYING:
            # Player movement
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx += 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy -= 1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy += 1
            
            # Shelly's move function handles boundary and obstacle collisions
            self.player.move(dx, dy, list(self.obstacles), self.objectives)
            self.player.update(dt) # Player's internal timers

            # Level timer
            self.level_timer -= dt
            if self.level_timer <= 0:
                self.level_timer = 0
                self.game_state = GAME_OVER
                self.background_music.stop()
                print("Time's up! Game Over.")

            # Enemies update
            for enemy in self.enemies:
                enemy.update(dt, self.player.rect, self.player.is_retracted)
                
                # Enemy-Player collision
                if enemy.get_rect().colliderect(self.player.rect):
                    if not self.player.is_invulnerable: # Only take damage if not invulnerable
                        if enemy.enemy_type == "shore_crab" and not self.player.is_retracted:
                            self.player.take_damage(CRAB_ATTACK_DAMAGE, self.sfx_hit, self)
                        elif enemy.enemy_type == "seagull" and enemy.state == "swooping" and not self.player.is_retracted:
                            self.player.take_damage(SEAGULL_ATTACK_DAMAGE, self.sfx_hit, self)
                    
                    if self.player.health <= 0:
                        self.game_state = GAME_OVER
                        self.background_music.stop()
                        print("Shelly ran out of health! Game Over.")
                        return # Exit update to prevent further actions


            # Player-Powerup collision
            collected_powerups = pygame.sprite.spritecollide(self.player, self.powerups, True)
            for powerup in collected_powerups:
                self.sfx_collect.play()
                if powerup.type == "juicy_berry":
                    self.player.activate_berry()
                    print("Collected Juicy Berry!")
                elif powerup.type == "protective_seaweed":
                    self.player.activate_seaweed()
                    print("Collected Protective Seaweed!")
                elif powerup.type == "shiny_starfish":
                    self.player.score += STARFISH_SCORE_BONUS
                    print(f"Collected Shiny Starfish! Score: {self.player.score}")

            # Check objectives
            all_objectives_complete = True
            for objective in self.objectives:
                objective.check_completion(self.player.rect) # Only "reach_destination" is checked here
                
                if not objective.is_completed:
                    all_objectives_complete = False
            
            # Win condition
            if all_objectives_complete:
                self.game_state = WIN
                self.background_music.stop()
                print("All objectives complete! You win!")
                self.calculate_final_score()

    def calculate_final_score(self):
        time_bonus = int(self.level_timer * 10) # 10 points per second remaining
        self.player.score += time_bonus
        print(f"Time bonus: {time_bonus}")

        if not self.player_hit_this_level:
            no_damage_bonus = 200 # Example bonus
            self.player.score += no_damage_bonus
            print(f"No damage bonus: {no_damage_bonus}")

        self.total_score = self.player.score # Store final level score

    def draw(self):
        self.screen.fill(SAND_COLOR)

        if self.game_state == MENU:
            self.draw_menu()
        elif self.game_state == PLAYING:
            # Draw goal area (tide pools)
            for objective in self.objectives:
                if objective.type == "reach_destination":
                    # Add a pulsating effect to the goal for visibility
                    alpha = int(100 + 100 * math.sin(pygame.time.get_ticks() / 200))
                    goal_surface = pygame.Surface((objective.target_area_radius*2, objective.target_area_radius*2), pygame.SRCALPHA)
                    pygame.draw.circle(goal_surface, (*OCEAN_COLOR, alpha), (objective.target_area_radius, objective.target_area_radius), objective.target_area_radius)
                    self.screen.blit(goal_surface, goal_surface.get_rect(center=(objective.target_x, objective.target_y)))

            # Draw obstacles
            for obj in self.obstacles:
                obj.draw(self.screen)
            
            # Draw powerups
            for pu in self.powerups:
                pu.draw(self.screen)

            # Draw enemies
            for enemy in self.enemies:
                enemy.draw(self.screen)

            # Draw player
            self.player.draw(self.screen)

            self.draw_ui()
        elif self.game_state == GAME_OVER:
            self.draw_game_over()
        elif self.game_state == WIN:
            self.draw_win_screen()

        pygame.display.flip()

    def draw_ui(self):
        # Time remaining
        time_text = self.font_ui.render(f"Time: {int(self.level_timer)}s", True, BLACK)
        self.screen.blit(time_text, (SCREEN_WIDTH - time_text.get_width() - 10, 10))

        # Health
        health_text = self.font_ui.render(f"Health: {self.player.health}", True, BLACK)
        self.screen.blit(health_text, (10, 10))

        # Stamina bar
        stamina_bar_width = 100
        stamina_bar_height = 10
        stamina_fill = int((self.player.stamina / PLAYER_STAMINA_MAX) * stamina_bar_width)
        pygame.draw.rect(self.screen, GRAY, (10, 40, stamina_bar_width, stamina_bar_height), 1) # Outline
        pygame.draw.rect(self.screen, BLUE, (10, 40, stamina_fill, stamina_bar_height)) # Fill
        stamina_label = self.font_ui.render("Stamina", True, BLACK)
        self.screen.blit(stamina_label, (10, 55))

        # Shell retreat cooldown
        if self.player.shell_retreat_cooldown_timer > 0:
            cooldown_text = self.font_ui.render(f"Shell CD: {self.player.shell_retreat_cooldown_timer:.1f}s", True, RED)
            self.screen.blit(cooldown_text, (10, 90))
        elif self.player.is_retracted:
            retreat_text = self.font_ui.render(f"RETREATING: {self.player.shell_retreat_timer:.1f}s", True, BLACK)
            self.screen.blit(retreat_text, (10, 90))
        else:
            cooldown_text = self.font_ui.render(f"Shell CD: READY", True, GREEN)
            self.screen.blit(cooldown_text, (10, 90))

        # Powerup indicators
        if self.player.protective_seaweed_active:
            seaweed_icon = self.font_ui.render("Seaweed Active!", True, SEAWEED_COLOR)
            self.screen.blit(seaweed_icon, (10, SCREEN_HEIGHT - 30))
        if self.player.berry_active:
            berry_icon = self.font_ui.render("Berry Boost!", True, BERRY_COLOR)
            self.screen.blit(berry_icon, (10, SCREEN_HEIGHT - 60))
        
        # Objectives
        y_offset = 10
        obj_header = self.font_ui.render("Objectives:", True, BLACK)
        self.screen.blit(obj_header, (SCREEN_WIDTH // 2 - obj_header.get_width() // 2, y_offset))
        y_offset += obj_header.get_height() + 5

        for i, objective in enumerate(self.objectives):
            status = "[X]" if objective.is_completed else "[ ]"
            obj_text = self.font_ui.render(f"{status} {objective.description}", True, BLACK)
            self.screen.blit(obj_text, (SCREEN_WIDTH // 2 - obj_text.get_width() // 2, y_offset + i * (obj_text.get_height() + 2)))

    def draw_menu(self):
        title_text = self.font_menu.render("Shelly's Shore Journey", True, BLACK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        self.screen.blit(title_text, title_rect)

        play_text = self.font_message.render("Press ENTER to Start", True, BLACK)
        play_rect = play_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(play_text, play_rect)

        exit_text = self.font_ui.render("Press ESC to Quit", True, BLACK)
        exit_rect = exit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(exit_text, exit_rect)

    def draw_game_over(self):
        self.screen.fill(RED)
        game_over_text = self.font_menu.render("GAME OVER", True, WHITE)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, game_over_rect)

        score_text = self.font_title.render(f"Score: {self.total_score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(score_text, score_rect)

        restart_text = self.font_message.render("Press ENTER to Restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(restart_text, restart_rect)

    def draw_win_screen(self):
        self.screen.fill(GREEN)
        win_text = self.font_menu.render("LEVEL COMPLETE!", True, WHITE)
        win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(win_text, win_rect)

        final_score_text = self.font_title.render(f"Final Score: {self.total_score}", True, WHITE)
        final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(final_score_text, final_score_rect)

        continue_text = self.font_message.render("Press ENTER for Menu", True, WHITE)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(continue_text, continue_rect)


    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0 # Delta time in seconds

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.handle_input(event)

            if self.game_state == PLAYING:
                self.update(dt)
            
            self.draw()

        pygame.quit()
        sys.exit()


# --- Level Data (as provided, with some additions for other powerups/enemies from concept) ---
LEVEL_1_DATA = {
  "title": "Shelly's First Crawl",
  "description": "Welcome to Shelly's Shore Journey! Your first challenge is to navigate the bustling beach. Practice crawling around natural obstacles like rocks, observe and avoid the patrolling shore crabs, and learn to push aside smaller objects to clear your path. Reach the shimmering tide pools for safety!",
  "size": {
    "width": 1000,
    "height": 700
  },
  "spawn_points": [
    {
      "x": 100,
      "y": 350,
      "type": "player"
    }
  ],
  "obstacles": [
    {
      "x": 250,
      "y": 250,
      "width": 70,
      "height": 100,
      "type": "rock",
      "pushable": False
    },
    {
      "x": 600,
      "y": 300,
      "width": 100,
      "height": 50,
      "type": "driftwood",
      "pushable": False
    },
    {
      "x": 600,
      "y": 400,
      "width": 80,
      "height": 60,
      "type": "puddle",
      "pushable": False
    },
    {
      "x": 640,
      "y": 360,
      "width": 40,
      "height": 40,
      "type": "large_shell",
      "pushable": True,
      "id": "path_blocker_shell"
    }
  ],
  "powerups": [
    { # Original 'health_leaf' interpreted as Protective Seaweed
      "x": 450,
      "y": 350,
      "type": "protective_seaweed" 
    },
    { # Added from concept
      "x": 300,
      "y": 450,
      "type": "shiny_starfish"
    },
    { # Added from concept
      "x": 750,
      "y": 150,
      "type": "juicy_berry"
    }
  ],
  "enemies": [
    {
      "x": 350,
      "y": 200,
      "type": "shore_crab",
      "patrol_path": [
        [350, 200],
        [350, 500]
      ],
      "speed": 80, # pixels per second
      "sight_range": 150,
      "alert_time": 2
    },
    {
      "x": 800,
      "y": 250,
      "type": "shore_crab",
      "patrol_path": [
        [800, 250],
        [900, 250],
        [900, 450],
        [800, 450]
      ],
      "speed": 80, # pixels per second
      "sight_range": 150,
      "alert_time": 2
    },
    { # Adding a seagull from concept, not in level_data but required by full concept
      "x": 500,
      "y": 50,
      "type": "seagull",
      "patrol_path": [
        [500, 50],
        [700, 100],
        [300, 100],
        [500, 50] # Explicitly close loop
      ],
      "speed": 60, # pixels per second
      "swoop_target_area": [450, 150, 100, 100] # Example area it might target
    }
  ],
  "objectives": [
    {
      "type": "interact",
      "target_type": "pushable_shell",
      "target_id": "path_blocker_shell",
      "description": "Push the large shell to clear your path."
    },
    {
      "type": "reach_destination",
      "target_x": 950,
      "target_y": 350,
      "target_area_radius": 40,
      "description": "Reach the safety of the shimmering tide pools!"
    }
  ],
  "difficulty": "easy",
  "time_limit": 180
}

# --- Main function ---
def main():
    game = Game(LEVEL_1_DATA)
    game.run()

if __name__ == "__main__":
    main()
```