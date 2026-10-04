
import pygame
import sys
import math
import random
import json

# Game Concept (parsed from the problem description)
GAME_CONCEPT = {
  "title": "Turtle Trek: Ocean's Call",
  "description": "Guide a brave, tiny sea turtle hatchling across a sun-drenched, perilous beach. Dodge scuttling crabs, avoid swooping gulls, and navigate environmental hazards to reach the safety of the vast ocean.",
  "genre": "Casual Arcade / Survival",
  "theme": "Vibrant beach, warm sun, ocean life, nature.",
  "objective": "Guide the turtle hatchling from its nest (top of the screen) to the ocean (bottom of the screen) without getting caught or succumbing to hazards.",
  "mechanics": [
    "Top-down directional movement (8-way) across the beach.",
    "Environmental hazard avoidance (crabs, gulls, waves).",
    "Briefly hiding or 'tucking' into the shell for momentary protection.",
    "Collecting optional beach items for bonus points."
  ],
  "player_abilities": [
    "**Walk**: Standard movement across the sand.",
    "**Tuck & Wait**: Pressing a button makes the turtle briefly pull its head and limbs into its shell, stopping movement but providing a very short burst of minor damage reduction/invincibility to small hits. High risk/reward as it leaves you stationary."
  ],
  "enemies": [
    {
      "name": "Crab Scuttler",
      "behavior": "Patrols small areas horizontally or in tight circles. If the turtle gets too close, it charges quickly in a straight line towards the turtle's last known position for a short distance before returning to patrol. Getting hit causes a brief stun and health loss.",
      "difficulty": "easy"
    },
    {
      "name": "Seagull Swooper",
      "behavior": "Flies in from off-screen, circles overhead, and then swoops down rapidly in an arc to attempt to snatch the turtle. If it misses, it flies off screen. If it hits, it carries the turtle back a short distance, causing damage.",
      "difficulty": "medium"
    },
    {
      "name": "Rogue Wave",
      "behavior": "Not an enemy in the traditional sense, but an environmental hazard. Periodically, a large wave sweeps across the lower portion of the beach (closer to the ocean). If caught, the turtle is pushed back significantly and takes damage.",
      "difficulty": "medium"
    }
  ],
  "powerups": [
    {
      "name": "Shiny Shell Fragment",
      "effect": "Grants temporary invulnerability to one hit from a predator or wave, or provides a short burst of speed."
    },
    {
      "name": "Energizing Algae",
      "effect": "Briefly increases movement speed for a few seconds, allowing quicker escape from threats or faster progress."
    }
  ],
  "level_progression": "Levels increase in length and complexity. New environmental obstacles (e.g., driftwood logs, tide pools that slow movement) are introduced. The density and variety of enemies/hazards increase, and their patterns become more intricate. Visual changes like different times of day (dawn, midday, sunset) or slight weather variations (overcast) might occur.",
  "scoring_system": "Points are earned for reaching the ocean. A 'Time Bonus' rewards faster completion. 'Survival Bonus' grants points for each segment of health remaining. 'Collectible Bonus' awards points for picking up rare seashells or starfish scattered on the beach, which might be in more dangerous locations.",
  "visual_style": "Cute, vibrant pixel art with a slightly 'chunky' and appealing aesthetic. Bright, warm color palette for the sandy beach, shifting to deep blues and greens for the ocean. Clear, expressive animations for the turtle, enemies, and environmental effects like waves and sand trails.",
  "sound_theme": "Relaxing and atmospheric, featuring gentle wave sounds, distant seagull cries, and subtle, uplifting chiptune melodies that swell during moments of danger. Distinct, light 'plink' sound for collecting items and a soft 'bonk' for minor hits or hazard interactions."
}

