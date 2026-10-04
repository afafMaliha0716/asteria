
# --- Core Setup ---
# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Color definitions (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Game constants for Chrono-Chimp
GRAVITY = 0.8
PLAYER_MOVE_SPEED = 5
PLAYER_JUMP_STRENGTH = -18
PLAYER_MAX_FALL_SPEED = 15
PLAYER_SWING_SPEED_MULTIPLIER = 1.5
PLAYER_STAMINA_MAX = 100
PLAYER_STAMINA_REGEN_RATE = 0.5
PLAYER_STAMINA_DRAIN_RATE = 2.0 # Per second while swinging

# Vines
VINE_GRAB_RADIUS = 50
VINE_SWING_POINT_OFFSET_Y = -20 # Offset for where the player hangs from the vine

# Grappling Hook
GRAPPLE_RANGE = 300
GRAPPLE_SPEED = 20
GRAPPLE_RETRACT_SPEED = 30

# Enemy constants
SNARK_SERPENT_SPEED = 2
PARROT_SNIPER_PROJECTILE_SPEED = 7
PARROT_SNIPER_FIRE_RATE = 2 # shots per second

# --- Initialization ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chrono-Chimp's Grand Voyage")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

# --- Asset Loading ---
# Placeholder for image loading - actual assets would be loaded here
# Example: player_img = pygame.image.load(resource_path('assets/player.png')).convert_alpha()
# For now, we'll use colored surfaces.

def create_colored_surface(color, width, height):
    surface = pygame.Surface((width, height))
    surface.fill(color)
    return surface

# Player assets
player_img_stand = create_colored_surface(RED, 40, 60)
player_img_swing = create_colored_surface(YELLOW, 40, 60) # Placeholder
player_img_grapple = create_colored_surface(ORANGE, 40, 60) # Placeholder

# Enemy assets
tarantula_img = create_colored_surface(BROWN, 30, 30)
parrot_sniper_img = create_colored_surface(GREEN, 40, 40)
parrot_sniper_projectile_img = create_colored_surface(BLUE, 10, 10)

# Powerup assets
banana_bunch_img = create_colored_surface(YELLOW, 30, 30)
grappling_hook_upgrade_img = create_colored_surface(BLUE, 30, 30)

# Environment assets
vine_img = create_colored_surface(BROWN, 10, 1) # Will be stretched
rock_ledge_img = create_colored_surface(BLACK, 100, 50)
dense_foliage_img = create_colored_surface((0, 100, 0), 75, 75)
crumbling_branch_img = create_colored_surface(BROWN, 150, 30)
lever_img_off = create_colored_surface(RED, 20, 40)
lever_img_on = create_colored_surface(GREEN, 20, 40)
moving_platform_img = create_colored_surface(RED, 80, 20)

# --- Game State Management ---
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3

current_state = GameState.MENU
score = 0
level_timer = 0 # In seconds

