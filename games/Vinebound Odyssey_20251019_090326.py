
# --- Player Sprite Class ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill((255, 165, 0))  # Orange color for the monkey
        self.rect = self.image.get_rect(center=(x, y))
        
        # Physics and Movement
        self.velocity = pygame.math.Vector2(0, 0)
        self.max_speed = 5
        self.acceleration = 0.5
        self.friction = -0.08
        self.jump_strength = -12
        self.gravity = 0.6
        self.on_ground = False

        # Vine Mechanics
        self.is_swinging = False
        self.vine_anchor = None
        self.vine_length = 0
        self.swing_angle = 0
        self.swing_velocity = 0
        self.grapple_active = False
        self.grapple_target = None
        self.grapple_range = 200

        # Sticker Foot
        self.sticker_active = False
        self.sticker_duration = 180 # Frames
        self.sticker_timer = 0

    def update(self, platforms, vines, grapple_points, hazards, interactive_elements):
        self.apply_gravity()
        self.handle_vine_swinging()
        self.handle_grapple()
        self.handle_sticker_foot()
        
        # Store old position for collision resolution
        self.old_rect = self.rect.copy()

        # Apply horizontal movement
        if not self.is_swinging and not self.grapple_active:
            self.velocity.x += self.acceleration
            self.velocity.x += self.friction
            self.velocity.x = max(-self.max_speed, min(self.velocity.x, self.max_speed))
            self.rect.x += self.velocity.x

        # Horizontal collision with platforms
        self.check_horizontal_collisions(platforms)

        # Apply vertical movement (if not swinging)
        if not self.is_swinging and not self.grapple_active:
            self.rect.y += self.velocity.y
        
        # Vertical collision with platforms and ground
        self.check_vertical_collisions(platforms)

        # Check for ground status
        self.on_ground = self.rect.bottom >= SCREEN_HEIGHT - 50 # Assuming a floor level

        # Interaction Checks
        self.check_interactions(hazards, interactive_elements)

        # Update sticker timer
        if self.sticker_active:
            self.sticker_timer -= 1
            if self.sticker_timer <= 0:
                self.sticker_active = False
                self.image.fill((255, 165, 0)) # Reset color


    def handle_input(self, vines, grapple_points):
        keys = pygame.key.get_pressed()

        # Jump
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.on_ground and not self.is_swinging and not self.grapple_active:
            self.velocity.y = self.jump_strength
            self.on_ground = False
        
        # Vine Grab (automatic when near vines and jumping)
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and not self.on_ground and not self.is_swinging and not self.grapple_active:
            for vine in vines:
                vine_rect = pygame.Rect(vine['x'] - 10, vine['y'] - vine['length'], 20, vine['length'])
                player_top_reach = pygame.Rect(self.rect.centerx - 10, self.rect.top - 50, 20, 50)
                if vine_rect.colliderect(player_top_reach):
                    self.start_swing(vine)
                    break
        
        # Vine Detach
        if keys[pygame.K_SPACE] and self.is_swinging:
            self.detach_vine()
        
        # Grapple Hook Throw
        if keys[pygame.K_e] and not self.grapple_active and not self.is_swinging:
            # Find closest grapple point
            closest_point = None
            min_dist = self.grapple_range
            for gp in grapple_points:
                dist = pygame.math.Vector2(self.rect.center).distance_to(gp)
                if dist < min_dist:
                    min_dist = dist
                    closest_point = gp
            if closest_point:
                self.throw_grapple(closest_point)
        
        # Grapple Hook Release
        if keys[pygame.K_e] and self.grapple_active:
            self.release_grapple()
        
        # Sticker Foot Activation
        if keys[pygame.K_s] and not self.sticker_active and not self.is_swinging and not self.grapple_active:
            self.activate_sticker_foot()

    def apply_gravity(self):
        if not self.is_swinging and not self.grapple_active:
            self.velocity.y += self.gravity
            self.velocity.y = min(self.velocity.y, 15) # Max fall speed

    def check_horizontal_collisions(self, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity.x > 0: # Moving right
                    self.rect.right = platform.rect.left
                elif self.velocity.x < 0: # Moving left
                    self.rect.left = platform.rect.right
                self.velocity.x = 0 # Stop horizontal movement

    def check_vertical_collisions(self, platforms):
        self.on_ground = False # Assume not on ground until proven otherwise
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity.y > 0: # Falling
                    self.rect.bottom = platform.rect.top
                    self.velocity.y = 0
                    self.on_ground = True
                elif self.velocity.y < 0: # Jumping
                    self.rect.top = platform.rect.bottom
                    self.velocity.y = 0

    def start_swing(self, vine_data):
        self.is_swinging = True
        self.vine_anchor = (vine_data['x'], vine_data['y'])
        self.vine_length = pygame.math.Vector2(self.rect.center).distance_to(self.vine_anchor)
        self.velocity = pygame.math.Vector2(0, 0) # Stop all current momentum
        self.swing_angle = pygame.math.Vector2(self.rect.center - pygame.math.Vector2(self.vine_anchor)).angle_to((1, 0))
        self.swing_velocity = 0

    def handle_vine_swinging(self):
        if not self.is_swinging:
            return

        # Calculate swing velocity (simple pendulum motion)
        self.swing_velocity += 0.1 * (self.vine_length * 0.02) * pygame.math.Vector2(1, 0).rotate(self.swing_angle).y
        self.swing_angle += self.swing_velocity
        
        # Calculate new position based on angle and length
        offset_x = self.vine_length * pygame.math.Vector2(1, 0).rotate(self.swing_angle).x
        offset_y = self.vine_length * pygame.math.Vector2(1, 0).rotate(self.swing_angle).y
        self.rect.center = (self.vine_anchor[0] + offset_x, self.vine_anchor[1] + offset_y)
        
        # Prevent player from getting stuck in the anchor
        if self.rect.colliderect(pygame.Rect(self.vine_anchor[0]-10, self.vine_anchor[1]-10, 20, 20)):
            self.detach_vine()

    def detach_vine(self):
        self.is_swinging = False
        self.vine_anchor = None
        # Apply current swing momentum to velocity
        forward_vector = pygame.math.Vector2(1, 0).rotate(self.swing_angle)
        self.velocity.x = forward_vector.x * 5  # Arbitrary multiplier for launch speed
        self.velocity.y = forward_vector.y * 5
        self.swing_angle = 0
        self.swing_velocity = 0
        self.vine_length = 0

    def throw_grapple(self, target):
        self.grapple_active = True
        self.grapple_target = pygame.math.Vector2(target)
        self.grapple_range = 200 # Reset range for this throw

    def handle_grapple(self):
        if not self.grapple_active:
            return
        
        # Move towards grapple target
        direction = (self.grapple_target - pygame.math.Vector2(self.rect.center)).normalize()
        self.velocity = direction * 15 # Grapple speed
        self.rect.move_ip(self.velocity)

        # Check if target is reached
        if pygame.math.Vector2(self.rect.center).distance_to(self.grapple_target) < 10:
            self.grapple_active = False
            self.grapple_target = None
            # Now that we've reached the grapple point, we can swing from it
            self.vine_anchor = self.grapple_target # Use grapple target as vine anchor
            self.vine_length = 0 # Start with no slack
            self.is_swinging = True
            self.swing_velocity = 0
            self.swing_angle = 0

    def release_grapple(self):
        self.grapple_active = False
        self.grapple_target = None
        self.velocity = pygame.math.Vector2(0, 0) # Stop moving if grapple is released

    def activate_sticker_foot(self):
        self.sticker_active = True
        self.sticker_timer = self.sticker_duration
        self.image.fill((0, 255, 0)) # Green color to indicate sticker active

    def handle_sticker_foot(self):
        if not self.sticker_active:
            return
        
        # If sticker is active, gravity is ignored and player can stick to surfaces
        self.velocity.y = 0 # Stop vertical falling
        self.gravity = 0 # Temporarily disable gravity

    def check_interactions(self, hazards, interactive_elements):
        # Hazard collision
        for hazard in hazards:
            if self.rect.colliderect(hazard.rect):
                self.take_damage(10) # Assuming take_damage method exists elsewhere

        # Interactive element collision
        for element in interactive_elements:
            if self.rect.colliderect(element.rect):
                if element.type == "bouncy_mushroom":
                    self.velocity.y = -25 # Big bounce
                    self.on_ground = False
                elif element.type == "lever":
                    element.interact() # Call the lever's interaction method

    def take_damage(self, amount):
        # This method should be part of a base Entity class or Player class
        # For this example, we'll just print
        print(f"Player took {amount} damage!")
        # Add actual health reduction logic here
        pass


# --- Vine Class ---
class Vine:
    def __init__(self, x, y, length):
        self.x = x
        self.y = y
        self.length = length
        self.color = (139, 69, 19) # Brown color for vines

    def draw(self, surface):
        pygame.draw.line(surface, self.color, (self.x, self.y), (self.x, self.y + self.length), 5)

# --- Grapple Point Class ---
class GrapplePoint(pygame.sprite.Sprite):
    def __init__(self, x, y, grapple_type):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        if grapple_type == "tree_branch":
            self.image.fill((101, 67, 33)) # Darker brown
        elif grapple_type == "rock_outcropping":
            self.image.fill((128, 128, 128)) # Grey
        else:
            self.image.fill((0, 255, 0)) # Default green
        self.rect = self.image.get_rect(center=(x, y))

# --- Platform Class ---
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, platform_type):
        super().__init__()
        self.image = pygame.Surface([width, height])
        if platform_type == "ground":
            self.image.fill((34, 139, 34)) # Forest green
        else:
            self.image.fill((160, 82, 45)) # Sienna for other platforms
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# --- Hazard Class ---
class Hazard(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, hazard_type):
        super().__init__()
        self.image = pygame.Surface([width, height])
        if hazard_type == "spiked_plant":
            self.image.fill((255, 0, 0)) # Red for spikes
        else:
            self.image.fill((100, 100, 100)) # Grey for other hazards
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# --- Interactive Element Class ---
class InteractiveElement(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, element_type, action=None):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.element_type = element_type
        self.action = action
        if element_type == "bouncy_mushroom":
            self.image.fill((255, 105, 180)) # Pink for mushroom
        elif element_type == "lever":
            self.image.fill((139, 69, 19)) # Brown for lever
        else:
            self.image.fill((100, 100, 100)) # Default grey
        self.rect = self.image.get_rect(center=(x, y))
        self.lever_pulled = False # For lever specific logic

    def interact(self):
        if self.element_type == "lever" and not self.lever_pulled:
            print("Lever pulled!")
            self.lever_pulled = True
            self.image.fill((60, 179, 113)) # Indicate pulled state (e.g., green)
            # In a real game, this would trigger an event or change level state
            # For now, we'll just print
            pass
        elif self.element_type == "bouncy_mushroom":
            pass # Player handles bounce logic

