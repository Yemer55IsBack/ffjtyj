import pygame
import random
import math
import sys

# =============================================================================
# GLOBAL CONFIGURATION & CONSTANTS
# =============================================================================
# We define these globally to allow for easy balancing of game difficulty 
# and UI scaling without digging through the logic classes.
WIDTH, HEIGHT = 900, 700
FPS = 60
PLAYER_SPEED = 6
INITIAL_ASTEROID_COUNT = 8
COLOR_BG = (10, 10, 25)      # Deep Space Blue
COLOR_PLAYER = (0, 255, 200) # Cyan Neon
COLOR_ASTEROID = (255, 50, 100) # Pink Neon
COLOR_TEXT = (255, 255, 255)

# =============================================================================
# CLASS DEFINITIONS
# =============================================================================

class Player(pygame.sprite.Sprite):
    """
    The Player class inherits from pygame.sprite.Sprite.
    Using Sprites allows us to use Group-based collision detection, 
    which is much more efficient than manual list iteration.
    """
    def __init__(self):
        super().__init__()
        # Surface creation: We create a transparent surface for the player
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        # Draw a triangle to represent a spaceship using polygon coordinates
        pygame.draw.polygon(self.image, COLOR_PLAYER, [(20, 0), (0, 40), (40, 40)])
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 100))
        
        # We use a secondary 'mask' for pixel-perfect collision.
        # Standard 'rect' collision is boxy; 'mask' follows the actual shape.
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        """
        Handle movement logic per frame. 
        We check the keyboard state directly for responsive control.
        """
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.left > 0:
            self.rect.x -= PLAYER_SPEED
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.right < WIDTH:
            self.rect.x += PLAYER_SPEED
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.rect.top > 0:
            self.rect.y -= PLAYER_SPEED
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.rect.bottom < HEIGHT:
            self.rect.y += PLAYER_SPEED

class Asteroid(pygame.sprite.Sprite):
    """
    Enemy objects that spawn at the top and move downward at varying speeds.
    """
    def __init__(self):
        super().__init__()
        # Varying size for visual diversity and difficulty
        size = random.randint(30, 70)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        # Draw a circle representing an asteroid
        pygame.draw.circle(self.image, COLOR_ASTEROID, (size // 2, size // 2), size // 2, 2)
        
        # Position initialization: Randomly across the X-axis, slightly off-screen on Y
        self.rect = self.image.get_rect(
            center=(random.randint(0, WIDTH), random.randint(-150, -50))
        )
        
        # Physics variables
        self.speed_y = random.uniform(3.0, 7.0)
        self.speed_x = random.uniform(-1.5, 1.5) # Slight diagonal drift
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        """
        Move the asteroid and reset it if it leaves the screen.
        Resetting is more performance-friendly than deleting and instantiating 
        new objects (Object Pooling concept).
        """
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x

        # If asteroid passes the bottom, recycle it to the top
        if self.rect.top > HEIGHT:
            self.rect.y = random.randint(-100, -40)
            self.rect.x = random.randint(0, WIDTH)
            self.speed_y = random.uniform(3.0, 7.0)

# =============================================================================
# GAME ENGINE CLASS
# =============================================================================

class GameEngine:
    """
    The Orchestrator. This class manages the initialization, the main loop,
    state transitions, and rendering. Optimized for local IDE execution.
    """
    def __init__(self):
        # Ensure pygame is fully initialized
        pygame.init()
        
        # Explicitly set the display mode. Using DOUBLEBUF for smoother rendering in Visual Studio.
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
        pygame.display.set_caption("Neon Asteroid Dodger")
        
        self.clock = pygame.time.Clock()
        
        # Robust font loading: Fallback to system default if Arial is missing
        try:
            self.font = pygame.font.SysFont("Arial", 28, bold=True)
        except:
            self.font = pygame.font.Font(None, 36)
            
        self.running = True
        self.game_active = True
        self.score = 0
        
        # Sprite Groups
        self.all_sprites = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        
        self.setup_game()

    def setup_game(self):
        """Initializes game entities for a new session."""
        self.player = Player()
        self.all_sprites.add(self.player)
        
        for _ in range(INITIAL_ASTEROID_COUNT):
            a = Asteroid()
            self.asteroids.add(a)
            self.all_sprites.add(a)

    def display_ui(self):
        """Renders the HUD (Heads-Up Display)."""
        score_surf = self.font.render(f"SCORE: {int(self.score)}", True, COLOR_TEXT)
        self.screen.blit(score_surf, (20, 20))

    def show_game_over(self):
        """Overlay displayed when the player crashes."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)) # Semi-transparent black
        self.screen.blit(overlay, (0, 0))
        
        msg = self.font.render("GAME OVER - Press R to Restart or Q to Quit", True, (255, 255, 255))
        msg_rect = msg.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.screen.blit(msg, msg_rect)

    def run(self):
        """The Heart of the Engine: The Main Game Loop."""
        # Initial fill to ensure the Visual Studio window doesn't appear "stuck" on start
        self.screen.fill(COLOR_BG)
        pygame.display.flip()

        while self.running:
            # 1. EVENT PROCESSING
            # It is crucial to process all events in the queue to prevent the 
            # "Not Responding" error in Windows/Visual Studio.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.KEYDOWN:
                    if not self.game_active:
                        if event.key == pygame.K_r: # Restart logic
                            self.score = 0
                            self.game_active = True
                            self.all_sprites.empty()
                            self.asteroids.empty()
                            self.setup_game()
                        if event.key == pygame.K_q: # Quit
                            self.running = False

            if self.game_active:
                # 2. STATE UPDATES
                self.all_sprites.update()
                
                # Increment score based on survival time
                self.score += 0.1
                
                # Difficulty scaling: Increase asteroid count as score grows
                if int(self.score) > 0 and int(self.score) % 100 == 0:
                    if len(self.asteroids) < 30: 
                        new_a = Asteroid()
                        self.asteroids.add(new_a)
                        self.all_sprites.add(new_a)

                # 3. COLLISION DETECTION
                # We use the collide_mask for pixel-perfect accuracy against the neon ship
                if pygame.sprite.spritecollide(self.player, self.asteroids, False, pygame.sprite.collide_mask):
                    self.game_active = False

            # 4. RENDERING
            self.screen.fill(COLOR_BG)
            self.all_sprites.draw(self.screen)
            self.display_ui()
            
            if not self.game_active:
                self.show_game_over()

            # Refresh the display hardware
            pygame.display.flip()
            
            # Maintain a steady framerate (Standard 60 FPS)
            self.clock.tick(FPS)

        # Cleanup: Ensure the window closes properly in Visual Studio
        pygame.quit()
        sys.exit()

# =============================================================================
# ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    try:
        game = GameEngine()
        game.run()
    except Exception as e:
        # Catching and printing errors helps debugging in the VS Output console
        print(f"Game Engine Error: {e}")
        pygame.quit()
        sys.exit()