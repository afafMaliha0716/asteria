
import pygame
import sys
import math
import json
import random

# --- Pygame Initialization ---
pygame.init()

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Turtle Tide: Ocean's Call"
FPS = 60

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SAND_COLOR = (244, 212, 126)
OCEAN_COLOR = (70, 130, 180) # SteelBlue
TURTLE_COLOR = (124, 252, 0) # LawnGreen
PATH_COLOR = (100, 100, 100) # Dark Gray
HIGHLIGHT_COLOR = (255, 255, 0) # Yellow
COCONUT_COLOR = (139, 69, 19) # SaddleBrown
SEAWEED_COLOR = (34, 139, 34) # ForestGreen
ROCK_COLOR = (105, 105, 105) # DimGray
SEAGULL_COLOR = (200, 200, 200) # Light Gray
POWERUP_COLOR = (255, 200, 0) # Gold
NEST_COLOR = (160, 82, 45) # Sienna
EXIT_COLOR = (135, 206, 250) # LightSkyBlue
UI_BG_COLOR = (50, 50, 50, 180) # Dark transparent grey

# --- Game States ---
GAME_STATE_MENU = 0
GAME_STATE_PLAYING = 1
GAME_STATE_GAME_OVER = 2
GAME_STATE_LEVEL_COMPLETE = 3

# --- Game Variables ---
game_state = GAME_STATE_MENU
current_level_data = None
score = 0
turtles_saved_current_level = 0
turtles_lost_current_level = 0
ability_clear_uses = 0
ability_distract_uses = 0

# Cooldowns (in seconds)
CLEAR_COOLDOWN = 3.0
DISTRACT_COOLDOWN = 4.0
last_clear_time = 0.0
last_distract_time = 0.0

# Path drawing variables
drawing_path = False
current_path_points = []
PATH_SEGMENT_LENGTH_SQ = 20**2 # Square of minimum distance between path points

# --- Set up the display ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(SCREEN_TITLE)
clock = pygame.time.Clock()

# --- Fonts ---
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)
small_font = pygame.font.Font(None, 24)

# --- Classes ---

class Entity:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

    def collides_with(self, other_rect):
        return self.rect.colliderect(other_rect)

