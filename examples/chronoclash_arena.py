
import pygame
import random
import math

# --- Game Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

# Player
PLAYER_SPEED = 5
PLAYER_DASH_SPEED = 15
PLAYER_DASH_DURATION = 0.2  # seconds
PLAYER_SHIELD_DURATION = 1.0  # seconds
PLAYER_HEALTH = 3
PLAYER_SIZE = 20

# Enemies
ENEMY_SPEED = 3
ENEMY_HEALTH = 1
ENEMY_SIZE = 20

# RPS Choices
ROCK = 0
PAPER = 1
SCISSORS = 2
CHOICES = [ROCK, PAPER, SCISSORS]
CHOICE_NAMES = {ROCK: "Rock", PAPER: "Paper", SCISSORS: "Scissors"}
CHOICE_COLORS = {ROCK: RED, PAPER: BLUE, SCISSORS: GREEN}

# Temporal Anomalies
TEMPORAL_ANOMALY_DURATION = 5.0  # seconds
TEMPORAL_ANOMALY_TYPES = ["slow_time", "speed_boost", "random_swap"]

# UI
FONT_SIZE = 30

# --- Game States ---
MENU = 0
PLAYING = 1
GAME_OVER = 2

# --- Classes ---

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = pygame.math.Vector2(0, 0)
        self.speed = PLAYER_SPEED
        self.health = PLAYER_HEALTH
        self.max_health = PLAYER_HEALTH
        self.combo_meter = 0
        self.max_combo = 10
        self.current_choice = None
        self.next_choice = None
        self.choice_timer = 0
        self.choice_cooldown = 1.0  # seconds
        self.can_choose = True
        self.dash_active = False
        self.dash_timer = 0
        self.dash_velocity = pygame.math.Vector2(0, 0)
        self.shield_active = False
        self.shield_timer = 0
        self.predictive_scan_cooldown = 5.0
        self.predictive_scan_timer = 0
        self.predictive_scan_active = False
        self.predicted_move = None
        self.special_move_unlocked = False
        self.special_move_cooldown = 10.0
        self.special_move_timer = 0

    def update(self, dt, obstacles, enemies, temporal_anomalies):
        if self.health <= 0:
            self.kill()
            return

        # Handle input for movement
        keys = pygame.key.get_pressed()
        self.velocity.x = 0
        self.velocity.y = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.velocity.x = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.velocity.x = 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.velocity.y = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.velocity.y = 1

        if self.velocity.length() > 0:
            self.velocity.normalize_ip()

        # Handle dash
        if keys[pygame.K_LSHIFT] and not self.dash_active:
            self.dash_active = True
            self.dash_timer = PLAYER_DASH_DURATION
            self.dash_velocity = self.velocity * PLAYER_DASH_SPEED
            if self.dash_velocity.length() == 0: # Default dash direction if not moving
                self.dash_velocity = pygame.math.Vector2(PLAYER_DASH_SPEED, 0)

        if self.dash_active:
            self.rect.x += self.dash_velocity.x * dt * FPS
            self.rect.y += self.dash_velocity.y * dt * FPS
            self.dash_timer -= dt
            if self.dash_timer <= 0:
                self.dash_active = False
        else:
            self.rect.x += self.velocity.x * self.speed * dt * FPS
            self.rect.y += self.velocity.y * self.speed * dt * FPS

        # Handle collisions with obstacles
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                if self.velocity.x > 0:
                    self.rect.right = obstacle.rect.left
                if self.velocity.x < 0:
                    self.rect.left = obstacle.rect.right
                if self.velocity.y > 0:
                    self.rect.bottom = obstacle.rect.top
                if self.velocity.y < 0:
                    self.rect.top = obstacle.rect.bottom

        # Keep player within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

        # Handle choice selection and cooldown
        if self.can_choose:
            if keys[pygame.K_1]:
                self.next_choice = ROCK
            elif keys[pygame.K_2]:
                self.next_choice = PAPER
            elif keys[pygame.K_3]:
                self.next_choice = SCISSORS
            elif keys[pygame.K_r] and not self.predictive_scan_active: # Predictive scan
                self.predictive_scan_timer = self.predictive_scan_cooldown
                self.predictive_scan_active = True
                self.special_move_timer = max(self.special_move_timer, self.special_move_cooldown) # Prevent special move immediately

        if self.next_choice is not None:
            self.current_choice = self.next_choice
            self.next_choice = None
            self.choice_timer = self.choice_cooldown
            self.can_choose = False
            self.predictive_scan_active = False # Reset predictive scan after making a choice

        if not self.can_choose:
            self.choice_timer -= dt
            if self.choice_timer <= 0:
                self.can_choose = True
                self.current_choice = None # Clear choice after round ends

        # Handle shield
        if keys[pygame.K_SPACE] and not self.shield_active and not self.dash_active:
            self.shield_active = True
            self.shield_timer = PLAYER_SHIELD_DURATION
            self.special_move_timer = max(self.special_move_timer, self.special_move_cooldown) # Prevent special move immediately

        if self.shield_active:
            self.shield_timer -= dt
            if self.shield_timer <= 0:
                self.shield_active = False

        # Handle special move
        if keys[pygame.K_q] and self.special_move_unlocked and self.special_move_timer <= 0:
            self.use_special_move()
            self.special_move_timer = self.special_move_cooldown

        if self.special_move_timer > 0:
            self.special_move_timer -= dt

        # Update predictive scan
        if self.predictive_scan_active:
            self.predictive_scan_timer -= dt
            if self.predictive_scan_timer <= 0:
                self.predictive_scan_active = False
                self.predicted_move = None

        # Check for powerup collection
        powerups_hit = pygame.sprite.spritecollide(self, game.powerups, True)
        for powerup in powerups_hit:
            powerup.apply_effect(self)

    def take_damage(self, damage=1):
        if self.shield_active:
            self.shield_active = False
            self.shield_timer = 0
            return False # Attack blocked
        else:
            self.health -= damage
            self.combo_meter = 0
            self.special_move_unlocked = False # Reset special move on damage
            self.special_move_timer = max(self.special_move_timer, self.special_move_cooldown) # Prevent special move immediately
            return True # Damage taken

    def win_round(self):
        self.combo_meter += 1
        self.combo_meter = min(self.combo_meter, self.max_combo)
        if self.combo_meter >= self.max_combo:
            self.special_move_unlocked = True

    def lose_round(self):
        self.combo_meter = 0
        self.special_move_unlocked = False
        self.special_move_timer = max(self.special_move_timer, self.special_move_cooldown) # Prevent special move immediately

    def use_special_move(self):
        print("Special move used!")
        # This is where you'd implement specific special moves based on current_choice
        pass

    def draw(self, screen):
        if self.health > 0:
            pygame.draw.rect(screen, YELLOW, self.rect)
            if self.shield_active:
                pygame.draw.circle(screen, CYAN, self.rect.center, PLAYER_SIZE * 1.5, 2)
            if self.current_choice is not None:
                choice_color = CHOICE_COLORS[self.current_choice]
                pygame.draw.circle(screen, choice_color, self.rect.center, PLAYER_SIZE / 2)
            if self.predictive_scan_active and self.predicted_move is not None:
                pygame.draw.circle(screen, MAGENTA, self.rect.center, PLAYER_SIZE * 0.7, 2)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type, patrol_path=None):
        super().__init__()
        self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
        self.enemy_type = enemy_type
        self.color = RED # Default color
        if enemy_type == "basic":
            self.color = RED
        elif enemy_type == "temporal_guardian":
            self.color = CYAN
        elif enemy_type == "chrono_master":
            self.color = MAGENTA
        self.image.fill(self.color)

        self.rect = self.image.get_rect(center=(x, y))
        self.health = ENEMY_HEALTH
        self.speed = ENEMY_SPEED
        self.current_choice = None
        self.next_choice = None
        self.choice_timer = 0
        self.choice_cooldown = 1.5 # Slightly longer cooldown for enemies
        self.can_choose = True
        self.patrol_path = patrol_path
        self.patrol_index = 0
        self.patrol_direction = 1
        self.target_pos = None
        self.predictive_scan_cooldown = 7.0
        self.predictive_scan_timer = 0
        self.predictive_scan_active = False
        self.predicted_move = None

        if patrol_path:
            self.target_pos = pygame.math.Vector2(self.patrol_path[self.patrol_index])

    def update(self, dt, player, temporal_anomalies):
        if self.health <= 0:
            self.kill()
            return

        # AI Behavior
        if self.enemy_type == "basic":
            self.basic_ai(dt)
        elif self.enemy_type == "temporal_guardian":
            self.temporal_guardian_ai(dt, player)
        elif self.enemy_type == "chrono_master":
            self.chrono_master_ai(dt, player)

        # Handle choice selection and cooldown
        if self.can_choose:
            self.current_choice = random.choice(CHOICES)
            self.choice_timer = self.choice_cooldown
            self.can_choose = False

        if not self.can_choose:
            self.choice_timer -= dt
            if self.choice_timer <= 0:
                self.can_choose = True
                self.current_choice = None # Clear choice after round ends

        # Update predictive scan
        if self.predictive_scan_active:
            self.predictive_scan_timer -= dt
            if self.predictive_scan_timer <= 0:
                self.predictive_scan_active = False
                self.predicted_move = None

    def basic_ai(self, dt):
        if self.patrol_path:
            direction = self.target_pos - pygame.math.Vector2(self.rect.center)
            if direction.length() < 5:
                self.patrol_index += self.patrol_direction
                if self.patrol_index >= len(self.patrol_path):
                    self.patrol_index = len(self.patrol_path) - 2
                    self.patrol_direction = -1
                elif self.patrol_index < 0:
                    self.patrol_index = 1
                    self.patrol_direction = 1
                self.target_pos = pygame.math.Vector2(self.patrol_path[self.patrol_index])
                direction = self.target_pos - pygame.math.Vector2(self.rect.center)

            if direction.length() > 0:
                direction.normalize_ip()
                self.rect.x += direction.x * self.speed * dt * FPS
                self.rect.y += direction.y * self.speed * dt * FPS
        else: # If no patrol path, try to move towards player if far away
            if pygame.math.Vector2(self.rect.center).distance_to(game.player.rect.center) > 100:
                direction = pygame.math.Vector2(game.player.rect.center) - pygame.math.Vector2(self.rect.center)
                if direction.length() > 0:
                    direction.normalize_ip()
                    self.rect.x += direction.x * self.speed * dt * FPS
                    self.rect.y += direction.y * self.speed * dt * FPS


    def temporal_guardian_ai(self, dt, player):
        self.basic_ai(dt) # Inherits basic movement
        self.predictive_scan_timer -= dt
        if self.predictive_scan_timer <= 0:
            self.predictive_scan_active = True
            # Basic prediction: assume player will counter last move
            if player.current_choice is not None:
                if player.current_choice == ROCK:
                    self.predicted_move = PAPER
                elif player.current_choice == PAPER:
                    self.predicted_move = SCISSORS
                else:
                    self.predicted_move = ROCK
            else:
                self.predicted_move = random.choice(CHOICES)
            self.predictive_scan_timer = self.predictive_scan_cooldown

        # More aggressive movement
        distance_to_player = pygame.math.Vector2(self.rect.center).distance_to(player.rect.center)
        if distance_to_player < 150 and distance_to_player > ENEMY_SIZE:
            direction = pygame.math.Vector2(player.rect.center) - pygame.math.Vector2(self.rect.center)
            direction.normalize_ip()
            self.rect.x += direction.x * self.speed * 1.5 * dt * FPS
            self.rect.y += direction.y * self.speed * 1.5 * dt * FPS

    def chrono_master_ai(self, dt, player):
        self.temporal_guardian_ai(dt, player) # Inherits guardian behavior
        # More intelligent prediction
        if player.current_choice is not None:
            # If player consistently chooses X, try to counter Y
            # This requires tracking player's history, which is more complex for this example
            # For now, a slightly more strategic prediction
            if random.random() < 0.7: # 70% chance of a more strategic prediction
                if player.current_choice == ROCK:
                    self.predicted_move = PAPER
                elif player.current_choice == PAPER:
                    self.predicted_move = SCISSORS
                else:
                    self.predicted_move = ROCK
            else:
                self.predicted_move = random.choice(CHOICES)
        else:
            self.predicted_move = random.choice(CHOICES)

        # Can trigger localized temporal anomalies (simplified)
        if random.random() < 0.005 * dt * FPS: # Chance per frame
            game.trigger_temporal_anomaly()

    def take_damage(self, damage=1):
        self.health -= damage
        if self.health <= 0:
            self.kill()

    def draw(self, screen):
        if self.health > 0:
            pygame.draw.rect(screen, self.color, self.rect)
            if self.current_choice is not None:
                choice_color = CHOICE_COLORS[self.current_choice]
                pygame.draw.circle(screen, choice_color, self.rect.center, ENEMY_SIZE / 2)
            if self.predictive_scan_active and self.predicted_move is not None:
                pygame.draw.circle(screen, YELLOW, self.rect.center, ENEMY_SIZE * 0.7, 2)

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, obstacle_type):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.obstacle_type = obstacle_type
        if obstacle_type == "table":
            self.image.fill((139, 69, 19)) # Brown
        elif obstacle_type == "couch":
            self.image.fill((128, 0, 128)) # Purple
        elif obstacle_type == "wardrobe":
            self.image.fill((101, 67, 33)) # Darker Brown
        elif obstacle_type == "fireplace":
            self.image.fill((169, 169, 169)) # Dark Gray
        else:
            self.image.fill((50, 50, 50)) # Default gray
        self.rect = self.image.get_rect(topleft=(x, y))

