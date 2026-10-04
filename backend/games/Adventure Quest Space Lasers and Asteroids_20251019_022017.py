
import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Generated Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.score = 0
        
        # Player
        self.player = pygame.Rect(50, 50, 30, 30)
        self.player_speed = 5
        
        # Collectibles
        self.coins = []
        for _ in range(5):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            self.coins.append(pygame.Rect(x, y, 20, 20))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
    
    def update(self):
        keys = pygame.key.get_pressed()
        
        # Player movement
        if keys[pygame.K_LEFT] and self.player.x > 0:
            self.player.x -= self.player_speed
        if keys[pygame.K_RIGHT] and self.player.x < SCREEN_WIDTH - self.player.width:
            self.player.x += self.player_speed
        if keys[pygame.K_UP] and self.player.y > 0:
            self.player.y -= self.player_speed
        if keys[pygame.K_DOWN] and self.player.y < SCREEN_HEIGHT - self.player.height:
            self.player.y += self.player_speed
        
        # Check coin collection
        for coin in self.coins[:]:
            if self.player.colliderect(coin):
                self.coins.remove(coin)
                self.score += 10
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw player
        pygame.draw.rect(self.screen, BLUE, self.player)
        
        # Draw coins
        for coin in self.coins:
            pygame.draw.rect(self.screen, YELLOW, coin)
        
        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
