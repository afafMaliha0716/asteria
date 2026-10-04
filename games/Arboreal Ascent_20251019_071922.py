
import pygame
import sys
import math
import random

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 150, 0)
DARK_GREEN = (0, 100, 0)
BROWN = (139, 69, 19)
GREY = (150, 150, 150)
RED = (200, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 200)
ORANGE = (255, 165, 0)
LIGHT_BLUE = (173, 216, 230) # For Canopy Glide effect
PURPLE = (128, 0, 128) # For Root Grapple points
DARK_RED = (150, 0, 0) # For Thorns/Fungi

# Game States
MENU = 0
PLAYING = 1
GAME_OVER = 2

# --- Level 1 Data (parsed from JSON, simplified for direct use) ---
LEVEL_DATA = {
    "level_number": 1,
    "name": "Level 1",
    "description": "Basic level 1",
    "size": {
        "width": SCREEN_WIDTH, # Use screen dimensions for simplicity
        "height": SCREEN_HEIGHT
    },
    "spawn_points": [
        {"x": 50, "y": 50, "type": "player"}
    ],
    "obstacles": [
        {"x": 200, "y": 200, "width": 50, "height": 50, "type": "wall"},
        {"x": 500, "y": 300, "width": 30, "height": 30, "type": "rock"},
        {"x": 350, "y": 100, "width": 20, "height": 20, "type": "fungi"}, # Example static enemy
        {"x": 600, "y": 500, "width": 40, "height": 40, "type": "thorn"} # Example static enemy
    ],
    "powerups": [
        {"x": 300, "y": 150, "type": "sunpetal"}, # Mapped from "health"
        {"x": 600, "y": 400, "type": "wind_blossom"} # Mapped from "speed"
    ],
    "enemies": [
        {"x": 400, "y": 300, "type": "grub", "patrol_path": [[400, 300], [450, 300], [400,350]]} # Mapped from "basic" to Grub for L1
    ],
    "objectives": [
        {"type": "collect", "target": "essence", "count": 3} # Mapped from "coins" to "essence"
    ],
    "difficulty": "easy",
    "time_limit": 120
}