# --- Game Entities ---

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = player_img_stand
        self.rect = self.image.get_rect(center=(x, y))
        
        # Physics and movement
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.is_climbing = False
        self.is_swinging = False
        self.is_grappling = False

        self.max_health = 100
        self.current_health = 100

        # Stamina system
        self.max_stamina = PLAYER_STAMINA_MAX
        self.current_stamina = self.max_stamina
        self.stamina_regen_rate = PLAYER_STAMINA_REGEN_RATE
        self.stamina_drain_rate = PLAYER_STAMINA_DRAIN_RATE

        # Swinging
        self.current_vine = None
        self.swing_angle = 0
        self.swing_angular_velocity = 0
        self.swing_pivot = pygame.math.Vector2(0, 0)

        # Grappling hook
        self.grapple_pos = None
        self.grapple_vector = pygame.math.Vector2(0, 0)
        self.grappling_hook_upgrade = False

        # Objective tracking
        self.map_pieces_collected = 0
        self.total_map_pieces = 5 # This should be determined by the level design

    def take_damage(self, amount):
        self.current_health -= amount
        self.current_health = max(0, self.current_health)
        if self.current_health == 0:
            self.die()

    def heal(self, amount):
        self.current_health += amount
        self.current_health = min(self.current_health, self.max_health)

    def restore_stamina(self, amount):
        self.current_stamina += amount
        self.current_stamina = min(self.current_stamina, self.max_stamina)

    def drain_stamina(self, amount):
        self.current_stamina -= amount
        self.current_stamina = max(0, self.current_stamina)

    def die(self):
        global current_state
        current_state = GameState.GAME_OVER
        print("Player died!")

    def update(self, platforms, vines, levers, grapple_points):
        if self.current_health <= 0:
            self.die()
            return

        # Stamina regeneration
        if not self.is_swinging and not self.is_grappling:
            self.restore_stamina(self.stamina_regen_rate)

        # Handle horizontal movement (unless swinging/grappling)
        if not self.is_swinging and not self.is_grappling:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.vel_x = -PLAYER_MOVE_SPEED
                self.image = pygame.transform.flip(player_img_stand, True, False)
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.vel_x = PLAYER_MOVE_SPEED
                self.image = player_img_stand
            else:
                self.vel_x = 0
        else:
            self.vel_x = 0 # Override horizontal movement when swinging/grappling

        # Apply gravity (unless swinging)
        if not self.is_swinging:
            self.vel_y += GRAVITY
            self.vel_y = min(self.vel_y, PLAYER_MAX_FALL_SPEED)
        else:
            # Swinging physics
            self.swing_angular_velocity += 0.1 * (self.current_stamina / self.max_stamina) # Influence swing by stamina
            self.swing_angular_velocity = min(self.swing_angular_velocity, 0.3) # Cap angular velocity
            
            if self.current_stamina > 0:
                self.drain_stamina(PLAYER_STAMINA_DRAIN_RATE / FPS * 2) # Drain stamina while swinging
            
            self.swing_angle += self.swing_angular_velocity
            
            # Update player position based on swing
            rad = self.swing_angle
            self.rect.centerx = self.swing_pivot.x + (self.rect.width * 1.5) * pygame.math.sin(rad) # Adjust radius for swing arc
            self.rect.centery = self.swing_pivot.y + (self.rect.width * 1.5) * pygame.math.cos(rad)

            # Check for releasing swing
            keys = pygame.key.get_pressed()
            if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.current_stamina > 0:
                 self.release_swing(keys[pygame.K_LEFT] or keys[pygame.K_a], keys[pygame.K_RIGHT] or keys[pygame.K_d])

        # Grappling hook logic
        if self.is_grappling:
            if self.grapple_pos:
                self.grapple_vector = pygame.math.Vector2(self.grapple_pos) - pygame.math.Vector2(self.rect.center)
                distance = self.grapple_vector.length()

                if distance > GRAPPLE_RANGE or distance < 10: # Out of range or hit target
                    self.is_grappling = False
                    self.grapple_pos = None
                    if not self.on_ground:
                        self.vel_y = 0 # Stop falling if grapple breaks
                    return

                # Pull player towards grapple point
                pull_force = self.grapple_vector.normalize() * (distance / GRAPPLE_RANGE) * 15 # Stronger pull when closer
                self.rect.centerx += pull_force.x
                self.rect.centery += pull_force.y
                
                # Check for collision with platforms while grappling
                for platform in platforms:
                    if self.rect.colliderect(platform.rect):
                        self.rect.centerx -= pull_force.x # Revert movement
                        self.rect.centery -= pull_force.y
                        self.is_grappling = False
                        self.grapple_pos = None
                        break

        # Apply movement and collision checks
        old_x, old_y = self.rect.x, self.rect.y

        # Horizontal collision
        self.rect.x += self.vel_x
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0: # Moving right
                    self.rect.right = platform.rect.left
                elif self.vel_x < 0: # Moving left
                    self.rect.left = platform.rect.right
                self.vel_x = 0 # Stop horizontal movement
                break

        # Vertical collision (and ground check)
        if not self.is_swinging:
            self.rect.y += self.vel_y
            self.on_ground = False
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    if self.vel_y > 0: # Falling
                        self.rect.bottom = platform.rect.top
                        self.vel_y = 0
                        self.on_ground = True
                    elif self.vel_y < 0: # Jumping into platform
                        self.rect.top = platform.rect.bottom
                        self.vel_y = 0
                    break
        
        # Clamp player within screen bounds
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)

        # Update image based on state
        if self.is_swinging:
            self.image = player_img_swing
        elif self.is_grappling:
            self.image = player_img_grapple
        else:
            self.image = player_img_stand
            if self.vel_x < 0:
                self.image = pygame.transform.flip(self.image, True, False)
            elif self.vel_x > 0:
                self.image = pygame.transform.flip(self.image, False, False)

        # If player fell off the map
        if self.rect.top > SCREEN_HEIGHT:
            self.die()
    
    def try_grab_vine(self, vines):
        if self.is_swinging or self.is_grappling:
            return

        for vine in vines:
            vine_top = vine.rect.top
            vine_bottom = vine.rect.bottom
            vine_center_x = vine.rect.centerx

            # Check if player is horizontally aligned and within reach above the vine
            if abs(self.rect.centerx - vine_center_x) < 30 and \
               vine_top - 50 < self.rect.bottom < vine_top + 10 and \
               self.vel_y < 0: # Moving upwards
                
                # Check distance from the vine's top point
                vine_grab_point = pygame.math.Vector2(vine_center_x, vine_top)
                player_center = pygame.math.Vector2(self.rect.centerx, self.rect.centery)
                
                if player_center.distance_to(vine_grab_point) < VINE_GRAB_RADIUS:
                    self.start_swing(vine)
                    break

    def start_swing(self, vine):
        self.is_swinging = True
        self.current_vine = vine
        self.swing_pivot = pygame.math.Vector2(vine.rect.centerx, vine.rect.top + VINE_SWING_POINT_OFFSET_Y)
        
        # Calculate initial angle and velocity based on player's current momentum
        player_pos = pygame.math.Vector2(self.rect.center)
        relative_pos = player_pos - self.swing_pivot
        self.swing_angle = pygame.math.Vector2(0, 1).angle_to(relative_pos) # Angle from the vertical down
        if relative_pos.x < 0:
            self.swing_angle = -self.swing_angle
        
        self.swing_angular_velocity = pygame.math.Vector2(self.vel_x, self.vel_y).angle_to(pygame.math.Vector2(0, 1)) / 50 # Initial push from player's velocity

        self.vel_y = 0 # Reset vertical velocity

    def release_swing(self, move_left, move_right):
        self.is_swinging = False
        self.current_vine = None
        
        # Apply velocity based on swing direction and player input
        # Convert angle back to velocity components
        rad = pygame.math.radians(self.swing_angle)
        release_speed = self.swing_angular_velocity * 30 # Scale the velocity
        
        self.vel_x = release_speed * pygame.math.sin(rad) * PLAYER_SWING_SPEED_MULTIPLIER
        self.vel_y = -release_speed * pygame.math.cos(rad) * PLAYER_SWING_SPEED_MULTIPLIER # Negative because y is down

        # Add player input influence
        if move_left:
            self.vel_x -= PLAYER_MOVE_SPEED * 0.5
        if move_right:
            self.vel_x += PLAYER_MOVE_SPEED * 0.5

        self.swing_angular_velocity = 0
        self.swing_angle = 0


    def try_grapple(self, grapple_points):
        if self.is_swinging or self.is_grappling:
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_f]: # Assuming 'F' key for grappling hook
            mouse_x, mouse_y = pygame.mouse.get_pos()
            target_pos = pygame.math.Vector2(mouse_x, mouse_y)
            player_pos = pygame.math.Vector2(self.rect.center)
            
            if player_pos.distance_to(target_pos) <= GRAPPLE_RANGE:
                self.is_grappling = True
                self.grapple_pos = target_pos
                self.grapple_vector = target_pos - player_pos
                self.grapple_endpoint = target_pos # Store the initial target
                self.vel_x = 0 # Stop horizontal movement
                self.vel_y = 0 # Stop vertical movement

    def handle_ground_pound(self):
        if self.on_ground:
            self.vel_y = 15 # Start a downward slam
            self.on_ground = False
        else:
            self.vel_y = 15 # Start a downward slam (if not already on ground)

    def draw_health_bar(self, surface):
        BAR_WIDTH = self.rect.width * 2
        BAR_HEIGHT = 8
        BAR_X = self.rect.centerx - BAR_WIDTH // 2
        BAR_Y = self.rect.top - BAR_HEIGHT - 5

        health_ratio = self.current_health / self.max_health
        fill_width = int(BAR_WIDTH * health_ratio)

        pygame.draw.rect(surface, RED, (BAR_X, BAR_Y, BAR_WIDTH, BAR_HEIGHT))
        pygame.draw.rect(surface, GREEN, (BAR_X, BAR_Y, fill_width, BAR_HEIGHT))

    def draw_stamina_bar(self, surface):
        BAR_WIDTH = self.rect.width * 2
        BAR_HEIGHT = 8
        BAR_X = self.rect.centerx - BAR_WIDTH // 2
        BAR_Y = self.rect.top - BAR_HEIGHT * 2 - 10

        stamina_ratio = self.current_stamina / self.max_stamina
        fill_width = int(BAR_WIDTH * stamina_ratio)

        pygame.draw.rect(surface, (100, 100, 200), (BAR_X, BAR_Y, BAR_WIDTH, BAR_HEIGHT)) # Stamina bar background
        pygame.draw.rect(surface, (50, 50, 255), (BAR_X, BAR_Y, fill_width, BAR_HEIGHT)) # Stamina bar fill


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, platform_type="solid"):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(GREEN) # Default to green
        self.rect = self.image.get_rect(topleft=(x, y))
        self.platform_type = platform_type

        # Specific properties for different types
        if platform_type == "rock_ledge":
            self.image = pygame.transform.scale(rock_ledge_img, (width, height))
        elif platform_type == "dense_foliage":
            self.image = pygame.transform.scale(dense_foliage_img, (width, height))
        elif platform_type == "crumbling_branch":
            self.image = pygame.transform.scale(crumbling_branch_img, (width, height))
            self.health = 3 # How many times it can be landed on before breaking
            self.original_image = self.image.copy() # For resetting
        elif platform_type == "moving_platform":
            self.target_x = x + width # Default target
            self.target_y = y
            self.speed = 50
            self.moving = False # Starts stationary
            self.image = pygame.transform.scale(moving_platform_img, (width, height))
            self.start_pos = pygame.math.Vector2(x, y)
            self.end_pos = pygame.math.Vector2(self.target_x, self.target_y)
            self.path_vector = self.end_pos - self.start_pos
            self.path_length = self.path_vector.length()
            self.current_progress = 0
            self.direction = 1


