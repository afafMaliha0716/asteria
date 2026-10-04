
# [LLM_INJECT_A_CORE_SETUP]
# This template section is already complete and provides the basic Pygame setup.
# No specific unique logic is required here beyond what is already present in the template.
# The constants (SCREEN_WIDTH, SCREEN_HEIGHT, FPS, etc.) defined in the template
# are assumed to be available globally for the injected code.


# [LLM_INJECT_D_HEALTH_DAMAGE]
# Integrating and extending the Entity class for Chimp's Climb
# Constants for game-specific colors and other properties
JUNGLE_GREEN = (34, 139, 34)
PLAYER_COLOR = (255, 165, 0) # Orange for Monkey
ENEMY_PARROT_COLOR = (255, 0, 255) # Magenta for Parrot
ENEMY_SPIDER_COLOR = (100, 100, 100) # Grey for Spider
OBSTACLE_COLOR = (200, 0, 0)
POWERUP_COLOR = (255, 255, 0) # Yellow for power-ups
VINE_COLOR = (139, 69, 19) # SaddleBrown

# --- Utility Function: Asset Loading ---
# This would typically use the resource_path from Template G.
# For this generated code, we use dummy surfaces as actual image files are not available.
def load_image(path, size=None):
    # print(f"Loading dummy asset for: {path}") # uncomment for debug
    img_surface = pygame.Surface(size if size else (32, 32), pygame.SRCALPHA)
    
    if "player_monkey" in path:
        img_surface = pygame.Surface(size if size else (40, 60), pygame.SRCALPHA)
        pygame.draw.circle(img_surface, PLAYER_COLOR, (20, 20), 18)
        pygame.draw.rect(img_surface, PLAYER_COLOR, (10, 20, 20, 40), border_radius=5)
        pygame.draw.circle(img_surface, (100, 50, 0), (10, 15), 5) # Eye
        pygame.draw.circle(img_surface, (100, 50, 0), (30, 15), 5) # Eye
    elif "parrot" in path:
        img_surface = pygame.Surface(size if size else (30, 30), pygame.SRCALPHA)
        pygame.draw.circle(img_surface, ENEMY_PARROT_COLOR, (15, 15), 15)
        pygame.draw.polygon(img_surface, (255,255,0), [(15,0),(20,5),(10,5)]) # Beak
    elif "spider" in path:
        img_surface = pygame.Surface(size if size else (30, 30), pygame.SRCALPHA)
        pygame.draw.circle(img_surface, ENEMY_SPIDER_COLOR, (15, 15), 10)
        # Simple legs
        pygame.draw.line(img_surface, ENEMY_SPIDER_COLOR, (15,10), (5,0), 2)
        pygame.draw.line(img_surface, ENEMY_SPIDER_COLOR, (15,10), (25,0), 2)
        pygame.draw.line(img_surface, ENEMY_SPIDER_COLOR, (15,20), (5,30), 2)
        pygame.draw.line(img_surface, ENEMY_SPIDER_COLOR, (15,20), (25,30), 2)
    elif "fruit_health" in path or "fruit" in path:
        img_surface = pygame.Surface(size if size else (20, 20), pygame.SRCALPHA)
        pygame.draw.circle(img_surface, RED, (10,10), 8) # Red fruit
        pygame.draw.ellipse(img_surface, JUNGLE_GREEN, (8, 0, 4, 8)) # Stem
    elif "leaf_speed" in path:
        img_surface = pygame.Surface(size if size else (20, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(img_surface, BLUE, (0, 0, 20, 15)) # Blue leaf
    elif "spiky_plant" in path:
        img_surface = pygame.Surface(size if size else (40, 40), pygame.SRCALPHA)
        pygame.draw.rect(img_surface, JUNGLE_GREEN, (5, 20, 30, 20))
        pygame.draw.polygon(img_surface, RED, [(10, 20), (20, 0), (30, 20)])
    elif "rolling_log" in path:
        img_surface = pygame.Surface(size if size else (30, 30), pygame.SRCALPHA)
        pygame.draw.circle(img_surface, (139, 69, 19), (15, 15), 15) # Brown log
    elif "bat" in path: # From game concept, but not in Level 1 JSON
        img_surface = pygame.Surface(size if size else (30, 30), pygame.SRCALPHA)
        pygame.draw.polygon(img_surface, (150, 150, 150), [(0,10),(15,0),(30,10),(20,30),(10,30)]) # Simple bat shape
    else:
        img_surface.fill((255, 0, 255)) # Default magenta for unknown

    return img_surface


class GameEntity(pygame.sprite.Sprite):
    def __init__(self, color, size, max_hp, position, image_path=None):
        super().__init__()
        self.image = load_image(image_path, size) if image_path else pygame.Surface(size, pygame.SRCALPHA); self.image.fill(color) # Fallback to color if no image path provided/dummy fails
        self.rect = self.image.get_rect(center=position)
        
        self.max_health = max_hp
        self.current_health = max_hp
        self.is_alive = True
        self.last_damage_time = 0
        self.invincibility_duration = 1000 # milliseconds after taking damage

    def take_damage(self, amount):
        current_time = pygame.time.get_ticks()
        if not self.is_alive or (current_time - self.last_damage_time < self.invincibility_duration):
            return
        
        self.current_health -= amount
        # print(f"{self.__class__.__name__} took damage: {amount}. Current HP: {self.current_health}")
        self.last_damage_time = current_time
        
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
        # print(f"{self.__class__.__name__} died!") # uncomment for debug
        self.kill()

    def draw_health_bar(self, surface):
        if not self.is_alive or self.max_health == self.current_health:
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
        pass

# --- Specific Game Classes inheriting from GameEntity ---

# Player class (incorporating C_MOVEMENT_PLATFORMER logic)
class Player(GameEntity):
    def __init__(self, position):
        super().__init__(PLAYER_COLOR, (40, 60), 100, position, image_path="assets/player_monkey.png")
        self.dx = 0
        self.dy = 0
        self.vertical_velocity = 0
        self.on_ground = False
        self.is_clinging = False
        self.climb_surface = None
        self.is_grappling = False
        self.grapple_target = None
        self.grapple_anchor = None
        self.grapple_length = 0
        self.is_dashing = False
        self.dash_timer = 0
        self.dash_duration = 200 # ms
        self.dash_speed_multiplier = 2.5
        self.facing_right = True
        self.jump_buffer_timer = 0 # For jump button press duration

        # Base movement stats
        self.base_speed = 4
        self.base_jump_strength = -12
        self.base_climb_speed = 2
        self.GRAVITY = 0.5
        self.MAX_FALL_SPEED = 10
        self.current_speed = self.base_speed
        self.current_jump_strength = self.base_jump_strength
        self.current_climb_speed = self.base_climb_speed

        # Powerup states
        self.has_sticky_paws = False
        self.sticky_paws_timer = 0
        self.sticky_paws_duration = 5000 # ms

        self.has_speedy_banana = False
        self.speedy_banana_timer = 0
        self.speedy_banana_duration = 5000 # ms
        self.speed_boost_multiplier = 1.5
        self.jump_boost_multiplier = 1.2
        self.dash_cooldown_timer = 0
        self.dash_cooldown_duration = 1000 # ms

    def update_powerups(self):
        self.current_speed = self.base_speed
        self.current_jump_strength = self.base_jump_strength
        self.current_climb_speed = self.base_climb_speed
        self.has_sticky_paws = False

        if self.has_speedy_banana and pygame.time.get_ticks() < self.speedy_banana_timer:
            self.current_speed = int(self.base_speed * self.speed_boost_multiplier)
            self.current_jump_strength = int(self.base_jump_strength * self.jump_boost_multiplier)
        else:
            self.has_speedy_banana = False

        if self.has_sticky_paws and pygame.time.get_ticks() < self.sticky_paws_timer:
            self.has_sticky_paws = True
        else:
            self.has_sticky_paws = False
            if self.is_clinging: # Auto-release cling if sticky paws expire
                self.is_clinging = False


    def activate_speedy_banana(self):
        self.has_speedy_banana = True
        self.speedy_banana_timer = pygame.time.get_ticks() + self.speedy_banana_duration
        # print("Speedy Banana activated!") # uncomment for debug

    def activate_sticky_paws(self):
        self.has_sticky_paws = True
        self.sticky_paws_timer = pygame.time.get_ticks() + self.sticky_paws_duration
        # print("Sticky Paws activated!") # uncomment for debug
        
    def handle_input(self, keys, platforms, wall_surfaces, vines):
        self.dx, self.dy = 0, 0

        # Horizontal movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.dx = -self.current_speed
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.dx = self.current_speed
            self.facing_right = True

        # Jump
        # Allow jump from ground, or from clinging/grappling to gain momentum
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]):
            if self.on_ground:
                self.vertical_velocity = self.current_jump_strength
                self.on_ground = False
                self.jump_buffer_timer = pygame.time.get_ticks() + 150 # Allow for short press for lower jump
            elif self.is_clinging:
                self.vertical_velocity = self.current_jump_strength * 0.8 # Shorter jump from wall
                self.is_clinging = False
                self.dx = (1 if self.facing_right else -1) * self.current_speed * 1.5 # Push off wall
                self.on_ground = False
            elif self.is_grappling:
                self.vertical_velocity = self.current_jump_strength * 1.2 # Boosted jump from swing
                self.is_grappling = False
                self.on_ground = False
        
        if pygame.key.get_pressed()[pygame.K_SPACE] and pygame.time.get_ticks() < self.jump_buffer_timer and self.vertical_velocity < 0:
            self.vertical_velocity += self.GRAVITY * 0.5 # Extend jump if button held (simplified precise jump)
        
        # Wall Clinging/Climbing
        if not self.on_ground and not self.is_grappling and (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or self.has_sticky_paws):
            colliding_walls = pygame.sprite.spritecollide(self, wall_surfaces, False)
            if colliding_walls:
                wall = colliding_walls[0]
                can_cling = False
                if self.has_sticky_paws:
                    can_cling = True
                elif (self.facing_right and self.rect.right >= wall.rect.left and self.rect.right < wall.rect.right) or \
                     (not self.facing_right and self.rect.left <= wall.rect.right and self.rect.left > wall.rect.left):
                    can_cling = True

                if can_cling:
                    self.is_clinging = True
                    self.climb_surface = wall
                    self.vertical_velocity = 0
                    if keys[pygame.K_UP]:
                        self.dy = -self.current_climb_speed
                    if keys[pygame.K_DOWN]:
                        self.dy = self.current_climb_speed
            else:
                self.is_clinging = False
                self.climb_surface = None
        else:
            self.is_clinging = False
            self.climb_surface = None

        # Vine Grapple (Toggle) - only if not already grappling and 'F' is pressed
        if keys[pygame.K_f] and not self.is_grappling and pygame.time.get_ticks() > self.dash_cooldown_timer: # Re-using cooldown for grapple for simplicity
            for vine in vines:
                if self.rect.colliderect(vine.rect.inflate(50, 50)): # Check proximity for grapple
                    self.is_grappling = True
                    self.grapple_target = vine
                    self.grapple_anchor = pygame.math.Vector2(vine.rect.centerx, vine.rect.top)
                    self.grapple_length = self.rect.center.__sub__(self.grapple_anchor).length() # Current distance as rope length
                    self.vertical_velocity = 0
                    self.on_ground = False
                    self.dash_cooldown_timer = pygame.time.get_ticks() + 500 # Short cooldown for grapple toggle
                    break
        elif keys[pygame.K_f] and self.is_grappling and pygame.time.get_ticks() > self.dash_cooldown_timer: # Release grapple
            self.is_grappling = False
            self.grapple_target = None
            self.grapple_anchor = None
            self.grapple_length = 0
            self.vertical_velocity = min(self.vertical_velocity, 0) # Release might cause upward momentum
            self.dash_cooldown_timer = pygame.time.get_ticks() + 500

        # Tail Swing Dash
        if keys[pygame.K_LSHIFT] and not self.is_dashing and pygame.time.get_ticks() > self.dash_cooldown_timer:
            self.is_dashing = True
            self.dash_timer = pygame.time.get_ticks() + self.dash_duration
            self.vertical_velocity = 0
            self.dash_cooldown_timer = pygame.time.get_ticks() + self.dash_cooldown_duration
            self.on_ground = False # Cannot dash while on ground

    def apply_gravity(self):
        if not self.on_ground and not self.is_clinging and not self.is_grappling:
            self.vertical_velocity += self.GRAVITY
            self.vertical_velocity = min(self.vertical_velocity, self.MAX_FALL_SPEED)

    def handle_grappling(self):
        if self.is_grappling and self.grapple_target:
            # Simple pendulum physics: keep player at grapple_length from anchor
            current_pos = pygame.math.Vector2(self.rect.centerx, self.rect.centery)
            
            # Apply 'gravity' swing force (simplified)
            self.vertical_velocity += self.GRAVITY / 2
            
            # Apply current dx, dy (velocity)
            current_pos.x += self.dx
            current_pos.y += self.vertical_velocity

            direction = current_pos - self.grapple_anchor
            if direction.length_squared() > 0: # Avoid division by zero
                # Normalize and scale to grapple length
                direction.normalize_ip()
                direction *= self.grapple_length
                
                # Update position
                self.rect.centerx = self.grapple_anchor.x + direction.x
                self.rect.centery = self.grapple_anchor.y + direction.y

                # Update dx, dy to simulate swing momentum for next frame
                # This is a very simplified way to transfer momentum.
                # A more accurate way would involve calculating tangential velocity.
                self.dx *= 0.99 # Dampen momentum slightly
                self.vertical_velocity *= 0.99
            
            # Allow player to gain momentum by moving left/right while swinging
            if pygame.key.get_pressed()[pygame.K_LEFT]:
                self.dx = max(self.dx - 0.2, -self.current_speed * 1.5)
            if pygame.key.get_pressed()[pygame.K_RIGHT]:
                self.dx = min(self.dx + 0.2, self.current_speed * 1.5)

    def handle_dash(self):
        if self.is_dashing:
            if pygame.time.get_ticks() < self.dash_timer:
                dash_direction = 1 if self.facing_right else -1
                self.dx = dash_direction * self.current_speed * self.dash_speed_multiplier
            else:
                self.is_dashing = False
                self.dx = 0

    def update(self, platforms, wall_surfaces, vines):
        self.update_powerups()
        keys = pygame.key.get_pressed()
        self.handle_input(keys, platforms, wall_surfaces, vines)
        self.apply_gravity()

        if self.is_grappling:
            self.handle_grappling()
            self.is_clinging = False # Cannot cling while grappling
            self.on_ground = False # Not on ground while grappling
            self.is_dashing = False # Cannot dash while grappling

        elif self.is_clinging:
            self.dx = 0 # No horizontal movement while clinging
            self.rect.y += self.dy
            # Keep player aligned with the wall they are clinging to
            # (simplified to just stop movement on Y axis if hitting top/bottom)
            if self.climb_surface:
                self.rect.top = max(self.rect.top, self.climb_surface.rect.top - self.rect.height + 5) 
                self.rect.bottom = min(self.rect.bottom, self.climb_surface.rect.bottom + self.rect.height - 5)
            self.on_ground = False # Not on ground while clinging
            self.is_dashing = False # Cannot dash while clinging

        else: # Normal movement (not grappling, not clinging)
            # Store old position for collision resolution
            self.old_x = self.rect.x
            self.old_y = self.rect.y
            
            if self.is_dashing:
                self.handle_dash()

            # Apply horizontal movement
            self.rect.x += self.dx
            # Check horizontal collision
            for p in platforms:
                if self.rect.colliderect(p.rect):
                    if self.dx > 0: # Moving right
                        self.rect.right = p.rect.left
                    elif self.dx < 0: # Moving left
                        self.rect.left = p.rect.right
                    self.dx = 0 # Stop horizontal movement if collided
            
            # Apply vertical movement
            self.rect.y += self.vertical_velocity
            # Check vertical collision
            self.on_ground = False
            for p in platforms:
                if self.rect.colliderect(p.rect):
                    if self.vertical_velocity > 0: # Falling down
                        self.rect.bottom = p.rect.top
                        self.vertical_velocity = 0
                        self.on_ground = True
                    elif self.vertical_velocity < 0: # Jumping up
                        self.rect.top = p.rect.bottom
                        self.vertical_velocity = 0
            
            # Keep player within screen bounds horizontally
            self.rect.left = max(0, self.rect.left)
            self.rect.right = min(SCREEN_WIDTH, self.rect.right)