class Powerup(pygame.sprite.Sprite):
    def __init__(self, x, y, powerup_type):
        super().__init__()
        self.powerup_type = powerup_type
        self.image = pygame.Surface((20, 20))
        self.color = YELLOW # Default
        if powerup_type == "health":
            self.color = GREEN
        elif powerup_type == "speed":
            self.color = CYAN
        elif powerup_type == "combo_boost":
            self.color = MAGENTA
        elif powerup_type == "predictive_matrix":
            self.color = YELLOW
        elif powerup_type == "temporal_warp":
            self.color = BLUE
        self.image.fill(self.color)
        self.rect = self.image.get_rect(center=(x, y))

    def apply_effect(self, player):
        if self.powerup_type == "health":
            player.health = min(player.max_health, player.health + 1)
        elif self.powerup_type == "speed":
            player.speed *= 1.5
            pygame.time.set_timer(pygame.USEREVENT + 1, 5000) # Reset speed after 5 seconds
        elif self.powerup_type == "combo_boost":
            player.combo_meter = min(player.max_combo, player.combo_meter * 2)
        elif self.powerup_type == "predictive_matrix":
            # This powerup should directly reveal the opponent's move for the next round
            # For simplicity here, we'll just give a visual cue or a temporary boost
            print("Predictive Matrix collected! (Effect not fully implemented)")
        elif self.powerup_type == "temporal_warp":
            player.rect.center = (random.randint(50, SCREEN_WIDTH - 50), random.randint(50, SCREEN_HEIGHT - 50))

