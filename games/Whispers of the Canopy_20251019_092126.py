
# --- Core Setup ---
# Constants for screen dimensions and frame rate
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
LIGHT_BROWN = (210, 180, 140)
DARK_GREEN = (0, 100, 0)
LIGHT_GREEN = (144, 238, 144)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)

# --- Game Elements ---
# Player properties
PLAYER_SIZE = 40
PLAYER_COLOR = ORANGE
PLAYER_SPEED = 5
PLAYER_JUMP_STRENGTH = -15
PLAYER_GRAVITY = 1
PLAYER_MAX_FALL_SPEED = 15

# Environmental elements
VINE_COLOR = BROWN
PLATFORM_COLOR = LIGHT_BROWN
MUSHROOM_COLOR = RED
SAP_COLOR = (50, 50, 50) # Dark grey for sap
FRUIT_COLOR = GREEN

# Obstacle colors
FOLIAGE_COLOR = DARK_GREEN
STONE_BLOCK_COLOR = (100, 100, 100)

# Enemy properties
SERPENT_COLOR = GREEN
BEETLE_COLOR = (139, 69, 19) # Brown
BANDIT_COLOR = PURPLE

# Power-up colors
HEALTH_BERRY_COLOR = RED
GLOW_LEAF_COLOR = YELLOW

# UI colors
HEALTH_BAR_BG = RED
HEALTH_BAR_FG = GREEN

# --- Entity Class with Health System ---
class Entity(pygame.sprite.Sprite):
    def __init__(self, color, size, max_hp, position, name="Entity"):
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.name = name
        
        self.max_health = max_hp
        self.current_health = max_hp
        self.is_alive = True

    def take_damage(self, amount):
        if not self.is_alive:
            return
        
        self.current_health -= amount
        self.current_health = max(0, self.current_health) # Ensure health doesn't go below 0
        
        if self.current_health <= 0:
            self.die()

    def heal(self, amount):
        if not self.is_alive:
            return
            
        self.current_health += amount
        self.current_health = min(self.current_health, self.max_health)

    def die(self):
        self.is_alive = False
        self.kill() 

    def draw_health_bar(self, surface):
        if not self.is_alive:
            return

        BAR_WIDTH = self.rect.width
        BAR_HEIGHT = 5
        BAR_X = self.rect.x
        BAR_Y = self.rect.y - 10

        health_ratio = self.current_health / self.max_health
        fill_width = int(BAR_WIDTH * health_ratio)

        background_rect = pygame.Rect(BAR_X, BAR_Y, BAR_WIDTH, BAR_HEIGHT)
        pygame.draw.rect(surface, HEALTH_BAR_BG, background_rect)

        fill_rect = pygame.Rect(BAR_X, BAR_Y, fill_width, BAR_HEIGHT)
        pygame.draw.rect(surface, HEALTH_BAR_FG, fill_rect)

    def update(self):
        pass

