
# --- TEMPLATE: A_CORE_SETUP ---
import pygame
import sys

# --- Core Setup ---
pygame.init()

# --- Constants ---
# Screen dimensions - extracted from Level Design
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Color definitions (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# --- Initialization ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("The Monkey's Goal!")
clock = pygame.time.Clock()

# --- Game Variables ---
# Placeholder for game state or other global variables
# [LLM_INJECT_GAME_VARIABLES]

# --- Main Game Loop ---
running = True
while running:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # [LLM_INJECT_EVENT_HANDLING]
    
    # 2. Update Game Logic (This is where movement, collision, etc., would go)
    # [LLM_INJECT_UPDATE_LOGIC]

    # 3. Drawing
    screen.fill(BLACK) # Clear the screen
    # [LLM_INJECT_DRAWING]
    
    # Update the full display surface to the screen
    pygame.display.flip()

    # 4. Cap the frame rate
    clock.tick(FPS)

# --- Cleanup ---
pygame.quit()
sys.exit()


# --- TEMPLATE: D_HEALTH_DAMAGE ---
import pygame

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

    def take_damage(self, amount):
        if not self.is_alive:
            return
        
        self.current_health -= amount
        # print(f"Damage taken: {amount}. Current HP: {self.current_health}")
        
        if self.current_health <= 0:
            self.current_health = 0
            self.die()

    def heal(self, amount):
        if not self.is_alive:
            return
            
        self.current_health += amount
        self.current_health = min(self.current_health, self.max_health)
        # print(f"Healed: {amount}. Current HP: {self.current_health}")

    def die(self):
        self.is_alive = False
        # print("Entity died!")
        self.kill() # Removes the sprite from all groups

    def draw_health_bar(self, surface):
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
        # Placeholder update logic
        pass

# --- Game Setup ---
# [LLM_INJECT_SPRITE_SETUP_D]

# --- Test Events (Simulating Damage/Heal) ---
def simulate_interaction():
    # Only interact if both are alive
    # [LLM_INJECT_SIMULATION_LOGIC]
    pass

# --- Main Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # [LLM_INJECT_EVENT_HANDLING_D]

    # 1. Update
    simulate_interaction()
    # [LLM_INJECT_SPRITE_UPDATE_D]

    # 2. Drawing
    screen.fill(WHITE)
    # [LLM_INJECT_SPRITE_DRAW_D]
    
    # MANDATORY: Draw health bars AFTER drawing sprites
    # [LLM_INJECT_HEALTH_BAR_DRAW_D]

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()


# --- TEMPLATE: E_BASIC_COLLISION ---
import pygame

# --- Constants & Initialization (Assumed from A) ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
FPS = 60
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# --- Player Class with Collision Memory ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([50, 50])
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (100, SCREEN_HEIGHT // 2)
        self.speed = 5
        self.dx = 0 # Delta X for current frame
        self.dy = 0 # Delta Y for current frame

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.dx, self.dy = 0, 0

        if keys[pygame.K_LEFT]:
            self.dx = -self.speed
        if keys[pygame.K_RIGHT]:
            self.dx = self.speed
        if keys[pygame.K_UP]:
            self.dy = -self.speed
        if keys[pygame.K_DOWN]:
            self.dy = self.speed

    def update(self):
        self.handle_input()
        
        # Store old position before movement
        self.old_x = self.rect.x
        self.old_y = self.rect.y
        
        # Apply movement
        self.rect.x += self.dx
        self.rect.y += self.dy

# --- Wall Class (Solid Object) ---
class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# --- Collision Functions ---
def check_and_resolve_collision(sprite, wall_group):
    """
    Checks for collision and resolves it by reverting the sprite's position.
    This demonstrates the basic logic required by the prompt.
    """
    # Check for collision with any wall
    hit_walls = pygame.sprite.spritecollide(sprite, wall_group, False)
    
    if hit_walls:
        # print("Collision detected! Reverting position.")
        # Revert movement by setting position back to the previous frame's position
        sprite.rect.x = sprite.old_x
        sprite.rect.y = sprite.old_y
        
        # Note: For more complex/accurate collision, you would check X and Y separately
        # and only revert the axis that caused the collision.

# --- Game Setup ---
all_sprites = pygame.sprite.Group()
walls = pygame.sprite.Group()

# [LLM_INJECT_SPRITE_SETUP_E]

# --- Main Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 1. Update
    # [LLM_INJECT_SPRITE_UPDATE_E]
    
    # 2. Collision Check and Resolution
    # [LLM_INJECT_COLLISION_CHECK_E]

    # 3. Drawing
    screen.fill(WHITE)
    all_sprites.draw(screen)
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()


# --- TEMPLATE: F_GAME_STATES ---
import pygame
import sys
from enum import Enum

# --- Constants & Initialization (Assumed from A) ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("The Monkey's Goal!")
clock = pygame.time.Clock()
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0) # Added missing constant definition
BLUE = (0, 0, 255)
FONT = pygame.font.Font(None, 74)
SMALL_FONT = pygame.font.Font(None, 36)

# --- Game States Enum ---
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3

# --- State Management ---
current_state = GameState.MENU

# --- Game Variables ---
# [LLM_INJECT_GAME_VARIABLES_F]

# --- Sprite Setup ---
# [LLM_INJECT_SPRITE_SETUP_F]

# --- Asset Loading ---
# [LLM_INJECT_ASSET_LOADING_F]

# --- State Functions ---

def run_menu(events):
    global current_state
    
    # Input Logic
    for event in events:
        if event.type == pygame.KEYDOWN:
            # Press SPACE to start the game
            if event.key == pygame.K_SPACE:
                current_state = GameState.PLAYING
                # [LLM_INJECT_TRANSITION_TO_PLAYING]
    
    # Drawing
    screen.fill(BLACK)
    title_text = FONT.render("THE MONKEY'S GOAL!", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 3))
    start_text = SMALL_FONT.render("PRESS SPACE TO START", True, GREEN)
    screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2))

def run_playing(events):
    global current_state
    
    # Input Logic
    for event in events:
        if event.type == pygame.QUIT:
            return False # Signal to exit the game loop
        if event.type == pygame.KEYDOWN:
            # [LLM_INJECT_PLAYING_KEY_HANDLING]
            pass
        # [LLM_INJECT_PLAYING_MOUSE_HANDLING]

    # Update Logic
    # [LLM_INJECT_PLAYING_UPDATE_LOGIC]
    
    # Drawing
    screen.fill((100, 150, 255)) # Sky blue background
    # [LLM_INJECT_PLAYING_DRAWING]
    # Draw score, multiplier, etc.
    # [LLM_INJECT_DRAW_HUD]
    return True # Signal to continue the game loop

def run_game_over(events):
    global current_state
    
    # Input Logic
    for event in events:
        if event.type == pygame.KEYDOWN:
            # Press R to restart (go back to menu)
            if event.key == pygame.K_r:
                current_state = GameState.MENU
                # [LLM_INJECT_TRANSITION_TO_MENU_FROM_GAMEOVER]
    
    # Drawing
    screen.fill(BLACK)
    over_text = FONT.render("GAME OVER", True, RED)
    screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 70))
    final_score_text = SMALL_FONT.render(f"FINAL SCORE: {game_data['score']}", True, WHITE)
    screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2))
    restart_text = SMALL_FONT.render("Press 'R' to Restart", True, WHITE)
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    return True # Signal to continue the game loop


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
        running = run_menu(events)
    elif current_state == GameState.PLAYING:
        running = run_playing(events)
    elif current_state == GameState.GAME_OVER:
        running = run_game_over(events)
    
    # 3. Drawing
    pygame.display.flip()
    
    # 4. Cap the frame rate
    clock.tick(FPS)

# --- Cleanup ---
pygame.quit()
sys.exit()


# --- TEMPLATE: G_ASSET_PATH_HANDLER ---
# --- TEMPLATE: G_ASSET_PATH_HANDLER ---

import os
import sys

def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller bundle.
    This function must be called every time a resource file (like an image) is loaded.
    
    CRITICAL NOTE: Assumes all assets are in a subfolder named 'assets' 
    relative to the script's execution directory in both dev and bundled modes.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # We join the base path with the 'assets' subdirectory, then the relative path.
        base_path = sys._MEIPASS 
        return os.path.join(base_path, 'assets', relative_path)
        
    except Exception:
        # Not running as a compiled executable, use the current script directory
        # We join the current directory with the relative path.
        base_path = os.path.abspath(".") 
        return os.path.join(base_path, 'assets', relative_path)
    
# --- END TEMPLATE: G_ASSET_PATH_HANDLER ---

# --- TEMPLATE: B_MOVEMENT_TOPDOWN ---
import pygame

