
import pygame
import random
import math

# Initialize Pygame
pygame.init()

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cluck 'n' Dash")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (150, 150, 150)
BROWN = (139, 69, 19)
DARK_GREEN = (0, 100, 0)
LIGHT_GREEN = (144, 238, 144)

# Game States
MENU = 0
PLAYING = 1
GAME_OVER = 2

# Player Constants
PLAYER_SIZE = 30
PLAYER_SPEED = 5
PLAYER_DASH_SPEED = 15
PLAYER_DASH_DURATION = 15  # frames
PLAYER_DASH_COOLDOWN = 60  # frames

# Vehicle Constants
VEHICLE_WIDTH = 50
VEHICLE_HEIGHT = 30
VEHICLE_SPEED_RANGE = (2, 7)
VEHICLE_SPAWN_RATE_MIN = 60  # frames
VEHICLE_SPAWN_RATE_MAX = 120  # frames

# Animal Constants
ANIMAL_SIZE = 20
ANIMAL_SPEED = 2

# Powerup Constants
POWERUP_SIZE = 20
POWERUP_DURATION = 300  # frames

# Level Data (Simplified for this example)
level_data = {
    "level_1": {
        "size": {"width": SCREEN_WIDTH, "height": SCREEN_HEIGHT},
        "spawn_points": [{"x": SCREEN_WIDTH // 2, "y": SCREEN_HEIGHT - 50, "type": "player"}],
        "obstacles": [
            {"x": 0, "y": 0, "width": SCREEN_WIDTH, "height": 50, "type": "road_boundary_top"},
            {"x": 0, "y": SCREEN_HEIGHT - 50, "width": SCREEN_WIDTH, "height": 50, "type": "road_boundary_bottom"},
            {"x": 0, "y": 0, "width": 50, "height": SCREEN_HEIGHT, "type": "road_boundary_left"},
            {"x": SCREEN_WIDTH - 50, "y": 0, "width": 50, "height": SCREEN_HEIGHT, "type": "road_boundary_right"},
        ],
        "powerups": [
            {"x": 100, "y": 150, "type": "dash_restore"},
            {"x": SCREEN_WIDTH - 100, "y": SCREEN_HEIGHT - 150, "type": "speed_boost"},
        ],
        "enemies": [
            {"x": SCREEN_WIDTH // 2, "y": 100, "type": "basic_car", "patrol_path": [[SCREEN_WIDTH // 2, 100], [SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100]]},
            {"x": SCREEN_WIDTH // 4, "y": 250, "type": "basic_car", "patrol_path": [[SCREEN_WIDTH // 4, 250], [SCREEN_WIDTH // 4, 100]]},
            {"x": SCREEN_WIDTH * 3 // 4, "y": 400, "type": "basic_car", "patrol_path": [[SCREEN_WIDTH * 3 // 4, 400], [SCREEN_WIDTH * 3 // 4, SCREEN_HEIGHT - 100]]},
        ],
        "objectives": [
            {"type": "collect", "target": "coins", "count": 7},
            {"type": "reach_destination", "target": {"x": SCREEN_WIDTH // 2, "y": 50}},
        ],
        "difficulty": "easy",
        "time_limit": 90
    }
}

# --- Classes ---

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([PLAYER_SIZE, PLAYER_SIZE])
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.direction = pygame.math.Vector2(0, 0)
        self.speed = PLAYER_SPEED
        self.momentum = pygame.math.Vector2(0, 0)
        self.momentum_decay = 0.9  # How quickly momentum fades
        self.max_momentum_duration = 15 # frames

        self.dash_speed = PLAYER_DASH_SPEED
        self.dash_duration = PLAYER_DASH_DURATION
        self.dash_cooldown = PLAYER_DASH_COOLDOWN
        self.dash_timer = 0
        self.is_dashing = False
        self.dash_direction = pygame.math.Vector2(0, 0)

        self.can_peck = False # For potential future implementation
        self.cluck_cooldown = 120 # frames
        self.cluck_timer = 0

        self.powerups = {
            "speed_boost": {"active": False, "timer": 0},
            "invincible": {"active": False, "timer": 0}
        }
        self.dash_restore_count = 0

        self.score = 0
        self.coins_collected = 0
        self.consecutive_crossings = 0

    def update(self, obstacles):
        # Handle dash
        if self.is_dashing:
            self.rect.x += self.dash_direction.x * self.dash_speed
            self.rect.y += self.dash_direction.y * self.dash_speed
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.is_dashing = False
                self.dash_timer = 0
                self.dash_cooldown_timer = self.dash_cooldown # Start cooldown after dash ends
        else:
            # Apply momentum
            self.momentum *= self.momentum_decay
            if abs(self.momentum.x) < 0.1: self.momentum.x = 0
            if abs(self.momentum.y) < 0.1: self.momentum.y = 0
            self.rect.x += self.momentum.x
            self.rect.y += self.momentum.y

            # Apply base speed if no momentum
            if self.momentum == (0, 0):
                self.rect.x += self.direction.x * self.speed
                self.rect.y += self.direction.y * self.speed

        # Apply powerups
        for powerup, data in self.powerups.items():
            if data["active"]:
                data["timer"] -= 1
                if data["timer"] <= 0:
                    data["active"] = False
                    if powerup == "speed_boost":
                        self.speed = PLAYER_SPEED # Reset to base speed
                        self.dash_speed = PLAYER_DASH_SPEED # Reset dash speed

        # Cluck cooldown
        if self.cluck_timer > 0:
            self.cluck_timer -= 1

        # Collision with obstacles (road boundaries)
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                # Simple push back logic
                if self.momentum.x > 0 and self.rect.right > obstacle.rect.left and self.rect.left < obstacle.rect.left:
                    self.rect.right = obstacle.rect.left
                    self.momentum.x = 0
                elif self.momentum.x < 0 and self.rect.left < obstacle.rect.right and self.rect.right > obstacle.rect.right:
                    self.rect.left = obstacle.rect.right
                    self.momentum.x = 0
                if self.momentum.y > 0 and self.rect.bottom > obstacle.rect.top and self.rect.top < obstacle.rect.top:
                    self.rect.bottom = obstacle.rect.top
                    self.momentum.y = 0
                elif self.momentum.y < 0 and self.rect.top < obstacle.rect.bottom and self.rect.bottom > obstacle.rect.bottom:
                    self.rect.top = obstacle.rect.bottom
                    self.momentum.y = 0

                # If not dashing, prevent movement into obstacles
                if not self.is_dashing:
                    if self.direction.x > 0: self.rect.right = obstacle.rect.left
                    elif self.direction.x < 0: self.rect.left = obstacle.rect.right
                    if self.direction.y > 0: self.rect.bottom = obstacle.rect.top
                    elif self.direction.y < 0: self.rect.top = obstacle.rect.bottom

        # Keep player within screen bounds (this should be handled by obstacles mostly)
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - self.rect.height))

    def move(self, direction, obstacles):
        if self.is_dashing:
            return # Cannot change direction while dashing

        self.direction = pygame.math.Vector2(direction)
        self.direction.normalize_ip() # Ensure it's a unit vector

        # Apply momentum based on direction
        self.momentum = self.direction * self.speed * 2 # Higher initial momentum
        if self.momentum.length() > self.max_momentum_duration: # Cap momentum
             self.momentum.scale_to_length(self.max_momentum_duration)


    def dash(self):
        if not self.is_dashing and self.dash_timer <= 0 and self.dash_cooldown_timer <= 0:
            self.is_dashing = True
            self.dash_direction = self.direction if self.direction != (0, 0) else pygame.math.Vector2(0, 1) # Default down if no direction
            self.dash_timer = self.dash_duration
            self.dash_cooldown_timer = self.dash_cooldown # Start cooldown immediately
            self.dash_restore_count -= 1 # Use a charge
            self.momentum = pygame.math.Vector2(0, 0) # Reset momentum when dashing

    def cluck(self):
        if self.cluck_timer <= 0:
            self.cluck_timer = self.cluck_cooldown
            return True
        return False

    def collect_coin(self):
        self.coins_collected += 1
        self.score += 10 * (self.consecutive_crossings + 1) # Score multiplier for consecutive crossings

    def reach_destination(self):
        self.consecutive_crossings += 1
        self.score += 100 * self.consecutive_crossings
        self.dash_restore_count = max(0, self.dash_restore_count + 1) # Gain a dash restore for successful crossing


class Vehicle(pygame.sprite.Sprite):
    def __init__(self, x, y, vehicle_type, patrol_path=None):
        super().__init__()
        self.vehicle_type = vehicle_type
        self.image = pygame.Surface([VEHICLE_WIDTH, VEHICLE_HEIGHT])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.speed = random.uniform(VEHICLE_SPEED_RANGE[0], VEHICLE_SPEED_RANGE[1])
        self.direction = 1 # 1 for right, -1 for left

        if vehicle_type == "basic_car":
            self.image.fill(RED)
            self.speed = random.uniform(3, 5)
        elif vehicle_type == "speedy_sedan":
            self.image.fill(BLUE)
            self.speed = random.uniform(5, 7)
        elif vehicle_type == "tractor":
            self.image.fill(BROWN)
            self.speed = random.uniform(1, 3)
            self.rect.width = VEHICLE_WIDTH * 1.5
            self.rect.height = VEHICLE_HEIGHT * 1.5
            self.image = pygame.Surface([self.rect.width, self.rect.height])
            self.image.fill(BROWN)
        elif vehicle_type == "rogue_pig":
            self.image.fill(GRAY)
            self.speed = random.uniform(4, 6)

        self.patrol_path = patrol_path
        self.current_waypoint = 0
        if self.patrol_path:
            self.rect.center = self.patrol_path[self.current_waypoint]

        self.lane_change_timer = random.randint(120, 300) # frames

    def update(self, player, obstacles):
        if self.patrol_path:
            target_x, target_y = self.patrol_path[self.current_waypoint]
            dx = target_x - self.rect.centerx
            dy = target_y - self.rect.centery

            if abs(dx) < self.speed and abs(dy) < self.speed:
                self.current_waypoint = (self.current_waypoint + 1) % len(self.patrol_path)
                target_x, target_y = self.patrol_path[self.current_waypoint]
                dx = target_x - self.rect.centerx
                dy = target_y - self.rect.centery

            distance = math.sqrt(dx**2 + dy**2)
            if distance > 0:
                move_x = (dx / distance) * self.speed
                move_y = (dy / distance) * self.speed
                self.rect.x += move_x
                self.rect.y += move_y
        else:
            # Default lane movement
            self.rect.x += self.speed * self.direction
            self.lane_change_timer -= 1

            # Simple lane cycling for basic cars
            if self.vehicle_type == "basic_car" and self.lane_change_timer <= 0:
                self.direction *= -1 # Reverse direction
                self.lane_change_timer = random.randint(120, 300) # Reset timer

            # Screen wrap around for vehicles
            if self.rect.left > SCREEN_WIDTH:
                self.rect.right = 0
            elif self.rect.right < 0:
                self.rect.left = SCREEN_WIDTH

        # Rogue Pig erratic movement
        if self.vehicle_type == "rogue_pig":
            self.lane_change_timer -= 1
            if self.lane_change_timer <= 0:
                random_lane_change = random.choice([-1, 0, 1]) # -1: up, 0: stay, 1: down
                if random_lane_change == -1:
                    self.rect.y -= 50 # Move up one lane (approx)
                elif random_lane_change == 1:
                    self.rect.y += 50 # Move down one lane (approx)
                self.lane_change_timer = random.randint(30, 90)

        # Prevent vehicles from going out of bounds or through specific obstacles
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                if obstacle.type in ["road_boundary_top", "road_boundary_bottom"]:
                    self.rect.y -= self.speed * self.direction # Push back
                    self.direction *= -1 # Reverse direction
                if obstacle.type in ["road_boundary_left", "road_boundary_right"]:
                    self.rect.x -= self.speed * self.direction # Push back
                    self.direction *= -1 # Reverse direction

class Powerup(pygame.sprite.Sprite):
    def __init__(self, x, y, powerup_type):
        super().__init__()
        self.image = pygame.Surface([POWERUP_SIZE, POWERUP_SIZE])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.powerup_type = powerup_type

        if powerup_type == "speed_boost":
            self.image.fill(GREEN)
        elif powerup_type == "dash_restore":
            self.image.fill(YELLOW)
        elif powerup_type == "invincible":
            self.image.fill(BLUE)

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([15, 15])
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, obstacle_type):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.obstacle_type = obstacle_type

        if obstacle_type in ["road_boundary_top", "road_boundary_bottom"]:
            self.image.fill(DARK_GREEN)
        elif obstacle_type in ["road_boundary_left", "road_boundary_right"]:
            self.image.fill(DARK_GREEN)
        else:
            self.image.fill(GRAY)

# --- Game Functions ---

def draw_text(text, font, color, surface, x, y, center=False):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    if center:
        textrect.center = (x, y)
    else:
        textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def reset_game(level_key="level_1"):
    all_sprites = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    vehicle_group = pygame.sprite.Group()
    powerup_group = pygame.sprite.Group()
    coin_group = pygame.sprite.Group()
    obstacle_group = pygame.sprite.Group()

    level = level_data[level_key]

    # Create player
    for spawn in level["spawn_points"]:
        if spawn["type"] == "player":
            player = Player(spawn["x"], spawn["y"])
            all_sprites.add(player)
            player_group.add(player)

    # Create obstacles
    for obs_data in level["obstacles"]:
        obstacle = Obstacle(obs_data["x"], obs_data["y"], obs_data["width"], obs_data["height"], obs_data["type"])
        all_sprites.add(obstacle)
        obstacle_group.add(obstacle)

    # Create powerups
    for pup_data in level["powerups"]:
        powerup = Powerup(pup_data["x"], pup_data["y"], pup_data["type"])
        all_sprites.add(powerup)
        powerup_group.add(powerup)

    # Create enemies
    for enemy_data in level["enemies"]:
        vehicle = Vehicle(enemy_data["x"], enemy_data["y"], enemy_data["type"], enemy_data.get("patrol_path"))
        all_sprites.add(vehicle)
        vehicle_group.add(vehicle)

    # Create coins (simplified: generate random coins within playable area, avoiding obstacles)
    num_coins_to_generate = level["objectives"][0]["count"]
    for _ in range(num_coins_to_generate):
        valid_position = False
        while not valid_position:
            coin_x = random.randint(50, SCREEN_WIDTH - 50)
            coin_y = random.randint(50, SCREEN_HEIGHT - 50)
            coin_sprite = Coin(coin_x, coin_y)
            if not pygame.sprite.spritecollideany(coin_sprite, obstacle_group) and \
               not pygame.sprite.spritecollideany(coin_sprite, player_group): # Avoid spawning on player
                valid_position = True
                all_sprites.add(coin_sprite)
                coin_group.add(coin_sprite)

    destination_pos = level["objectives"][1]["target"]
    destination_rect = pygame.Rect(destination_pos["x"] - 25, destination_pos["y"] - 25, 50, 50) # Visual marker for destination

    return player, all_sprites, player_group, vehicle_group, powerup_group, coin_group, obstacle_group, destination_rect, level

def main():
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    large_font = pygame.font.Font(None, 72)

    game_state = MENU

    # Menu specific variables
    menu_options = ["Start Game", "Quit"]
    selected_option = 0

    # Game Over specific variables
    game_over_score = 0

    # Game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_state == MENU:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        if menu_options[selected_option] == "Start Game":
                            player, all_sprites, player_group, vehicle_group, powerup_group, coin_group, obstacle_group, destination_rect, current_level = reset_game()
                            game_state = PLAYING
                        elif menu_options[selected_option] == "Quit":
                            running = False
            elif game_state == PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        player.move((0, -1), obstacle_group)
                    elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        player.move((0, 1), obstacle_group)
                    elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        player.move((-1, 0), obstacle_group)
                    elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        player.move((1, 0), obstacle_group)
                    elif event.key == pygame.K_SPACE:
                        player.dash()
                    elif event.key == pygame.K_c:
                        if player.cluck():
                            # Implement cluck logic (e.g., slightly distract nearby animals)
                            pass

            elif game_state == GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        game_state = MENU
                    elif event.key == pygame.K_r: # Restart
                        player, all_sprites, player_group, vehicle_group, powerup_group, coin_group, obstacle_group, destination_rect, current_level = reset_game()
                        game_state = PLAYING

        # --- Game Logic ---
        if game_state == PLAYING:
            all_sprites.update(obstacle_group) # Pass obstacles to player update for boundary checks

            # Player collision with vehicles
            collided_vehicles = pygame.sprite.spritecollide(player, vehicle_group, False)
            for vehicle in collided_vehicles:
                if not player.powerups["invincible"]["active"]:
                    game_over_score = player.score
                    game_state = GAME_OVER

            # Player collision with powerups
            collided_powerups = pygame.sprite.spritecollide(player, powerup_group, True)
            for powerup in collided_powerups:
                if powerup.powerup_type == "speed_boost":
                    player.powerups["speed_boost"]["active"] = True
                    player.powerups["speed_boost"]["timer"] = POWERUP_DURATION
                    player.speed = PLAYER_SPEED * 1.5
                    player.dash_speed = PLAYER_DASH_SPEED * 1.5
                elif powerup.powerup_type == "dash_restore":
                    player.dash_restore_count += 1
                elif powerup.powerup_type == "invincible":
                    player.powerups["invincible"]["active"] = True
                    player.powerups["invincible"]["timer"] = POWERUP_DURATION

            # Player collision with coins
            collided_coins = pygame.sprite.spritecollide(player, coin_group, True)
            for coin in collided_coins:
                player.collect_coin()

            # Check for reaching destination
            if player.rect.colliderect(destination_rect):
                player.reach_destination()
                # Transition to next level or reset for now
                player, all_sprites, player_group, vehicle_group, powerup_group, coin_group, obstacle_group, destination_rect, current_level = reset_game()

            # Update vehicle positions and potentially spawn new ones
            for vehicle in vehicle_group:
                vehicle.update(player, obstacle_group)

            # Simple enemy spawning (this can be more complex)
            if random.randint(0, 100) < 5: # Chance to spawn a new vehicle
                lane_y = random.choice([100, 200, 300, 400, 500])
                if not any(v.rect.centery == lane_y for v in vehicle_group): # Avoid stacking
                    new_vehicle_type = random.choice(["basic_car", "speedy_sedan", "tractor"])
                    vehicle = Vehicle(-VEHICLE_WIDTH, lane_y, new_vehicle_type)
                    all_sprites.add(vehicle)
                    vehicle_group.add(vehicle)


        # --- Drawing ---
        screen.fill(LIGHT_GREEN) # Grass background

        if game_state == MENU:
            draw_text("Cluck 'n' Dash", large_font, BLACK, screen, SCREEN_WIDTH // 2, 100, center=True)
            for i, option in enumerate(menu_options):
                color = WHITE if i == selected_option else GRAY
                draw_text(option, font, color, screen, SCREEN_WIDTH // 2, 250 + i * 50, center=True)

        elif game_state == PLAYING:
            # Draw road
            pygame.draw.rect(screen, GRAY, (0, 50, SCREEN_WIDTH, SCREEN_HEIGHT - 100))
            # Draw lane lines
            for y in range(100, SCREEN_HEIGHT - 50, 50):
                pygame.draw.line(screen, WHITE, (0, y), (SCREEN_WIDTH, y), 2)

            # Draw destination
            pygame.draw.rect(screen, GREEN, destination_rect, 5)

            all_sprites.draw(screen)

            # Draw UI
            draw_text(f"Score: {player.score}", font, BLACK, screen, 10, 10)
            draw_text(f"Coins: {player.coins_collected}", font, BLACK, screen, 10, 40)
            draw_text(f"Dash: {player.dash_restore_count}", font, BLACK, screen, 10, 70)

        elif game_state == GAME_OVER:
            draw_text("Game Over!", large_font, RED, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, center=True)
            draw_text(f"Final Score: {game_over_score}", font, BLACK, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20, center=True)
            draw_text("Press ENTER to return to menu", font, BLACK, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70, center=True)
            draw_text("Press R to restart", font, BLACK, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 110, center=True)


        pygame.display.flip()
        clock.tick(60) # Limit frame rate

    pygame.quit()

if __name__ == "__main__":
    main()