# Level Design (parsed from the problem description)
LEVEL_DESIGN = {
  "level_number": 1,
  "name": "Hatchling's First Journey",
  "description": "The ocean beckons! Guide your tiny turtle hatchling from its nest across the sandy beach to the welcoming waves. Avoid slow-moving crabs, be mindful of circling gulls, and navigate the gentle, periodic waves at the shore. Collect sparkling seashells for bonus points!",
  "size": {
    "width": 800,
    "height": 600
  },
  "spawn_points": [
    {
      "x": 400,
      "y": 100,
      "type": "player"
    }
  ],
  "obstacles": [
    {
      "x": 250,
      "y": 180,
      "width": 80,
      "height": 40,
      "type": "rock"
    },
    {
      "x": 550,
      "y": 250,
      "width": 40,
      "height": 80,
      "type": "rock_cluster"
    },
    {
      "x": 180,
      "y": 350,
      "width": 120,
      "height": 30,
      "type": "driftwood"
    },
    {
      "x": 600,
      "y": 450,
      "width": 100,
      "height": 50,
      "type": "tidal_pool"
    },
    {
      "x": 0,
      "y": 550,
      "width": 800,
      "height": 50,
      "type": "ocean_exit_zone"
    },
    {
      "x": 0,
      "y": 500,
      "width": 800,
      "height": 50,
      "type": "wave_hazard",
      "movement": {
        "direction": "up",
        "speed": 0.5,
        "frequency": 10,
        "offset": 0,
        "active_zone_y": [
          500,
          550
        ]
      }
    }
  ],
  "powerups": [
    {
      "x": 100,
      "y": 250,
      "type": "seashell",
      "value": 100
    },
    {
      "x": 700,
      "y": 300,
      "type": "seashell",
      "value": 100
    },
    {
      "x": 400,
      "y": 480,
      "type": "seashell",
      "value": 100
    },
    {
      "x": 300,
      "y": 300,
      "type": "seaweed_snack",
      "effect": "speed_boost",
      "duration": 5
    },
    {
      "x": 500,
      "y": 150,
      "type": "shiny_pebble",
      "effect": "tuck_cooldown_reduction",
      "duration": 0
    }
  ],
  "enemies": [
    {
      "x": 300,
      "y": 200,
      "type": "crab_basic",
      "patrol_path": [
        [
          300,
          200
        ],
        [
          450,
          200
        ],
        [
          450,
          250
        ],
        [
          300,
          250
        ]
      ]
    },
    {
      "x": 150,
      "y": 400,
      "type": "crab_basic",
      "patrol_path": [
        [
          150,
          400
        ],
        [
          250,
          400
        ]
      ]
    },
    {
      "x": 550,
      "y": 100,
      "type": "gull_basic",
      "patrol_path": [
        [
          550,
          100
        ],
        [
          650,
          100
        ],
        [
          650,
          200
        ],
        [
          550,
          200
        ]
      ],
      "trigger_radius": 100,
      "swoop_delay": 3
    }
  ],
  "objectives": [
    {
      "type": "reach_destination",
      "target": "ocean_exit_zone",
      "message": "Reach the Ocean!"
    },
    {
      "type": "collect",
      "target": "seashell",
      "count": 3,
      "message": "Collect 3 Seashells (Bonus)"
    }
  ],
  "difficulty": "easy",
  "time_limit": 120
}


# Pygame Initialization
pygame.init()

# Screen dimensions
SCREEN_WIDTH = LEVEL_DESIGN["size"]["width"]
SCREEN_HEIGHT = LEVEL_DESIGN["size"]["height"]
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(GAME_CONCEPT["title"])

