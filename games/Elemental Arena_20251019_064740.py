
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
GRAY = (100, 100, 100)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# Player
PLAYER_SPEED = 5
PLAYER_SIZE = 30
PLAYER_COLOR = ORANGE
PLAYER_CHARGE_MAX = 100
PLAYER_SURGE_DURATION = 2000  # milliseconds
PLAYER_DODGE_DURATION = 500   # milliseconds
PLAYER_DODGE_COOLDOWN = 1000  # milliseconds
PLAYER_DODGE_SPEED_MULTIPLIER = 2.5

# Enemies
ENEMY_SPEED = 2
ENEMY_SIZE = 25
STONE_GOLEM_COLOR = GRAY
WHISPERING_SERPENT_COLOR = GREEN
BLAZING_PHOENIX_COLOR = RED

# Elements
ROCK = 0
PAPER = 1
SCISSORS = 2

ELEMENT_COLORS = {
    ROCK: GRAY,
    PAPER: WHITE,
    SCISSORS: PURPLE,
}
ELEMENT_NAMES = ["Rock", "Paper", "Scissors"]

# Powerups
POWERUP_SIZE = 15
ELEMENTAL_SHARD_COLOR = BLUE
ANCIENT_CHARM_COLOR = YELLOW

# Game States
MENU_STATE = 0
PLAYING_STATE = 1
GAME_OVER_STATE = 2

