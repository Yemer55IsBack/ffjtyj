import pygame
import random
import sys

# =============================================================================
# GLOBAL CONFIGURATION
# =============================================================================
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20  # The world is divided into 20x20 pixel tiles
FPS = 12        # Snake games usually feel better at a lower FPS for grid alignment

# Colors - Using a "Cyberpunk" palette
COLOR_BG = (15, 5, 25)
COLOR_SNAKE = (0, 255, 150)   # Emerald Neon
COLOR_FOOD = (255, 0, 150)    # Hot Pink
COLOR_GRID = (30, 20, 50)
COLOR_TEXT = (255, 255, 255)

class Snake:
    """
    Manages the snake's body coordinates, direction, and growth logic.
    """
    def __init__(self):
        # Start in the middle of the screen
        self.body = [(WIDTH // 2, HEIGHT // 2)]
        self.direction = (GRID_SIZE, 0) # Moving Right initially
        self.grow_pending = False

    def move(self):
        """
        Calculates the new head position based on current direction.
        Removed the modulo (%) operator to stop screen wrap-around.
        """
        current_head = self.body[0]
        dx, dy = self.direction
        
        # Simple addition for movement without wrapping
        new_head = (
            current_head[0] + dx,
            current_head[1] + dy
        )

        # Insert the new head at the front of the list
        self.body.insert(0, new_head)

        # If we didn't eat food, remove the tail. If we did, keep it to "grow".
        if not self.grow_pending:
            self.body.pop()
        else:
            self.grow_pending = False

    def check_collision(self):
        """
        Returns True if the head is out of bounds or hits the body.
        """
        head = self.body[0]
        
        # 1. BOUNDARY COLLISION: Check if head is outside the screen dimensions
        if head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT:
            return True
            
        # 2. SELF COLLISION: Check if head coordinate exists in the rest of the body
        return head in self.body[1:]

class Food:
    """Handles random spawning of the 'Data Bit' targets."""
    def __init__(self):
        self.position = (0, 0)
        self.randomize_position()

    def randomize_position(self):
        """Ensures food snaps to the grid."""
        x = random.randint(0, (WIDTH // GRID_SIZE) - 1) * GRID_SIZE
        y = random.randint(0, (HEIGHT // GRID_SIZE) - 1) * GRID_SIZE
        self.position = (x, y)

    def draw(self, surface):
        """Draws a glowing square for the food."""
        rect = pygame.Rect(self.position[0], self.position[1], GRID_SIZE, GRID_SIZE)
        # Inner solid
        pygame.draw.rect(surface, COLOR_FOOD, rect)
        # Outer glow (border)
        pygame.draw.rect(surface, COLOR_TEXT, rect, 1)

class GameEngine:
    """
    The main controller managing the Pygame lifecycle, 
    input processing, and the relationship between Snake and Food.
    """
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Synthwave Snake v1.0")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Courier New", 24, bold=True)
        
        self.reset_game()

    def reset_game(self):
        """Initializes or restarts the game state."""
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.game_over = False

    def draw_grid(self):
        """Subtle grid lines to help the player navigate the 2D space."""
        for x in range(0, WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID, (0, y), (WIDTH, y))

    def handle_input(self):
        """Processes key presses to change snake direction, preventing 180-degree turns."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    continue

                # Logical check: Snake cannot move directly opposite to current direction
                if event.key == pygame.K_UP and self.snake.direction != (0, GRID_SIZE):
                    self.snake.direction = (0, -GRID_SIZE)
                elif event.key == pygame.K_DOWN and self.snake.direction != (0, -GRID_SIZE):
                    self.snake.direction = (0, GRID_SIZE)
                elif event.key == pygame.K_LEFT and self.snake.direction != (GRID_SIZE, 0):
                    self.snake.direction = (-GRID_SIZE, 0)
                elif event.key == pygame.K_RIGHT and self.snake.direction != (-GRID_SIZE, 0):
                    self.snake.direction = (GRID_SIZE, 0)

    def update(self):
        """Updates physics and checks for interactions."""
        if self.game_over:
            return

        self.snake.move()

        # Check if head hit boundary or tail
        if self.snake.check_collision():
            self.game_over = True
            return

        # Check if head reached food
        if self.snake.body[0] == self.food.position:
            self.snake.grow_pending = True
            self.score += 10
            self.food.randomize_position()

    def render(self):
        """Draws all elements to the screen."""
        self.screen.fill(COLOR_BG)
        self.draw_grid()

        # Draw Food
        self.food.draw(self.screen)

        # Draw Snake
        for i, segment in enumerate(self.snake.body):
            # Only draw segments that are within the screen (prevents drawing one frame out-of-bounds)
            if 0 <= segment[0] < WIDTH and 0 <= segment[1] < HEIGHT:
                color = COLOR_SNAKE if i == 0 else (0, 180, 100)
                rect = pygame.Rect(segment[0], segment[1], GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(self.screen, color, rect.inflate(-2, -2), border_radius=4)

        # Draw UI
        score_txt = self.font.render(f"DATA RETRIEVED: {self.score}", True, COLOR_TEXT)
        self.screen.blit(score_txt, (10, 10))

        if self.game_over:
            # Semi-transparent overlay to highlight game over state
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            
            over_surf = self.font.render("SYSTEM CRASHED! PRESS 'R' TO REBOOT", True, COLOR_FOOD)
            over_rect = over_surf.get_rect(center=(WIDTH//2, HEIGHT//2))
            self.screen.blit(over_surf, over_rect)

        pygame.display.flip()

    def run(self):
        """Primary loop."""
        while True:
            self.handle_input()
            self.update()
            self.render()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = GameEngine()
    game.run()