"""
Core Game Engine for Topdown Games
Provides the base classes and systems for pygame-based topdown games
"""

import pygame
import math
import random
from typing import List, Dict, Any, Tuple, Optional
from enum import Enum

# Initialize pygame
pygame.init()

class GameState(Enum):
    """Game state enumeration"""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    VICTORY = "victory"

class Entity:
    """Base class for all game entities"""
    
    def __init__(self, x: float, y: float, width: int, height: int, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.rect = pygame.Rect(x, y, width, height)
        self.active = True
    
    def update(self, dt: float):
        """Update entity logic"""
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
    
    def draw(self, screen: pygame.Surface):
        """Draw the entity"""
        if self.active:
            pygame.draw.rect(screen, self.color, self.rect)
    
    def collides_with(self, other: 'Entity') -> bool:
        """Check collision with another entity"""
        return self.rect.colliderect(other.rect)

class Player(Entity):
    """Player character"""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 30, 30, (0, 0, 255))  # Blue
        self.speed = 200  # pixels per second
        self.health = 100
        self.max_health = 100
        self.score = 0
        self.powerups = []
    
    def update(self, dt: float, keys_pressed: Dict[int, bool], screen_width: int, screen_height: int):
        """Update player based on input"""
        # Movement
        dx = dy = 0
        if keys_pressed.get(pygame.K_LEFT) or keys_pressed.get(pygame.K_a):
            dx = -self.speed * dt
        if keys_pressed.get(pygame.K_RIGHT) or keys_pressed.get(pygame.K_d):
            dx = self.speed * dt
        if keys_pressed.get(pygame.K_UP) or keys_pressed.get(pygame.K_w):
            dy = -self.speed * dt
        if keys_pressed.get(pygame.K_DOWN) or keys_pressed.get(pygame.K_s):
            dy = self.speed * dt
        
        # Apply movement
        self.x += dx
        self.y += dy
        
        # Keep player on screen
        self.x = max(0, min(screen_width - self.width, self.x))
        self.y = max(0, min(screen_height - self.height, self.y))
        
        super().update(dt)
    
    def take_damage(self, damage: int):
        """Take damage"""
        self.health = max(0, self.health - damage)
    
    def heal(self, amount: int):
        """Heal the player"""
        self.health = min(self.max_health, self.health + amount)
    
    def add_score(self, points: int):
        """Add to score"""
        self.score += points

class Enemy(Entity):
    """Enemy entity"""
    
    def __init__(self, x: float, y: float, enemy_type: str = "basic"):
        colors = {
            "basic": (255, 0, 0),      # Red
            "aggressive": (139, 0, 0), # Dark red
            "fast": (255, 165, 0)      # Orange
        }
        super().__init__(x, y, 25, 25, colors.get(enemy_type, (255, 0, 0)))
        self.type = enemy_type
        self.speed = 50 if enemy_type == "basic" else 80 if enemy_type == "aggressive" else 120
        self.patrol_path = []
        self.current_target = 0
        self.direction = 1
        self.last_direction_change = 0
        
    def update(self, dt: float, player: Player):
        """Update enemy AI"""
        if not self.active:
            return
        
        # Simple AI behaviors
        if self.type == "basic":
            self._patrol_behavior(dt)
        elif self.type == "aggressive":
            self._chase_behavior(dt, player)
        elif self.type == "fast":
            self._fast_patrol_behavior(dt)
        
        super().update(dt)
    
    def _patrol_behavior(self, dt: float):
        """Basic patrol behavior"""
        if not self.patrol_path:
            # Random movement if no patrol path
            if random.random() < 0.01:  # 1% chance to change direction
                self.direction = random.choice([-1, 1])
            
            self.x += self.direction * self.speed * dt
        else:
            # Follow patrol path
            target = self.patrol_path[self.current_target]
            dx = target[0] - self.x
            dy = target[1] - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < 10:  # Close enough to target
                self.current_target = (self.current_target + 1) % len(self.patrol_path)
            else:
                # Move towards target
                self.x += (dx / distance) * self.speed * dt
                self.y += (dy / distance) * self.speed * dt
    
    def _chase_behavior(self, dt: float, player: Player):
        """Aggressive chase behavior"""
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            # Move towards player
            self.x += (dx / distance) * self.speed * dt
            self.y += (dy / distance) * self.speed * dt
    
    def _fast_patrol_behavior(self, dt: float):
        """Fast patrol behavior"""
        self._patrol_behavior(dt)

