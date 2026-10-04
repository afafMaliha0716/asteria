
import pygame
import sys
import math

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 200)
RED = (200, 0, 0)
YELLOW = (200, 200, 0)
ORANGE = (255, 165, 0)
GRAY = (150, 150, 150)
BROWN = (139, 69, 19)
LIGHT_BLUE = (173, 216, 230)
DARK_GREEN = (0, 100, 0)
PURPLE = (128, 0, 128)
LIGHT_GRAY = (200, 200, 200)

# Game States
GAME_MENU = 0
GAME_PLAYING = 1
GAME_OVER = 2
GAME_WIN = 3

# Game Concept Mappings
# Powerups
POWERUP_COOLING_DEWDROP = "cooling_dewdrop"
POWERUP_STAMINA_BERRY = "stamina_berry"
POWERUP_SEAWEED_CAMOUFLAGE = "seaweed_camouflage"
POWERUP_COMPANION_SHELL = "companion_shell"

# Enemies
ENEMY_SKITTERING_CRAB = "skittering_crab"
ENEMY_HUNGRY_SEAGULL = "hungry_seagull"
ENEMY_RACCOON_FOX = "raccoon_fox"
ENEMY_TIDE_POOL_PERIL = "tide_pool_peril"

# Obstacles
OBSTACLE_WALL = "wall"
OBSTACLE_ROCK = "rock"
OBSTACLE_SHADE = "shade" # Custom addition for heat mechanic
OBSTACLE_WATER = "water" # Custom addition for hydro glide


# --- Game Data (Simplified Level 1) ---
LEVEL_DATA = {
    "level_number": 1,
    "name": "Level 1: Sandy Shores",
    "description": "Basic level 1 - Reach the ocean!",
    "size": {
        "width": SCREEN_WIDTH,
        "height": SCREEN_HEIGHT
    },
    "spawn_points": [
        {"x": 50, "y": 50, "type": "player"}
    ],
    "obstacles": [
        {"x": 200, "y": 200, "width": 50, "height": 50, "type": "wall"},
        {"x": 500, "y": 300, "width": 30, "height": 30, "type": "rock"},
        # Added environmental obstacles for mechanics
        {"x": 0, "y": 500, "width": SCREEN_WIDTH, "height": 100, "type": "water"}, # Ocean goal
        {"x": 100, "y": 100, "width": 80, "height": 80, "type": "shade"}, # Shaded area
        {"x": 400, "y": 100, "width": 60, "height": 120, "type": "shade"}, # Another shaded area
        {"x": 50, "y": 300, "width": 100, "height": 50, "type": "water"}, # Tide pool
    ],
    "powerups": [
        {"x": 300, "y": 150, "type": POWERUP_COOLING_DEWDROP}, # Health -> Cooling Dewdrop
        {"x": 600, "y": 400, "type": POWERUP_STAMINA_BERRY}, # Speed -> Stamina Berry
        {"x": 100, "y": 250, "type": POWERUP_COMPANION_SHELL},
        {"x": 700, "y": 50, "type": POWERUP_SEAWEED_CAMOUFLAGE},
    ],
    "enemies": [
        {
            "x": 400,
            "y": 300,
            "type": ENEMY_SKITTERING_CRAB, # Basic -> Skittering Crab
            "patrol_path": [[400, 300], [450, 300], [450, 350], [400, 350]] # More interesting path
        }
    ],
    "collectibles": [ # Coins -> Ocean Fragments
        {"x": 250, "y": 50, "type": "ocean_fragment"},
        {"x": 550, "y": 250, "type": "ocean_fragment"},
        {"x": 700, "y": 500, "type": "ocean_fragment"}
    ],
    "objectives": [
        {"type": "collect", "target": "ocean_fragment", "count": 3},
        {"type": "reach_area", "x": 0, "y": 500, "width": SCREEN_WIDTH, "height": 100, "name": "ocean"}
    ],
    "difficulty": "easy",
    "time_limit": 120
}