# --- Game Classes ---

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = PLAYER_SPEED
        self.element_choice = -1  # -1 for no choice, 0: Rock, 1: Paper, 2: Scissors
        self.health = 100
        self.max_health = 100
        self.charge = 0
        self.max_charge = PLAYER_CHARGE_MAX
        self.special_ability_charge = 0
        self.max_special_ability_charge = 100
        self.elemental_surge_active = False
        self.surge_start_time = 0
        self.evasive_dodge_active = False
        self.dodge_start_time = 0
        self.dodge_end_time = 0
        self.dodge_cooldown_start_time = 0
        self.is_invincible = False
        self.invincibility_start_time = 0
        self.damage_multiplier = 1.0
        self.score = 0

    def update(self, obstacles):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        current_speed = self.speed

        if self.evasive_dodge_active:
            current_speed *= PLAYER_DODGE_SPEED_MULTIPLIER

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -current_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = current_speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -current_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = current_speed

        self.rect.x += dx
        self.rect.y += dy

        # Collision with obstacles
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                if dx > 0: self.rect.right = obstacle.rect.left
                if dx < 0: self.rect.left = obstacle.rect.right
                if dy > 0: self.rect.bottom = obstacle.rect.top
                if dy < 0: self.rect.top = obstacle.rect.bottom

        # Screen boundaries
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH: self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT: self.rect.bottom = SCREEN_HEIGHT

        # Update abilities
        if self.elemental_surge_active and pygame.time.get_ticks() - self.surge_start_time > PLAYER_SURGE_DURATION:
            self.elemental_surge_active = False
            self.damage_multiplier = 1.0

        if self.evasive_dodge_active and pygame.time.get_ticks() >= self.dodge_end_time:
            self.evasive_dodge_active = False
            self.dodge_cooldown_start_time = pygame.time.get_ticks()

        if not self.evasive_dodge_active and self.dodge_cooldown_start_time > 0 and pygame.time.get_ticks() - self.dodge_cooldown_start_time > PLAYER_DODGE_COOLDOWN:
            self.dodge_cooldown_start_time = 0

        if self.is_invincible and pygame.time.get_ticks() - self.invincibility_start_time > 3000: # Invincibility lasts 3 seconds
            self.is_invincible = False
            self.damage_multiplier = 1.0

    def choose_element(self, element):
        self.element_choice = element

    def use_elemental_surge(self):
        if self.special_ability_charge >= self.max_special_ability_charge:
            self.special_ability_charge = 0
            self.elemental_surge_active = True
            self.surge_start_time = pygame.time.get_ticks()
            self.damage_multiplier = 1.5  # Increased damage

    def use_evasive_dodge(self):
        if not self.evasive_dodge_active and self.dodge_cooldown_start_time == 0:
            self.evasive_dodge_active = True
            self.dodge_start_time = pygame.time.get_ticks()
            self.dodge_end_time = self.dodge_start_time + PLAYER_DODGE_DURATION

    def elemental_vision(self):
        # Placeholder for visual feedback of enemy weakness
        pass

    def take_damage(self, amount):
        if not self.is_invincible:
            self.health -= amount
            if self.health < 0:
                self.health = 0
            return True
        return False

    def heal(self, amount):
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health

    def add_charge(self, amount):
        self.charge += amount
        if self.charge > self.max_charge:
            self.charge = self.max_charge

    def add_special_ability_charge(self, amount):
        self.special_ability_charge += amount
        if self.special_ability_charge > self.max_special_ability_charge:
            self.special_ability_charge = self.max_special_ability_charge

    def apply_ancient_charm(self):
        self.is_invincible = True
        self.invincibility_start_time = pygame.time.get_ticks()
        self.damage_multiplier = 2.0 # Increased damage from charm

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, element_type, patrol_path=None):
        super().__init__()
        self.element_type = element_type
        self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
        self.image.fill(ELEMENT_COLORS.get(element_type, BLACK))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = ENEMY_SPEED
        self.health = 50
        self.max_health = 50
        self.attack_damage = 10
        self.weakness = -1 # Rock: 0, Paper: 1, Scissors: 2
        self.charge_on_hit = 10

        if element_type == ROCK: # Stone Golem
            self.weakness = PAPER
            self.health = 70
            self.max_health = 70
            self.attack_damage = 15
            self.charge_on_hit = 15
        elif element_type == PAPER: # Whispering Serpent
            self.weakness = SCISSORS
            self.health = 40
            self.max_health = 40
            self.attack_damage = 8
            self.charge_on_hit = 10
        elif element_type == SCISSORS: # Blazing Phoenix
            self.weakness = ROCK
            self.health = 60
            self.max_health = 60
            self.attack_damage = 12
            self.charge_on_hit = 12

        self.patrol_path = patrol_path
        self.current_path_point = 0
        self.patrol_direction = 1 # 1 for forward, -1 for backward

        self.ai_state = "chase" # chase, patrol, attack
        self.target = None
        self.attack_range = 50
        self.attack_cooldown = 1500 # milliseconds
        self.last_attack_time = 0

    def update(self, player, obstacles):
        if self.health <= 0:
            self.kill()
            return

        if self.target is None:
            self.target = player

        dx, dy = 0, 0

        if self.ai_state == "chase":
            distance_to_player = math.hypot(self.rect.centerx - player.rect.centerx, self.rect.centery - player.rect.centery)
            if distance_to_player < self.attack_range:
                self.ai_state = "attack"
                self.last_attack_time = pygame.time.get_ticks() # Start cooldown immediately
            else:
                if self.rect.centerx < player.rect.centerx:
                    dx = self.speed
                elif self.rect.centerx > player.rect.centerx:
                    dx = -self.speed
                if self.rect.centery < player.rect.centery:
                    dy = self.speed
                elif self.rect.centery > player.rect.centery:
                    dy = -self.speed

        elif self.ai_state == "attack":
            if pygame.time.get_ticks() - self.last_attack_time > self.attack_cooldown:
                self.attack(player)
                self.last_attack_time = pygame.time.get_ticks()
            distance_to_player = math.hypot(self.rect.centerx - player.rect.centerx, self.rect.centery - player.rect.centery)
            if distance_to_player > self.attack_range * 1.5: # If player moves too far, re-engage chase
                self.ai_state = "chase"

        elif self.ai_state == "patrol" and self.patrol_path:
            if self.current_path_point < len(self.patrol_path):
                target_x, target_y = self.patrol_path[self.current_path_point]
                distance_to_target = math.hypot(self.rect.centerx - target_x, self.rect.centery - target_y)
                if distance_to_target < self.speed:
                    self.current_path_point += self.patrol_direction
                    if self.current_path_point >= len(self.patrol_path) or self.current_path_point < 0:
                        self.patrol_direction *= -1
                        self.current_path_point += self.patrol_direction * 2 # Go back to the previous point
                else:
                    if self.rect.centerx < target_x: dx = self.speed
                    elif self.rect.centerx > target_x: dx = -self.speed
                    if self.rect.centery < target_y: dy = self.speed
                    elif self.rect.centery > target_y: dy = -self.speed
            else:
                self.ai_state = "chase" # If patrol path ends, chase player

        self.rect.x += dx
        self.rect.y += dy

        # Collision with obstacles
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                if dx > 0: self.rect.right = obstacle.rect.left
                if dx < 0: self.rect.left = obstacle.rect.right
                if dy > 0: self.rect.bottom = obstacle.rect.top
                if dy < 0: self.rect.top = obstacle.rect.bottom

        # Screen boundaries
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH: self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT: self.rect.bottom = SCREEN_HEIGHT


    def attack(self, player):
        # This method will be called when the enemy attacks the player.
        # The actual damage and effects are handled in the main game loop
        # based on element choice.
        pass

    def take_damage(self, amount, player_element):
        critical_hit = False
        stunned = False
        damage_dealt = amount * player.damage_multiplier # Apply player's damage multiplier

        if player.element_choice != -1:
            if player_element == self.weakness:
                critical_hit = True
                damage_dealt *= 2 # Critical damage
                stunned = True
                self.charge_on_hit *= 2 # More charge for successful counter
            elif (player_element == ROCK and self.element_type == PAPER) or \
                 (player_element == PAPER and self.element_type == SCISSORS) or \
                 (player_element == SCISSORS and self.element_type == ROCK):
                # Player's attack is countered by the enemy
                damage_dealt /= 2 # Reduced damage
        else:
            # No element chosen by player, normal damage
            pass

        self.health -= int(damage_dealt)
        if self.health <= 0:
            self.health = 0
            return "defeated", stunned
        else:
            player.add_charge(self.charge_on_hit)
            if stunned:
                return "stunned", True
            else:
                return "hit", False

    def get_element_name(self):
        return ELEMENT_NAMES[self.element_type]

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

