
import pygame
import sys
import os
import random
from enum import Enum

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)
COSMIC_BLUE = (30, 30, 70) # Dark blue for space background
GRID_LINE_COLOR = (80, 80, 120) # Muted blue-grey for grid lines
WIN_LINE_COLOR = (255, 255, 0) # Bright yellow for winning line highlight
PREDICT_INSIGHT_COLOR = (255, 100, 0) # Orange for predictive insight

# Grid dimensions
GRID_ROWS = 3
GRID_COLS = 3
CELL_SIZE = 150 # Size of each square cell
GRID_WIDTH = GRID_COLS * CELL_SIZE
GRID_HEIGHT = GRID_ROWS * CELL_SIZE
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_WIDTH) // 2
GRID_OFFSET_Y = (SCREEN_HEIGHT - GRID_HEIGHT) // 2

# Game markers
PLAYER_MARKER = 'X' # Benevolent star
AI_MARKER = 'O'     # Swirling void

# Game settings
ROUNDS_TO_WIN_GAME = 3 # Win condition for the overall game
AI_TURN_DELAY_MS = 700 # milliseconds delay for AI moves

# --- Initialization ---
pygame.init()
pygame.mixer.init() # Initialize mixer for sounds

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cosmic Grid Guardians")
clock = pygame.time.Clock()

# Fonts
FONT_TITLE = pygame.font.Font(None, 74)
FONT_HEADER = pygame.font.Font(None, 56)
FONT_MEDIUM = pygame.font.Font(None, 48)
FONT_SMALL = pygame.font.Font(None, 36)
FONT_TINY = pygame.font.Font(None, 24)