# --- Pygame Setup ---
pygame.init()
pygame.mixer.init() # Initialize mixer for sounds (even if not used extensively yet)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tidebound: Hatchling's Journey")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)
big_font = pygame.font.Font(None, 72)
medium_font = pygame.font.Font(None, 48)

# --- Sound Placeholders (No actual sound files needed for this task) ---
def play_sound(sound_name):
    # This function would load and play actual sound files.
    # For this exercise, it's a placeholder.
    pass


# --- Game Classes ---

class Entity:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.speed = 0 # Base speed, overridden by specific entities

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

    def get_center(self):
        return self.rect.center

    def move_towards(self, target_x, target_y, speed):
        dx, dy = target_x - self.rect.centerx, target_y - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.rect.x += dx / dist * speed
            self.rect.y += dy / dist * speed
        return dist # Return remaining distance

class PlayerHatchling(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 20, 20, GREEN)
        self.base_speed = 3
        self.speed = self.base_speed
        self.hatchlings = [] # List of follower Hatchling objects
        self.max_hatchlings = 5
        self.init_hatchlings(2) # Start with 2 followers + 1 leader = 3 total turtles

        self.stamina = 100
        self.max_stamina = 100
        self.stamina_regen_rate = 5 # per second
        self.shell_sprint_cost = 25
        self.shell_sprint_duration = 1.5 # seconds
        self.shell_sprint_multiplier = 2.0
        self.is_sprinting = False
        self.sprint_timer = 0

        self.heat = 0
        self.max_heat = 100
        self.heat_gain_rate = 10 # per second in sun
        self.heat_loss_rate = 15 # per second in shade
        self.heat_death_threshold = 80 # Lose hatchling if heat > this
        self.heat_loss_cooldown = 0 # To prevent immediate heat loss after gaining

        self.is_burrowing = False
        self.burrow_duration = 3 # seconds
        self.burrow_timer = 0
        self.burrow_cooldown = 0 # seconds
        self.burrow_cooldown_max = 5

        self.is_hydro_gliding = False # Similar to sprint, but conceptually for water
        self.hydro_glide_cost = 20
        self.hydro_glide_duration = 2.0
        self.hydro_glide_multiplier = 2.5
        self.glide_timer = 0

        self.is_camouflaged = False
        self.camouflage_duration = 0 # Set by power-up

        self.ocean_fragments_collected = 0
        self.hatchlings_lost_count = 0

    def init_hatchlings(self, count):
        self.hatchlings = []
        for i in range(count):
            # Spawn followers slightly behind the leader
            offset_x = - (i + 1) * (self.rect.width + 5)
            new_hatchling = FollowerHatchling(self.rect.x + offset_x, self.rect.y, i + 1)
            self.hatchlings.append(new_hatchling)

    def update(self, dt, obstacles, enemies):
        # Update timers
        if self.is_sprinting:
            self.sprint_timer -= dt
            if self.sprint_timer <= 0:
                self.is_sprinting = False
                self.speed = self.base_speed # Reset speed
        
        if self.is_burrowing:
            self.burrow_timer -= dt
            if self.burrow_timer <= 0:
                self.is_burrowing = False
                self.color = GREEN # Emerge
        if self.burrow_cooldown > 0:
            self.burrow_cooldown -= dt

        if self.is_hydro_gliding:
            self.glide_timer -= dt
            if self.glide_timer <= 0:
                self.is_hydro_gliding = False
                self.speed = self.base_speed # Reset speed if in water

        if self.is_camouflaged:
            self.camouflage_duration -= dt
            if self.camouflage_duration <= 0:
                self.is_camouflaged = False

        # Stamina regeneration
        if self.stamina < self.max_stamina:
            self.stamina += self.stamina_regen_rate * dt
            self.stamina = min(self.stamina, self.max_stamina)

        # Heat management (if not burrowing)
        if not self.is_burrowing:
            in_shade = False
            for obs in obstacles:
                if obs.type == OBSTACLE_SHADE and self.rect.colliderect(obs.rect):
                    in_shade = True
                    break
            
            if in_shade:
                self.heat -= self.heat_loss_rate * dt
                self.heat = max(0, self.heat)
                self.heat_loss_cooldown = 0 # Allow immediate heat loss
            else:
                self.heat_loss_cooldown += dt # Accumulate cooldown if in sun
                # If in sun for a while, start gaining heat
                if self.heat_loss_cooldown > 0.5: # Small delay before heat gain starts
                    self.heat += self.heat_gain_rate * dt
                    self.heat = min(self.heat, self.max_heat)

            # Check for heat-related hatchling loss
            if self.heat >= self.heat_death_threshold and len(self.hatchlings) > 0:
                self.lose_hatchling()
                self.heat = 0 # Reset heat after losing one, to give a chance

        # Follower update
        self.update_following(dt)

    def move(self, dx, dy, obstacles):
        if self.is_burrowing:
            return

        original_x, original_y = self.rect.x, self.rect.y
        new_x = self.rect.x + dx * self.speed
        new_y = self.rect.y + dy * self.speed
        
        self.rect.x = new_x
        self.rect.y = new_y

        # Collision with obstacles
        for obs in obstacles:
            if obs.type in [OBSTACLE_WALL, OBSTACLE_ROCK] and self.rect.colliderect(obs.rect):
                # Revert position on collision
                self.rect.x = original_x
                self.rect.y = original_y
                # Try moving only in one direction
                self.rect.x = new_x
                if self.rect.colliderect(obs.rect):
                    self.rect.x = original_x
                self.rect.y = new_y
                if self.rect.colliderect(obs.rect):
                    self.rect.y = original_y
                break # Only resolve for one obstacle for simplicity

        # Keep player on screen
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)

    def update_following(self, dt):
        target_pos = self.rect.center
        for i, hatchling in enumerate(self.hatchlings):
            # Calculate a delayed target position for each hatchling
            # This creates a "snake" like following behavior
            leader_x = self.rect.centerx
            leader_y = self.rect.centery
            if i > 0:
                # Follow the previous hatchling
                prev_hatchling = self.hatchlings[i-1]
                leader_x = prev_hatchling.rect.centerx
                leader_y = prev_hatchling.rect.centery
            
            # Simple direct following, for more complex trailing, store historical positions
            follow_distance = 25 + hatchling.rect.width * i * 0.5 # Distance between hatchlings
            
            dx = leader_x - hatchling.rect.centerx
            dy = leader_y - hatchling.rect.centery
            distance = math.hypot(dx, dy)

            if distance > follow_distance:
                move_speed = self.speed * 0.8 # Followers move slightly slower
                if self.is_sprinting:
                    move_speed *= self.shell_sprint_multiplier
                elif self.is_hydro_gliding:
                    move_speed *= self.hydro_glide_multiplier
                
                # Move towards the leader, but stop at follow_distance
                move_amount = min(distance - follow_distance, move_speed * dt * FPS) # Factor in FPS for consistent movement
                if distance > 0:
                    hatchling.rect.x += (dx / distance) * move_amount
                    hatchling.rect.y += (dy / distance) * move_amount

            # Ensure followers stay on screen
            hatchling.rect.left = max(0, hatchling.rect.left)
            hatchling.rect.right = min(SCREEN_WIDTH, hatchling.rect.right)
            hatchling.rect.top = max(0, hatchling.rect.top)
            hatchling.rect.bottom = min(SCREEN_HEIGHT, hatchling.rect.bottom)


    def burrow(self):
        if not self.is_burrowing and self.burrow_cooldown <= 0:
            self.is_burrowing = True
            self.burrow_timer = self.burrow_duration
            self.burrow_cooldown = self.burrow_cooldown_max
            self.color = BROWN # Visually change for burrowing
            play_sound("burrow")

    def shell_sprint(self):
        if not self.is_sprinting and self.stamina >= self.shell_sprint_cost and not self.is_burrowing:
            self.stamina -= self.shell_sprint_cost
            self.is_sprinting = True
            self.sprint_timer = self.shell_sprint_duration
            self.speed = self.base_speed * self.shell_sprint_multiplier
            play_sound("sprint")

    def hydro_glide(self, in_water):
        if in_water and not self.is_hydro_gliding and self.stamina >= self.hydro_glide_cost and not self.is_burrowing:
            self.stamina -= self.hydro_glide_cost
            self.is_hydro_gliding = True
            self.glide_timer = self.hydro_glide_duration
            self.speed = self.base_speed * self.hydro_glide_multiplier
            play_sound("glide")
    
    def apply_powerup(self, powerup_type):
        play_sound("powerup_collect")
        if powerup_type == POWERUP_COOLING_DEWDROP:
            self.heat = max(0, self.heat - self.max_heat / 2) # Reduce heat significantly
        elif powerup_type == POWERUP_STAMINA_BERRY:
            self.stamina = min(self.max_stamina, self.stamina + self.max_stamina / 2) # Replenish stamina
            # For a temporary buff, one could also increase max_stamina or regen rate for a duration
        elif powerup_type == POWERUP_COMPANION_SHELL:
            if len(self.hatchlings) < self.max_hatchlings:
                self.add_hatchling()
        elif powerup_type == POWERUP_SEAWEED_CAMOUFLAGE:
            self.is_camouflaged = True
            self.camouflage_duration = 5 # seconds of invisibility/reduced detection

    def add_hatchling(self):
        if len(self.hatchlings) < self.max_hatchlings:
            # Position the new hatchling at the end of the line
            if self.hatchlings:
                last_hatchling = self.hatchlings[-1]
                offset_x = last_hatchling.rect.x - (last_hatchling.rect.width + 5)
                offset_y = last_hatchling.rect.y
            else: # If adding the first follower
                offset_x = self.rect.x - (self.rect.width + 5)
                offset_y = self.rect.y
            
            new_hatchling_id = len(self.hatchlings) + 1
            new_hatchling = FollowerHatchling(offset_x, offset_y, new_hatchling_id)
            self.hatchlings.append(new_hatchling)
            play_sound("hatchling_added")

    def lose_hatchling(self):
        if self.hatchlings:
            self.hatchlings.pop()
            self.hatchlings_lost_count += 1
            play_sound("hatchling_lost")
            print(f"Hatchling lost! {len(self.hatchlings)} remaining.")

    def draw(self, surface):
        if not self.is_burrowing:
            # Draw leader hatchling
            leader_color = YELLOW if self.is_camouflaged else self.color
            pygame.draw.rect(surface, leader_color, self.rect)
            # Draw eye
            pygame.draw.circle(surface, BLACK, (self.rect.centerx + 5, self.rect.centery - 5), 3)

        # Draw follower hatchlings
        for hatchling in self.hatchlings:
            hatchling.draw(surface, self.is_camouflaged)

