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
