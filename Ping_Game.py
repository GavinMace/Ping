import pygame
import random
import subprocess
import sys

# Initialize pygame
pygame.init()

# Fullscreen
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Ping - Select Difficulty")

# Fonts
FONT = pygame.font.Font(None, 50)
BIG_FONT = pygame.font.Font(None, 80)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GRAY = (180, 180, 180)

# Pause button rect
PAUSE_BTN_RECT = pygame.Rect(WIDTH - 70, 20, 50, 50)

# Difficulty settings
DIFFICULTIES = {
    "Easy": {"ball_speed": [3, 3], "paddle_speed": 1.7, "bot_accuracy": 1.0},
    "Medium": {"ball_speed": [3, 3], "paddle_speed": 2, "bot_accuracy": 1.0},
    "Hard": {"ball_speed": [3, 3], "paddle_speed": 2.5, "bot_accuracy": 1.0},
    "IMPOSSIBLE": {"ball_speed": [3, 3], "paddle_speed": 3, "bot_accuracy": 1.0}
}

# Pause menu
def pause_menu():
    paused = True
    options = ["Resume", "Restart (Difficulty)", "Quit"]
    option_rects = []
    while paused:
        screen.fill(BLACK)

        pause_text = BIG_FONT.render("PAUSED", True, WHITE)
        screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, 100))

        option_rects.clear()
        for i, opt in enumerate(options):
            text = FONT.render(opt, True, BLUE)
            rect = text.get_rect(center=(WIDTH // 2, 250 + i * 100))
            option_rects.append((rect, opt))
            screen.blit(text, rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for rect, opt in option_rects:
                    if rect.collidepoint(event.pos):
                        if opt == "Resume":
                            paused = False
                        elif opt == "Restart (Difficulty)":
                            difficulty_menu()
                        elif opt == "Quit":
                            subprocess.Popen([sys.executable, 'Ping_Launcher.py'])
                            pygame.quit()
                            sys.exit()

# Draw difficulty menu
def draw_menu(selected_idx, options):
    screen.fill(BLACK)
    title = BIG_FONT.render("Select Difficulty", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

    button_rects = []
    for i, option in enumerate(options):
        color = BLUE if i == selected_idx else WHITE
        text = FONT.render(option, True, color)
        rect = text.get_rect(center=(WIDTH // 2, 250 + i * 100))
        button_rects.append((rect, option))
        screen.blit(text, rect)

    back_text = FONT.render("Back to Launcher", True, RED)
    back_rect = back_text.get_rect(center=(WIDTH // 2, HEIGHT - 100))
    screen.blit(back_text, back_rect)

    pygame.display.flip()
    return button_rects, back_rect

# Difficulty menu
def difficulty_menu():
    options = list(DIFFICULTIES.keys())
    selected = 0
    while True:
        button_rects, back_rect = draw_menu(selected, options)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    run_game(options[selected])
                elif event.key == pygame.K_BACKSPACE:
                    subprocess.Popen([sys.executable, 'Ping_Launcher.py'])
                    pygame.quit()
                    sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                for rect, opt in button_rects:
                    if rect.collidepoint(event.pos):
                        run_game(opt)
                if back_rect.collidepoint(event.pos):
                    subprocess.Popen([sys.executable, 'Ping_Launcher.py'])
                    pygame.quit()
                    sys.exit()

# Main Game
def run_game(difficulty):
    pygame.display.set_caption(f"Pong - {difficulty}")
    settings = DIFFICULTIES[difficulty]
    ball_speed = settings["ball_speed"].copy()
    paddle_speed = settings["paddle_speed"]
    bot_accuracy = settings["bot_accuracy"]

    # Objects
    left_paddle = pygame.Rect(40, HEIGHT//2 - 70, 20, 140)
    right_paddle = pygame.Rect(WIDTH - 40, HEIGHT//2 - 70, 20, 140)
    ball = pygame.Rect(WIDTH//2, HEIGHT//2, 20, 20)

    left_score, right_score = 0, 0
    clock = pygame.time.Clock()

    running = True
    while running:
        clock.tick(60)
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pause_menu()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PAUSE_BTN_RECT.collidepoint(event.pos):
                    pause_menu()

        # Player input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and left_paddle.top > 0:
            left_paddle.y -= 6
        if keys[pygame.K_s] and left_paddle.bottom < HEIGHT:
            left_paddle.y += 6

        # Bot movement
        if right_paddle.centery < ball.centery and right_paddle.bottom < HEIGHT:
            right_paddle.y += paddle_speed
        elif right_paddle.centery > ball.centery and right_paddle.top > 0:
            right_paddle.y -= paddle_speed

        # Ball movement
        ball.x += ball_speed[0]
        ball.y += ball_speed[1]

        # Ball collision
        if ball.top <= 0 or ball.bottom >= HEIGHT:
            ball_speed[1] = -ball_speed[1]
        if ball.colliderect(left_paddle) or ball.colliderect(right_paddle):
            ball_speed[0] = -ball_speed[0]

        # Score
        if ball.left <= 0:
            right_score += 1
            ball.center = (WIDTH//2, HEIGHT//2)
        if ball.right >= WIDTH:
            left_score += 1
            ball.center = (WIDTH//2, HEIGHT//2)

        # Drawing
        pygame.draw.rect(screen, BLUE, left_paddle)
        pygame.draw.rect(screen, RED, right_paddle)
        pygame.draw.ellipse(screen, WHITE, ball)
        pygame.draw.aaline(screen, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT))

        # Scores
        left_text = FONT.render(str(left_score), True, WHITE)
        right_text = FONT.render(str(right_score), True, WHITE)
        screen.blit(left_text, (WIDTH//4, 20))
        screen.blit(right_text, (WIDTH*3//4, 20))

        # Draw pause button
        pygame.draw.rect(screen, GRAY, PAUSE_BTN_RECT, border_radius=8)
        pause_icon = FONT.render("II", True, BLACK)
        icon_rect = pause_icon.get_rect(center=PAUSE_BTN_RECT.center)
        screen.blit(pause_icon, icon_rect)

        pygame.display.flip()

# Start the game
difficulty_menu()
