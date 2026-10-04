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
pygame.display.set_caption("Template A: Core Setup")
clock = pygame.time.Clock()

# --- Game Variables ---
# Example: a placeholder object position
player_x = SCREEN_WIDTH // 2
player_y = SCREEN_HEIGHT // 2
player_size = 50

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
    pygame.draw.rect(screen, BLUE, (player_x, player_y, player_size, player_size))
    
    # Update the full display surface to the screen
    pygame.display.flip()

    # 4. Cap the frame rate
    clock.tick(FPS)

# --- Cleanup ---
pygame.quit()
sys.exit()
