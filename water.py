import pygame
import random
import sys

# --- CONFIGURATION AND CONSTANTS ---
# Redefining constants for a marine survival environment.
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Marine Themed Colors
COLOR_OCEAN_DEEP = (0, 10, 50)
COLOR_DIVER = (255, 165, 0)      # Bright Orange for visibility
COLOR_SHARK = (100, 115, 130)    # Slate Blue/Grey
COLOR_OXYGEN = (0, 191, 255)     # Deep Sky Blue
COLOR_TEXT = (240, 240, 240)
COLOR_DANGER = (255, 50, 50)

class Diver(pygame.sprite.Sprite):
    """
    The Diver class handles the player's movement and oxygen consumption.
    The player must move through the water to reach oxygen bubbles while
    avoiding predators.
    """
    def __init__(self):
        super().__init__()
        # Creating a rectangular diver shape with a 'helmet' detail
        self.image = pygame.Surface((40, 25), pygame.SRCALPHA)
        pygame.draw.rect(self.image, COLOR_DIVER, (0, 0, 40, 25), border_radius=8)
        pygame.draw.rect(self.image, (50, 50, 50), (25, 5, 10, 10), border_radius=2) # Visor
        
        self.rect = self.image.get_rect()
        self.rect.center = (100, SCREEN_HEIGHT // 2)
        self.speed = 5
        self.oxygen = 100.0  # Max oxygen

    def update(self):
        """
        Processes movement and constant oxygen depletion.
        Oxygen drops faster if the player moves quickly.
        """
        keys = pygame.key.get_pressed()
        moving = False
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
            moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
            moving = True
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
            moving = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed
            moving = True

        # Natural oxygen decay + extra cost for movement exertion
        decay = 0.05 if not moving else 0.08
        self.oxygen -= decay
        
        # Screen boundary constraints
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

class Shark(pygame.sprite.Sprite):
    """
    Predatory obstacles that move horizontally across the screen.
    Collision with a shark results in immediate game over.
    """
    def __init__(self):
        super().__init__()
        width = random.randint(60, 90)
        height = 30
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        # Simple shark silhouette: body and a fin
        pygame.draw.ellipse(self.image, COLOR_SHARK, (0, 5, width, height - 10))
        pygame.draw.polygon(self.image, COLOR_SHARK, [(width//2, 0), (width//2 + 10, 10), (width//2 - 10, 10)])
        
        self.rect = self.image.get_rect()
        # Spawn from the right side at varying heights and speeds
        self.rect.x = SCREEN_WIDTH + random.randint(50, 300)
        self.rect.y = random.randint(0, SCREEN_HEIGHT - height)
        self.speed = random.randint(3, 7)

    def update(self):
        """Moves the shark left. Re-spawns it on the right to maintain density."""
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.rect.x = SCREEN_WIDTH + random.randint(10, 100)
            self.rect.y = random.randint(0, SCREEN_HEIGHT - 30)

class Bubble(pygame.sprite.Sprite):
    """
    Oxygen pickups that rise from the bottom of the sea.
    Collecting these restores the diver's oxygen level.
    """
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, COLOR_OXYGEN, (10, 10), 8, 2)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - 20)
        self.rect.y = SCREEN_HEIGHT + random.randint(10, 100)
        self.speed_y = random.uniform(1.0, 3.0)

    def update(self):
        """Bubbles float upwards. If they hit the surface, they disappear."""
        self.rect.y -= self.speed_y
        if self.rect.bottom < 0:
            self.kill()

class Game:
    """
    Main controller for 'Deep Sea Diver'.
    Manages survival time, predator spawning, and UI rendering.
    """
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Deep Sea Diver: Survival")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Courier New", 22, bold=True)
        self.reset_game()

    def reset_game(self):
        """
        Initializes or resets the game state to its starting conditions.
        This allows for the 'Restart' functionality without re-initializing Pygame.
        """
        self.running = True
        self.game_over = False
        self.depth_score = 0
        
        # Groups
        self.all_sprites = pygame.sprite.Group()
        self.sharks = pygame.sprite.Group()
        self.bubbles = pygame.sprite.Group()

        self.player = Diver()
        self.all_sprites.add(self.player)

        # Initial shark population
        for _ in range(4):
            s = Shark()
            self.sharks.add(s)
            self.all_sprites.add(s)

    def spawn_logic(self):
        """Periodically creates oxygen bubbles."""
        if random.random() < 0.02: # 2% chance per frame
            b = Bubble()
            self.bubbles.add(b)
            self.all_sprites.add(b)

    def handle_events(self):
        """
        Processes system events. If the game is over, it listens for 
        the 'R' key to trigger a reset.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if self.game_over and event.key == pygame.K_r:
                    self.reset_game()

    def check_collisions(self):
        """
        Handles interaction with pickups and hazards.
        Sets game_over to True if the player fails.
        """
        # Collect Oxygen
        found_air = pygame.sprite.spritecollide(self.player, self.bubbles, True)
        for _ in found_air:
            self.player.oxygen = min(100, self.player.oxygen + 15)
        
        # Hit Predator
        if pygame.sprite.spritecollide(self.player, self.sharks, False):
            self.game_over = True
            
        # Run out of air
        if self.player.oxygen <= 0:
            self.game_over = True

    def draw_ui(self):
        """Renders the oxygen bar and distance score."""
        # Oxygen Bar Shadow
        pygame.draw.rect(self.screen, (50, 50, 50), (20, 20, 200, 20))
        # Oxygen Bar Fill
        bar_color = COLOR_OXYGEN if self.player.oxygen > 25 else COLOR_DANGER
        fill_width = int((max(0, self.player.oxygen) / 100) * 200)
        pygame.draw.rect(self.screen, bar_color, (20, 20, fill_width, 20))
        
        score_text = self.font.render(f"DEPTH: {self.depth_score // 10}m", True, COLOR_TEXT)
        self.screen.blit(score_text, (20, 50))

    def run(self):
        """
        Modified main loop to handle a 'Paused' or 'Game Over' state
        visually while still processing events for the restart key.
        """
        while self.running:
            self.handle_events()
            
            if not self.game_over:
                self.spawn_logic()
                
                # Logic Updates
                self.all_sprites.update()
                self.check_collisions()
                self.depth_score += 1
                
                # Rendering
                self.screen.fill(COLOR_OCEAN_DEEP)
                self.all_sprites.draw(self.screen)
                self.draw_ui()
            else:
                self.show_end_screen()
            
            pygame.display.flip()
            self.clock.tick(FPS)

    def show_end_screen(self):
        """
        Displays the game over message and restart instructions.
        Called every frame once game_over is True.
        """
        # Dim the background slightly for readability
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0,0))

        msg = "OXYGEN DEPLETED" if self.player.oxygen <= 0 else "PREDATOR ATTACK"
        final_text = self.font.render(f"{msg} | Final Depth: {self.depth_score // 10}m", True, COLOR_DANGER)
        restart_text = self.font.render("Press 'R' to Restart or Close to Quit", True, COLOR_TEXT)
        
        rect = final_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        re_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        
        self.screen.blit(final_text, rect)
        self.screen.blit(restart_text, re_rect)

if __name__ == "__main__":
    game = Game()
    game.run()