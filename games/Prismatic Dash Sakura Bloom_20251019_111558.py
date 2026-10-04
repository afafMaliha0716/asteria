# --- START GENERATED GAME CODE TEMPLATE ---

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

# [LLM_INJECT_A_2_COLORS]
# Prismatic Dash: Sakura Bloom specific colors
PINK = (255, 192, 203)
MAGENTA = (255, 0, 255)
SOFT_PINK = (255, 220, 230)
LIGHT_PURPLE = (200, 160, 220)
TEAL = (0, 128, 128)
GOLD = (255, 215, 0)
ACCENT_BLUE = (100, 150, 255)
BACKGROUND_GRADIENT_TOP = (20, 0, 40) # Dark purple
BACKGROUND_GRADIENT_BOTTOM = (60, 0, 80) # Darker purple

# --- Initialization ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# [LLM_INJECT_A_1_CAPTION]
pygame.display.set_caption("Prismatic Dash: Sakura Bloom")
clock = pygame.time.Clock()

# --- Game Variables ---
# Example: a placeholder object position
# [LLM_INJECT_A_3_PLAYER_INITIALIZATION]
PLAYER_COLOR = MAGENTA
player_x = 50 # Initial spawn x from level design
player_y = 550 # Initial spawn y from level design
player_size = 30 # For a geometric player, this defines the bounding box size


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
    pygame.draw.rect(screen, PLAYER_COLOR, (player_x, player_y, player_size, player_size))

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

# Prismatic Dash Colors (from A_CORE_SETUP for consistency)
PINK = (255, 192, 203)
MAGENTA = (255, 0, 255)
SOFT_PINK = (255, 220, 230)
LIGHT_PURPLE = (200, 160, 220)
TEAL = (0, 128, 128)
GOLD = (255, 215, 0)
ACCENT_BLUE = (100, 150, 255)

# --- Entity Class with Health System ---
class Entity(pygame.sprite.Sprite):
    def __init__(self, color, size, max_hp, position):
        super().__init__()
        self.image = pygame.Surface(size, pygame.SRCALPHA) # SRCALPHA for transparency
        self.color = color

        # Draw a geometric shape for the entity (e.g., a square for simplicity)
        # For a more advanced implementation, this could be a parameter.
        pygame.draw.rect(self.image, self.color, (0, 0, size[0], size[1]))

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
        if not self.is_alive:
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

    # [LLM_INJECT_D_1_ENTITY_UPDATE_CUSTOM]
    def update(self):
        # Placeholder update logic - no custom update needed for this basic template demonstration.
        # Specific entities in Prismatic Dash would have their movement/behavior here.
        pass

# --- Game Setup ---
all_sprites = pygame.sprite.Group()
# [LLM_INJECT_D_2_GAME_SETUP_CUSTOM]
# Player: "nimble geometric entity". Colliding with enemies "resets player to last checkpoint".
# This means the player essentially has 1 HP in a 'take damage' sense before a reset.
player = Entity(MAGENTA, (30, 30), 1, (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2))