# --- Enemy Classes ---
class Parrot(GameEntity):
    def __init__(self, position, patrol_path):
        super().__init__(ENEMY_PARROT_COLOR, (30, 30), 20, position, image_path="assets/enemy_parrot.png")
        self.patrol_path = [pygame.math.Vector2(p[0], p[1]) for p in patrol_path]
        self.path_index = 0
        self.speed = 2
        self.target_pos = self.patrol_path[self.path_index]

    def update(self):
        if not self.is_alive: return

        current_pos = pygame.math.Vector2(self.rect.centerx, self.rect.centery)
        direction = self.target_pos - current_pos
        
        if direction.length() < self.speed:
            self.rect.center = self.target_pos
            self.path_index = (self.path_index + 1) % len(self.patrol_path)
            self.target_pos = self.patrol_path[self.path_index]
        else:
            direction.normalize_ip()
            self.rect.x += direction.x * self.speed
            self.rect.y += direction.y * self.speed

class Spider(GameEntity):
    def __init__(self, position, patrol_path):
        super().__init__(ENEMY_SPIDER_COLOR, (30, 30), 30, position, image_path="assets/enemy_spider.png")
        self.patrol_path = [pygame.math.Vector2(p[0], p[1]) for p in patrol_path]
        self.path_index = 0
        self.speed = 1
        self.target_pos = self.patrol_path[self.path_index]

    def update(self):
        if not self.is_alive: return

        current_pos = pygame.math.Vector2(self.rect.centerx, self.rect.centery)
        direction = self.target_pos - current_pos
        
        if direction.length() < self.speed:
            self.rect.center = self.target_pos
            self.path_index = (self.path_index + 1) % len(self.patrol_path)
            self.target_pos = self.patrol_path[self.path_index]
        else:
            direction.normalize_ip()
            self.rect.x += direction.x * self.speed
            self.rect.y += direction.y * self.speed

