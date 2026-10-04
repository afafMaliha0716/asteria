# --- Constants from Game Concept ---
# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Color definitions (RGB) - Based on visual style
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
NEON_CYAN = (0, 255, 255)
NEON_MAGENTA = (255, 0, 255)
NEON_YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GREY = (128, 128, 128)
DARK_BLUE = (0, 0, 100)

# Player properties
PLAYER_SIZE = 30
PLAYER_SPEED = 4
PLAYER_DASH_SPEED = 12
PLAYER_DASH_DURATION = 15 # frames
PLAYER_DASH_COOLDOWN = 60 # frames
PLAYER_TEMPORAL_SHIFT_DURATION = 30 # frames
PLAYER_TEMPORAL_SHIFT_COOLDOWN = 120 # frames
PLAYER_TEMPORAL_SHIFT_SPEED_BOOST = 1.5
PLAYER_MAX_TEMPORAL_SHIFT_USES = 3

# Powerup properties
POWERUP_SIZE = 20
POWERUP_SPAWN_CHANCE = 0.1 # Relative to number of fragments collected

# Enemy properties
TEMPORAL_ECHO_SIZE = 25
TEMPORAL_ECHO_SPEED = 2
TEMPORAL_ECHO_TRAIL_DURATION = 60 # frames
TEMPORAL_ECHO_RESPAWN_DELAY = 180 # frames
TEMPORAL_ECHO_DETECTION_RADIUS = 150 # Pixels

ANOMALY_SENTINEL_SIZE = 40
ANOMALY_SENTINEL_PULSE_RADIUS = 75
ANOMALY_SENTINEL_PULSE_INTERVAL = 90 # frames
ANOMALY_SENTINEL_PULSE_DAMAGE = 10
ANOMALY_SENTINEL_AGGRESSION_RADIUS = 100 # Pixels

PARADOX_SHARD_SIZE = 15
PARADOX_SHARD_SPEED = 6
PARADOX_SHARD_TELEPORT_INTERVAL = 60 # frames
PARADOX_SHARD_TELEPORT_RANGE = 50 # Pixels
PARADOX_SHARD_DAMAGE_RADIUS = 30
PARADOX_SHARD_DAMAGE = 15

# Environmental hazard properties
TEMPORAL_RIFT_SIZE = 50
TEMPORAL_RIFT_DAMAGE = 5
TEMPORAL_RIFT_PULSE_INTERVAL = 75 # frames

TEMPORAL_DISTORTION_SIZE = 40
TEMPORAL_DISTORTION_PULL_FORCE = 0.1
TEMPORAL_DISTORTION_MAX_PULL_RADIUS = 80

# Obstacle properties
WALL_COLOR = GREY
ROCK_COLOR = (80, 80, 80)

# Objective properties
COLLECTIBLE_FRAGMENT_SIZE = 15
COLLECTIBLE_FRAGMENT_VALUE = 1

# Level properties (from Level Design)
LEVEL_WIDTH = 800
LEVEL_HEIGHT = 600
EXIT_PORTAL_SIZE = 40

# --- Initialization ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chronosweeper")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

# --- Game State Enum ---
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    LEVEL_COMPLETE = 3
    GAME_OVER = 4

current_state = GameState.MENU
level_data = {
  "level_number": 1,
  "name": "Temporal Anomaly Outbreak",
  "description": "A minor temporal anomaly has manifested, scattering paradox fragments and unleashing nascent chronal entities. Navigate the unstable environment, collect the scattered fragments, and neutralize the emerging threats to stabilize the area.",
  "size": {
    "width": 800,
    "height": 600
  },
  "spawn_points": [
    {
      "x": 50,
      "y": 50,
      "type": "player"
    }
  ],
  "obstacles": [
    {
      "x": 150,
      "y": 100,
      "width": 100,
      "height": 50,
      "type": "wall"
    },
    {
      "x": 300,
      "y": 200,
      "width": 50,
      "height": 50,
      "type": "temporal_rift"
    },
    {
      "x": 450,
      "y": 150,
      "width": 75,
      "height": 25,
      "type": "wall"
    },
    {
      "x": 600,
      "y": 250,
      "width": 40,
      "height": 40,
      "type": "paradox_fragment_cluster"
    },
    {
      "x": 200,
      "y": 350,
      "width": 50,
      "height": 50,
      "type": "rock"
    },
    {
      "x": 400,
      "y": 400,
      "width": 60,
      "height": 60,
      "type": "temporal_distortion"
    },
    {
      "x": 550,
      "y": 450,
      "width": 80,
      "height": 30,
      "type": "wall"
    },
    {
      "x": 100,
      "y": 500,
      "width": 70,
      "height": 70,
      "type": "rock"
    }
  ],
  "powerups": [
    {
      "x": 100,
      "y": 250,
      "type": "chrono_charge" # Corresponds to Temporal Shift refill
    },
    {
      "x": 500,
      "y": 300,
      "type": "cooldown_reduction" # Not explicitly defined in game concept for a powerup, will map to Echo Amplifier for now.
    },
    {
      "x": 700,
      "y": 100,
      "type": "shield" # Corresponds to Stabilizer Fragment
    }
  ],
  "enemies": [
    {
      "x": 350,
      "y": 250,
      "type": "basic", # Temporal Echo
      "patrol_path": [
        [
          350,
          250
        ],
        [
          380,
          250
        ],
        [
          380,
          280
        ],
        [
          350,
          280
        ]
      ]
    },
    {
      "x": 550,
      "y": 150,
      "type": "aggressive", # Anomaly Sentinel
      "patrol_path": [
        [
          550,
          150
        ],
        [
          600,
          150
        ]
      ]
    },
    {
      "x": 150,
      "y": 400,
      "type": "basic", # Temporal Echo
      "patrol_path": [
        [
          150,
          400
        ],
        [
          150,
          430
        ],
        [
          180,
          430
        ],
        [
          180,
          400
        ]
      ]
    }
  ],
  "objectives": [
    {
      "type": "collect",
      "target": "paradox_fragments",
      "count": 10
    },
    {
      "type": "defeat",
      "target": "enemies",
      "count": 3
    }
  ],
  "difficulty": "easy",
  "time_limit": 180 # seconds
}