class Vine(pygame.sprite.Sprite):
    def __init__(self, x, y, length):
        super().__init__()
        self.image = pygame.transform.scale(vine_img, (10, length))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.length = length
        self.grab_point = pygame.math.Vector2(self.rect.centerx, self.rect.top)

class Lever(pygame.sprite.Sprite):
    def __init__(self, x, y, description=""):
        super().__init__()
        self.image = lever_img_off
        self.rect = self.image.get_rect(topleft=(x, y))
        self.is_on = False
        self.description = description
        self.target_platform = None # Will be set later

    def activate(self):
        if not self.is_on:
            self.is_on = True
            self.image = lever_img_on
            print(f"Lever activated: {self.description}")
            # Trigger associated action
            if self.target_platform and isinstance(self.target_platform, Platform) and self.target_platform.platform_type == "moving_platform":
                self.target_platform.start_moving()

    def deactivate(self):
        self.is_on = False
        self.image = lever_img_off

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, powerup_type):
        super().__init__()
        self.powerup_type = powerup_type
        if powerup_type == "banana_bunch":
            self.image = pygame.transform.scale(banana_bunch_img, (30, 30))
            self.value = 20 # Amount of stamina restored
        elif powerup_type == "grappling_hook_upgrade":
            self.image = pygame.transform.scale(grappling_hook_upgrade_img, (30, 30))
            self.value = True # Enables upgrade
        else: # Default to banana
            self.image = pygame.transform.scale(banana_bunch_img, (30, 30))
            self.value = 20
        self.rect = self.image.get_rect(center=(x, y))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type, patrol_path=None):
        super().__init__()
        self.enemy_type = enemy_type
        self.patrol_path = patrol_path if patrol_path else []
        self.current_path_index = 0
        self.patrol_speed = 0

        self.max_health = 50
        self.current_health = self.max_health

        self.facing_right = True

        if enemy_type == "tarantula":
            self.image = tarantula_img
            self.rect = self.image.get_rect(center=(x, y))
            self.patrol_speed = SNARK_SERPENT_SPEED
            self.attack_damage = 5
            self.aggro_radius = 100
        elif enemy_type == "parrot_sniper":
            self.image = parrot_sniper_img
            self.rect = self.image.get_rect(center=(x, y))
            self.fire_rate = PARROT_SNIPER_FIRE_RATE # Shots per second
            self.last_shot_time = 0
            self.projectile_speed = PARROT_SNIPER_PROJECTILE_SPEED
            self.aggro_radius = 200
        else: # Default
            self.image = tarantula_img
            self.rect = self.image.get_rect(center=(x, y))
            self.patrol_speed = SNARK_SERPENT_SPEED
            self.attack_damage = 5
            self.aggro_radius = 100
        
        self.initial_pos = pygame.math.Vector2(x, y)

    def update(self, player, platforms):
        if self.current_health <= 0:
            self.kill()
            return

        # Patrol behavior
        if self.patrol_path and len(self.patrol_path) > 0:
            target_pos = pygame.math.Vector2(self.patrol_path[self.current_path_index])
            
            # Move towards target
            if self.rect.center != target_pos:
                direction = target_pos - pygame.math.Vector2(self.rect.center)
                distance = direction.length()
                
                if distance < self.patrol_speed:
                    self.rect.center = target_pos
                else:
                    move_direction = direction.normalize()
                    self.rect.centerx += move_direction.x * self.patrol_speed
                    self.rect.centery += move_direction.y * self.patrol_speed

                    # Update facing direction
                    if move_direction.x > 0 and not self.facing_right:
                        self.flip()
                    elif move_direction.x < 0 and self.facing_right:
                        self.flip()
            else:
                # Reached path point, move to the next
                self.current_path_index = (self.current_path_index + 1) % len(self.patrol_path)

        # Aggro and special abilities
        if self.enemy_type == "tarantula":
            player_dist = pygame.math.Vector2(self.rect.center).distance_to(pygame.math.Vector2(player.rect.center))
            if player_dist < self.aggro_radius:
                # Basic lunge attack
                if player_dist < 50:
                    player.take_damage(self.attack_damage)
                    # Push back slightly
                    if player.rect.centerx < self.rect.centerx:
                        player.rect.x -= 10
                    else:
                        player.rect.x += 10

        elif self.enemy_type == "parrot_sniper":
            player_dist = pygame.math.Vector2(self.rect.center).distance_to(pygame.math.Vector2(player.rect.center))
            if player_dist < self.aggro_radius:
                # Fire projectile
                now = pygame.time.get_ticks()
                if now - self.last_shot_time > 1000 / self.fire_rate:
                    self.shoot(player)
                    self.last_shot_time = now
            
            # Update facing direction based on player position if patrolling
            if not self.patrol_path:
                if player.rect.centerx < self.rect.centerx and self.facing_right:
                    self.flip()
                elif player.rect.centerx > self.rect.centerx and not self.facing_right:
                    self.flip()

    def flip(self):
        self.image = pygame.transform.flip(self.image, True, False)
        self.facing_right = not self.facing_right

    def shoot(self, player):
        global all_sprites, projectiles
        
        target_direction = pygame.math.Vector2(player.rect.center) - pygame.math.Vector2(self.rect.center)
        if target_direction.length() == 0: return # Avoid division by zero

        projectile_speed_vec = target_direction.normalize() * self.projectile_speed
        
        projectile = Projectile(self.rect.centerx, self.rect.centery, projectile_speed_vec, "parrot_shot")
        all_sprites.add(projectile)
        projectiles.add(projectile)

    def take_damage(self, amount):
        self.current_health -= amount
        if self.current_health <= 0:
            self.die()

    def die(self):
        print(f"{self.enemy_type} died!")
        self.kill() # Remove from all sprite groups

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, velocity, proj_type):
        super().__init__()
        self.proj_type = proj_type
        self.velocity = pygame.math.Vector2(velocity)
        self.speed = self.velocity.length()

        if proj_type == "parrot_shot":
            self.image = pygame.transform.scale(parrot_sniper_projectile_img, (10, 10))
            self.damage = 10
        else: # Default
            self.image = pygame.transform.scale(parrot_sniper_projectile_img, (10, 10))
            self.damage = 10

        self.rect = self.image.get_rect(center=(x, y))
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 5000 # milliseconds

    def update(self, platforms, player):
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()
            return

        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        # Collision with platforms
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                self.kill()
                return
        
        # Collision with player
        if pygame.sprite.collide_rect(self, player):
            if player.current_health > 0: # Only damage if player is alive
                player.take_damage(self.damage)
                self.kill()