class Bat(GameEntity): # Included from game concept, even if not explicitly required for Level 1 objectives
    def __init__(self, position, patrol_path):
        super().__init__((150, 150, 150), (30, 30), 25, position, image_path="assets/enemy_bat.png")
        self.patrol_path = [pygame.math.Vector2(p[0], p[1]) for p in patrol_path]
        self.path_index = 0
        self.speed = 3
        self.target_pos = self.patrol_path[self.path_index]

    def update(self):
        if not self.is_alive: return

        current_pos = pygame.math.Vector2(self.rect.centerx, self.rect.centery)
        direction = self.target_pos - current_pos
        
        if direction.length() < self.speed:
            self.rect.center = self.target_pos
            self.path_index = (self.path_index + 1) % len(self.patrol_path)
            self.target_pos = self.patrol_path[self.path_index]
        else:
            direction.normalize_ip()
            self.rect.x += direction.x * self.speed
            self.rect.y += direction.y * self.speed


# [LLM_INJECT_E_BASIC_COLLISION]
# Collision resolution is integrated directly into the Player and other game objects' update methods.
# This section defines static level elements and collectible items used for collision and interaction.

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=JUNGLE_GREEN):
        super().__init__()
        self.image = pygame.Surface([width, height], pygame.SRCALPHA)
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