# --- Game Classes ---

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(x, y))
        self.base_speed = 3
        self.speed = self.base_speed
        self.dx = 0
        self.dy = 0
        self.photosynthetic_energy = 100
        self.max_energy = 100
        self.energy_recharge_rate = 0.05 # per frame
        self.energy_sunlit_boost = 0.1 # additional in sunlit patches (not implemented in L1 directly)

        # Ability cooldowns & durations (in frames)
        self.root_dash_cooldown = 0
        self.root_dash_duration = 0
        self.canopy_glide_duration = 0
        self.seed_burst_cooldown = 0
        self.root_extend_duration = 0
        self.root_anchor_duration = 0
        self.root_grapple_cooldown = 0
        
        # Ability costs
        self.root_dash_cost = 10
        self.root_extend_cost = 15
        self.canopy_glide_cost_per_frame = 5 / FPS 
        self.seed_burst_cost = 20
        self.root_grapple_cost = 25

        # Ability enhancements from powerups
        self.growth_sprout_active = False
        self.growth_sprout_timer = 0
        self.wind_blossom_active = False
        self.wind_blossom_timer = 0
        self.drought_charm_active = False
        self.drought_charm_timer = 0

        self.grapple_target = None
        self.is_anchored = False # Added flag for anchor state

    def update(self, obstacles, enemies, grapple_points):
        # Cooldowns
        self.root_dash_cooldown = max(0, self.root_dash_cooldown - 1)
        self.seed_burst_cooldown = max(0, self.seed_burst_cooldown - 1)
        self.root_grapple_cooldown = max(0, self.root_grapple_cooldown - 1)
        
        # Energy regeneration
        if not self.is_anchored: # Default slow regeneration
            self.photosynthetic_energy = min(self.max_energy, self.photosynthetic_energy + self.energy_recharge_rate)
        
        # Powerup timers
        if self.growth_sprout_active:
            self.growth_sprout_timer -= 1
            if self.growth_sprout_timer <= 0:
                self.growth_sprout_active = False
        
        if self.wind_blossom_active:
            self.wind_blossom_timer -= 1
            if self.wind_blossom_timer <= 0:
                self.wind_blossom_active = False
                self.speed = self.base_speed # Reset speed if glide isn't active
        
        if self.drought_charm_active:
            self.drought_charm_timer -= 1
            if self.drought_charm_timer <= 0:
                self.drought_charm_active = False
            else:
                self.photosynthetic_energy = min(self.max_energy, self.photosynthetic_energy + self.energy_recharge_rate * 2) # Doubled regen

        # Ability durations
        if self.root_dash_duration > 0:
            self.root_dash_duration -= 1
            if self.root_dash_duration <= 0:
                self.speed = self.base_speed # Reset speed after dash
        
        if self.canopy_glide_duration > 0:
            self.canopy_glide_duration -= 1
            self.photosynthetic_energy -= self.canopy_glide_cost_per_frame
            if self.photosynthetic_energy <= 0:
                self.canopy_glide_duration = 0 # Force end glide if no energy
            
            self.speed = self.base_speed * (1.5 if not self.wind_blossom_active else 2.5) # Glide speed boost
            if self.canopy_glide_duration <= 0:
                self.speed = self.base_speed
        
        if self.root_extend_duration > 0:
            self.root_extend_duration -= 1
        
        if self.is_anchored:
            self.root_anchor_duration -= 1
            self.dx = self.dy = 0 # Player is immobile
            self.photosynthetic_energy = min(self.max_energy, self.photosynthetic_energy + self.energy_recharge_rate * 3) # Faster regen when anchored
            if self.root_anchor_duration <= 0:
                self.is_anchored = False
                self.dx = self.dy = 0 # Ensure stopped after un-anchor
        
        if self.grapple_target:
            self._grapple_to_target()
        elif not self.is_anchored: # Only move if not anchored or grappling
            # Handle movement
            self.rect.x += self.dx * self.speed
            self.rect.y += self.dy * self.speed

        # Collision with walls/rocks
        self._handle_collisions(obstacles)
        
    def _handle_collisions(self, obstacles):
        # Store original position to revert if collision
        original_x, original_y = self.rect.topleft

        # Handle X-axis movement and collision
        self.rect.x += self.dx * self.speed
        for obj in obstacles:
            if self.rect.colliderect(obj.rect):
                if isinstance(obj, Wall):
                    if self.dx > 0: self.rect.right = obj.rect.left
                    if self.dx < 0: self.rect.left = obj.rect.right
                elif isinstance(obj, Rock) and obj.can_be_pushed and self.root_extend_duration > 0:
                    # Player pushing rock
                    push_force = 2 if self.growth_sprout_active else 1
                    if self.dx > 0: obj.rect.x += push_force
                    if self.dx < 0: obj.rect.x -= push_force
                    # If rock hits another wall, revert its position
                    for other_obj in obstacles:
                        if other_obj != obj and obj.rect.colliderect(other_obj.rect) and isinstance(other_obj, Wall):
                            # Revert rock position if it hit something
                            if self.dx > 0: obj.rect.right = other_obj.rect.left
                            if self.dx < 0: obj.rect.left = other_obj.rect.right
                    # After pushing, player stops against the rock
                    if self.dx > 0: self.rect.right = obj.rect.left
                    if self.dx < 0: self.rect.left = obj.rect.right
                elif isinstance(obj, Rock): # Rock not pushed (e.g., extend not active)
                    if self.dx > 0: self.rect.right = obj.rect.left
                    if self.dx < 0: self.rect.left = obj.rect.right
        
        # Handle Y-axis movement and collision
        self.rect.y += self.dy * self.speed
        for obj in obstacles:
            if self.rect.colliderect(obj.rect):
                if isinstance(obj, Wall):
                    if self.dy > 0: self.rect.bottom = obj.rect.top
                    if self.dy < 0: self.rect.top = obj.rect.bottom
                elif isinstance(obj, Rock) and obj.can_be_pushed and self.root_extend_duration > 0:
                    push_force = 2 if self.growth_sprout_active else 1
                    if self.dy > 0: obj.rect.y += push_force
                    if self.dy < 0: obj.rect.y -= push_force
                    for other_obj in obstacles:
                        if other_obj != obj and obj.rect.colliderect(other_obj.rect) and isinstance(other_obj, Wall):
                            if self.dy > 0: obj.rect.bottom = other_obj.rect.top
                            if self.dy < 0: obj.rect.top = other_obj.rect.bottom
                    if self.dy > 0: self.rect.bottom = obj.rect.top
                    if self.dy < 0: self.rect.top = obj.rect.bottom
                elif isinstance(obj, Rock):
                    if self.dy > 0: self.rect.bottom = obj.rect.top
                    if self.dy < 0: self.rect.top = obj.rect.bottom

    def move(self, dx, dy):
        if self.is_anchored or self.grapple_target: # Cannot move if anchored or grappling
            return
        self.dx = dx
        self.dy = dy

    def stop_move_x(self):
        self.dx = 0
    
    def stop_move_y(self):
        self.dy = 0

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        
        # Indicate active abilities
        if self.root_dash_duration > 0:
            pygame.draw.circle(screen, ORANGE, self.rect.center, 15, 2) # Dash indicator
        if self.canopy_glide_duration > 0:
            pygame.draw.circle(screen, LIGHT_BLUE, self.rect.center, 15, 2) # Glide indicator
        if self.root_extend_duration > 0:
            pygame.draw.circle(screen, BROWN, self.rect.center, 15, 2) # Root extend indicator
        if self.is_anchored:
            pygame.draw.rect(screen, DARK_GREEN, self.rect.inflate(10,10), 2) # Anchor indicator

    def root_dash(self):
        if self.root_dash_cooldown <= 0 and self.photosynthetic_energy >= self.root_dash_cost:
            self.photosynthetic_energy -= self.root_dash_cost
            self.speed = self.base_speed * (2 if not self.growth_sprout_active else 3) # Dash speed boost
            self.root_dash_duration = FPS * (0.5 if not self.growth_sprout_active else 0.75) # 0.5 or 0.75 seconds
            self.root_dash_cooldown = FPS * 2 # 2 second cooldown
            
    def root_extend(self):
        # Root Extend is primarily about interacting with objects like pushing rocks
        if self.photosynthetic_energy >= self.root_extend_cost:
            self.photosynthetic_energy -= self.root_extend_cost
            self.root_extend_duration = FPS * (1 if not self.growth_sprout_active else 1.5) # 1 or 1.5 seconds

    def root_anchor(self):
        # Anchor consumes energy and makes player immobile while boosting regen
        if self.photosynthetic_energy >= self.root_extend_cost: # Same cost as extend for simplicity
            self.photosynthetic_energy -= self.root_extend_cost
            self.is_anchored = True
            self.root_anchor_duration = FPS * (2 if not self.growth_sprout_active else 3) # 2 or 3 seconds
            self.dx = self.dy = 0 # Stop movement

    def canopy_glide(self):
        if self.photosynthetic_energy >= self.canopy_glide_cost_per_frame * FPS and self.canopy_glide_duration <= 0:
            self.canopy_glide_duration = FPS * (1 if not self.wind_blossom_active else 2) # 1 or 2 seconds

    def seed_burst(self, game_state):
        if self.seed_burst_cooldown <= 0 and self.photosynthetic_energy >= self.seed_burst_cost:
            self.photosynthetic_energy -= self.seed_burst_cost
            new_plant = SeedPlant(self.rect.centerx, self.rect.centery)
            game_state.all_sprites.add(new_plant)
            game_state.obstacles.add(new_plant) # Plants act as temporary obstacles
            game_state.temp_objects.append(new_plant) # To manage its lifetime
            self.seed_burst_cooldown = FPS * 3 # 3 second cooldown

    def root_grapple(self, mouse_pos, grapple_points):
        if self.root_grapple_cooldown <= 0 and self.photosynthetic_energy >= self.root_grapple_cost:
            closest_gp = None
            min_dist = float('inf')
            
            for gp in grapple_points:
                dist = math.hypot(mouse_pos[0] - gp.rect.centerx, mouse_pos[1] - gp.rect.centery)
                if dist < 200: # Grapple range
                    if dist < min_dist:
                        min_dist = dist
                        closest_gp = gp
            
            if closest_gp:
                self.photosynthetic_energy -= self.root_grapple_cost
                self.grapple_target = closest_gp.rect.center
                self.root_grapple_cooldown = FPS * 4 # 4 second cooldown
                self.dx = self.dy = 0 # Stop any current movement

    def _grapple_to_target(self):
        if not self.grapple_target:
            return

        target_x, target_y = self.grapple_target
        dx = target_x - self.rect.centerx
        dy = target_y - self.rect.centery
        distance = math.hypot(dx, dy)

        grapple_speed = 15 # Fast grapple speed
        
        if distance > grapple_speed:
            self.rect.centerx += int(dx / distance * grapple_speed)
            self.rect.centery += int(dy / distance * grapple_speed)
        else:
            self.rect.center = self.grapple_target
            self.grapple_target = None # Arrived