# --- Level Data ---
level_data = {
    "level_number": 1,
    "name": "The Whispering Canopy",
    "size": {"width": 1200, "height": 800},
    "spawn_points": [{"x": 100, "y": 150, "type": "player"}],
    "obstacles": [
        {"x": 250, "y": 300, "width": 100, "height": 50, "type": "rock_ledge"},
        {"x": 500, "y": 450, "width": 75, "height": 75, "type": "dense_foliage"},
        {"x": 800, "y": 250, "width": 150, "height": 30, "type": "crumbling_branch"}
    ],
    "powerups": [
        {"x": 350, "y": 200, "type": "banana_bunch"},
        {"x": 700, "y": 350, "type": "grappling_hook_upgrade"}
    ],
    "enemies": [
        {"x": 400, "y": 380, "type": "tarantula", "patrol_path": [{"x": 400, "y": 380}, {"x": 480, "y": 380}]},
        {"x": 650, "y": 300, "type": "parrot_sniper", "patrol_path": [{"x": 650, "y": 300}, {"x": 650, "y": 320}]},
        {"x": 900, "y": 400, "type": "tarantula", "patrol_path": [{"x": 900, "y": 400}, {"x": 980, "y": 400}]}
    ],
    "environmental_elements": [
        {"x": 150, "y": 200, "type": "vine", "length": 150},
        {"x": 300, "y": 350, "type": "vine", "length": 100},
        {"x": 550, "y": 200, "type": "vine", "length": 120},
        {"x": 750, "y": 400, "type": "vine", "length": 180},
        {"x": 950, "y": 300, "type": "vine", "length": 130},
        {"x": 350, "y": 100, "type": "lever", "description": "Activates a nearby platform."},
        {"x": 400, "y": 120, "type": "moving_platform", "target_x": 500, "target_y": 120, "speed": 50}
    ],
    "objectives": [
        {"type": "collect", "target": "banana", "count": 10},
        {"type": "defeat", "target": "tarantula", "count": 2},
        {"type": "activate", "target": "lever", "description": "Pull the lever to reveal a path."}
    ],
    "difficulty": "easy",
    "time_limit": 180
}