# Enemy: Let's use "Prism Sentinel" as an example. "A larger, square enemy".
# For this health template demonstration, we give it some HP. In the actual game, it resets player.
enemy = Entity(LIGHT_PURPLE, (40, 40), 50, (SCREEN_WIDTH * 2 // 3, SCREEN_HEIGHT // 2))

all_sprites.add(player, enemy)

# --- Test Events (Simulating Damage/Heal) ---
def simulate_interaction():
    # Only interact if both are alive
    if player.is_alive and enemy.is_alive:
        # Player takes damage every 60 frames (1 second). If player has 1HP, this is a "reset".
        if pygame.time.get_ticks() % 60 == 0:
            player.take_damage(1) 

        # Enemy takes damage every 120 frames (2 seconds)
        if pygame.time.get_ticks() % 120 == 0:
            enemy.take_damage(10)

# --- Main Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            # Press 'H' to heal the player (which effectively means revive in this 1HP scenario)
            if event.key == pygame.K_h and not player.is_alive:
                player = Entity(MAGENTA, (30, 30), 1, (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2))
                all_sprites.add(player)
            # Press 'J' to heal the enemy
            if event.key == pygame.K_j and not enemy.is_alive:
                enemy = Entity(LIGHT_PURPLE, (40, 40), 50, (SCREEN_WIDTH * 2 // 3, SCREEN_HEIGHT // 2))
                all_sprites.add(enemy)

    # 1. Update
    simulate_interaction()
    all_sprites.update()

    # 2. Drawing
    screen.fill(SOFT_PINK) # A pastel background for this template to fit theme
    all_sprites.draw(screen)

    # MANDATORY: Draw health bars AFTER drawing sprites
    if player.is_alive:
        player.draw_health_bar(screen)
    if enemy.is_alive:
        enemy.draw_health_bar(screen)

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

# Prismatic Dash Colors (from A_CORE_SETUP for consistency)
PINK = (255, 192, 203)
MAGENTA = (255, 0, 255)
SOFT_PINK = (255, 220, 230)
LIGHT_PURPLE = (200, 160, 220)
TEAL = (0, 128, 128)
PLAYER_COLOR_E = MAGENTA 
WALL_COLOR_E = LIGHT_PURPLE


# --- Player Class with Collision Memory ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # [LLM_INJECT_E_1_PLAYER_CUSTOM_DRAW]
        # Player is a geometric entity, let's make it a triangle for this template.
        self.image = pygame.Surface([50, 50], pygame.SRCALPHA) # SRCALPHA for transparent background
        pygame.draw.polygon(self.image, PLAYER_COLOR_E, [(25, 0), (0, 50), (50, 50)])
        self.rect = self.image.get_rect()
        self.rect.center = (100, SCREEN_HEIGHT // 2)
        self.speed = 5
        self.dx = 0 # Delta X for current frame
        self.dy = 0 # Delta Y for current frame
        self.old_x = self.rect.x # For collision memory
        self.old_y = self.rect.y # For collision memory

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
        # [LLM_INJECT_E_2_WALL_CUSTOM_DRAW]
        # Walls are geometric obstacles/platforms
        self.image = pygame.Surface([width, height])
        self.image.fill(WALL_COLOR_E)
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

    # [LLM_INJECT_E_3_COLLISION_EXTENSION]
    if hit_walls:
        # print("Collision detected! Reverting position.") # Uncomment for console output
        # Revert movement by setting position back to the previous frame's position
        sprite.rect.x = sprite.old_x
        sprite.rect.y = sprite.old_y

        # Note: For more complex/accurate collision, you would check X and Y separately
        # and only revert the axis that caused the collision.

# --- Game Setup ---
all_sprites = pygame.sprite.Group()
walls = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# Create a wall in the center
wall_1 = Wall(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT // 2 - 100, 50, 200)
walls.add(wall_1)
all_sprites.add(wall_1)

# Create a second wall for more collision opportunities
wall_2 = Wall(SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2, 150, 50)
walls.add(wall_2)
all_sprites.add(wall_2)

# --- Main Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 1. Update
    all_sprites.update()

    # 2. Collision Check and Resolution
    check_and_resolve_collision(player, walls)

    # 3. Drawing
    screen.fill(SOFT_PINK) # A pastel background for this template
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
pygame.display.set_caption("Template F: Game States")
clock = pygame.time.Clock()
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0) # Added missing constant definition

# Prismatic Dash Colors (from A_CORE_SETUP for consistency)
PINK = (255, 192, 203)
MAGENTA = (255, 0, 255)
SOFT_PINK = (255, 220, 230)
LIGHT_PURPLE = (200, 160, 220)
TEAL = (0, 128, 128)
GOLD = (255, 215, 0)
ACCENT_BLUE = (100, 150, 255)
BACKGROUND_GRADIENT_TOP = (20, 0, 40) # Dark purple
BACKGROUND_GRADIENT_BOTTOM = (60, 0, 80) # Darker purple

# [LLM_INJECT_F_1_GAME_STATE_EXTENSIONS]
# Custom Fonts for Prismatic Dash theme
FONT_TITLE = pygame.font.Font(None, 74) # Using default font, but named for clarity
FONT_SUBTITLE = pygame.font.Font(None, 48)
FONT_NORMAL = pygame.font.Font(None, 36)

# --- Game States Enum ---
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3

# --- State Management ---
current_state = GameState.MENU

# --- State Functions ---

def run_menu(events):
    global current_state

    # Input Logic
    for event in events:
        if event.type == pygame.KEYDOWN:
            # Press SPACE to start the game
            if event.key == pygame.K_SPACE:
                current_state = GameState.PLAYING

    # Drawing
    # [LLM_INJECT_F_2_MENU_STATE_CONTENT]
    # Gradient background reflecting the abstract visual style
    for y in range(SCREEN_HEIGHT):
        color = (
            BACKGROUND_GRADIENT_TOP[0] + (BACKGROUND_GRADIENT_BOTTOM[0] - BACKGROUND_GRADIENT_TOP[0]) * y / SCREEN_HEIGHT,
            BACKGROUND_GRADIENT_TOP[1] + (BACKGROUND_GRADIENT_BOTTOM[1] - BACKGROUND_GRADIENT_TOP[1]) * y / SCREEN_HEIGHT,
            BACKGROUND_GRADIENT_TOP[2] + (BACKGROUND_GRADIENT_BOTTOM[2] - BACKGROUND_GRADIENT_TOP[2]) * y / SCREEN_HEIGHT
        )
        pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))

    title_text = FONT_TITLE.render("Prismatic Dash: Sakura Bloom", True, PINK)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))

    start_text = FONT_SUBTITLE.render("PRESS SPACE TO START", True, WHITE)
    screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2))

    instruction_text = FONT_NORMAL.render("Press 'Q' in-game to lose.", True, SOFT_PINK)
    screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))


