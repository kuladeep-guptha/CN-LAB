import pygame
import random

# Initialize Pygame
pygame.init()

# Define constants
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("4-Player Car Race")

# Define colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Define player class
class Player:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.x = random.randint(50, WIDTH - 50)
        self.y = HEIGHT - 50
        self.speed = 5

    def move_left(self):
        self.x -= self.speed

    def move_right(self):
        self.x += self.speed

    def draw(self):
        pygame.draw.rect(SCREEN, self.color, (self.x, self.y, 50, 50))

# Initialize players list
players = []

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Check for player input
    keys = pygame.key.get_pressed()
    for player in players:
        if keys[pygame.K_LEFT]:
            player.move_left()
        if keys[pygame.K_RIGHT]:
            player.move_right()

    # Update screen
    SCREEN.fill(WHITE)
    for player in players:
        player.draw()

    # Check for race completion (for simplicity, you can define your own finish line)
    if players and players[0].y <= 0:
        winner = players[0].name
        print(f"{winner} wins!")
        running = False

    pygame.display.update()

# Quit Pygame
pygame.quit()
