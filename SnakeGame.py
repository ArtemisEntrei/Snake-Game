import pygame
import random

# Constants
BOARD_SIZE = 20
CELL_SIZE = 30
SCREEN_SIZE = BOARD_SIZE * CELL_SIZE
APPLE_COLOR = (255, 0, 0)  # Red
SNAKE_COLOR = (0, 255, 0)  # Green
BACKGROUND_COLOR = (0, 0, 0)  # Black
GAME_OVER_COLOR = (255, 255, 255)  # White
GRID_COLOR = (200, 200, 200)  # Light grey
SNAKE_START_LENGTH = 3
INITIAL_DIRECTION = (1, 0)  # Moving right initially

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = {pygame.K_UP: UP, pygame.K_DOWN: DOWN, pygame.K_LEFT: LEFT, pygame.K_RIGHT: RIGHT}

def draw_block(screen, color, position):
    pygame.draw.rect(screen, color, pygame.Rect(position[0] * CELL_SIZE, position[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_grid(screen):
    for x in range(0, SCREEN_SIZE, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, SCREEN_SIZE))
    for y in range(0, SCREEN_SIZE, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (SCREEN_SIZE, y))

def display_message(screen, message, color, size=30):
    font = pygame.font.SysFont(None, size)
    text = font.render(message, True, color)
    text_rect = text.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 2))
    screen.fill(BACKGROUND_COLOR)
    screen.blit(text, text_rect)
    pygame.display.flip()

def mode_selection_screen(screen):
    font = pygame.font.SysFont(None, 55)
    screen.fill(BACKGROUND_COLOR)
    
    easy_text = font.render('Easy Mode (Press E)', True, GAME_OVER_COLOR)
    easy_rect = easy_text.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 2 - 50))
    
    medium_text = font.render('Medium Mode (Press M)', True, GAME_OVER_COLOR)
    medium_rect = medium_text.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 2 + 50))
    
    quit_text = font.render('Quit (Press Q)', True, GAME_OVER_COLOR)
    quit_rect = quit_text.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 2 + 150))
    
    screen.blit(easy_text, easy_rect)
    screen.blit(medium_text, medium_rect)
    screen.blit(quit_text, quit_rect)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    return 'easy'
                elif event.key == pygame.K_m:
                    return 'medium'
                elif event.key == pygame.K_q:
                    pygame.quit()
                    return None

def game_over_screen(screen):
    font = pygame.font.SysFont(None, 30)  # Smaller font size
    screen.fill(BACKGROUND_COLOR)
    
    message_text = font.render('Uh oh, can\'t eat yourself', True, GAME_OVER_COLOR)
    message_rect = message_text.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 2 - 30))
    
    options_text = font.render('Press R to Retry, M for Main Menu, or Q to Quit', True, GAME_OVER_COLOR)
    options_rect = options_text.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 2 + 30))
    
    screen.blit(message_text, message_rect)
    screen.blit(options_text, options_rect)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return 'quit'
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return 'retry'
                elif event.key == pygame.K_m:
                    return 'menu'
                elif event.key == pygame.K_q:
                    pygame.quit()
                    return 'quit'

def reset_game():
    global snake, direction, apple, apple_count
    snake = [(10, 10), (9, 10), (8, 10)]
    direction = INITIAL_DIRECTION
    apple = (random.randint(0, BOARD_SIZE - 1), random.randint(0, BOARD_SIZE - 1))
    apple_count = 0

def main():
    global snake, direction, apple, apple_count  # Ensure global access
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
    pygame.display.set_caption("Snake Game")
    clock = pygame.time.Clock()

    while True:
        mode = mode_selection_screen(screen)
        if mode is None:
            break

        reset_game()
        running = True

        while running:
            new_direction = direction
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    elif event.type == pygame.KEYDOWN:
                        if event.key in DIRECTIONS:
                            if (DIRECTIONS[event.key][0] + direction[0] != 0) or (DIRECTIONS[event.key][1] + direction[1] != 0):
                                new_direction = DIRECTIONS[event.key]

                head_x, head_y = snake[0]
                move_x, move_y = new_direction
                new_head = ((head_x + move_x) % BOARD_SIZE, (head_y + move_y) % BOARD_SIZE)
                snake = [new_head] + snake[:-1]

                if new_head in snake[1:]:
                    result = game_over_screen(screen)
                    if result == 'quit':
                        pygame.quit()
                        return
                    elif result == 'retry':
                        reset_game()
                        break
                    elif result == 'menu':
                        running = False  # Exit the inner while loop to return to the main menu
                        break

                if new_head == apple:
                    snake.append(snake[-1])
                    apple = (random.randint(0, BOARD_SIZE - 1), random.randint(0, BOARD_SIZE - 1))
                    apple_count += 1

                screen.fill(BACKGROUND_COLOR)

                if mode == 'easy':
                    draw_grid(screen)

                for segment in snake:
                    draw_block(screen, SNAKE_COLOR, segment)
                draw_block(screen, APPLE_COLOR, apple)

                font = pygame.font.SysFont(None, 36)
                text = font.render(f'Apples Eaten: {apple_count}', True, (255, 255, 255))
                screen.blit(text, (10, 10))

                pygame.display.flip()
                clock.tick(10)

                direction = new_direction

if __name__ == "__main__":
    main()
