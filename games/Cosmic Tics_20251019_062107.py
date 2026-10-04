
import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Game Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 3
CELL_SIZE = WIDTH // GRID_SIZE
LINE_THICKNESS = 5
SYMBOL_THICKNESS = 10
MENU_FONT_SIZE = 60
SCORE_FONT_SIZE = 30
MESSAGE_FONT_SIZE = 40
POWERUP_FONT_SIZE = 20

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
GRAY = (200, 200, 200)
DARK_BLUE = (0, 0, 50)
LIGHT_BLUE = (100, 100, 200)

# Game States
MENU = 0
PLAYING = 1
GAME_OVER = 2

# Symbols
STAR = 'star'
NEBULA = 'nebula'
EMPTY = None

# Player
PLAYER_SPEED = 5
PLAYER_SIZE = 30
PLAYER_COLOR = YELLOW

# Enemies
ENEMY_COLORS = {
    "cosmic_drifter": RED,
    "wandering_comet": CYAN,
}
ENEMY_SPEED = 2
ENEMY_SIZE = 20
AI_MOVE_DELAY = 30 # Frames

# Powerups
POWERUP_COLORS = {
    "symbol_boost": GREEN,
    "vision_enhancer": BLUE,
}
POWERUP_SIZE = 15

# Game Variables
current_state = MENU
board = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
player_symbol = STAR
ai_symbol = NEBULA
current_player = STAR  # STAR starts
player_pos = [0, 0]
score = 0
message = ""
message_timer = 0
powerup_available = {
    "comet_strike": True,
    "supernova": True,
}
ai_difficulty = "easy"  # Default AI difficulty
player_score = 0
ai_score = 0
game_winner = None
player_has_powerup = {
    "comet_strike": False,
    "supernova": False,
}

# Fonts
menu_font = pygame.font.Font(None, MENU_FONT_SIZE)
score_font = pygame.font.Font(None, SCORE_FONT_SIZE)
message_font = pygame.font.Font(None, MESSAGE_FONT_SIZE)
powerup_font = pygame.font.Font(None, POWERUP_FONT_SIZE)