# --- Powerup Class ---
class Powerup(pygame.sprite.Sprite):
    def __init__(self, x, y, powerup_type):
        super().__init__()
        self.powerup_type = powerup_type
        self.image = pygame.Surface((30, 30))
        self.rect = self.image.get_rect(center=(x, y))

        if powerup_type == "health_berry":
            self.image.fill((255, 0, 0)) # Red for health berry
        elif powerup_type == "speed_boost_leaf":
            self.image.fill((0, 255, 0)) # Green for speed boost leaf
        # Add other powerup types and their visuals here

# --- Enemy Class ---
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type, patrol_path=None):
        super().__init__()
        self.enemy_type = enemy_type
        self.patrol_path = patrol_path
        self.current_path_point = 0
        self.speed = 2

        if enemy_type == "basic":
            self.image = pygame.Surface((30, 30))
            self.image.fill((255, 100, 0)) # Orange-ish for basic enemy
            self.max_health = 30
            self.current_health = self.max_health
        elif enemy_type == "aggressive":
            self.image = pygame.Surface((35, 35))
            self.image.fill((200, 50, 50)) # Red-ish for aggressive
            self.max_health = 50
            self.current_health = self.max_health
        else:
            self.image = pygame.Surface((30, 30))
            self.image.fill((128, 128, 128)) # Grey for unknown types

        self.rect = self.image.get_rect(center=(x, y))
        self.is_alive = True

    def update(self, player):
        if not self.is_alive:
            return

        # Patrol behavior
        if self.patrol_path:
            target_pos = pygame.math.Vector2(self.patrol_path[self.current_path_point])
            if pygame.math.Vector2(self.rect.center).distance_to(target_pos) < 5:
                self.current_path_point = (self.current_path_point + 1) % len(self.patrol_path)
                target_pos = pygame.math.Vector2(self.patrol_path[self.current_path_point])
            
            direction = (target_pos - pygame.math.Vector2(self.rect.center)).normalize()
            self.rect.move_ip(direction * self.speed)
        
        # Example: simple chase if player is nearby (for aggressive)
        if self.enemy_type == "aggressive" and player.is_alive:
            player_pos = pygame.math.Vector2(player.rect.center)
            dist_to_player = pygame.math.Vector2(self.rect.center).distance_to(player_pos)
            if dist_to_player < 150: # Chase range
                direction = (player_pos - pygame.math.Vector2(self.rect.center)).normalize()
                self.rect.move_ip(direction * (self.speed + 2)) # Faster when chasing


    def take_damage(self, amount):
        self.current_health -= amount
        if self.current_health <= 0:
            self.die()
    
    def die(self):
        self.is_alive = False
        self.kill() # Remove from sprite groups