class Turtle(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 15, 15, TURTLE_COLOR) # Smaller size for baby turtle
        self.speed = 40.0 # Base speed in pixels per second
        self.original_speed = self.speed
        self.path = []
        self.path_index = 0
        self.alive = True
        self.saved = False
        self.guardian_aura_active = False
        self.aura_timer = 0.0
        self.speed_boost_active = False
        self.speed_boost_timer = 0.0

    def set_path(self, path_points):
        self.path = []
        if path_points:
            # Ensure path starts from current turtle position for smooth transition
            self.path.append(pygame.Vector2(self.rect.center))
            # Add other points, ensuring they are not too close to the last one
            for p in path_points:
                if self.path[-1].distance_squared_to(p) > 10: # Minimum distance for path points
                    self.path.append(pygame.Vector2(p))
            self.path_index = 0
            
    def update(self, dt):
        if not self.alive or self.saved:
            return

        # Handle speed boost
        if self.speed_boost_active:
            self.speed_boost_timer -= dt
            if self.speed_boost_timer <= 0:
                self.speed_boost_active = False
                self.speed = self.original_speed # Reset speed

        # Handle guardian aura
        if self.guardian_aura_active:
            self.aura_timer -= dt
            if self.aura_timer <= 0:
                self.guardian_aura_active = False

        if not self.path or self.path_index >= len(self.path):
            return

        target_pos = self.path[self.path_index]
        current_pos = pygame.Vector2(self.rect.center)

        # Calculate direction
        direction_vec = target_pos - current_pos
        distance = direction_vec.length()

        if distance < self.speed * dt: # Close enough to target point
            self.rect.center = target_pos
            self.path_index += 1
            if self.path_index >= len(self.path):
                self.path = [] # Path finished
        else:
            # Move towards the target
            direction_vec.normalize_ip()
            self.rect.x += direction_vec.x * self.speed * dt
            self.rect.y += direction_vec.y * self.speed * dt

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.rect.center, self.rect.width // 2)
        if self.guardian_aura_active:
            pygame.draw.circle(surface, HIGHLIGHT_COLOR, self.rect.center, self.rect.width // 2 + 5, 2) # Aura effect
        
        # Draw the path it's currently following
        if self.path and self.path_index < len(self.path):
            points_to_draw = [self.rect.center] + [p for p in self.path[self.path_index:]]
            if len(points_to_draw) > 1:
                pygame.draw.lines(surface, PATH_COLOR, False, points_to_draw, 1)

    def die(self):
        self.alive = False

    def activate_guardian_aura(self, duration):
        self.guardian_aura_active = True
        self.aura_timer = duration

    def activate_speed_boost(self, duration, boost_factor=2):
        self.speed_boost_active = True
        self.speed_boost_timer = duration
        self.speed = self.original_speed * boost_factor

class Obstacle(Entity):
    def __init__(self, x, y, width, height, obstacle_type, clearable):
        color = COCONUT_COLOR if obstacle_type == "fallen_coconut" else \
                SEAWEED_COLOR if obstacle_type == "seaweed_clump" else \
                ROCK_COLOR
        super().__init__(x, y, width, height, color)
        self.type = obstacle_type
        self.clearable = clearable
        self.cleared = False
        self.original_color = self.color

    def draw(self, surface):
        if not self.cleared:
            super().draw(surface)

    def clear(self):
        if self.clearable:
            self.cleared = True

class Predator(Entity):
    def __init__(self, x, y, width, height, predator_type, speed, aggro_range, patrol_path):
        color = SEAGULL_COLOR # Only seagull for Level 1
        super().__init__(x, y, width, height, color)
        self.type = predator_type
        self.speed = speed
        self.aggro_range = aggro_range
        self.patrol_path = [pygame.Vector2(p) for p in patrol_path]
        self.patrol_index = 0
        self.target_pos = self.patrol_path[self.patrol_index]
        self.distracted = False
        self.distraction_timer = 0.0
        self.distraction_cooldown = 0.0 # From level data

    def update(self, dt, turtles):
        if self.distracted:
            self.distraction_timer -= dt
            if self.distraction_timer <= 0:
                self.distracted = False
            return

        # Check for turtles in aggro range
        closest_turtle = None
        min_dist = self.aggro_range + 1

        for turtle in turtles:
            if turtle.alive and not turtle.saved:
                dist = pygame.Vector2(self.rect.center).distance_to(turtle.rect.center)
                if dist < min_dist:
                    min_dist = dist
                    closest_turtle = turtle

        if closest_turtle and min_dist <= self.aggro_range:
            # Aggro: move towards turtle
            self.target_pos = pygame.Vector2(closest_turtle.rect.center)
            
            # Check for direct collision to attack
            if self.collides_with(closest_turtle.rect):
                if not closest_turtle.guardian_aura_active:
                    closest_turtle.die()
                else:
                    closest_turtle.guardian_aura_active = False # Aura consumed
                self.distract(self.distraction_cooldown) # Predator briefly stunned after attack
        else:
            # Patrol: move along path
            if pygame.Vector2(self.rect.center).distance_to(self.target_pos) < self.speed * dt:
                self.rect.center = self.target_pos
                self.patrol_index = (self.patrol_index + 1) % len(self.patrol_path)
                self.target_pos = self.patrol_path[self.patrol_index]
            else:
                direction = (self.target_pos - pygame.Vector2(self.rect.center)).normalize()
                self.rect.x += direction.x * self.speed * dt
                self.rect.y += direction.y * self.speed * dt

    def draw(self, surface):
        super().draw(surface)
        if self.distracted:
            pygame.draw.circle(surface, HIGHLIGHT_COLOR, self.rect.center, self.rect.width // 2 + 5, 2) # Distraction effect

    def distract(self, duration):
        self.distracted = True
        self.distraction_timer = duration

class Powerup(Entity):
    def __init__(self, x, y, powerup_type, duration):
        super().__init__(x, y, 20, 20, POWERUP_COLOR)
        self.type = powerup_type
        self.duration = duration
        self.collected = False

    def draw(self, surface):
        if not self.collected:
            super().draw(surface)
            # Add a small identifier for the powerup type
            if self.type == "turtle_speed_boost":
                text_surf = small_font.render("S", True, BLACK)
            elif self.type == "guardian_aura":
                text_surf = small_font.render("G", True, BLACK)
            else:
                text_surf = small_font.render("?", True, BLACK)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)


class Level:
    def __init__(self, level_data):
        global score, turtles_saved_current_level, turtles_lost_current_level, ability_clear_uses, ability_distract_uses

        self.width = level_data["size"]["width"]
        self.height = level_data["size"]["height"]
        self.time_limit = level_data["time_limit"]
        self.time_left = float(self.time_limit) # Use float for accurate countdown

        self.turtles = []
        self.obstacles = []
        self.predators = []
        self.powerups = []

        self.nest_rect = None
        self.ocean_exit_rect = None
        self.initial_turtle_count = 0

        # Reset level-specific stats
        score = 0
        turtles_saved_current_level = 0
        turtles_lost_current_level = 0
        ability_clear_uses = 0
        ability_distract_uses = 0
        global last_clear_time, last_distract_time
        last_clear_time = 0.0
        last_distract_time = 0.0

        # Parse spawn points
        for sp in level_data["spawn_points"]:
            if sp["type"] == "turtle_nest":
                self.nest_rect = pygame.Rect(sp["x"] - 25, sp["y"] - 25, 50, 50) # Nest area
                self.initial_turtle_count = sp["initial_turtles"]
                for _ in range(self.initial_turtle_count):
                    # Spawn turtles slightly randomly around the nest
                    turtle_x = sp["x"] + random.randint(-10, 10)
                    turtle_y = sp["y"] + random.randint(-10, 10)
                    self.turtles.append(Turtle(turtle_x, turtle_y))
            elif sp["type"] == "ocean_exit":
                self.ocean_exit_rect = pygame.Rect(sp["x"] - 50, sp["y"] - 50, 100, 100) # Exit area

        # Parse obstacles
        for ob in level_data["obstacles"]:
            self.obstacles.append(Obstacle(ob["x"], ob["y"], ob["width"], ob["height"], ob["type"], ob["clearable"]))

        # Parse enemies
        for en in level_data["enemies"]:
            if en["type"] == "seagull":
                seagull_width = 30
                seagull_height = 30
                predator = Predator(en["x"], en["y"], seagull_width, seagull_height, en["type"], en["speed"], en["aggro_range"], en["patrol_path"])
                predator.distraction_cooldown = en["cooldown_distraction"]
                self.predators.append(predator)

        # Parse powerups
        for pu in level_data["powerups"]:
            self.powerups.append(Powerup(pu["x"], pu["y"], pu["type"], pu["duration"]))

        # Objectives
        self.objectives = level_data["objectives"]
        self.min_turtles_to_save = 0
        for obj in self.objectives:
            if obj["type"] == "reach_destination" and obj["target_entity_type"] == "turtle":
                self.min_turtles_to_save = obj["count"]

    def update(self, dt):
        global turtles_saved_current_level, turtles_lost_current_level, game_state, score

        self.time_left -= dt
        if self.time_left <= 0:
            self.time_left = 0
            if turtles_saved_current_level < self.min_turtles_to_save:
                game_state = GAME_STATE_GAME_OVER
                print("Time ran out! Game Over.")
                return
            else:
                self.calculate_score()
                game_state = GAME_STATE_LEVEL_COMPLETE
                print("Level Complete! Time bonus.")
                return

        for turtle in self.turtles:
            turtle.update(dt)

            if not turtle.alive or turtle.saved: # Skip further checks for dead/saved turtles
                continue

            # Check collision with obstacles (if not cleared)
            for obstacle in self.obstacles:
                if not obstacle.cleared and turtle.collides_with(obstacle.rect):
                    # Turtles can't pass non-clearable obstacles, or clearable ones that aren't cleared
                    turtle.path = [] # Stop turtle if it hits an obstacle
                    break # A turtle can only collide with one obstacle at a time

            # Check collision with powerups
            for powerup in self.powerups:
                if not powerup.collected and turtle.collides_with(powerup.rect):
                    powerup.collected = True
                    if powerup.type == "turtle_speed_boost":
                        turtle.activate_speed_boost(powerup.duration)
                        print("Turtle collected speed boost!")
                    elif powerup.type == "guardian_aura":
                        turtle.activate_guardian_aura(powerup.duration)
                        print("Turtle collected guardian aura!")

            # Check if turtle reached ocean
            if self.ocean_exit_rect and turtle.collides_with(self.ocean_exit_rect) and not turtle.saved:
                turtle.saved = True
                turtles_saved_current_level += 1
                score += 100 # Base points per turtle
                print(f"Turtle saved! Total saved: {turtles_saved_current_level}")
                if turtles_saved_current_level >= self.min_turtles_to_save:
                    self.calculate_score()
                    game_state = GAME_STATE_LEVEL_COMPLETE
                    print("Level objective met! Level Complete.")
                    return

        # Update predators
        for predator in self.predators:
            predator.update(dt, self.turtles)

        # Check for dead turtles
        turtles_lost_current_level = sum(1 for t in self.turtles if not t.alive and not t.saved)
        # If too many turtles died, and we can no longer reach the objective
        if self.initial_turtle_count - turtles_lost_current_level < self.min_turtles_to_save:
            game_state = GAME_STATE_GAME_OVER
            print("Too many turtles lost! Game Over.")
            return

    def draw(self, surface):
        # Draw background
        surface.fill(SAND_COLOR)
        # Ocean area will be at the top
        pygame.draw.rect(surface, OCEAN_COLOR, (0, 0, self.width, self.ocean_exit_rect.centery + self.ocean_exit_rect.height // 2))

        # Draw nest and exit
        if self.nest_rect:
            pygame.draw.rect(surface, NEST_COLOR, self.nest_rect)
            nest_text = small_font.render("NEST", True, WHITE)
            text_rect = nest_text.get_rect(center=self.nest_rect.center)
            surface.blit(nest_text, text_rect)
        if self.ocean_exit_rect:
            pygame.draw.rect(surface, EXIT_COLOR, self.ocean_exit_rect)
            ocean_text = small_font.render("OCEAN", True, BLACK)
            text_rect = ocean_text.get_rect(center=self.ocean_exit_rect.center)
            surface.blit(ocean_text, text_rect)

        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(surface)

        # Draw powerups
        for powerup in self.powerups:
            powerup.draw(surface)

        # Draw current path being drawn
        if drawing_path and len(current_path_points) > 1:
            pygame.draw.lines(surface, HIGHLIGHT_COLOR, False, current_path_points, 2)

        # Draw turtles (alive first, then dead/saved)
        # Drawing order matters, alive turtles need to be visible on top
        for turtle in sorted(self.turtles, key=lambda t: (t.alive, not t.saved), reverse=True):
            if turtle.alive and not turtle.saved:
                turtle.draw(surface)
            elif turtle.saved:
                # Draw saved turtles slightly differently, e.g., faded or smaller
                pygame.draw.circle(surface, (TURTLE_COLOR[0], TURTLE_COLOR[1], TURTLE_COLOR[2], 100), turtle.rect.center, turtle.rect.width // 2)
            else: # Dead
                pygame.draw.circle(surface, BLACK, turtle.rect.center, turtle.rect.width // 2, 1) # Outline

        # Draw predators
        for predator in self.predators:
            predator.draw(surface)

        # Draw UI
        self.draw_ui(surface)

    def draw_ui(self, surface):
        # Semi-transparent background for UI
        s = pygame.Surface((SCREEN_WIDTH, 70), pygame.SRCALPHA)
        s.fill(UI_BG_COLOR)
        surface.blit(s, (0, 0))

        # Time left
        time_text = font.render(f"Time: {int(self.time_left)}s", True, WHITE)
        surface.blit(time_text, (SCREEN_WIDTH - time_text.get_width() - 20, 10))

        # Turtles saved / total
        turtles_text = font.render(f"Saved: {turtles_saved_current_level}/{self.initial_turtle_count} ({self.min_turtles_to_save} min)", True, WHITE)
        surface.blit(turtles_text, (20, 10))

        # Score
        score_text = font.render(f"Score: {score}", True, WHITE)
        surface.blit(score_text, (20, 40))

        # Ability cooldowns
        current_time = pygame.time.get_ticks() / 1000.0
        clear_cooldown_left = max(0.0, CLEAR_COOLDOWN - (current_time - last_clear_time))
        distract_cooldown_left = max(0.0, DISTRACT_COOLDOWN - (current_time - last_distract_time))

        clear_text = font.render(f"Clear: {clear_cooldown_left:.1f}s", True, WHITE if clear_cooldown_left == 0 else (150, 150, 150))
        distract_text = font.render(f"Distract: {distract_cooldown_left:.1f}s", True, WHITE if distract_cooldown_left == 0 else (150, 150, 150))

        surface.blit(clear_text, (SCREEN_WIDTH // 2 - clear_text.get_width() - 50, 25))
        surface.blit(distract_text, (SCREEN_WIDTH // 2 + 50, 25))


    def calculate_score(self):
        global score

        # Time Bonus
        time_bonus = int(self.time_left * 10)
        score += time_bonus
        print(f"Time Bonus: {time_bonus}")

        # Efficiency Bonus
        efficiency_bonus = 0
        if ability_clear_uses == 0:
            efficiency_bonus += 50
        elif ability_clear_uses <= 1:
            efficiency_bonus += 20
        if ability_distract_uses == 0:
            efficiency_bonus += 50
        elif ability_distract_uses <= 1:
            efficiency_bonus += 20
        score += efficiency_bonus
        print(f"Efficiency Bonus: {efficiency_bonus} (Clears: {ability_clear_uses}, Distractions: {ability_distract_uses})")

        # Perfect Run Bonus
        if turtles_saved_current_level == self.initial_turtle_count:
            perfect_bonus = 500
            score += perfect_bonus
            print(f"Perfect Run Bonus: {perfect_bonus}")


# --- Game Functions ---

def load_level(level_json):
    global current_level_data
    current_level_data = Level(level_json)

def reset_game():
    global game_state, score, turtles_saved_current_level, turtles_lost_current_level, ability_clear_uses, ability_distract_uses
    global last_clear_time, last_distract_time, drawing_path, current_path_points

    game_state = GAME_STATE_MENU
    score = 0
    turtles_saved_current_level = 0
    turtles_lost_current_level = 0
    ability_clear_uses = 0
    ability_distract_uses = 0
    last_clear_time = 0.0
    last_distract_time = 0.0
    drawing_path = False
    current_path_points = []
    current_level_data = None # Ensure it's cleared

def start_level(level_json):
    global game_state
    load_level(level_json)
    game_state = GAME_STATE_PLAYING

# --- UI Elements (for menus) ---
class Button:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.color = (100, 150, 200) # Button color
        self.hover_color = (120, 170, 220)
        self.text_color = WHITE
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2) # Border

        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            self.action()
            return True
        return False

# --- Game State Functions ---

def main_menu():
    global game_state

    # Buttons
    play_button = Button(
        SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50,
        "Start Game", lambda: start_level(level_1_data)
    )
    quit_button = Button(
        SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 70, 200, 50,
        "Quit", sys.exit
    )
    menu_buttons = [play_button, quit_button]

    while game_state == GAME_STATE_MENU:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            for button in menu_buttons:
                button.handle_event(event)

        screen.fill(OCEAN_COLOR)
        title_surf = large_font.render(SCREEN_TITLE, True, WHITE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(title_surf, title_rect)

        for button in menu_buttons:
            button.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

def game_over_screen():
    global game_state

    retry_button = Button(
        SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50,
        "Retry Level", lambda: start_level(level_1_data)
    )
    menu_button = Button(
        SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 70, 200, 50,
        "Main Menu", reset_game
    )
    game_over_buttons = [retry_button, menu_button]

    while game_state == GAME_STATE_GAME_OVER:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            for button in game_over_buttons:
                button.handle_event(event)

        screen.fill(BLACK)
        game_over_surf = large_font.render("GAME OVER", True, (255, 0, 0))
        game_over_rect = game_over_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(game_over_surf, game_over_rect)

        # Display score and stats
        final_score_surf = font.render(f"Final Score: {score}", True, WHITE)
        final_score_rect = final_score_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        screen.blit(final_score_surf, final_score_rect)
        turtles_lost_surf = font.render(f"Turtles Lost: {turtles_lost_current_level}", True, WHITE)
        turtles_lost_rect = turtles_lost_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        screen.blit(turtles_lost_surf, turtles_lost_rect)


        for button in game_over_buttons:
            button.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

def level_complete_screen():
    global game_state

    next_level_button = Button(
        SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50,
        "Next Level (Not Implemented)", lambda: reset_game() # For now, return to menu, later load next level
    )
    menu_button = Button(
        SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 70, 200, 50,
        "Main Menu", reset_game
    )
    level_complete_buttons = [next_level_button, menu_button]

    while game_state == GAME_STATE_LEVEL_COMPLETE:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            for button in level_complete_buttons:
                button.handle_event(event)

        screen.fill(SAND_COLOR)
        complete_surf = large_font.render("LEVEL COMPLETE!", True, SEAWEED_COLOR)
        complete_rect = complete_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(complete_surf, complete_rect)

        # Display score and stats
        final_score_surf = font.render(f"Final Score: {score}", True, BLACK)
        final_score_rect = final_score_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        screen.blit(final_score_surf, final_score_rect)
        turtles_saved_surf = font.render(f"Turtles Saved: {turtles_saved_current_level}/{current_level_data.initial_turtle_count}", True, BLACK)
        turtles_saved_rect = turtles_saved_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        screen.blit(turtles_saved_surf, turtles_saved_rect)


        for button in level_complete_buttons:
            button.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

# --- Level 1 Data (JSON provided in problem description) ---
level_1_data = {
  "level_number": 1,
  "name": "Sandy Shores: First Hatchlings",
  "description": "Welcome, Ranger! Guide your first group of baby turtles from their nest to the safety of the ocean. Learn to draw paths, clear small obstacles, and distract a hungry seagull.",
  "size": {
    "width": 800,
    "height": 600
  },
  "spawn_points": [
    {
      "x": 100,
      "y": 500,
      "type": "turtle_nest",
      "initial_turtles": 5
    },
    {
      "x": 700,
      "y": 100,
      "type": "ocean_exit"
    }
  ],
  "obstacles": [
    {
      "x": 250,
      "y": 400,
      "width": 40,
      "height": 40,
      "type": "fallen_coconut",
      "clearable": True
    },
    {
      "x": 450,
      "y": 250,
      "width": 60,
      "height": 30,
      "type": "seaweed_clump",
      "clearable": True
    },
    {
      "x": 300,
      "y": 200,
      "width": 80,
      "height": 80,
      "type": "rock_formation",
      "clearable": False
    }
  ],
  "powerups": [
    {
      "x": 350,
      "y": 350,
      "type": "turtle_speed_boost",
      "duration": 5.0,
      "description": "Temporarily increases turtle movement speed."
    }
  ],
  "enemies": [
    {
      "x": 400,
      "y": 180,
      "type": "seagull",
      "speed": 1.5,
      "aggro_range": 70,
      "cooldown_distraction": 3.0,
      "patrol_path": [
        [
          400,
          180
        ],
        [
          480,
          220
        ],
        [
          400,
          260
        ],
        [
          320,
          220
        ]
      ]
    }
  ],
  "objectives": [
    {
      "type": "reach_destination",
      "target_entity_type": "turtle",
      "count": 3,
      "destination_tag": "ocean_exit",
      "fail_on_less": True,
      "description": "Guide at least 3 turtles to the ocean."
    }
  ],
  "difficulty": "easy",
  "time_limit": 90
}


# --- Main Game Loop ---
def main():
    global game_state, drawing_path, current_path_points, last_clear_time, last_distract_time
    global ability_clear_uses, ability_distract_uses

    # Main game loop
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0 # Time since last frame in seconds

        if game_state == GAME_STATE_MENU:
            main_menu()
        elif game_state == GAME_STATE_PLAYING:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left click
                        mouse_pos = event.pos
                        current_time = pygame.time.get_ticks() / 1000.0

                        # Check for obstacle clearing
                        cleared_obstacle = False
                        if current_time - last_clear_time >= CLEAR_COOLDOWN:
                            for ob in current_level_data.obstacles:
                                if ob.clearable and not ob.cleared and ob.rect.collidepoint(mouse_pos):
                                    ob.clear()
                                    ability_clear_uses += 1
                                    last_clear_time = current_time
                                    cleared_obstacle = True
                                    print("Obstacle cleared!")
                                    break
                        
                        # Check for predator distraction
                        distracted_predator = False
                        if not cleared_obstacle and current_time - last_distract_time >= DISTRACT_COOLDOWN:
                            for predator in current_level_data.predators:
                                # Check if click is near the predator (e.g., within double its width)
                                if pygame.Vector2(predator.rect.center).distance_to(mouse_pos) <= predator.rect.width * 2:
                                    predator.distract(predator.distraction_cooldown)
                                    ability_distract_uses += 1
                                    last_distract_time = current_time
                                    distracted_predator = True
                                    print("Predator distracted!")
                                    break

                        # Start path drawing if no other interaction happened
                        if not cleared_obstacle and not distracted_predator:
                            drawing_path = True
                            current_path_points = [mouse_pos]
                elif event.type == pygame.MOUSEMOTION:
                    if drawing_path:
                        last_point = pygame.Vector2(current_path_points[-1])
                        current_point = pygame.Vector2(event.pos)
                        if last_point.distance_squared_to(current_point) > PATH_SEGMENT_LENGTH_SQ:
                            current_path_points.append(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and drawing_path:
                        drawing_path = False
                        if len(current_path_points) > 1:
                            # Assign path to all alive, not-saved turtles.
                            # The game concept says "a group of turtles", so apply to all currently unguided.
                            for turtle in current_level_data.turtles:
                                if turtle.alive and not turtle.saved:
                                    turtle.set_path(current_path_points)
                        current_path_points = [] # Clear temporary path

            # Update game logic
            if current_level_data:
                current_level_data.update(dt)

            # Drawing
            if current_level_data:
                current_level_data.draw(screen)

            pygame.display.flip()

        elif game_state == GAME_STATE_GAME_OVER:
            game_over_screen()
        elif game_state == GAME_STATE_LEVEL_COMPLETE:
            level_complete_screen()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