# --- Asset Path Handler (from G_ASSET_PATH_HANDLER) ---
def resource_path(relative_path):
    """
    Get the absolute path to resource, works for dev and for PyInstaller.
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Asset Loading ---
IMAGES = {}
SOUNDS = {}

def load_assets():
    # Attempt to load actual assets; fallback to generated surfaces/no sound if not found.
    # To use actual images, create an 'assets' folder and place:
    # 'background.png', 'player_x.png', 'ai_o.png'
    # 'marker_place.wav', 'win_fanfare.wav', 'lose_sound.wav' inside.

    # Background
    try:
        IMAGES['background'] = pygame.image.load(resource_path(os.path.join('assets', 'background.png'))).convert()
        IMAGES['background'] = pygame.transform.scale(IMAGES['background'], (SCREEN_WIDTH, SCREEN_HEIGHT))
    except FileNotFoundError:
        print("Background image not found, using solid color.")
        bg_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        bg_surface.fill(COSMIC_BLUE)
        IMAGES['background'] = bg_surface

    # Markers (Benevolent Star for X, Swirling Void for O)
    try:
        IMAGES['player_x'] = pygame.image.load(resource_path(os.path.join('assets', 'player_x.png'))).convert_alpha()
        IMAGES['player_x'] = pygame.transform.scale(IMAGES['player_x'], (CELL_SIZE - 20, CELL_SIZE - 20))
    except FileNotFoundError:
        print("Player X (star) image not found, using placeholder circle.")
        x_surface = pygame.Surface((CELL_SIZE - 20, CELL_SIZE - 20), pygame.SRCALPHA)
        pygame.draw.circle(x_surface, YELLOW, ((CELL_SIZE - 20) // 2, (CELL_SIZE - 20) // 2), (CELL_SIZE - 20) // 2 - 5, 5) # Outline
        pygame.draw.circle(x_surface, (255, 255, 150), ((CELL_SIZE - 20) // 2, (CELL_SIZE - 20) // 2), (CELL_SIZE - 20) // 2 - 10) # Fill
        IMAGES['player_x'] = x_surface

    try:
        IMAGES['ai_o'] = pygame.image.load(resource_path(os.path.join('assets', 'ai_o.png'))).convert_alpha()
        IMAGES['ai_o'] = pygame.transform.scale(IMAGES['ai_o'], (CELL_SIZE - 20, CELL_SIZE - 20))
    except FileNotFoundError:
        print("AI O (void) image not found, using placeholder circle.")
        o_surface = pygame.Surface((CELL_SIZE - 20, CELL_SIZE - 20), pygame.SRCALPHA)
        pygame.draw.circle(o_surface, PURPLE, ((CELL_SIZE - 20) // 2, (CELL_SIZE - 20) // 2), (CELL_SIZE - 20) // 2 - 5, 5) # Outline
        pygame.draw.circle(o_surface, (50, 0, 50), ((CELL_SIZE - 20) // 2, (CELL_SIZE - 20) // 2), (CELL_SIZE - 20) // 2 - 10) # Fill
        IMAGES['ai_o'] = o_surface

    # Sounds
    try:
        SOUNDS['marker_place'] = pygame.mixer.Sound(resource_path(os.path.join('assets', 'marker_place.wav')))
        SOUNDS['marker_place'].set_volume(0.5)
    except FileNotFoundError:
        print("Marker place sound not found.")
        SOUNDS['marker_place'] = None

    try:
        SOUNDS['win_fanfare'] = pygame.mixer.Sound(resource_path(os.path.join('assets', 'win_fanfare.wav')))
    except FileNotFoundError:
        print("Win fanfare sound not found.")
        SOUNDS['win_fanfare'] = None
    
    try:
        SOUNDS['lose_sound'] = pygame.mixer.Sound(resource_path(os.path.join('assets', 'lose_sound.wav')))
    except FileNotFoundError:
        print("Lose sound not found.")
        SOUNDS['lose_sound'] = None

load_assets()

# --- Game States (from F_GAME_STATES) ---
class GameState(Enum):
    MENU = 1
    PLAYING_ROUND = 2
    ROUND_OVER = 3
    GAME_OVER_SCREEN = 4

current_state = GameState.MENU

# --- Game Variables ---
board = [['' for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
current_player = PLAYER_MARKER
winner = None
winning_line = None # Stores (start_cell, end_cell) for highlighting
game_over = False # True if round is over

player_score = 0
ai_score = 0

ai_active_delay = 0 # Timer for AI turn delay

# Player Abilities / Powerups
scramble_grid_uses = 1 # Usable once per game
cosmic_rewind_uses = 1 # Usable once per game
last_player_move = None # Stores (row, col) of the last player move for Cosmic Rewind
stellar_shift_active = False # True when player is selecting markers to swap
stellar_shift_selection = [] # Stores (row, col) of two selected markers for swap

# Round Timer
round_time_limit = 180 # seconds for Level 1
current_round_time = round_time_limit
round_timer_started = False

# --- Helper Functions ---
def reset_game():
    """Resets all game progress and abilities for a new game."""
    global player_score, ai_score, scramble_grid_uses, cosmic_rewind_uses, game_over
    player_score = 0
    ai_score = 0
    scramble_grid_uses = 1
    cosmic_rewind_uses = 1
    game_over = False # Overall game over state
    reset_round()

def reset_round():
    """Resets the board and round-specific variables for a new round."""
    global board, current_player, winner, winning_line, game_over, current_round_time, round_timer_started, ai_active_delay, last_player_move, stellar_shift_active, stellar_shift_selection
    board = [['' for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    current_player = PLAYER_MARKER # Player always starts new rounds
    winner = None
    winning_line = None
    game_over = False # Round over state
    current_round_time = round_time_limit
    round_timer_started = False
    ai_active_delay = 0
    last_player_move = None
    stellar_shift_active = False
    stellar_shift_selection = []

def draw_grid():
    """Draws the Tic-Tac-Toe grid lines."""
    for row in range(1, GRID_ROWS):
        pygame.draw.line(screen, GRID_LINE_COLOR, 
                         (GRID_OFFSET_X, GRID_OFFSET_Y + row * CELL_SIZE), 
                         (GRID_OFFSET_X + GRID_WIDTH, GRID_OFFSET_Y + row * CELL_SIZE), 5)
    for col in range(1, GRID_COLS):
        pygame.draw.line(screen, GRID_LINE_COLOR, 
                         (GRID_OFFSET_X + col * CELL_SIZE, GRID_OFFSET_Y), 
                         (GRID_OFFSET_X + col * CELL_SIZE, GRID_OFFSET_Y + GRID_HEIGHT), 5)

def draw_markers():
    """Draws the 'X' (player) and 'O' (AI) markers on the grid."""
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            center_x = GRID_OFFSET_X + col * CELL_SIZE + CELL_SIZE // 2
            center_y = GRID_OFFSET_Y + row * CELL_SIZE + CELL_SIZE // 2
            
            if board[row][col] == PLAYER_MARKER:
                marker_rect = IMAGES['player_x'].get_rect(center=(center_x, center_y))
                screen.blit(IMAGES['player_x'], marker_rect)
            elif board[row][col] == AI_MARKER:
                marker_rect = IMAGES['ai_o'].get_rect(center=(center_x, center_y))
                screen.blit(IMAGES['ai_o'], marker_rect)

def get_cell_from_mouse_pos(pos):
    """Converts mouse click coordinates to grid (row, col) indices."""
    mouse_x, mouse_y = pos
    if GRID_OFFSET_X <= mouse_x < GRID_OFFSET_X + GRID_WIDTH and \
       GRID_OFFSET_Y <= mouse_y < GRID_OFFSET_Y + GRID_HEIGHT:
        col = (mouse_x - GRID_OFFSET_X) // CELL_SIZE
        row = (mouse_y - GRID_OFFSET_Y) // CELL_SIZE
        return row, col
    return None, None

def is_valid_move(row, col):
    """Checks if a given cell is within bounds and empty."""
    return 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS and board[row][col] == ''

def place_marker(row, col, player):
    """Places a marker on the board if the move is valid."""
    global board, last_player_move
    if is_valid_move(row, col):
        board[row][col] = player
        if player == PLAYER_MARKER:
            last_player_move = (row, col)
        if SOUNDS['marker_place']:
            SOUNDS['marker_place'].play()
        return True
    return False

def check_win(board_state, player):
    """Checks if the given player has a winning line on the board."""
    # Check rows
    for row in range(GRID_ROWS):
        if all(board_state[row][col] == player for col in range(GRID_COLS)):
            return [(row, 0), (row, GRID_COLS - 1)] # Start and end cells for line
    # Check columns
    for col in range(GRID_COLS):
        if all(board_state[row][col] == player for row in range(GRID_ROWS)):
            return [(0, col), (GRID_ROWS - 1, col)]
    # Check diagonals
    if all(board_state[i][i] == player for i in range(GRID_ROWS)):
        return [(0, 0), (GRID_ROWS - 1, GRID_COLS - 1)]
    if all(board_state[i][GRID_COLS - 1 - i] == player for i in range(GRID_ROWS)):
        return [(0, GRID_COLS - 1), (GRID_ROWS - 1, 0)]
    return None

def check_draw(board_state):
    """Checks if the board is full and there's no winner."""
    return all(board_state[row][col] != '' for row in range(GRID_ROWS) for col in range(GRID_COLS)) and not check_win(board_state, PLAYER_MARKER) and not check_win(board_state, AI_MARKER)