# --- Collectible Class ---
class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y, collectible_type):
        super().__init__()
        self.collectible_type = collectible_type
        self.image = pygame.Surface((20, 20))
        if collectible_type == "coin":
            self.image.fill((255, 215, 0)) # Gold for coin
        # Add other collectible types
        self.rect = self.image.get_rect(center=(x, y))

# --- Game Level Data ---
LEVEL_DATA = {
    "level_number": 1,
    "name": "The Whispering Canopy",
    "size": {"width": 1200, "height": 800},
    "spawn_points": [{"x": 100, "y": 150, "type": "player"}],
    "vines": [
        {"x": 250, "y": 100, "length": 150},
        {"x": 400, "y": 100, "length": 150},
        {"x": 550, "y": 250, "length": 200},
        {"x": 700, "y": 100, "length": 150},
        {"x": 900, "y": 300, "length": 250},
        {"x": 1100, "y": 200, "length": 180}
    ],
    "grapple_points": [
        {"x": 325, "y": 80, "type": "tree_branch"},
        {"x": 625, "y": 230, "type": "tree_branch"},
        {"x": 800, "y": 280, "type": "tree_branch"},
        {"x": 1000, "y": 180, "type": "rock_outcropping"}
    ],
    "platforms": [
        {"x": 200, "y": 250, "width": 100, "height": 20, "type": "ground"},
        {"x": 450, "y": 300, "width": 100, "height": 20, "type": "ground"},
        {"x": 750, "y": 350, "width": 150, "height": 20, "type": "ground"},
        {"x": 1050, "y": 400, "width": 100, "height": 20, "type": "ground"}
    ],
    "hazards": [
        {"x": 150, "y": 450, "width": 50, "height": 50, "type": "spiked_plant"},
        {"x": 500, "y": 450, "width": 50, "height": 50, "type": "spiked_plant"},
        {"x": 850, "y": 500, "width": 50, "height": 50, "type": "spiked_plant"}
    ],
    "interactive_elements": [
        {"x": 480, "y": 280, "width": 40, "height": 40, "type": "bouncy_mushroom"},
        {"x": 780, "y": 330, "width": 30, "height": 30, "type": "lever", "action": "open_path"}
    ],
    "powerups": [
        {"x": 300, "y": 100, "type": "health_berry"},
        {"x": 580, "y": 200, "type": "speed_boost_leaf"},
        {"x": 950, "y": 350, "type": "health_berry"}
    ],
    "enemies": [
        {"x": 180, "y": 200, "type": "basic", "patrol_path": [[180, 200], [220, 200]]},
        {"x": 430, "y": 250, "type": "basic", "patrol_path": [[430, 250], [470, 250]]},
        {"x": 730, "y": 300, "type": "aggressive", "patrol_path": [[730, 300], [780, 300]]}
    ],
    "collectibles": [
        {"x": 280, "y": 50, "type": "coin"},
        {"x": 350, "y": 180, "type": "coin"},
        {"x": 500, "y": 150, "type": "coin"},
        {"x": 680, "y": 50, "type": "coin"},
        {"x": 850, "y": 200, "type": "coin"},
        {"x": 1000, "y": 300, "type": "coin"}
    ],
    "objectives": [
        {"type": "collect", "target": "coins", "count": 6},
        {"type": "defeat", "target": "enemies", "count": 3},
        {"type": "reach", "location": {"x": 1150, "y": 400}}
    ],
    "difficulty": "easy",
    "time_limit": 180
}