class Powerup(pygame.sprite.Sprite):
    def __init__(self, x, y, powerup_type):
        super().__init__()
        self.powerup_type = powerup_type
        self.image = pygame.Surface((POWERUP_SIZE, POWERUP_SIZE))
        self.rect = self.image.get_rect(center=(x, y))

        if powerup_type == "health_shard":
            self.image.fill(BLUE)
        elif powerup_type == "speed_boost_orb":
            self.image.fill(GREEN)
        elif powerup_type == "attack_buff_crystal":
            self.image.fill(RED)
        elif powerup_type == "elemental_shard":
            self.image.fill(YELLOW)
        elif powerup_type == "ancient_charm":
            self.image.fill(ORANGE)

    def apply_effect(self, player):
        if self.powerup_type == "health_shard":
            player.heal(25)
        elif self.powerup_type == "speed_boost_orb":
            player.speed += 2
            pygame.time.set_timer(pygame.USEREVENT + 1, 5000) # Speed boost duration
        elif self.powerup_type == "attack_buff_crystal":
            player.damage_multiplier *= 1.2
            pygame.time.set_timer(pygame.USEREVENT + 2, 5000) # Attack buff duration
        elif self.powerup_type == "elemental_shard":
            player.add_special_ability_charge(50)
        elif self.powerup_type == "ancient_charm":
            player.apply_ancient_charm()
        self.kill()

# --- Game Data ---
LEVEL_DATA = {
    1: {
        "level_number": 1,
        "name": "The Crumbling Foundations",
        "description": "Welcome to the Elemental Arena! Your first challenge awaits in these unstable ruins. Learn the basics of elemental combat while navigating the debris and facing off against rudimentary defenses.",
        "size": {"width": 800, "height": 600},
        "spawn_points": [
            {"x": 100, "y": 100, "type": "player"},
            {"x": 400, "y": 300, "type": "enemy"}
        ],
        "obstacles": [
            {"x": 200, "y": 200, "width": 70, "height": 70, "type": "rock_formation", "color": GRAY},
            {"x": 550, "y": 400, "width": 50, "height": 100, "type": "crumbling_pillar", "color": GRAY},
            {"x": 300, "y": 450, "width": 150, "height": 50, "type": "broken_wall", "color": GRAY}
        ],
        "powerups": [
            {"x": 300, "y": 150, "type": "health_shard"},
            {"x": 600, "y": 500, "type": "speed_boost_orb"},
            {"x": 700, "y": 150, "type": "attack_buff_crystal"}
        ],
        "enemies": [
            {"x": 350, "y": 250, "type": "rock_golem", "patrol_path": [[350, 250], [400, 250], [400, 300], [350, 300]]},
            {"x": 150, "y": 450, "type": "paper_sprite", "patrol_path": [[150, 450], [220, 450]]},
            {"x": 650, "y": 100, "type": "scissors_bug", "patrol_path": [[650, 100], [650, 170]]}
        ],
        "objectives": [
            {"type": "collect", "target": "elemental_fragments", "count": 5},
            {"type": "defeat", "target": "all_enemies", "count": 3}
        ],
        "difficulty": "easy",
        "time_limit": 180
    }
    # Add more levels here
}

