
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
GREY = (50, 50, 50)
LIGHT_GREY = (150, 150, 150)
PLAYER_COLOR = (50, 200, 50) # Pip Green
PLAYER_DASH_COLOR = (150, 255, 150)
STOMP_AOE_COLOR = (200, 255, 200)

WALL_COLOR = (139, 69, 19)
ROCK_COLOR = (100, 100, 100)

GUB_COLOR = (80, 80, 90)
SPINY_COLOR = (120, 50, 120)
SPINY_STUNNED_COLOR = (200, 150, 200)
SLINGER_COLOR = (100, 30, 30)
PROJECTILE_COLOR = (20, 20, 20)
GLOOMBAT_COLOR = (60, 60, 70)

SWITCH_OFF_COLOR = (0, 100, 200)
SWITCH_ON_COLOR = (50, 180, 255)
GATE_CLOSED_COLOR = (200, 50, 50)

POWERUP_HEALTH_COLOR = (255, 100, 100)

FONT_COLOR = (240, 240, 240)

# Game Data (from JSON)
LEVEL_DATA = {
  "level_number": 1,
  "name": "The Bouncing Beginnings",
  "size": { "width": 800, "height": 600 },
  "spawn_points": [{"x": 75, "y": 525, "type": "player"}],
  "obstacles": [
    {"x": 0, "y": 0, "width": 800, "height": 10, "type": "wall"}, # Top wall
    {"x": 0, "y": 590, "width": 800, "height": 10, "type": "wall"}, # Bottom wall
    {"x": 0, "y": 0, "width": 10, "height": 600, "type": "wall"}, # Left wall
    {"x": 790, "y": 0, "width": 10, "height": 600, "type": "wall"},# Right wall
    {"x": 0, "y": 450, "width": 250, "height": 20, "type": "wall"},
    {"x": 300, "y": 200, "width": 20, "height": 250, "type": "wall"},
    {"x": 550, "y": 150, "width": 100, "height": 40, "type": "rock_cluster"},
    {"x": 650, "y": 450, "width": 40, "height": 40, "type": "stomp_switch", "id": "exit_switch"},
    {"x": 770, "y": 50, "width": 20, "height": 100, "type": "gate_closed", "linked_switch_id": "exit_switch"}
  ],
  "powerups": [{"x": 350, "y": 100, "type": "health"}],
  "enemies": [
    {"x": 200, "y": 500, "type": "gloom_gub", "patrol_path": [[200, 500], [250, 500]]},
    {"x": 400, "y": 300, "type": "gloom_gub", "patrol_path": []},
    {"x": 450, "y": 320, "type": "gloom_gub", "patrol_path": []},
    {"x": 400, "y": 100, "type": "spiny_shuffler", "patrol_path": [[350, 100], [500, 100]]},
    {"x": 600, "y": 250, "type": "shade_slinger", "patrol_path": []},
    {"x": 100, "y": 100, "type": "gloombat", "patrol_path": []}
  ],
  "objectives": [{"type": "reach_location", "target": {"x": 780, "y": 100}}],
  "time_limit": 180
}