# --- Constants & Initialization (Assumed from A) ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
FPS = 60
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# --- Player Class for Top-Down Movement ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([50, 50])
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed = 5

    def update(self):
        # Get all currently pressed keys
        keys = pygame.key.get_pressed()
        
        # Initialize movement delta
        dx, dy = 0, 0

        # Calculate movement based on keys
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = self.speed

        # Update position
        self.rect.x += dx
        self.rect.y += dy
        
        # Keep player within screen bounds (simple boundary checking)
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)

# --- Game Setup ---
all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

# --- Main Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 1. Update (The player's position is updated here)
    all_sprites.update()

    # 2. Drawing
    screen.fill(WHITE)
    all_sprites.draw(screen)
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()


# --- LLM_INJECT_GAME_VARIABLES ---
game_data = {
    "level": 1,
    "score": 0,
    "multiplier": 1,
    "high_score": 0, # Placeholder for future expansion
    "current_state": "MENU", # Using string for simplicity with FSM template
    "game_over": False,
    "target_transition_time": 0.5, # Seconds
    "transition_timer": 0.0,
    "current_sprite_state": "monkey", # "monkey" or "footballer"
    "time_limit": 90, # Seconds
    "level_timer": 0.0,
    "bananas_collected": 0,
    "target_bananas": 8,
    "target_score_level": 5000,
    "focus_active": False,
    "focus_timer": 0.0,
    "focus_duration": 5.0,
    "insight_active": False,
    "insight_timer": 0.0,
    "insight_duration": 3.0,
    "quick_reflex_available": True,
    "quick_reflex_timer": 0.0,
    "quick_reflex_duration": 1.0,
    "powerup_banana_boost_active": False,
    "powerup_banana_boost_timer": 0.0,
    "powerup_banana_boost_duration": 10.0,
    "powerup_goal_zone_active": False,
    "powerup_goal_zone_timer": 0.0,
    "powerup_goal_zone_duration": 7.0,
    "enemy_spawn_timer": 0.0,
    "enemy_spawn_interval": 5.0,
    "powerup_spawn_timer": 0.0,
    "powerup_spawn_interval": 15.0,
    "lives": 3, # Placeholder for future expansion
    "is_paused": False,
}

# --- SPRITE DEFINITIONS ---

class Monkey(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill((255, 165, 0)) # Orange for monkey
        self.rect = self.image.get_rect(center=pos)
        self.frames = [] # Placeholder for animation frames
        self.current_frame = 0
        self.animation_speed = 0.1 # seconds per frame
        self.last_update = pygame.time.get_ticks() / 1000.0

    def update(self):
        # [LLM_INJECT_MONKEY_UPDATE]
        pass

class Footballer(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill((0, 128, 0)) # Green for footballer
        self.rect = self.image.get_rect(center=pos)
        self.frames = [] # Placeholder for animation frames
        self.current_frame = 0
        self.animation_speed = 0.1 # seconds per frame
        self.last_update = pygame.time.get_ticks() / 1000.0

    def update(self):
        # [LLM_INJECT_FOOTBALLER_UPDATE]
        pass

class RedButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((80, 80))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=pos)
        self.is_active = False # True when footballer is shown

    def update(self):
        self.image.fill(RED) # Default color
        if self.is_active:
            # Slightly highlight when active (e.g., brighter red or outline)
            # For simplicity, we'll keep it red, but its 'active' state is key.
            pass

class Banana(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 255, 0)) # Yellow
        self.rect = self.image.get_rect(center=pos)

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, type):
        super().__init__()
        self.image = pygame.Surface([width, height])
        if type == "vines":
            self.image.fill((139, 69, 19)) # Brown
        elif type == "boulder":
            self.image.fill((105, 105, 105)) # Grey
        elif type == "log":
            self.image.fill((139, 69, 19)) # Brown
        else:
            self.image.fill((128, 128, 128)) # Default grey
        self.rect = self.image.get_rect(topleft=(x, y))
        self.type = type

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.type = type
        self.image = pygame.Surface((30, 30))
        if type == "multiplier_boost":
            self.image.fill(GREEN)
        elif type == "time_extension":
            self.image.fill(BLUE)
        elif type == "focus":
            self.image.fill((255, 0, 255)) # Purple
        elif type == "insight":
            self.image.fill((128, 0, 128)) # Dark Purple
        elif type == "quick_reflex":
            self.image.fill((255, 255, 0)) # Yellow
        else:
            self.image.fill((255, 255, 255)) # White
        self.rect = self.image.get_rect(center=(x, y))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, type, patrol_path=None):
        super().__init__()
        self.type = type
        self.image = pygame.Surface((40, 40))
        if type == "slow_mover":
            self.image.fill((255, 0, 0)) # Red
        else:
            self.image.fill((128, 128, 128))
        self.rect = self.image.get_rect(center=(x, y))
        self.patrol_path = patrol_path
        self.current_path_point = 0
        self.speed = 2

    def update(self):
        # [LLM_INJECT_ENEMY_UPDATE]
        pass

# --- Sprite Groups ---
all_sprites = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
bananas = pygame.sprite.Group()
powerups = pygame.sprite.Group()
enemies = pygame.sprite.Group()
interactive_elements = pygame.sprite.Group() # For button and interactable sprites

# --- Game Data Initialization ---
# This will be managed by the FSM template, but we define it here for scope.
game_data = {
    "level": 1,
    "score": 0,
    "multiplier": 1,
    "high_score": 0,
    "current_state": "MENU",
    "game_over": False,
    "target_transition_time": 0.5,
    "transition_timer": 0.0,
    "current_sprite_state": "monkey",
    "time_limit": 90,
    "level_timer": 0.0,
    "bananas_collected": 0,
    "target_bananas": 8,
    "target_score_level": 5000,
    "focus_active": False,
    "focus_timer": 0.0,
    "focus_duration": 5.0,
    "insight_active": False,
    "insight_timer": 0.0,
    "insight_duration": 3.0,
    "quick_reflex_available": True,
    "quick_reflex_timer": 0.0,
    "quick_reflex_duration": 1.0,
    "powerup_banana_boost_active": False,
    "powerup_banana_boost_timer": 0.0,
    "powerup_banana_boost_duration": 10.0,
    "powerup_goal_zone_active": False,
    "powerup_goal_zone_timer": 0.0,
    "powerup_goal_zone_duration": 7.0,
    "enemy_spawn_timer": 0.0,
    "enemy_spawn_interval": 5.0,
    "powerup_spawn_timer": 0.0,
    "powerup_spawn_interval": 15.0,
    "lives": 3,
    "is_paused": False,
    "click_window_open": False, # For the red button
    "click_window_timer": 0.0,
    "click_window_duration": 0.2, # Short window for button press
}

# --- Fonts ---
try:
    score_font = pygame.font.Font(None, 48)
    level_font = pygame.font.Font(None, 36)
    timer_font = pygame.font.Font(None, 48)
    message_font = pygame.font.Font(None, 72)
    small_message_font = pygame.font.Font(None, 36)
except pygame.error as e:
    print(f"Warning: Could not load default font. {e}")
    score_font = pygame.font.SysFont(None, 48)
    level_font = pygame.font.SysFont(None, 36)
    timer_font = pygame.font.SysFont(None, 48)
    message_font = pygame.font.SysFont(None, 72)
    small_message_font = pygame.font.SysFont(None, 36)

# --- Sounds ---
# Placeholder for sound loading
# jump_sound = pygame.mixer.Sound(resource_path('jump.wav'))
# hit_sound = pygame.mixer.Sound(resource_path('hit.wav'))
# collect_sound = pygame.mixer.Sound(resource_path('collect.wav'))
button_click_success_sound = None
button_click_fail_sound = None
powerup_get_sound = None
enemy_hit_sound = None
level_complete_sound = None
game_over_sound = None
background_music = None

# --- Asset Loading Function ---
def load_assets():
    global monkey_sprite_img, footballer_sprite_img, red_button_img
    global button_click_success_sound, button_click_fail_sound, powerup_get_sound
    global enemy_hit_sound, level_complete_sound, game_over_sound, background_music
    
    # Load Sprites (placeholder images)
    monkey_sprite_img = pygame.Surface((60, 60))
    monkey_sprite_img.fill((255, 165, 0)) # Orange
    
    footballer_sprite_img = pygame.Surface((60, 60))
    footballer_sprite_img.fill((0, 128, 0)) # Green
    
    red_button_img = pygame.Surface((80, 80))
    red_button_img.fill(RED)

    # Load Sounds (placeholder - replace with actual sound files)
    try:
        button_click_success_sound = pygame.mixer.Sound(resource_path('sounds/success.wav'))
        button_click_fail_sound = pygame.mixer.Sound(resource_path('sounds/fail.wav'))
        powerup_get_sound = pygame.mixer.Sound(resource_path('sounds/powerup.wav'))
        enemy_hit_sound = pygame.mixer.Sound(resource_path('sounds/enemy_hit.wav'))
        level_complete_sound = pygame.mixer.Sound(resource_path('sounds/level_complete.wav'))
        game_over_sound = pygame.mixer.Sound(resource_path('sounds/game_over.wav'))
        # pygame.mixer.music.load(resource_path('sounds/background_music.mp3'))
    except pygame.error as e:
        print(f"Warning: Could not load sounds. {e}")
        # Assign dummy sounds to prevent errors
        button_click_success_sound = pygame.mixer.Sound(pygame.sndarray.make_sound(bytearray(100000))) # Silent sound
        button_click_fail_sound = pygame.mixer.Sound(pygame.sndarray.make_sound(bytearray(100000)))
        powerup_get_sound = pygame.mixer.Sound(pygame.sndarray.make_sound(bytearray(100000)))
        enemy_hit_sound = pygame.mixer.Sound(pygame.sndarray.make_sound(bytearray(100000)))
        level_complete_sound = pygame.mixer.Sound(pygame.sndarray.make_sound(bytearray(100000)))
        game_over_sound = pygame.mixer.Sound(pygame.sndarray.make_sound(bytearray(100000)))