# --- Helper Functions ---

def draw_text(surface, text, size, x, y, color=WHITE):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)

def draw_health_bar(surface, x, y, width, height, current_health, max_health, color=GREEN):
    fill = (current_health / max_health) * width
    border = pygame.Rect(x, y, width, height)
    fill_rect = pygame.Rect(x, y, fill, height)
    pygame.draw.rect(surface, color, fill_rect)
    pygame.draw.rect(surface, BLACK, border, 2)

def get_element_type_from_name(name):
    if name.lower() == "rock": return ROCK
    if name.lower() == "paper": return PAPER
    if name.lower() == "scissors": return SCISSORS
    return -1

def check_elemental_win(player_element, enemy_element):
    if player_element == -1 or enemy_element == -1:
        return False
    if player_element == ROCK and enemy_element == SCISSORS: return True
    if player_element == SCISSORS and enemy_element == PAPER: return True
    if player_element == PAPER and enemy_element == ROCK: return True
    return False

def check_elemental_loss(player_element, enemy_element):
    if player_element == -1 or enemy_element == -1:
        return False
    if player_element == ROCK and enemy_element == PAPER: return True
    if player_element == SCISSORS and enemy_element == ROCK: return True
    if player_element == PAPER and enemy_element == SCISSORS: return True
    return False