# --- Sprite Groups ---
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
vines = pygame.sprite.Group()
levers = pygame.sprite.Group()
powerups = pygame.sprite.Group()
enemies = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
grapple_points = pygame.sprite.Group() # For designated grapple spots


# --- Level Loading Function ---
def load_level(level_data):
    global player, all_sprites, platforms, vines, levers, powerups, enemies, projectiles, grapple_points
    
    # Clear existing groups
    all_sprites.clear()
    platforms.clear()
    vines.clear()
    levers.clear()
    powerups.clear()
    enemies.clear()
    projectiles.clear()
    grapple_points.clear()

    # Set screen dimensions based on level
    global SCREEN_WIDTH, SCREEN_HEIGHT
    SCREEN_WIDTH = level_data["size"]["width"]
    SCREEN_HEIGHT = level_data["size"]["height"]
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Spawn player
    player_spawn = next((spawn for spawn in level_data["spawn_points"] if spawn["type"] == "player"), None)
    if player_spawn:
        player = Player(player_spawn["x"], player_spawn["y"])
        all_sprites.add(player)
    else:
        # Fallback player spawn if not defined
        player = Player(100, 100)
        all_sprites.add(player)

    # Add environmental elements
    for elem in level_data.get("environmental_elements", []):
        if elem["type"] == "vine":
            vine = Vine(elem["x"], elem["y"], elem["length"])
            vines.add(vine)
            all_sprites.add(vine)
        elif elem["type"] == "lever":
            lever = Lever(elem["x"], elem["y"], elem["description"])
            levers.add(lever)
            all_sprites.add(lever)
        elif elem["type"] == "moving_platform":
            platform = Platform(elem["x"], elem["y"], elem["width"], elem["height"], platform_type="moving_platform")
            platform.target_x = elem.get("target_x", platform.rect.x)
            platform.target_y = elem.get("target_y", platform.rect.y)
            platform.speed = elem.get("speed", 50)
            platform.start_pos = pygame.math.Vector2(elem["x"], elem["y"])
            platform.end_pos = pygame.math.Vector2(platform.target_x, platform.target_y)
            platform.path_vector = platform.end_pos - platform.start_pos
            platform.path_length = platform.path_vector.length()
            platforms.add(platform)
            all_sprites.add(platform)
            # Link lever to this platform if applicable
            for lever_elem in level_data.get("environmental_elements", []):
                if lever_elem["type"] == "lever" and lever_elem["description"] == platform.platform_type and lever_elem["description"] == elem.get("lever_description"): # Example linking
                    associated_lever = next((l for l in levers if l.rect.x == lever_elem["x"] and l.rect.y == lever_elem["y"]), None)
                    if associated_lever:
                        associated_lever.target_platform = platform

    # Add platforms and obstacles
    for obs in level_data.get("obstacles", []):
        platform = Platform(obs["x"], obs["y"], obs["width"], obs["height"], platform_type=obs["type"])
        platforms.add(platform)
        all_sprites.add(platform)

    # Add powerups
    for pup in level_data.get("powerups", []):
        powerup = PowerUp(pup["x"], pup["y"], pup["type"])
        powerups.add(powerup)
        all_sprites.add(powerup)

    # Add enemies
    for enemy_data in level_data.get("enemies", []):
        patrol_path = enemy_data.get("patrol_path", [])
        # Convert patrol path dictionaries to Vector2 objects if necessary
        if patrol_path:
            path_vectors = [pygame.math.Vector2(p) for p in patrol_path]
        else:
            path_vectors = []
            
        enemy = Enemy(enemy_data["x"], enemy_data["y"], enemy_data["type"], patrol_path=path_vectors)
        enemies.add(enemy)
        all_sprites.add(enemy)

    # Add designated grapple points (if any)
    # Example: grapple_points_data = [{"x": 600, "y": 100}]
    # for gp_data in grapple_points_data:
    #     gp = pygame.sprite.Sprite()
    #     gp.image = pygame.Surface((10, 10))
    #     gp.image.fill(BLUE)
    #     gp.rect = gp.image.get_rect(center=(gp_data["x"], gp_data["y"]))
    #     grapple_points.add(gp)
    #     all_sprites.add(gp)

    # Set level timer and objectives
    global level_timer
    level_timer = level_data.get("time_limit", 180)
    player.map_pieces_collected = 0
    player.total_map_pieces = 5 # This should be dynamic based on level progression