class SeedPlant(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((25, 25))
        self.image.fill(DARK_GREEN)
        self.rect = self.image.get_rect(center=(x, y))
        self.lifetime = FPS * 5 # 5 seconds
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime * 1000:
            self.kill() # Remove itself after lifetime

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect(topleft=(x, y))

class Rock(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREY)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.can_be_pushed = True # For Root Extend

class GrapplePoint(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((15, 15), pygame.SRCALPHA)
        pygame.draw.circle(self.image, PURPLE, (7, 7), 7)
        self.rect = self.image.get_rect(center=(x, y))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type="basic", patrol_path=None):
        super().__init__()
        self.enemy_type = enemy_type
        self.damage_on_contact = 5 # Photosynthetic Energy drain per second (converted to per frame)
        self.speed = 1.5

        if enemy_type == "grub":
            self.image = pygame.Surface((25, 25))
            self.image.fill(RED)
            self.rect = self.image.get_rect(center=(x, y))
            self.active_duration = FPS * 3 # Active for 3 seconds
            self.inactive_duration = FPS * 2 # Inactive for 2 seconds (underground)
            self.is_active = True
            self.timer_start = pygame.time.get_ticks()
            self.original_pos = (x, y)
            self.invisible_offset = 50 # Move off-screen when inactive
            
            self.patrol_path = patrol_path if patrol_path else []
            self.path_index = 0
            if self.patrol_path:
                self.target_pos = list(self.patrol_path[self.path_index])
            else:
                self.target_pos = [self.rect.centerx, self.rect.centery] # Stay put
        
        elif enemy_type == "fungi": # Parasitic Fungi
            self.image = pygame.Surface((30, 30))
            self.image.fill(DARK_RED)
            self.rect = self.image.get_rect(topleft=(x,y))
            self.damage_on_contact = 3 # Slower drain
            self.speed = 0 # Static

        elif enemy_type == "thorn": # Aggressive Thorns/Vines
            self.image = pygame.Surface((40, 40))
            self.image.fill((100, 0, 0)) # Darker red for thorns
            self.rect = self.image.get_rect(topleft=(x,y))
            self.damage_on_contact = 10 # Higher drain
            self.speed = 0 # Static for now

        elif enemy_type == "blight": # The Blight (not in L1 but included for completeness)
            self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
            self.image.fill((50, 0, 50, 150)) # Translucent purple-black
            self.rect = self.image.get_rect(topleft=(x,y))
            self.damage_on_contact = 20 # Rapid drain
            self.expansion_rate = 0.5 # Pixels per frame
            self.speed = 0 # Static, but expands

    def update(self, player_rect, obstacles):
        if self.enemy_type == "grub":
            self._update_grub(obstacles) # Pass obstacles for collision detection
        elif self.enemy_type == "blight":
            self._update_blight()
        # Other enemies are static and don't require specific update logic here

    def _update_grub(self, obstacles):
        current_time = pygame.time.get_ticks()
        if self.is_active:
            # Active state: Patrol
            target_x, target_y = self.target_pos
            dx = target_x - self.rect.centerx
            dy = target_y - self.rect.centery
            distance = math.hypot(dx, dy)

            if distance > self.speed:
                self.rect.centerx += int(dx / distance * self.speed)
                self.rect.centery += int(dy / distance * self.speed)
                
                # Simple collision: if hit obstacle, turn around (only works well for 2-point path)
                collided = pygame.sprite.spritecollideany(self, obstacles)
                if collided and not isinstance(collided, Rock): # Ignore rocks for simplicity
                    self.path_index = (self.path_index + 1) % len(self.patrol_path)
                    self.target_pos = list(self.patrol_path[self.path_index])

            else:
                self.rect.center = self.target_pos
                self.path_index = (self.path_index + 1) % len(self.patrol_path)
                self.target_pos = list(self.patrol_path[self.path_index])
            
            if (current_time - self.timer_start) / 1000 > self.active_duration / FPS:
                self.is_active = False
                self.timer_start = current_time
                self.rect.center = (self.original_pos[0], self.original_pos[1] + self.invisible_offset) # Move off-screen
                
        else:
            # Inactive state: Invisible, waiting
            if (current_time - self.timer_start) / 1000 > self.inactive_duration / FPS:
                self.is_active = True
                self.timer_start = current_time
                self.rect.center = self.original_pos # Reappear at original spot
                if self.patrol_path: # Reset patrol for consistency
                    self.path_index = 0
                    self.target_pos = list(self.patrol_path[self.path_index])

    def _update_blight(self):
        # The Blight slowly expands
        original_center = self.rect.center
        self.rect.width += self.expansion_rate
        self.rect.height += self.expansion_rate
        self.rect.center = original_center

class Powerup(pygame.sprite.Sprite):
    def __init__(self, x, y, powerup_type):
        super().__init__()
        self.powerup_type = powerup_type
        self.image = pygame.Surface((15, 15))
        self.rect = self.image.get_rect(center=(x, y))

        if powerup_type == "sunpetal":
            self.image.fill(YELLOW)
        elif powerup_type == "growth_sprout":
            self.image.fill(ORANGE)
        elif powerup_type == "wind_blossom":
            self.image.fill(LIGHT_BLUE)
        elif powerup_type == "drought_charm":
            self.image.fill(BLUE)

class Essence(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(WHITE) # Essences glow
        self.rect = self.image.get_rect(center=(x, y))

class GameState:
    def __init__(self):
        self.current_state = MENU
        self.level_data = LEVEL_DATA
        self.player = None
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.essences = pygame.sprite.Group()
        self.grapple_points = pygame.sprite.Group()
        self.temp_objects = [] # For SeedBurst plants, etc.

        self.score = 0
        self.essences_collected = 0
        self.total_essences_in_level = 0
        self.level_start_time = 0
        self.time_limit = self.level_data.get("time_limit", 120)
        self.game_over_reason = ""

        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

    def load_level(self):
        self.all_sprites.empty()
        self.obstacles.empty()
        self.enemies.empty()
        self.powerups.empty()
        self.essences.empty()
        self.grapple_points.empty()
        self.temp_objects = []

        self.score = 0
        self.essences_collected = 0
        self.total_essences_in_level = 0
        self.level_start_time = pygame.time.get_ticks()

        # Player spawn
        for sp in self.level_data["spawn_points"]:
            if sp["type"] == "player":
                self.player = Player(sp["x"], sp["y"])
                self.all_sprites.add(self.player)
                break
        
        # Obstacles and static enemies (fungi, thorns)
        for obs in self.level_data["obstacles"]:
            if obs["type"] == "wall":
                wall = Wall(obs["x"], obs["y"], obs["width"], obs["height"])
                self.all_sprites.add(wall)
                self.obstacles.add(wall)
            elif obs["type"] == "rock":
                rock = Rock(obs["x"], obs["y"], obs["width"], obs["height"])
                self.all_sprites.add(rock)
                self.obstacles.add(rock)
            elif obs["type"] == "fungi" or obs["type"] == "thorn" or obs["type"] == "blight":
                enemy = Enemy(obs["x"], obs["y"], obs["type"])
                self.all_sprites.add(enemy)
                self.enemies.add(enemy)

        # Powerups
        for pu in self.level_data["powerups"]:
            powerup = Powerup(pu["x"], pu["y"], pu["type"])
            self.all_sprites.add(powerup)
            self.powerups.add(powerup)

        # Moving enemies
        for en in self.level_data["enemies"]:
            enemy = Enemy(en["x"], en["y"], en["type"], patrol_path=en.get("patrol_path"))
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)

        # Collectibles (Essences)
        for obj_spec in self.level_data["objectives"]:
            if obj_spec["type"] == "collect" and obj_spec["target"] == "essence":
                self.total_essences_in_level = obj_spec["count"]
                for _ in range(self.total_essences_in_level):
                    while True: # Try to place essence without overlap
                        ex = random.randint(50, SCREEN_WIDTH - 50)
                        ey = random.randint(50, SCREEN_HEIGHT - 50)
                        essence = Essence(ex, ey)
                        # Check for collision with existing sprites
                        collisions = pygame.sprite.spritecollide(essence, self.all_sprites, False)
                        if not collisions: # If no collisions, place it
                            self.all_sprites.add(essence)
                            self.essences.add(essence)
                            break
                        else:
                            essence.kill() # Remove the temporary essence

        # Grapple points (not specified in L1 data, but good to add for testing)
        gp1 = GrapplePoint(100, 300)
        gp2 = GrapplePoint(700, 100)
        self.all_sprites.add(gp1, gp2)
        self.grapple_points.add(gp1, gp2)


    def update(self):
        if self.current_state == PLAYING:
            current_time = pygame.time.get_ticks()
            elapsed_time_seconds = (current_time - self.level_start_time) // 1000
            
            # Check time limit
            if elapsed_time_seconds >= self.time_limit:
                self.current_state = GAME_OVER
                self.game_over_reason = "Time's Up!"
                return

            self.player.update(self.obstacles, self.enemies, self.grapple_points)
            self.enemies.update(self.player.rect, self.obstacles)
            
            # Update temporary objects (e.g., SeedBurst plants)
            for obj in list(self.temp_objects): # Iterate over a copy to allow modification
                obj.update()
                if not obj.alive():
                    self.temp_objects.remove(obj)
                    self.obstacles.remove(obj) # Remove from obstacles group too
                    self.all_sprites.remove(obj)

            # Player-enemy collision
            enemy_collisions = pygame.sprite.spritecollide(self.player, self.enemies, False)
            for enemy in enemy_collisions:
                if isinstance(enemy, Enemy):
                    if enemy.enemy_type == "grub" and not enemy.is_active:
                        continue # Grubs don't hurt when inactive/underground
                    
                    self.player.photosynthetic_energy -= enemy.damage_on_contact / FPS # Damage over time
                    if self.player.photosynthetic_energy <= 0:
                        self.current_state = GAME_OVER
                        self.game_over_reason = "Photosynthetic Energy depleted!"
                        return
                    
            # Player-powerup collision
            powerup_collisions = pygame.sprite.spritecollide(self.player, self.powerups, True)
            for powerup in powerup_collisions:
                self.score += 50
                if powerup.powerup_type == "sunpetal":
                    self.player.photosynthetic_energy = self.player.max_energy # Instantly refills
                elif powerup.powerup_type == "growth_sprout":
                    self.player.growth_sprout_active = True
                    self.player.growth_sprout_timer = FPS * 10 # 10 seconds
                elif powerup.powerup_type == "wind_blossom":
                    self.player.wind_blossom_active = True
                    self.player.wind_blossom_timer = FPS * 10 # 10 seconds
                    self.player.speed = self.player.base_speed * 1.5 # Immediate speed boost
                elif powerup.powerup_type == "drought_charm":
                    self.player.drought_charm_active = True
                    self.player.drought_charm_timer = FPS * 15 # 15 seconds

            # Player-essence collision
            essence_collisions = pygame.sprite.spritecollide(self.player, self.essences, True)
            for essence in essence_collisions:
                self.essences_collected += 1
                self.score += 100
                if self.essences_collected >= self.total_essences_in_level:
                    self.current_state = GAME_OVER # Level completed!
                    self.game_over_reason = "Level Completed!"
                    self._calculate_final_score(elapsed_time_seconds)

    def _calculate_final_score(self, elapsed_time_seconds):
        # Base score from essences collected
        # Completion Time: Bonus for finishing quickly (less time = more points)
        time_bonus = max(0, (self.time_limit - elapsed_time_seconds) * 5)
        self.score += time_bonus
        
        # Photosynthetic Efficiency: Bonus for high energy remaining
        energy_bonus = int((self.player.photosynthetic_energy / self.player.max_energy) * 200)
        self.score += energy_bonus

    def draw(self, screen):
        if self.current_state == MENU:
            self._draw_menu(screen)
        elif self.current_state == PLAYING:
            self._draw_playing(screen)
        elif self.current_state == GAME_OVER:
            self._draw_game_over(screen)

    def _draw_menu(self, screen):
        screen.fill(DARK_GREEN)
        title_text = self.font.render("Arboreal Ascent", True, WHITE)
        instruction_text = self.small_font.render("Press SPACE to Start", True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

    def _draw_playing(self, screen):
        screen.fill(GREEN) # Forest background
        self.all_sprites.draw(screen)

        # Draw UI
        self._draw_ui(screen)
        
        # Draw root grapple line if active
        if self.player.grapple_target:
            pygame.draw.line(screen, PURPLE, self.player.rect.center, self.player.grapple_target, 2)


    def _draw_ui(self, screen):
        # Score
        score_text = self.small_font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Essences
        essence_text = self.small_font.render(f"Essence: {self.essences_collected}/{self.total_essences_in_level}", True, WHITE)
        screen.blit(essence_text, (10, 40))

        # Time Left
        elapsed_time_seconds = (pygame.time.get_ticks() - self.level_start_time) // 1000
        time_left = max(0, self.time_limit - elapsed_time_seconds)
        time_text = self.small_font.render(f"Time: {time_left}s", True, WHITE)
        screen.blit(time_text, (SCREEN_WIDTH - time_text.get_width() - 10, 10))

        # Player Energy Bar (top center of screen)
        energy_bar_width = 200
        energy_bar_height = 15
        energy_bar_x = (SCREEN_WIDTH - energy_bar_width) // 2
        energy_bar_y = 10
        pygame.draw.rect(screen, BLACK, (energy_bar_x, energy_bar_y, energy_bar_width, energy_bar_height), 2)
        pygame.draw.rect(screen, YELLOW, (energy_bar_x + 2, energy_bar_y + 2,
                                         (energy_bar_width - 4) * (self.player.photosynthetic_energy / self.player.max_energy),
                                         energy_bar_height - 4))
        energy_label = self.small_font.render("Photosynthetic Energy", True, WHITE)
        screen.blit(energy_label, (energy_bar_x + energy_bar_width // 2 - energy_label.get_width() // 2, energy_bar_y + energy_bar_height + 5))

        # Ability Cooldowns (Bottom left)
        cooldown_y = SCREEN_HEIGHT - 60
        cooldown_labels = [
            ("Dash (Q)", self.player.root_dash_cooldown),
            ("Extend (E)", self.player.root_extend_duration),
            ("Anchor (A)", self.player.root_anchor_duration),
            ("Glide (R)", self.player.canopy_glide_duration),
            ("Seed Burst (F)", self.player.seed_burst_cooldown),
            ("Grapple (L-Click)", self.player.root_grapple_cooldown)
        ]
        
        for i, (label, cooldown) in enumerate(cooldown_labels):
            display_cooldown = max(0, math.ceil(cooldown / FPS)) # Convert to seconds
            # Use specific color for active duration instead of just 'not cooldown'
            if "Extend" in label and self.player.root_extend_duration > 0:
                 color = ORANGE
            elif "Anchor" in label and self.player.is_anchored:
                color = DARK_GREEN
            elif "Glide" in label and self.player.canopy_glide_duration > 0:
                color = LIGHT_BLUE
            elif cooldown > 0:
                color = GREY
            else:
                color = WHITE

            cooldown_text = self.small_font.render(f"{label}: {display_cooldown}s", True, color)
            screen.blit(cooldown_text, (10, cooldown_y + i * 20))


    def _draw_game_over(self, screen):
        screen.fill(DARK_RED)
        game_over_text = self.font.render("GAME OVER", True, WHITE)
        reason_text = self.small_font.render(self.game_over_reason, True, WHITE)
        final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        restart_text = self.small_font.render("Press R to Restart, Q to Quit", True, WHITE)

        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 70))
        screen.blit(reason_text, (SCREEN_WIDTH // 2 - reason_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
        screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 30))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 80))

