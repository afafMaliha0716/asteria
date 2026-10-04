import pygame

# --- Constants & Initialization (Assumed from A) ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
FPS = 60
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# --- Entity Class with Health System ---
class Entity(pygame.sprite.Sprite):
    def __init__(self, color, size, max_hp, position):
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = position
        
        # Health Variables
        self.max_health = max_hp
        self.current_health = max_hp
        self.is_alive = True

    def take_damage(self, amount):
        if not self.is_alive:
            return
        
        self.current_health -= amount
        print(f"Damage taken: {amount}. Current HP: {self.current_health}")
        
        if self.current_health <= 0:
            self.current_health = 0
            self.die()

    def heal(self, amount):
        if not self.is_alive:
            return
            
        self.current_health += amount
        self.current_health = min(self.current_health, self.max_health)
        print(f"Healed: {amount}. Current HP: {self.current_health}")

    def die(self):
        self.is_alive = False
        print("Entity died!")
        self.kill() # Removes the sprite from all groups

    def draw_health_bar(self, surface):
        # Health bar dimensions and position relative to the entity
        BAR_WIDTH = self.rect.width
        BAR_HEIGHT = 5
        BAR_X = self.rect.x
        BAR_Y = self.rect.y - 10 # Position 10 pixels above the entity

        # Calculate health ratio
        health_ratio = self.current_health / self.max_health
        fill_width = int(BAR_WIDTH * health_ratio)

        # Draw background (Red)
        background_rect = pygame.Rect(BAR_X, BAR_Y, BAR_WIDTH, BAR_HEIGHT)
        pygame.draw.rect(surface, RED, background_rect)

        # Draw foreground (Green)
        fill_rect = pygame.Rect(BAR_X, BAR_Y, fill_width, BAR_HEIGHT)
        pygame.draw.rect(surface, GREEN, fill_rect)

    def update(self):
        # Placeholder update logic
        pass

# --- Game Setup ---
all_sprites = pygame.sprite.Group()
player = Entity(BLUE, (60, 60), 100, (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2))
enemy = Entity(RED, (60, 60), 50, (SCREEN_WIDTH * 2 // 3, SCREEN_HEIGHT // 2))

all_sprites.add(player, enemy)

# --- Test Events (Simulating Damage/Heal) ---
def simulate_interaction():
    # Only interact if both are alive
    if player.is_alive and enemy.is_alive:
        # Player takes damage every 60 frames (1 second)
        if pygame.time.get_ticks() % 60 == 0:
            player.take_damage(5)
        
        # Enemy takes damage every 120 frames (2 seconds)
        if pygame.time.get_ticks() % 120 == 0:
            enemy.take_damage(10)

# --- Main Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            # Press 'H' to heal the player
            if event.key == pygame.K_h:
                player.heal(10)

    # 1. Update
    simulate_interaction()
    all_sprites.update()

    # 2. Drawing
    screen.fill(WHITE)
    all_sprites.draw(screen)
    
    # MANDATORY: Draw health bars AFTER drawing sprites
    if player.is_alive:
        player.draw_health_bar(screen)
    if enemy.is_alive:
        enemy.draw_health_bar(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