# --- Game State Functions ---

def run_menu(events):
    global current_state
    
    screen.fill(BLACK)
    title_text = large_font.render("Chrono-Chimp's Grand Voyage", True, WHITE)
    start_text = font.render("Press SPACE to Begin", True, WHITE)
    
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 3))
    screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2))

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                current_state = GameState.PLAYING
                load_level(level_data) # Load the first level

def run_playing(events):
    global current_state, score, level_timer

    # --- Update ---
    all_sprites.update(platforms, vines, levers, grapple_points) # Pass relevant groups

    # Player-specific updates
    if player.is_alive:
        player.try_grab_vine(vines)
        player.try_grapple(grapple_points)
        
        # Check for collisions with enemies
        hit_enemies = pygame.sprite.spritecollide(player, enemies, False)
        for enemy in hit_enemies:
            if enemy.enemy_type == "tarantula": # Example damage type
                player.take_damage(enemy.attack_damage)
            elif enemy.enemy_type == "parrot_sniper":
                player.take_damage(enemy.attack_damage) # Assume parrot sniper also has direct attack

        # Check for collisions with projectiles
        hit_projectiles = pygame.sprite.spritecollide(player, projectiles, False)
        for proj in hit_projectiles:
            player.take_damage(proj.damage)
            proj.kill() # Projectile is used up on hitting player

        # Check for collisions with powerups
        collected_powerups = pygame.sprite.spritecollide(player, powerups, True)
        for pup in collected_powerups:
            if pup.powerup_type == "banana_bunch":
                player.restore_stamina(pup.value)
                score += 10 # Score for collecting bananas
            elif pup.powerup_type == "grappling_hook_upgrade":
                player.grappling_hook_upgrade = pup.value
                score += 50 # Score for upgrade

        # Check for collisions with levers
        hit_levers = pygame.sprite.spritecollide(player, levers, False)
        for lever in hit_levers:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_e]: # Use 'E' to interact
                lever.activate()
                if lever.description == "Pull the lever to reveal a path.":
                    score += 20 # Score for objective completion

        # Check for collecting map pieces (assuming map pieces are represented by special items or objectives)
        # For now, let's say collecting 5 bananas completes a map piece
        if player.current_stamina >= player.max_stamina and player.map_pieces_collected < player.total_map_pieces:
             player.map_pieces_collected += 1
             player.current_stamina = 0 # Reset stamina to signify collection
             score += 100 # Score for collecting map piece
             print(f"Map piece collected! ({player.map_pieces_collected}/{player.total_map_pieces})")


        # Check for ground pound activation
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and player.on_ground:
            player.handle_ground_pound()
            # Check if ground pound hits anything below
            temp_rect = player.rect.copy()
            temp_rect.y += 20 # Simulate pound movement
            for obstacle in platforms:
                if temp_rect.colliderect(obstacle.rect) and obstacle.platform_type == "crumbling_branch":
                    obstacle.health -= 1
                    if obstacle.health <= 0:
                        obstacle.kill()
                        score += 15 # Score for breaking obstacle
                        break # Only break one obstacle

    # Timer update
    if level_timer > 0:
        level_timer -= 1 / FPS
    if level_timer <= 0:
        current_state = GameState.GAME_OVER
        print("Time's up!")

    # Check win condition
    if player.map_pieces_collected >= player.total_map_pieces:
        # Potentially trigger next level load or win screen
        print("All map pieces collected! You win this level!")
        # For now, transition to game over state as a placeholder for level completion
        current_state = GameState.GAME_OVER

    # --- Drawing ---
    screen.fill((100, 149, 237)) # Cornflower blue background for jungle

    # Draw platforms and obstacles
    for platform in platforms:
        screen.blit(platform.image, platform.rect)
        
    # Draw vines
    for vine in vines:
        # Draw the vine segment by segment for better stretching effect
        segment_height = 20
        for y in range(vine.rect.top, vine.rect.bottom, segment_height):
            segment = pygame.Surface((vine.rect.width, min(segment_height, vine.rect.bottom - y)))
            segment.fill(BROWN) # Vine color
            screen.blit(segment, (vine.rect.left, y))

    # Draw levers
    for lever in levers:
        screen.blit(lever.image, lever.rect)

    # Draw powerups
    for pup in powerups:
        screen.blit(pup.image, pup.rect)

    # Draw enemies
    for enemy in enemies:
        screen.blit(enemy.image, enemy.rect)
        # Draw enemy health bar (optional)
        enemy_bar_width = enemy.rect.width * 2
        enemy_bar_height = 5
        enemy_bar_x = enemy.rect.centerx - enemy_bar_width // 2
        enemy_bar_y = enemy.rect.top - enemy_bar_height - 3
        pygame.draw.rect(screen, RED, (enemy_bar_x, enemy_bar_y, enemy_bar_width, enemy_bar_height))
        health_ratio = enemy.current_health / enemy.max_health
        pygame.draw.rect(screen, GREEN, (enemy_bar_x, enemy_bar_y, int(enemy_bar_width * health_ratio), enemy_bar_height))

    # Draw projectiles
    for proj in projectiles:
        screen.blit(proj.image, proj.rect)

    # Draw player
    if player.is_alive:
        screen.blit(player.image, player.rect)
        player.draw_health_bar(screen)
        player.draw_stamina_bar(screen)

        # Draw grappling hook line
        if player.is_grappling and player.grapple_pos:
            pygame.draw.line(screen, (150, 150, 150), player.rect.center, player.grapple_pos, 3)

    # Draw UI elements
    timer_text = font.render(f"Time: {int(level_timer)}s", True, WHITE)
    screen.blit(timer_text, (10, 10))
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 40))
    map_pieces_text = font.render(f"Map Pieces: {player.map_pieces_collected}/{player.total_map_pieces}", True, WHITE)
    screen.blit(map_pieces_text, (10, 70))
    
    # Display instructions during gameplay
    instruction_text = font.render("WASD/Arrows: Move | SPACE: Jump/Swing Release | F: Grapple | E: Interact | S/Down: Ground Pound", True, WHITE)
    screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, 10))