def run_playing(events):
    global current_state

    # Input Logic
    for event in events:
        if event.type == pygame.KEYDOWN:
            # Press Q to trigger game over
            if event.key == pygame.K_q:
                current_state = GameState.GAME_OVER

    # Update Logic (Movement, Collision, etc. goes here)
    # This is where the actual game world updates in the full game.

    # Drawing
    # [LLM_INJECT_F_3_PLAYING_STATE_CONTENT]
    screen.fill(ACCENT_BLUE) # A vibrant background for playing state, geometric and abstract
    playing_text = FONT_TITLE.render("DASHING THROUGH LEVELS", True, WHITE)
    screen.blit(playing_text, (SCREEN_WIDTH // 2 - playing_text.get_width() // 2, SCREEN_HEIGHT // 2))

    instruction_text = FONT_NORMAL.render("Current Score: 0 | Bloom Essences: 0", True, SOFT_PINK)
    screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))


def run_game_over(events):
    global current_state

    # Input Logic
    for event in events:
        if event.type == pygame.KEYDOWN:
            # Press R to restart (go back to menu)
            if event.key == pygame.K_r:
                current_state = GameState.MENU

    # Drawing
    # [LLM_INJECT_F_4_GAME_OVER_STATE_CONTENT]
    screen.fill(BACKGROUND_GRADIENT_TOP) # Dark background for game over
    over_text = FONT_TITLE.render("GAME OVER", True, RED)
    screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))

    score_text = FONT_SUBTITLE.render("Final Score: 12345", True, WHITE) # Placeholder score
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))

    restart_text = FONT_NORMAL.render("Press 'R' to return to Menu", True, SOFT_PINK)
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 80))


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

# --- TEMPLATE: C_MOVEMENT_PLATFORMER ---
import pygame

# --- Constants & Initialization (Assumed from A) ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
FPS = 60
BLACK = (0, 0, 0)
RED = (255, 0, 0)
FLOOR_Y = SCREEN_HEIGHT - 50 # Y position of the "ground" - THIS WILL BE REPLACED by platforms

# Prismatic Dash Colors (from A_CORE_SETUP for consistency)
PINK = (255, 192, 203)
MAGENTA = (255, 0, 255)
SOFT_PINK = (255, 220, 230)
LIGHT_PURPLE = (200, 160, 220)
TEAL = (0, 128, 128)
GOLD = (255, 215, 0)
PLAYER_COLOR_C = MAGENTA
PLATFORM_COLOR_C = LIGHT_PURPLE
BACKGROUND_COLOR_C = (30, 0, 60) # A dark purple for platformer background

