import pygame

# --- Constants & Initialization (Assumed from A) ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
FPS = 60
BLACK = (0, 0, 0)
RED = (255, 0, 0)
FLOOR_Y = SCREEN_HEIGHT - 50 # Y position of the "ground"

# --- Platformer Player Class ---
class Player(pygame.sprite.Sprite):
    GRAVITY = 1
    JUMP_STRENGTH = -20
    
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([40, 60])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 4
        self.rect.y = FLOOR_Y - self.rect.height
        
        # Movement state
        self.speed = 8
        self.vertical_velocity = 0
        self.on_ground = False

    def handle_input(self):
        # Get all currently pressed keys
        keys = pygame.key.get_pressed()
        
        # Horizontal movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
            
        # Jump handling (only if on the ground)
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.on_ground:
            self.vertical_velocity = self.JUMP_STRENGTH
            self.on_ground = False # Cannot jump again mid-air

    def apply_gravity(self):
        # Apply gravity to vertical velocity
        self.vertical_velocity += self.GRAVITY
        
        # Clamp max fall speed to prevent clipping through thin platforms
        self.vertical_velocity = min(self.vertical_velocity, 20)
        
        # Apply vertical velocity to position
        self.rect.y += self.vertical_velocity

    def check_floor_collision(self):
        # Simple collision check with a fixed floor height
        if self.rect.bottom >= FLOOR_Y:
            self.rect.bottom = FLOOR_Y
            self.vertical_velocity = 0 # Stop falling
            self.on_ground = True # Landed

    def update(self):
        self.handle_input()
        self.apply_gravity()
        self.check_floor_collision()
        
        # Keep player within screen bounds horizontally
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)


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

    # 1. Update
    all_sprites.update()

    # 2. Drawing
    screen.fill(BLACK)
    
    # Draw the floor for context
    pygame.draw.line(screen, (100, 100, 100), (0, FLOOR_Y), (SCREEN_WIDTH, FLOOR_Y), 5)
    
    all_sprites.draw(screen)
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