# --- Screen Setup ---
SCREEN_WIDTH = LEVEL_DATA["size"]["width"]
SCREEN_HEIGHT = LEVEL_DATA["size"]["height"]
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(f"Vinebound Odyssey - {LEVEL_DATA['name']}")
clock = pygame.time.Clock()
FPS = 60

# --- Sprite Groups ---
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
vines_group = [] # List to hold Vine objects
grapple_points = pygame.sprite.Group()
hazards = pygame.sprite.Group()
interactive_elements = pygame.sprite.Group()
powerups = pygame.sprite.Group()
enemies = pygame.sprite.Group()
collectibles = pygame.sprite.Group()

# --- Game Variables ---
player = None
game_over = False
score = 0
time_left = LEVEL_DATA["time_limit"]
objective_progress = {obj["type"]: 0 for obj in LEVEL_DATA["objectives"]}

# --- Font Setup ---
FONT_LARGE = pygame.font.Font(None, 74)
FONT_MEDIUM = pygame.font.Font(None, 36)
FONT_SMALL = pygame.font.Font(None, 24)

# --- Load Level Data ---
def load_level(level_data):
    global player, time_left

    # Reset groups and lists
    all_sprites.empty()
    platforms.empty()
    vines_group.clear()
    grapple_points.empty()
    hazards.empty()
    interactive_elements.empty()
    powerups.empty()
    enemies.empty()
    collectibles.empty()

    # Spawn player
    for spawn in level_data["spawn_points"]:
        if spawn["type"] == "player":
            player = Player(spawn["x"], spawn["y"])
            all_sprites.add(player)
            break
    
    # Add platforms
    for p_data in level_data["platforms"]:
        platform = Platform(p_data["x"], p_data["y"], p_data["width"], p_data["height"], p_data["type"])
        all_sprites.add(platform)
        platforms.add(platform)

    # Add vines
    for v_data in level_data["vines"]:
        vine = Vine(v_data["x"], v_data["y"], v_data["length"])
        vines_group.append(vine)

    # Add grapple points
    for gp_data in level_data["grapple_points"]:
        gp = GrapplePoint(gp_data["x"], gp_data["y"], gp_data["type"])
        all_sprites.add(gp)
        grapple_points.add(gp)

    # Add hazards
    for h_data in level_data["hazards"]:
        hazard = Hazard(h_data["x"], h_data["y"], h_data["width"], h_data["height"], h_data["type"])
        all_sprites.add(hazard)
        hazards.add(hazard)

    # Add interactive elements
    for ie_data in level_data["interactive_elements"]:
        element = InteractiveElement(ie_data["x"], ie_data["y"], ie_data["width"], ie_data["height"], ie_data["type"], ie_data.get("action"))
        all_sprites.add(element)
        interactive_elements.add(element)

    # Add powerups
    for pu_data in level_data["powerups"]:
        powerup = Powerup(pu_data["x"], pu_data["y"], pu_data["type"])
        all_sprites.add(powerup)
        powerups.add(powerup)

    # Add enemies
    for enemy_data in level_data["enemies"]:
        enemy = Enemy(enemy_data["x"], enemy_data["y"], enemy_data["type"], enemy_data.get("patrol_path"))
        all_sprites.add(enemy)
        enemies.add(enemy)

    # Add collectibles
    for c_data in level_data["collectibles"]:
        collectible = Collectible(c_data["x"], c_data["y"], c_data["type"])
        all_sprites.add(collectible)
        collectibles.add(collectible)

    # Reset game state variables
    time_left = level_data["time_limit"]
    score = 0
    objective_progress = {obj["type"]: 0 for obj in level_data["objectives"]}