class FollowerHatchling(Entity):
    def __init__(self, x, y, hatchling_id):
        super().__init__(x, y, 18, 18, DARK_GREEN) # Slightly smaller
        self.hatchling_id = hatchling_id

    def draw(self, surface, is_camouflaged=False):
        draw_color = YELLOW if is_camouflaged else self.color
        pygame.draw.rect(surface, draw_color, self.rect)


class Obstacle(Entity):
    def __init__(self, x, y, width, height, obs_type):
        color_map = {
            OBSTACLE_WALL: GRAY,
            OBSTACLE_ROCK: BROWN,
            OBSTACLE_SHADE: DARK_GREEN,
            OBSTACLE_WATER: LIGHT_BLUE
        }
        super().__init__(x, y, width, height, color_map.get(obs_type, BLACK))
        self.type = obs_type

class Powerup(Entity):
    def __init__(self, x, y, pup_type):
        size = 15
        color_map = {
            POWERUP_COOLING_DEWDROP: BLUE,
            POWERUP_STAMINA_BERRY: RED,
            POWERUP_SEAWEED_CAMOUFLAGE: YELLOW,
            POWERUP_COMPANION_SHELL: PURPLE
        }
        super().__init__(x, y, size, size, color_map.get(pup_type, BLACK))
        self.type = pup_type