# --- Game Classes ---

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.speed = 4

        # States: idle, moving, stomping, hopping, dashing
        self.state = 'idle'
        
        # Stomp
        self.stomp_charge_time = 0
        self.stomp_charge_max = 60 # 1 second
        self.stomp_cooldown = 0
        self.stomp_hop_timer = 0
        self.last_stomp_aoe = None

        # Dash
        self.dash_duration = 10 # frames
        self.dash_cooldown = 60 # frames
        self.dash_timer = 0
        self.is_invincible = False
        
        # Stats
        self.health = 3
        self.score = 0
        self.combo = 0
        self.combo_timer = 0
        self.max_combo_time = 120 # 2 seconds

    def get_input(self):
        if self.state in ['idle', 'moving']:
            keys = pygame.key.get_pressed()
            self.vel.x = 0
            self.vel.y = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.vel.x = -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.vel.x = 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.vel.y = -1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.vel.y = 1
            
            if self.vel.magnitude() > 0:
                self.vel = self.vel.normalize() * self.speed
                self.state = 'moving'
            else:
                self.state = 'idle'

            # Stomp charging
            if keys[pygame.K_SPACE] and self.stomp_cooldown == 0:
                self.state = 'stomping'
                self.stomp_charge_time += 1
                if self.stomp_charge_time > self.stomp_charge_max:
                    self.stomp_charge_time = self.stomp_charge_max
            elif self.stomp_charge_time > 0:
                self.execute_stomp()
            
            # Dash
            if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.dash_timer == 0:
                self.dash()

    def execute_stomp(self):
        charge_ratio = self.stomp_charge_time / self.stomp_charge_max
        radius = 20 + 40 * charge_ratio # Min radius 20, max 60
        is_charged = charge_ratio == 1.0

        self.last_stomp_aoe = {'rect': pygame.Rect(0,0, radius*2, radius*2), 'charged': is_charged, 'timer': 5}
        self.last_stomp_aoe['rect'].center = self.rect.center
        
        self.stomp_charge_time = 0
        self.stomp_cooldown = 20
        self.state = 'idle'

    def dash(self):
        self.state = 'dashing'
        self.dash_timer = self.dash_duration
        self.is_invincible = True
        if self.vel.magnitude() == 0: # If standing still, dash forward
            self.vel = pygame.math.Vector2(self.speed * 2.5, 0) 
        else:
            self.vel *= 2.5

    def update(self):
        self.get_input()
        
        # State machine
        if self.state == 'dashing':
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.state = 'idle'
                self.vel /= 2.5
                self.is_invincible = False
                self.dash_cooldown = 60
        
        if self.state == 'hopping':
            self.stomp_hop_timer -= 1
            if self.stomp_hop_timer <= 0:
                self.state = 'idle'

        if self.state == 'stomping':
            self.vel = pygame.math.Vector2(0, 0)

        # Update timers
        if self.dash_cooldown > 0 and self.state != 'dashing':
            self.dash_cooldown -= 1
        if self.stomp_cooldown > 0:
            self.stomp_cooldown -= 1
        
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0

        if self.last_stomp_aoe and self.last_stomp_aoe['timer'] > 0:
            self.last_stomp_aoe['timer'] -= 1

        self.pos += self.vel
        self.rect.center = self.pos

    def draw(self, screen):
        # Stomp Charge Indicator
        if self.state == 'stomping' and self.stomp_charge_time > 0:
            charge_ratio = self.stomp_charge_time / self.stomp_charge_max
            max_radius = self.rect.width
            radius = int(max_radius * charge_ratio)
            color = WHITE if charge_ratio == 1.0 else PLAYER_DASH_COLOR
            pygame.draw.circle(screen, color, self.rect.center, radius, 2)
        
        # Stomp AOE effect
        if self.last_stomp_aoe and self.last_stomp_aoe['timer'] > 0:
            aoe_rect = self.last_stomp_aoe['rect']
            s = pygame.Surface((aoe_rect.width, aoe_rect.height), pygame.SRCALPHA)
            alpha = int(255 * (self.last_stomp_aoe['timer'] / 5))
            pygame.draw.circle(s, STOMP_AOE_COLOR + (alpha,), (aoe_rect.width//2, aoe_rect.height//2), aoe_rect.width//2)
            screen.blit(s, aoe_rect.topleft)

        # Player sprite
        current_color = PLAYER_COLOR
        if self.is_invincible:
            current_color = PLAYER_DASH_COLOR
        
        self.image.fill(current_color)
        screen.blit(self.image, self.rect)

    def on_stomp_hit(self, enemy):
        self.state = 'hopping'
        self.stomp_hop_timer = 15 # Bounce in the air briefly
        self.combo += 1
        self.combo_timer = self.max_combo_time
        self.score += 100 * self.combo
    
    def take_damage(self):
        if not self.is_invincible:
            self.health -= 1
            self.is_invincible = True
            self.dash_timer = 60 # 1 second of invincibility after hit
            self.combo = 0
            return True
        return False
        
    def collision_with_walls(self, walls):
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                # Horizontal collision
                if self.vel.x > 0: self.rect.right = wall.rect.left
                if self.vel.x < 0: self.rect.left = wall.rect.right
                # Vertical collision
                if self.vel.y > 0: self.rect.bottom = wall.rect.top
                if self.vel.y < 0: self.rect.top = wall.rect.bottom
        self.pos.x = self.rect.centerx
        self.pos.y = self.rect.centery

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color, health, patrol_path=[]):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.color = color
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.speed = 1
        self.health = health
        self.patrol_path = patrol_path
        self.patrol_index = 0
        if self.patrol_path:
            self.move_to_target()

    def update(self):
        if self.patrol_path:
            target_pos = pygame.math.Vector2(self.patrol_path[self.patrol_index])
            if self.pos.distance_to(target_pos) < self.speed:
                self.patrol_index = (self.patrol_index + 1) % len(self.patrol_path)
                self.move_to_target()
        
        self.pos += self.vel
        self.rect.center = self.pos

    def move_to_target(self):
        if not self.patrol_path: return
        target_pos = pygame.math.Vector2(self.patrol_path[self.patrol_index])
        direction = target_pos - self.pos
        if direction.magnitude() > 0:
            self.vel = direction.normalize() * self.speed
    
    def take_damage(self, stomp_data):
        self.health -= 1
        if self.health <= 0:
            self.kill()

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class GloomGub(Enemy):
    def __init__(self, x, y, patrol_path):
        super().__init__(x, y, 25, 25, GUB_COLOR, 1, patrol_path)

class SpinyShuffler(Enemy):
    def __init__(self, x, y, patrol_path):
        super().__init__(x, y, 35, 35, SPINY_COLOR, 2, patrol_path)
        self.stunned_timer = 0
        self.is_stunned = False

    def update(self):
        super().update()
        if self.is_stunned:
            self.stunned_timer -= 1
            if self.stunned_timer <= 0:
                self.is_stunned = False
                self.image.fill(self.color)
                self.vel = pygame.math.Vector2(self.speed, 0)
                self.move_to_target()

    def take_damage(self, stomp_data):
        if stomp_data['charged'] and not self.is_stunned:
            self.is_stunned = True
            self.stunned_timer = 180 # 3 seconds
            self.image.fill(SPINY_STUNNED_COLOR)
            self.vel = pygame.math.Vector2(0, 0)
        elif self.is_stunned:
            self.health -= 1
            if self.health <= 0:
                self.kill()

class Gloombat(Enemy):
    def __init__(self, x, y, patrol_path):
        super().__init__(x, y, 30, 20, GLOOMBAT_COLOR, 1, patrol_path)
        self.state = 'hovering' # hovering, diving
        self.dive_timer = random.randint(120, 240)
        self.dive_target = None
        self.hover_pos = self.pos.copy()
        self.speed = 2
    
    def update(self, player_pos):
        self.dive_timer -= 1
        if self.state == 'hovering' and self.dive_timer <= 0:
            self.state = 'diving'
            self.dive_target = player_pos
            direction = self.dive_target - self.pos
            if direction.magnitude() > 0:
                self.vel = direction.normalize() * self.speed * 2.5
        
        elif self.state == 'diving':
            if self.pos.distance_to(self.dive_target) < 10 or self.pos.distance_to(self.hover_pos) > 200:
                self.state = 'returning'
                direction = self.hover_pos - self.pos
                if direction.magnitude() > 0:
                    self.vel = direction.normalize() * self.speed * 1.5

        elif self.state == 'returning':
            if self.pos.distance_to(self.hover_pos) < 10:
                self.state = 'hovering'
                self.pos = self.hover_pos.copy()
                self.vel = pygame.math.Vector2(0,0)
                self.dive_timer = random.randint(120, 240)

        self.pos += self.vel
        self.rect.center = self.pos

    def take_damage(self, stomp_data):
        if self.state == 'diving':
            self.kill()

class ShadeSlinger(Enemy):
    def __init__(self, x, y, patrol_path):
        super().__init__(x, y, 40, 40, SLINGER_COLOR, 1, patrol_path)
        self.shoot_cooldown = 120 # 2 seconds
        self.vel = pygame.math.Vector2(0,0)

    def update(self, player_pos, projectiles_group):
        self.shoot_cooldown -= 1
        if self.shoot_cooldown <= 0:
            self.shoot(player_pos, projectiles_group)
            self.shoot_cooldown = 120

    def shoot(self, player_pos, projectiles_group):
        direction = player_pos - self.pos
        if direction.magnitude() > 0:
            projectile = Projectile(self.rect.centerx, self.rect.centery, direction.normalize())
            projectiles_group.add(projectile)

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction_vec):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(PROJECTILE_COLOR)
        pygame.draw.circle(self.image, PROJECTILE_COLOR, (5, 5), 5)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = direction_vec * 3
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        self.rect.x += self.vel.x
        self.rect.y += self.vel.y
        if pygame.time.get_ticks() - self.spawn_time > 5000: # 5 second lifetime
            self.kill()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