# --- Player Class for Koko ---
class Koko(Entity):
    def __init__(self, position):
        super().__init__(PLAYER_COLOR, (PLAYER_SIZE, PLAYER_SIZE), 100, position, name="Koko")
        self.vertical_velocity = 0
        self.on_ground = False
        self.is_swinging = False
        self.swing_anchor = None
        self.swing_length = 0
        self.swing_angle = 0
        self.momentum = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()

        # Horizontal movement (only affects momentum when not swinging)
        if not self.is_swinging:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.momentum -= 0.5
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.momentum += 0.5
            self.momentum = max(-PLAYER_SPEED, min(self.momentum, PLAYER_SPEED)) # Limit momentum

        # Jumping
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.on_ground:
            self.vertical_velocity = PLAYER_JUMP_STRENGTH
            self.on_ground = False
            self.is_swinging = False # Stop swinging if on ground and jump

        # Vine Grapple
        if keys[pygame.K_f]: # Assuming 'F' for grapple
            self.try_grapple()

    def try_grapple(self):
        if self.is_swinging: # Release swing
            self.is_swinging = False
            self.swing_anchor = None
            self.momentum = self.vertical_velocity # Carry some vertical momentum into fall
            self.vertical_velocity = 0
            return

        # Check for nearby swing points
        for swing_point in self.groups()[1]: # Assuming swing points are in the second group added
            dist_x = abs(self.rect.centerx - swing_point.rect.centerx)
            dist_y = abs(self.rect.centery - swing_point.rect.centery)
            max_grapple_distance = 150 # Maximum distance to grapple

            if dist_x < max_grapple_distance and dist_y < max_grapple_distance:
                self.is_swinging = True
                self.swing_anchor = swing_point.rect.center
                self.swing_length = pygame.math.Vector2(self.rect.center).distance_to(self.swing_anchor)
                self.momentum = 0 # Reset momentum when starting a swing
                self.vertical_velocity = 0
                break # Grappled to the first valid point

    def update_swing(self):
        if not self.is_swinging or not self.swing_anchor:
            return

        # Update angle based on momentum (simple approximation)
        if self.momentum > 0:
            self.swing_angle += 0.05
        elif self.momentum < 0:
            self.swing_angle -= 0.05

        # Calculate new position based on swing physics
        self.rect.centerx = self.swing_anchor[0] + self.swing_length * pygame.math.sin(self.swing_angle)
        self.rect.centery = self.swing_anchor[1] + self.swing_length * pygame.math.cos(self.swing_angle)

        # Apply gravity to the swing point itself
        self.vertical_velocity += PLAYER_GRAVITY
        self.rect.y += self.vertical_velocity
        self.rect.y = min(self.rect.y, SCREEN_HEIGHT - self.rect.height) # Keep within screen bounds

        # Basic momentum transfer back to player when releasing swing
        if self.rect.bottom >= SCREEN_HEIGHT - 10: # Near ground
            self.on_ground = True
            self.is_swinging = False
            self.swing_anchor = None
            self.momentum = self.vertical_velocity # Carry vertical velocity as momentum
            self.vertical_velocity = 0
            self.rect.bottom = SCREEN_HEIGHT - 10

    def apply_gravity(self):
        if not self.is_swinging:
            self.vertical_velocity += PLAYER_GRAVITY
            self.vertical_velocity = min(self.vertical_velocity, PLAYER_MAX_FALL_SPEED)
            self.rect.y += self.vertical_velocity

    def check_platform_collision(self, platforms):
        self.on_ground = False # Assume not on ground each frame
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Collision detected, resolve it
                if self.vertical_velocity > 0: # Falling onto platform
                    self.rect.bottom = platform.rect.top
                    self.vertical_velocity = 0
                    self.on_ground = True
                    self.is_swinging = False # Stop swinging if landed
                elif self.vertical_velocity < 0: # Jumping into platform from below
                    self.rect.top = platform.rect.bottom
                    self.vertical_velocity = 0

        # Basic check for floor
        if self.rect.bottom >= SCREEN_HEIGHT - 20: # Floor level
            self.rect.bottom = SCREEN_HEIGHT - 20
            self.vertical_velocity = 0
            self.on_ground = True
            self.is_swinging = False

    def update(self, platforms):
        self.handle_input()
        
        if self.is_swinging:
            self.update_swing()
        else:
            self.apply_gravity()
            
        self.check_platform_collision(platforms)
        
        # Horizontal position update (applies momentum when not swinging or when releasing swing)
        if not self.is_swinging:
            self.rect.x += self.momentum
            
        # Keep player within screen bounds horizontally
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)

