import pygame
import random
import json
import os

# Constants
BOARD_SIZE = 20
CELL_SIZE = 30
SCREEN_SIZE = BOARD_SIZE * CELL_SIZE
APPLE_COLOR = (255, 0, 0)  # Red
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
DIRECTIONS = {
    pygame.K_UP: UP,
    pygame.K_DOWN: DOWN,
    pygame.K_LEFT: LEFT,
    pygame.K_RIGHT: RIGHT
}

# Define 12 colors for the snake, including green as default
SNAKE_COLORS = [
    (0, 255, 0),     # Green (default)
    (0, 0, 255),     # Blue
    (255, 255, 0),   # Yellow
    (255, 165, 0),   # Orange
    (128, 0, 128),   # Purple
    (0, 255, 255),   # Cyan
    (255, 192, 203), # Pink
    (165, 42, 42),   # Brown
    (255, 215, 0),   # Gold
    (0, 128, 128),   # Teal
    (255, 105, 180), # Hot Pink
    (64, 224, 208)   # Turquoise
]

# Milestones at every 10 apples up to 100, plus a milestone at 25
MILESTONES = [10, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100]

# Initialize variables
unlocked_colors = []
snake_color = SNAKE_COLORS[0]  # Default color (green)
milestones_reached = []
current_game_milestones = []
total_apples = 0
total_deaths = 0

def draw_block(screen, color, position):
    pygame.draw.rect(
        screen,
        color,
        pygame.Rect(
            position[0] * CELL_SIZE,
            position[1] * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )
    )

def draw_grid(screen):
    for x in range(0, SCREEN_SIZE, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, SCREEN_SIZE))
    for y in range(0, SCREEN_SIZE, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (SCREEN_SIZE, y))

def display_message(screen, message, color, size=30, y_offset=0):
    font = pygame.font.SysFont(None, size)
    text = font.render(message, True, color)
    text_rect = text.get_rect(
        center=(SCREEN_SIZE // 2, SCREEN_SIZE // 2 + y_offset)
    )
    screen.blit(text, text_rect)

def load_data():
    global unlocked_colors, snake_color, milestones_reached, total_apples, total_deaths
    if os.path.exists('data.json'):
        with open('data.json', 'r') as f:
            data = json.load(f)
            unlocked_colors = [tuple(color) for color in data.get('unlocked_colors', [])]
            snake_color = tuple(data.get('snake_color', SNAKE_COLORS[0]))
            milestones_reached = data.get('milestones_reached', [])
            total_apples = data.get('total_apples', 0)
            total_deaths = data.get('total_deaths', 0)
    else:
        unlocked_colors = [SNAKE_COLORS[0]]  # Start with green unlocked
        snake_color = SNAKE_COLORS[0]
        milestones_reached = []
        total_apples = 0
        total_deaths = 0

def save_data():
    data = {
        'unlocked_colors': [list(color) for color in unlocked_colors],
        'snake_color': list(snake_color),
        'milestones_reached': milestones_reached,
        'total_apples': total_apples,
        'total_deaths': total_deaths
    }
    with open('data.json', 'w') as f:
        json.dump(data, f)

def mode_selection_screen(screen):
    global snake_color
    while True:
        screen.fill(BACKGROUND_COLOR)
        font = pygame.font.SysFont(None, 55)
        easy_text = font.render('Easy Mode (Press E)', True, GAME_OVER_COLOR)
        easy_rect = easy_text.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 2 - 120))
        
        medium_text = font.render('Medium Mode (Press M)', True, GAME_OVER_COLOR)
        medium_rect = medium_text.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 2 - 70))
        
        color_text = font.render('Choose Snake Color (Press C)', True, GAME_OVER_COLOR)
        color_rect = color_text.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 2 - 20))
        
        stats_text = font.render('Statistics (Press S)', True, GAME_OVER_COLOR)
        stats_rect = stats_text.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 2 + 30))
        
        quit_text = font.render('Quit (Press Q)', True, GAME_OVER_COLOR)
        quit_rect = quit_text.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE // 2 + 80))
        
        screen.blit(easy_text, easy_rect)
        screen.blit(medium_text, medium_rect)
        screen.blit(color_text, color_rect)
        screen.blit(stats_text, stats_rect)
        screen.blit(quit_text, quit_rect)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    return 'easy'
                elif event.key == pygame.K_m:
                    return 'medium'
                elif event.key == pygame.K_c:
                    choose_color_menu(screen)
                elif event.key == pygame.K_s:
                    statistics_screen(screen)
                elif event.key == pygame.K_q:
                    pygame.quit()
                    return None