class StompSwitch(Obstacle):
    def __init__(self, x, y, w, h, switch_id):
        super().__init__(x, y, w, h, SWITCH_OFF_COLOR)
        self.id = switch_id
        self.is_pressed = False

    def press(self):
        if not self.is_pressed:
            self.is_pressed = True
            self.image.fill(SWITCH_ON_COLOR)
            return True
        return False

class Gate(Obstacle):
    def __init__(self, x, y, w, h, linked_id):
        super().__init__(x, y, w, h, GATE_CLOSED_COLOR)
        self.linked_switch_id = linked_id
        self.is_open = False
    
    def open(self):
        self.is_open = True
        self.kill() # Remove from all groups so it no longer collides/draws

class Powerup(pygame.sprite.Sprite):
    def __init__(self, x, y, p_type):
        super().__init__()
        self.type = p_type
        self.image = pygame.Surface((20, 20))
        if self.type == 'health':
            self.image.fill(POWERUP_HEALTH_COLOR)
        self.rect = self.image.get_rect(center=(x,y))

    def apply(self, player):
        if self.type == 'health':
            player.health += 1
        self.kill()

# --- Main Game Class ---

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Stompbound")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.game_state = 'MENU'
        self.level_time = 0
        self.start_ticks = 0
        
    def load_level(self, data):
        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.interactables = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()

        spawn_pos = data["spawn_points"][0]
        self.player = Player(spawn_pos['x'], spawn_pos['y'])
        self.all_sprites.add(self.player)

        for obs_data in data["obstacles"]:
            if obs_data["type"] == "wall":
                o = Obstacle(obs_data['x'], obs_data['y'], obs_data['width'], obs_data['height'], WALL_COLOR)
                self.walls.add(o)
            elif obs_data["type"] == "rock_cluster":
                o = Obstacle(obs_data['x'], obs_data['y'], obs_data['width'], obs_data['height'], ROCK_COLOR)
                self.walls.add(o)
            elif obs_data["type"] == "stomp_switch":
                o = StompSwitch(obs_data['x'], obs_data['y'], obs_data['width'], obs_data['height'], obs_data['id'])
                self.interactables.add(o)
            elif obs_data["type"] == "gate_closed":
                o = Gate(obs_data['x'], obs_data['y'], obs_data['width'], obs_data['height'], obs_data['linked_switch_id'])
                self.walls.add(o) # Gates are walls until opened
                self.interactables.add(o)
            self.all_sprites.add(o)

        for enemy_data in data["enemies"]:
            path = [pygame.math.Vector2(p) for p in enemy_data['patrol_path']]
            if enemy_data['type'] == 'gloom_gub':
                e = GloomGub(enemy_data['x'], enemy_data['y'], path)
            elif enemy_data['type'] == 'spiny_shuffler':
                e = SpinyShuffler(enemy_data['x'], enemy_data['y'], path)
            elif enemy_data['type'] == 'shade_slinger':
                e = ShadeSlinger(enemy_data['x'], enemy_data['y'], path)
            elif enemy_data['type'] == 'gloombat':
                e = Gloombat(enemy_data['x'], enemy_data['y'], path)
            self.enemies.add(e)
            self.all_sprites.add(e)

        for p_data in data["powerups"]:
            p = Powerup(p_data['x'], p_data['y'], p_data['type'])
            self.powerups.add(p)
            self.all_sprites.add(p)
        
        self.objective_rect = pygame.Rect(
            data["objectives"][0]["target"]["x"] - 10,
            data["objectives"][0]["target"]["y"] - 10,
            20, 20
        )
        self.time_limit = data["time_limit"]
        self.start_ticks = pygame.time.get_ticks()

    def run(self):
        while True:
            if self.game_state == 'MENU':
                self.run_menu()
            elif self.game_state == 'PLAYING':
                self.run_game()
            elif self.game_state == 'GAME_OVER':
                self.run_game_over()
            elif self.game_state == 'VICTORY':
                self.run_victory()

    def run_menu(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.load_level(LEVEL_DATA)
                self.game_state = 'PLAYING'
        
        self.screen.fill(GREY)
        title_text = self.font.render("Stompbound", True, WHITE)
        start_text = self.font.render("Press ENTER to Start", True, WHITE)
        self.screen.blit(title_text, (SCREEN_WIDTH/2 - title_text.get_width()/2, SCREEN_HEIGHT/2 - 50))
        self.screen.blit(start_text, (SCREEN_WIDTH/2 - start_text.get_width()/2, SCREEN_HEIGHT/2 + 20))
        pygame.display.flip()
        self.clock.tick(FPS)

    def run_game_over(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.game_state = 'MENU'
        
        self.screen.fill(BLACK)
        text1 = self.font.render("GAME OVER", True, WHITE)
        text2 = self.font.render("Press ENTER to return to Menu", True, WHITE)
        self.screen.blit(text1, (SCREEN_WIDTH/2 - text1.get_width()/2, SCREEN_HEIGHT/2 - 50))
        self.screen.blit(text2, (SCREEN_WIDTH/2 - text2.get_width()/2, SCREEN_HEIGHT/2 + 20))
        pygame.display.flip()
        self.clock.tick(FPS)

    def run_victory(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.game_state = 'MENU'
        
        self.screen.fill((50, 100, 50))
        text1 = self.font.render("VICTORY!", True, WHITE)
        text2 = self.font.render(f"Final Score: {self.player.score}", True, WHITE)
        text3 = self.font.render("Press ENTER to return to Menu", True, WHITE)
        self.screen.blit(text1, (SCREEN_WIDTH/2 - text1.get_width()/2, SCREEN_HEIGHT/2 - 80))
        self.screen.blit(text2, (SCREEN_WIDTH/2 - text2.get_width()/2, SCREEN_HEIGHT/2 - 30))
        self.screen.blit(text3, (SCREEN_WIDTH/2 - text3.get_width()/2, SCREEN_HEIGHT/2 + 40))
        pygame.display.flip()
        self.clock.tick(FPS)

    def run_game(self):
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Update
        self.player.update()
        for enemy in self.enemies:
            if isinstance(enemy, ShadeSlinger):
                enemy.update(self.player.pos, self.projectiles)
            elif isinstance(enemy, Gloombat):
                enemy.update(self.player.pos)
            else:
                enemy.update()
        self.projectiles.update()

        # Collisions
        self.player.collision_with_walls(self.walls)

        # Player stomp vs enemies/interactables
        if self.player.last_stomp_aoe and self.player.last_stomp_aoe['timer'] == 4: # check only on first frame
            for enemy in self.enemies:
                if enemy.rect.colliderect(self.player.last_stomp_aoe['rect']):
                    enemy.take_damage(self.player.last_stomp_aoe)
                    self.player.on_stomp_hit(enemy)
            
            for item in self.interactables:
                if isinstance(item, StompSwitch) and item.rect.colliderect(self.player.last_stomp_aoe['rect']):
                    if item.press():
                        # Find linked gate and open it
                        for gate in self.interactables:
                            if isinstance(gate, Gate) and gate.linked_switch_id == item.id:
                                gate.open()
        
        # Player vs enemy contact
        hit_enemies = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in hit_enemies:
            if self.player.take_damage():
                # Damage taken, maybe add a sound or screen shake here
                pass

        # Player vs projectiles
        hit_projectiles = pygame.sprite.spritecollide(self.player, self.projectiles, True)
        for proj in hit_projectiles:
            if self.player.take_damage():
                pass
        
        # Player vs powerups
        hit_powerups = pygame.sprite.spritecollide(self.player, self.powerups, False)
        for p in hit_powerups:
            p.apply(self.player)
        
        # Check game state changes
        if self.player.health <= 0:
            self.game_state = 'GAME_OVER'
        
        if self.player.rect.colliderect(self.objective_rect):
            # Time bonus
            time_taken = (pygame.time.get_ticks() - self.start_ticks) / 1000
            time_bonus = max(0, int((self.time_limit - time_taken) * 10))
            self.player.score += time_bonus
            self.game_state = 'VICTORY'
            
        self.level_time = (pygame.time.get_ticks() - self.start_ticks) / 1000
        if self.level_time >= self.time_limit:
            self.game_state = 'GAME_OVER'

        # Drawing
        self.screen.fill(GREY)
        self.all_sprites.draw(self.screen) # Draw all sprites that have an image
        self.player.draw(self.screen) # Player draw has custom logic
        self.projectiles.draw(self.screen)

        # Draw HUD
        self.draw_hud()

        pygame.display.flip()
        self.clock.tick(FPS)

    def draw_hud(self):
        # Health
        health_text = self.font.render(f"Health: {self.player.health}", True, FONT_COLOR)
        self.screen.blit(health_text, (10, 10))

        # Score
        score_text = self.font.render(f"Score: {self.player.score}", True, FONT_COLOR)
        self.screen.blit(score_text, (10, 40))

        # Combo
        if self.player.combo > 1:
            combo_text = self.font.render(f"Combo: x{self.player.combo}", True, WHITE)
            self.screen.blit(combo_text, (self.player.rect.centerx - 30, self.player.rect.top - 30))

        # Timer
        time_left = self.time_limit - self.level_time
        time_text = self.font.render(f"Time: {int(time_left)}", True, FONT_COLOR)
        self.screen.blit(time_text, (SCREEN_WIDTH - time_text.get_width() - 10, 10))


def main():
    game = Game()
    game.run()

if __name__ == '__main__':
    main()