class Powerup(Entity):
    """Powerup item"""
    
    def __init__(self, x: float, y: float, powerup_type: str = "health"):
        colors = {
            "health": (0, 255, 0),     # Green
            "speed": (255, 255, 0),    # Yellow
            "score": (255, 0, 255),    # Magenta
            "shield": (0, 255, 255)    # Cyan
        }
        super().__init__(x, y, 20, 20, colors.get(powerup_type, (0, 255, 0)))
        self.type = powerup_type
        self.value = 20 if powerup_type == "health" else 50 if powerup_type == "score" else 1
    
    def apply_effect(self, player: Player):
        """Apply powerup effect to player"""
        if self.type == "health":
            player.heal(self.value)
        elif self.type == "score":
            player.add_score(self.value)
        elif self.type == "speed":
            player.speed = min(300, player.speed + 50)  # Cap speed
        elif self.type == "shield":
            player.health = min(player.max_health, player.health + 10)

class Obstacle(Entity):
    """Static obstacle"""
    
    def __init__(self, x: float, y: float, width: int, height: int, obstacle_type: str = "wall"):
        colors = {
            "wall": (128, 128, 128),   # Gray
            "rock": (139, 69, 19),     # Brown
            "water": (0, 100, 200),    # Blue
            "lava": (255, 100, 0)      # Orange-red
        }
        super().__init__(x, y, width, height, colors.get(obstacle_type, (128, 128, 128)))
        self.type = obstacle_type

class Collectible(Entity):
    """Collectible item"""
    
    def __init__(self, x: float, y: float, collectible_type: str = "coin"):
        colors = {
            "coin": (255, 215, 0),     # Gold
            "gem": (128, 0, 128),      # Purple
            "key": (255, 255, 255),    # White
            "star": (255, 255, 0)      # Yellow
        }
        super().__init__(x, y, 15, 15, colors.get(collectible_type, (255, 215, 0)))
        self.type = collectible_type
        self.value = 10 if collectible_type == "coin" else 50 if collectible_type == "gem" else 100

