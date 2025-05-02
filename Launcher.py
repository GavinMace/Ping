import pygame
import random
import subprocess
import sys

# Initialize pygame
pygame.init()

# Screen settings
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Ping Launcher")

# Fonts
title_font = pygame.font.SysFont("Arial", 80)
button_font = pygame.font.SysFont("Arial", 40)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (180, 180, 180)

# Raindrop class
class Raindrop:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-HEIGHT, 0)
        self.speed = random.randint(2, 6)

    def fall(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = random.randint(-HEIGHT, 0)
            self.x = random.randint(0, WIDTH)
            self.speed = random.randint(2, 6)

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), 2)

# Create many raindrops
raindrops = [Raindrop() for _ in range(150)]

# Button
start_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 60)

# Main loop
running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if start_button_rect.collidepoint(event.pos):
                # Launch the Ping_Main_Game.py
                subprocess.Popen([sys.executable, 'Ping_Main_Game.py'])
                pygame.quit()
                sys.exit()

    # Update and draw raindrops
    for drop in raindrops:
        drop.fall()
        drop.draw(screen)

    # Draw title
    title_text = title_font.render("PING", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))

    # Draw button
    pygame.draw.rect(screen, GRAY, start_button_rect, border_radius=10)
    start_text = button_font.render("START", True, BLACK)
    screen.blit(start_text, (start_button_rect.centerx - start_text.get_width() // 2,
                             start_button_rect.centery - start_text.get_height() // 2))

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