# --- Game Logic Functions ---
def handle_player_input(player, vines, grapple_points):
    player.handle_input(vines, grapple_points)

def update_game_state(player, platforms, vines, grapple_points, hazards, interactive_elements, powerups, enemies, collectibles):
    global score, time_left, game_over, objective_progress

    # Update player
    player.update(platforms, vines_group, grapple_points, hazards, interactive_elements)

    # Update other sprites
    for enemy in enemies:
        if enemy.is_alive:
            enemy.update(player)

    # Check for collisions
    # Player with powerups
    for powerup in pygame.sprite.spritecollide(player, powerups, True):
        if powerup.powerup_type == "health_berry":
            player.heal(20) # Assuming player has a heal method
        elif powerup.powerup_type == "speed_boost_leaf":
            # Implement temporary speed boost logic for player
            pass

    # Player with collectibles
    for collectible in pygame.sprite.spritecollide(player, collectibles, True):
        if collectible.collectible_type == "coin":
            score += 10
            objective_progress["coins"] = objective_progress.get("coins", 0) + 1

    # Player with enemies
    for enemy in pygame.sprite.spritecollide(player, enemies, False):
        if enemy.is_alive:
            if player.velocity.y > 0 and player.rect.bottom - player.velocity.y <= enemy.rect.top: # Jumped on enemy
                enemy.take_damage(10) # Damage enemy
                player.velocity.y = -player.jump_strength * 0.5 # Small bounce
            else:
                player.take_damage(10) # Damage player

    # Player with hazards
    for hazard in pygame.sprite.spritecollide(player, hazards, False):
        player.take_damage(10) # Damage player


    # Update timer
    time_left -= 1
    if time_left <= 0:
        game_over = True

    # Check objectives
    check_objectives(objective_progress, LEVEL_DATA["objectives"], player)