class TemporalAnomaly:
    def __init__(self, anomaly_type, duration):
        self.anomaly_type = anomaly_type
        self.duration = duration
        self.timer = duration
        self.active = True
        self.visual_effect = self.create_visual_effect()

    def create_visual_effect(self):
        if self.anomaly_type == "slow_time":
            return {"color": (100, 100, 255, 128), "alpha": 128} # Semi-transparent blue
        elif self.anomaly_type == "speed_boost":
            return {"color": (255, 100, 100, 128), "alpha": 128} # Semi-transparent red
        elif self.anomaly_type == "random_swap":
            return {"color": (255, 255, 0, 128), "alpha": 128} # Semi-transparent yellow
        return None

    def update(self, dt):
        if self.active:
            self.timer -= dt
            if self.timer <= 0:
                self.active = False

    def draw(self, screen):
        if self.active and self.visual_effect:
            surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            surface.fill(self.visual_effect["color"])
            screen.blit(surface, (0, 0))

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("ChronoClash: Rock Paper Scissors Arena")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.game_state = MENU

        self.player = None
        self.enemies = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.temporal_anomalies = []

        self.score = 0
        self.level_data = None
        self.current_level = 1
        self.enemies_defeated_this_level = 0
        self.temporal_distortions_survived_this_level = 0
        self.time_limit = 0
        self.time_remaining = 0

    def load_level(self, level_data):
        self.level_data = level_data
        self.screen = pygame.display.set_mode((level_data["size"]["width"], level_data["size"]["height"]))
        pygame.display.set_caption(f"ChronoClash: {level_data['name']}")

        self.player = Player(level_data["spawn_points"][0]["x"], level_data["spawn_points"][0]["y"])

        self.enemies.empty()
        for enemy_data in level_data["enemies"]:
            enemy = Enemy(enemy_data["x"], enemy_data["y"], enemy_data["type"], enemy_data.get("patrol_path"))
            self.enemies.add(enemy)

        self.obstacles.empty()
        for obstacle_data in level_data["obstacles"]:
            obstacle = Obstacle(obstacle_data["x"], obstacle_data["y"], obstacle_data["width"], obstacle_data["height"], obstacle_data["type"])
            self.obstacles.add(obstacle)

        self.powerups.empty()
        for powerup_data in level_data["powerups"]:
            powerup = Powerup(powerup_data["x"], powerup_data["y"], powerup_data["type"])
            self.powerups.add(powerup)

        self.enemies_defeated_this_level = 0
        self.temporal_distortions_survived_this_level = 0
        self.time_limit = level_data.get("time_limit", 120)
        self.time_remaining = self.time_limit
        self.temporal_anomalies = []

    def trigger_temporal_anomaly(self):
        if len(self.temporal_anomalies) < 1: # Limit to one active anomaly at a time for simplicity
            anomaly_type = random.choice(TEMPORAL_ANOMALY_TYPES)
            self.temporal_anomalies.append(TemporalAnomaly(anomaly_type, TEMPORAL_ANOMALY_DURATION))
            print(f"Temporal Anomaly triggered: {anomaly_type}")

    def resolve_rps_round(self, player_choice, enemy_choice):
        if player_choice is None or enemy_choice is None:
            return

        if player_choice == enemy_choice:
            return "tie"
        elif (player_choice == ROCK and enemy_choice == SCISSORS) or \
             (player_choice == SCISSORS and enemy_choice == PAPER) or \
             (player_choice == PAPER and enemy_choice == ROCK):
            return "player_win"
        else:
            return "enemy_win"

    def update_temporal_effects(self, dt):
        active_anomalies = [a for a in self.temporal_anomalies if a.active]
        for anomaly in active_anomalies:
            anomaly.update(dt)
            if anomaly.anomaly_type == "slow_time":
                return 0.5 # Halve game speed
            elif anomaly.anomaly_type == "speed_boost":
                return 1.5 # Double game speed
        self.temporal_anomalies = [a for a in active_anomalies if a.active] # Remove inactive anomalies
        return 1.0 # Normal speed

    def draw_text(self, text, x, y, color=WHITE):
        surface = self.font.render(text, True, color)
        rect = surface.get_rect(center=(x, y))
        self.screen.blit(surface, rect)

    def run_menu(self):
        self.screen.fill(BLACK)
        self.draw_text("ChronoClash: Rock Paper Scissors Arena", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, YELLOW)
        self.draw_text("Press ENTER to Start", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.draw_text("Controls: WASD/Arrows to move, Shift to Dash, Space to Shield, Q for Special, 1,2,3 for RPS", SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.game_state = PLAYING
                    self.load_level(LEVEL_DATA[0]) # Load first level
        return True

    def run_playing(self, dt):
        # Update
        speed_multiplier = self.update_temporal_effects(dt)
        self.player.update(dt * speed_multiplier, self.obstacles, self.enemies, self.temporal_anomalies)

        # RPS Round Logic
        if self.player.can_choose and all(enemy.can_choose for enemy in self.enemies):
            # All characters have made their choice for the round
            # Determine outcomes and apply damage/combos
            player_choice = self.player.current_choice
            enemies_to_remove = []
            for enemy in self.enemies:
                enemy_choice = enemy.current_choice
                outcome = self.resolve_rps_round(player_choice, enemy_choice)

                if outcome == "player_win":
                    enemy.take_damage()
                    self.player.win_round()
                    self.score += 10
                    if enemy.health <= 0:
                        self.enemies_defeated_this_level += 1
                        self.score += 50 # Bonus for defeating enemy
                        enemies_to_remove.append(enemy)
                elif outcome == "enemy_win":
                    if self.player.take_damage():
                        self.score -= 5
                    self.player.lose_round()
                elif outcome == "tie":
                    pass # No change

            for enemy in enemies_to_remove:
                self.enemies.remove(enemy)

            # Reset choices for the next round
            self.player.current_choice = None
            for enemy in self.enemies:
                enemy.current_choice = None

        # Update enemies
        for enemy in self.enemies:
            enemy.update(dt * speed_multiplier, self.player, self.temporal_anomalies)

        # Update powerups
        self.powerups.update()

        # Time limit check
        self.time_remaining -= dt
        if self.time_remaining <= 0:
            self.game_state = GAME_OVER

        # Level progression check
        if self.enemies_defeated_this_level >= len(self.level_data["enemies"]):
            self.current_level += 1
            if self.current_level < len(LEVEL_DATA):
                self.load_level(LEVEL_DATA[self.current_level - 1])
            else:
                self.game_state = GAME_OVER # Game complete

        # Draw
        self.screen.fill(BLACK)
        self.obstacles.draw(self.screen)
        self.powerups.draw(self.screen)
        for anomaly in self.temporal_anomalies:
            anomaly.draw(self.screen)
        self.enemies.draw(self.screen)
        if self.player.health > 0:
            self.player.draw(self.screen)

        # Draw UI
        self.draw_text(f"Level: {self.current_level}", 80, 20)
        self.draw_text(f"Health: {self.player.health}/{self.player.max_health}", 150, 20)
        combo_bar_width = (self.player.combo_meter / self.player.max_combo) * 100
        pygame.draw.rect(self.screen, GREEN, (250, 10, 100, 15))
        pygame.draw.rect(self.screen, YELLOW, (250, 10, combo_bar_width, 15))
        self.draw_text(f"Combo: {self.player.combo_meter}", 250, 35)
        self.draw_text(f"Time: {int(self.time_remaining)}", SCREEN_WIDTH - 80, 20)
        self.draw_text(f"Score: {self.score}", SCREEN_WIDTH - 120, 50)

        # Display player and enemy choices
        if self.player.current_choice is not None:
            choice_img = pygame.Surface((15, 15))
            choice_img.fill(CHOICE_COLORS[self.player.current_choice])
            self.screen.blit(choice_img, (self.player.rect.centerx - 20, self.player.rect.top - 20))

        for enemy in self.enemies:
            if enemy.current_choice is not None:
                choice_img = pygame.Surface((15, 15))
                choice_img.fill(CHOICE_COLORS[enemy.current_choice])
                self.screen.blit(choice_img, (enemy.rect.centerx - 20, enemy.rect.top - 20))

        # Handle events for playing state
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.USEREVENT + 1: # Speed reset timer
                self.player.speed = PLAYER_SPEED
        return True

    def run_game_over(self):
        self.screen.fill(BLACK)
        self.draw_text("Game Over", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, RED)
        self.draw_text(f"Final Score: {self.score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.draw_text("Press ENTER to Play Again", SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.game_state = MENU
                    self.current_level = 1 # Reset level
                    self.score = 0
        return True

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0 # Delta time in seconds

            if self.game_state == MENU:
                running = self.run_menu()
            elif self.game_state == PLAYING:
                running = self.run_playing(dt)
            elif self.game_state == GAME_OVER:
                running = self.run_game_over()

            pygame.display.flip()
        pygame.quit()

# --- Level Data ---
LEVEL_DATA = [
    {
        "level_number": 1,
        "name": "The Chrono-Cottage",
        "description": "The first arena is a quaint, slightly dilapidated cottage interior, perfect for learning the ropes of ChronoClash. Watch out for rickety furniture and the occasional temporal hiccup!",
        "size": {
            "width": 800,
            "height": 600
        },
        "spawn_points": [
            {
                "x": 100,
                "y": 100,
                "type": "player"
            },
            {
                "x": 700,
                "y": 500,
                "type": "enemy"
            }
        ],
        "obstacles": [
            {
                "x": 150,
                "y": 200,
                "width": 75,
                "height": 150,
                "type": "table"
            },
            {
                "x": 400,
                "y": 100,
                "width": 100,
                "height": 50,
                "type": "couch"
            },
            {
                "x": 650,
                "y": 300,
                "width": 50,
                "height": 75,
                "type": "wardrobe"
            },
            {
                "x": 250,
                "y": 450,
                "width": 75,
                "height": 75,
                "type": "fireplace"
            }
        ],
        "powerups": [
            {
                "x": 300,
                "y": 150,
                "type": "health"
            },
            {
                "x": 600,
                "y": 500,
                "type": "speed"
            },
            {
                "x": 100,
                "y": 550,
                "type": "combo_boost"
            }
        ],
        "enemies": [
            {
                "x": 350,
                "y": 250,
                "type": "basic",
                "patrol_path": [
                    [
                        350,
                        250
                    ],
                    [
                        450,
                        250
                    ],
                    [
                        450,
                        350
                    ],
                    [
                        350,
                        350
                    ]
                ]
            },
            {
                "x": 150,
                "y": 450,
                "type": "basic",
                "patrol_path": [
                    [
                        150,
                        450
                    ],
                    [
                        200,
                        450
                    ],
                    [
                        200,
                        500
                    ],
                    [
                        150,
                        500
                    ]
                ]
            },
            {
                "x": 600,
                "y": 100,
                "type": "basic",
                "patrol_path": [
                    [
                        600,
                        100
                    ],
                    [
                        700,
                        100
                    ],
                    [
                        700,
                        200
                    ],
                    [
                        600,
                        200
                    ]
                ]
            }
        ],
        "objectives": [
            {
                "type": "defeat",
                "target": "enemies",
                "count": 3
            },
            {
                "type": "survive_temporal_distortions",
                "count": 2
            }
        ],
        "difficulty": "easy",
        "time_limit": 120
    }
    # Add more levels here
]


if __name__ == "__main__":
    game = Game()
    game.run()
