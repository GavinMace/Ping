import pygame
import random

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_RADIUS = 20
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
FONT = pygame.font.Font(None, 50)
MENU_FONT = pygame.font.Font(None, 60)

# Difficulty settings
DIFFICULTIES = {
    "Easy": {
        "ball_speed": [4, 4],
        "paddle_speed": 6,
        "bot_accuracy": 0.4
    },
    "Medium": {
        "ball_speed": [6, 6],
        "paddle_speed": 10,
        "bot_accuracy": 0.7
    },
    "Hard": {
        "ball_speed": [8, 8],
        "paddle_speed": 14,
        "bot_accuracy": 1.0
    }
}

# Create game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

def draw_menu(selected_idx, options):
    screen.fill(BLACK)
    title = MENU_FONT.render("Select Difficulty", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

    for i, option in enumerate(options):
        color = BLUE if i == selected_idx else WHITE
        text = FONT.render(option, True, color)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 200 + i * 60))

    pygame.display.flip()

def difficulty_menu():
    options = list(DIFFICULTIES.keys())
    selected = 0
    while True:
        draw_menu(selected, options)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    return options[selected]

# --- Main Game ---
def run_game(difficulty):
    settings = DIFFICULTIES[difficulty]
    ball_speed = settings["ball_speed"].copy()
    PADDLE_SPEED = settings["paddle_speed"]
    bot_accuracy = settings["bot_accuracy"]

    # Paddle positions
    left_paddle = pygame.Rect(20, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = pygame.Rect(WIDTH - 30, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(WIDTH // 2, HEIGHT // 2, BALL_RADIUS, BALL_RADIUS)

    # Scores
    left_score = 0
    right_score = 0

    running = True
    while running:
        pygame.time.delay(30)
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Human paddle
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and left_paddle.top > 0:
            left_paddle.y -= PADDLE_SPEED
        if keys[pygame.K_s] and left_paddle.bottom < HEIGHT:
            left_paddle.y += PADDLE_SPEED

        # Bot paddle
        target_y = ball.centery
        if random.random() < bot_accuracy:
            if right_paddle.centery < target_y and right_paddle.bottom < HEIGHT:
                right_paddle.y += PADDLE_SPEED
            elif right_paddle.centery > target_y and right_paddle.top > 0:
                right_paddle.y -= PADDLE_SPEED

        # Move ball
        ball.x += ball_speed[0]
        ball.y += ball_speed[1]

        # Ball collisions
        if ball.top <= 0 or ball.bottom >= HEIGHT:
            ball_speed[1] = -ball_speed[1]
        if ball.colliderect(left_paddle) or ball.colliderect(right_paddle):
            ball_speed[0] = -ball_speed[0]

        # Scoring
        if ball.left <= 0:
            right_score += 1
            ball.x, ball.y = WIDTH // 2, HEIGHT // 2
            ball_speed = settings["ball_speed"].copy()
        if ball.right >= WIDTH:
            left_score += 1
            ball.x, ball.y = WIDTH // 2, HEIGHT // 2
            ball_speed = settings["ball_speed"].copy()

        # Draw
        pygame.draw.rect(screen, BLUE, left_paddle)
        pygame.draw.rect(screen, RED, right_paddle)
        pygame.draw.ellipse(screen, WHITE, ball)
        pygame.draw.aaline(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))

        # Scores
        left_text = FONT.render(str(left_score), True, WHITE)
        right_text = FONT.render(str(right_score), True, WHITE)
        screen.blit(left_text, (WIDTH // 4, 20))
        screen.blit(right_text, (WIDTH * 3 // 4, 20))

        pygame.display.flip()

    pygame.quit()

# Run everything
chosen_difficulty = difficulty_menu()
pygame.display.set_caption(f"Pong - {chosen_difficulty} Mode")
run_game(chosen_difficulty)
