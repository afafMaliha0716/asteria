
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
BROWN = (139, 69, 19)
DARK_GREEN = (0, 100, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GOLD = (255, 215, 0)

# Player constants
PLAYER_SIZE = 40
PLAYER_SPEED = 5
PLAYER_JUMP_STRENGTH = -15
PLAYER_GRAVITY = 0.8
PLAYER_ACCELERATION = 0.5
PLAYER_FRICTION = -0.1
PLAYER_MAX_FALL_SPEED = 15

# Vine constants
VINE_SWING_SPEED_MULTIPLIER = 1.5
VINE_MAX_SWING_ANGLE = 70
VINE_ATTACH_RANGE = 50
VINE_RETRACT_SPEED = 5
VINE_EXTEND_SPEED = 5

# Enemy constants
GRUBLER_SPEED = 1
SPORER_SHOOT_DELAY = 2000 # milliseconds
SHADOW_STALKER_SPEED = 3
SHADOW_STALKER_ALERT_RANGE = 150
SHADOW_STALKER_ATTACK_COOLDOWN = 1500 # milliseconds

# Powerup constants
POWERUP_DURATION = 5000 # milliseconds

# Game state constants
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    LEVEL_COMPLETE = 3
    GAME_OVER = 4

# --- Game Objects ---

class Player(pygame.sprite.Sprite):
    GRAVITY = PLAYER_GRAVITY
    JUMP_STRENGTH = PLAYER_JUMP_STRENGTH
    
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([PLAYER_SIZE, PLAYER_SIZE])
        self.image.fill(GREEN) # Pip will be green initially
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Physics
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.acceleration = PLAYER_ACCELERATION
        self.friction = PLAYER_FRICTION
        self.max_fall_speed = PLAYER_MAX_FALL_SPEED
        
        # Abilities
        self.can_double_jump = True
        self.has_ground_pound = False # Unlockable ability
        self.ground_pound_active = False
        self.ground_pound_force = 25
        
        # Swinging
        self.is_swinging = False
        self.current_vine = None
        self.swing_angle = 0 # Current angle relative to vertical
        self.swing_omega = 0 # Angular velocity
        self.swing_radius = 0 # Distance from swing point

    def handle_input(self, platforms, vines):
        keys = pygame.key.get_pressed()

        # Horizontal movement and acceleration
        if not self.is_swinging:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.vel_x -= self.acceleration
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.vel_x += self.acceleration

            # Apply friction if no input
            if not (keys[pygame.K_LEFT] or keys[pygame.K_a]) and not (keys[pygame.K_RIGHT] or keys[pygame.K_d]):
                self.vel_x += self.friction

            # Clamp horizontal speed
            self.vel_x = max(-PLAYER_SPEED, min(PLAYER_SPEED, self.vel_x))
        
        # Jump
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]):
            if self.on_ground:
                self.vel_y = self.JUMP_STRENGTH
                self.on_ground = False
                self.can_double_jump = True # Reset double jump on landing
            elif not self.on_ground and self.can_double_jump:
                self.vel_y = self.JUMP_STRENGTH * 0.8 # Slightly weaker double jump
                self.can_double_jump = False

        # Ground Pound (if unlocked)
        if self.has_ground_pound and not self.on_ground and self.vel_y > 0 and not self.ground_pound_active:
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.ground_pound_active = True
                self.vel_y = self.ground_pound_force
                
        # Vine interaction
        if keys[pygame.K_f]: # Use 'F' key to try and grab vines
            if not self.is_swinging:
                self.try_grab_vine(vines)
        
        if self.is_swinging and self.current_vine:
            if keys[pygame.K_f]: # Release vine
                self.release_vine()
            
            # Control swing direction/momentum
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.swing_omega -= 0.05 # Counter-clockwise push
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.swing_omega += 0.05 # Clockwise push

    def try_grab_vine(self, vines):
        for vine in vines:
            # Check if player is close enough to the vine's top attachment point
            distance_to_vine_top = pygame.math.Vector2(self.rect.center).distance_to(vine.attach_point)
            if distance_to_vine_top < VINE_ATTACH_RANGE:
                self.is_swinging = True
                self.current_vine = vine
                self.swing_radius = distance_to_vine_top
                self.rect.center = vine.attach_point # Snap to vine's attachment point
                self.on_ground = False # Not on ground while swinging
                self.vel_x = 0
                self.vel_y = 0
                
                # Initial swing angle based on player's horizontal position relative to vine attachment
                dx = self.rect.centerx - vine.attach_point[0]
                self.swing_angle = pygame.math.radians(dx * 0.2) # Initial small angle
                self.swing_omega = 0
                break # Grab the first vine found

    def release_vine(self):
        if self.current_vine:
            self.is_swinging = False
            self.current_vine = None
            self.swing_radius = 0
            self.swing_angle = 0
            self.swing_omega = 0
            # Player keeps momentum from the last swing
            self.vel_x = self.swing_omega * 50 # Apply some horizontal velocity based on angular momentum
            self.vel_y = self.swing_omega * 30 # Apply some vertical velocity

    def update_swing(self):
        if self.is_swinging and self.current_vine:
            # Apply gravity to angular velocity
            self.swing_omega += self.GRAVITY * 0.1 # Slower gravity effect on swing
            
            # Limit swing speed
            self.swing_omega = max(-0.5, min(0.5, self.swing_omega))
            
            # Update swing angle
            self.swing_angle += self.swing_omega

            # Clamp swing angle to avoid extreme rotations and flipping
            self.swing_angle = max(-pygame.math.radians(VINE_MAX_SWING_ANGLE), min(pygame.math.radians(VINE_MAX_SWING_ANGLE), self.swing_angle))

            # Calculate new position based on polar coordinates
            center_x = self.current_vine.attach_point[0] + self.swing_radius * pygame.math.sin(self.swing_angle)
            center_y = self.current_vine.attach_point[1] + self.swing_radius * pygame.math.cos(self.swing_angle)
            self.rect.center = (int(center_x), int(center_y))
            
            # If swing reaches the bottom, it might be too low to swing back up effectively
            if self.rect.bottom > SCREEN_HEIGHT - 50:
                self.release_vine() # Automatically release if too low

    def apply_physics(self, platforms, crumbling_ledges):
        if not self.is_swinging:
            # Apply gravity
            self.vel_y += self.GRAVITY
            self.vel_y = min(self.vel_y, self.max_fall_speed)

            # Store old position before movement
            old_x, old_y = self.rect.x, self.rect.y

            # Update position based on velocity
            self.rect.x += self.vel_x
            self.check_platform_collisions(platforms, old_x, old_y, "x")
            
            self.rect.y += self.vel_y
            self.check_platform_collisions(platforms, old_x, old_y, "y")
            self.check_crumbling_ledge_collisions(crumbling_ledges, old_x, old_y)

            # Ground check
            self.on_ground = False
            for platform in platforms:
                if self.rect.colliderect(platform.rect) and self.vel_y > 0 and self.rect.bottom <= platform.rect.top + 5:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.can_double_jump = True # Reset double jump
                    self.ground_pound_active = False # Reset ground pound
                    break

            # Wall collision (basic clamp)
            self.rect.left = max(0, self.rect.left)
            self.rect.right = min(SCREEN_WIDTH, self.rect.right)
        else:
            self.update_swing()

    def check_platform_collisions(self, platforms, old_x, old_y, axis):
        collisions = pygame.sprite.spritecollide(self, platforms, False)
        for other in collisions:
            if axis == "x":
                if self.vel_x > 0: # Moving right
                    self.rect.right = min(other.rect.left, self.rect.right)
                if self.vel_x < 0: # Moving left
                    self.rect.left = max(other.rect.right, self.rect.left)
                self.vel_x = 0 # Stop horizontal movement on collision
            elif axis == "y":
                if self.vel_y > 0: # Moving down
                    self.rect.bottom = min(other.rect.top, self.rect.bottom)
                    self.on_ground = True # Landed on platform
                    self.can_double_jump = True # Reset double jump
                    self.ground_pound_active = False # Reset ground pound
                if self.vel_y < 0: # Moving up
                    self.rect.top = max(other.rect.bottom, self.rect.top)
                self.vel_y = 0 # Stop vertical movement on collision

    def check_crumbling_ledge_collisions(self, crumbling_ledges, old_x, old_y):
        collisions = pygame.sprite.spritecollide(self, crumbling_ledges, False)
        for ledge in collisions:
            if self.vel_y > 0 and self.rect.bottom <= ledge.rect.top + 10: # Crushing from above
                ledge.collapse()
                self.rect.bottom = ledge.rect.top
                self.vel_y = 0
                self.on_ground = True
                self.can_double_jump = True
                self.ground_pound_active = False
            elif self.vel_y < 0 and self.rect.top >= ledge.rect.bottom - 10: # Hitting from below
                self.rect.top = ledge.rect.bottom
                self.vel_y = 0
            elif self.vel_x > 0 and self.rect.right <= ledge.rect.left + 10: # Hitting from left
                self.rect.right = ledge.rect.left
                self.vel_x = 0
            elif self.vel_x < 0 and self.rect.left >= ledge.rect.right - 10: # Hitting from right
                self.rect.left = ledge.rect.right
                self.vel_x = 0

    def update(self, platforms, vines, crumbling_ledges):
        self.handle_input(platforms, vines)
        self.apply_physics(platforms, crumbling_ledges)
        self.image.fill(GREEN) # Default color

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, platform_type="ground"):
        super().__init__()
        self.image = pygame.Surface([width, height])
        if platform_type == "ground":
            self.image.fill(BROWN)
        elif platform_type == "wall":
            self.image.fill(DARK_GREEN) # Darker green for walls
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Vine(pygame.sprite.Sprite):
    def __init__(self, x, y, length, attach_point_offset_y, swing_range):
        super().__init__()
        self.image = pygame.Surface([10, length])
        self.image.fill(PURPLE) # Vines are purple
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.attach_point = (x + self.image.get_width() // 2, y + attach_point_offset_y)
        self.original_length = length
        self.current_length = length
        self.swing_range = swing_range # Degrees
        self.is_extended = True

    def update_length(self, target_length):
        if self.current_length < target_length:
            self.current_length = min(target_length, self.current_length + VINE_EXTEND_SPEED)
        elif self.current_length > target_length:
            self.current_length = max(target_length, self.current_length - VINE_RETRACT_SPEED)
        
        self.image = pygame.Surface([10, self.current_length])
        self.image.fill(PURPLE)
        self.rect.height = self.current_length
        # The attachment point remains fixed, but the sprite's visual position needs to be adjusted
        self.rect.y = self.attach_point[1] - self.current_length
        self.rect.x = self.attach_point[0] - self.image.get_width() // 2

class InteractiveVine(Vine):
    def __init__(self, x, y, attach_point_offset_y, id, initial_state="retracted", retracted_length=50, extended_length=120, swing_range=45):
        super().__init__(x, y, retracted_length if initial_state == "retracted" else extended_length, attach_point_offset_y, swing_range)
        self.id = id
        self.target_length = extended_length if initial_state == "extended" else retracted_length
        self.is_extended = (initial_state == "extended")

    def toggle_state(self):
        if self.is_extended:
            self.target_length = self.original_length # Reset to original if it was extended beyond that
        else:
            self.target_length = self.original_length
        self.is_extended = not self.is_extended
        self.update_length(self.target_length)
        
class CrumblingLedge(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(ORANGE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.initial_y = y
        self.has_collapsed = False
        self.collapse_speed = 10
        self.collapse_distance = 100 # How far it falls

    def collapse(self):
        if not self.has_collapsed:
            self.has_collapsed = True

    def update(self):
        if self.has_collapsed:
            if self.rect.y < self.initial_y + self.collapse_distance:
                self.rect.y += self.collapse_speed
            else:
                self.kill() # Remove from groups once fully fallen

class Rock(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(BROWN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class ThornyBush(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(RED) # Thorny bushes are dangerous (red)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Lever(pygame.sprite.Sprite):
    def __init__(self, x, y, linked_to):
        super().__init__()
        self.image = pygame.Surface([30, 30])
        self.image.fill(GOLD)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.linked_to = linked_to
        self.is_activated = False

    def activate(self):
        self.is_activated = True
        self.image.fill(YELLOW) # Visually indicate activation

class Grubler(pygame.sprite.Sprite):
    def __init__(self, x, y, patrol_path):
        super().__init__()
        self.image = pygame.Surface([30, 30])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.patrol_path = patrol_path
        self.current_path_index = 0
        self.speed = GRUBLER_SPEED
        self.direction = 1 # 1 for right, -1 for left

    def update(self):
        if not self.patrol_path: return

        target_x, target_y = self.patrol_path[self.current_path_index]
        
        if abs(self.rect.x - target_x) < self.speed and abs(self.rect.y - target_y) < self.speed:
            self.current_path_index = (self.current_path_index + 1) % len(self.patrol_path)
            target_x, target_y = self.patrol_path[self.current_path_index]
            
        if target_x > self.rect.x:
            self.direction = 1
            self.rect.x += self.speed
        elif target_x < self.rect.x:
            self.direction = -1
            self.rect.x -= self.speed
        
        if target_y > self.rect.y:
            self.rect.y += self.speed
        elif target_y < self.rect.y:
            self.rect.y -= self.speed

class SporePuff(pygame.sprite.Sprite):
    def __init__(self, x, y, patrol_path):
        super().__init__()
        self.image = pygame.Surface([25, 25])
        self.image.fill(ORANGE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.patrol_path = patrol_path
        self.current_path_index = 0
        self.speed = 0.5 # Very slow movement
        self.shoot_delay = SPORER_SHOOT_DELAY
        self.last_shot_time = pygame.time.get_ticks()
        self.projectile_speed = 3

    def update(self, projectiles):
        if not self.patrol_path: return

        # Patrol movement
        target_x, target_y = self.patrol_path[self.current_path_index]
        if abs(self.rect.x - target_x) < self.speed and abs(self.rect.y - target_y) < self.speed:
            self.current_path_index = (self.current_path_index + 1) % len(self.patrol_path)
            target_x, target_y = self.patrol_path[self.current_path_index]
            
        if target_x > self.rect.x: self.rect.x += self.speed
        elif target_x < self.rect.x: self.rect.x -= self.speed
        if target_y > self.rect.y: self.rect.y += self.speed
        elif target_y < self.rect.y: self.rect.y -= self.speed

        # Shooting
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.shoot_delay:
            projectile = Projectile(self.rect.centerx, self.rect.centery, (0, 1), self.projectile_speed) # Shoots downwards
            projectiles.add(projectile)
            self.last_shot_time = current_time

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed):
        super().__init__()
        self.image = pygame.Surface([10, 10])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = pygame.math.Vector2(direction).normalize()
        self.speed = speed

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        
        if not (0 <= self.rect.x < SCREEN_WIDTH and 0 <= self.rect.y < SCREEN_HEIGHT):
            self.kill()

class ShadowStalker(pygame.sprite.Sprite):
    def __init__(self, x, y, patrol_path):
        super().__init__()
        self.image = pygame.Surface([35, 35])
        self.image.fill(BLACK) # Shadowy
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.patrol_path = patrol_path
        self.current_path_index = 0
        self.speed = SHADOW_STALKER_SPEED
        self.alert_range = SHADOW_STALKER_ALERT_RANGE
        self.attack_cooldown = SHADOW_STALKER_ATTACK_COOLDOWN
        self.last_attack_time = pygame.time.get_ticks()
        self.is_alerted = False
        self.attack_target = None # The player it's currently targeting

    def update(self, player):
        if player.is_alive:
            distance_to_player = pygame.math.Vector2(self.rect.center).distance_to(player.rect.center)

            if distance_to_player < self.alert_range:
                self.is_alerted = True
                self.attack_target = player
            
            if self.is_alerted and self.attack_target:
                # Move towards player
                if self.rect.centerx < self.attack_target.rect.centerx:
                    self.rect.x += self.speed
                elif self.rect.centerx > self.attack_target.rect.centerx:
                    self.rect.x -= self.speed
                
                if self.rect.centery < self.attack_target.rect.centery:
                    self.rect.y += self.speed
                elif self.rect.centery > self.attack_target.rect.centery:
                    self.rect.y -= self.speed

                # Attack if close enough and cooldown is over
                if self.rect.colliderect(self.attack_target.rect):
                    current_time = pygame.time.get_ticks()
                    if current_time - self.last_attack_time > self.attack_cooldown:
                        self.attack_target.take_damage(10) # Deal damage to player
                        self.last_attack_time = current_time
            else:
                # Patrol behavior (if not alerted)
                if not self.patrol_path: return
                target_x, target_y = self.patrol_path[self.current_path_index]
                if abs(self.rect.x - target_x) < self.speed and abs(self.rect.y - target_y) < self.speed:
                    self.current_path_index = (self.current_path_index + 1) % len(self.patrol_path)
                    target_x, target_y = self.patrol_path[self.current_path_index]
                
                if target_x > self.rect.x: self.rect.x += self.speed
                elif target_x < self.rect.x: self.rect.x -= self.speed
                if target_y > self.rect.y: self.rect.y += self.speed
                elif target_y < self.rect.y: self.rect.y -= self.speed
        else:
            self.kill() # Remove if player is dead

class Powerup(pygame.sprite.Sprite):
    def __init__(self, x, y, powerup_type):
        super().__init__()
        self.powerup_type = powerup_type
        self.image = pygame.Surface([30, 30])
        
        if powerup_type == "guava_burst":
            self.image.fill(ORANGE) # Guava
        elif powerup_type == "spirit_leaf":
            self.image.fill(GREEN) # Leaf
        elif powerup_type == "health_potion":
            self.image.fill(RED) # Health potion
        elif powerup_type == "momentum_boost":
            self.image.fill(YELLOW) # Momentum boost
        else:
            self.image.fill(BLUE) # Default

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.duration = POWERUP_DURATION
        self.spawn_time = pygame.time.get_ticks()

    def apply_effect(self, player):
        if self.powerup_type == "guava_burst":
            player.acceleration *= 1.5
            player.JUMP_STRENGTH *= 1.2
            player.max_fall_speed *= 1.1
            # The effect is temporary and will be reverted in the main loop
        elif self.powerup_type == "spirit_leaf":
            player.has_shield = True # Temporary shield flag
        elif self.powerup_type == "health_potion":
            player.heal(25) # Assuming Player has a heal method
        elif self.powerup_type == "momentum_boost":
            player.vel_x *= 1.5 # Boost current momentum


class HealthBar:
    def __init__(self, x, y, width, height, color_bg=RED, color_fg=GREEN):
        self.rect = pygame.Rect(x, y, width, height)
        self.color_bg = color_bg
        self.color_fg = color_fg
        self.width = width

    def draw(self, surface, current_health, max_health):
        health_ratio = current_health / max_health
        fill_width = int(self.width * health_ratio)
        
        pygame.draw.rect(surface, self.color_bg, self.rect)
        pygame.draw.rect(surface, self.color_fg, (self.rect.x, self.rect.y, fill_width, self.rect.height))

class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y, collectible_type):
        super().__init__()
        self.collectible_type = collectible_type
        self.image = pygame.Surface([20, 20])
        
        if collectible_type == "glowing_berries":
            self.image.fill(YELLOW)
        elif collectible_type == "ancient_relic":
            self.image.fill(GOLD)
        else:
            self.image.fill(BLUE)

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

# --- Level Data ---
level_data = {
    "level_number": 1,
    "name": "Whispering Canopy",
    "description": "Begin your journey in the tranquil lower canopy, learning the basics of vine swinging and navigating the vibrant jungle. A few mischievous creatures have made their home here, so tread carefully.",
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
            "x": 250,
            "y": 280,
            "width": 50,
            "height": 50,
            "type": "rock"
        },
        {
            "x": 400,
            "y": 450,
            "width": 60,
            "height": 60,
            "type": "thorny_bush"
        },
        {
            "x": 650,
            "y": 350,
            "width": 70,
            "height": 40,
            "type": "crumbling_ledge"
        }
    ],
    "vines": [
        {
            "x": 150,
            "y": 150,
            "length": 100,
            "attach_point_offset_y": 0, # Assuming vine starts at y, attaches at y
            "swing_range": 45
        },
        {
            "x": 300,
            "y": 150,
            "length": 120,
            "attach_point_offset_y": 0,
            "swing_range": 60
        },
        {
            "x": 550,
            "y": 250,
            "length": 80,
            "attach_point_offset_y": 0,
            "swing_range": 30
        },
        {
            "x": 700,
            "y": 300,
            "length": 100,
            "attach_point_offset_y": 0,
            "swing_range": 50
        },
        {
            "x": 450,
            "y": 500,
            "length": 60,
            "attach_point_offset_y": 0,
            "swing_range": 20
        }
    ],
    "platforms": [
        {
            "x": 50,
            "y": 250,
            "width": 100,
            "height": 20,
            "type": "ground"
        },
        {
            "x": 250,
            "y": 350,
            "width": 150,
            "height": 20,
            "type": "ground"
        },
        {
            "x": 500,
            "y": 250,
            "width": 120,
            "height": 20,
            "type": "ground"
        },
        {
            "x": 700,
            "y": 400,
            "width": 80,
            "height": 20,
            "type": "ground"
        },
        {
            "x": 400,
            "y": 550,
            "width": 200,
            "height": 20,
            "type": "ground"
        }
    ],
    "powerups": [
        {
            "x": 300,
            "y": 100,
            "type": "health_potion"
        },
        {
            "x": 600,
            "y": 200,
            "type": "momentum_boost"
        }
    ],
    "enemies": [
        {
            "x": 450,
            "y": 220,
            "type": "vine_crawler", # Assuming this is a placeholder for Grubler
            "patrol_path": [
                [
                    450,
                    220
                ],
                [
                    520,
                    220
                ]
            ]
        },
        {
            "x": 720,
            "y": 380,
            "type": "spore_puff",
            "patrol_path": [
                [
                    720,
                    380
                ],
                [
                    750,
                    380
                ]
            ]
        },
        {
            "x": 180,
            "y": 330,
            "type": "vine_crawler", # Assuming this is a placeholder for Grubler
            "patrol_path": [
                [
                    180,
                    330
                ],
                [
                    220,
                    330
                ]
            ]
        }
    ],
    "environmental_elements": [
        {
            "x": 580,
            "y": 380,
            "type": "lever",
            "linked_to": "vine_extender_1"
        }
    ],
    "interactive_vines": [
        {
            "x": 580,
            "y": 300,
            "type": "vine_extender",
            "id": "vine_extender_1",
            "initial_state": "retracted",
            "retracted_length": 50,
            "extended_length": 120
        }
    ],
    "objectives": [
        {
            "type": "collect",
            "target": "glowing_berries",
            "count": 5
        },
        {
            "type": "reach",
            "location": {
                "x": 750,
                "y": 450
            }
        },
        {
            "type": "defeat",
            "target": "enemies",
            "count": 3
        }
    ],
    "difficulty": "easy",
    "time_limit": 180 # seconds
}

# --- Game State Variables ---
current_state = GameState.MENU
player = None
all_sprites = None
platforms = None
vines = None
crumbling_ledges = None
rocks = None
thorny_bushes = None
levers = None
projectiles = None
powerups = None
collectibles = None
enemies = None
health_bars = None
font_large = None
font_medium = None
font_small = None
score = 0
score_multiplier = 1
level_timer = 0
collectibles_collected_count = 0
enemies_defeated_count = 0
game_over_reason = ""

# --- Helper Functions ---

def load_level(level_data):
    global player, all_sprites, platforms, vines, crumbling_ledges, rocks, thorny_bushes, levers, projectiles, powerups, collectibles, enemies
    
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    vines = pygame.sprite.Group()
    crumbling_ledges = pygame.sprite.Group()
    rocks = pygame.sprite.Group()
    thorny_bushes = pygame.sprite.Group()
    levers = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    collectibles = pygame.sprite.Group()
    enemies = pygame.sprite.Group()

    # Spawn point
    player_start_pos = (level_data["spawn_points"][0]["x"], level_data["spawn_points"][0]["y"])
    player = Player(player_start_pos[0], player_start_pos[1])
    all_sprites.add(player)

    # Platforms
    for p_data in level_data["platforms"]:
        platform = Platform(p_data["x"], p_data["y"], p_data["width"], p_data["height"], p_data["type"])
        platforms.add(platform)
        all_sprites.add(platform)

    # Obstacles
    for o_data in level_data["obstacles"]:
        if o_data["type"] == "rock":
            obstacle = Rock(o_data["x"], o_data["y"], o_data["width"], o_data["height"])
            rocks.add(obstacle)
            all_sprites.add(obstacle)
        elif o_data["type"] == "thorny_bush":
            obstacle = ThornyBush(o_data["x"], o_data["y"], o_data["width"], o_data["height"])
            thorny_bushes.add(obstacle)
            all_sprites.add(obstacle)
        elif o_data["type"] == "crumbling_ledge":
            obstacle = CrumblingLedge(o_data["x"], o_data["y"], o_data["width"], o_data["height"])
            crumbling_ledges.add(obstacle)
            all_sprites.add(obstacle)

    # Vines
    for v_data in level_data["vines"]:
        vine = Vine(v_data["x"], v_data["y"], v_data["length"], v_data["attach_point_offset_y"], v_data["swing_range"])
        vines.add(vine)
        all_sprites.add(vine)

    # Interactive Vines
    for iv_data in level_data["interactive_vines"]:
        interactive_vine = InteractiveVine(iv_data["x"], iv_data["y"], 0, iv_data["id"], iv_data["initial_state"], iv_data["retracted_length"], iv_data["extended_length"], iv_data["swing_range"])
        vines.add(interactive_vine) # Add to the general vines group too
        all_sprites.add(interactive_vine)
    
    # Environmental Elements (Levers)
    for e_data in level_data["environmental_elements"]:
        if e_data["type"] == "lever":
            lever = Lever(e_data["x"], e_data["y"], e_data["linked_to"])
            levers.add(lever)
            all_sprites.add(lever)

    # Powerups
    for p_data in level_data["powerups"]:
        powerup = Powerup(p_data["x"], p_data["y"], p_data["type"])
        powerups.add(powerup)
        all_sprites.add(powerup)
        
    # Collectibles
    for c_data in level_data["objectives"]:
        if c_data["type"] == "collect":
            target_type = c_data["target"]
            for _ in range(c_data["count"]):
                # For now, place them at the same spot, would need specific placements
                collectible = Collectible(100 + _ * 30, 100, target_type) # Example placement
                collectibles.add(collectible)
                all_sprites.add(collectible)

    # Enemies
    for e_data in level_data["enemies"]:
        if e_data["type"] == "vine_crawler": # Assuming this is Grubler
            enemy = Grubler(e_data["x"], e_data["y"], e_data["patrol_path"])
        elif e_data["type"] == "spore_puff":
            enemy = SporePuff(e_data["x"], e_data["y"], e_data["patrol_path"])
        elif e_data["type"] == "shadow_stalker": # For later levels
            enemy = ShadowStalker(e_data["x"], e_data["y"], e_data["patrol_path"])
        else:
            enemy = None # Unknown enemy type

        if enemy:
            enemies.add(enemy)
            all_sprites.add(enemy)

    # Initialize health bars for player and enemies
    global health_bars
    health_bars = pygame.sprite.Group()
    if player:
        player_health_bar = HealthBar(player.rect.x, player.rect.y - 10, player.rect.width, 5)
        health_bars.add(player_health_bar)

    for enemy in enemies:
        enemy_health_bar = HealthBar(enemy.rect.x, enemy.rect.y - 10, enemy.rect.width, 5)
        health_bars.add(enemy_health_bar)

def reset_game_state():
    global current_state, player, all_sprites, platforms, vines, crumbling_ledges, rocks, thorny_bushes, levers, projectiles, powerups, collectibles, enemies, health_bars, score, score_multiplier, level_timer, collectibles_collected_count, enemies_defeated_count, game_over_reason
    
    current_state = GameState.MENU
    player = None
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    vines = pygame.sprite.Group()
    crumbling_ledges = pygame.sprite.Group()
    rocks = pygame.sprite.Group()
    thorny_bushes = pygame.sprite.Group()
    levers = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    collectibles = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    health_bars = pygame.sprite.Group()
    
    score = 0
    score_multiplier = 1
    level_timer = 0
    collectibles_collected_count = 0
    enemies_defeated_count = 0
    game_over_reason = ""

def update_score(points):
    global score, score_multiplier
    score += points * score_multiplier

def apply_powerup_effects(player):
    current_time = pygame.time.get_ticks()
    
    # Reset player stats that were modified by temporary powerups
    if not hasattr(player, 'powerup_active_time') or current_time - player.powerup_active_time > POWERUP_DURATION:
        # Revert Guava Burst effects
        if hasattr(player, 'original_acceleration'):
            player.acceleration = player.original_acceleration
            player.JUMP_STRENGTH = player.original_jump_strength
            player.max_fall_speed = player.original_max_fall_speed
            del player.original_acceleration
            del player.original_jump_strength
            del player.original_max_fall_speed
        
        # Revert Spirit Leaf effect
        if hasattr(player, 'has_shield'):
            del player.has_shield

    # If a powerup is currently active, ensure its effects are applied
    for pu in powerups:
        if pu.rect.colliderect(player.rect):
            if pu.powerup_type == "guava_burst":
                if not hasattr(player, 'powerup_active_time'):
                    player.original_acceleration = player.acceleration
                    player.original_jump_strength = player.JUMP_STRENGTH
                    player.original_max_fall_speed = player.max_fall_speed
                    player.powerup_active_time = current_time
                player.acceleration *= 1.5
                player.JUMP_STRENGTH *= 1.2
                player.max_fall_speed *= 1.1
            elif pu.powerup_type == "spirit_leaf":
                if not hasattr(player, 'powerup_active_time'):
                    player.powerup_active_time = current_time
                player.has_shield = True
            elif pu.powerup_type == "health_potion":
                player.heal(25)
                pu.kill() # Consume immediately
            elif pu.powerup_type == "momentum_boost":
                player.vel_x *= 1.5
                pu.kill() # Consume immediately
            break # Only one powerup can be picked up at a time

def check_objective_completion(player):
    global current_state, collectibles_collected_count, enemies_defeated_count
    
    # Check collect objective
    collected_count = 0
    for c in collectibles:
        if player.rect.colliderect(c.rect):
            if c.collectible_type == "glowing_berries":
                update_score(10)
                collected_count += 1
            elif c.collectible_type == "ancient_relic":
                update_score(50)
                # Potentially unlock new areas or abilities
            c.kill() # Remove collected item
    collectibles_collected_count += collected_count
    
    # Check reach objective
    for obj in level_data["objectives"]:
        if obj["type"] == "reach":
            if pygame.math.Vector2(player.rect.center).distance_to(pygame.math.Vector2(obj["location"]["x"], obj["location"]["y"])) < 30:
                # Mark as completed, or move to next level if this is the final objective
                pass # For now, assume reaching the end of the level implies this
    
    # Check defeat objective
    # The count is managed by the enemy kill logic

    # Determine if all objectives are met
    all_collected = True
    for obj in level_data["objectives"]:
        if obj["type"] == "collect":
            if collectibles_collected_count < obj["count"]:
                all_collected = False
                break
        # Add checks for other objective types if needed
    
    all_defeated = True
    for obj in level_data["objectives"]:
        if obj["type"] == "defeat":
            if enemies_defeated_count < obj["count"]:
                all_defeated = False
                break
    
    if all_collected and all_defeated:
        current_state = GameState.LEVEL_COMPLETE

def check_enemy_collision_with_player(player, enemies, projectiles):
    global score_multiplier, enemies_defeated_count
    
    # Player collision with enemies
    for enemy in pygame.sprite.spritecollide(player, enemies, False):
        if not player.ground_pound_active and not (player.is_swinging and player.current_vine): # If not attacking from above or swinging
            if hasattr(player, 'has_shield') and player.has_shield:
                player.has_shield = False # Shield used
                enemy.kill() # Enemy defeated by shield
                update_score(20)
                enemies_defeated_count += 1
            else:
                player.take_damage(10) # Deal damage to player
                # Maybe knockback player or enemy
        elif player.ground_pound_active and player.vel_y > 0: # Player ground pounding
            enemy.kill()
            update_score(20)
            enemies_defeated_count += 1
            player.ground_pound_active = False # End ground pound
            player.vel_y = 0 # Stop downward momentum
            player.on_ground = True # Landed
        elif player.is_swinging and player.current_vine: # Player swinging
            # Could add logic for attacking while swinging, e.g., if enemy is below
            pass

    # Player collision with projectiles
    for proj in pygame.sprite.spritecollide(player, projectiles, False):
        if hasattr(player, 'has_shield') and player.has_shield:
            player.has_shield = False
            proj.kill()
        else:
            player.take_damage(5) # Projectile damage
            proj.kill()

    # Player collision with thorny bushes
    for bush in pygame.sprite.spritecollide(player, thorny_bushes, False):
        if hasattr(player, 'has_shield') and player.has_shield:
            player.has_shield = False
            bush.kill() # Assuming shield destroys bush
        else:
            player.take_damage(15) # Thorny bush damage


# --- State Management Functions ---

def run_menu_state(events):
    global current_state, player

    # Drawing
    screen.fill(BLACK)
    title_text = font_large.render("Vinebound Odyssey", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 3))
    
    instruction_text = font_small.render("Press SPACE to Start", True, WHITE)
    screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

    # Input Logic
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                reset_game_state() # Reset all game variables
                load_level(level_data) # Load the first level
                current_state = GameState.PLAYING

def run_playing_state(events):
    global score, score_multiplier, level_timer, current_state, game_over_reason

    # Update Timer
    dt = clock.get_time() / 1000.0 # Delta time in seconds
    level_timer += dt

    # Update Game Objects
    platforms.update()
    vines.update() # For interactive vines that extend/retract
    crumbling_ledges.update()
    
    # Update enemies (pass player and other groups as needed)
    for enemy in enemies:
        if isinstance(enemy, Grubler):
            enemy.update()
        elif isinstance(enemy, SporePuff):
            enemy.update(projectiles)
        elif isinstance(enemy, ShadowStalker):
            enemy.update(player)

    projectiles.update()

    # Player update requires other groups for collision detection
    player.update(platforms, vines, crumbling_ledges)

    # Collision Checks
    check_enemy_collision_with_player(player, enemies, projectiles)
    
    # Player collision with obstacles
    for rock in rocks:
        if player.rect.colliderect(rock.rect):
            # Basic collision response: if player was moving into rock, stop movement
            if player.vel_x > 0 and player.rect.right > rock.rect.left and player.rect.left < rock.rect.left:
                player.rect.right = rock.rect.left
                player.vel_x = 0
            elif player.vel_x < 0 and player.rect.left < rock.rect.right and player.rect.right > rock.rect.right:
                player.rect.left = rock.rect.right
                player.vel_x = 0
            if player.vel_y > 0 and player.rect.bottom > rock.rect.top and player.rect.top < rock.rect.top:
                player.rect.bottom = rock.rect.top
                player.vel_y = 0
                player.on_ground = True
            elif player.vel_y < 0 and player.rect.top < rock.rect.bottom and player.rect.bottom > rock.rect.bottom:
                player.rect.top = rock.rect.bottom
                player.vel_y = 0

    for bush in thorny_bushes:
        if player.rect.colliderect(bush.rect):
             if hasattr(player, 'has_shield') and player.has_shield:
                player.has_shield = False
                bush.kill()
             else:
                player.take_damage(15) # Thorny bush damage
                # Knockback player slightly
                if player.rect.centerx < bush.rect.centerx: player.vel_x = -5
                else: player.vel_x = 5
                player.vel_y = -5 # Knock up slightly

    # Player collision with levers
    for lever in levers:
        if player.rect.colliderect(lever.rect):
            if lever.is_activated == False: # Only activate if not already
                # Find the interactive vine it's linked to
                for iv in vines:
                    if isinstance(iv, InteractiveVine) and iv.id == lever.linked_to:
                        iv.toggle_state()
                        lever.activate()
                        break # Found and activated the vine

    # Player collision with powerups
    for pu in pygame.sprite.spritecollide(player, powerups, False):
        # Store powerup info on player to manage effects and duration
        player.active_powerup = pu
        player.powerup_spawn_time = pygame.time.get_ticks()
        pu.kill() # Remove from scene

    # Apply active powerup effects
    if hasattr(player, 'active_powerup') and player.active_powerup:
        current_time = pygame.time.get_ticks()
        if current_time - player.powerup_spawn_time < player.active_powerup.duration:
            if player.active_powerup.powerup_type == "guava_burst":
                if not hasattr(player, 'original_acceleration'):
                    player.original_acceleration = player.acceleration
                    player.original_jump_strength = player.JUMP_STRENGTH
                    player.original_max_fall_speed = player.max_fall_speed
                player.acceleration *= 1.5
                player.JUMP_STRENGTH *= 1.2
                player.max_fall_speed *= 1.1
            elif player.active_powerup.powerup_type == "spirit_leaf":
                player.has_shield = True
            # Health potion and momentum boost are applied immediately and consumed
        else:
            # Powerup duration ended, revert effects
            if player.active_powerup.powerup_type == "guava_burst":
                if hasattr(player, 'original_acceleration'):
                    player.acceleration = player.original_acceleration
                    player.JUMP_STRENGTH = player.original_jump_strength
                    player.max_fall_speed = player.original_max_fall_speed
                    del player.original_acceleration
                    del player.original_jump_strength
                    del player.original_max_fall_speed
            elif player.active_powerup.powerup_type == "spirit_leaf":
                del player.has_shield
            
            player.active_powerup = None # Clear active powerup

    # Collectible collection
    for c in pygame.sprite.spritecollide(player, collectibles, False):
        if c.collectible_type == "glowing_berries":
            update_score(10)
            collectibles_collected_count += 1
            c.kill()
        elif c.collectible_type == "ancient_relic":
            update_score(50)
            # Potentially unlock new areas or abilities
            c.kill()

    # Update Score Multiplier (e.g., for vine chains)
    if player.is_swinging:
        score_multiplier = 2 # Example: Double score while swinging
    else:
        score_multiplier = 1 # Reset multiplier

    # Check Objectives and Game Over Conditions
    check_objective_completion(player)

    if not player.is_alive:
        game_over_reason = "Pip was defeated!"
        current_state = GameState.GAME_OVER

    if level_timer > level_data["time_limit"]:
        game_over_reason = "Time ran out!"
        current_state = GameState.GAME_OVER

    # Drawing
    screen.fill(DARK_GREEN) # Lush jungle background

    # Draw parallax layers if implemented
    
    # Draw platforms and obstacles
    all_sprites.draw(screen)

    # Draw health bars for alive entities
    for entity in all_sprites:
        if hasattr(entity, 'current_health') and hasattr(entity, 'max_health') and entity.is_alive:
            bar_rect = pygame.Rect(entity.rect.x, entity.rect.y - 10, entity.rect.width, 5)
            health_bar = HealthBar(bar_rect.x, bar_rect.y, bar_rect.width, bar_rect.height)
            health_bar.draw(screen, entity.current_health, entity.max_health)

    # Draw UI elements
    score_text = font_small.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    multiplier_text = font_small.render(f"Multiplier: {score_multiplier}x", True, YELLOW)
    screen.blit(multiplier_text, (10, 30))

    timer_text = font_small.render(f"Time: {int(level_data['time_limit'] - level_timer)}", True, WHITE)
    screen.blit(timer_text, (SCREEN_WIDTH - timer_text.get_width() - 10, 10))
    
    objective_text = font_small.render(f"Berries: {collectibles_collected_count}/{len([obj for obj in level_data['objectives'] if obj['type'] == 'collect'][0]['count'])}", True, WHITE)
    screen.blit(objective_text, (SCREEN_WIDTH - objective_text.get_width() - 10, 30))

def run_level_complete_state(events):
    global current_state
    screen.fill(BLACK)
    completion_text = font_large.render("Level Complete!", True, GREEN)
    screen.blit(completion_text, (SCREEN_WIDTH // 2 - completion_text.get_width() // 2, SCREEN_HEIGHT // 3))

    score_text = font_medium.render(f"Final Score: {score}", True, WHITE)
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
    
    next_level_instruction = font_small.render("Press SPACE to proceed (or R to restart)", True, WHITE)
    screen.blit(next_level_instruction, (SCREEN_WIDTH // 2 - next_level_instruction.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Logic to load next level or go to main menu
                current_state = GameState.MENU # For now, go back to menu
            elif event.key == pygame.K_r:
                reset_game_state()
                load_level(level_data) # Reload the current level
                current_state = GameState.PLAYING

def run_game_over_state(events):
    global current_state
    screen.fill(BLACK)
    game_over_text = font_large.render("Game Over", True, RED)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 3))

    reason_text = font_medium.render(game_over_reason, True, WHITE)
    screen.blit(reason_text, (SCREEN_WIDTH // 2 - reason_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))

    score_text = font_medium.render(f"Final Score: {score}", True, WHITE)
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 30))
    
    restart_instruction = font_small.render("Press R to Restart or M for Menu", True, WHITE)
    screen.blit(restart_instruction, (SCREEN_WIDTH // 2 - restart_instruction.get_width() // 2, SCREEN_HEIGHT // 2 + 80))

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_game_state()
                load_level(level_data) # Reload the current level
                current_state = GameState.PLAYING
            elif event.key == pygame.K_m:
                reset_game_state()
                current_state = GameState.MENU


# --- Initialization ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Vinebound Odyssey")
clock = pygame.time.Clock()

# Fonts
font_large = pygame.font.Font(None, 74)
font_medium = pygame.font.Font(None, 50)
font_small = pygame.font.Font(None, 36)

# Initialize game state
reset_game_state()


# --- Main Game Loop ---
running = True
while running:
    # 1. Event Handling
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    # 2. State Management
    if current_state == GameState.MENU:
        run_menu_state(events)
    elif current_state == GameState.PLAYING:
        run_playing_state(events)
    elif current_state == GameState.LEVEL_COMPLETE:
        run_level_complete_state(events)
    elif current_state == GameState.GAME_OVER:
        run_game_over_state(events)
    
    # 3. Drawing
    pygame.display.flip()
    
    # 4. Cap the frame rate
    clock.tick(FPS)

# --- Cleanup ---
pygame.quit()
sys.exit()
