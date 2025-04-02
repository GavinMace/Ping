import pygame

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
BALL_SPEED = [5, 5]
PADDLE_SPEED = 10
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_RADIUS = 10
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
FONT = pygame.font.Font(None, 50)

# Create game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

# Paddle positions
left_paddle = pygame.Rect(20, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
right_paddle = pygame.Rect(WIDTH - 30, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(WIDTH // 2, HEIGHT // 2, BALL_RADIUS, BALL_RADIUS)

# Ball speed
ball_speed = BALL_SPEED.copy()

# Scores
left_score = 0
right_score = 0

# Game loop
running = True
while running:
    pygame.time.delay(30)
    screen.fill(BLACK)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Paddle movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and left_paddle.top > 0:
        left_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_s] and left_paddle.bottom < HEIGHT:
        left_paddle.y += PADDLE_SPEED
    if keys[pygame.K_UP] and right_paddle.top > 0:
        right_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_DOWN] and right_paddle.bottom < HEIGHT:
        right_paddle.y += PADDLE_SPEED
    
    # Ball movement
    ball.x += ball_speed[0]
    ball.y += ball_speed[1]
    
    # Ball collisions
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_speed[1] = -ball_speed[1]
    if ball.colliderect(left_paddle) or ball.colliderect(right_paddle):
        ball_speed[0] = -ball_speed[0]
    
    # Reset ball if out of bounds and update score
    if ball.left <= 0:
        right_score += 1
        ball.x, ball.y = WIDTH // 2, HEIGHT // 2
        ball_speed = BALL_SPEED.copy()
    if ball.right >= WIDTH:
        left_score += 1
        ball.x, ball.y = WIDTH // 2, HEIGHT // 2
        ball_speed = BALL_SPEED.copy()
    
    # Draw paddles and ball
    pygame.draw.rect(screen, BLUE, left_paddle)
    pygame.draw.rect(screen, RED, right_paddle)
    pygame.draw.ellipse(screen, WHITE, ball)
    pygame.draw.aaline(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))
    
    # Draw scores
    left_text = FONT.render(str(left_score), True, WHITE)
    right_text = FONT.render(str(right_score), True, WHITE)
    screen.blit(left_text, (WIDTH // 4, 20))
    screen.blit(right_text, (WIDTH * 3 // 4, 20))
    
    pygame.display.flip()

pygame.quit()