class Collectible(Entity):
    def __init__(self, x, y, col_type):
        size = 12
        color_map = {
            "ocean_fragment": YELLOW
        }
        super().__init__(x, y, size, size, color_map.get(col_type, BLACK))
        self.type = col_type

class Enemy(Entity):
    def __init__(self, x, y, width, height, color, enemy_type):
        super().__init__(x, y, width, height, color)
        self.type = enemy_type
        self.speed = 2
        self.patrol_path = []
        self.path_index = 0
        self.is_aggressive = False # Becomes aggressive if player detected
        self.detection_range = 100 # Default detection range

    def update(self, dt, player):
        if not self.patrol_path:
            return

        target_x, target_y = self.patrol_path[self.path_index]
        
        # Simple detection: if player is within range
        if not player.is_burrowing and not player.is_camouflaged:
            dist_to_player = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
            if dist_to_player < self.detection_range:
                self.is_aggressive = True
                target_x, target_y = player.rect.centerx, player.rect.centery
            else:
                self.is_aggressive = False
        else:
            self.is_aggressive = False # Cannot detect burrowed/camouflaged player

        current_speed = self.speed * (1.5 if self.is_aggressive else 1) # Faster when aggressive
        
        remaining_dist = self.move_towards(target_x, target_y, current_speed * dt * FPS)

        if not self.is_aggressive and remaining_dist < current_speed * dt * FPS: # Reached patrol point (approx)
            self.path_index = (self.path_index + 1) % len(self.patrol_path)