def check_objectives(progress, objectives_data, player_instance):
    global game_over
    for obj in objectives_data:
        if obj["type"] == "collect" and obj["target"] == "coins":
            progress["coins"] = len(collectibles) # Assuming coins are removed on collection
            if progress["coins"] <= 0: # Check if all coins are collected
                 progress["coins"] = LEVEL_DATA["objectives"][0]["count"] # Mark as completed if count reached
        elif obj["type"] == "defeat" and obj["target"] == "enemies":
            defeated_count = sum(1 for enemy in enemies if not enemy.is_alive)
            progress["enemies"] = defeated_count
        elif obj["type"] == "reach":
            player_pos = pygame.math.Vector2(player_instance.rect.center)
            target_pos = pygame.math.Vector2(obj["location"]["x"], obj["location"]["y"])
            if player_pos.distance_to(target_pos) < 50:
                progress["reach"] = 1 # Mark as reached

    # Check win condition
    all_objectives_met = True
    for obj in objectives_data:
        target_type = obj["type"]
        if target_type == "collect" and obj["target"] == "coins":
            if progress.get("coins", 0) < obj["count"]:
                all_objectives_met = False
                break
        elif target_type == "defeat" and obj["target"] == "enemies":
            if progress.get("enemies", 0) < obj["count"]:
                all_objectives_met = False
                break
        elif target_type == "reach":
            if progress.get("reach", 0) < 1:
                all_objectives_met = False
                break
    
    if all_objectives_met:
        print("All objectives met!")
        # Potentially trigger level complete screen or next level
        # For now, we'll just print
        pass