class GameEngine:
    """Main game engine"""
    
    def __init__(self, width: int = 800, height: int = 600, title: str = "Generated Game"):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Game state
        self.state = GameState.MENU
        self.running = True
        
        # Game objects
        self.player = None
        self.enemies: List[Enemy] = []
        self.powerups: List[Powerup] = []
        self.obstacles: List[Obstacle] = []
        self.collectibles: List[Collectible] = []
        
        # UI
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game settings
        self.level_number = 1
        self.time_limit = 120  # seconds
        self.start_time = 0
        self.level_complete = False
    
    def load_level(self, level_data: Dict[str, Any]):
        """Load level from level data"""
        # Clear existing objects
        self.enemies.clear()
        self.powerups.clear()
        self.obstacles.clear()
        self.collectibles.clear()
        
        # Set level properties
        self.level_number = level_data.get("level_number", 1)
        self.time_limit = level_data.get("time_limit", 120)
        self.start_time = pygame.time.get_ticks() / 1000.0
        
        # Create player
        spawn_points = level_data.get("spawn_points", [])
        player_spawn = next((sp for sp in spawn_points if sp["type"] == "player"), {"x": 50, "y": 50})
        self.player = Player(player_spawn["x"], player_spawn["y"])
        
        # Create obstacles
        for obs_data in level_data.get("obstacles", []):
            obstacle = Obstacle(
                obs_data["x"], obs_data["y"],
                obs_data["width"], obs_data["height"],
                obs_data["type"]
            )
            self.obstacles.append(obstacle)
        
        # Create powerups
        for pow_data in level_data.get("powerups", []):
            powerup = Powerup(pow_data["x"], pow_data["y"], pow_data["type"])
            self.powerups.append(powerup)
        
        # Create enemies
        for enemy_data in level_data.get("enemies", []):
            enemy = Enemy(enemy_data["x"], enemy_data["y"], enemy_data["type"])
            enemy.patrol_path = enemy_data.get("patrol_path", [])
            self.enemies.append(enemy)
        
        # Create collectibles (coins, gems, etc.)
        objectives = level_data.get("objectives", [])
        for obj in objectives:
            if obj["type"] == "collect":
                count = obj.get("count", 3)
                for _ in range(count):
                    x = random.randint(50, self.width - 50)
                    y = random.randint(50, self.height - 50)
                    collectible = Collectible(x, y, obj["target"])
                    self.collectibles.append(collectible)
        
        self.state = GameState.PLAYING
        self.level_complete = False
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                elif event.key == pygame.K_SPACE and self.state == GameState.MENU:
                    self.state = GameState.PLAYING
                elif event.key == pygame.K_r and self.state in [GameState.GAME_OVER, GameState.VICTORY]:
                    self.restart_level()
    
    def update(self, dt: float):
        """Update game logic"""
        if self.state != GameState.PLAYING:
            return
        
        if not self.player:
            return
        
        keys_pressed = pygame.key.get_pressed()
        
        # Update player
        self.player.update(dt, keys_pressed, self.width, self.height)
        
        # Update enemies
        for enemy in self.enemies:
            enemy.update(dt, self.player)
        
        # Check collisions
        self._check_collisions()
        
        # Check level completion
        self._check_level_completion()
        
        # Check time limit
        current_time = pygame.time.get_ticks() / 1000.0
        if current_time - self.start_time > self.time_limit:
            self.state = GameState.GAME_OVER
    
    def _check_collisions(self):
        """Check all collision events"""
        if not self.player:
            return
        
        # Player vs Obstacles
        for obstacle in self.obstacles:
            if self.player.collides_with(obstacle):
                # Simple collision response - push player back
                overlap_x = min(self.player.rect.right - obstacle.rect.left,
                              obstacle.rect.right - self.player.rect.left)
                overlap_y = min(self.player.rect.bottom - obstacle.rect.top,
                              obstacle.rect.bottom - self.player.rect.top)
                
                if overlap_x < overlap_y:
                    if self.player.x < obstacle.x:
                        self.player.x = obstacle.x - self.player.width
                    else:
                        self.player.x = obstacle.x + obstacle.width
                else:
                    if self.player.y < obstacle.y:
                        self.player.y = obstacle.y - self.player.height
                    else:
                        self.player.y = obstacle.y + obstacle.height
        
        # Player vs Powerups
        for powerup in self.powerups[:]:
            if powerup.active and self.player.collides_with(powerup):
                powerup.apply_effect(self.player)
                powerup.active = False
                self.powerups.remove(powerup)
        
        # Player vs Collectibles
        for collectible in self.collectibles[:]:
            if collectible.active and self.player.collides_with(collectible):
                self.player.add_score(collectible.value)
                collectible.active = False
                self.collectibles.remove(collectible)
        
        # Player vs Enemies
        for enemy in self.enemies:
            if enemy.active and self.player.collides_with(enemy):
                self.player.take_damage(10)
                if self.player.health <= 0:
                    self.state = GameState.GAME_OVER
    
    def _check_level_completion(self):
        """Check if level is complete"""
        if not self.collectibles:  # All collectibles collected
            self.state = GameState.VICTORY
            self.level_complete = True
    
    def draw(self):
        """Draw everything"""
        self.screen.fill((0, 0, 0))  # Black background
        
        if self.state == GameState.MENU:
            self._draw_menu()
        elif self.state == GameState.PLAYING:
            self._draw_game()
        elif self.state == GameState.PAUSED:
            self._draw_game()
            self._draw_pause_overlay()
        elif self.state == GameState.GAME_OVER:
            self._draw_game()
            self._draw_game_over()
        elif self.state == GameState.VICTORY:
            self._draw_game()
            self._draw_victory()
        
        pygame.display.flip()
    
    def _draw_menu(self):
        """Draw main menu"""
        title_text = self.font.render("Generated Game", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.width//2, self.height//2 - 50))
        self.screen.blit(title_text, title_rect)
        
        start_text = self.small_font.render("Press SPACE to start", True, (255, 255, 255))
        start_rect = start_text.get_rect(center=(self.width//2, self.height//2 + 50))
        self.screen.blit(start_text, start_rect)
    
    def _draw_game(self):
        """Draw game elements"""
        if not self.player:
            return
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        
        # Draw powerups
        for powerup in self.powerups:
            powerup.draw(self.screen)
        
        # Draw collectibles
        for collectible in self.collectibles:
            collectible.draw(self.screen)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw UI
        self._draw_ui()
    
    def _draw_ui(self):
        """Draw user interface"""
        # Score
        score_text = self.small_font.render(f"Score: {self.player.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # Health bar
        health_width = 200
        health_height = 20
        health_x = 10
        health_y = 40
        
        # Background
        pygame.draw.rect(self.screen, (255, 0, 0), (health_x, health_y, health_width, health_height))
        # Foreground
        health_percent = self.player.health / self.player.max_health
        pygame.draw.rect(self.screen, (0, 255, 0), (health_x, health_y, health_width * health_percent, health_height))
        
        # Time remaining
        current_time = pygame.time.get_ticks() / 1000.0
        time_remaining = max(0, self.time_limit - (current_time - self.start_time))
        time_text = self.small_font.render(f"Time: {int(time_remaining)}", True, (255, 255, 255))
        self.screen.blit(time_text, (10, 70))
        
        # Level
        level_text = self.small_font.render(f"Level: {self.level_number}", True, (255, 255, 255))
        self.screen.blit(level_text, (10, 100))
    
    def _draw_pause_overlay(self):
        """Draw pause overlay"""
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.font.render("PAUSED", True, (255, 255, 255))
        pause_rect = pause_text.get_rect(center=(self.width//2, self.height//2))
        self.screen.blit(pause_text, pause_rect)
        
        resume_text = self.small_font.render("Press ESC to resume", True, (255, 255, 255))
        resume_rect = resume_text.get_rect(center=(self.width//2, self.height//2 + 40))
        self.screen.blit(resume_text, resume_rect)
    
    def _draw_game_over(self):
        """Draw game over screen"""
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(self.width//2, self.height//2 - 20))
        self.screen.blit(game_over_text, game_over_rect)
        
        score_text = self.small_font.render(f"Final Score: {self.player.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.width//2, self.height//2 + 20))
        self.screen.blit(score_text, score_rect)
        
        restart_text = self.small_font.render("Press R to restart", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(self.width//2, self.height//2 + 60))
        self.screen.blit(restart_text, restart_rect)
    
    def _draw_victory(self):
        """Draw victory screen"""
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        victory_text = self.font.render("LEVEL COMPLETE!", True, (0, 255, 0))
        victory_rect = victory_text.get_rect(center=(self.width//2, self.height//2 - 20))
        self.screen.blit(victory_text, victory_rect)
        
        score_text = self.small_font.render(f"Score: {self.player.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.width//2, self.height//2 + 20))
        self.screen.blit(score_text, score_rect)
        
        next_text = self.small_font.render("Press R for next level", True, (255, 255, 255))
        next_rect = next_text.get_rect(center=(self.width//2, self.height//2 + 60))
        self.screen.blit(next_text, next_rect)
    
    def restart_level(self):
        """Restart the current level"""
        if self.player:
            self.player.health = self.player.max_health
            self.player.score = 0
            self.start_time = pygame.time.get_ticks() / 1000.0
            self.state = GameState.PLAYING
    
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0  # Delta time in seconds
            
            self.handle_events()
            self.update(dt)
            self.draw()
        
        pygame.quit()