# --- Game Initialization ---
load_assets()

# --- Functions ---

def reset_game_data():
    global game_data
    game_data = {
        "level": 1,
        "score": 0,
        "multiplier": 1,
        "high_score": 0,
        "current_state": "MENU",
        "game_over": False,
        "target_transition_time": 0.5,
        "transition_timer": 0.0,
        "current_sprite_state": "monkey",
        "time_limit": 90,
        "level_timer": 0.0,
        "bananas_collected": 0,
        "target_bananas": 8,
        "target_score_level": 5000,
        "focus_active": False,
        "focus_timer": 0.0,
        "focus_duration": 5.0,
        "insight_active": False,
        "insight_timer": 0.0,
        "insight_duration": 3.0,
        "quick_reflex_available": True,
        "quick_reflex_timer": 0.0,
        "quick_reflex_duration": 1.0,
        "powerup_banana_boost_active": False,
        "powerup_banana_boost_timer": 0.0,
        "powerup_banana_boost_duration": 10.0,
        "powerup_goal_zone_active": False,
        "powerup_goal_zone_timer": 0.0,
        "powerup_goal_zone_duration": 7.0,
        "enemy_spawn_timer": 0.0,
        "enemy_spawn_interval": 5.0,
        "powerup_spawn_timer": 0.0,
        "powerup_spawn_interval": 15.0,
        "lives": 3,
        "is_paused": False,
        "click_window_open": False,
        "click_window_timer": 0.0,
        "click_window_duration": 0.2,
    }
    all_sprites.empty()
    obstacles.empty()
    bananas.empty()
    powerups.empty()
    enemies.empty()
    interactive_elements.empty()

def setup_level(level_data):
    global game_data
    reset_game_data()
    
    game_data["level"] = level_data["level_number"]
    game_data["time_limit"] = level_data["time_limit"]
    game_data["target_bananas"] = level_data["objectives"][0]["count"]
    game_data["target_score_level"] = level_data["objectives"][1]["target_score"]
    
    # Center player sprite at spawn point
    player_spawn_pos = (level_data["spawn_points"][0]["x"], level_data["spawn_points"][0]["y"])
    
    # Placeholder for the main interactive button
    button_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
    game_data["red_button"] = RedButton(button_pos)
    interactive_elements.add(game_data["red_button"])
    all_sprites.add(game_data["red_button"])

    # Add obstacles
    for obs_data in level_data["obstacles"]:
        obstacle = Obstacle(obs_data["x"], obs_data["y"], obs_data["width"], obs_data["height"], obs_data["type"])
        obstacles.add(obstacle)
        all_sprites.add(obstacle)

    # Add powerups
    for pup_data in level_data["powerups"]:
        powerup = PowerUp(pup_data["x"], pup_data["y"], pup_data["type"])
        powerups.add(powerup)
        all_sprites.add(powerup)

    # Add enemies
    for enemy_data in level_data["enemies"]:
        enemy = Enemy(enemy_data["x"], enemy_data["y"], enemy_data["type"], enemy_data.get("patrol_path"))
        enemies.add(enemy)
        all_sprites.add(enemy)

    # Add bananas (collectibles)
    for _ in range(game_data["target_bananas"]):
        while True:
            # Find a random position not on obstacles
            pos_x = random.randint(50, SCREEN_WIDTH - 50)
            pos_y = random.randint(50, SCREEN_HEIGHT - 50)
            banana_rect = pygame.Rect(pos_x - 10, pos_y - 10, 20, 20)
            
            is_overlapping_obstacle = False
            for obs in obstacles:
                if banana_rect.colliderect(obs.rect):
                    is_overlapping_obstacle = True
                    break
            if not is_overlapping_obstacle:
                banana = Banana((pos_x, pos_y))
                bananas.add(banana)
                all_sprites.add(banana)
                break

    # Set initial transition timer
    game_data["transition_timer"] = game_data["target_transition_time"]

def switch_sprite():
    global game_data
    current_time = pygame.time.get_ticks() / 1000.0
    
    if game_data["transition_timer"] > 0:
        game_data["transition_timer"] -= (current_time - (game_data["level_timer"] - (pygame.time.get_ticks() / 1000.0))) # time delta
        game_data["level_timer"] = current_time # Update level timer

    if game_data["transition_timer"] <= 0:
        # Randomly choose between monkey and footballer
        if random.random() < 0.5:
            game_data["current_sprite_state"] = "monkey"
        else:
            game_data["current_sprite_state"] = "footballer"
            
        # Reset timer for the next transition
        game_data["transition_timer"] = game_data["target_transition_time"]

        # Activate/Deactivate the button based on the new sprite
        if game_data["current_sprite_state"] == "footballer":
            game_data["red_button"].is_active = True
            game_data["click_window_open"] = True
            game_data["click_window_timer"] = game_data["click_window_duration"]
        else:
            game_data["red_button"].is_active = False
            game_data["click_window_open"] = False