def run_game_over(events):
    global current_state, score
    
    screen.fill(BLACK)
    
    if player.current_health <= 0:
        message = "GAME OVER"
        color = RED
    elif player.map_pieces_collected >= player.total_map_pieces:
        message = "VICTORY!"
        color = GREEN
    else:
        message = "GAME OVER - Time Up"
        color = RED
        
    game_over_text = large_font.render(message, True, color)
    final_score_text = font.render(f"Final Score: {score}", True, WHITE)
    restart_text = font.render("Press R to Restart", True, WHITE)
    
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 3))
    screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                current_state = GameState.MENU
                # Reset score and other global vars here if needed for restart
                score = 0


# --- Main Game Loop ---
running = True
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
            
        # Handle input specific to player actions that are not continuous
        if current_state == GameState.PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.is_swinging: # Space to release swing
                    player.release_swing(
                        (pygame.key.get_pressed()[pygame.K_LEFT] or pygame.key.get_pressed()[pygame.K_a]),
                        (pygame.key.get_pressed()[pygame.K_RIGHT] or pygame.key.get_pressed()[pygame.K_d])
                    )
                if event.key == pygame.K_f and not player.is_swinging: # F to grapple
                     player.try_grapple(grapple_points)
                if event.key == pygame.K_UP or event.key == pygame.K_w: # Jump
                    if player.on_ground and not player.is_swinging and not player.is_grappling:
                        player.vel_y = Player.JUMP_STRENGTH
                        player.on_ground = False
                if event.key == pygame.K_s or event.key == pygame.K_DOWN: # Ground Pound initiation
                    if not player.on_ground and not player.is_swinging and not player.is_grappling:
                        player.handle_ground_pound()


    # State Logic
    if current_state == GameState.MENU:
        run_menu(events)
    elif current_state == GameState.PLAYING:
        run_playing(events)
    elif current_state == GameState.GAME_OVER:
        run_game_over(events)
    
    # Update display
    pygame.display.flip()
    
    # Cap frame rate
    clock.tick(FPS)

# --- Cleanup ---
pygame.quit()
sys.exit()
