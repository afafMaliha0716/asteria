import pygame

# --- Constants & Initialization (Assumed from A) ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
FPS = 60
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# --- Player Class for Top-Down Movement ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([50, 50])
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed = 5

    def update(self):
        # Get all currently pressed keys
        keys = pygame.key.get_pressed()
        
        # Initialize movement delta
        dx, dy = 0, 0

        # Calculate movement based on keys
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = self.speed

        # Update position
        self.rect.x += dx
        self.rect.y += dy
        
        # Keep player within screen bounds (simple boundary checking)
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)

# --- Game Setup ---
all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

# --- Main Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 1. Update (The player's position is updated here)
    all_sprites.update()

    # 2. Drawing
    screen.fill(WHITE)
    all_sprites.draw(screen)
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