# --- Main Game Loop ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Arboreal Ascent")
    clock = pygame.time.Clock()

    game_state = GameState()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game_state.current_state == MENU:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game_state.current_state = PLAYING
                    game_state.load_level() # Load the level when starting
            
            elif game_state.current_state == PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        game_state.player.move(0, -1)
                    if event.key == pygame.K_s:
                        game_state.player.move(0, 1)
                    if event.key == pygame.K_a:
                        # 'A' is for Anchor, 'D' for right. Original 'A' movement overridden
                        game_state.player.move(-1, game_state.player.dy)
                    if event.key == pygame.K_d:
                        game_state.player.move(1, game_state.player.dy)
                    
                    # Abilities
                    if event.key == pygame.K_q: # Root Dash
                        game_state.player.root_dash()
                    if event.key == pygame.K_e: # Root Extend
                        game_state.player.root_extend()
                    if event.key == pygame.K_a and game_state.player.dx == 0 and game_state.player.dy == 0: # Root Anchor (if stationary, using 'A' for ability)
                        game_state.player.root_anchor()
                    elif event.key == pygame.K_a: # Left movement
                        game_state.player.move(-1, game_state.player.dy) # Normal left movement
                    
                    if event.key == pygame.K_r: # Canopy Glide
                        game_state.player.canopy_glide()
                    if event.key == pygame.K_f: # Seed Burst
                        game_state.player.seed_burst(game_state)
                    
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_w or event.key == pygame.K_s:
                        game_state.player.stop_move_y()
                    if event.key == pygame.K_a or event.key == pygame.K_d:
                        # Only stop if it was a movement 'A' not an anchor 'A'
                        if not game_state.player.is_anchored:
                            game_state.player.stop_move_x()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Left-click for Root Grapple
                    game_state.player.root_grapple(pygame.mouse.get_pos(), game_state.grapple_points)

            elif game_state.current_state == GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r: # Restart
                        game_state.current_state = MENU
                        game_state.load_level() # Reset player, score etc.
                    if event.key == pygame.K_q: # Quit
                        running = False

        game_state.update()
        game_state.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