class SkitteringCrab(Enemy):
    def __init__(self, x, y, patrol_path):
        super().__init__(x, y, 25, 25, RED, ENEMY_SKITTERING_CRAB)
        self.speed = 1.5
        self.patrol_path = patrol_path
        self.detection_range = 120 # Wider detection for crab


class GameManager:
    def __init__(self):
        self.game_state = GAME_MENU
        self.player = None
        self.obstacles = []
        self.powerups = []
        self.enemies = []
        self.collectibles = []
        self.score = 0
        self.time_left = 0
        self.level_objectives = []
        self.level_start_time = 0

        self.load_level(LEVEL_DATA)

    def load_level(self, level_data):
        self.player = None
        self.obstacles = []
        self.powerups = []
        self.enemies = []
        self.collectibles = []
        self.score = 0
        self.time_left = level_data["time_limit"]
        self.level_objectives = level_data["objectives"]
        self.collected_fragments = 0 # Specific tracker for the L1 objective

        # Player Spawn
        for spawn in level_data["spawn_points"]:
            if spawn["type"] == "player":
                self.player = PlayerHatchling(spawn["x"], spawn["y"])
                self.player.add_hatchling() # Add a couple of initial followers
                self.player.add_hatchling()
                break

        # Obstacles
        for obs_data in level_data["obstacles"]:
            self.obstacles.append(Obstacle(obs_data["x"], obs_data["y"], obs_data["width"], obs_data["height"], obs_data["type"]))

        # Powerups
        for pup_data in level_data["powerups"]:
            self.powerups.append(Powerup(pup_data["x"], pup_data["y"], pup_data["type"]))

        # Enemies
        for enemy_data in level_data["enemies"]:
            if enemy_data["type"] == ENEMY_SKITTERING_CRAB:
                self.enemies.append(SkitteringCrab(enemy_data["x"], enemy_data["y"], enemy_data["patrol_path"]))
            # Add other enemy types here if they were in level_data
            
        # Collectibles
        for col_data in level_data["collectibles"]:
            if col_data["type"] == "ocean_fragment":
                self.collectibles.append(Collectible(col_data["x"], col_data["y"], col_data["type"]))

        self.ocean_goal_rect = None
        for obj in self.level_objectives:
            if obj["type"] == "reach_area" and obj["name"] == "ocean":
                self.ocean_goal_rect = pygame.Rect(obj["x"], obj["y"], obj["width"], obj["height"])
                break


    def handle_input(self, event, dt):
        if self.game_state == GAME_MENU:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    self.game_state = GAME_PLAYING
                    self.level_start_time = pygame.time.get_ticks()
        elif self.game_state == GAME_PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e: # Burrow
                    self.player.burrow()
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT: # Shell Sprint
                    self.player.shell_sprint()
                if event.key == pygame.K_f: # Hydro Glide (assuming player is in water)
                    in_water = False
                    for obs in self.obstacles:
                        if obs.type == OBSTACLE_WATER and self.player.rect.colliderect(obs.rect):
                            in_water = True
                            break
                    self.player.hydro_glide(in_water)
        elif self.game_state == GAME_OVER or self.game_state == GAME_WIN:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    self.load_level(LEVEL_DATA) # Restart current level
                    self.game_state = GAME_MENU


    def update(self, dt):
        if self.game_state == GAME_PLAYING:
            current_time_ms = pygame.time.get_ticks()
            elapsed_time = (current_time_ms - self.level_start_time) / 1000
            self.time_left = LEVEL_DATA["time_limit"] - elapsed_time
            
            if self.time_left <= 0:
                self.game_state = GAME_OVER
                play_sound("game_over")
                return

            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = 1

            # Normalize diagonal movement
            if dx != 0 and dy != 0:
                length = math.hypot(dx, dy)
                dx /= length
                dy /= length
            
            self.player.move(dx, dy, self.obstacles)
            self.player.update(dt, self.obstacles, self.enemies)

            for enemy in self.enemies:
                enemy.update(dt, self.player)
                
                # Enemy collision with player (leader)
                if not self.player.is_burrowing and self.player.rect.colliderect(enemy.rect) and not self.player.is_camouflaged:
                    self.player.lose_hatchling()
                    # Push player back slightly to avoid multiple hits
                    self.player.rect.x -= dx * 30
                    self.player.rect.y -= dy * 30
                    if len(self.player.hatchlings) == 0:
                        self.game_state = GAME_OVER
                        play_sound("game_over")
                        return

                # Enemy collision with followers
                for hatchling in list(self.player.hatchlings): # Iterate over a copy to allow removal
                    if hatchling.rect.colliderect(enemy.rect) and not self.player.is_burrowing and not self.player.is_camouflaged:
                        self.player.lose_hatchling()
                        if len(self.player.hatchlings) == 0:
                            self.game_state = GAME_OVER
                            play_sound("game_over")
                            return

            # Powerup collection
            for powerup in list(self.powerups):
                if self.player.rect.colliderect(powerup.rect):
                    self.player.apply_powerup(powerup.type)
                    self.powerups.remove(powerup)

            # Collectible collection
            for collectible in list(self.collectibles):
                if self.player.rect.colliderect(collectible.rect):
                    if collectible.type == "ocean_fragment":
                        self.player.ocean_fragments_collected += 1
                        play_sound("collect_fragment")
                    self.collectibles.remove(collectible)

            # Check win condition
            win_conditions_met = True
            for obj in self.level_objectives:
                if obj["type"] == "collect" and obj["target"] == "ocean_fragment":
                    if self.player.ocean_fragments_collected < obj["count"]:
                        win_conditions_met = False
                        break
                elif obj["type"] == "reach_area" and obj["name"] == "ocean":
                    if not self.player.rect.colliderect(self.ocean_goal_rect):
                        win_conditions_met = False
                        break
            
            if win_conditions_met:
                self.game_state = GAME_WIN
                play_sound("level_complete")
                # Calculate final score
                self.score = (len(self.player.hatchlings) + 1) * 100 # Hatchlings remaining
                self.score += self.player.ocean_fragments_collected * 50 # Fragments
                self.score += int(self.time_left * 2) # Time bonus
                self.score -= self.player.hatchlings_lost_count * 25 # Penalty for lost hatchlings


    def draw(self, surface):
        surface.fill(LIGHT_GRAY) # Sandy background

        for obs in self.obstacles:
            obs.draw(surface)
        
        for powerup in self.powerups:
            powerup.draw(surface)
            
        for collectible in self.collectibles:
            collectible.draw(surface)

        for enemy in self.enemies:
            enemy.draw(surface)
            if enemy.is_aggressive:
                # Draw a simple alert indicator
                pygame.draw.circle(surface, ORANGE, (enemy.rect.centerx, enemy.rect.top - 10), 5)


        if self.player:
            self.player.draw(surface)
            
            # Draw player stats HUD
            self.draw_hud(surface)

        if self.game_state == GAME_MENU:
            self.draw_menu(surface)
        elif self.game_state == GAME_OVER:
            self.draw_game_over(surface)
        elif self.game_state == GAME_WIN:
            self.draw_game_win(surface)

    def draw_hud(self, surface):
        # Hatchlings remaining
        hatchlings_text = font.render(f"Hatchlings: {len(self.player.hatchlings) + 1}", True, BLACK)
        surface.blit(hatchlings_text, (10, 10))

        # Ocean Fragments
        fragments_text = font.render(f"Fragments: {self.player.ocean_fragments_collected}/{LEVEL_DATA['objectives'][0]['count']}", True, BLACK)
        surface.blit(fragments_text, (10, 40))

        # Time left
        time_text = font.render(f"Time: {int(self.time_left)}s", True, BLACK)
        surface.blit(time_text, (SCREEN_WIDTH - time_text.get_width() - 10, 10))

        # Stamina Bar
        stamina_bar_width = 100
        stamina_bar_height = 15
        stamina_ratio = self.player.stamina / self.player.max_stamina
        pygame.draw.rect(surface, GRAY, (10, 70, stamina_bar_width, stamina_bar_height), 2)
        pygame.draw.rect(surface, BLUE, (10, 70, stamina_bar_width * stamina_ratio, stamina_bar_height))
        stamina_text = font.render("Stamina", True, BLACK)
        surface.blit(stamina_text, (10 + stamina_bar_width + 5, 68))

        # Heat Bar
        heat_bar_width = 100
        heat_bar_height = 15
        heat_ratio = self.player.heat / self.player.max_heat
        pygame.draw.rect(surface, GRAY, (10, 95, heat_bar_width, heat_bar_height), 2)
        pygame.draw.rect(surface, ORANGE, (10, 95, heat_bar_width * heat_ratio, heat_bar_height))
        heat_text = font.render("Heat", True, BLACK)
        surface.blit(heat_text, (10 + heat_bar_width + 5, 93))

    def draw_menu(self, surface):
        surface.fill(LIGHT_BLUE)
        title = big_font.render("Tidebound: Hatchling's Journey", True, BLACK)
        start_text = medium_font.render("Press SPACE to Start", True, BLACK)
        controls_text = font.render("Move: WASD/Arrows | Burrow: E | Sprint: SHIFT | Glide (water): F", True, BLACK)
        
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 3))
        surface.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2))
        surface.blit(controls_text, (SCREEN_WIDTH // 2 - controls_text.get_width() // 2, SCREEN_HEIGHT // 2 + 70))


    def draw_game_over(self, surface):
        surface.fill(RED)
        game_over_text = big_font.render("GAME OVER", True, WHITE)
        retry_text = medium_font.render("Press SPACE to Restart", True, WHITE)
        surface.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 3))
        surface.blit(retry_text, (SCREEN_WIDTH // 2 - retry_text.get_width() // 2, SCREEN_HEIGHT // 2))

    def draw_game_win(self, surface):
        surface.fill(GREEN)
        win_text = big_font.render("LEVEL COMPLETE!", True, WHITE)
        score_text = medium_font.render(f"Final Score: {self.score}", True, WHITE)
        retry_text = medium_font.render("Press SPACE for Menu", True, WHITE)
        surface.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 3))
        surface.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
        surface.blit(retry_text, (SCREEN_WIDTH // 2 - retry_text.get_width() // 2, SCREEN_HEIGHT // 2 + 70))


# --- Main Game Loop ---
def main():
    game_manager = GameManager()

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0 # Delta time in seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game_manager.handle_input(event, dt)

        game_manager.update(dt)
        game_manager.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