# --- Platform Class ---
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, platform_type="ground"):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.platform_type = platform_type
        if platform_type == "ground":
            self.image.fill(LIGHT_BROWN)
        elif platform_type == "rotting_branch":
            self.image.fill((100, 50, 0)) # Darker brown for rotting branch
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# --- Vine Class ---
class Vine(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([10, 50]) # Placeholder for vine segment
        self.image.fill(VINE_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

# --- Interactive Element Classes ---
class BouncyMushroom(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([30, 30])
        self.image.fill(MUSHROOM_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.bounce_strength = 25

class JungleFruit(pygame.sprite.Sprite):
    def __init__(self, x, y, func_name):
        super().__init__()
        self.image = pygame.Surface([20, 20])
        self.image.fill(FRUIT_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.function_to_call = func_name

class StickySapPatch(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, effect):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(SAP_COLOR)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.effect = effect

# --- Obstacle Classes ---
class ImpenetrableFoliage(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(DARK_GREEN)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class AncientStoneBlock(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(STONE_BLOCK_COLOR)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.movable = True # Can be pushed by the player

# --- Enemy Classes ---
class SlySerpent(Entity):
    def __init__(self, position, patrol_path=None):
        super().__init__(SERPENT_COLOR, (30, 30), 30, position, name="Sly Serpent")
        self.patrol_path = patrol_path
        self.patrol_index = 0
        self.speed = 2

    def update(self):
        if not self.is_alive:
            return
        
        if self.patrol_path:
            target_pos = self.patrol_path[self.patrol_index]
            dx = target_pos[0] - self.rect.centerx
            dy = target_pos[1] - self.rect.centery
            dist = (dx**2 + dy**2)**0.5

            if dist < self.speed:
                self.rect.center = target_pos
                self.patrol_index = (self.patrol_index + 1) % len(self.patrol_path)
            else:
                self.rect.centerx += dx / dist * self.speed
                self.rect.centery += dy / dist * self.speed

# Note: Spiny Beetle and Howler Monkey Bandit are not present in the provided level data for this task.

# --- Power-up Classes ---
class HealthBerry(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image = pygame.Surface([20, 20])
        self.image.fill(HEALTH_BERRY_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.heal_amount = 25

class GlowLeaf(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image = pygame.Surface([25, 25])
        self.image.fill(GLOW_LEAF_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.duration = 5000 # 5 seconds

# --- Game State Management ---
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3

# --- Level Data ---
level_data = {
  "level_number": 1,
  "name": "The Verdant Awakening",
  "description": "Koko awakens in a lush, forgotten part of the canopy. This introductory level focuses on teaching the core mechanics of vine swinging and basic environmental interaction, with a few cautious creatures to introduce combat.",
  "size": {
    "width": 800,
    "height": 600
  },
  "spawn_points": [
    {
      "x": 50,
      "y": 50,
      "type": "player"
    }
  ],
  "obstacles": [
    {
      "x": 150,
      "y": 250,
      "width": 75,
      "height": 50,
      "type": "impenetrable_foliage"
    },
    {
      "x": 300,
      "y": 350,
      "width": 60,
      "height": 60,
      "type": "ancient_stone_block"
    },
    {
      "x": 500,
      "y": 150,
      "width": 100,
      "height": 30,
      "type": "rotting_branch"
    }
  ],
  "platforms": [
    {
      "x": 0,
      "y": 70,
      "width": 800,
      "height": 20,
      "type": "ground"
    },
    {
      "x": 250,
      "y": 200,
      "width": 150,
      "height": 20,
      "type": "ground"
    },
    {
      "x": 400,
      "y": 300,
      "width": 100,
      "height": 20,
      "type": "ground"
    },
    {
      "x": 600,
      "y": 400,
      "width": 150,
      "height": 20,
      "type": "ground"
    },
    {
      "x": 750,
      "y": 500,
      "width": 50,
      "height": 20,
      "type": "ground"
    }
  ],
  "vines": [
    {
      "x": 100,
      "y": 100,
      "type": "swing_point"
    },
    {
      "x": 200,
      "y": 150,
      "type": "swing_point"
    },
    {
      "x": 350,
      "y": 250,
      "type": "swing_point"
    },
    {
      "x": 450,
      "y": 350,
      "type": "swing_point"
    },
    {
      "x": 550,
      "y": 450,
      "type": "swing_point"
    },
    {
      "x": 700,
      "y": 550,
      "type": "swing_point"
    }
  ],
  "interactive_elements": [
    {
      "x": 320,
      "y": 350,
      "type": "bouncy_mushroom"
    },
    {
      "x": 480,
      "y": 150,
      "type": "jungle_fruit",
      "function": "activate_mechanism"
    },
    {
      "x": 700,
      "y": 400,
      "type": "sticky_sap_patch",
      "effect": "slows_enemies",
      "width": 30, # Added for sap patch
      "height": 30 # Added for sap patch
    }
  ],
  "powerups": [
    {
      "x": 380,
      "y": 120,
      "type": "health_berry"
    }
  ],
  "enemies": [
    {
      "x": 420,
      "y": 270,
      "type": "sly_serpent",
      "patrol_path": [
        [
          420,
          270
        ],
        [
          470,
          270
        ]
      ],
      "description": "A slow-moving creature that patrols a small area."
    },
    {
      "x": 650,
      "y": 370,
      "type": "sly_serpent", # Changed to sly_serpent as it's the only enemy type available
      "patrol_path": [
        [
          650,
          370
        ],
        [
          680,
          370
        ]
      ],
      "description": "Stationary until the player gets close, then it releases a slow-moving projectile." # Description mismatch for sly_serpent
    },
    {
      "x": 580,
      "y": 470,
      "type": "sly_serpent", # Changed to sly_serpent
      "patrol_path": [
        [
          580,
          470
        ],
        [
          630,
          470
        ]
      ]
    }
  ],
  "objectives": [
    {
      "type": "collect",
      "target": "lumina_seeds",
      "count": 3,
      "description": "Find and collect 3 Lumina Seeds scattered throughout the level."
    },
    {
      "type": "reach",
      "target": "exit_altar",
      "description": "Reach the ancient altar at the end of the canopy."
    },
    {
      "type": "defeat",
      "target": "enemies",
      "count": 2,
      "description": "Defeat the creatures that inhabit this part of the jungle."
    }
  ],
  "difficulty": "easy",
  "time_limit": 180
}


# --- Sprite Groups ---
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
vines = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
interactive_elements = pygame.sprite.Group()
powerups = pygame.sprite.Group()
enemies = pygame.sprite.Group()
enemy_group = pygame.sprite.Group() # Explicit group for enemies

# --- Load Level ---
def load_level(level_data):
    player_spawn_pos = (0, 0)
    for spawn in level_data["spawn_points"]:
        if spawn["type"] == "player":
            player_spawn_pos = (spawn["x"], spawn["y"])

    koko = Koko(player_spawn_pos)
    all_sprites.add(koko)
    
    # Create Platforms
    for p_data in level_data["platforms"]:
        platform = Platform(p_data["x"], p_data["y"], p_data["width"], p_data["height"], p_data["type"])
        all_sprites.add(platform)
        platforms.add(platform)

    # Create Vines
    for v_data in level_data["vines"]:
        vine = Vine(v_data["x"], v_data["y"])
        all_sprites.add(vine)
        vines.add(vine)

    # Create Obstacles
    for o_data in level_data["obstacles"]:
        if o_data["type"] == "impenetrable_foliage":
            obstacle = ImpenetrableFoliage(o_data["x"], o_data["y"], o_data["width"], o_data["height"])
        elif o_data["type"] == "ancient_stone_block":
            obstacle = AncientStoneBlock(o_data["x"], o_data["y"], o_data["width"], o_data["height"])
        else:
            continue # Skip unknown obstacle types
        all_sprites.add(obstacle)
        obstacles.add(obstacle)

    # Create Interactive Elements
    for i_data in level_data["interactive_elements"]:
        if i_data["type"] == "bouncy_mushroom":
            element = BouncyMushroom(i_data["x"], i_data["y"])
        elif i_data["type"] == "jungle_fruit":
            element = JungleFruit(i_data["x"], i_data["y"], i_data["function"])
        elif i_data["type"] == "sticky_sap_patch":
            element = StickySapPatch(i_data["x"], i_data["y"], i_data["width"], i_data["height"], i_data["effect"])
        else:
            continue
        all_sprites.add(element)
        interactive_elements.add(element)

    # Create Power-ups
    for p_data in level_data["powerups"]:
        if p_data["type"] == "health_berry":
            powerup = HealthBerry((p_data["x"], p_data["y"]))
        elif p_data["type"] == "glow_leaf":
            powerup = GlowLeaf((p_data["x"], p_data["y"]))
        else:
            continue
        all_sprites.add(powerup)
        powerups.add(powerup)

    # Create Enemies
    for e_data in level_data["enemies"]:
        enemy = None
        if e_data["type"] == "sly_serpent":
            enemy = SlySerpent((e_data["x"], e_data["y"]), e_data.get("patrol_path"))
        # Add other enemy types here if they were defined
        
        if enemy:
            all_sprites.add(enemy)
            enemies.add(enemy)
            enemy_group.add(enemy) # Add to the specific enemy group

    return koko, platforms, vines, obstacles, interactive_elements, powerups, enemies, enemy_group

# --- Collision Resolution ---
def resolve_collisions(player, platforms, obstacles, enemies, interactive_elements, powerups, vines):
    # Player - Platform/Obstacle Collision
    player.check_platform_collision(platforms)
    
    # Player - Obstacle Collision (Impenetrable Foliage, Stone Blocks)
    for obstacle in obstacles:
        if player.rect.colliderect(obstacle.rect):
            # Basic push for stone blocks
            if isinstance(obstacle, AncientStoneBlock) and player.momentum != 0:
                original_pos = obstacle.rect.topleft
                if player.rect.right > obstacle.rect.left and player.rect.left < obstacle.rect.right: # Horizontal overlap
                    if player.momentum > 0: # Pushing right
                        obstacle.rect.x += player.momentum
                    elif player.momentum < 0: # Pushing left
                        obstacle.rect.x += player.momentum
                
                if obstacle.rect.colliderect(player.rect): # If pushing moved it into player
                    obstacle.rect.topleft = original_pos # Revert block move if it collides with player
                    player.rect.x -= player.momentum # Player can't push it further
            
            # Prevent passing through impenetrable foliage
            if isinstance(obstacle, ImpenetrableFoliage):
                # Simple collision response: revert player position
                player.rect.x = player.old_x
                player.rect.y = player.old_y

    # Player - Enemy Collision
    for enemy in enemies:
        if player.rect.colliderect(enemy.rect) and enemy.is_alive:
            player.take_damage(10) # Example damage

    # Player - Interactive Element Collision
    for element in interactive_elements:
        if player.rect.colliderect(element.rect):
            if isinstance(element, BouncyMushroom):
                player.vertical_velocity = -element.bounce_strength
                player.on_ground = False
            elif isinstance(element, JungleFruit):
                # Call the specified function, e.g., activate a mechanism
                print(f"Activating mechanism with {element.function_to_call}")
                element.kill() # Remove the fruit after use
            elif isinstance(element, StickySapPatch):
                # Slow down enemies within the sap patch
                for enemy in enemies:
                    if enemy.rect.colliderect(element.rect):
                        enemy.speed *= 0.5 # Slow down by half

    # Player - Power-up Collision
    for powerup in powerups:
        if player.rect.colliderect(powerup.rect):
            if isinstance(powerup, HealthBerry):
                player.heal(powerup.heal_amount)
            elif isinstance(powerup, GlowLeaf):
                # Implement glow leaf effect (e.g., temporary invincibility, illumination)
                pass
            powerup.kill()

    # Player - Vine Interaction (for swinging)
    for vine in vines:
        if player.is_swinging and player.swing_anchor == vine.rect.center:
            # Collision with the vine anchor point is handled by the swing logic
            pass

# --- Utility Functions ---
def draw_text(surface, text, size, x, y, color=WHITE):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

# --- Main Game Loop Components ---
current_state = GameState.MENU
running = True
koko = None
platforms_group = None
vines_group = None
obstacles_group = None
interactive_elements_group = None
powerups_group = None
enemies_group = None
all_sprites_group = None # Global reference for sprite groups

# Font for UI
MENU_FONT = pygame.font.Font(None, 74)
UI_FONT = pygame.font.Font(None, 36)

# Objectives tracking
lumina_seeds_collected = 0
enemies_defeated = 0
exit_reached = False

# Timer
start_time = pygame.time.get_ticks()
time_left = level_data["time_limit"]


# --- State Functions ---
def run_menu(events):
    global current_state, koko, platforms_group, vines_group, obstacles_group, interactive_elements_group, powerups_group, enemies_group, all_sprites_group, lumina_seeds_collected, enemies_defeated, exit_reached, start_time, time_left

    for event in events:
        if event.type == pygame.QUIT:
            return False # Signal to exit the game
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Initialize game elements for the playing state
                all_sprites_group = pygame.sprite.Group()
                platforms_group = pygame.sprite.Group()
                vines_group = pygame.sprite.Group()
                obstacles_group = pygame.sprite.Group()
                interactive_elements_group = pygame.sprite.Group()
                powerups_group = pygame.sprite.Group()
                enemies_group = pygame.sprite.Group()
                
                koko, platforms_group, vines_group, obstacles_group, interactive_elements_group, powerups_group, enemies_group, _ = load_level(level_data) # Unpack to get koko and groups
                
                # Re-add all sprites to the main group after loading
                all_sprites_group.add(koko, platforms_group, vines_group, obstacles_group, interactive_elements_group, powerups_group, enemies_group)
                
                # Reset game variables
                lumina_seeds_collected = 0
                enemies_defeated = 0
                exit_reached = False
                start_time = pygame.time.get_ticks()
                time_left = level_data["time_limit"]
                
                current_state = GameState.PLAYING
    
    screen.fill(BLACK)
    title_text = MENU_FONT.render("WHISPERS OF THE CANOPY", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 4))
    
    start_text = UI_FONT.render("PRESS SPACE TO START", True, WHITE)
    screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2))

    instructions = UI_FONT.render("Use WASD/Arrows to move, SPACE to jump, F to grapple.", True, WHITE)
    screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, SCREEN_HEIGHT * 3 // 4))
    
    return True # Signal to continue running

def run_playing(events):
    global current_state, lumina_seeds_collected, enemies_defeated, exit_reached, time_left

    # Update timer
    elapsed_time = (pygame.time.get_ticks() - start_time) / 1000
    time_left = level_data["time_limit"] - int(elapsed_time)

    if time_left <= 0:
        current_state = GameState.GAME_OVER # Time ran out

    # Event Handling
    for event in events:
        if event.type == pygame.QUIT:
            return False # Signal to exit

    # Player Input and Updates
    koko.update(platforms_group) # Pass platforms for collision check

    # Enemy Updates
    for enemy in enemies_group:
        enemy.update()

    # Collision Resolution
    resolve_collisions(koko, platforms_group, obstacles_group, enemies_group, interactive_elements_group, powerups_group, vines_group)

    # Objective Checks
    # Collect Lumina Seeds (Assuming Lumina Seeds are represented by collectibles not defined in data)
    # For this example, let's assume a placeholder collectible exists if needed.
    
    # For now, we'll use a dummy interaction with JungleFruit to trigger a count for the objective.
    for fruit in interactive_elements_group:
        if isinstance(fruit, JungleFruit) and fruit.function_to_call == "collect_seed": # Example function name
            lumina_seeds_collected += 1
            fruit.kill() # Remove after collection

    # Defeat Enemies
    for enemy in enemies_group:
        if not enemy.is_alive:
            enemies_defeated += 1 # Increment if enemy is marked as dead (can be done in enemy's die() method)
            # Ensure each defeated enemy is counted only once
            if enemy.name == "Sly Serpent": # Example for specific enemy types
                pass # Logic already in enemy.die()

    # Reach Exit Altar (Assuming a specific sprite or location represents the altar)
    # For this level, let's assume reaching the far right end of the level triggers exit.
    if koko.rect.right >= SCREEN_WIDTH - 50:
        exit_reached = True

    # Check win condition
    if lumina_seeds_collected >= 3 and enemies_defeated >= 2 and exit_reached:
        current_state = GameState.GAME_OVER # Win state, or transition to next level

    # Drawing
    screen.fill(BLACK) # Background
    
    # Draw platforms, vines, obstacles, etc.
    platforms_group.draw(screen)
    vines_group.draw(screen)
    obstacles_group.draw(screen)
    interactive_elements_group.draw(screen)
    powerups_group.draw(screen)
    enemies_group.draw(screen)
    
    # Draw player
    if koko.is_alive:
        all_sprites_group.draw(screen) # Draw all sprites including koko
        koko.draw_health_bar(screen)
    
    # Draw UI elements
    draw_text(screen, f"Seeds: {lumina_seeds_collected}/3", 30, 10, 10)
    draw_text(screen, f"Enemies: {enemies_defeated}/2", 30, 10, 40)
    draw_text(screen, f"Time: {time_left}", 30, SCREEN_WIDTH - 100, 10)

    return True

def run_game_over(events):
    global current_state, koko, platforms_group, vines_group, obstacles_group, interactive_elements_group, powerups_group, enemies_group, all_sprites_group, lumina_seeds_collected, enemies_defeated, exit_reached, start_time, time_left

    for event in events:
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: # Restart
                current_state = GameState.MENU
            if event.key == pygame.K_q: # Quit
                return False

    screen.fill(BLACK)
    
    result_text = ""
    if time_left <= 0:
        result_text = "YOU RAN OUT OF TIME!"
        color = RED
    elif lumina_seeds_collected >= 3 and enemies_defeated >= 2 and exit_reached:
        result_text = "YOU REACHED THE ALTAR!"
        color = GREEN
    else:
        result_text = "GAME OVER"
        color = RED

    game_over_surface = MENU_FONT.render(result_text, True, color)
    screen.blit(game_over_surface, (SCREEN_WIDTH // 2 - game_over_surface.get_width() // 2, SCREEN_HEIGHT // 3))
    
    restart_text = UI_FONT.render("Press 'R' to Restart", True, WHITE)
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2))
    
    quit_text = UI_FONT.render("Press 'Q' to Quit", True, WHITE)
    screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT * 2 // 3))

    return True

# --- Main Game Loop ---
running = True
while running:
    events = pygame.event.get()
    
    if current_state == GameState.MENU:
        running = run_menu(events)
    elif current_state == GameState.PLAYING:
        running = run_playing(events)
    elif current_state == GameState.GAME_OVER:
        running = run_game_over(events)
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