# Level 1 data (simplified for direct use in this template)
level_design = {
  "level_number": 1,
  "name": "Sakura Grove's First Steps",
  "description": "Welcome to Prismatic Dash! This introductory level will guide you through the basic platforming and rhythm mechanics. Focus on precise jumps and timing your movements to the gentle beat of the falling cherry blossoms.",
  "size": {
    "width": 800,
    "height": 600
  },
  "spawn_points": [
    {
      "x": 50,
      "y": 550,
      "type": "player"
    }
  ],
  "platforms": [
    {
      "x": 50,
      "y": 500,
      "width": 100,
      "height": 20,
      "type": "ground"
    },
    {
      "x": 150,
      "y": 450,
      "width": 80,
      "height": 20,
      "type": "ground"
    },
    {
      "x": 230,
      "y": 400,
      "width": 60,
      "height": 20,
      "type": "ground"
    },
    {
      "x": 300,
      "y": 350,
      "width": 70,
      "height": 20,
      "type": "ground"
    },
    {
      "x": 370,
      "y": 300,
      "width": 80,
      "height": 20,
      "type": "ground"
    },
    {
      "x": 450,
      "y": 250,
      "width": 100,
      "height": 20,
      "type": "ground"
    },
    {
      "x": 550,
      "y": 200,
      "width": 70,
      "height": 20,
      "type": "ground"
    },
    {
      "x": 620,
      "y": 150,
      "width": 80,
      "height": 20,
      "type": "ground"
    },
    {
      "x": 700,
      "y": 100,
      "width": 100,
      "height": 20,
      "type": "ground"
    },
    {
      "x": 100,
      "y": 300,
      "width": 50,
      "height": 20,
      "type": "ground"
    },
    {
      "x": 200,
      "y": 250,
      "width": 50,
      "height": 20,
      "type": "ground"
    }
  ],
  "hazards": [],
  "powerups": [],
  "enemies": [],
  "objectives": [],
  "difficulty": "easy",
  "time_limit": 90
}

# --- Platform Class ---
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=PLATFORM_COLOR_C):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