# --- Game Logic ---

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Elemental Arena")
        self.clock = pygame.time.Clock()
        self.game_state = MENU_STATE
        self.current_level_data = None
        self.player = None
        self.enemies = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.elemental_fragments_collected = 0
        self.enemies_defeated = 0
        self.current_level_number = 1
        self.level_timer = 0
        self.speed_boost_event_id = pygame.USEREVENT + 1
        self.attack_buff_event_id = pygame.USEREVENT + 2
        self.speed_boost_active = False
        self.attack_buff_active = False

    def load_level(self, level_num):
        self.current_level_data = LEVEL_DATA.get(level_num)
        if not self.current_level_data:
            print(f"Error: Level {level_num} not found.")
            return

        self.screen = pygame.display.set_mode((self.current_level_data["size"]["width"], self.current_level_data["size"]["height"]))
        pygame.display.set_caption(f"Elemental Arena - {self.current_level_data['name']}")

        self.enemies.empty()
        self.obstacles.empty()
        self.powerups.empty()
        self.all_sprites.empty()

        # Player
        player_spawn = next((s for s in self.current_level_data["spawn_points"] if s["type"] == "player"), None)
        if player_spawn:
            self.player = Player(player_spawn["x"], player_spawn["y"])
            self.all_sprites.add(self.player)
        else:
            print("Error: Player spawn point not found.")
            return

        # Obstacles
        for obs_data in self.current_level_data["obstacles"]:
            obstacle = Obstacle(obs_data["x"], obs_data["y"], obs_data["width"], obs_data["height"], obs_data["color"])
            self.obstacles.add(obstacle)
            self.all_sprites.add(obstacle)

        # Enemies
        for enemy_data in self.current_level_data["enemies"]:
            element_type = get_element_type_from_name(enemy_data["type"].split('_')[0]) # e.g. "rock_golem" -> ROCK
            if element_type != -1:
                enemy = Enemy(enemy_data["x"], enemy_data["y"], element_type, enemy_data.get("patrol_path"))
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)
            else:
                print(f"Warning: Unknown enemy type '{enemy_data['type']}' in level data.")

        # Powerups
        for powerup_data in self.current_level_data["powerups"]:
            powerup = Powerup(powerup_data["x"], powerup_data["y"], powerup_data["type"])
            self.powerups.add(powerup)
            self.all_sprites.add(powerup)

        # Level objectives
        self.elemental_fragments_collected = 0
        self.enemies_defeated = 0
        self.objectives = self.current_level_data["objectives"]
        self.time_limit = self.current_level_data["time_limit"]
        self.level_timer = pygame.time.get_ticks()

        # Reset player state for the new level
        self.player.health = self.player.max_health
        self.player.charge = 0
        self.player.special_ability_charge = 0
        self.player.elemental_surge_active = False
        self.player.evasive_dodge_active = False
        self.player.is_invincible = False
        self.player.damage_multiplier = 1.0
        self.player.speed = PLAYER_SPEED
        self.speed_boost_active = False
        self.attack_buff_active = False


    def handle_menu(self):
        self.screen.fill(BLACK)
        draw_text(self.screen, "Elemental Arena", 64, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        draw_text(self.screen, "Press ENTER to Start", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text(self.screen, "Use WASD or Arrow Keys to Move", 20, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4)
        draw_text(self.screen, "Press 1, 2, or 3 to Choose Element", 20, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4 + 30)
        draw_text(self.screen, "Press SPACE for Evasive Dodge", 20, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4 + 60)
        draw_text(self.screen, "Press SHIFT for Elemental Surge", 20, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4 + 90)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.load_level(self.current_level_number)
                    self.game_state = PLAYING_STATE
                if event.key == pygame.K_ESCAPE:
                    return False
        return True

    def handle_playing(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game_state = MENU_STATE
                    return True

                # Element Choice
                if event.key == pygame.K_1:
                    self.player.choose_element(ROCK)
                elif event.key == pygame.K_2:
                    self.player.choose_element(PAPER)
                elif event.key == pygame.K_3:
                    self.player.choose_element(SCISSORS)

                # Abilities
                if event.key == pygame.K_SPACE:
                    self.player.use_evasive_dodge()
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    self.player.use_elemental_surge()

            if event.type == self.speed_boost_event_id:
                self.player.speed = PLAYER_SPEED
                self.speed_boost_active = False
            if event.type == self.attack_buff_event_id:
                self.player.damage_multiplier = 1.0
                self.attack_buff_active = False

        # Update
        self.player.update(self.obstacles)
        self.enemies.update(self.player, self.obstacles)
        self.all_sprites.update(self.obstacles)

        # Collisions
        # Player-Powerup collision
        powerup_hits = pygame.sprite.spritecollide(self.player, self.powerups, False)
        for powerup in powerup_hits:
            if powerup.powerup_type == "health_shard":
                powerup.apply_effect(self.player)
            elif powerup.powerup_type == "speed_boost_orb":
                if not self.speed_boost_active:
                    powerup.apply_effect(self.player)
                    self.speed_boost_active = True
                    pygame.time.set_timer(self.speed_boost_event_id, 5000)
            elif powerup.powerup_type == "attack_buff_crystal":
                if not self.attack_buff_active:
                    powerup.apply_effect(self.player)
                    self.attack_buff_active = True
                    pygame.time.set_timer(self.attack_buff_event_id, 5000)
            elif powerup.powerup_type == "elemental_shard":
                powerup.apply_effect(self.player)
            elif powerup.powerup_type == "ancient_charm":
                powerup.apply_effect(self.player)


        # Enemy attacks player
        for enemy in self.enemies:
            if pygame.sprite.collide_rect(self.player, enemy) and not self.player.evasive_dodge_active:
                if pygame.time.get_ticks() - enemy.last_attack_time > enemy.attack_cooldown:
                    if self.player.take_damage(enemy.attack_damage):
                        enemy.attack_cooldown = 2000 # Longer cooldown after hitting player
                    enemy.last_attack_time = pygame.time.get_ticks()

        # Player attacks enemy
        for enemy in self.enemies:
            if self.player.element_choice != -1:
                # Check for attack input (e.g., mouse click or key press)
                # For now, let's make it so player attacks automatically if an element is chosen and enemy is in range.
                distance_to_enemy = math.hypot(self.player.rect.centerx - enemy.rect.centerx, self.player.rect.centery - enemy.rect.centery)
                if distance_to_enemy < PLAYER_SIZE + ENEMY_SIZE: # Simple proximity attack
                    action, stunned = enemy.take_damage(10, self.player.element_choice) # Base damage 10
                    if action == "hit":
                        self.player.score += 10
                        self.player.add_charge(enemy.charge_on_hit)
                    elif action == "defeated":
                        self.player.score += 50
                        self.enemies_defeated += 1
                        self.elemental_fragments_collected += 1 # Assuming each enemy drop fragment
                        enemy.kill()
                    elif action == "stunned":
                        self.player.score += 25
                        self.player.add_charge(enemy.charge_on_hit)
                        enemy.ai_state = "stunned" # Simple AI state for stunned
                        enemy.stun_start_time = pygame.time.get_ticks()

        # Re-enable enemy chase after stun
        for enemy in self.enemies:
            if hasattr(enemy, "ai_state") and enemy.ai_state == "stunned":
                if pygame.time.get_ticks() - enemy.stun_start_time > 1500: # Stun duration
                    enemy.ai_state = "chase"

        # Check level objectives
        completed_objectives = 0
        for obj in self.objectives:
            if obj["type"] == "collect" and obj["target"] == "elemental_fragments":
                if self.elemental_fragments_collected >= obj["count"]:
                    completed_objectives += 1
            elif obj["type"] == "defeat" and obj["target"] == "all_enemies":
                if self.enemies_defeated >= obj["count"]:
                    completed_objectives += 1

        if completed_objectives >= len(self.objectives):
            self.game_state = PLAYING_STATE # Temporarily stay in playing to show win message
            self.show_level_complete()
            return True

        # Time limit check
        if pygame.time.get_ticks() - self.level_timer > self.time_limit * 1000:
            self.game_state = GAME_OVER_STATE
            self.reason_for_game_over = "Time's Up!"

        # Player health check
        if self.player.health <= 0:
            self.game_state = GAME_OVER_STATE
            self.reason_for_game_over = "You Were Defeated!"

        # Drawing
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)

        # UI Elements
        draw_health_bar(self.screen, 20, 20, 150, 20, self.player.health, self.player.max_health)
        draw_text(self.screen, f"Health: {self.player.health}/{self.player.max_health}", 18, 100, 30)
        draw_text(self.screen, f"Score: {self.player.score}", 20, SCREEN_WIDTH - 80, 30)

        # Element Choice Indicator
        if self.player.element_choice != -1:
            pygame.draw.circle(self.screen, ELEMENT_COLORS[self.player.element_choice], (self.player.rect.centerx, self.player.rect.bottom + 20), 10)

        # Special Ability Charge Bar
        pygame.draw.rect(self.screen, GRAY, (20, 50, 100, 15))
        pygame.draw.rect(self.screen, YELLOW, (20, 50, (self.player.special_ability_charge / self.player.max_special_ability_charge) * 100, 15))
        draw_text(self.screen, "Surge", 14, 70, 60)

        # Time Limit
        time_left = max(0, self.time_limit - (pygame.time.get_ticks() - self.level_timer) // 1000)
        draw_text(self.screen, f"Time: {time_left}", 20, SCREEN_WIDTH // 2, 30)

        # Objective progress
        objective_y = 80
        for obj in self.objectives:
            if obj["type"] == "collect" and obj["target"] == "elemental_fragments":
                draw_text(self.screen, f"Fragments: {self.elemental_fragments_collected}/{obj['count']}", 18, 100, objective_y)
                objective_y += 20
            elif obj["type"] == "defeat" and obj["target"] == "all_enemies":
                draw_text(self.screen, f"Enemies Defeated: {self.enemies_defeated}/{obj['count']}", 18, 150, objective_y)
                objective_y += 20

        return True

    def show_level_complete(self):
        self.screen.fill(BLACK)
        draw_text(self.screen, "Level Complete!", 72, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        draw_text(self.screen, f"Score: {self.player.score}", 40, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text(self.screen, "Press ENTER to proceed to next level", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4)
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.current_level_number += 1
                        if self.current_level_number in LEVEL_DATA:
                            self.load_level(self.current_level_number)
                            self.game_state = PLAYING_STATE
                        else:
                            # End of game / final boss
                            self.game_state = GAME_OVER_STATE
                            self.reason_for_game_over = "You have mastered the elements!"
                        waiting = False
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = MENU_STATE
                        waiting = False
            self.clock.tick(FPS)
        return True


    def handle_game_over(self):
        self.screen.fill(BLACK)
        draw_text(self.screen, "Game Over", 72, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        draw_text(self.screen, self.reason_for_game_over, 36, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text(self.screen, f"Final Score: {self.player.score}", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4)
        draw_text(self.screen, "Press ENTER to play again or ESC to quit", 25, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4 + 40)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.reset_game()
                    self.game_state = MENU_STATE
                if event.key == pygame.K_ESCAPE:
                    return False
        return True

    def reset_game(self):
        self.current_level_number = 1
        self.player = None
        self.enemies.empty()
        self.obstacles.empty()
        self.powerups.empty()
        self.all_sprites.empty()
        self.elemental_fragments_collected = 0
        self.enemies_defeated = 0
        self.level_timer = 0
        self.speed_boost_active = False
        self.attack_buff_active = False

    def run(self):
        running = True
        while running:
            if self.game_state == MENU_STATE:
                running = self.handle_menu()
            elif self.game_state == PLAYING_STATE:
                running = self.handle_playing()
            elif self.game_state == GAME_OVER_STATE:
                running = self.handle_game_over()

            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