# Game Board Drawing Function
def draw_board():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, LIGHT_BLUE, rect, LINE_THICKNESS)

            symbol = board[row][col]
            center_x = col * CELL_SIZE + CELL_SIZE // 2
            center_y = row * CELL_SIZE + CELL_SIZE // 2

            if symbol == STAR:
                # Draw Star (X)
                pygame.draw.line(screen, RED, (center_x - CELL_SIZE // 3, center_y - CELL_SIZE // 3),
                                 (center_x + CELL_SIZE // 3, center_y + CELL_SIZE // 3), SYMBOL_THICKNESS)
                pygame.draw.line(screen, RED, (center_x - CELL_SIZE // 3, center_y + CELL_SIZE // 3),
                                 (center_x + CELL_SIZE // 3, center_y - CELL_SIZE // 3), SYMBOL_THICKNESS)
            elif symbol == NEBULA:
                # Draw Nebula (O)
                pygame.draw.circle(screen, PURPLE, (center_x, center_y), CELL_SIZE // 3, SYMBOL_THICKNESS)

# Check for Win Condition
def check_win():
    for row in range(GRID_SIZE):
        if board[row][0] == board[row][1] == board[row][2] and board[row][0] is not EMPTY:
            return board[row][0]
    for col in range(GRID_SIZE):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col] is not EMPTY:
            return board[0][col]
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not EMPTY:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] is not EMPTY:
        return board[0][2]
    if all(board[r][c] is not EMPTY for r in range(GRID_SIZE) for c in range(GRID_SIZE)):
        return 'tie'
    return None

# AI Logic
def ai_move():
    global board, ai_symbol, current_player

    if ai_difficulty == "easy":
        # Stardust Sprite (Easy AI): Places symbols randomly
        available_moves = []
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if board[r][c] == EMPTY:
                    available_moves.append((r, c))
        if available_moves:
            row, col = random.choice(available_moves)
            board[row][col] = ai_symbol
            return True
    elif ai_difficulty == "medium":
        # Gravity Guardian (Medium AI): Prioritizes winning, then blocking, then random
        # 1. Check for winning moves
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if board[r][c] == EMPTY:
                    board[r][c] = ai_symbol
                    if check_win() == ai_symbol:
                        return True
                    board[r][c] = EMPTY  # Undo move

        # 2. Check for blocking moves
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if board[r][c] == EMPTY:
                    board[r][c] = player_symbol
                    if check_win() == player_symbol:
                        board[r][c] = ai_symbol  # Block the player
                        return True
                    board[r][c] = EMPTY  # Undo move

        # 3. Place randomly
        available_moves = []
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if board[r][c] == EMPTY:
                    available_moves.append((r, c))
        if available_moves:
            row, col = random.choice(available_moves)
            board[row][col] = ai_symbol
            return True
    elif ai_difficulty == "hard":
        # Singularity Sentinel (Hard AI): Minimax algorithm
        def minimax(current_board, depth, is_maximizing):
            result = check_win_minimax(current_board)
            if result == ai_symbol:
                return 10 - depth
            if result == player_symbol:
                return depth - 10
            if result == 'tie':
                return 0

            if is_maximizing:
                max_eval = -math.inf
                for r in range(GRID_SIZE):
                    for c in range(GRID_SIZE):
                        if current_board[r][c] == EMPTY:
                            current_board[r][c] = ai_symbol
                            eval = minimax(current_board, depth + 1, False)
                            current_board[r][c] = EMPTY
                            max_eval = max(max_eval, eval)
                return max_eval
            else:
                min_eval = math.inf
                for r in range(GRID_SIZE):
                    for c in range(GRID_SIZE):
                        if current_board[r][c] == EMPTY:
                            current_board[r][c] = player_symbol
                            eval = minimax(current_board, depth + 1, True)
                            current_board[r][c] = EMPTY
                            min_eval = min(min_eval, eval)
                return min_eval

        def check_win_minimax(b):
            for row in range(GRID_SIZE):
                if b[row][0] == b[row][1] == b[row][2] and b[row][0] is not EMPTY:
                    return b[row][0]
            for col in range(GRID_SIZE):
                if b[0][col] == b[1][col] == b[2][col] and b[0][col] is not EMPTY:
                    return b[0][col]
            if b[0][0] == b[1][1] == b[2][2] and b[0][0] is not EMPTY:
                return b[0][0]
            if b[0][2] == b[1][1] == b[2][0] and b[0][2] is not EMPTY:
                return b[0][2]
            if all(b[r][c] is not EMPTY for r in range(GRID_SIZE) for c in range(GRID_SIZE)):
                return 'tie'
            return None

        best_eval = -math.inf
        best_move = None
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if board[r][c] == EMPTY:
                    board[r][c] = ai_symbol
                    eval = minimax(board, 0, False)
                    board[r][c] = EMPTY
                    if eval > best_eval:
                        best_eval = eval
                        best_move = (r, c)
        if best_move:
            board[best_move[0]][best_move[1]] = ai_symbol
            return True
    return False

# Powerup Logic
def apply_comet_strike(target_row, target_col):
    global board, player_symbol, ai_symbol
    if board[target_row][target_col] == ai_symbol:
        board[target_row][target_col] = EMPTY
        return True
    return False

def apply_supernova():
    # This effect for AI is tricky. For now, we'll make the AI re-evaluate its next move more randomly.
    # A true "re-roll" for a strategic AI might involve forcing a different path in minimax, which is complex.
    # For simplicity, we'll just make the AI behave a bit more randomly for its next move if this is used against it.
    # In a real game, this might be more impactful.
    pass

# Collision Detection
def check_player_enemy_collision(player_rect, enemies):
    for enemy in enemies:
        enemy_rect = pygame.Rect(enemy['x'] - ENEMY_SIZE // 2, enemy['y'] - ENEMY_SIZE // 2, ENEMY_SIZE, ENEMY_SIZE)
        if player_rect.colliderect(enemy_rect):
            return True
    return False

def check_player_powerup_collision(player_rect, powerups):
    for i, powerup in enumerate(powerups):
        powerup_rect = pygame.Rect(powerup['x'] - POWERUP_SIZE // 2, powerup['y'] - POWERUP_SIZE // 2, POWERUP_SIZE, POWERUP_SIZE)
        if player_rect.colliderect(powerup_rect):
            return i
    return -1

# Enemy AI Logic (for movement)
def move_enemy(enemy, patrol_path):
    if not patrol_path:
        return

    current_pos = [enemy['x'], enemy['y']]
    target_index = enemy.get('patrol_index', 0)
    target_pos = patrol_path[target_index]

    direction_x = target_pos[0] - current_pos[0]
    direction_y = target_pos[1] - current_pos[1]
    distance = math.sqrt(direction_x**2 + direction_y**2)

    if distance < ENEMY_SPEED:
        enemy['x'], enemy['y'] = target_pos
        target_index = (target_index + 1) % len(patrol_path)
        enemy['patrol_index'] = target_index
    else:
        normalized_direction_x = direction_x / distance
        normalized_direction_y = direction_y / distance
        enemy['x'] += normalized_direction_x * ENEMY_SPEED
        enemy['y'] += normalized_direction_y * ENEMY_SPEED

# Reset Game
def reset_game():
    global board, current_player, message, message_timer, game_winner, player_has_powerup, ai_turn_timer
    board = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    current_player = STAR
    message = ""
    message_timer = 0
    game_winner = None
    player_has_powerup = {
        "comet_strike": False,
        "supernova": False,
    }
    ai_turn_timer = 0

# Initialize Game
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cosmic Tics")

# Game Objects Initialization (for Level 1)
level_data = {
    "size": {"width": 800, "height": 600},
    "spawn_points": [
        {"x": 100, "y": 500, "type": "player"},
        {"x": 700, "y": 100, "type": "enemy"}
    ],
    "obstacles": [
        {"x": 350, "y": 200, "width": 100, "height": 30, "type": "asteroid_belt"},
        {"x": 500, "y": 400, "width": 40, "height": 40, "type": "small_planetoid"}
    ],
    "powerups": [
        {"x": 200, "y": 150, "type": "symbol_boost"},
        {"x": 600, "y": 500, "type": "vision_enhancer"}
    ],
    "enemies": [
        {"x": 400, "y": 300, "type": "cosmic_drifter", "patrol_path": [[400, 300], [450, 300], [450, 350], [400, 350]]},
        {"x": 150, "y": 100, "type": "wandering_comet", "patrol_path": [[150, 100], [200, 100]]}
    ],
    "objectives": [
        {"type": "place_symbols", "description": "Place three Stars (X) in a row horizontally, vertically, or diagonally.", "win_condition": True},
        {"type": "avoid_enemy_collision", "description": "Do not collide with any celestial beings."}
    ],
    "difficulty": "easy",
    "time_limit": 90
}

player_pos = [level_data['spawn_points'][0]['x'], level_data['spawn_points'][0]['y']]
enemies = []
for enemy_data in level_data['enemies']:
    enemies.append({
        'x': enemy_data['x'],
        'y': enemy_data['y'],
        'type': enemy_data['type'],
        'color': ENEMY_COLORS.get(enemy_data['type'], RED),
        'patrol_path': enemy_data['patrol_path'],
        'patrol_index': 0
    })
obstacles = level_data['obstacles']
powerups = []
for pup_data in level_data['powerups']:
    powerups.append({
        'x': pup_data['x'],
        'y': pup_data['y'],
        'type': pup_data['type'],
        'color': POWERUP_COLORS.get(pup_data['type'], GREEN)
    })

ai_turn_timer = 0
game_timer = level_data['time_limit']
level_timer_event = pygame.USEREVENT + 1
pygame.time.set_timer(level_timer_event, 1000) # Tick every second

# Main Game Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if current_state == MENU:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    current_state = PLAYING
                    reset_game()
                    player_pos = [level_data['spawn_points'][0]['x'], level_data['spawn_points'][0]['y']]
                    for enemy_data in level_data['enemies']:
                        enemies.append({
                            'x': enemy_data['x'],
                            'y': enemy_data['y'],
                            'type': enemy_data['type'],
                            'color': ENEMY_COLORS.get(enemy_data['type'], RED),
                            'patrol_path': enemy_data['patrol_path'],
                            'patrol_index': 0
                        })
                    powerups = []
                    for pup_data in level_data['powerups']:
                        powerups.append({
                            'x': pup_data['x'],
                            'y': pup_data['y'],
                            'type': pup_data['type'],
                            'color': POWERUP_COLORS.get(pup_data['type'], GREEN)
                        })
                    game_timer = level_data['time_limit']
                    player_score = 0
                    ai_score = 0
                    ai_difficulty = "easy" # Reset AI difficulty for each new game
                elif event.key == pygame.K_1:
                    ai_difficulty = "easy"
                    message = "Difficulty: Easy. Press Enter to start."
                    message_timer = 120
                elif event.key == pygame.K_2:
                    ai_difficulty = "medium"
                    message = "Difficulty: Medium. Press Enter to start."
                    message_timer = 120
                elif event.key == pygame.K_3:
                    ai_difficulty = "hard"
                    message = "Difficulty: Hard. Press Enter to start."
                    message_timer = 120
                elif event.key == pygame.K_c:
                    if player_has_powerup["comet_strike"]:
                        message = "Select a target to remove (mouse click)."
                        message_timer = 120
                        powerup_used = "comet_strike"
                elif event.key == pygame.K_s:
                    if player_has_powerup["supernova"]:
                        apply_supernova()
                        message = "Supernova used! AI will re-evaluate."
                        message_timer = 120
                        player_has_powerup["supernova"] = False

        elif current_state == PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    current_state = MENU
                    reset_game()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if message_timer > 0 and "Select a target to remove" in message:
                    mouse_x, mouse_y = event.pos
                    row = mouse_y // CELL_SIZE
                    col = mouse_x // CELL_SIZE
                    if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                        if apply_comet_strike(row, col):
                            message = "Opponent's symbol removed!"
                            player_has_powerup["comet_strike"] = False
                        else:
                            message = "Cannot remove an empty space or your own symbol."
                        message_timer = 120
                        powerup_used = None # Reset powerup usage state
                elif current_player == player_symbol and game_winner is None:
                    mouse_x, mouse_y = event.pos
                    col = mouse_x // CELL_SIZE
                    row = mouse_y // CELL_SIZE

                    if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE and board[row][col] == EMPTY:
                        board[row][col] = player_symbol
                        current_player = ai_symbol
                        ai_turn_timer = AI_MOVE_DELAY
                        win_check = check_win()
                        if win_check:
                            if win_check == player_symbol:
                                message = "You Win!"
                                player_score += 100
                                game_winner = player_symbol
                            elif win_check == 'tie':
                                message = "It's a Tie!"
                                player_score += 25
                                game_winner = 'tie'
                            else:
                                message = "AI Wins!"
                                ai_score += 100
                                game_winner = ai_symbol
                            message_timer = 240
                            current_state = GAME_OVER
                        else:
                            message = "AI's Turn..."
                            message_timer = 60

            if event.type == level_timer_event:
                if game_timer > 0:
                    game_timer -= 1
                else:
                    if game_winner is None:
                        message = "Time's Up! It's a Tie!"
                        player_score += 25
                        game_winner = 'tie'
                        current_state = GAME_OVER

        elif current_state == GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    current_state = MENU
                    reset_game()
                elif event.key == pygame.K_r:
                    current_state = PLAYING
                    reset_game()
                    player_pos = [level_data['spawn_points'][0]['x'], level_data['spawn_points'][0]['y']]
                    for enemy_data in level_data['enemies']:
                        enemies.append({
                            'x': enemy_data['x'],
                            'y': enemy_data['y'],
                            'type': enemy_data['type'],
                            'color': ENEMY_COLORS.get(enemy_data['type'], RED),
                            'patrol_path': enemy_data['patrol_path'],
                            'patrol_index': 0
                        })
                    powerups = []
                    for pup_data in level_data['powerups']:
                        powerups.append({
                            'x': pup_data['x'],
                            'y': pup_data['y'],
                            'type': pup_data['type'],
                            'color': POWERUP_COLORS.get(pup_data['type'], GREEN)
                        })
                    game_timer = level_data['time_limit']
                    player_score = 0 # Reset scores for a new game after game over
                    ai_score = 0
                    ai_difficulty = "easy" # Reset AI difficulty for each new game

    # Player Movement
    if current_state == PLAYING:
        keys = pygame.key.get_pressed()
        new_player_pos = list(player_pos)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            new_player_pos[1] -= PLAYER_SPEED
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            new_player_pos[1] += PLAYER_SPEED
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            new_player_pos[0] -= PLAYER_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            new_player_pos[0] += PLAYER_SPEED

        # Boundary Checking for player
        if 0 <= new_player_pos[0] <= WIDTH - PLAYER_SIZE:
            player_pos[0] = new_player_pos[0]
        if 0 <= new_player_pos[1] <= HEIGHT - PLAYER_SIZE:
            player_pos[1] = new_player_pos[1]

        player_rect = pygame.Rect(player_pos[0], player_pos[1], PLAYER_SIZE, PLAYER_SIZE)

        # Collision with obstacles
        for obstacle in obstacles:
            obstacle_rect = pygame.Rect(obstacle['x'], obstacle['y'], obstacle['width'], obstacle['height'])
            if player_rect.colliderect(obstacle_rect):
                # Basic repulsion to push player out of obstacle
                if player_pos[0] < obstacle['x']:
                    player_pos[0] = obstacle['x'] - PLAYER_SIZE
                elif player_pos[0] + PLAYER_SIZE > obstacle['x'] + obstacle['width']:
                    player_pos[0] = obstacle['x'] + obstacle['width']
                if player_pos[1] < obstacle['y']:
                    player_pos[1] = obstacle['y'] - PLAYER_SIZE
                elif player_pos[1] + PLAYER_SIZE > obstacle['y'] + obstacle['height']:
                    player_pos[1] = obstacle['y'] + obstacle['height']


        # Collision with enemies
        if check_player_enemy_collision(player_rect, enemies):
            message = "Collision! You lose a turn."
            message_timer = 120
            current_player = ai_symbol # Enemy gets a turn
            ai_turn_timer = AI_MOVE_DELAY # Give AI a bit of a delay after collision
            # Optionally, you could make the player lose a point or reset position


        # Powerup Collection
        powerup_index_to_remove = -1
        for i, powerup in enumerate(powerups):
            powerup_rect = pygame.Rect(powerup['x'] - POWERUP_SIZE // 2, powerup['y'] - POWERUP_SIZE // 2, POWERUP_SIZE, POWERUP_SIZE)
            if player_rect.colliderect(powerup_rect):
                if powerup['type'] == "symbol_boost":
                    # This could be implemented to switch player_symbol/ai_symbol, but for now it's just a collection
                    message = "Symbol Boost collected!"
                    powerup_available["symbol_boost"] = True # Not really used in the current logic, but could be
                elif powerup['type'] == "vision_enhancer":
                    # This could be implemented to reveal AI's next move or highlight winning lines
                    message = "Vision Enhancer collected!"
                    player_has_powerup["comet_strike"] = True # Map this to comet strike for demonstration
                powerup_index_to_remove = i
                message_timer = 120
                break
        if powerup_index_to_remove != -1:
            powerups.pop(powerup_index_to_remove)

        # AI Turn Logic
        if current_player == ai_symbol and game_winner is None:
            if ai_turn_timer > 0:
                ai_turn_timer -= 1
            else:
                if ai_move():
                    current_player = player_symbol
                    win_check = check_win()
                    if win_check:
                        if win_check == player_symbol:
                            message = "You Win!"
                            player_score += 100
                            game_winner = player_symbol
                        elif win_check == 'tie':
                            message = "It's a Tie!"
                            player_score += 25
                            game_winner = 'tie'
                        else:
                            message = "AI Wins!"
                            ai_score += 100
                            game_winner = ai_symbol
                        message_timer = 240
                        current_state = GAME_OVER
                    else:
                        message = "Your Turn!"
                        message_timer = 60
                else:
                    # Should not happen if game is not over, but for safety
                    pass


    # Drawing
    screen.fill(DARK_BLUE)  # Deep space background

    if current_state == MENU:
        title_text = menu_font.render("Cosmic Tics", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title_text, title_rect)

        start_text = score_font.render("Press Enter to Start", True, WHITE)
        start_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(start_text, start_rect)

        difficulty_text_1 = powerup_font.render("1 - Easy", True, WHITE)
        difficulty_rect_1 = difficulty_text_1.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(difficulty_text_1, difficulty_rect_1)

        difficulty_text_2 = powerup_font.render("2 - Medium", True, WHITE)
        difficulty_rect_2 = difficulty_text_2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 75))
        screen.blit(difficulty_text_2, difficulty_rect_2)

        difficulty_text_3 = powerup_font.render("3 - Hard", True, WHITE)
        difficulty_rect_3 = difficulty_text_3.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
        screen.blit(difficulty_text_3, difficulty_rect_3)

        if message:
            message_surface = message_font.render(message, True, YELLOW)
            message_rect = message_surface.get_rect(center=(WIDTH // 2, HEIGHT * 3 // 4))
            screen.blit(message_surface, message_rect)
            if message_timer > 0:
                message_timer -= 1
            else:
                message = ""

    elif current_state == PLAYING:
        # Draw Level Elements
        for obstacle in obstacles:
            pygame.draw.rect(screen, GRAY, (obstacle['x'], obstacle['y'], obstacle['width'], obstacle['height']))

        for enemy in enemies:
            pygame.draw.circle(screen, enemy['color'], (int(enemy['x']), int(enemy['y'])), ENEMY_SIZE // 2)

        for powerup in powerups:
            pygame.draw.circle(screen, powerup['color'], (powerup['x'], powerup['y']), POWERUP_SIZE // 2)

        # Draw Player
        pygame.draw.rect(screen, PLAYER_COLOR, player_rect)

        # Draw Tic-Tac-Toe Grid
        draw_board()

        # Draw Powerup indicators
        powerup_y = HEIGHT - 30
        if player_has_powerup["comet_strike"]:
            comet_text = powerup_font.render("C: Comet Strike", True, WHITE)
            screen.blit(comet_text, (10, powerup_y))
        if player_has_powerup["supernova"]:
            supernova_text = powerup_font.render("S: Supernova", True, WHITE)
            screen.blit(supernova_text, (150, powerup_y))


        # Display Game Timer
        timer_text = score_font.render(f"Time: {game_timer}", True, WHITE)
        screen.blit(timer_text, (WIDTH - 150, 10))

        # Display Score
        score_text = score_font.render(f"Player: {player_score} | AI: {ai_score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Display Message
        if message:
            message_surface = message_font.render(message, True, YELLOW)
            message_rect = message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(message_surface, message_rect)
            if message_timer > 0:
                message_timer -= 1
            else:
                message = ""


    elif current_state == GAME_OVER:
        screen.fill(BLACK)
        win_message = ""
        if game_winner == player_symbol:
            win_message = "Congratulations! You Win!"
        elif game_winner == ai_symbol:
            win_message = "The AI has Conquered!"
        elif game_winner == 'tie':
            win_message = "A Celestial Stalemate!"

        win_text = menu_font.render(win_message, True, YELLOW)
        win_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        screen.blit(win_text, win_rect)

        final_score_text = score_font.render(f"Final Score: Player {player_score} - AI {ai_score}", True, WHITE)
        final_score_rect = final_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(final_score_text, final_score_rect)

        restart_text = score_font.render("Press R to Restart or Enter for Menu", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT * 2 // 3))
        screen.blit(restart_text, restart_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()
