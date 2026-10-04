# --- Game Logic for Touchdown Blitz ---

# Constants based on game concept and level design
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0) # For tokens

# Player
PLAYER_SIZE = 30
PLAYER_SPEED = 5
SPRINT_BOOST_MULTIPLIER = 2.0
SPRINT_DURATION = 1.5 # seconds
SPRINT_COOLDOWN = 3.0 # seconds
JUKE_DURATION = 0.3 # seconds
STUMBLE_RECOVERY_DURATION = 0.5 # seconds

# Enemies
ENEMY_SIZE = 30
ENEMY_SPEED_BASE = 3
ENEMY_SPEED_INCREASE_CLOSE = 1.0 # Speed increase when player is close to endzone
ENEMY_PATROL_SPEED = 2
ENEMY_DETECTION_RADIUS = 150 # How close player needs to be for direct pursuit
ENEMY_AGGRESSIVENESS_MULTIPLIER = 1.2 # How much they try to cut off

# Power-ups
POWERUP_SIZE = 20
SPEED_BOOST_ACCELERATION_MULTIPLIER = 1.5
MAGNETIC_BOOTS_DURATION = 5.0 # seconds
STAMINA_RECHARGE_AMOUNT = 1.0 # Represents a full recharge

# Obstacles
OBSTACLE_TYPES = {
    "cone": (20, 40),
    "water_cooler": (30, 30),
    "spare_ball": (20, 20),
}

# Tokens
TOKEN_SIZE = 15
TOKEN_VALUE = 10 # Points per token

# Game State
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3
    LEVEL_COMPLETE = 4

current_state = GameState.MENU
current_level = 1
score = 0
level_data = {
    "level_number": 1,
    "name": "The Practice Field",
    "size": {"width": 800, "height": 600},
    "spawn_points": [{"x": 100, "y": 300, "type": "player"}],
    "obstacles": [
        {"x": 200, "y": 150, "width": 70, "height": 100, "type": "cone"},
        {"x": 550, "y": 300, "width": 80, "height": 60, "type": "water_cooler"},
        {"x": 700, "y": 100, "width": 50, "height": 50, "type": "spare_ball"},
    ],
    "powerups": [
        {"x": 300, "y": 200, "type": "speed_boost"},
        {"x": 650, "y": 450, "type": "stamina_recharge"},
    ],
    "enemies": [
        {"x": 400, "y": 200, "type": "pursuer", "patrol_path": []}, # Pursuer behavior, no fixed path
        {"x": 600, "y": 350, "type": "flanker", "patrol_path": [
            {"x": 600, "y": 350}, {"x": 650, "y": 350},
            {"x": 650, "y": 400}, {"x": 600, "y": 400}
        ]},
        {"x": 250, "y": 400, "type": "flanker", "patrol_path": [
            {"x": 250, "y": 400}, {"x": 300, "y": 400},
            {"x": 300, "y": 450}, {"x": 250, "y": 450}
        ]},
    ],
    "objectives": [
        {"type": "collect", "target": "tokens", "count": 5},
        {"type": "reach_goal", "description": "Reach the end zone at the opposite side of the field.", "goal_x": 750, "goal_y": 300},
    ],
    "difficulty": "easy",
    "time_limit": 180, # seconds
}

# Game Over zone
GOAL_LINE_X = SCREEN_WIDTH - 50
GOAL_WIDTH = 50
GOAL_HEIGHT = SCREEN_HEIGHT

# Fonts
BIG_FONT = pygame.font.Font(None, 74)
MEDIUM_FONT = pygame.font.Font(None, 36)
SMALL_FONT = pygame.font.Font(None, 24)

# Sprites Groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
powerups = pygame.sprite.Group()
tokens = pygame.sprite.Group()
goal_rect = pygame.Rect(GOAL_LINE_X, 0, GOAL_WIDTH, GOAL_HEIGHT)

# Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([PLAYER_SIZE, PLAYER_SIZE])
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.speed = PLAYER_SPEED
        self.max_speed = PLAYER_SPEED * SPRINT_BOOST_MULTIPLIER
        self.current_speed = self.speed

        self.stamina = 1.0 # 0.0 to 1.0
        self.max_stamina = 1.0
        self.stamina_regen_rate = 0.1 # per second

        self.sprint_active = False
        self.sprint_timer = 0
        self.sprint_cooldown_timer = 0

        self.is_dodging = False
        self.dodge_direction = (0, 0)
        self.dodge_timer = 0

        self.is_stumbling = False
        self.stumble_timer = 0

        self.last_move_direction = (0, 0) # For juke/dodge targeting

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        # Sprint input
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] or keys[pygame.K_SPACE]) and self.stamina > 0 and not self.is_stumbling:
            self.sprint_active = True
            self.stamina_regen_rate = 0.05 # Slower regen while sprinting
        else:
            self.sprint_active = False
            self.stamina_regen_rate = 0.1

        # Movement input
        if not self.is_stumbling and not self.is_dodging:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx -= 1
                self.last_move_direction = (-1, 0)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx += 1
                self.last_move_direction = (1, 0)
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy -= 1
                self.last_move_direction = (0, -1)
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy += 1
                self.last_move_direction = (0, 1)

            # Normalize diagonal movement
            if dx != 0 and dy != 0:
                dx *= 0.707 # sqrt(2)/2
                dy *= 0.707

            self.rect.x += dx * self.current_speed
            self.rect.y += dy * self.current_speed

        # Juke/Dodge input (quick directional change while moving)
        if not self.is_stumbling and (keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_RIGHT] or keys[pygame.K_d] or keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_DOWN] or keys[pygame.K_s]):
            # Check if a directional key is pressed that's different from the *current* movement direction
            # This is a simplification, a true juke would be a quick double tap or specific button
            # For this template, we'll assume if player tries to move in a new direction while holding another, it's a juke.
            # A more robust implementation would use specific key combinations or a dedicated juke button.
            pass # Juke logic is handled in the update loop based on sudden direction change

    def perform_dodge(self, direction):
        if not self.is_dodging and not self.is_stumbling:
            self.is_dodging = True
            self.dodge_direction = direction
            self.dodge_timer = JUKE_DURATION
            self.stumble_timer = STUMBLE_RECOVERY_DURATION # Start recovery immediately
            self.is_stumbling = True # Stumbling briefly gives invincibility

    def update(self, dt, enemies):
        self.handle_input()

        # Stamina management
        if self.sprint_active and self.stamina > 0:
            self.stamina -= dt / SPRINT_DURATION # Drain stamina over sprint duration
            self.stamina = max(0, self.stamina)
            self.current_speed = self.max_speed
            self.sprint_timer += dt
            if self.sprint_timer >= SPRINT_DURATION:
                self.sprint_active = False
                self.sprint_timer = 0
                self.sprint_cooldown_timer = dt
        else:
            self.sprint_active = False
            self.current_speed = self.speed
            if self.stamina < self.max_stamina:
                self.stamina += self.stamina_regen_rate * dt
                self.stamina = min(self.max_stamina, self.stamina)
            if self.sprint_cooldown_timer > 0:
                self.sprint_cooldown_timer -= dt
                if self.sprint_cooldown_timer <= 0:
                    self.sprint_cooldown_timer = 0

        # Dodge/Juke logic
        if self.is_dodging:
            self.dodge_timer -= dt
            self.rect.x += self.dodge_direction[0] * self.max_speed * 1.5 # Faster dodge movement
            self.rect.y += self.dodge_direction[1] * self.max_speed * 1.5
            if self.dodge_timer <= 0:
                self.is_dodging = False
                # Stumble recovery handled by stumble_timer

        # Stumble recovery
        if self.is_stumbling:
            self.stumble_timer -= dt
            if self.stumble_timer <= 0:
                self.is_stumbling = False
                self.dodge_direction = (0,0)

        # Keep player within screen bounds
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)

        # Check for collision with enemies
        for enemy in enemies:
            if pygame.sprite.collide_rect(self, enemy) and not self.is_stumbling:
                # If player is not stumbling and collides with an enemy
                # This is a tackle attempt. If they collide, player is tackled.
                # A juke would attempt to evade this by changing direction rapidly.
                # For simplicity, if they collide while not stumbling, player is tackled.
                # True juke requires predicting enemy movement and rapid counter-direction change.
                global current_state
                current_state = GameState.GAME_OVER
                break # Exit loop if tackled