def draw_game(screen, player, vines, grapple_points, hazards, interactive_elements, powerups, enemies, collectibles):
    # Background (lush jungle theme)
    screen.fill((46, 139, 87)) # Dark sea green for foliage

    # Parallax scrolling background elements (simplified)
    pygame.draw.rect(screen, (0, 100, 0), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT // 3)) # Darker green canopy
    pygame.draw.rect(screen, (139, 69, 19), (0, SCREEN_HEIGHT // 3, SCREEN_WIDTH, SCREEN_HEIGHT // 3)) # Brown for trunks/branches

    # Draw platforms
    platforms.draw(screen)

    # Draw vines
    for vine in vines:
        vine.draw(screen)

    # Draw grapple points
    grapple_points.draw(screen)

    # Draw interactive elements
    interactive_elements.draw(screen)

    # Draw hazards
    hazards.draw(screen)

    # Draw powerups
    powerups.draw(screen)

    # Draw enemies
    enemies.draw(screen)

    # Draw collectibles
    collectibles.draw(screen)

    # Draw player
    if player:
        screen.blit(player.image, player.rect)

    # Draw grapple line if active
    if player and player.grapple_active and player.grapple_target:
        pygame.draw.line(screen, (100, 100, 100), player.rect.center, player.grapple_target, 2)

    # Draw UI elements
    draw_ui(screen)

def draw_ui(screen):
    # Score
    score_text = FONT_MEDIUM.render(f"Score: {score}", True, (255, 255, 0))
    screen.blit(score_text, (10, 10))

    # Time
    time_text = FONT_MEDIUM.render(f"Time: {time_left}", True, (255, 255, 255))
    screen.blit(time_text, (SCREEN_WIDTH - time_text.get_width() - 10, 10))

    # Objectives
    obj_y = 50
    for obj in LEVEL_DATA["objectives"]:
        progress_str = ""
        if obj["type"] == "collect" and obj["target"] == "coins":
            progress_str = f"{objective_progress.get('coins', 0)}/{obj['count']}"
        elif obj["type"] == "defeat" and obj["target"] == "enemies":
            progress_str = f"{objective_progress.get('enemies', 0)}/{obj['count']}"
        elif obj["type"] == "reach":
            progress_str = "Reached" if objective_progress.get("reach", 0) >= 1 else "Not Reached"

        obj_display_text = f"{obj['type'].capitalize()} {obj['target']}: {progress_str}"
        obj_surface = FONT_SMALL.render(obj_display_text, True, (255, 255, 255))
        screen.blit(obj_surface, (10, obj_y))
        obj_y += 30


def draw_game_over_screen(screen):
    screen.fill((0, 0, 0, 180)) # Semi-transparent black overlay
    
    title_text = FONT_LARGE.render("GAME OVER", True, (255, 0, 0))
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(title_text, title_rect)

    final_score_text = FONT_MEDIUM.render(f"Final Score: {score}", True, (255, 255, 255))
    final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
    screen.blit(final_score_text, final_score_rect)

    restart_text = FONT_MEDIUM.render("Press R to Restart", True, (255, 255, 255))
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
    screen.blit(restart_text, restart_rect)

def draw_level_complete_screen(screen):
    screen.fill((0, 0, 0, 180)) # Semi-transparent black overlay
    
    title_text = FONT_LARGE.render("LEVEL COMPLETE!", True, (0, 255, 0))
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(title_text, title_rect)

    final_score_text = FONT_MEDIUM.render(f"Final Score: {score}", True, (255, 255, 255))
    final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
    screen.blit(final_score_text, final_score_rect)

    next_level_text = FONT_MEDIUM.render("Press N for Next Level", True, (255, 255, 255))
    next_level_rect = next_level_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
    screen.blit(next_level_text, next_level_rect)


# --- Main Game Loop ---
load_level(LEVEL_DATA)
running = True
current_state = "playing" # "playing", "game_over", "level_complete"

while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        
        if current_state == "playing":
            if event.type == pygame.KEYDOWN:
                handle_player_input(player, vines_group, grapple_points)
                # Example for Sticker Foot activation (if not using continuous press)
                if event.key == pygame.K_s and not player.sticker_active and not player.is_swinging and not player.grapple_active:
                    player.activate_sticker_foot()
        elif current_state == "game_over":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    load_level(LEVEL_DATA) # Reload the same level
                    current_state = "playing"
        elif current_state == "level_complete":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    # Load next level (or restart if this is the last level)
                    print("Loading next level...")
                    # For now, just restart the current level
                    load_level(LEVEL_DATA)
                    current_state = "playing"


    if current_state == "playing":
        update_game_state(player, platforms, vines_group, grapple_points, hazards, interactive_elements, powerups, enemies, collectibles)
        
        # Check for level completion after updates
        all_objectives_met = True
        for obj in LEVEL_DATA["objectives"]:
            target_type = obj["type"]
            if target_type == "collect" and obj["target"] == "coins":
                if objective_progress.get("coins", 0) < obj["count"]:
                    all_objectives_met = False
                    break
            elif target_type == "defeat" and obj["target"] == "enemies":
                if objective_progress.get("enemies", 0) < obj["count"]:
                    all_objectives_met = False
                    break
            elif target_type == "reach":
                if objective_progress.get("reach", 0) < 1:
                    all_objectives_met = False
                    break
        
        if all_objectives_met:
            current_state = "level_complete"

        # Check for game over conditions (e.g., player dies)
        if player and not player.is_alive:
             current_state = "game_over"

    # --- Drawing ---
    screen.fill(BLACK) # Clear screen before drawing new frame

    if current_state == "playing":
        draw_game(screen, player, vines_group, grapple_points, hazards, interactive_elements, powerups, enemies, collectibles)
    elif current_state == "game_over":
        draw_game(screen, player, vines_group, grapple_points, hazards, interactive_elements, powerups, enemies, collectibles) # Draw game world in background
        draw_game_over_screen(screen)
    elif current_state == "level_complete":
        draw_game(screen, player, vines_group, grapple_points, hazards, interactive_elements, powerups, enemies, collectibles) # Draw game world in background
        draw_level_complete_screen(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
