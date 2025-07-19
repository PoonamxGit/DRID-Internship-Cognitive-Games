import pygame
import random
import time

# Initialize
pygame.init()
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 4
CELL_SIZE = WIDTH // GRID_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pattern Recall Grid")

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 102, 204)
GREY = (180, 180, 180)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Grid rectangles
grid_rects = [[pygame.Rect(j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
               for j in range(GRID_SIZE)] for i in range(GRID_SIZE)]

# Generate random pattern
def generate_pattern(level):
    return random.sample([(i, j) for i in range(GRID_SIZE) for j in range(GRID_SIZE)], min(level + 2, GRID_SIZE**2))

# Show the pattern to memorize
def show_pattern(cells):
    screen.fill(WHITE)
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            color = BLUE if (i, j) in cells else WHITE
            pygame.draw.rect(screen, color, grid_rects[i][j])
            pygame.draw.rect(screen, BLACK, grid_rects[i][j], 2)
    pygame.display.flip()
    time.sleep(1.5)

# Draw a blank grid
def draw_blank_grid():
    screen.fill(WHITE)
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            pygame.draw.rect(screen, WHITE, grid_rects[i][j])
            pygame.draw.rect(screen, BLACK, grid_rects[i][j], 2)
    pygame.display.flip()

# Show "Correct!" or "Wrong!" message
def show_result(text, color):
    font = pygame.font.SysFont(None, 60)
    screen.fill(WHITE)
    msg = font.render(text, True, color)
    screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - msg.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(1500)

# Display level number
def draw_level(level):
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Level {level}", True, BLACK)
    screen.blit(text, (10, 10))

# Main game function
def main():
    running = True
    level = 1

    while running:
        pattern = generate_pattern(level)
        show_pattern(pattern)
        draw_blank_grid()
        draw_level(level)
        pygame.display.flip()

        selected = []
        input_active = True

        while input_active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    input_active = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    for i in range(GRID_SIZE):
                        for j in range(GRID_SIZE):
                            if grid_rects[i][j].collidepoint(x, y) and (i, j) not in selected:
                                selected.append((i, j))
                                pygame.draw.rect(screen, GREY, grid_rects[i][j])
                                pygame.draw.rect(screen, BLACK, grid_rects[i][j], 2)
                                draw_level(level)
                                pygame.display.flip()

                    # After all selections
                    if len(selected) == len(pattern):
                        if set(selected) == set(pattern):
                            show_result("Correct!", GREEN)
                            level += 1
                        else:
                            show_result("Wrong!", RED)
                            level = 1
                        input_active = False  # ends inner loop, goes to next level

    pygame.quit()

if __name__ == "__main__":
    main()