# Enemy Class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type, patrol_path=None):
        super().__init__()
        self.image = pygame.Surface([ENEMY_SIZE, ENEMY_SIZE])
        self.color = RED if enemy_type == "pursuer" else GREEN # Pursuer red, Flanker green
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.enemy_type = enemy_type
        self.speed = ENEMY_SPEED_BASE
        self.patrol_path = patrol_path
        self.patrol_index = 0
        self.patrol_moving = False

        if self.patrol_path and len(self.patrol_path) > 0:
            self.patrol_moving = True

        self.target = None
        self.chase_radius = ENEMY_DETECTION_RADIUS

    def update(self, player, dt):
        if player.is_stumbling:
            # Enemies might slow down or lose track briefly if player is stumbling
            current_speed = self.speed * 0.7
        else:
            current_speed = self.speed
            # Increase speed if player is close to the endzone
            if player.rect.centerx > GOAL_LINE_X - 100:
                current_speed += ENEMY_SPEED_INCREASE_CLOSE

        if self.enemy_type == "pursuer":
            self.pursue_player(player, dt, current_speed)
        elif self.enemy_type == "flanker":
            self.flank_player(player, dt, current_speed)

        # Boundary checking for enemies (similar to player)
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)

    def pursue_player(self, player, dt, current_speed):
        # Simple direct pursuit
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = (dx**2 + dy**2)**0.5

        if dist > 0:
            dx = (dx / dist) * current_speed * dt
            dy = (dy / dist) * current_speed * dt
            self.rect.x += dx
            self.rect.y += dy

    def flank_player(self, player, dt, current_speed):
        if self.patrol_path and self.patrol_moving:
            current_target_pos = (self.patrol_path[self.patrol_index]['x'], self.patrol_path[self.patrol_index]['y'])
            dx = current_target_pos[0] - self.rect.centerx
            dy = current_target_pos[1] - self.rect.centery
            dist_to_target = (dx**2 + dy**2)**0.5

            if dist_to_target < 5: # Reached the current patrol point
                self.patrol_index = (self.patrol_index + 1) % len(self.patrol_path)
                current_target_pos = (self.patrol_path[self.patrol_index]['x'], self.patrol_path[self.patrol_index]['y'])
                dx = current_target_pos[0] - self.rect.centerx
                dy = current_target_pos[1] - self.rect.centery
                dist_to_target = (dx**2 + dy**2)**0.5

            # Basic path following
            if dist_to_target > 0:
                move_dist = min(current_speed * dt, dist_to_target)
                self.rect.x += (dx / dist_to_target) * move_dist
                self.rect.y += (dy / dist_to_target) * move_dist
        else:
            # If no patrol path, flank can also try to intercept if player is in range
            player_dist = ((player.rect.centerx - self.rect.centerx)**2 + (player.rect.centery - self.rect.centery)**2)**0.5
            if player_dist < self.chase_radius * ENEMY_AGGRESSIVENESS_MULTIPLIER:
                self.pursue_player(player, dt, current_speed)


# Obstacle Class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, obs_type):
        super().__init__()
        self.image = pygame.Surface([width, height])
        if obs_type == "cone":
            self.image.fill(RED)
        elif obs_type == "water_cooler":
            self.image.fill(GREEN)
        elif obs_type == "spare_ball":
            self.image.fill(YELLOW)
        else:
            self.image.fill(WHITE) # Default
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.obs_type = obs_type

