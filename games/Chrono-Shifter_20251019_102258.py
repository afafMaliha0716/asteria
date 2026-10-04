
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

# --- Initialization ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chrono-Shifter") # Updated caption
clock = pygame.time.Clock()

# --- Game Variables ---
# No specific game variables needed here for this template, but can be added later
player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2] # Placeholder for player position
player_color = BLUE # Placeholder for player color


# --- Main Game Loop ---
running = True
while running:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Example: Handle key presses for demonstration
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                print("Space bar pressed!") # Placeholder action

    # 2. Update Game Logic
    # Placeholder: If player_pos was being controlled, update it here.
    pass

    # 3. Drawing
    screen.fill(BLACK) # Clear the screen
    
    # Draw a placeholder object
    pygame.draw.rect(screen, player_color, (player_pos[0], player_pos[1], 50, 50)) # Example placeholder drawing
    
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
YELLOW = (255, 255, 0) # For power-ups

# --- Entity Class with Health System ---
class Entity(pygame.sprite.Sprite):
    def __init__(self, color, size, max_hp, position, name="Entity"):
        super().__init__()
        self.name = name
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
        print(f"{self.name} took damage: {amount}. Current HP: {self.current_health}")
        
        if self.current_health <= 0:
            self.current_health = 0
            self.die()

    def heal(self, amount):
        if not self.is_alive:
            return
            
        self.current_health += amount
        self.current_health = min(self.current_health, self.max_health)
        print(f"{self.name} healed: {amount}. Current HP: {self.current_health}")

    def die(self):
        self.is_alive = False
        print(f"{self.name} died!")
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

# --- PowerUp Class ---
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, color, size, position, type, duration=5000): # Duration in milliseconds
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.type = type
        self.duration = duration
        self.start_time = pygame.time.get_ticks() # Time when power-up is activated

    def is_active(self):
        return pygame.time.get_ticks() - self.start_time < self.duration

# --- Game Setup ---
all_sprites = pygame.sprite.Group()
entities = pygame.sprite.Group() # Group for entities that can have health

# Player and Enemy initialization
player = Entity(BLUE, (60, 60), 100, (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2), name="Player")
enemy = Entity(RED, (60, 60), 50, (SCREEN_WIDTH * 2 // 3, SCREEN_HEIGHT // 2), name="Enemy")

all_sprites.add(player, enemy)
entities.add(player, enemy)

# Power-up initialization
health_powerup = PowerUp(YELLOW, (30, 30), (SCREEN_WIDTH * 0.75, SCREEN_HEIGHT // 2), "health", duration=5000)
all_sprites.add(health_powerup)


# --- Test Events (Simulating Damage/Heal) ---
def simulate_interaction():
    # Only interact if both are alive
    if player.is_alive and enemy.is_alive:
        # Player takes damage every 60 frames (1 second)
        if pygame.time.get_ticks() % 60 == 0:
            player.take_damage(5)
        
        # Enemy takes damage every 120 frames (2 seconds)
        if pygame.time.get_ticks() % 120 == 0:
            enemy.take_damage(10)

# --- Main Game Loop ---
running = True
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            # Press 'H' to heal the player
            if event.key == pygame.K_h:
                player.heal(10)

    # 1. Update
    simulate_interaction()
    all_sprites.update()

    # Power-up collision with player
    if pygame.sprite.collide_rect(player, health_powerup):
        if health_powerup.is_active(): # Ensure power-up is still active
            player.heal(20)
            print("Player picked up health power-up!")
            health_powerup.kill() # Remove power-up after collection
            # Optionally, re-spawn power-up after a delay or add new ones

    # Drawing
    screen.fill(WHITE)
    all_sprites.draw(screen)
    
    # MANDATORY: Draw health bars AFTER drawing sprites
    for entity in entities:
        if entity.is_alive:
            entity.draw_health_bar(screen)

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
BLUE = (0, 0, 255) # Added for player

# --- Player Class with Collision Memory ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([50, 50])
        self.image.fill(BLUE) # Changed color to BLUE for clarity
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
        print("Collision detected! Reverting position.")
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
pygame.display.set_caption("Template F: Game States")
clock = pygame.time.Clock()
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0) # Added missing constant definition
FONT = pygame.font.Font(None, 74)
SMALL_FONT = pygame.font.Font(None, 36)

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
    screen.fill(BLACK)
    title_text = FONT.render("PRESS SPACE TO START", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
    instruction_text = SMALL_FONT.render("Press 'Q' in-game to lose.", True, WHITE)
    screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))


def run_playing(events):
    global current_state
    
    # Input Logic
    for event in events:
        if event.type == pygame.KEYDOWN:
            # Press Q to trigger game over
            if event.key == pygame.K_q:
                current_state = GameState.GAME_OVER
    
    # Update Logic (Movement, Collision, etc. goes here)
    
    # Drawing
    screen.fill((50, 50, 150)) # Blue background for playing state
    playing_text = FONT.render("GAME IN PROGRESS", True, WHITE)
    screen.blit(playing_text, (SCREEN_WIDTH // 2 - playing_text.get_width() // 2, SCREEN_HEIGHT // 2))


def run_game_over(events):
    global current_state
    
    # Input Logic
    for event in events:
        if event.type == pygame.KEYDOWN:
            # Press R to restart (go back to menu)
            if event.key == pygame.K_r:
                current_state = GameState.MENU
    
    # Drawing
    screen.fill(BLACK)
    over_text = FONT.render("GAME OVER", True, RED)
    screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
    restart_text = SMALL_FONT.render("Press 'R' to return to Menu", True, WHITE)
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))


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


# --- END GENERATED GAME CODE TEMPLATE ---