def highlight_winning_line():
    """Draws a line through the winning markers."""
    if winning_line:
        start_row, start_col = winning_line[0]
        end_row, end_col = winning_line[1]

        # Calculate pixel coordinates for the center of the start and end cells
        start_x = GRID_OFFSET_X + start_col * CELL_SIZE + CELL_SIZE // 2
        start_y = GRID_OFFSET_Y + start_row * CELL_SIZE + CELL_SIZE // 2
        end_x = GRID_OFFSET_X + end_col * CELL_SIZE + CELL_SIZE // 2
        end_y = GRID_OFFSET_Y + end_row * CELL_SIZE + CELL_SIZE // 2

        pygame.draw.line(screen, WIN_LINE_COLOR, (start_x, start_y), (end_x, end_y), 8)

def get_empty_cells(board_state):
    """Returns a list of (row, col) for all empty cells on the board."""
    return [(r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS) if board_state[r][c] == '']

# --- AI Behaviors ---
# Level 1: Nebula Nuisance (easy) - Randomly places markers.
def ai_move_nebula_nuisance():
    empty_cells = get_empty_cells(board)
    if empty_cells:
        return random.choice(empty_cells)
    return None # No moves available

# --- Predictive Insight (Passive Ability) ---
def get_predictive_insight_moves(player_to_check):
    """
    Identifies potential winning moves for the given player on the current board.
    This is used passively for the player to see opponent's threats.
    """
    potential_winning_moves = []
    empty_cells = get_empty_cells(board)
    
    for r, c in empty_cells:
        temp_board = [row[:] for row in board] # Create a deep copy to simulate move
        temp_board[r][c] = player_to_check
        if check_win(temp_board, player_to_check):
            potential_winning_moves.append((r, c))
    return potential_winning_moves