# --- Platformer Player Class ---
class Player(pygame.sprite.Sprite):
    GRAVITY = 1
    JUMP_STRENGTH = -18 # Adjusted for typical platformer feel

    # [LLM_INJECT_C_1_PLAYER_DASH_LOGIC]
    DASH_SPEED = 15 # Horizontal burst speed
    DASH_DURATION = 15 # frames the dash lasts
    DASH_COOLDOWN = 60 # frames until dash can be used again after ending

    def __init__(self, start_x, start_y):
        super().__init__()
        # [LLM_INJECT_C_4_PLAYER_VISUALS]
        # Player is a geometric entity: triangle
        self.width = 30
        self.height = 40
        self.image = pygame.Surface([self.width, self.height], pygame.SRCALPHA)
        pygame.draw.polygon(self.image, PLAYER_COLOR_C, 
                            [(self.width // 2, 0), (0, self.height), (self.width, self.height)])

        # Position rect adjusted for bottom-left spawn to be on ground
        self.rect = self.image.get_rect(midbottom=(start_x + self.width//2, start_y)) 

        # Movement state
        self.speed = 5
        self.horizontal_velocity = 0
        self.vertical_velocity = 0
        self.on_ground = False
        self.can_dash = True # Resets on landing
        self.dashing = False
        self.dash_direction = 0 # -1 for left, 1 for right
        self.dash_timer = 0
        self.dash_cooldown_timer = 0

        self.old_x = self.rect.x # For collision resolution
        self.old_y = self.rect.y # For collision resolution

    def handle_input(self):
        keys = pygame.key.get_pressed()

        # Reset horizontal velocity if not dashing, and apply new input
        if not self.dashing:
            self.horizontal_velocity = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.horizontal_velocity = -self.speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.horizontal_velocity = self.speed

        # Jump handling (only if on the ground)
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vertical_velocity = self.JUMP_STRENGTH
            self.on_ground = False # Cannot jump again mid-air
            self.can_dash = True # Player can dash after a new jump

        # Dash ability (if not currently dashing, can dash, and cooldown is over)
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.can_dash and self.dash_cooldown_timer <= 0:
            # Dash is a quick horizontal burst. Can be performed mid-air or with horizontal input.
            if self.horizontal_velocity != 0 or not self.on_ground: # Requires some direction or being airborne
                self.dashing = True
                self.can_dash = False # One dash per jump/ground contact
                self.dash_timer = self.DASH_DURATION
                self.dash_cooldown_timer = self.DASH_COOLDOWN

                # Determine dash direction: use current horizontal velocity, or default if none
                if self.horizontal_velocity < 0:
                    self.dash_direction = -1
                elif self.horizontal_velocity > 0:
                    self.dash_direction = 1
                else: # If no horizontal input, dash in the last known direction or default to right
                    self.dash_direction = 1 if self.dash_direction == 0 else self.dash_direction # Default to right if no prior direction

                self.horizontal_velocity = self.dash_direction * self.DASH_SPEED # Apply dash speed

    def apply_gravity(self):
        # Apply gravity to vertical velocity
        self.vertical_velocity += self.GRAVITY

        # Clamp max fall speed to prevent clipping through thin platforms
        self.vertical_velocity = min(self.vertical_velocity, 20)

    def check_platform_collision(self, platforms):
        # Store old position for collision resolution
        self.old_x = self.rect.x
        self.old_y = self.rect.y

        # Apply horizontal movement
        self.rect.x += self.horizontal_velocity
        # Check horizontal collisions
        hit_platforms = pygame.sprite.spritecollide(self, platforms, False)
        for platform in hit_platforms:
            if self.horizontal_velocity > 0: # Moving right, hit left side of platform
                self.rect.right = platform.rect.left
            elif self.horizontal_velocity < 0: # Moving left, hit right side of platform
                self.rect.left = platform.rect.right
            self.horizontal_velocity = 0 # Stop horizontal movement on collision

        # Apply vertical movement
        self.rect.y += self.vertical_velocity
        # Check vertical collisions
        hit_platforms = pygame.sprite.spritecollide(self, platforms, False)
        self.on_ground = False # Assume not on ground unless collision proves otherwise
        for platform in hit_platforms:
            if self.vertical_velocity > 0: # Falling (landed on platform)
                self.rect.bottom = platform.rect.top
                self.vertical_velocity = 0
                self.on_ground = True
                self.can_dash = True # Reset dash on landing
            elif self.vertical_velocity < 0: # Jumping (hit head on platform)
                self.rect.top = platform.rect.bottom
                self.vertical_velocity = 0


    def update(self, platforms):
        # Handle dash timer
        if self.dashing:
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.dashing = False
                self.horizontal_velocity = 0 # Stop dash movement immediately after duration

        # Handle dash cooldown
        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= 1

        self.handle_input()
        self.apply_gravity()
        # [LLM_INJECT_C_2_PLATFORM_COLLISION]
        self.check_platform_collision(platforms) # Pass the platforms group for accurate collision

        # Keep player within screen bounds
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top) # Prevent player from going above screen

        # If player falls off screen, reset to spawn
        if self.rect.top > SCREEN_HEIGHT: 
            player_spawn = level_design["spawn_points"][0]
            self.rect.midbottom = (player_spawn["x"] + self.width//2, player_spawn["y"]) # Reset to spawn point
            self.vertical_velocity = 0
            self.horizontal_velocity = 0
            self.on_ground = True
            self.can_dash = True
            self.dashing = False
            self.dash_timer = 0
            self.dash_cooldown_timer = 0


# --- Game Setup ---
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()

# [LLM_INJECT_C_3_LEVEL_SETUP]
# Create player at specified spawn point from level_design
player_spawn = level_design["spawn_points"][0]
player = Player(player_spawn["x"], player_spawn["y"])
all_sprites.add(player)

# Create platforms from level data
for p_data in level_design["platforms"]:
    platform = Platform(p_data["x"], p_data["y"], p_data["width"], p_data["height"])
    platforms.add(platform)
    all_sprites.add(platform) # Add platforms to all_sprites for drawing

# --- Main Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 1. Update
    player.update(platforms) # Pass the platforms group to player's update for collision

    # 2. Drawing
    screen.fill(BACKGROUND_COLOR_C) # Use a themed background color

    # Draw all sprites (platforms first, then player)
    all_sprites.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()


# --- END GENERATED GAME CODE TEMPLATE ---