# --- Game Objects ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([PLAYER_SIZE, PLAYER_SIZE], pygame.SRCALPHA)
        pygame.draw.circle(self.image, NEON_CYAN, (PLAYER_SIZE // 2, PLAYER_SIZE // 2), PLAYER_SIZE // 2)
        self.rect = self.image.get_rect()
        self.rect.center = (level_data["spawn_points"][0]["x"], level_data["spawn_points"][0]["y"])

        self.speed = PLAYER_SPEED
        self.dash_speed = PLAYER_DASH_SPEED
        self.dash_duration = PLAYER_DASH_DURATION
        self.dash_cooldown = PLAYER_DASH_COOLDOWN
        self.dash_timer = 0
        self.is_dashing = False
        self.dash_direction = (0, 0)

        self.temporal_shift_uses = PLAYER_MAX_TEMPORAL_SHIFT_USES
        self.temporal_shift_duration = PLAYER_TEMPORAL_SHIFT_DURATION
        self.temporal_shift_cooldown = PLAYER_TEMPORAL_SHIFT_COOLDOWN
        self.temporal_shift_timer = 0
        self.is_temporal_shifting = False
        self.temporal_shift_speed_boost = PLAYER_TEMPORAL_SHIFT_SPEED_BOOST

        self.echo_trace_duration = 120 # frames
        self.echo_trace_cooldown = 240 # frames
        self.echo_trace_timer = 0
        self.is_echo_tracing = False
        self.echo_trace_path = []

        self.kinetic_rebound_active = False
        self.kinetic_rebound_boost = 1.5
        self.kinetic_rebound_duration = 15 # frames
        self.kinetic_rebound_timer = 0

        self.max_health = 100
        self.current_health = self.max_health

    def handle_input(self):
        keys = pygame.key.get_pressed()

        # Movement
        move_x, move_y = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move_y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move_y += 1

        # Normalize diagonal movement
        if move_x != 0 and move_y != 0:
            move_x *= 0.707
            move_y *= 0.707

        current_speed = self.speed
        if self.is_dashing:
            current_speed = self.dash_speed
        elif self.is_temporal_shifting:
            current_speed = self.speed * self.temporal_shift_speed_boost

        self.rect.x += move_x * current_speed
        self.rect.y += move_y * current_speed

        # Dash (Spacebar)
        if keys[pygame.K_SPACE] and self.dash_timer <= 0 and not self.is_dashing and not self.is_temporal_shifting:
            self.is_dashing = True
            self.dash_timer = self.dash_cooldown
            self.dash_duration_timer = self.dash_duration
            # Determine dash direction based on current movement or last direction
            if move_x != 0 or move_y != 0:
                self.dash_direction = (move_x, move_y)
            else: # If not moving, dash in a default direction (e.g., right)
                self.dash_direction = (1, 0)
            # Normalize dash direction
            if self.dash_direction != (0,0):
                norm = (self.dash_direction[0]**2 + self.dash_direction[1]**2)**0.5
                self.dash_direction = (self.dash_direction[0]/norm, self.dash_direction[1]/norm)

        # Temporal Shift (Shift key)
        if keys[pygame.K_LSHIFT] and self.temporal_shift_uses > 0 and self.temporal_shift_timer <= 0 and not self.is_temporal_shifting and not self.is_dashing:
            self.is_temporal_shifting = True
            self.temporal_shift_timer = self.temporal_shift_cooldown
            self.temporal_shift_duration_timer = self.temporal_shift_duration
            self.temporal_shift_uses -= 1
            self.image.set_alpha(150) # Make player semi-transparent during shift

        # Echo Trace (E key)
        if keys[pygame.K_e] and self.echo_trace_timer <= 0 and not self.is_echo_tracing:
            self.is_echo_tracing = True
            self.echo_trace_timer = self.echo_trace_cooldown
            self.echo_trace_duration_timer = self.echo_trace_duration
            self.echo_trace_path = [] # Clear previous path


    def update_timers(self):
        if self.dash_timer > 0:
            self.dash_timer -= 1
        if self.dash_duration_timer > 0:
            self.dash_duration_timer -= 1
            if self.dash_duration_timer <= 0:
                self.is_dashing = False

        if self.temporal_shift_timer > 0:
            self.temporal_shift_timer -= 1
        if self.temporal_shift_duration_timer > 0:
            self.temporal_shift_duration_timer -= 1
            if self.temporal_shift_duration_timer <= 0:
                self.is_temporal_shifting = False
                self.image.set_alpha(255) # Restore alpha

        if self.echo_trace_timer > 0:
            self.echo_trace_timer -= 1
        if self.echo_trace_duration_timer > 0:
            self.echo_trace_duration_timer -= 1
            if self.echo_trace_duration_timer <= 0:
                self.is_echo_tracing = False

        if self.kinetic_rebound_timer > 0:
            self.kinetic_rebound_timer -= 1
            if self.kinetic_rebound_timer <= 0:
                self.kinetic_rebound_active = False

    def take_damage(self, amount):
        if not self.is_temporal_shifting:
            self.current_health -= amount
            self.current_health = max(0, self.current_health)
            if self.current_health == 0:
                global current_state
                current_state = GameState.GAME_OVER

    def refill_temporal_shift(self):
        self.temporal_shift_uses = PLAYER_MAX_TEMPORAL_SHIFT_USES
        self.temporal_shift_timer = 0 # Allow immediate use

    def draw_health_bar(self, surface):
        BAR_WIDTH = self.rect.width * 2
        BAR_HEIGHT = 5
        BAR_X = self.rect.centerx - BAR_WIDTH // 2
        BAR_Y = self.rect.top - 15

        health_ratio = self.current_health / self.max_health
        fill_width = int(BAR_WIDTH * health_ratio)

        pygame.draw.rect(surface, RED, (BAR_X, BAR_Y, BAR_WIDTH, BAR_HEIGHT))
        pygame.draw.rect(surface, GREEN, (BAR_X, BAR_Y, fill_width, BAR_HEIGHT))

    def draw_ability_bars(self, surface):
        bar_height = 5
        bar_width = 50
        bar_spacing = 10
        start_x = 10
        start_y = SCREEN_HEIGHT - 30

        # Temporal Shift Bar
        ts_uses_text = font.render(f"Shift ({self.temporal_shift_uses}/{PLAYER_MAX_TEMPORAL_SHIFT_USES})", True, WHITE)
        surface.blit(ts_uses_text, (start_x, start_y - bar_height - bar_spacing))
        for i in range(PLAYER_MAX_TEMPORAL_SHIFT_USES):
            bar_color = GREEN if i < self.temporal_shift_uses else GREY
            pygame.draw.rect(surface, bar_color, (start_x + i * (bar_width + bar_spacing), start_y, bar_width, bar_height))

        # Dash Cooldown Bar
        dash_cooldown_text = font.render("Dash", True, WHITE)
        surface.blit(dash_cooldown_text, (start_x + PLAYER_MAX_TEMPORAL_SHIFT_USES * (bar_width + bar_spacing) + bar_spacing, start_y - bar_height - bar_spacing))
        dash_fill_width = bar_width if self.dash_timer <= 0 else int(bar_width * (self.dash_cooldown - self.dash_timer) / self.dash_cooldown)
        pygame.draw.rect(surface, RED, (start_x + PLAYER_MAX_TEMPORAL_SHIFT_USES * (bar_width + bar_spacing) + bar_spacing, start_y, bar_width, bar_height))
        pygame.draw.rect(surface, GREEN, (start_x + PLAYER_MAX_TEMPORAL_SHIFT_USES * (bar_width + bar_spacing) + bar_spacing, start_y, dash_fill_width, bar_height))

        # Echo Trace Cooldown Bar
        et_cooldown_text = font.render("Trace", True, WHITE)
        surface.blit(et_cooldown_text, (start_x + PLAYER_MAX_TEMPORAL_SHIFT_USES * (bar_width + bar_spacing) + bar_spacing + bar_width + bar_spacing, start_y - bar_height - bar_spacing))
        et_fill_width = bar_width if self.echo_trace_timer <= 0 else int(bar_width * (self.echo_trace_cooldown - self.echo_trace_timer) / self.echo_trace_cooldown)
        pygame.draw.rect(surface, RED, (start_x + PLAYER_MAX_TEMPORAL_SHIFT_USES * (bar_width + bar_spacing) + bar_spacing + bar_width + bar_spacing, start_y, bar_width, bar_height))
        pygame.draw.rect(surface, GREEN, (start_x + PLAYER_MAX_TEMPORAL_SHIFT_USES * (bar_width + bar_spacing) + bar_spacing + bar_width + bar_spacing, start_y, et_fill_width, bar_height))

    def update(self):
        self.handle_input()
        self.update_timers()

        # Boundary checking
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)

        # Echo Trace path generation
        if self.is_echo_tracing and len(self.echo_trace_path) < 100: # Limit path length
            self.echo_trace_path.append(self.rect.center)


class TemporalEcho(pygame.sprite.Sprite):
    def __init__(self, patrol_path):
        super().__init__()
        self.image = pygame.Surface([TEMPORAL_ECHO_SIZE, TEMPORAL_ECHO_SIZE], pygame.SRCALPHA)
        pygame.draw.circle(self.image, NEON_YELLOW, (TEMPORAL_ECHO_SIZE // 2, TEMPORAL_ECHO_SIZE // 2), TEMPORAL_ECHO_SIZE // 2)
        self.rect = self.image.get_rect()
        self.patrol_path = patrol_path
        self.current_path_index = 0
        self.rect.center = self.patrol_path[0]
        self.speed = TEMPORAL_ECHO_SPEED
        self.trail = []
        self.trail_duration = TEMPORAL_ECHO_TRAIL_DURATION
        self.respawn_timer = 0

    def update(self):
        if self.respawn_timer > 0:
            self.respawn_timer -= 1
            if self.respawn_timer == 0:
                self.respawn()
            return

        # Add current position to trail
        self.trail.append((self.rect.centerx, self.rect.centery, pygame.time.get_ticks()))

        # Remove old trails
        self.trail = [(x, y, t) for x, y, t in self.trail if pygame.time.get_ticks() - t < self.trail_duration * 10] # Keep slightly longer than duration for drawing

        # Move along patrol path
        target_x, target_y = self.patrol_path[self.current_path_index]
        dx = target_x - self.rect.centerx
        dy = target_y - self.rect.centery
        dist = (dx**2 + dy**2)**0.5

        if dist < self.speed:
            self.rect.centerx, self.rect.centery = target_x, target_y
            self.current_path_index = (self.current_path_index + 1) % len(self.patrol_path)
        else:
            self.rect.centerx += (dx / dist) * self.speed
            self.rect.centery += (dy / dist) * self.speed

    def draw_trail(self, surface):
        for i in range(len(self.trail) - 1, 0, -1):
            x1, y1, t1 = self.trail[i]
            x2, y2, t2 = self.trail[i-1]
            alpha = max(0, 255 * (pygame.time.get_ticks() - t1) // (self.trail_duration * 10))
            color = (255, 200, 0, alpha) # Yellow with fading alpha
            if alpha > 0:
                pygame.draw.line(surface, color, (x1, y1), (x2, y2), TEMPORAL_ECHO_SIZE // 2)

    def dissipate(self):
        self.respawn_timer = TEMPORAL_ECHO_RESPAWN_DELAY
        self.trail = []
        self.rect.center = (-100, -100) # Move off-screen

    def respawn(self):
        self.current_path_index = 0
        self.rect.center = self.patrol_path[0]
        self.respawn_timer = 0


class AnomalySentinel(pygame.sprite.Sprite):
    def __init__(self, patrol_path):
        super().__init__()
        self.image = pygame.Surface([ANOMALY_SENTINEL_SIZE, ANOMALY_SENTINEL_SIZE], pygame.SRCALPHA)
        pygame.draw.circle(self.image, NEON_MAGENTA, (ANOMALY_SENTINEL_SIZE // 2, ANOMALY_SENTINEL_SIZE // 2), ANOMALY_SENTINEL_SIZE // 2)
        self.rect = self.image.get_rect()
        self.rect.center = patrol_path[0] # Stationary for now, patrol_path ignored but kept for structure
        self.pulse_interval = ANOMALY_SENTINEL_PULSE_INTERVAL
        self.pulse_timer = self.pulse_interval
        self.pulse_radius = ANOMALY_SENTINEL_PULSE_RADIUS
        self.pulse_damage = ANOMALY_SENTINEL_PULSE_DAMAGE
        self.aggression_radius = ANOMALY_SENTINEL_AGGRESSION_RADIUS
        self.is_aggressive = False

    def update(self, player_pos):
        self.pulse_timer -= 1
        distance_to_player = ((self.rect.centerx - player_pos[0])**2 + (self.rect.centery - player_pos[1])**2)**0.5
        self.is_aggressive = distance_to_player < self.aggression_radius

        if self.pulse_timer <= 0:
            self.pulse_timer = self.pulse_interval
            self.trigger_pulse()
            return True # Indicate a pulse occurred
        return False

    def trigger_pulse(self):
        # Visual effect for pulse could be added here
        pass # Actual damage dealt in collision detection

    def get_pulse_rect(self):
        return pygame.Rect(self.rect.centerx - self.pulse_radius, self.rect.centery - self.pulse_radius, self.pulse_radius * 2, self.pulse_radius * 2)

class ParadoxShard(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([PARADOX_SHARD_SIZE, PARADOX_SHARD_SIZE], pygame.SRCALPHA)
        pygame.draw.circle(self.image, NEON_RED, (PARADOX_SHARD_SIZE // 2, PARADOX_SHARD_SIZE // 2), PARADOX_SHARD_SIZE // 2)
        self.rect = self.image.get_rect()
        self.speed = PARADOX_SHARD_SPEED
        self.teleport_interval = PARADOX_SHARD_TELEPORT_INTERVAL
        self.teleport_timer = self.teleport_interval
        self.teleport_range = PARADOX_SHARD_TELEPORT_RANGE
        self.damage_radius = PARADOX_SHARD_DAMAGE_RADIUS
        self.damage = PARADOX_SHARD_DAMAGE
        self.target_position = self.rect.center # Where it's trying to move

    def update(self, player_pos):
        self.teleport_timer -= 1
        if self.teleport_timer <= 0:
            self.teleport_timer = self.teleport_interval
            self.teleport(player_pos)
            self.target_position = self.rect.center # Update target after teleporting

        # Move towards target_position
        dx = self.target_position[0] - self.rect.centerx
        dy = self.target_position[1] - self.rect.centery
        dist = (dx**2 + dy**2)**0.5

        if dist < self.speed:
            self.rect.centerx, self.rect.centery = self.target_position
        else:
            self.rect.centerx += (dx / dist) * self.speed
            self.rect.centery += (dy / dist) * self.speed

    def teleport(self, player_pos):
        # Teleport to a random location within range of player
        angle = random.uniform(0, 2 * math.pi)
        offset_x = self.teleport_range * math.cos(angle)
        offset_y = self.teleport_range * math.sin(angle)

        new_x = player_pos[0] + offset_x
        new_y = player_pos[1] + offset_y

        # Ensure teleported position is within screen bounds
        new_x = max(PARADOX_SHARD_SIZE // 2, min(SCREEN_WIDTH - PARADOX_SHARD_SIZE // 2, new_x))
        new_y = max(PARADOX_SHARD_SIZE // 2, min(SCREEN_HEIGHT - PARADOX_SHARD_SIZE // 2, new_y))

        self.rect.center = (int(new_x), int(new_y))

    def get_damage_rect(self):
        return pygame.Rect(self.rect.centerx - self.damage_radius, self.rect.centery - self.damage_radius, self.damage_radius * 2, self.damage_radius * 2)


class TemporalRift(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height], pygame.SRCALPHA)
        self.image.fill((50, 0, 50, 150)) # Semi-transparent purple
        self.rect = self.image.get_rect(topleft=(x, y))
        self.damage = TEMPORAL_RIFT_DAMAGE
        self.pulse_interval = TEMPORAL_RIFT_PULSE_INTERVAL
        self.pulse_timer = self.pulse_interval

    def update(self):
        self.pulse_timer -= 1
        if self.pulse_timer <= 0:
            self.pulse_timer = self.pulse_interval
            # Visual effect for pulse could be added

class TemporalDistortion(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height], pygame.SRCALPHA)
        self.image.fill((0, 50, 50, 100)) # Semi-transparent cyan
        self.rect = self.image.get_rect(topleft=(x, y))
        self.pull_force = TEMPORAL_DISTORTION_PULL_FORCE
        self.max_pull_radius = TEMPORAL_DISTORTION_MAX_PULL_RADIUS

    def apply_pull(self, player_rect):
        distance = ((self.rect.centerx - player_rect.centerx)**2 + (self.rect.centery - player_rect.centery)**2)**0.5
        if distance < self.max_pull_radius and distance > 0:
            force_magnitude = self.pull_force * (1 - distance / self.max_pull_radius) # Stronger closer
            angle = math.atan2(self.rect.centery - player_rect.centery, self.rect.centerx - player_rect.centerx)
            pull_x = force_magnitude * math.cos(angle)
            pull_y = force_magnitude * math.sin(angle)
            return pull_x, pull_y
        return 0, 0

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(WALL_COLOR)
        self.rect = self.image.get_rect(topleft=(x, y))

class Rock(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(ROCK_COLOR)
        self.rect = self.image.get_rect(topleft=(x, y))

class CollectibleFragment(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([COLLECTIBLE_FRAGMENT_SIZE, COLLECTIBLE_FRAGMENT_SIZE], pygame.SRCALPHA)
        pygame.draw.circle(self.image, NEON_YELLOW, (COLLECTIBLE_FRAGMENT_SIZE // 2, COLLECTIBLE_FRAGMENT_SIZE // 2), COLLECTIBLE_FRAGMENT_SIZE // 2)
        self.rect = self.image.get_rect(center=(x, y))
        self.value = COLLECTIBLE_FRAGMENT_VALUE

class Powerup(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.image = pygame.Surface([POWERUP_SIZE, POWERUP_SIZE], pygame.SRCALPHA)
        self.type = type
        color = (0,0,0)
        if type == "chrono_charge":
            color = NEON_CYAN
        elif type == "cooldown_reduction": # Map to Echo Amplifier
            color = NEON_MAGENTA
        elif type == "shield": # Map to Stabilizer Fragment
            color = NEON_YELLOW
        pygame.draw.circle(self.image, color, (POWERUP_SIZE // 2, POWERUP_SIZE // 2), POWERUP_SIZE // 2)
        self.rect = self.image.get_rect(center=(x, y))
        self.color = color

class ExitPortal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([EXIT_PORTAL_SIZE, EXIT_PORTAL_SIZE], pygame.SRCALPHA)
        pygame.draw.circle(self.image, GREEN, (EXIT_PORTAL_SIZE // 2, EXIT_PORTAL_SIZE // 2), EXIT_PORTAL_SIZE // 2)
        self.rect = self.image.get_rect(center=(x, y))
        self.active = False # Becomes active when objectives met

    def activate(self):
        self.active = True
        self.image.fill((0, 255, 0, 128)) # Slightly transparent green when active

# --- Sprite Groups ---
all_sprites = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
hazards = pygame.sprite.Group()
enemies = pygame.sprite.Group()
powerups = pygame.sprite.Group()
collectible_fragments = pygame.sprite.Group()
player_group = pygame.sprite.GroupSingle()
exit_portal_group = pygame.sprite.GroupSingle()

# --- Game Variables ---
player = None
exit_portal = None
score = 0
fragments_collected = 0
time_remaining = level_data["time_limit"]
level_start_time = 0
game_over_reason = ""

# --- Helper Functions ---

def setup_level(level_data):
    global player, exit_portal, score, fragments_collected, time_remaining

    # Clear existing groups
    all_sprites.empty()
    obstacles.empty()
    hazards.empty()
    enemies.empty()
    powerups.empty()
    collectible_fragments.empty()
    player_group.empty()
    exit_portal_group.empty()

    # Player
    player = Player()
    player_group.add(player)
    all_sprites.add(player)

    # Obstacles and Hazards
    for obs_data in level_data["obstacles"]:
        x, y, w, h = obs_data["x"], obs_data["y"], obs_data["width"], obs_data["height"]
        obs_type = obs_data["type"]
        rect = pygame.Rect(x, y, w, h)

        if obs_type == "wall":
            obj = Wall(x, y, w, h)
            obstacles.add(obj)
            all_sprites.add(obj)
        elif obs_type == "rock":
            obj = Rock(x, y, w, h)
            obstacles.add(obj)
            all_sprites.add(obj)
        elif obs_type == "temporal_rift":
            obj = TemporalRift(x, y, w, h)
            hazards.add(obj)
            all_sprites.add(obj)
        elif obs_type == "temporal_distortion":
            obj = TemporalDistortion(x, y, w, h)
            hazards.add(obj)
            all_sprites.add(obj)
        elif obs_type == "paradox_fragment_cluster":
            # Spawn multiple fragments
            num_fragments = 5 # Arbitrary number for a cluster
            for _ in range(num_fragments):
                frag_x = random.randint(x, x + w - COLLECTIBLE_FRAGMENT_SIZE)
                frag_y = random.randint(y, y + h - COLLECTIBLE_FRAGMENT_SIZE)
                fragment = CollectibleFragment(frag_x, frag_y)
                collectible_fragments.add(fragment)
                all_sprites.add(fragment)


    # Powerups
    for pup_data in level_data["powerups"]:
        powerup = Powerup(pup_data["x"], pup_data["y"], pup_data["type"])
        powerups.add(powerup)
        all_sprites.add(powerup)

    # Enemies
    for enemy_data in level_data["enemies"]:
        enemy_type = enemy_data["type"]
        x, y = enemy_data["x"], enemy_data["y"]
        patrol_path = enemy_data.get("patrol_path", [[x, y]]) # Default to stationary if no path

        if enemy_type == "basic": # Temporal Echo
            enemy = TemporalEcho(patrol_path)
            enemies.add(enemy)
            all_sprites.add(enemy)
        elif enemy_type == "aggressive": # Anomaly Sentinel
            enemy = AnomalySentinel(patrol_path)
            enemies.add(enemy)
            all_sprites.add(enemy)
        # Paradox Shard doesn't have patrol paths in this level design but will be spawned randomly

    # Spawn Paradox Shards (as per game concept, they teleport randomly)
    for _ in range(2): # Spawn 2 paradox shards for this level
        shard = ParadoxShard()
        shard.rect.center = (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)) # Initial random position
        enemies.add(shard)
        all_sprites.add(shard)

    # Exit Portal
    # Determine a reasonable exit portal position, not explicitly defined
    exit_portal_x = SCREEN_WIDTH - EXIT_PORTAL_SIZE - 20
    exit_portal_y = SCREEN_HEIGHT - EXIT_PORTAL_SIZE - 20
    exit_portal = ExitPortal(exit_portal_x, exit_portal_y)
    exit_portal_group.add(exit_portal)
    all_sprites.add(exit_portal)

    # Objectives
    objective_fragments = 0
    objective_enemies = 0
    for obj in level_data["objectives"]:
        if obj["target"] == "paradox_fragments":
            objective_fragments = obj["count"]
        elif obj["target"] == "enemies":
            objective_enemies = obj["count"]

    global required_fragments, required_enemies
    required_fragments = objective_fragments
    required_enemies = objective_enemies

    # Reset game variables
    score = 0
    fragments_collected = 0
    time_remaining = level_data["time_limit"]
    level_start_time = pygame.time.get_ticks()


def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)

def draw_echo_trace(surface, player_echo_trace_path):
    if not player_echo_trace_path:
        return

    for i in range(len(player_echo_trace_path) - 1):
        start_pos = player_echo_trace_path[i]
        end_pos = player_echo_trace_path[i+1]
        pygame.draw.line(surface, (0, 255, 255, 100), start_pos, end_pos, 3) # Faint cyan line

def draw_enemy_paths(surface, enemy_group):
    for enemy in enemy_group:
        if isinstance(enemy, TemporalEcho) and enemy.patrol_path:
            path_points = enemy.patrol_path
            if len(path_points) > 1:
                for i in range(len(path_points) - 1):
                    pygame.draw.line(surface, (255, 100, 0, 150), path_points[i], path_points[i+1], 2) # Faint orange line

def check_player_collision(player, obstacles, hazards, enemies, powerups, collectible_fragments, exit_portal):
    global fragments_collected, score, current_state, game_over_reason

    # Obstacle collision
    for obs in obstacles:
        if player.rect.colliderect(obs.rect):
            # Basic collision response: revert player position
            if player.rect.right <= obs.rect.left or player.rect.left >= obs.rect.right:
                player.rect.x -= (player.rect.centerx - obs.rect.centerx) * 0.1 # Nudge away
            if player.rect.bottom <= obs.rect.top or player.rect.top >= obs.rect.bottom:
                player.rect.y -= (player.rect.centery - obs.rect.centery) * 0.1 # Nudge away

            # Kinetic Rebound (if dashing into walls)
            if player.is_dashing and not player.kinetic_rebound_active:
                player.kinetic_rebound_active = True
                player.kinetic_rebound_timer = player.kinetic_rebound_duration
                dash_dir_x = player.dash_direction[0]
                dash_dir_y = player.dash_direction[1]

                # Determine rebound direction (opposite of dash)
                rebound_dir_x = -dash_dir_x
                rebound_dir_y = -dash_dir_y

                # Apply a burst of speed in the rebound direction
                player.rect.x += rebound_dir_x * player.dash_speed * player.kinetic_rebound_boost
                player.rect.y += rebound_dir_y * player.dash_speed * player.kinetic_rebound_boost

                # Temporarily disable dash to prevent multiple rebounds
                player.is_dashing = False 

    # Hazard collision
    for hazard in hazards:
        if player.rect.colliderect(hazard.rect):
            if isinstance(hazard, TemporalRift):
                if hazard.pulse_timer <= 0: # Damage on pulse
                    player.take_damage(hazard.damage)
            elif isinstance(hazard, TemporalDistortion):
                pull_x, pull_y = hazard.apply_pull(player.rect)
                player.rect.x += pull_x
                player.rect.y += pull_y

    # Enemy collision & interaction
    enemies_to_remove = []
    for enemy in enemies:
        if player.rect.colliderect(enemy.rect):
            if isinstance(enemy, TemporalEcho):
                player.take_damage(10) # Basic damage
                enemy.dissipate() # Echo dissipates on collision
            elif isinstance(enemy, AnomalySentinel):
                player.take_damage(10) # Collision damage
            elif isinstance(enemy, ParadoxShard):
                player.take_damage(enemy.damage)

        # Paradox Shard damage zone
        if isinstance(enemy, ParadoxShard):
            if player.rect.colliderect(enemy.get_damage_rect()):
                player.take_damage(enemy.damage)

        # Anomaly Sentinel pulse damage
        if isinstance(enemy, AnomalySentinel):
            if enemy.get_pulse_rect().colliderect(player.rect):
                 player.take_damage(enemy.pulse_damage)

        # Temporal Echo dissipation logic (player too far)
        if isinstance(enemy, TemporalEcho):
            dist_to_player = ((enemy.rect.centerx - player.rect.centerx)**2 + (enemy.rect.centery - player.rect.centery)**2)**0.5
            if dist_to_player > TEMPORAL_ECHO_DETECTION_RADIUS and enemy.respawn_timer == 0:
                enemy.dissipate()

    # Powerup collection
    collected_powerups = pygame.sprite.spritecollide(player, powerups, True)
    for pup in collected_powerups:
        if pup.type == "chrono_charge":
            player.refill_temporal_shift()
        elif pup.type == "cooldown_reduction": # Echo Amplifier
            player.echo_trace_duration += 60 # Extend duration by 1 second
            player.echo_trace_cooldown -= 30 # Reduce cooldown
            player.echo_trace_cooldown = max(60, player.echo_trace_cooldown) # Min cooldown
        elif pup.type == "shield": # Stabilizer Fragment
            player.current_health = player.max_health # Full heal, acts as shield by resetting health
            # Add actual shield visual/logic if needed

    # Collectible fragment collection
    collected_fragments = pygame.sprite.spritecollide(player, collectible_fragments, True)
    for fragment in collected_fragments:
        fragments_collected += fragment.value
        score += fragment.value * 10 # Points for collecting fragments

    # Exit portal
    if exit_portal.active and player.rect.colliderect(exit_portal.rect):
        current_state = GameState.LEVEL_COMPLETE

    # Update objectives progress
    current_enemies_alive = len([e for e in enemies if e.respawn_timer == 0])

    if fragments_collected >= required_fragments and current_enemies_alive <= 0:
        exit_portal.activate()

def update_enemy_anomalies(player_pos):
    global score

    # Paradox Shard specific interactions
    for enemy in enemies:
        if isinstance(enemy, ParadoxShard):
            enemy.update(player_pos)
            # Damage player if within paradox shard's damage radius
            if player.rect.colliderect(enemy.get_damage_rect()):
                player.take_damage(enemy.damage)

    # Anomaly Sentinel pulse logic
    for enemy in enemies:
        if isinstance(enemy, AnomalySentinel):
            enemy.update(player_pos)
            if enemy.pulse_timer <= 0: # Pulse occurred
                for hazard_rect in [enemy.get_pulse_rect()]: # Treat sentinel pulse as a temporary hazard
                    if player.rect.colliderect(hazard_rect):
                        player.take_damage(enemy.pulse_damage)


def apply_player_abilities(player, all_sprites, hazards):
    # Temporal Shift visual/effect
    if player.is_temporal_shifting:
        # Example: Draw a glow around the player
        glow_surface = pygame.Surface((PLAYER_SIZE * 2, PLAYER_SIZE * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (0, 255, 255, 100), (PLAYER_SIZE, PLAYER_SIZE), PLAYER_SIZE)
        screen.blit(glow_surface, (player.rect.centerx - PLAYER_SIZE, player.rect.centery - PLAYER_SIZE))

        # Can temporarily disable hazards or make player ignore them
        pass

    # Kinetic Rebound effect
    if player.kinetic_rebound_active:
        # Could add a visual trail or speed lines
        pass

    # Echo Trace path visualization
    if player.is_echo_tracing:
        # Draw the predicted path of temporal echoes or other moving hazards
        pass

# --- Game State Functions ---

def run_menu():
    global current_state
    screen.fill(BLACK)
    draw_text(screen, "CHRONOSWEEPER", large_font, NEON_CYAN, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
    draw_text(screen, "Press SPACE to Start", font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    draw_text(screen, "WASD/Arrows to Move", font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
    draw_text(screen, "Space to Dash", font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90)
    draw_text(screen, "LShift for Temporal Shift", font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 130)
    draw_text(screen, "E for Echo Trace", font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 170)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                current_state = GameState.PLAYING
                setup_level(level_data) # Setup the first level
    return True

def run_playing():
    global current_state, score, fragments_collected, time_remaining, game_over_reason

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: # Quit game
                current_state = GameState.MENU
                return True

    # Update Time
    current_time = pygame.time.get_ticks()
    time_elapsed = (current_time - level_start_time) / 1000
    time_remaining = max(0, level_data["time_limit"] - int(time_elapsed))
    if time_remaining <= 0:
        game_over_reason = "Time's Up!"
        current_state = GameState.GAME_OVER
        return True

    # Update Player and other entities
    player.update()
    for enemy in enemies:
        if isinstance(enemy, TemporalEcho):
            enemy.update()
        elif isinstance(enemy, AnomalySentinel):
            enemy.update(player.rect.center)
        elif isinstance(enemy, ParadoxShard):
            enemy.update(player.rect.center)
    for hazard in hazards:
        hazard.update()

    # Collision checks
    check_player_collision(player, obstacles, hazards, enemies, powerups, collectible_fragments, exit_portal)
    update_enemy_anomalies(player.rect.center)

    # Powerup logic (e.g. shield effect duration)

    # Drawing
    screen.fill(DARK_BLUE) # Retro-futuristic background

    # Draw environment
    for obs in obstacles:
        screen.blit(obs.image, obs.rect)
    for hazard in hazards:
        screen.blit(hazard.image, hazard.rect)
        # Visual effects for hazards (e.g., pulsing rift) could go here

    # Draw enemies with trails
    for enemy in enemies:
        if isinstance(enemy, TemporalEcho):
            enemy.draw_trail(screen)
    for enemy in enemies:
        screen.blit(enemy.image, enemy.rect)

    # Draw collected fragments
    for fragment in collectible_fragments:
        screen.blit(fragment.image, fragment.rect)

    # Draw powerups
    for pup in powerups:
        screen.blit(pup.image, pup.rect)

    # Draw Exit Portal
    screen.blit(exit_portal.image, exit_portal.rect)

    # Draw Player
    screen.blit(player.image, player.rect)

    # Apply Player Abilities Visuals
    apply_player_abilities(player, all_sprites, hazards) # Pass necessary groups

    # Draw Echo Trace
    if player.is_echo_tracing:
        draw_echo_trace(screen, player.echo_trace_path)

    # Draw Enemy Patrol Paths (for debugging/visuals)
    # draw_enemy_paths(screen, enemies)

    # Draw UI elements
    player.draw_health_bar(screen)
    player.draw_ability_bars(screen)

    draw_text(screen, f"Fragments: {fragments_collected}/{required_fragments}", font, WHITE, SCREEN_WIDTH - 150, 30)
    draw_text(screen, f"Time: {time_remaining}", font, WHITE, SCREEN_WIDTH - 100, 70)
    draw_text(screen, f"Score: {score}", font, WHITE, SCREEN_WIDTH - 100, 110)

    return True

def run_level_complete():
    global current_state, level_data
    screen.fill(BLACK)
    draw_text(screen, "LEVEL COMPLETE", large_font, GREEN, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
    draw_text(screen, f"Score: {score}", font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    draw_text(screen, "Press SPACE to continue", font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Logic for moving to the next level or main menu
                # For now, just go back to menu
                current_state = GameState.MENU
                return True
    return True

def run_game_over():
    global current_state
    screen.fill(BLACK)
    draw_text(screen, "GAME OVER", large_font, RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
    draw_text(screen, game_over_reason, font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)
    draw_text(screen, f"Final Score: {score}", font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)
    draw_text(screen, "Press R to Restart (Menu)", font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                current_state = GameState.MENU
                return True
    return True

# --- Main Game Loop ---
running = True
while running:
    if current_state == GameState.MENU:
        running = run_menu()
    elif current_state == GameState.PLAYING:
        running = run_playing()
    elif current_state == GameState.LEVEL_COMPLETE:
        running = run_level_complete()
    elif current_state == GameState.GAME_OVER:
        running = run_game_over()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()