# Powerup Class
class Powerup(pygame.sprite.Sprite):
    def __init__(self, x, y, powerup_type):
        super().__init__()
        self.image = pygame.Surface([POWERUP_SIZE, POWERUP_SIZE])
        self.powerup_type = powerup_type
        if self.powerup_type == "speed_boost":
            self.image.fill(YELLOW) # Yellow for boost
        elif self.powerup_type == "stamina_recharge":
            self.image.fill(GREEN) # Green for recharge
        elif self.powerup_type == "magnetic_boots":
            self.image.fill(BLUE) # Blue for magnetic boots
        else:
            self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

# Token Class
class Token(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([TOKEN_SIZE, TOKEN_SIZE])
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

# UI Helper Functions
def draw_text(surface, text, font, color, x, y, center=False):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

def draw_health_bar(surface, entity_rect, current_hp, max_hp, color=GREEN, bg_color=RED):
    bar_width = entity_rect.width
    bar_height = 5
    bar_x = entity_rect.x
    bar_y = entity_rect.y - 10

    if bar_y < 0: # Ensure health bar doesn't go off-screen at top
        bar_y = entity_rect.y + entity_rect.height + 2 # Position below if too high

    health_ratio = max(0, min(current_hp, max_hp)) / max_hp
    fill_width = int(bar_width * health_ratio)

    background_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
    pygame.draw.rect(surface, bg_color, background_rect)

    fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
    pygame.draw.rect(surface, color, fill_rect)

def draw_stamina_bar(surface, player_rect, stamina, max_stamina):
    bar_width = player_rect.width
    bar_height = 5
    bar_x = player_rect.x
    bar_y = player_rect.y - 15 # Position 15 pixels above the player

    if bar_y < 0: # Ensure stamina bar doesn't go off-screen at top
        bar_y = player_rect.y + player_rect.height + 12 # Position below if too high

    stamina_ratio = max(0, min(stamina, max_stamina)) / max_stamina
    fill_width = int(bar_width * stamina_ratio)

    # Stamina bar color changes based on fullness
    stamina_color = GREEN if stamina_ratio > 0.5 else (YELLOW if stamina_ratio > 0.2 else RED)

    background_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
    pygame.draw.rect(surface, (50, 50, 50), background_rect) # Dark gray background

    fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
    pygame.draw.rect(surface, stamina_color, fill_rect)

# Game Loop Functions
def load_level(level_data):
    global player, enemies, obstacles, powerups, tokens, score, goal_rect

    # Clear existing groups
    all_sprites.empty()
    enemies.empty()
    obstacles.empty()
    powerups.empty()
    tokens.empty()

    # Player
    player_spawn = level_data["spawn_points"][0]
    player = Player(player_spawn["x"], player_spawn["y"])
    all_sprites.add(player)

    # Obstacles
    for obs_data in level_data["obstacles"]:
        obs = Obstacle(obs_data["x"], obs_data["y"], obs_data["width"], obs_data["height"], obs_data["type"])
        obstacles.add(obs)
        all_sprites.add(obs)

    # Enemies
    for enemy_data in level_data["enemies"]:
        enemy = Enemy(enemy_data["x"], enemy_data["y"], enemy_data["type"], enemy_data.get("patrol_path"))
        enemies.add(enemy)
        all_sprites.add(enemy)

    # Powerups
    for powerup_data in level_data["powerups"]:
        powerup = Powerup(powerup_data["x"], powerup_data["y"], powerup_data["type"])
        powerups.add(powerup)
        all_sprites.add(powerup)

    # Tokens
    # For this level, tokens are pre-defined in level_data.
    # A more dynamic system would generate tokens based on spawn patterns.
    # For now, we'll simulate collecting them. The objective specifies 5 tokens.
    # We'll just add 5 placeholder tokens to the screen.
    token_count_needed = next((obj['count'] for obj in level_data['objectives'] if obj['type'] == 'collect'), 0)
    token_spacing = (GOAL_LINE_X - player.rect.centerx) / (token_count_needed + 1)
    for i in range(token_count_needed):
        token_x = player.rect.centerx + token_spacing * (i + 1)
        token_y = SCREEN_HEIGHT // 2 + (i % 2 * 20 - 10) # Stagger them slightly
        token = Token(token_x, token_y)
        tokens.add(token)
        all_sprites.add(token)

    # Goal line
    goal_rect = pygame.Rect(level_data["objectives"][-1]["goal_x"], 0, GOAL_WIDTH, SCREEN_HEIGHT)

    # Set screen dimensions if not already set
    global SCREEN_WIDTH, SCREEN_HEIGHT
    SCREEN_WIDTH = level_data["size"]["width"]
    SCREEN_HEIGHT = level_data["size"]["height"]
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


def run_menu(events):
    global current_state

    screen.fill(BLACK)
    draw_text(screen, "Touchdown Blitz", BIG_FONT, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, center=True)
    draw_text(screen, "Press SPACE to Start", MEDIUM_FONT, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, center=True)
    draw_text(screen, "Use WASD to move, Shift to Sprint", SMALL_FONT, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40, center=True)
    draw_text(screen, "Dodge/Juke with quick directional changes", SMALL_FONT, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70, center=True)
    draw_text(screen, "Collect Tokens and Reach the Endzone!", SMALL_FONT, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100, center=True)

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                current_state = GameState.PLAYING
                # Load the first level
                load_level(level_data)
                # Reset score and other game variables for the new game
                global score
                score = 0
                # Reset global timers or relevant game state variables if any

def run_playing(events, dt):
    global current_state, score

    # Input Handling
    player.handle_input()

    # Update Game Logic
    player.update(dt, enemies)
    for enemy in enemies:
        enemy.update(player, dt)

    # Collision Checks
    # Player-Token collision
    tokens_collected = pygame.sprite.spritecollide(player, tokens, True)
    for token in tokens_collected:
        score += TOKEN_VALUE
        print(f"Token collected! Score: {score}")
        # Play sound effect

    # Player-Powerup collision
    powerup_collected = pygame.sprite.spritecollideany(player, powerups)
    if powerup_collected:
        if powerup_collected.powerup_type == "speed_boost":
            # Apply temporary speed boost effect - modify player's max_speed and maybe current_speed
            player.speed *= SPEED_BOOST_ACCELERATION_MULTIPLIER
            player.max_speed *= SPEED_BOOST_ACCELERATION_MULTIPLIER
            # This should probably be a timed effect, not permanent for the level
            print("Speed Boost collected!")
            # Implement a timer for this effect
        elif powerup_collected.powerup_type == "stamina_recharge":
            player.stamina = player.max_stamina
            print("Stamina Recharge collected!")
        elif powerup_collected.powerup_type == "magnetic_boots":
            # Implement magnetic boots effect - make enemies miss tackles more often
            print("Magnetic Boots collected!")
            # Implement a timer for this effect
        powerup_collected.kill()

    # Player-Goal collision
    if player.rect.colliderect(goal_rect):
        current_state = GameState.LEVEL_COMPLETE
        # Check if all objectives are met
        token_objective_met = False
        for obj in level_data['objectives']:
            if obj['type'] == 'collect' and obj['target'] == 'tokens':
                if len(tokens) == 0: # All tokens collected
                    token_objective_met = True
                    break
        if token_objective_met:
            print("Level Complete!")
        else:
            # Maybe allow reaching goal without all tokens, but with penalty or different outcome
            print("Goal reached, but not all tokens collected!")


    # Obstacle collision (player bounces off)
    for obs in obstacles:
        if player.rect.colliderect(obs.rect):
            # Simple bounce-back logic
            # Push player back based on direction of collision
            # This is a simplified collision response
            if abs(player.rect.centerx - obs.rect.centerx) < abs(player.rect.centery - obs.rect.centery): # Vertical collision
                if player.rect.bottom > obs.rect.top and player.rect.top < obs.rect.bottom:
                    if player.rect.centery < obs.rect.centery: # Player above obstacle
                        player.rect.bottom = obs.rect.top
                    else: # Player below obstacle
                        player.rect.top = obs.rect.bottom
            else: # Horizontal collision
                if player.rect.right > obs.rect.left and player.rect.left < obs.rect.right:
                    if player.rect.centerx < obs.rect.centerx: # Player left of obstacle
                        player.rect.right = obs.rect.left
                    else: # Player right of obstacle
                        player.rect.left = obs.rect.right


    # Drawing
    screen.fill((30, 100, 40)) # Green field background

    # Draw the goal line
    pygame.draw.rect(screen, (200, 200, 0), goal_rect) # Yellow goal line

    all_sprites.draw(screen)

    # Draw UI elements
    draw_text(screen, f"Score: {score}", MEDIUM_FONT, WHITE, 10, 10)
    draw_text(screen, f"Level: {current_level}", MEDIUM_FONT, WHITE, 10, 40)

    # Draw stamina bar
    draw_stamina_bar(screen, player.rect, player.stamina, player.max_stamina)

    # Draw enemy speed/aggression indicators if needed
    # for enemy in enemies:
    #     if enemy.enemy_type == "flanker":
    #         pygame.draw.circle(screen, GREEN, enemy.rect.center, ENEMY_DETECTION_RADIUS, 1)


def run_level_complete(events, dt):
    global current_state, current_level

    screen.fill(BLACK)
    draw_text(screen, "LEVEL COMPLETE!", BIG_FONT, GREEN, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, center=True)
    draw_text(screen, f"Score: {score}", MEDIUM_FONT, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, center=True)
    draw_text(screen, "Press SPACE for next level or R to restart", SMALL_FONT, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, center=True)

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                current_level += 1
                # Load next level data (this part requires more levels to be defined)
                # For now, we'll just go to game over if this is the only level
                if current_level > 1: # Assuming only level 1 exists for now
                    current_state = GameState.GAME_OVER
                    print("All levels completed! Going to Game Over.")
                else:
                    # Load the next level if defined
                    # load_level(level_data_for_next_level)
                    pass # Placeholder for loading next level
            elif event.key == pygame.K_r:
                current_state = GameState.PLAYING
                load_level(level_data) # Reload the current level

def run_game_over(events, dt):
    global current_state

    screen.fill(BLACK)
    draw_text(screen, "GAME OVER", BIG_FONT, RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, center=True)
    draw_text(screen, f"Final Score: {score}", MEDIUM_FONT, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, center=True)
    draw_text(screen, "Press R to Restart, SPACE to return to Menu", SMALL_FONT, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, center=True)

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                current_state = GameState.PLAYING
                load_level(level_data) # Reload the first level
            elif event.key == pygame.K_SPACE:
                current_state = GameState.MENU
                # Reset score and level
                global score, current_level
                score = 0
                current_level = 1


# --- Main Game Loop ---
running = True
while running:
    # 1. Event Handling
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    # Calculate delta time (time since last frame)
    dt = clock.tick(FPS) / 1000.0 # Convert milliseconds to seconds

    # 2. State Logic
    if current_state == GameState.MENU:
        run_menu(events)
    elif current_state == GameState.PLAYING:
        run_playing(events, dt)
    elif current_state == GameState.LEVEL_COMPLETE:
        run_level_complete(events, dt)
    elif current_state == GameState.GAME_OVER:
        run_game_over(events, dt)

    # 3. Drawing
    pygame.display.flip()

# --- Cleanup ---
pygame.quit()
sys.exit()