def statistics_screen(screen):
    running = True
    while running:
        screen.fill(BACKGROUND_COLOR)
        font_title = pygame.font.SysFont(None, 48)
        font = pygame.font.SysFont(None, 28)
        title_text = font_title.render('Statistics', True, GAME_OVER_COLOR)
        title_rect = title_text.get_rect(center=(SCREEN_SIZE // 2, 50))
        screen.blit(title_text, title_rect)
        
        # Prepare milestones text
        milestones_str = ", ".join(map(str, MILESTONES))
        milestones_lines = []
        max_line_width = SCREEN_SIZE - 40  # Margin of 20 pixels on each side
        words = milestones_str.split(', ')
        line = 'Milestones for new colors: '
        for word in words:
            test_line = f"{line}{word}, "
            if font.size(test_line)[0] < max_line_width:
                line = test_line
            else:
                milestones_lines.append(line.rstrip(', '))
                line = f"{word}, "
        milestones_lines.append(line.rstrip(', '))
        
        # Display milestones
        y = 120
        for line in milestones_lines:
            line_text = font.render(line, True, GAME_OVER_COLOR)
            line_rect = line_text.get_rect(center=(SCREEN_SIZE // 2, y))
            screen.blit(line_text, line_rect)
            y += 30  # Adjust spacing between lines
        
        # Display total deaths and apples collected
        y += 10  # Extra spacing before next section
        deaths_text = font.render(f'Total Deaths: {total_deaths}', True, GAME_OVER_COLOR)
        deaths_rect = deaths_text.get_rect(center=(SCREEN_SIZE // 2, y))
        screen.blit(deaths_text, deaths_rect)
        
        y += 30
        apples_text = font.render(f'Total Apples Collected: {total_apples}', True, GAME_OVER_COLOR)
        apples_rect = apples_text.get_rect(center=(SCREEN_SIZE // 2, y))
        screen.blit(apples_text, apples_rect)
        
        instructions_text = font.render('Press any key to return', True, GAME_OVER_COLOR)
        instructions_rect = instructions_text.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE - 50))
        screen.blit(instructions_text, instructions_rect)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                running = False

def choose_color_menu(screen):
    global snake_color
    while True:
        screen.fill(BACKGROUND_COLOR)
        font = pygame.font.SysFont(None, 36)
        title_text = font.render('Choose Your Snake Color', True, GAME_OVER_COLOR)
        title_rect = title_text.get_rect(center=(SCREEN_SIZE // 2, 50))
        screen.blit(title_text, title_rect)
        
        # Display unlocked colors
        for idx, color in enumerate(unlocked_colors):
            x = 50 + (idx % 5) * 100
            y = 100 + (idx // 5) * 100
            color_rect = pygame.Rect(x, y, 80, 80)
            pygame.draw.rect(screen, color, color_rect)
            if idx < 9:
                label = str(idx + 1)
            else:
                label = chr(ord('A') + idx - 9)
            number_text = font.render(label, True, GAME_OVER_COLOR)
            number_rect = number_text.get_rect(center=color_rect.center)
            screen.blit(number_text, number_rect)
        
        instructions_text = font.render('Press key to select color or ESC to go back', True, GAME_OVER_COLOR)
        instructions_rect = instructions_text.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE - 50))
        screen.blit(instructions_text, instructions_rect)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return  # Exit the color menu
                choice = None
                if pygame.K_1 <= event.key <= pygame.K_9:
                    choice = event.key - pygame.K_1
                elif pygame.K_a <= event.key <= pygame.K_z:
                    choice = event.key - pygame.K_a + 9
                if choice is not None and 0 <= choice < len(unlocked_colors):
                    snake_color = unlocked_colors[choice]
                    save_data()
                    return

def game_over_screen(screen):
    global total_deaths
    total_deaths += 1
    save_data()
    while True:
        screen.fill(BACKGROUND_COLOR)
        font = pygame.font.SysFont(None, 30)
        display_message(screen, 'Uh oh, can\'t eat yourself', GAME_OVER_COLOR, y_offset=-60)
        display_message(screen, 'Press R to Retry, M for Main Menu,', GAME_OVER_COLOR, y_offset=-20)
        display_message(screen, 'C to Choose Color, or Q to Quit', GAME_OVER_COLOR, y_offset=20)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return 'quit'
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return 'retry'
                elif event.key == pygame.K_m:
                    return 'menu'
                elif event.key == pygame.K_c:
                    choose_color_menu(screen)
                elif event.key == pygame.K_q:
                    pygame.quit()
                    return 'quit'

def check_milestones():
    if (apple_count in MILESTONES and
        apple_count not in milestones_reached and
        apple_count not in current_game_milestones):
        current_game_milestones.append(apple_count)

def handle_new_milestones():
    global unlocked_colors, milestones_reached
    new_milestones = [m for m in current_game_milestones if m not in milestones_reached]
    if new_milestones:
        for milestone in new_milestones:
            milestones_reached.append(milestone)
            choose_new_color(screen)
        save_data()

def choose_new_color(screen):
    global unlocked_colors
    available_colors = [color for color in SNAKE_COLORS if color not in unlocked_colors]
    if not available_colors:
        return  # All colors unlocked
    
    while True:
        screen.fill(BACKGROUND_COLOR)
        font = pygame.font.SysFont(None, 36)
        title_text = font.render('Choose a new Snake Color', True, GAME_OVER_COLOR)
        title_rect = title_text.get_rect(center=(SCREEN_SIZE // 2, 50))
        screen.blit(title_text, title_rect)
        
        # Display available colors
        for idx, color in enumerate(available_colors):
            x = 50 + (idx % 5) * 100
            y = 100 + (idx // 5) * 100
            color_rect = pygame.Rect(x, y, 80, 80)
            pygame.draw.rect(screen, color, color_rect)
            if idx < 9:
                label = str(idx + 1)
            else:
                label = chr(ord('A') + idx - 9)
            number_text = font.render(label, True, GAME_OVER_COLOR)
            number_rect = number_text.get_rect(center=color_rect.center)
            screen.blit(number_text, number_rect)
        
        instructions_text = font.render('Press key to select color', True, GAME_OVER_COLOR)
        instructions_rect = instructions_text.get_rect(center=(SCREEN_SIZE // 2, SCREEN_SIZE - 50))
        screen.blit(instructions_text, instructions_rect)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                choice = None
                if pygame.K_1 <= event.key <= pygame.K_9:
                    choice = event.key - pygame.K_1
                elif pygame.K_a <= event.key <= pygame.K_z:
                    choice = event.key - pygame.K_a + 9
                if choice is not None and 0 <= choice < len(available_colors):
                    selected_color = available_colors[choice]
                    unlocked_colors.append(selected_color)
                    save_data()
                    return

def reset_game():
    global snake, direction, apple, apple_count, current_game_milestones
    snake = [(10, 10), (9, 10), (8, 10)]
    direction = INITIAL_DIRECTION
    apple = (
        random.randint(0, BOARD_SIZE - 1),
        random.randint(0, BOARD_SIZE - 1)
    )
    apple_count = 0
    current_game_milestones = []

def main():
    global snake, direction, apple, apple_count, screen, total_apples  # Ensure global access
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
    pygame.display.set_caption("Snake Game")
    clock = pygame.time.Clock()
    
    load_data()  # Load unlocked colors and selected snake color
    
    while True:
        mode = mode_selection_screen(screen)
        if mode is None:
            break
        
        reset_game()
        running = True
        
        while running:
            new_direction = direction
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key in DIRECTIONS:
                        if (DIRECTIONS[event.key][0] + direction[0] != 0) or (
                            DIRECTIONS[event.key][1] + direction[1] != 0
                        ):
                            new_direction = DIRECTIONS[event.key]
            
            head_x, head_y = snake[0]
            move_x, move_y = new_direction
            new_head = (
                (head_x + move_x) % BOARD_SIZE,
                (head_y + move_y) % BOARD_SIZE
            )
            snake = [new_head] + snake[:-1]
            
            if new_head in snake[1:]:
                # Handle new milestones before game over
                handle_new_milestones()
                result = game_over_screen(screen)
                if result == 'quit':
                    pygame.quit()
                    return
                elif result == 'retry':
                    reset_game()
                    continue
                elif result == 'menu':
                    break  # Exit the inner while loop to return to the main menu
            
            if new_head == apple:
                snake.append(snake[-1])
                apple = (
                    random.randint(0, BOARD_SIZE - 1),
                    random.randint(0, BOARD_SIZE - 1)
                )
                apple_count += 1
                total_apples += 1
                check_milestones()
                save_data()
            
            screen.fill(BACKGROUND_COLOR)
            
            if mode == 'easy':
                draw_grid(screen)
            
            for segment in snake:
                draw_block(screen, snake_color, segment)
            draw_block(screen, APPLE_COLOR, apple)
            
            font = pygame.font.SysFont(None, 36)
            text = font.render(f'Apples Eaten: {apple_count}', True, (255, 255, 255))
            screen.blit(text, (10, 10))
            
            pygame.display.flip()
            clock.tick(10)
            
            direction = new_direction

if __name__ == "__main__":
    main()