# --- Powerup Callbacks ---
def trigger_scramble_grid():
    """
    Re-randomizes the current state of the grid, offering a fresh start.
    Usable once per game.
    """
    global board, scramble_grid_uses, current_player, last_player_move
    if scramble_grid_uses > 0:
        # Collect existing markers
        player_markers = []
        ai_markers = []
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if board[r][c] == PLAYER_MARKER:
                    player_markers.append((r,c))
                elif board[r][c] == AI_MARKER:
                    ai_markers.append((r,c))

        # Re-initialize board to empty
        board = [['' for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        
        # Combine and shuffle all markers
        all_markers_types = [PLAYER_MARKER] * len(player_markers) + [AI_MARKER] * len(ai_markers)
        random.shuffle(all_markers_types)

        # Get all empty cells (which is all cells now) and shuffle
        available_cells = [(r,c) for r in range(GRID_ROWS) for c in range(GRID_COLS)]
        random.shuffle(available_cells)

        # Place markers back randomly
        for marker_type in all_markers_types:
            if available_cells:
                r, c = available_cells.pop(0)
                board[r][c] = marker_type
        
        scramble_grid_uses -= 1
        current_player = PLAYER_MARKER # Player always gets the first turn after scramble
        last_player_move = None # Reset last move as board state is new
        print("Scramble Grid activated!")
        return True
    print("No Scramble Grid uses left!")
    return False

def trigger_cosmic_rewind():
    """
    Lets the player undo their last move, providing a chance to reconsider.
    Usable once per game.
    """
    global board, cosmic_rewind_uses, current_player, last_player_move, winner, winning_line, game_over
    if cosmic_rewind_uses > 0 and last_player_move and current_player == AI_MARKER:
        # Can only rewind if it's currently AI's turn (meaning player just made a move)
        row, col = last_player_move
        board[row][col] = '' # Remove last placed marker
        current_player = PLAYER_MARKER # Player's turn again
        last_player_move = None # Cannot undo again without a new player move
        cosmic_rewind_uses -= 1
        # Also clear any winning state from that move
        winner = None
        winning_line = None
        game_over = False
        print("Cosmic Rewind activated!")
        return True
    print("No Cosmic Rewind uses left or no previous player move to undo (or not player's turn)!")
    return False

def trigger_stellar_shift():
    """
    Allows the player to swap the positions of two of their already placed markers.
    """
    global stellar_shift_active, stellar_shift_selection, current_player
    if stellar_shift_active: # If already active, cancel it
        stellar_shift_active = False
        stellar_shift_selection = []
        print("Stellar Shift cancelled.")
    else:
        # Check if there are at least two of the player's markers to swap
        player_markers_on_board = sum(1 for row in board for cell in row if cell == PLAYER_MARKER)
        if player_markers_on_board >= 2:
            stellar_shift_active = True
            stellar_shift_selection = []
            current_player = PLAYER_MARKER # Player can use ability on their turn
            print("Stellar Shift activated. Select two of your markers to swap.")
        else:
            print("Not enough player markers on the board to use Stellar Shift.")


# --- UI Elements ---
class Button:
    def __init__(self, x, y, width, height, text, font, color, hover_color, text_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.action = action
        self.is_hovered = False

    def draw(self, surface):
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=8)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            if self.action:
                self.action()
                return True
        return False

# Buttons for game states
start_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 70, "START GAME", FONT_MEDIUM, BLUE, (50, 50, 200), WHITE, lambda: globals().update(current_state=GameState.PLAYING_ROUND, round_timer_started=True))
# The menu button is reused and its position updated per state
menu_button = Button(0, 0, 200, 70, "BACK TO MENU", FONT_MEDIUM, BLUE, (50, 50, 200), WHITE, lambda: globals().update(current_state=GameState.MENU))

# Powerup buttons positioned to the right of the grid
# X for Scramble Button to make it visually clear it's limited
scramble_button = Button(SCREEN_WIDTH - 200, 100, 180, 50, "Scramble Grid", FONT_SMALL, GREEN, (0, 200, 0), WHITE, trigger_scramble_grid)
# X for Rewind Button
rewind_button = Button(SCREEN_WIDTH - 200, 170, 180, 50, "Cosmic Rewind", FONT_SMALL, GREEN, (0, 200, 0), WHITE, trigger_cosmic_rewind)
# Stellar Shift button (no X as it's not strictly limited by count in the same way, but by having 2 markers)
shift_button = Button(SCREEN_WIDTH - 200, 240, 180, 50, "Stellar Shift", FONT_SMALL, GREEN, (0, 200, 0), WHITE, trigger_stellar_shift)


# --- State Functions (Adapted from F_GAME_STATES) ---

def run_menu(events):
    """Handles logic and drawing for the main menu state."""
    global current_state
    
    # Ensure game state is fully reset when entering menu
    reset_game()

    # Input Logic
    for event in events:
        start_button.handle_event(event) # start_button's action changes the state
    
    # Drawing
    screen.blit(IMAGES['background'], (0,0))
    title_text = FONT_TITLE.render("COSMIC GRID GUARDIANS", True, YELLOW)
    desc_text = FONT_SMALL.render("Defend your star system! First to win 3 rounds.", True, WHITE)
    
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(desc_text, (SCREEN_WIDTH // 2 - desc_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
    
    start_button.draw(screen)

def run_playing_round(events):
    """Handles logic and drawing for the active Tic-Tac-Toe round."""
    global current_player, winner, winning_line, game_over, player_score, ai_score, ai_active_delay, current_round_time, round_timer_started, stellar_shift_active, stellar_shift_selection

    # Start timer if not already started
    if not round_timer_started:
        round_timer_started = True

    # Time Limit Update
    if round_timer_started and not game_over:
        current_round_time -= clock.get_rawtime() / 1000  # Subtract elapsed time in seconds
        if current_round_time <= 0:
            current_round_time = 0
            # Time's up, AI wins the round (player couldn't finish)
            winner = AI_MARKER
            game_over = True
            ai_score += 1
            if SOUNDS['lose_sound']: SOUNDS['lose_sound'].play()
            current_state = GameState.ROUND_OVER
            print("Time's up! AI wins the round.")

    # Input Logic
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left click
                row, col = get_cell_from_mouse_pos(event.pos)
                if row is not None and col is not None and not game_over:
                    # Stellar Shift Logic - player selecting markers to swap
                    if stellar_shift_active:
                        if board[row][col] == PLAYER_MARKER: # Can only select own markers
                            stellar_shift_selection.append((row, col))
                            if len(stellar_shift_selection) == 2: # Two markers selected, perform swap
                                r1, c1 = stellar_shift_selection[0]
                                r2, c2 = stellar_shift_selection[1]
                                
                                # Perform swap
                                board[r1][c1], board[r2][c2] = board[r2][c2], board[r1][c1]
                                
                                stellar_shift_active = False # Deactivate ability
                                stellar_shift_selection = []
                                current_player = AI_MARKER # After shifting, it's AI's turn
                                print("Stellar Shift complete!")
                                if SOUNDS['marker_place']: SOUNDS['marker_place'].play() # Play a sound for swap
                        else:
                            print("Select only your markers for Stellar Shift.")
                    # Normal marker placement logic
                    elif current_player == PLAYER_MARKER:
                        if place_marker(row, col, PLAYER_MARKER):
                            winning_line = check_win(board, PLAYER_MARKER)
                            if winning_line:
                                winner = PLAYER_MARKER
                                game_over = True
                                player_score += 1
                                if SOUNDS['win_fanfare']: SOUNDS['win_fanfare'].play()
                                current_state = GameState.ROUND_OVER
                            elif check_draw(board):
                                winner = "Draw"
                                game_over = True
                                current_state = GameState.ROUND_OVER
                            else:
                                current_player = AI_MARKER
                                ai_active_delay = pygame.time.get_ticks() + AI_TURN_DELAY_MS # Start AI timer
                                print(f"Player placed marker at ({row},{col}). AI's turn.")
                    else:
                        print("It's not your turn!")
        
        # Handle powerup button events
        scramble_button.handle_event(event)
        rewind_button.handle_event(event)
        shift_button.handle_event(event)

    # AI Turn Logic
    if current_player == AI_MARKER and not game_over:
        if pygame.time.get_ticks() > ai_active_delay:
            ai_row, ai_col = ai_move_nebula_nuisance() # Only Nebula Nuisance for Level 1
            if ai_row is not None:
                place_marker(ai_row, ai_col, AI_MARKER)
                winning_line = check_win(board, AI_MARKER)
                if winning_line:
                    winner = AI_MARKER
                    game_over = True
                    ai_score += 1
                    if SOUNDS['lose_sound']: SOUNDS['lose_sound'].play()
                    current_state = GameState.ROUND_OVER
                elif check_draw(board):
                    winner = "Draw"
                    game_over = True
                    current_state = GameState.ROUND_OVER
                else:
                    current_player = PLAYER_MARKER
                    print(f"AI placed marker at ({ai_row},{ai_col}). Player's turn.")

    # --- Drawing ---
    screen.blit(IMAGES['background'], (0,0))
    draw_grid()
    draw_markers()
    
    # Predictive Insight (Passive Ability - highlights AI's potential winning moves)
    if current_player == PLAYER_MARKER and not game_over:
        ai_potential_wins = get_predictive_insight_moves(AI_MARKER)
        for r, c in ai_potential_wins:
            # Highlight with a subtle border
            cell_x = GRID_OFFSET_X + c * CELL_SIZE
            cell_y = GRID_OFFSET_Y + r * CELL_SIZE
            pygame.draw.rect(screen, PREDICT_INSIGHT_COLOR, (cell_x + 5, cell_y + 5, CELL_SIZE - 10, CELL_SIZE - 10), 3) # Orange border

    # Stellar Shift selection visual
    if stellar_shift_active:
        for r, c in stellar_shift_selection:
            cell_x = GRID_OFFSET_X + c * CELL_SIZE
            cell_y = GRID_OFFSET_Y + r * CELL_SIZE
            pygame.draw.rect(screen, BLUE, (cell_x + 2, cell_y + 2, CELL_SIZE - 4, CELL_SIZE - 4), 5) # Blue border for selected

    if game_over and winning_line:
        highlight_winning_line()

    # Score Display
    player_score_text = FONT_MEDIUM.render(f"Guardian: {player_score}", True, YELLOW)
    ai_score_text = FONT_MEDIUM.render(f"Invader: {ai_score}", True, PURPLE)
    screen.blit(player_score_text, (20, 20))
    screen.blit(ai_score_text, (20, 70))

    # Current player turn indicator
    turn_text = FONT_SMALL.render(f"Turn: {'YOURS (X)' if current_player == PLAYER_MARKER else 'INVADER (O)'}", True, WHITE)
    screen.blit(turn_text, (GRID_OFFSET_X + GRID_WIDTH // 2 - turn_text.get_width() // 2, GRID_OFFSET_Y + GRID_HEIGHT + 20))

    # Round Timer Display
    timer_text = FONT_MEDIUM.render(f"Time: {int(current_round_time)}s", True, WHITE)
    screen.blit(timer_text, (SCREEN_WIDTH - timer_text.get_width() - 20, 20))

    # Powerup buttons and their uses/status
    scramble_button.draw(screen)
    rewind_button.draw(screen)
    shift_button.draw(screen)

    # Display uses/status next to buttons
    scramble_count_text = FONT_TINY.render(f"Uses: {scramble_grid_uses}", True, WHITE)
    rewind_count_text = FONT_TINY.render(f"Uses: {cosmic_rewind_uses}", True, WHITE)
    shift_status_text = FONT_TINY.render(f"Active: {'YES' if stellar_shift_active else 'NO'}", True, WHITE)

    screen.blit(scramble_count_text, (scramble_button.rect.x + scramble_button.rect.width + 10, scramble_button.rect.y + 10))
    screen.blit(rewind_count_text, (rewind_button.rect.x + rewind_button.rect.width + 10, rewind_button.rect.y + 10))
    screen.blit(shift_status_text, (shift_button.rect.x + shift_button.rect.width + 10, shift_button.rect.y + 10))


def run_round_over(events):
    """Handles logic and drawing for the round-over state."""
    global current_state, winner, player_score, ai_score

    # Check for overall game over condition
    if player_score >= ROUNDS_TO_WIN_GAME or ai_score >= ROUNDS_TO_WIN_GAME:
        current_state = GameState.GAME_OVER_SCREEN
        return

    # Input Logic
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                reset_round() # Prepare for next round
                current_state = GameState.PLAYING_ROUND
                return # Exit early to prevent drawing previous state
        menu_button.handle_event(event) # Handle menu button for this state
    
    # Drawing
    screen.blit(IMAGES['background'], (0,0))
    draw_grid()
    draw_markers()
    if winning_line:
        highlight_winning_line()

    if winner == PLAYER_MARKER:
        msg = "GUARDIAN PREVAILS!"
        color = YELLOW
    elif winner == AI_MARKER:
        msg = "INVADER DOMINATES!"
        color = RED
    else: # Draw
        msg = "COSMIC STALEMATE!"
        color = WHITE

    win_text = FONT_HEADER.render(msg, True, color)
    prompt_text = FONT_MEDIUM.render("Press SPACE for Next Round", True, WHITE)
    
    screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
    
    # Adjust menu button position for this screen
    menu_button.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
    menu_button.draw(screen)


def run_game_over_screen(events):
    """Handles logic and drawing for the final game over state."""
    global current_state, player_score, ai_score

    # Input Logic
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: # Restart game
                current_state = GameState.MENU # Go back to menu, which triggers reset_game()
                return
        menu_button.handle_event(event) # Handle menu button for this state
    
    # Drawing
    screen.blit(IMAGES['background'], (0,0))

    if player_score > ai_score:
        final_msg = "GALACTIC VICTORY!"
        final_color = YELLOW
    else:
        final_msg = "STAR SYSTEM LOST!"
        final_color = RED

    final_score_text = FONT_TITLE.render(final_msg, True, final_color)
    score_summary_text = FONT_MEDIUM.render(f"Final Score: Guardian {player_score} - {ai_score} Invader", True, WHITE)
    restart_prompt_text = FONT_SMALL.render("Press 'R' to Play Again", True, WHITE)

    screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(score_summary_text, (SCREEN_WIDTH // 2 - score_summary_text.get_width() // 2, SCREEN_HEIGHT // 2))
    screen.blit(restart_prompt_text, (SCREEN_WIDTH // 2 - restart_prompt_text.get_width() // 2, SCREEN_HEIGHT // 2 + 70))
    
    # Adjust menu button position for this screen
    menu_button.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150)
    menu_button.draw(screen)


# --- Main Game Loop (from A_CORE_SETUP & F_GAME_STATES) ---
running = True
while running:
    events = pygame.event.get() # Collect all events once per frame
    for event in events:
        if event.type == pygame.QUIT:
            running = False
            
    # State Logic - call the appropriate function based on the current game state
    if current_state == GameState.MENU:
        run_menu(events)
    elif current_state == GameState.PLAYING_ROUND:
        run_playing_round(events)
    elif current_state == GameState.ROUND_OVER:
        run_round_over(events)
    elif current_state == GameState.GAME_OVER_SCREEN:
        run_game_over_screen(events)
    
    pygame.display.flip() # Update the full display surface to the screen
    clock.tick(FPS) # Cap the frame rate

# --- Cleanup ---
pygame.quit()
sys.exit()