# Colors
COLOR_SAND = (240, 220, 130)
COLOR_OCEAN = (0, 100, 150)
COLOR_TURTLE = (50, 150, 70)
COLOR_TURTLE_TUCKED = (30, 90, 40)
COLOR_TURTLE_INVINCIBLE = (100, 200, 100)
COLOR_CRAB = (180, 50, 0)
COLOR_SEAGULL = (180, 180, 180)
COLOR_ROCK = (100, 100, 100)
COLOR_DRIFTWOOD = (139, 69, 19)
COLOR_TIDAL_POOL = (70, 140, 160)
COLOR_SEASHELL = (255, 215, 0) # Gold
COLOR_SPEED_BOOST = (0, 200, 0) # Bright Green for Algae
COLOR_TUCK_COOLDOWN_REDUCTION = (0, 150, 255) # Light blue for Pebble
COLOR_WAVE = (150, 200, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (200, 0, 0)
COLOR_GREEN = (0, 200, 0)
COLOR_BLUE = (0, 0, 200)

# Fonts
FONT_SMALL = pygame.font.Font(None, 24)
FONT_MEDIUM = pygame.font.Font(None, 36)
FONT_LARGE = pygame.font.Font(None, 48)
FONT_HUGE = pygame.font.Font(None, 72)

# Game States
MENU = 0
PLAYING = 1
GAME_OVER = 2
GAME_WIN = 3
current_game_state = MENU

# Game variables
player = None
enemies = []
obstacles = []
powerups = []
rogue_wave = None
ocean_exit_zone = None
game_score = 0
game_start_time = 0
time_limit = LEVEL_DESIGN["time_limit"]
collected_seashells = 0
required_seashells = 0
game_over_message = ""

# Constants
PLAYER_SPEED = 2.5
PLAYER_SIZE = 20
PLAYER_HEALTH = 100
TUCK_DURATION = 1.0 # seconds
TUCK_COOLDOWN = 3.0 # seconds
INVINCIBILITY_DURATION = 1.0 # seconds after taking damage
CRAB_SPEED = 1.5
CRAB_AGGRO_SPEED = 3
CRAB_AGGRO_RANGE = 75
CRAB_AGGRO_DURATION = 1.5 # seconds
SEAGULL_PATROL_SPEED = 1
SEAGULL_SWOOP_SPEED = 4
SEAGULL_SWOOP_DURATION = 1.5 # seconds
SEAGULL_CARRY_BACK_DISTANCE = 50
CRAB_DAMAGE = 10
SEAGULL_DAMAGE = 20
WAVE_DAMAGE = 15
WAVE_PUSH_BACK = 75

# Utility function for drawing text
def draw_text(surface, text, font, color, x, y, center=False):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.size = PLAYER_SIZE
        self.image = pygame.Surface((self.size, self.size))
        self.color = COLOR_TURTLE
        self.image.fill(self.color) # Default, will be drawn as a circle
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = pygame.math.Vector2(0, 0)
        self.speed = PLAYER_SPEED
        self.base_speed = PLAYER_SPEED
        self.health = PLAYER_HEALTH
        self.max_health = PLAYER_HEALTH
        
        self.is_tucked = False
        self.tuck_timer = 0
        self.tuck_cooldown = TUCK_COOLDOWN
        self.last_tuck_time = 0
        
        self.is_invincible = False
        self.invincible_timer = 0
        
        self.speed_boost_timer = 0
        self.is_speed_boosted = False

    def handle_input(self, keys):
        if self.is_tucked:
            self.vel = pygame.math.Vector2(0,0)
            return

        self.vel = pygame.math.Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel.x = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel.x = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vel.y = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vel.y = 1
        
        if self.vel.length() > 0:
            self.vel.normalize_ip() # Normalize for 8-way movement

    def tuck(self):
        current_time = pygame.time.get_ticks() / 1000
        if not self.is_tucked and (current_time - self.last_tuck_time > self.tuck_cooldown):
            self.is_tucked = True
            self.tuck_timer = TUCK_DURATION
            self.vel = pygame.math.Vector2(0,0) # Stop movement
            self.is_invincible = True # Temporarily invincible while tucked
            self.invincible_timer = TUCK_DURATION # Invincibility lasts for tuck duration
            self.last_tuck_time = current_time

    def update(self, dt):
        current_time = pygame.time.get_ticks() / 1000

        # Tuck timer
        if self.is_tucked:
            self.tuck_timer -= dt
            if self.tuck_timer <= 0:
                self.is_tucked = False
                # Invincibility for tuck ends here, if it was tied to tuck_timer

        # Invincibility timer
        if self.is_invincible:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                self.is_invincible = False
        
        # Speed boost timer
        if self.is_speed_boosted:
            self.speed_boost_timer -= dt
            if self.speed_boost_timer <= 0:
                self.speed = self.base_speed # Revert to base speed
                self.is_speed_boosted = False

        if not self.is_tucked:
            # Store old position for collision rollback
            old_rect = self.rect.copy()
            
            # Apply movement
            self.rect.x += self.vel.x * self.speed * dt * 60 # Convert dt to something more like frames
            self.rect.y += self.vel.y * self.speed * dt * 60

            # Keep player within screen bounds
            self.rect.left = max(0, self.rect.left)
            self.rect.right = min(SCREEN_WIDTH, self.rect.right)
            self.rect.top = max(0, self.rect.top)
            self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)

            # Collision with obstacles
            for obs in obstacles:
                if self.rect.colliderect(obs.rect):
                    # Simple collision response: prevent movement
                    self.rect = old_rect
                    if obs.type == "tidal_pool" and not self.is_speed_boosted:
                        self.speed = self.base_speed * 0.5 # Slow down in tidal pool
                    else:
                        self.speed = self.base_speed # Restore speed if not in tidal pool or boosted
                    break
            else: # No collision with obstacles
                if not self.is_speed_boosted: # Only restore if not currently boosted
                    self.speed = self.base_speed

    def take_damage(self, amount, knockback_vector=None):
        if not self.is_invincible:
            self.health -= amount
            if self.health < 0:
                self.health = 0
            
            # Activate invincibility after hit
            self.is_invincible = True
            self.invincible_timer = INVINCIBILITY_DURATION
            
            # Apply knockback if provided
            if knockback_vector:
                self.rect.x += knockback_vector.x
                self.rect.y += knockback_vector.y
                # Keep player within screen bounds after knockback
                self.rect.left = max(0, self.rect.left)
                self.rect.right = min(SCREEN_WIDTH, self.rect.right)
                self.rect.top = max(0, self.rect.top)
                self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)
            
            return True # Damage taken
        return False # No damage taken due to invincibility

    def apply_speed_boost(self, duration):
        self.speed = self.base_speed * 1.5 # Increase speed by 50%
        self.is_speed_boosted = True
        self.speed_boost_timer = duration

    def reduce_tuck_cooldown(self, amount):
        self.tuck_cooldown = max(1.0, self.tuck_cooldown - amount) # Minimum cooldown of 1 second

    def draw(self, surface):
        current_color = self.color
        if self.is_tucked:
            current_color = COLOR_TURTLE_TUCKED
            pygame.draw.circle(surface, current_color, self.rect.center, self.size // 2)
        elif self.is_invincible and int(self.invincible_timer * 10) % 2 == 0: # Flash when invincible
            current_color = COLOR_TURTLE_INVINCIBLE
            pygame.draw.circle(surface, current_color, self.rect.center, self.size // 2)
        else:
            pygame.draw.circle(surface, current_color, self.rect.center, self.size // 2)
            # Add a small 'head' to show direction if not tucked
            if self.vel.length() > 0:
                head_offset = self.vel.normalize() * (self.size // 2 + 5)
                head_pos = self.rect.center + head_offset
                pygame.draw.circle(surface, current_color, (int(head_pos.x), int(head_pos.y)), self.size // 4)

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, obs_type):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.type = obs_type
        self.color = COLOR_ROCK # Default
        
        if self.type == "rock" or self.type == "rock_cluster":
            self.color = COLOR_ROCK
        elif self.type == "driftwood":
            self.color = COLOR_DRIFTWOOD
        elif self.type == "tidal_pool":
            self.color = COLOR_TIDAL_POOL
        elif self.type == "ocean_exit_zone":
            self.color = COLOR_OCEAN # This will be drawn as the ocean background

    def draw(self, surface):
        # Ocean exit zone is drawn as background, so don't draw rect over it
        if self.type != "ocean_exit_zone":
            pygame.draw.rect(surface, self.color, self.rect)

class Powerup(pygame.sprite.Sprite):
    def __init__(self, x, y, p_type, value=0, effect=None, duration=0):
        super().__init__()
        self.size = 15
        self.rect = pygame.Rect(x - self.size // 2, y - self.size // 2, self.size, self.size)
        self.type = p_type
        self.value = value
        self.effect = effect
        self.duration = duration
        
        if self.type == "seashell":
            self.color = COLOR_SEASHELL
        elif self.type == "seaweed_snack": # Energizing Algae
            self.color = COLOR_SPEED_BOOST
        elif self.type == "shiny_pebble": # Shiny Shell Fragment
            self.color = COLOR_TUCK_COOLDOWN_REDUCTION

    def apply_effect(self, target_player):
        global game_score, collected_seashells
        if self.type == "seashell":
            game_score += self.value
            collected_seashells += 1
            return True
        elif self.effect == "speed_boost":
            target_player.apply_speed_boost(self.duration)
            return True
        elif self.effect == "tuck_cooldown_reduction":
            target_player.reduce_tuck_cooldown(TUCK_COOLDOWN * 0.5) # Reduce by 50%
            return True
        return False

    def draw(self, surface):
        if self.type == "seashell":
            # Draw a simple star/flower shape
            pygame.draw.polygon(surface, self.color, [
                (self.rect.centerx, self.rect.top),
                (self.rect.right, self.rect.centery),
                (self.rect.centerx, self.rect.bottom),
                (self.rect.left, self.rect.centery)
            ])
            pygame.draw.circle(surface, COLOR_WHITE, self.rect.center, self.size // 4)
        else: # Generic square for other powerups
            pygame.draw.rect(surface, self.color, self.rect)

class Crab(pygame.sprite.Sprite):
    PATROL = 0
    AGGRO = 1
    
    def __init__(self, x, y, patrol_path):
        super().__init__()
        self.size = 25
        self.rect = pygame.Rect(x - self.size // 2, y - self.size // 2, self.size, self.size)
        self.color = COLOR_CRAB
        self.speed = CRAB_SPEED
        self.patrol_path = [pygame.math.Vector2(p[0], p[1]) for p in patrol_path]
        self.current_patrol_index = 0
        self.target_pos = self.patrol_path[self.current_patrol_index]
        self.state = Crab.PATROL
        
        self.aggro_target_pos = None
        self.aggro_timer = 0
        self.aggro_duration = CRAB_AGGRO_DURATION
        self.aggro_speed = CRAB_AGGRO_SPEED
        self.aggro_range = CRAB_AGGRO_RANGE
        self.attack_cooldown = 1.0 # to prevent instant re-hits
        self.last_attack_time = 0

    def update(self, dt, target_player_pos):
        current_time = pygame.time.get_ticks() / 1000

        if self.state == Crab.PATROL:
            direction = self.target_pos - pygame.math.Vector2(self.rect.center)
            if direction.length() < self.speed * dt * 60: # Reached target
                self.rect.center = self.target_pos
                self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_path)
                self.target_pos = self.patrol_path[self.current_patrol_index]
            else:
                self.rect.center += direction.normalize() * self.speed * dt * 60
            
            # Check for player in aggro range
            if target_player_pos and (pygame.math.Vector2(self.rect.center) - target_player_pos).length() < self.aggro_range:
                self.state = Crab.AGGRO
                self.aggro_target_pos = target_player_pos.copy() # Target player's current position
                self.aggro_timer = self.aggro_duration

        elif self.state == Crab.AGGRO:
            if self.aggro_timer > 0:
                direction = self.aggro_target_pos - pygame.math.Vector2(self.rect.center)
                if direction.length() > self.aggro_speed * dt * 60: # Move towards aggro target
                    self.rect.center += direction.normalize() * self.aggro_speed * dt * 60
                else: # Reached aggro target
                    self.rect.center = self.aggro_target_pos
                    self.aggro_timer = 0 # Stop moving towards aggro_target_pos
                self.aggro_timer -= dt
            else:
                self.state = Crab.PATROL # Return to patrol once aggro duration is over

    def check_hit(self, player_rect):
        current_time = pygame.time.get_ticks() / 1000
        if self.rect.colliderect(player_rect) and (current_time - self.last_attack_time > self.attack_cooldown):
            self.last_attack_time = current_time
            return True
        return False

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        # Draw eyes
        eye_radius = 3
        eye_offset = 5
        pygame.draw.circle(surface, COLOR_WHITE, (self.rect.centerx - eye_offset, self.rect.centery - eye_offset), eye_radius)
        pygame.draw.circle(surface, COLOR_BLACK, (self.rect.centerx - eye_offset, self.rect.centery - eye_offset), eye_radius - 1)
        pygame.draw.circle(surface, COLOR_WHITE, (self.rect.centerx + eye_offset, self.rect.centery - eye_offset), eye_radius)
        pygame.draw.circle(surface, COLOR_BLACK, (self.rect.centerx + eye_offset, self.rect.centery - eye_offset), eye_radius - 1)

class Seagull(pygame.sprite.Sprite):
    PATROL = 0
    PREPARE_SWOOP = 1
    SWOOP = 2
    FLY_OFF = 3
    
    def __init__(self, x, y, patrol_path, trigger_radius, swoop_delay):
        super().__init__()
        self.size = 30
        self.rect = pygame.Rect(x - self.size // 2, y - self.size // 2, self.size, self.size)
        self.color = COLOR_SEAGULL
        self.speed = SEAGULL_PATROL_SPEED
        self.patrol_path = [pygame.math.Vector2(p[0], p[1]) for p in patrol_path]
        self.current_patrol_index = 0
        self.target_pos = self.patrol_path[self.current_patrol_index]
        self.state = Seagull.PATROL
        
        self.trigger_radius = trigger_radius
        self.swoop_delay = swoop_delay
        self.swoop_timer = 0
        self.swoop_target_pos = None
        self.swoop_speed = SEAGULL_SWOOP_SPEED
        self.swoop_duration = SEAGULL_SWOOP_DURATION
        self.swoop_active_timer = 0
        self.attack_cooldown = 2.0
        self.last_attack_time = 0
        self.original_position = pygame.math.Vector2(x, y) # For resetting after swooping off

    def update(self, dt, target_player_pos):
        current_time = pygame.time.get_ticks() / 1000

        if self.state == Seagull.PATROL:
            direction = self.target_pos - pygame.math.Vector2(self.rect.center)
            if direction.length() < self.speed * dt * 60:
                self.rect.center = self.target_pos
                self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_path)
                self.target_pos = self.patrol_path[self.current_patrol_index]
            else:
                self.rect.center += direction.normalize() * self.speed * dt * 60
            
            if target_player_pos and (pygame.math.Vector2(self.rect.center) - target_player_pos).length() < self.trigger_radius:
                self.state = Seagull.PREPARE_SWOOP
                self.swoop_timer = self.swoop_delay # Start countdown
                self.swoop_target_pos = target_player_pos.copy() # Lock on player's current position

        elif self.state == Seagull.PREPARE_SWOOP:
            self.swoop_timer -= dt
            if self.swoop_timer <= 0:
                self.state = Seagull.SWOOP
                self.swoop_active_timer = self.swoop_duration # Swoop for a limited time
                # Adjust swoop target to be slightly past player to ensure a full swoop
                if target_player_pos:
                    swoop_vector = (target_player_pos - pygame.math.Vector2(self.rect.center)).normalize()
                    self.swoop_target_pos = target_player_pos + swoop_vector * 50 # Swoop a bit further

        elif self.state == Seagull.SWOOP:
            if self.swoop_active_timer > 0:
                direction = self.swoop_target_pos - pygame.math.Vector2(self.rect.center)
                if direction.length() > self.swoop_speed * dt * 60:
                    self.rect.center += direction.normalize() * self.swoop_speed * dt * 60
                else:
                    self.rect.center = self.swoop_target_pos
                    self.state = Seagull.FLY_OFF # Swoop finished, fly off
                self.swoop_active_timer -= dt
            else:
                self.state = Seagull.FLY_OFF # Swoop timed out, fly off
            
        elif self.state == Seagull.FLY_OFF:
            # Fly towards a random point off-screen or back to original position (for now, original)
            direction = self.original_position - pygame.math.Vector2(self.rect.center)
            if direction.length() < self.swoop_speed * dt * 60:
                self.state = Seagull.PATROL
                self.rect.center = self.original_position
            else:
                self.rect.center += direction.normalize() * self.swoop_speed * dt * 60

    def check_hit(self, player_rect):
        current_time = pygame.time.get_ticks() / 1000
        if self.state == Seagull.SWOOP and self.rect.colliderect(player_rect) and (current_time - self.last_attack_time > self.attack_cooldown):
            self.last_attack_time = current_time
            return True
        return False

    def draw(self, surface):
        # Draw a simple triangle for the seagull body
        points = [
            (self.rect.centerx, self.rect.top),
            (self.rect.right, self.rect.bottom),
            (self.rect.left, self.rect.bottom)
        ]
        pygame.draw.polygon(surface, self.color, points)

class RogueWave(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, wave_data):
        super().__init__()
        self.original_rect = pygame.Rect(x, y, width, height)
        self.rect = self.original_rect.copy()
        self.color = COLOR_WAVE
        self.speed = wave_data["movement"]["speed"] * 60 # Convert to px/sec
        self.frequency = wave_data["movement"]["frequency"] # seconds
        self.active_zone_y = wave_data["movement"]["active_zone_y"]
        self.direction = wave_data["movement"]["direction"] # 'up' or 'down'

        self.last_activated_time = pygame.time.get_ticks() / 1000
        self.is_active = False
        self.current_movement_direction = 1 # 1 for up, -1 for down

    def update(self, dt):
        current_time = pygame.time.get_ticks() / 1000

        if not self.is_active and (current_time - self.last_activated_time > self.frequency):
            self.is_active = True
            self.rect.y = self.active_zone_y[1] # Start at bottom of active zone
            self.current_movement_direction = -1 # Move upwards initially

        if self.is_active:
            if self.current_movement_direction == -1: # Moving up
                self.rect.y -= self.speed * dt
                if self.rect.bottom <= self.active_zone_y[0]: # Reached top of active zone
                    self.is_active = False
                    self.last_activated_time = current_time

    def check_hit(self, player_rect):
        if self.is_active and self.rect.colliderect(player_rect):
            return True
        return False

    def draw(self, surface):
        if self.is_active:
            pygame.draw.rect(surface, self.color, self.rect)


def setup_level(level_data):
    global player, enemies, obstacles, powerups, rogue_wave, ocean_exit_zone, game_score, collected_seashells, required_seashells, game_start_time

    # Reset game state
    player = None
    enemies = []
    obstacles = []
    powerups = []
    rogue_wave = None
    ocean_exit_zone = None
    game_score = 0
    collected_seashells = 0
    required_seashells = 0
    game_start_time = pygame.time.get_ticks() / 1000 # Convert to seconds

    # Player spawn
    for sp in level_data["spawn_points"]:
        if sp["type"] == "player":
            player = Player(sp["x"], sp["y"])
            break

    # Obstacles
    for obs_data in level_data["obstacles"]:
        if obs_data["type"] == "ocean_exit_zone":
            ocean_exit_zone = Obstacle(obs_data["x"], obs_data["y"], obs_data["width"], obs_data["height"], obs_data["type"])
        elif obs_data["type"] == "wave_hazard":
            rogue_wave = RogueWave(obs_data["x"], obs_data["y"], obs_data["width"], obs_data["height"], obs_data)
        else:
            obstacles.append(Obstacle(obs_data["x"], obs_data["y"], obs_data["width"], obs_data["height"], obs_data["type"]))
    
    # Powerups
    for pu_data in level_data["powerups"]:
        powerups.append(Powerup(pu_data["x"], pu_data["y"], pu_data["type"], pu_data.get("value", 0), pu_data.get("effect"), pu_data.get("duration", 0)))
    
    # Enemies
    for enemy_data in level_data["enemies"]:
        if enemy_data["type"] == "crab_basic":
            enemies.append(Crab(enemy_data["x"], enemy_data["y"], enemy_data["patrol_path"]))
        elif enemy_data["type"] == "gull_basic":
            enemies.append(Seagull(enemy_data["x"], enemy_data["y"], enemy_data["patrol_path"], enemy_data["trigger_radius"], enemy_data["swoop_delay"]))

    # Objectives
    for obj in level_data["objectives"]:
        if obj["type"] == "collect" and obj["target"] == "seashell":
            required_seashells = obj["count"]
            break


def main_menu():
    global current_game_state
    
    title_text = GAME_CONCEPT["title"]
    start_text = "Press ENTER to Start"
    quit_text = "Press ESC to Quit"

    while current_game_state == MENU:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    setup_level(LEVEL_DESIGN)
                    current_game_state = PLAYING
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        SCREEN.fill(COLOR_SAND)
        draw_text(SCREEN, title_text, FONT_HUGE, COLOR_BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, center=True)
        draw_text(SCREEN, start_text, FONT_LARGE, COLOR_BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, center=True)
        draw_text(SCREEN, quit_text, FONT_MEDIUM, COLOR_BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3, center=True)
        
        pygame.display.flip()

def game_over_screen():
    global current_game_state, game_score, game_over_message
    
    restart_text = "Press R to Restart"
    menu_text = "Press ESC for Main Menu"

    while current_game_state == GAME_OVER or current_game_state == GAME_WIN:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    setup_level(LEVEL_DESIGN)
                    current_game_state = PLAYING
                    return
                if event.key == pygame.K_ESCAPE:
                    current_game_state = MENU
                    return

        SCREEN.fill(COLOR_OCEAN if current_game_state == GAME_WIN else COLOR_BLACK)
        
        if current_game_state == GAME_WIN:
            draw_text(SCREEN, "YOU REACHED THE OCEAN!", FONT_HUGE, COLOR_WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, center=True)
        else:
            draw_text(SCREEN, "GAME OVER", FONT_HUGE, COLOR_RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, center=True)

        # Split message into lines for drawing
        messages_lines = game_over_message.split('\n')
        for i, line in enumerate(messages_lines):
            draw_text(SCREEN, line, FONT_LARGE, COLOR_WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 50 + i * FONT_LARGE.get_height(), center=True)

        draw_text(SCREEN, f"Final Score: {game_score}", FONT_MEDIUM, COLOR_WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + len(messages_lines) * FONT_LARGE.get_height(), center=True)
        draw_text(SCREEN, restart_text, FONT_MEDIUM, COLOR_WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3 + len(messages_lines) * FONT_LARGE.get_height(), center=True)
        draw_text(SCREEN, menu_text, FONT_SMALL, COLOR_WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3 + 40 + len(messages_lines) * FONT_LARGE.get_height(), center=True)
        
        pygame.display.flip()


def game_loop():
    global current_game_state, game_score, game_start_time, collected_seashells, game_over_message

    clock = pygame.time.Clock()

    while current_game_state == PLAYING:
        dt = clock.tick(60) / 1000.0 # Delta time in seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.tuck()

        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        
        # Update
        player.update(dt)

        for enemy in enemies:
            enemy.update(dt, pygame.math.Vector2(player.rect.center))
            if enemy.check_hit(player.rect):
                if isinstance(enemy, Crab):
                    # Knockback direction from crab to player
                    knockback_vec = pygame.math.Vector2(player.rect.center) - pygame.math.Vector2(enemy.rect.center)
                    if knockback_vec.length() == 0: knockback_vec = pygame.math.Vector2(random.choice([-1,1]), random.choice([-1,1])) # Avoid zero vector
                    knockback_vec.normalize_ip()
                    knockback_vec *= 20 # Small push
                    player.take_damage(CRAB_DAMAGE, knockback_vec)
                elif isinstance(enemy, Seagull):
                    # Carry back: push player in direction opposite to gull's flight
                    knockback_vec = pygame.math.Vector2(enemy.rect.center) - pygame.math.Vector2(player.rect.center)
                    if knockback_vec.length() == 0: knockback_vec = pygame.math.Vector2(random.choice([-1,1]), random.choice([-1,1]))
                    knockback_vec.normalize_ip()
                    knockback_vec *= SEAGULL_CARRY_BACK_DISTANCE
                    player.take_damage(SEAGULL_DAMAGE, knockback_vec)

        if rogue_wave:
            rogue_wave.update(dt)
            if rogue_wave.check_hit(player.rect):
                # Push player back (upwards in this case as wave moves upwards)
                knockback_vec = pygame.math.Vector2(0, WAVE_PUSH_BACK)
                player.take_damage(WAVE_DAMAGE, knockback_vec)

        # Powerup collection
        for pu in list(powerups): # Iterate over a copy to allow removal
            if player.rect.colliderect(pu.rect):
                if pu.apply_effect(player):
                    powerups.remove(pu)

        # Win condition (reach ocean)
        if ocean_exit_zone and player.rect.colliderect(ocean_exit_zone.rect):
            # Calculate bonuses
            time_elapsed = pygame.time.get_ticks() / 1000 - game_start_time
            time_bonus = max(0, int((time_limit - time_elapsed) * 10)) # 10 points per second remaining
            survival_bonus = int(player.health) # 1 point per health point
            # Collectible bonus is already added when collected for seashells, but can add extra here if needed
            # For this implementation, seashells add points directly, so collected_seashells * X points as a final bonus.
            collectible_bonus_final = collected_seashells * 50 # Add 50 for each seashell (total 150 for 3)

            game_score += time_bonus + survival_bonus
            game_over_message = f"Time Bonus: {time_bonus}\nSurvival Bonus: {survival_bonus}\nCollected Seashells Bonus: {collectible_bonus_final}"
            current_game_state = GAME_WIN
            return

        # Lose condition (health or time)
        if player.health <= 0:
            game_over_message = "Your turtle ran out of health!"
            current_game_state = GAME_OVER
            return
        
        time_remaining = max(0, time_limit - (pygame.time.get_ticks() / 1000 - game_start_time))
        if time_remaining <= 0:
            game_over_message = "Time ran out for your turtle!"
            current_game_state = GAME_OVER
            return

        # Drawing
        SCREEN.fill(COLOR_SAND)
        if ocean_exit_zone:
            ocean_exit_zone.draw(SCREEN)

        for obs in obstacles:
            obs.draw(SCREEN)
        for pu in powerups:
            pu.draw(SCREEN)
        for enemy in enemies:
            enemy.draw(SCREEN)
        if rogue_wave:
            rogue_wave.draw(SCREEN)
        
        player.draw(SCREEN)

        # HUD
        draw_text(SCREEN, f"Score: {game_score}", FONT_SMALL, COLOR_BLACK, 10, 10)
        draw_text(SCREEN, f"Health: {player.health}/{player.max_health}", FONT_SMALL, COLOR_BLACK, 10, 30)
        draw_text(SCREEN, f"Time: {int(time_remaining)}s", FONT_SMALL, COLOR_BLACK, 10, 50)
        draw_text(SCREEN, f"Seashells: {collected_seashells}/{required_seashells}", FONT_SMALL, COLOR_BLACK, 10, 70)
        
        tuck_cooldown_progress = pygame.time.get_ticks() / 1000 - player.last_tuck_time
        if tuck_cooldown_progress < player.tuck_cooldown:
            draw_text(SCREEN, f"Tuck Cooldown: {int(player.tuck_cooldown - tuck_cooldown_progress) + 1}s", FONT_SMALL, COLOR_BLUE, SCREEN_WIDTH - 200, 10)
        else:
            draw_text(SCREEN, "Tuck Ready (SPACE)", FONT_SMALL, COLOR_GREEN, SCREEN_WIDTH - 200, 10)

        pygame.display.flip()

# Main game loop execution
def main():
    global current_game_state
    
    while True:
        if current_game_state == MENU:
            main_menu()
        elif current_game_state == PLAYING:
            game_loop()
        elif current_game_state == GAME_OVER or current_game_state == GAME_WIN:
            game_over_screen()

if __name__ == "__main__":
    main()