class WallSurface(Platform): # Wall surfaces are essentially climbable platforms
    def __init__(self, x, y, width, height, color=(100, 70, 40)): # Bark-like color
        super().__init__(x, y, width, height, color)
        self.is_climbable = True

class Vine(pygame.sprite.Sprite):
    def __init__(self, x, y, length, color=VINE_COLOR):
        super().__init__()
        self.anchor_point = pygame.math.Vector2(x, y) # Top fixed point
        self.length = length
        # Rect for collision detection around the vine (make it a bit wider than drawn line)
        self.image = pygame.Surface([10, length], pygame.SRCALPHA)
        self.image.fill((0,0,0,0)) # Transparent surface for rect detection
        self.rect = self.image.get_rect(midtop=(x, y))

    def draw(self, surface):
        pygame.draw.line(surface, VINE_COLOR, self.anchor_point, (self.anchor_point.x, self.anchor_point.y + self.length), 3)


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, obstacle_type, damage_amount=10):
        super().__init__()
        self.type = obstacle_type
        self.image = load_image(f"assets/obstacle_{obstacle_type}.png", (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.damage_amount = damage_amount

class Powerup(pygame.sprite.Sprite):
    def __init__(self, x, y, powerup_type, size=(20, 20)):
        super().__init__()
        self.type = powerup_type
        self.image = load_image(f"assets/powerup_{powerup_type}.png", size)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.collected = False


# [LLM_INJECT_F_GAME_STATES]
from enum import Enum

# Game States Enum (if not already defined in the template)
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    LEVEL_COMPLETE = 3
    GAME_OVER = 4

# Game variables for managing state and level data
current_state = GameState.MENU
player = None
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
wall_surfaces = pygame.sprite.Group()
vines = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
powerups = pygame.sprite.Group()
enemies = pygame.sprite.Group()

# Game specific counters/timers
score = 0
fruits_collected = 0
parrots_defeated = 0
spiders_defeated = 0
level_timer = 0
level_start_time = 0
level_objectives = {}

# Font for UI (assuming FONT and SMALL_FONT from template F are available)
FONT_UI = pygame.font.Font(None, 30)

# Level 1 Data (parsed from JSON, simplified here for direct access)
LEVEL_DATA = {
    "level_number": 1,
    "name": "The Whispering Canopy",
    "description": "Begin your ascent through the ancient jungle canopy. Master the basics of vine swinging and wall climbing as you navigate gentle gaps and encounter your first jungle inhabitants. Collect some glittering fruits along the way to bolster your health and speed.",
    "size": { "width": 800, "height": 600 },
    "spawn_points": [ { "x": 50, "y": 550, "type": "player" } ],
    "platforms": [
        { "x": 0, "y": 580, "width": 800, "height": 20, "type": "ground" },
        { "x": 150, "y": 450, "width": 150, "height": 20, "type": "platform" },
        { "x": 350, "y": 350, "width": 100, "height": 20, "type": "platform" },
        { "x": 500, "y": 250, "width": 120, "height": 20, "type": "platform" },
        { "x": 650, "y": 150, "width": 100, "height": 20, "type": "platform" }
    ],
    "vines": [
        { "x": 100, "y": 400, "length": 100, "type": "swing" },
        { "x": 250, "y": 300, "length": 80, "type": "swing" },
        { "x": 420, "y": 200, "length": 90, "type": "swing" },
        { "x": 580, "y": 100, "length": 70, "type": "swing" }
    ],
    "wall_surfaces": [
        { "x": 300, "y": 350, "width": 20, "height": 100, "type": "climbable" },
        { "x": 480, "y": 250, "width": 20, "height": 100, "type": "climbable" }
    ],
    "obstacles": [
        { "x": 270, "y": 430, "width": 40, "height": 40, "type": "spiky_plant" },
        { "x": 570, "y": 230, "width": 30, "height": 30, "type": "rolling_log" }
    ],
    "powerups": [
        { "x": 180, "y": 460, "type": "fruit_health" },
        { "x": 380, "y": 360, "type": "leaf_speed" },
        { "x": 520, "y": 260, "type": "fruit_health" }
    ],
    "enemies": [
        { "x": 180, "y": 420, "type": "parrot", "patrol_path": [[180, 420], [220, 420]] },
        { "x": 400, "y": 320, "type": "spider", "patrol_path": [[400, 320], [440, 320]] },
        { "x": 670, "y": 120, "type": "bat", "patrol_path": [[670, 120], [700, 120]] }
    ],
    "objectives": [
        { "type": "collect", "target": "fruit", "count": 5 },
        { "type": "defeat", "target": "parrot", "count": 1 },
        { "type": "defeat", "target": "spider", "count": 1 }
    ],
    "difficulty": "easy",
    "time_limit": 150
}

# Keep track of initial enemy counts for objective checking
initial_enemy_counts = {}
for enemy_data in LEVEL_DATA['enemies']:
    enemy_type = enemy_data['type']
    initial_enemy_counts[enemy_type] = initial_enemy_counts.get(enemy_type, 0) + 1


def reset_game_state():
    global player, score, fruits_collected, parrots_defeated, spiders_defeated, level_timer, level_start_time
    global all_sprites, platforms, wall_surfaces, vines, obstacles, powerups, enemies, level_objectives
    
    all_sprites.empty()
    platforms.empty()
    wall_surfaces.empty()
    vines.empty()
    obstacles.empty()
    powerups.empty()
    enemies.empty() # Enemies will be added back from level data

    score = 0
    fruits_collected = 0
    parrots_defeated = 0
    spiders_defeated = 0
    level_timer = LEVEL_DATA["time_limit"]
    level_start_time = pygame.time.get_ticks()

    # Load level objects
    for spawn in LEVEL_DATA["spawn_points"]:
        if spawn["type"] == "player":
            player = Player(position=(spawn["x"], spawn["y"]))
            all_sprites.add(player)

    for p_data in LEVEL_DATA["platforms"]:
        plat = Platform(p_data["x"], p_data["y"], p_data["width"], p_data["height"])
        platforms.add(plat)
        all_sprites.add(plat) # Add to all_sprites for rendering

    for ws_data in LEVEL_DATA["wall_surfaces"]:
        ws = WallSurface(ws_data["x"], ws_data["y"], ws_data["width"], ws_data["height"])
        wall_surfaces.add(ws)
        all_sprites.add(ws) # Add to all_sprites for rendering

    for v_data in LEVEL_DATA["vines"]:
        vine = Vine(v_data["x"], v_data["y"], v_data["length"])
        vines.add(vine)
        # Vines are drawn separately, no need to add to all_sprites unless they have images

    for o_data in LEVEL_DATA["obstacles"]:
        obstacle = Obstacle(o_data["x"], o_data["y"], o_data["width"], o_data["height"], o_data["type"])
        obstacles.add(obstacle)
        all_sprites.add(obstacle)

    for pu_data in LEVEL_DATA["powerups"]:
        powerup = Powerup(pu_data["x"], pu_data["y"], pu_data["type"])
        powerups.add(powerup)
        all_sprites.add(powerup)

    for e_data in LEVEL_DATA["enemies"]:
        enemy = None
        if e_data["type"] == "parrot":
            enemy = Parrot((e_data["x"], e_data["y"]), e_data["patrol_path"])
        elif e_data["type"] == "spider":
            enemy = Spider((e_data["x"], e_data["y"]), e_data["patrol_path"])
        elif e_data["type"] == "bat":
            enemy = Bat((e_data["x"], e_data["y"]), e_data["patrol_path"])
        if enemy:
            enemies.add(enemy)
            all_sprites.add(enemy)
    
    level_objectives = {obj['target']: {'current': 0, 'required': obj['count'], 'type': obj['type']} for obj in LEVEL_DATA['objectives']}


def run_menu(events):
    global current_state
    
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                reset_game_state()
                current_state = GameState.PLAYING
    
    screen.fill(BLACK)
    title_text = FONT.render("CHIMP'S CLIMB", True, WHITE)
    start_text = SMALL_FONT.render("Press SPACE to Start Level 1", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))


def run_playing(events, dt):
    global current_state, score, fruits_collected, parrots_defeated, spiders_defeated, level_timer, level_start_time
    
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: # Pause/Exit
                current_state = GameState.MENU # Go back to menu for simplicity
                
    # Update Game Logic
    if player and player.is_alive:
        player.update(platforms, wall_surfaces, vines) # dt is implicitly handled by pygame.time.get_ticks() internally

        # Enemy updates
        enemies.update()

        # Player-Enemy collisions
        enemy_hits = pygame.sprite.spritecollide(player, enemies, False)
        for enemy_hit in enemy_hits:
            player.take_damage(10) # Generic damage from enemies

        # Player-Obstacle collisions
        obstacle_hits = pygame.sprite.spritecollide(player, obstacles, False)
        for obstacle_hit in obstacle_hits:
            player.take_damage(obstacle_hit.damage_amount)

        # Player-Powerup collisions
        powerup_hits = pygame.sprite.spritecollide(player, powerups, True) # Remove powerup on collision
        for powerup_hit in powerup_hits:
            if powerup_hit.type == "fruit_health":
                player.heal(20)
                score += 10
                fruits_collected += 1
                if 'fruit' in level_objectives:
                    level_objectives['fruit']['current'] += 1
                # print(f"Collected fruit. Fruits: {fruits_collected}, Score: {score}") # uncomment for debug
            elif powerup_hit.type == "leaf_speed":
                player.activate_speedy_banana() # Mapped to Speedy Banana powerup
                score += 20
                # print(f"Collected leaf. Score: {score}") # uncomment for debug
        
        # Monitor enemy deaths for objectives
        # Recalculate how many of each enemy type are left vs. initial
        current_parrot_count = sum(1 for e in enemies if isinstance(e, Parrot))
        current_spider_count = sum(1 for e in enemies if isinstance(e, Spider))
        
        if 'parrot' in level_objectives:
            level_objectives['parrot']['current'] = initial_enemy_counts.get('parrot', 0) - current_parrot_count
        if 'spider' in level_objectives:
            level_objectives['spider']['current'] = initial_enemy_counts.get('spider', 0) - current_spider_count

        # Level Timer
        time_elapsed = (pygame.time.get_ticks() - level_start_time) / 1000
        level_timer = LEVEL_DATA["time_limit"] - time_elapsed
        if level_timer <= 0:
            current_state = GameState.GAME_OVER
            # print("Time's up!") # uncomment for debug

    else: # Player is not alive
        current_state = GameState.GAME_OVER

    # Check objectives for Level Complete
    all_objectives_met = True
    for target, obj_data in level_objectives.items():
        if obj_data['current'] < obj_data['required']:
            all_objectives_met = False
            break
            
    if all_objectives_met and player and player.is_alive:
        current_state = GameState.LEVEL_COMPLETE


    # Drawing
    screen.fill(JUNGLE_GREEN) # Jungle background
    
    # Draw vines first so player can be on top, but the line is behind (visually)
    for vine in vines:
        vine.draw(screen)

    all_sprites.draw(screen) # Draw all other sprites (platforms, walls, player, enemies, obstacles, powerups)

    # Draw player health bar
    if player and player.is_alive:
        player.draw_health_bar(screen)

    # Draw UI
    score_text = FONT_UI.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    timer_text = FONT_UI.render(f"Time: {max(0, int(level_timer))}", True, WHITE)
    screen.blit(timer_text, (SCREEN_WIDTH - timer_text.get_width() - 10, 10))
    
    # Draw objectives
    y_offset = 40
    for target, obj_data in level_objectives.items():
        obj_type_str = "Collect" if obj_data['type'] == 'collect' else "Defeat"
        obj_text = FONT_UI.render(f"{obj_type_str} {obj_data['required']} {target.capitalize()}s: {obj_data['current']}/{obj_data['required']}", True, WHITE)
        screen.blit(obj_text, (10, y_offset))
        y_offset += 25


def run_level_complete(events):
    global current_state
    
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN: # Press Enter to continue/restart
                current_state = GameState.MENU # For now, back to menu

    screen.fill((50, 150, 50)) # Green background for level complete
    complete_text = FONT.render("LEVEL COMPLETE!", True, WHITE)
    score_display = SMALL_FONT.render(f"Final Score: {score}", True, WHITE)
    continue_text = SMALL_FONT.render("Press ENTER to continue", True, WHITE)
    screen.blit(complete_text, (SCREEN_WIDTH // 2 - complete_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(score_display, (SCREEN_WIDTH // 2 - score_display.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
    screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))


def run_game_over(events):
    global current_state
    
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: # Press R to restart
                current_state = GameState.MENU
    
    screen.fill(BLACK)
    over_text = FONT.render("GAME OVER", True, RED)
    restart_text = SMALL_FONT.render("Press 'R' to return to Menu", True, WHITE)
    screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))


# [LLM_INJECT_G_ASSET_PATH_HANDLER]
# The template already provides the resource_path function.
# No specific game logic needs to be injected here.
# The `load_image` function in D_HEALTH_DAMAGE would typically use `resource_path`.
# For example: `pygame.image.load(resource_path(image_path)).convert_alpha()`


# [LLM_INJECT_C_MOVEMENT_PLATFORMER]
# The Player class with comprehensive platformer movement logic (gravity, jumping,
# vine grappling, wall clinging, dashing) has been fully defined and extended
# within the [LLM_INJECT_D_HEALTH_DAMAGE] section.
# This injection point serves to acknowledge that the Player class defined earlier
# encapsulates all the movement and interaction logic specified for the game.
# The main game loop in [LLM_INJECT_F_GAME_STATES] calls `player.update()`
# which executes all these mechanics.
# No additional code is required here.
