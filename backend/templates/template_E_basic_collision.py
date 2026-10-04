import pygame

# --- Constants & Initialization (Assumed from A) ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
FPS = 60
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# --- Player Class with Collision Memory ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([50, 50])
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (100, SCREEN_HEIGHT // 2)
        self.speed = 5
        self.dx = 0 # Delta X for current frame
        self.dy = 0 # Delta Y for current frame

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.dx, self.dy = 0, 0

        if keys[pygame.K_LEFT]:
            self.dx = -self.speed
        if keys[pygame.K_RIGHT]:
            self.dx = self.speed
        if keys[pygame.K_UP]:
            self.dy = -self.speed
        if keys[pygame.K_DOWN]:
            self.dy = self.speed

    def update(self):
        self.handle_input()
        
        # Store old position before movement
        self.old_x = self.rect.x
        self.old_y = self.rect.y
        
        # Apply movement
        self.rect.x += self.dx
        self.rect.y += self.dy

# --- Wall Class (Solid Object) ---
class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# --- Collision Functions ---
def check_and_resolve_collision(sprite, wall_group):
    """
    Checks for collision and resolves it by reverting the sprite's position.
    This demonstrates the basic logic required by the prompt.
    """
    # Check for collision with any wall
    hit_walls = pygame.sprite.spritecollide(sprite, wall_group, False)
    
    if hit_walls:
        print("Collision detected! Reverting position.")
        # Revert movement by setting position back to the previous frame's position
        sprite.rect.x = sprite.old_x
        sprite.rect.y = sprite.old_y
        
        # Note: For more complex/accurate collision, you would check X and Y separately
        # and only revert the axis that caused the collision.

# --- Game Setup ---
all_sprites = pygame.sprite.Group()
walls = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# Create a wall in the center
wall_1 = Wall(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT // 2 - 100, 50, 200)
walls.add(wall_1)
all_sprites.add(wall_1)

# --- Main Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 1. Update
    all_sprites.update()
    
    # 2. Collision Check and Resolution
    check_and_resolve_collision(player, walls)

    # 3. Drawing
    screen.fill(WHITE)
    all_sprites.draw(screen)
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
