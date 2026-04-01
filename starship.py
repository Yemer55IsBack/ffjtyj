import pygame
import random
import math

# --- Global Initialization & Engine Setup ---
# Initializes all imported pygame modules. This is required before any other 
# pygame functions can be called to ensure hardware drivers (audio, display) are ready.
pygame.init()

# --- Configuration & Constants ---
# Defined at the top level for easy adjustments to game difficulty and visuals.
SCREEN_WIDTH = 800   # Width of the game window in pixels
SCREEN_HEIGHT = 600  # Height of the game window in pixels
FPS = 60             # Frames Per Second: governs the speed of the game loop

# Color Palette (RGB tuples)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 0)

# --- Game Classes (Object Oriented Design) ---

class Player(pygame.sprite.Sprite):
    """
    The Player class inherits from pygame.sprite.Sprite.
    Using Sprites allows for efficient collision detection and grouping.
    """
    def __init__(self):
        super().__init__()
        # Create a surface with per-pixel alpha for transparency
        self.image = pygame.Surface((50, 40), pygame.SRCALPHA)
        # Draw a custom polygon to represent the ship
        pygame.draw.polygon(self.image, GREEN, [(25, 0), (50, 40), (0, 40)])
        
        # rect handles the object's position and boundaries for collision
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 20
        self.speed = 7

    def update(self):
        """
        Calculates movement based on real-time keyboard polling.
        Includes boundary checking to prevent the ship from leaving the screen.
        """
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

    def shoot(self):
        """Returns a new Bullet instance originating from the ship's nose."""
        return Bullet(self.rect.centerx, self.rect.top)

class Enemy(pygame.sprite.Sprite):
    """
    Autonomous agents that descend from the top.
    Logic includes randomized spawning and variable movement speeds.
    """
    def __init__(self):
        super().__init__()
        width = random.randint(30, 50)
        height = 30
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        # Visual representation: Oval body with a cockpit detail
        pygame.draw.ellipse(self.image, RED, [0, 0, width, height])
        pygame.draw.rect(self.image, WHITE, [width//4, height//3, width//2, 5])
        
        self.rect = self.image.get_rect()
        # Randomized start coordinates above the visible screen area (y < 0)
        self.rect.x = random.randrange(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -50)
        
        # Velocity components for diagonal movement
        self.speed_y = random.randrange(2, 5)
        self.speed_x = random.randrange(-2, 3)

    def update(self):
        """Moves the enemy and resets it if it travels off the bottom edge."""
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        
        if self.rect.top > SCREEN_HEIGHT + 10:
            self.rect.x = random.randrange(0, SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)

class Bullet(pygame.sprite.Sprite):
    """Simple projectile with high vertical velocity."""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((6, 15))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speed = -10 # Negative value moves the bullet UP the screen (decreases Y)

    def update(self):
        self.rect.y += self.speed
        # Garbage collection: remove the sprite if it exits the top boundary
        if self.rect.bottom < 0:
            self.kill()

class Star(pygame.sprite.Sprite):
    """Parallax-style background effect for immersion."""
    def __init__(self):
        super().__init__()
        size = random.randint(1, 3)
        self.image = pygame.Surface((size, size))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH)
        self.rect.y = random.randrange(SCREEN_HEIGHT)
        # Faster stars appear 'closer', creating a depth effect
        self.speed = random.randrange(1, 4)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.y = -10
            self.rect.x = random.randrange(SCREEN_WIDTH)

# --- Main Game Engine Loop ---

def main():
    # Setup display surface and timing clock
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Starship Defender")
    clock = pygame.time.Clock()
    
    # Initialize fonts for UI rendering
    font = pygame.font.SysFont("Arial", 24)
    large_font = pygame.font.SysFont("Arial", 64)

    # Sprite Groups: Used for efficient batch updates, drawing, and collision checking
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    stars = pygame.sprite.Group()

    # Pre-populate background stars
    for _ in range(50):
        star = Star()
        stars.add(star)
        all_sprites.add(star)

    player = Player()
    all_sprites.add(player)

    # Instantiate initial wave of enemies
    for _ in range(8):
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)

    score = 0
    game_over = False
    running = True

    # --- Core Loop ---
    while running:
        # 1. Event Processing: Capture user inputs (mouse, keyboard, window closing)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    bullet = player.shoot()
                    all_sprites.add(bullet)
                    bullets.add(bullet)
                # Restart logic: Recurses into main() to reset all state variables
                if event.key == pygame.K_r and game_over:
                    main()
                    return

        if not game_over:
            # 2. Logic Updates: Movement and Game State
            all_sprites.update()

            # Collision Logic: Bullets hit Enemies
            # groupcollide(GroupA, GroupB, DoKillA, DoKillB) returns a dictionary of collisions
            hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
            for hit in hits:
                score += 10
                # Spawn replacement to maintain constant enemy count
                new_enemy = Enemy()
                all_sprites.add(new_enemy)
                enemies.add(new_enemy)

            # Collision Logic: Enemy hits Player
            # spritecollide returns a list of sprites from 'enemies' hitting 'player'
            if pygame.sprite.spritecollide(player, enemies, False):
                game_over = True

        # 3. Rendering: Draw everything to the hidden buffer, then flip to display
        screen.fill(BLACK) # Clear the screen with a solid color
        all_sprites.draw(screen) # Draw all current sprites in their updated positions

        # UI Rendering: Displaying the score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if game_over:
            # Draw Game Over overlay using centered rectangles for perfect alignment
            msg = large_font.render("GAME OVER", True, RED)
            retry_msg = font.render("Press 'R' to Restart", True, WHITE)
            
            msg_rect = msg.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
            retry_rect = retry_msg.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
            
            screen.blit(msg, msg_rect)
            screen.blit(retry_msg, retry_rect)

        # Refresh the display (Double Buffering)
        pygame.display.flip()
        # Cap the loop at the specified FPS to ensure consistent speed across different PCs
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    # Standard entry point to prevent code from running if the file is imported elsewhere
    main()