def update_timers(dt):
    global game_data
    
    # Level Timer
    game_data["level_timer"] += dt
    if game_data["level_timer"] >= game_data["time_limit"] and game_data["current_state"] == "PLAYING":
        game_data["current_state"] = "GAME_OVER"
        if game_over_sound: game_over_sound.play()
        return

    # Sprite Transition Timer
    game_data["transition_timer"] -= dt
    if game_data["transition_timer"] <= 0:
        switch_sprite()
        game_data["transition_timer"] = game_data["target_transition_time"]
        
    # Powerup Timers
    if game_data["powerup_banana_boost_active"]:
        game_data["powerup_banana_boost_timer"] -= dt
        if game_data["powerup_banana_boost_timer"] <= 0:
            game_data["powerup_banana_boost_active"] = False
            game_data["multiplier"] = max(1, game_data["multiplier"] // 2) # Reduce multiplier
            
    if game_data["powerup_goal_zone_active"]:
        game_data["powerup_goal_zone_timer"] -= dt
        if game_data["powerup_goal_zone_timer"] <= 0:
            game_data["powerup_goal_zone_active"] = False
            
    if game_data["focus_active"]:
        game_data["focus_timer"] -= dt
        if game_data["focus_timer"] <= 0:
            game_data["focus_active"] = False
            game_data["target_transition_time"] *= 1.5 # Restore normal speed (approx)
            
    if game_data["insight_active"]:
        game_data["insight_timer"] -= dt
        if game_data["insight_timer"] <= 0:
            game_data["insight_active"] = False
            
    if game_data["quick_reflex_timer"] > 0:
        game_data["quick_reflex_timer"] -= dt
        if game_data["quick_reflex_timer"] <= 0:
            game_data["quick_reflex_available"] = True

    # Click Window Timer
    if game_data["click_window_open"]:
        game_data["click_window_timer"] -= dt
        if game_data["click_window_timer"] <= 0:
            game_data["click_window_open"] = False
            # If window closes and it was footballer, it's a miss
            if game_data["current_sprite_state"] == "footballer":
                handle_incorrect_click()


def handle_correct_click():
    global game_data
    if game_data["current_sprite_state"] == "footballer":
        game_data["score"] += 100 * game_data["multiplier"]
        game_data["multiplier"] += 1
        if button_click_success_sound: button_click_success_sound.play()
        
        # Check for level completion
        if game_data["score"] >= game_data["target_score_level"]:
            game_data["current_state"] = "LEVEL_COMPLETE"
            if level_complete_sound: level_complete_sound.play()

    # Reset click window after a successful click
    game_data["click_window_open"] = False

def handle_incorrect_click():
    global game_data
    if game_data["quick_reflex_available"] and game_data["quick_reflex_timer"] > 0:
        # Player has quick reflex active, ignore this penalty
        game_data["quick_reflex_timer"] = 0 # Consume the reflex
        return

    if button_click_fail_sound: button_click_fail_sound.play()
    game_data["multiplier"] = max(1, game_data["multiplier"] - 1) # Reduce multiplier
    game_data["score"] -= 50 # Penalty
    game_data["lives"] -= 1 # Lose a life
    if game_data["lives"] <= 0:
        game_data["current_state"] = "GAME_OVER"
        if game_over_sound: game_over_sound.play()
        
    # Reset click window after an incorrect click
    game_data["click_window_open"] = False

def check_for_level_completion():
    if game_data["bananas_collected"] >= game_data["target_bananas"] and game_data["score"] >= game_data["target_score_level"]:
        game_data["current_state"] = "LEVEL_COMPLETE"
        if level_complete_sound: level_complete_sound.play()

def spawn_random_object(group, sprite_class, spawn_chance_per_sec):
    if random.random() < spawn_chance_per_sec * dt:
        pos_x = random.randint(0, SCREEN_WIDTH)
        pos_y = random.randint(0, SCREEN_HEIGHT)
        
        # Avoid spawning on obstacles or other sprites
        new_rect = pygame.Rect(pos_x - 15, pos_y - 15, 30, 30)
        
        valid_position = True
        for sprite in all_sprites:
            if new_rect.colliderect(sprite.rect):
                valid_position = False
                break
        
        if valid_position:
            new_sprite = sprite_class((pos_x, pos_y))
            group.add(new_sprite)
            all_sprites.add(new_sprite)
            return new_sprite
    return None


# --- Sprite Initialization ---
# Level 1 data
level_1_data = {
  "level_number": 1,
  "name": "The First Kick",
  "description": "Welcome to the jungle! Learn the rhythm of the sprites and master the timed press. Your goal is to collect the scattered bananas and outsmart the clumsy jungle dwellers.",
  "size": {
    "width": 800,
    "height": 600
  },
  "spawn_points": [
    {
      "x": 400,
      "y": 300,
      "type": "player"
    }
  ],
  "obstacles": [
    {
      "x": 100,
      "y": 200,
      "width": 100,
      "height": 50,
      "type": "vines"
    },
    {
      "x": 600,
      "y": 400,
      "width": 70,
      "height": 70,
      "type": "boulder"
    },
    {
      "x": 300,
      "y": 500,
      "width": 150,
      "height": 30,
      "type": "log"
    }
  ],
  "powerups": [
    {
      "x": 250,
      "y": 100,
      "type": "multiplier_boost"
    },
    {
      "x": 700,
      "y": 250,
      "type": "time_extension"
    }
  ],
  "enemies": [
    {
      "x": 200,
      "y": 400,
      "type": "slow_mover",
      "patrol_path": [
        {
          "x": 200,
          "y": 400
        },
        {
          "x": 300,
          "y": 400
        }
      ]
    },
    {
      "x": 550,
      "y": 150,
      "type": "slow_mover",
      "patrol_path": [
        {
          "x": 550,
          "y": 150
        },
        {
          "x": 550,
          "y": 250
        }
      ]
    }
  ],
  "objectives": [
    {
      "type": "collect",
      "target": "bananas",
      "count": 8
    },
    {
      "type": "reach_score",
      "target_score": 5000
    }
  ],
  "difficulty": "easy",
  "time_limit": 90
}

# --- LLM_INJECT_GAME_VARIABLES_F ---
# Handled by A_CORE_SETUP's game_data and global state management.

# --- LLM_INJECT_SPRITE_SETUP_F ---
# Sprites are created and added within setup_level function.

# --- LLM_INJECT_ASSET_LOADING_F ---
# Handled by load_assets function.

# --- LLM_INJECT_TRANSITION_TO_PLAYING ---
    setup_level(level_1_data) # Setup the first level
    if background_music: pygame.mixer.music.play(-1) # Start background music

# --- LLM_INJECT_PLAYING_KEY_HANDLING ---
    if event.key == pygame.K_ESCAPE:
        game_data["is_paused"] = not game_data["is_paused"]
    if event.key == pygame.K_q: # Quick quit for testing
        current_state = GameState.GAME_OVER
    if event.key == pygame.K_f: # Focus ability
        if not game_data["focus_active"]:
            game_data["focus_active"] = True
            game_data["focus_timer"] = game_data["focus_duration"]
            game_data["target_transition_time"] *= 0.5 # Slow down transition
            if powerup_get_sound: powerup_get_sound.play()
    if event.key == pygame.K_i: # Insight ability
        if not game_data["insight_active"]:
            game_data["insight_active"] = True
            game_data["insight_timer"] = game_data["insight_duration"]
            if powerup_get_sound: powerup_get_sound.play()
    if event.key == pygame.K_r: # Quick Reflex ability
        if game_data["quick_reflex_available"]:
            game_data["quick_reflex_timer"] = game_data["quick_reflex_duration"]
            game_data["quick_reflex_available"] = False
            if powerup_get_sound: powerup_get_sound.play()

# --- LLM_INJECT_PLAYING_MOUSE_HANDLING ---
    if event.type == pygame.MOUSEBUTTONDOWN:
        if game_data["red_button"].rect.collidepoint(event.pos):
            if game_data["current_sprite_state"] == "footballer" and game_data["click_window_open"]:
                handle_correct_click()
            else:
                handle_incorrect_click()

# --- LLM_INJECT_PLAYING_UPDATE_LOGIC ---
    if not game_data["is_paused"]:
        dt = clock.get_time() / 1000.0 # Delta time in seconds
        update_timers(dt)

        # Update sprites
        all_sprites.update()
        
        # Check for collisions
        # Banana collection
        player_hit_bananas = pygame.sprite.spritecollide(game_data["red_button"], bananas, True) # Use red_button as placeholder for player interaction point
        for banana in player_hit_bananas:
            game_data["bananas_collected"] += 1
            game_data["score"] += 10 * game_data["multiplier"] # Small bonus for collecting
            if powerup_get_sound: powerup_get_sound.play()
            
        # Powerup collection
        player_hit_powerups = pygame.sprite.spritecollide(game_data["red_button"], powerups, True)
        for powerup in player_hit_powerups:
            if powerup.type == "multiplier_boost":
                game_data["multiplier"] *= 2
                game_data["powerup_banana_boost_active"] = True
                game_data["powerup_banana_boost_timer"] = game_data["powerup_banana_boost_duration"]
                if powerup_get_sound: powerup_get_sound.play()
            elif powerup.type == "time_extension": # This is now Goal Zone Powerup
                game_data["powerup_goal_zone_active"] = True
                game_data["powerup_goal_zone_timer"] = game_data["powerup_goal_zone_duration"]
                game_data["click_window_duration"] *= 1.5 # Expand click window
                if powerup_get_sound: powerup_get_sound.play()
            # Add other powerup types here if needed

        # Enemy collisions
        player_hit_enemies = pygame.sprite.spritecollide(game_data["red_button"], enemies, False)
        for enemy in player_hit_enemies:
            handle_incorrect_click() # Treat hitting enemy as an incorrect click
            enemy.kill() # Enemy is removed

        # Check for level completion
        check_for_level_completion()

# --- LLM_INJECT_PLAYING_DRAWING ---
    screen.fill((100, 150, 255)) # Sky blue background
    
    # Draw background elements (vines, boulders etc.)
    for obstacle in obstacles:
        pygame.draw.rect(screen, obstacle.image.get_at((0,0)), obstacle.rect)

    # Draw bananas
    for banana in bananas:
        pygame.draw.rect(screen, (255, 255, 0), banana.rect)

    # Draw powerups
    for powerup in powerups:
        color = (255, 255, 255) # Default
        if powerup.type == "multiplier_boost": color = GREEN
        elif powerup.type == "time_extension": color = BLUE
        elif powerup.type == "focus": color = (255, 0, 255)
        elif powerup.type == "insight": color = (128, 0, 128)
        elif powerup.type == "quick_reflex": color = (255, 255, 0)
        pygame.draw.rect(screen, color, powerup.rect)

    # Draw enemies
    for enemy in enemies:
        pygame.draw.rect(screen, enemy.image.get_at((0,0)), enemy.rect)

    # Draw current sprite (monkey or footballer)
    if game_data["current_sprite_state"] == "monkey":
        # Create a temporary monkey sprite for drawing
        monkey_surface = pygame.Surface((60, 60))
        monkey_surface.fill((255, 165, 0)) # Orange
        screen.blit(monkey_surface, (SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2 - 30))
    elif game_data["current_sprite_state"] == "footballer":
        # Create a temporary footballer sprite for drawing
        footballer_surface = pygame.Surface((60, 60))
        footballer_surface.fill((0, 128, 0)) # Green
        screen.blit(footballer_surface, (SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2 - 30))

    # Draw the interactive button
    pygame.draw.rect(screen, game_data["red_button"].image.get_at((0,0)), game_data["red_button"].rect)
    button_text_surface = SMALL_FONT.render("CLICK!", True, WHITE)
    button_text_rect = button_text_surface.get_rect(center=game_data["red_button"].rect.center)
    screen.blit(button_text_surface, button_text_rect)
    
    # Highlight active powerups
    if game_data["focus_active"]:
        focus_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        focus_overlay.fill((0, 0, 255, 50)) # Semi-transparent blue
        screen.blit(focus_overlay, (0, 0))
        
    if game_data["insight_active"]:
        insight_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        insight_overlay.fill((255, 255, 0, 70)) # Semi-transparent yellow
        screen.blit(insight_overlay, (0, 0))
        
    if game_data["powerup_goal_zone_active"]:
        goal_zone_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        goal_zone_overlay.fill((0, 255, 0, 40)) # Semi-transparent green
        screen.blit(goal_zone_overlay, (0, 0))

    # Draw pause screen if paused
    if game_data["is_paused"]:
        pause_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pause_overlay.fill((0, 0, 0, 150))
        screen.blit(pause_overlay, (0, 0))
        pause_text = message_font.render("PAUSED", True, WHITE)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(pause_text, pause_rect)
        esc_text = small_message_font.render("Press ESC to resume", True, WHITE)
        esc_rect = esc_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        screen.blit(esc_text, esc_rect)

# --- LLM_INJECT_DRAW_HUD ---
    # Score display
    score_text = score_font.render(f"Score: {game_data['score']}", True, WHITE)
    screen.blit(score_text, (20, 20))
    
    # Multiplier display
    multiplier_text = score_font.render(f"x{game_data['multiplier']}", True, GREEN if game_data["multiplier"] > 1 else WHITE)
    screen.blit(multiplier_text, (20, 70))
    
    # Level display
    level_text = level_font.render(f"Level: {game_data['level']}", True, WHITE)
    screen.blit(level_text, (SCREEN_WIDTH - level_text.get_width() - 20, 20))
    
    # Timer display
    remaining_time = max(0, int(game_data["time_limit"] - game_data["level_timer"]))
    timer_color = WHITE if remaining_time > 15 else (255, 165, 0) if remaining_time > 5 else RED
    timer_text = timer_font.render(f"Time: {remaining_time}", True, timer_color)
    screen.blit(timer_text, (SCREEN_WIDTH - timer_text.get_width() - 20, 70))

    # Bananas collected display
    banana_icon = pygame.Surface((20, 20))
    banana_icon.fill((255, 255, 0))
    screen.blit(banana_icon, (20, 120))
    banana_count_text = score_font.render(f"x{game_data['bananas_collected']} / {game_data['target_bananas']}", True, WHITE)
    screen.blit(banana_count_text, (50, 115))

    # Lives display (placeholder)
    # for i in range(game_data["lives"]):
    #     life_icon = pygame.Surface((20, 20))
    #     life_icon.fill(GREEN)
    #     screen.blit(life_icon, (SCREEN_WIDTH - (i + 1) * 30, 120))

# --- LLM_INJECT_TRANSITION_TO_MENU_FROM_GAMEOVER ---
    # Reset game state and clear sprites
    reset_game_data()
    if background_music: pygame.mixer.music.stop()

# --- LLM_INJECT_EVENT_HANDLING ---
    # [LLM_INJECT_EVENT_HANDLING_F] # This will call the FSM specific event handling

# --- LLM_INJECT_UPDATE_LOGIC ---
    # [LLM_INJECT_PLAYING_UPDATE_LOGIC] # This will be called when in PLAYING state

# --- LLM_INJECT_DRAWING ---
    # [LLM_INJECT_PLAYING_DRAWING] # This will be called when in PLAYING state
    # [LLM_INJECT_DRAW_HUD] # This will be called when in PLAYING state

# --- TEMPLATE: D_HEALTH_DAMAGE ---
# --- LLM_INJECT_SPRITE_SETUP_D ---
all_sprites_d = pygame.sprite.Group()
player_d = Entity(BLUE, (60, 60), 100, (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2))
enemy_d = Entity(RED, (60, 60), 50, (SCREEN_WIDTH * 2 // 3, SCREEN_HEIGHT // 2))

all_sprites_d.add(player_d, enemy_d)

# --- LLM_INJECT_SIMULATION_LOGIC ---
    # Player takes damage every 60 frames (1 second)
    if pygame.time.get_ticks() % 60 == 0 and player_d.is_alive:
        player_d.take_damage(5)
    
    # Enemy takes damage every 120 frames (2 seconds)
    if pygame.time.get_ticks() % 120 == 0 and enemy_d.is_alive:
        enemy_d.take_damage(10)

# --- LLM_INJECT_EVENT_HANDLING_D ---
        if event.type == pygame.KEYDOWN:
            # Press 'H' to heal the player
            if event.key == pygame.K_h:
                player_d.heal(10)

# --- LLM_INJECT_SPRITE_UPDATE_D ---
    all_sprites_d.update()

# --- LLM_INJECT_SPRITE_DRAW_D ---
    all_sprites_d.draw(screen)

# --- LLM_INJECT_HEALTH_BAR_DRAW_D ---
    if player_d.is_alive:
        player_d.draw_health_bar(screen)
    if enemy_d.is_alive:
        enemy_d.draw_health_bar(screen)

# --- TEMPLATE: E_BASIC_COLLISION ---
# --- LLM_INJECT_SPRITE_SETUP_E ---
all_sprites_e = pygame.sprite.Group()
walls_e = pygame.sprite.Group()

player_e = Player()
all_sprites_e.add(player_e)

# Create a wall in the center
wall_1_e = Wall(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT // 2 - 100, 50, 200)
walls_e.add(wall_1_e)
all_sprites_e.add(wall_1_e)

# --- LLM_INJECT_SPRITE_UPDATE_E ---
    all_sprites_e.update()

# --- LLM_INJECT_COLLISION_CHECK_E ---
    check_and_resolve_collision(player_e, walls_e)

# --- CORE GAME LOGIC ---

# Placeholder for actual sprite loading
monkey_sprite = pygame.Surface((60, 60))
monkey_sprite.fill((255, 165, 0)) # Orange

footballer_sprite = pygame.Surface((60, 60))
footballer_sprite.fill((0, 128, 0)) # Green

red_button_sprite = pygame.Surface((80, 80))
red_button_sprite.fill(RED)

# --- Monkey Sprite Update ---
class Monkey(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.transform.scale(monkey_sprite, (60, 60))
        self.rect = self.image.get_rect(center=pos)
        self.animation_frames = [] # Placeholder
        self.current_frame_index = 0
        self.animation_speed = 0.1
        self.last_animation_update = 0.0

    def update(self, dt, game_data):
        # Basic animation logic if frames were loaded
        # current_time = pygame.time.get_ticks() / 1000.0
        # if current_time - self.last_animation_update > self.animation_speed:
        #     self.current_frame_index = (self.current_frame_index + 1) % len(self.animation_frames)
        #     self.image = self.animation_frames[self.current_frame_index]
        #     self.last_animation_update = current_time
        pass # No complex animation for now

# --- Footballer Sprite Update ---
class Footballer(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.transform.scale(footballer_sprite, (60, 60))
        self.rect = self.image.get_rect(center=pos)
        self.animation_frames = [] # Placeholder
        self.current_frame_index = 0
        self.animation_speed = 0.1
        self.last_animation_update = 0.0

    def update(self, dt, game_data):
        # Basic animation logic if frames were loaded
        pass # No complex animation for now

# --- Red Button Sprite Update ---
class RedButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.transform.scale(red_button_sprite, (80, 80))
        self.rect = self.image.get_rect(center=pos)
        self.is_active = False

    def update(self, dt, game_data):
        # Button visual feedback based on game state
        if self.is_active:
            self.image.fill(RED) # Default active
            if game_data.get("click_window_open", False):
                # Briefly flash or change color when click window is open
                flash_speed = 0.1 # seconds per flash
                current_time = pygame.time.get_ticks() / 1000.0
                if int(current_time / flash_speed) % 2 == 0:
                    self.image.fill((255, 100, 100)) # Brighter red
                else:
                    self.image.fill(RED)
        else:
            self.image.fill((150, 150, 150)) # Grey when inactive

# --- Banana Sprite ---
class Banana(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 255, 0)) # Yellow
        self.rect = self.image.get_rect(center=pos)

# --- Obstacle Sprite ---
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, type):
        super().__init__()
        self.image = pygame.Surface([width, height])
        color = (128, 128, 128) # Default grey
        if type == "vines": color = (139, 69, 19) # Brown
        elif type == "boulder": color = (105, 105, 105) # Grey
        elif type == "log": color = (139, 69, 19) # Brown
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.type = type

# --- PowerUp Sprite ---
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.type = type
        self.image = pygame.Surface((30, 30))
        color = (255, 255, 255) # White default
        if type == "multiplier_boost": color = GREEN
        elif type == "time_extension": color = BLUE
        elif type == "focus": color = (255, 0, 255) # Purple
        elif type == "insight": color = (128, 0, 128) # Dark Purple
        elif type == "quick_reflex": color = (255, 255, 0) # Yellow
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))

# --- Enemy Sprite ---
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, type, patrol_path=None):
        super().__init__()
        self.type = type
        self.image = pygame.Surface((40, 40))
        color = (128, 128, 128) # Default grey
        if type == "slow_mover": color = RED
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.patrol_path = patrol_path
        self.current_path_point = 0
        self.speed = 2 # pixels per second

    def update(self, dt, game_data):
        if self.patrol_path:
            target_pos = pygame.math.Vector2(self.patrol_path[self.current_path_point])
            current_pos = pygame.math.Vector2(self.rect.center)
            
            if current_pos.distance_to(target_pos) < self.speed * dt * 10: # Threshold to switch points
                self.current_path_point = (self.current_path_point + 1) % len(self.patrol_path)
                target_pos = pygame.math.Vector2(self.patrol_path[self.current_path_point])
            
            direction = target_pos - current_pos
            if direction.length() > 0:
                direction = direction.normalize()
                movement = direction * self.speed * dt * 10 # Multiply by 10 to convert px/sec to px/frame (approx)
                self.rect.centerx += movement.x
                self.rect.centery += movement.y

# --- Sprite Groups ---
all_sprites = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
bananas = pygame.sprite.Group()
powerups = pygame.sprite.Group()
enemies = pygame.sprite.Group()
interactive_elements = pygame.sprite.Group() # For button and interactable sprites

# --- Game Data ---
game_data = {
    "level": 1,
    "score": 0,
    "multiplier": 1,
    "high_score": 0,
    "current_state": "MENU", # MENU, PLAYING, GAME_OVER, LEVEL_COMPLETE
    "game_over": False,
    "target_transition_time": 0.5, # Seconds between sprite changes
    "transition_timer": 0.0,
    "current_sprite_state": "monkey", # "monkey" or "footballer"
    "time_limit": 90, # Seconds for the level
    "level_timer": 0.0,
    "bananas_collected": 0,
    "target_bananas": 8,
    "target_score_level": 5000,
    "focus_active": False,
    "focus_timer": 0.0,
    "focus_duration": 5.0,
    "insight_active": False,
    "insight_timer": 0.0,
    "insight_duration": 3.0,
    "quick_reflex_available": True,
    "quick_reflex_timer": 0.0,
    "quick_reflex_duration": 1.0,
    "powerup_banana_boost_active": False,
    "powerup_banana_boost_timer": 0.0,
    "powerup_banana_boost_duration": 10.0,
    "powerup_goal_zone_active": False,
    "powerup_goal_zone_timer": 0.0,
    "powerup_goal_zone_duration": 7.0,
    "enemy_spawn_timer": 0.0,
    "enemy_spawn_interval": 5.0,
    "powerup_spawn_timer": 0.0,
    "powerup_spawn_interval": 15.0,
    "lives": 3,
    "is_paused": False,
    "click_window_open": False, # For the red button press timing
    "click_window_timer": 0.0,
    "click_window_duration": 0.2, # Short window for button press
    "red_button": None # Placeholder for the button object
}

# --- Fonts ---
try:
    score_font = pygame.font.Font(None, 48)
    level_font = pygame.font.Font(None, 36)
    timer_font = pygame.font.Font(None, 48)
    message_font = pygame.font.Font(None, 72)
    small_message_font = pygame.font.Font(None, 36)
except pygame.error as e:
    print(f"Warning: Could not load default font. {e}")
    score_font = pygame.font.SysFont(None, 48)
    level_font = pygame.font.SysFont(None, 36)
    timer_font = pygame.font.SysFont(None, 48)
    message_font = pygame.font.SysFont(None, 72)
    small_message_font = pygame.font.SysFont(None, 36)

# --- Sounds ---
button_click_success_sound = None
button_click_fail_sound = None
powerup_get_sound = None
enemy_hit_sound = None
level_complete_sound = None
game_over_sound = None
background_music = None

import random # Import random for sprite placement

# --- Asset Loading Function ---
def load_assets():
    global monkey_sprite, footballer_sprite, red_button_sprite
    global button_click_success_sound, button_click_fail_sound, powerup_get_sound
    global enemy_hit_sound, level_complete_sound, game_over_sound, background_music
    
    # Load Sprites (placeholder images)
    monkey_sprite = pygame.Surface((60, 60))
    monkey_sprite.fill((255, 165, 0)) # Orange
    
    footballer_sprite = pygame.Surface((60, 60))
    footballer_sprite.fill((0, 128, 0)) # Green
    
    red_button_sprite = pygame.Surface((80, 80))
    red_button_sprite.fill(RED)

    # Load Sounds (placeholder - replace with actual sound files)
    try:
        button_click_success_sound = pygame.mixer.Sound(resource_path('sounds/success.wav'))
        button_click_fail_sound = pygame.mixer.Sound(resource_path('sounds/fail.wav'))
        powerup_get_sound = pygame.mixer.Sound(resource_path('sounds/powerup.wav'))
        enemy_hit_sound = pygame.mixer.Sound(resource_path('sounds/enemy_hit.wav'))
        level_complete_sound = pygame.mixer.Sound(resource_path('sounds/level_complete.wav'))
        game_over_sound = pygame.mixer.Sound(resource_path('sounds/game_over.wav'))
        # pygame.mixer.music.load(resource_path('sounds/background_music.mp3'))
    except pygame.error as e:
        print(f"Warning: Could not load sounds. {e}")
        # Assign dummy sounds to prevent errors
        button_click_success_sound = pygame.mixer.Sound(pygame.sndarray.make_sound(bytearray(100000))) # Silent sound
        button_click_fail_sound = pygame.mixer.Sound(pygame.sndarray.make_sound(bytearray(100000)))
        powerup_get_sound = pygame.mixer.Sound(pygame.sndarray.make_sound(bytearray(100000)))
        enemy_hit_sound = pygame.mixer.Sound(pygame.sndarray.make_sound(bytearray(100000)))
        level_complete_sound = pygame.mixer.Sound(pygame.sndarray.make_sound(bytearray(100000)))
        game_over_sound = pygame.mixer.Sound(pygame.sndarray.make_sound(bytearray(100000)))

# --- Game Initialization ---
load_assets()

# --- Functions ---

def reset_game_data():
    global game_data
    game_data = {
        "level": 1,
        "score": 0,
        "multiplier": 1,
        "high_score": 0,
        "current_state": "MENU",
        "game_over": False,
        "target_transition_time": 0.5,
        "transition_timer": 0.0,
        "current_sprite_state": "monkey",
        "time_limit": 90,
        "level_timer": 0.0,
        "bananas_collected": 0,
        "target_bananas": 8,
        "target_score_level": 5000,
        "focus_active": False,
        "focus_timer": 0.0,
        "focus_duration": 5.0,
        "insight_active": False,
        "insight_timer": 0.0,
        "insight_duration": 3.0,
        "quick_reflex_available": True,
        "quick_reflex_timer": 0.0,
        "quick_reflex_duration": 1.0,
        "powerup_banana_boost_active": False,
        "powerup_banana_boost_timer": 0.0,
        "powerup_banana_boost_duration": 10.0,
        "powerup_goal_zone_active": False,
        "powerup_goal_zone_timer": 0.0,
        "powerup_goal_zone_duration": 7.0,
        "enemy_spawn_timer": 0.0,
        "enemy_spawn_interval": 5.0,
        "powerup_spawn_timer": 0.0,
        "powerup_spawn_interval": 15.0,
        "lives": 3,
        "is_paused": False,
        "click_window_open": False,
        "click_window_timer": 0.0,
        "click_window_duration": 0.2,
        "red_button": None
    }
    all_sprites.empty()
    obstacles.empty()
    bananas.empty()
    powerups.empty()
    enemies.empty()
    interactive_elements.empty()

def setup_level(level_data):
    global game_data
    reset_game_data()
    
    game_data["level"] = level_data["level_number"]
    game_data["time_limit"] = level_data["time_limit"]
    game_data["target_bananas"] = level_data["objectives"][0]["count"]
    game_data["target_score_level"] = level_data["objectives"][1]["target_score"]
    
    # Player spawn position (not used directly for movement in this game, but useful for context)
    player_spawn_pos = (level_data["spawn_points"][0]["x"], level_data["spawn_points"][0]["y"])
    
    # Button position (central, slightly above bottom)
    button_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
    game_data["red_button"] = RedButton(button_pos)
    interactive_elements.add(game_data["red_button"])
    all_sprites.add(game_data["red_button"])

    # Add obstacles
    for obs_data in level_data["obstacles"]:
        obstacle = Obstacle(obs_data["x"], obs_data["y"], obs_data["width"], obs_data["height"], obs_data["type"])
        obstacles.add(obstacle)
        all_sprites.add(obstacle)

    # Add powerups
    for pup_data in level_data["powerups"]:
        powerup = PowerUp(pup_data["x"], pup_data["y"], pup_data["type"])
        powerups.add(powerup)
        all_sprites.add(powerup)

    # Add enemies
    for enemy_data in level_data["enemies"]:
        enemy = Enemy(enemy_data["x"], enemy_data["y"], enemy_data["type"], enemy_data.get("patrol_path"))
        enemies.add(enemy)
        all_sprites.add(enemy)

    # Add bananas (collectibles)
    for _ in range(game_data["target_bananas"]):
        while True:
            pos_x = random.randint(50, SCREEN_WIDTH - 50)
            pos_y = random.randint(50, SCREEN_HEIGHT - 50)
            banana_rect = pygame.Rect(pos_x - 10, pos_y - 10, 20, 20)
            
            is_overlapping_obstacle = False
            for obs in obstacles:
                if banana_rect.colliderect(obs.rect):
                    is_overlapping_obstacle = True
                    break
            if not is_overlapping_obstacle:
                banana = Banana((pos_x, pos_y))
                bananas.add(banana)
                all_sprites.add(banana)
                break

    # Set initial transition timer
    game_data["transition_timer"] = game_data["target_transition_time"]

def switch_sprite():
    global game_data
    
    # Determine new sprite state
    possible_states = ["monkey", "footballer"]
    
    # Adjust transition speed based on powerups
    transition_speed_multiplier = 1.0
    if game_data["focus_active"]:
        transition_speed_multiplier = 0.5 # Slower
    
    current_transition_duration = game_data["target_transition_time"] / transition_speed_multiplier

    if game_data["transition_timer"] <= 0:
        if random.random() < 0.5:
            game_data["current_sprite_state"] = "monkey"
        else:
            game_data["current_sprite_state"] = "footballer"
            
        game_data["transition_timer"] = current_transition_duration
        
        # Update button state and click window
        if game_data["current_sprite_state"] == "footballer":
            game_data["red_button"].is_active = True
            game_data["click_window_open"] = True
            game_data["click_window_timer"] = game_data["click_window_duration"]
        else:
            game_data["red_button"].is_active = False
            game_data["click_window_open"] = False

def update_timers(dt):
    global game_data
    
    # Level Timer
    game_data["level_timer"] += dt
    if game_data["level_timer"] >= game_data["time_limit"] and game_data["current_state"] == "PLAYING":
        game_data["current_state"] = "GAME_OVER"
        if game_over_sound: game_over_sound.play()
        return

    # Sprite Transition Timer
    game_data["transition_timer"] -= dt
    if game_data["transition_timer"] <= 0:
        switch_sprite()
        
    # Powerup Timers
    if game_data["powerup_banana_boost_active"]:
        game_data["powerup_banana_boost_timer"] -= dt
        if game_data["powerup_banana_boost_timer"] <= 0:
            game_data["powerup_banana_boost_active"] = False
            game_data["multiplier"] = max(1, game_data["multiplier"] // 2)
            
    if game_data["powerup_goal_zone_active"]:
        game_data["powerup_goal_zone_timer"] -= dt
        if game_data["powerup_goal_zone_timer"] <= 0:
            game_data["powerup_goal_zone_active"] = False
            game_data["click_window_duration"] /= 1.5 # Restore normal window size

    if game_data["focus_active"]:
        game_data["focus_timer"] -= dt
        if game_data["focus_timer"] <= 0:
            game_data["focus_active"] = False
            
    if game_data["insight_active"]:
        game_data["insight_timer"] -= dt
        if game_data["insight_timer"] <= 0:
            game_data["insight_active"] = False
            
    if game_data["quick_reflex_timer"] > 0:
        game_data["quick_reflex_timer"] -= dt
        if game_data["quick_reflex_timer"] <= 0:
            game_data["quick_reflex_available"] = True

    # Click Window Timer
    if game_data["click_window_open"]:
        game_data["click_window_timer"] -= dt
        if game_data["click_window_timer"] <= 0:
            game_data["click_window_open"] = False
            # If window closes and it was footballer, it's a miss
            if game_data["current_sprite_state"] == "footballer":
                handle_incorrect_click()


def handle_correct_click():
    global game_data
    if game_data["current_sprite_state"] == "footballer" and game_data["click_window_open"]:
        game_data["score"] += 100 * game_data["multiplier"]
        game_data["multiplier"] += 1
        if button_click_success_sound: button_click_success_sound.play()
        
        # Check for level completion
        if game_data["score"] >= game_data["target_score_level"]:
            game_data["current_state"] = "LEVEL_COMPLETE"
            if level_complete_sound: level_complete_sound.play()
        
        game_data["click_window_open"] = False # Consume click window
    else: # Incorrect click (wrong sprite or outside window)
        handle_incorrect_click()

def handle_incorrect_click():
    global game_data
    if game_data["quick_reflex_timer"] > 0: # If quick reflex is active
        game_data["quick_reflex_timer"] = 0 # Consume reflex
        return # No penalty

    if button_click_fail_sound: button_click_fail_sound.play()
    game_data["multiplier"] = max(1, game_data["multiplier"] - 1) # Reduce multiplier
    game_data["score"] -= 50 # Penalty
    game_data["lives"] -= 1 # Lose a life
    if game_data["lives"] <= 0:
        game_data["current_state"] = "GAME_OVER"
        if game_over_sound: game_over_sound.play()
        
    game_data["click_window_open"] = False # Consume click window


def check_for_level_completion():
    if game_data["bananas_collected"] >= game_data["target_bananas"] and game_data["score"] >= game_data["target_score_level"]:
        game_data["current_state"] = "LEVEL_COMPLETE"
        if level_complete_sound: level_complete_sound.play()

def spawn_random_object(group, sprite_class, spawn_chance_per_sec, dt):
    if random.random() < spawn_chance_per_sec * dt:
        pos_x = random.randint(30, SCREEN_WIDTH - 30)
        pos_y = random.randint(30, SCREEN_HEIGHT - 30)
        
        # Avoid spawning on obstacles or other sprites
        new_rect = pygame.Rect(pos_x - 15, pos_y - 15, 30, 30)
        
        valid_position = True
        for sprite in all_sprites:
            if new_rect.colliderect(sprite.rect):
                valid_position = False
                break
        
        if valid_position:
            new_sprite = sprite_class((pos_x, pos_y))
            group.add(new_sprite)
            all_sprites.add(new_sprite)
            return new_sprite
    return None

# --- LLM_INJECT_GAME_VARIABLES ---
# This is the main game_data dictionary, defined above.

# --- LLM_INJECT_SPRITE_SETUP_D ---
# Sprite setup is handled within the FSM template's setup_level function.

# --- LLM_INJECT_SIMULATION_LOGIC ---
# Game loop logic for PLAYING state handles interactions and updates.

# --- LLM_INJECT_EVENT_HANDLING_D ---
# Event handling is managed by the FSM template.

# --- LLM_INJECT_SPRITE_UPDATE_D ---
# Sprite updates are handled within the PLAYING state's update logic.

# --- LLM_INJECT_SPRITE_DRAW_D ---
# Sprite drawing is handled within the PLAYING state's drawing logic.

# --- LLM_INJECT_HEALTH_BAR_DRAW_D ---
# Health bars are not a primary feature of this game, but could be added to enemies if needed.

# --- LLM_INJECT_SPRITE_SETUP_E ---
# Sprite setup is handled within the FSM template's setup_level function.

# --- LLM_INJECT_SPRITE_UPDATE_E ---
# Sprite updates are handled within the PLAYING state's update logic.

# --- LLM_INJECT_COLLISION_CHECK_E ---
# Collision checks are handled within the PLAYING state's update logic.

# --- LLM_INJECT_GAME_VARIABLES_F ---
# Global game_data dictionary is defined above and used across states.

# --- LLM_INJECT_SPRITE_SETUP_F ---
# Sprites are created and added within the setup_level function.

# --- LLM_INJECT_ASSET_LOADING_F ---
# Asset loading is handled by the load_assets function.

# --- LLM_INJECT_TRANSITION_TO_PLAYING ---
    setup_level(level_1_data) # Setup the first level
    if background_music: pygame.mixer.music.play(-1) # Start background music

# --- LLM_INJECT_PLAYING_KEY_HANDLING ---
    if event.key == pygame.K_ESCAPE:
        game_data["is_paused"] = not game_data["is_paused"]
    if event.key == pygame.K_q: # Quick quit for testing
        current_state = GameState.GAME_OVER
        if game_over_sound: game_over_sound.play()
    if event.key == pygame.K_f: # Focus ability
        if not game_data["focus_active"]:
            game_data["focus_active"] = True
            game_data["focus_timer"] = game_data["focus_duration"]
            game_data["target_transition_time"] *= 0.5 # Slow down transition
            if powerup_get_sound: powerup_get_sound.play()
    if event.key == pygame.K_i: # Insight ability
        if not game_data["insight_active"]:
            game_data["insight_active"] = True
            game_data["insight_timer"] = game_data["insight_duration"]
            if powerup_get_sound: powerup_get_sound.play()
    if event.key == pygame.K_r: # Quick Reflex ability
        if game_data["quick_reflex_available"]:
            game_data["quick_reflex_timer"] = game_data["quick_reflex_duration"]
            game_data["quick_reflex_available"] = False
            if powerup_get_sound: powerup_get_sound.play()

# --- LLM_INJECT_PLAYING_MOUSE_HANDLING ---
    if event.type == pygame.MOUSEBUTTONDOWN:
        if game_data["red_button"] and game_data["red_button"].rect.collidepoint(event.pos):
            if game_data["current_sprite_state"] == "footballer" and game_data["click_window_open"]:
                handle_correct_click()
            else:
                handle_incorrect_click()

# --- LLM_INJECT_PLAYING_UPDATE_LOGIC ---
    if not game_data["is_paused"]:
        dt = clock.get_time() / 1000.0 # Delta time in seconds
        update_timers(dt)

        # Update sprites
        for sprite in all_sprites:
            sprite.update(dt, game_data) # Pass dt and game_data for context
        
        # Check for collisions
        # Banana collection
        player_hit_bananas = pygame.sprite.spritecollide(game_data["red_button"], bananas, True)
        for banana in player_hit_bananas:
            game_data["bananas_collected"] += 1
            game_data["score"] += 10 * game_data["multiplier"] # Small bonus for collecting
            if powerup_get_sound: powerup_get_sound.play()
            
        # Powerup collection
        player_hit_powerups = pygame.sprite.spritecollide(game_data["red_button"], powerups, True)
        for powerup in player_hit_powerups:
            if powerup.type == "multiplier_boost":
                game_data["multiplier"] *= 2
                game_data["powerup_banana_boost_active"] = True
                game_data["powerup_banana_boost_timer"] = game_data["powerup_banana_boost_duration"]
                if powerup_get_sound: powerup_get_sound.play()
            elif powerup.type == "time_extension": # This is now Goal Zone Powerup
                game_data["powerup_goal_zone_active"] = True
                game_data["powerup_goal_zone_timer"] = game_data["powerup_goal_zone_duration"]
                # Expand click window duration
                game_data["click_window_duration"] *= 1.5 
                if powerup_get_sound: powerup_get_sound.play()
            # Add other powerup types here if needed

        # Enemy collisions
        player_hit_enemies = pygame.sprite.spritecollide(game_data["red_button"], enemies, False)
        for enemy in player_hit_enemies:
            handle_incorrect_click() # Treat hitting enemy as an incorrect click
            enemy.kill() # Enemy is removed

        # Spawn new powerups and enemies periodically
        game_data["powerup_spawn_timer"] += dt
        if game_data["powerup_spawn_timer"] >= game_data["powerup_spawn_interval"]:
            spawn_random_object(powerups, PowerUp, 0.1, dt) # Chance to spawn a powerup
            game_data["powerup_spawn_timer"] = 0

        game_data["enemy_spawn_timer"] += dt
        if game_data["enemy_spawn_timer"] >= game_data["enemy_spawn_interval"]:
            # Spawn enemy (e.g., slow_mover)
            enemy_x = random.randint(50, SCREEN_WIDTH - 50)
            enemy_y = random.randint(50, SCREEN_HEIGHT - 150) # Avoid spawning too close to the button
            new_enemy = Enemy(enemy_x, enemy_y, "slow_mover")
            enemies.add(new_enemy)
            all_sprites.add(new_enemy)
            game_data["enemy_spawn_timer"] = 0

        # Check for level completion
        check_for_level_completion()

# --- LLM_INJECT_PLAYING_DRAWING ---
    screen.fill((100, 150, 255)) # Sky blue background
    
    # Draw background elements (vines, boulders etc.)
    for obstacle in obstacles:
        pygame.draw.rect(screen, obstacle.image.get_at((0,0)), obstacle.rect)

    # Draw bananas
    for banana in bananas:
        pygame.draw.rect(screen, (255, 255, 0), banana.rect)

    # Draw powerups
    for powerup in powerups:
        pygame.draw.rect(screen, powerup.image.get_at((0,0)), powerup.rect)

    # Draw enemies
    for enemy in enemies:
        pygame.draw.rect(screen, enemy.image.get_at((0,0)), enemy.rect)

    # Draw current sprite (monkey or footballer)
    sprite_pos = (SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2 - 30)
    if game_data["current_sprite_state"] == "monkey":
        screen.blit(monkey_sprite, sprite_pos)
    elif game_data["current_sprite_state"] == "footballer":
        screen.blit(footballer_sprite, sprite_pos)

    # Draw the interactive button
    if game_data["red_button"]:
        pygame.draw.rect(screen, game_data["red_button"].image.get_at((0,0)), game_data["red_button"].rect)
        button_text_surface = SMALL_FONT.render("CLICK!", True, WHITE)
        button_text_rect = button_text_surface.get_rect(center=game_data["red_button"].rect.center)
        screen.blit(button_text_surface, button_text_rect)
    
    # Overlay for active powerups
    if game_data["focus_active"]:
        focus_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        focus_overlay.fill((0, 0, 255, 30)) # Semi-transparent blue
        screen.blit(focus_overlay, (0, 0))
        
    if game_data["insight_active"]:
        insight_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        insight_overlay.fill((255, 255, 0, 40)) # Semi-transparent yellow
        screen.blit(insight_overlay, (0, 0))
        
    if game_data["powerup_goal_zone_active"]:
        goal_zone_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        goal_zone_overlay.fill((0, 255, 0, 20)) # Semi-transparent green
        screen.blit(goal_zone_overlay, (0, 0))

    # Draw pause screen if paused
    if game_data["is_paused"]:
        pause_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pause_overlay.fill((0, 0, 0, 150))
        screen.blit(pause_overlay, (0, 0))
        pause_text = message_font.render("PAUSED", True, WHITE)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(pause_text, pause_rect)
        esc_text = small_message_font.render("Press ESC to resume", True, WHITE)
        esc_rect = esc_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        screen.blit(esc_text, esc_rect)

# --- LLM_INJECT_DRAW_HUD ---
    # Score display
    score_text = score_font.render(f"Score: {game_data['score']}", True, WHITE)
    screen.blit(score_text, (20, 20))
    
    # Multiplier display
    multiplier_color = GREEN if game_data["multiplier"] > 1 else WHITE
    multiplier_text = score_font.render(f"x{game_data['multiplier']}", True, multiplier_color)
    screen.blit(multiplier_text, (20, 70))
    
    # Level display
    level_text = level_font.render(f"Level: {game_data['level']}", True, WHITE)
    screen.blit(level_text, (SCREEN_WIDTH - level_text.get_width() - 20, 20))
    
    # Timer display
    remaining_time = max(0, int(game_data["time_limit"] - game_data["level_timer"]))
    timer_color = WHITE if remaining_time > 15 else (255, 165, 0) if remaining_time > 5 else RED
    timer_text = timer_font.render(f"Time: {remaining_time}", True, timer_color)
    screen.blit(timer_text, (SCREEN_WIDTH - timer_text.get_width() - 20, 70))

    # Bananas collected display
    banana_icon = pygame.Surface((20, 20))
    banana_icon.fill((255, 255, 0))
    screen.blit(banana_icon, (20, 120))
    banana_count_text = score_font.render(f"x{game_data['bananas_collected']} / {game_data['target_bananas']}", True, WHITE)
    screen.blit(banana_count_text, (50, 115))

    # Lives display (placeholder)
    life_icon_size = 20
    life_spacing = 5
    for i in range(game_data["lives"]):
        life_icon = pygame.Surface((life_icon_size, life_icon_size))
        life_icon.fill(GREEN)
        screen.blit(life_icon, (SCREEN_WIDTH - (i + 1) * (life_icon_size + life_spacing) - 20, 115))

# --- LLM_INJECT_TRANSITION_TO_MENU_FROM_GAMEOVER ---
    reset_game_data()
    if background_music: pygame.mixer.music.stop()

# --- LLM_INJECT_EVENT_HANDLING ---
    # This placeholder will be replaced by the FSM's event handling logic
    pass

# --- LLM_INJECT_UPDATE_LOGIC ---
    # This placeholder will be replaced by the FSM's update logic
    pass

# --- LLM_INJECT_DRAWING ---
    # This placeholder will be replaced by the FSM's drawing logic
    pass

# --- LLM_INJECT_GAME_VARIABLES ---
# This dictionary is defined globally at the top of the file.

# --- END OF GENERATED GAME CODE ---
