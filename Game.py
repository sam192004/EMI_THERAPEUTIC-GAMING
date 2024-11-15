import pygame
import random
import sys
import tkinter as tk

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

# Colors
LIGHT_BLUE = (173, 216, 230)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Paddle attributes
PADDLE_WIDTH = 230
PADDLE_HEIGHT = 200
PADDLE_SPEED = 3
ACTIVE_PADDLE_WIDTH = 100  # Reduced size for active mode

# Ball attributes
BALL_SIZE = 90
NORMAL_BALL_SPEED = 5
ACTIVE_BALL_SPEED = 10  # Slightly increased speed for active mode
SUPER_BALL_SPEED = 7

# Bomb attributes
BOMB_SIZE = 100
BOMB_SPEED = 20

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Paddle Game")

# Load images
background_img = pygame.image.load(r'ADD IMAGE')
paddle_img = pygame.image.load(r'ADD IMAGE')
ball_img = pygame.image.load(r'ADD IMAGE')
bomb_img = pygame.image.load(r'ADD IMAGE')

# Fonts
title_font = pygame.font.Font(None, 48)
text_font = pygame.font.Font(None, 24)

# Auto-play variables
auto_play = True
hit_counts = [7, 3, 5, 2]  # Hit sequence
current_play = 0
current_hits = 0
target_hits = hit_counts[0]

# Paddle class
class Paddle(pygame.sprite.Sprite):
    def __init__(self, x, y, width):
        super().__init__()
        self.image = pygame.transform.scale(paddle_img, (width, PADDLE_HEIGHT))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y

    def update(self, ball=None):
        global auto_play, current_hits, target_hits, current_play
        if auto_play:
            # Move paddle only when the ball is close
            if ball and abs(ball.rect.centery - self.rect.centery) < 100:
                if ball.rect.centerx < self.rect.centerx:
                    self.rect.x -= PADDLE_SPEED
                elif ball.rect.centerx > self.rect.centerx:
                    self.rect.x += PADDLE_SPEED
        else:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.rect.x -= PADDLE_SPEED
            if keys[pygame.K_RIGHT]:
                self.rect.x += PADDLE_SPEED
        # Keep paddle within the screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

# Ball class
class Ball(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.transform.scale(ball_img, (BALL_SIZE, BALL_SIZE))
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speedx = random.choice([-speed, speed])
        self.speedy = -speed

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        # Check if ball hits the walls
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.speedx = -self.speedx
        if self.rect.top <= 0:
            self.speedy = -self.speedy

# Bomb class
class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(bomb_img, (BOMB_SIZE, BOMB_SIZE))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speedy = BOMB_SPEED

    def update(self):
        self.rect.y += self.speedy
        # Remove bomb if it falls off the screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Button class
class Button:
    def __init__(self, text, x, y, width, height, color, font_color, callback):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.font_color = font_color
        self.callback = callback
        self.font = pygame.font.Font(None, 36)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surf = self.font.render(self.text, True, self.font_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Main function to run the game
def main(mode):
    global player_paddle, computer_paddle, balls, bombs, running, paused, replay_button, exit_button, game_over, score, auto_play, current_hits, target_hits, current_play

    paddle_width = ACTIVE_PADDLE_WIDTH if mode == "active" else PADDLE_WIDTH
    player_paddle = Paddle(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20, paddle_width)

    balls = pygame.sprite.Group()
    bombs = pygame.sprite.Group()

    if mode == "normal":
        ball = Ball(NORMAL_BALL_SPEED)
        balls.add(ball)
    elif mode == "active":
        ball = Ball(ACTIVE_BALL_SPEED)
        balls.add(ball)
    elif mode == "super":
        ball = Ball(SUPER_BALL_SPEED)
        balls.add(ball)
        computer_paddle = Paddle(SCREEN_WIDTH // 2, 20 + PADDLE_HEIGHT, PADDLE_WIDTH)

    clock = pygame.time.Clock()
    pause_button = Button("Pause", 650, 50, 100, 50, BLUE, WHITE, pause_game)
    resume_button = Button("Resume", 650, 120, 100, 50, GREEN, WHITE, resume_game)
    replay_button = Button("Replay", 300, 200, 200, 100, BLUE, WHITE, replay_game)
    exit_button = Button("Exit", 300, 350, 200, 100, RED, WHITE, quit_game)

    running = True
    paused = False
    game_over = False
    score = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pause_button.is_clicked(event.pos):
                    pause_game()
                if resume_button.is_clicked(event.pos):
                    resume_game()
                if game_over:
                    if replay_button.is_clicked(event.pos):
                        replay_game()
                    if exit_button.is_clicked(event.pos):
                        quit_game()

        if not paused and not game_over:
            if mode == "super":
                # Update computer paddle position based on the ball
                if balls:
                    ball = balls.sprites()[0]
                    if ball.rect.centerx < computer_paddle.rect.centerx:
                        computer_paddle.rect.centerx -= PADDLE_SPEED
                    elif ball.rect.centerx > computer_paddle.rect.centerx:
                        computer_paddle.rect.centerx += PADDLE_SPEED

            # Check if the balls hit the paddles
            for ball in balls:
                if pygame.sprite.spritecollideany(ball, [player_paddle]):
                    ball.speedy = -ball.speedy
                    score += 1

            if pygame.sprite.spritecollideany(ball, [computer_paddle]):
                ball.speedy = -ball.speedy
                score += 1

            # Update sprites
            player_paddle.update(ball)
            balls.update()
            bombs.update()

            screen.fill(LIGHT_BLUE)
            screen.blit(background_img, (0, 0))

            player_paddle.draw(screen)
            computer_paddle.draw(screen)

            balls.draw(screen)
            bombs.draw(screen)

            if game_over:
                replay_button.draw(screen)
                exit_button.draw(screen)

            pygame.display.update()
            clock.tick(60)

# Start game with mode selection
def start_game():
    mode = mode_var.get()
    create_mode_selection_window()
    main(mode)

# Create the mode selection window
def create_mode_selection_window():
    global mode_var, root
    root = tk.Tk()
    root.title("Cosmic Paddle")
    root.geometry("500x500")
    
    mode_var = tk.StringVar(value="normal")

    title_label = tk.Label(root, text="Select Game Mode", font=("Arial", 18))
    title_label.pack(pady=10)

    normal_mode_radio = tk.Radiobutton(root, text="Normal Mode", variable=mode_var, value="normal")
    normal_mode_radio.pack(anchor=tk.W, padx=20, pady=5)

    active_mode_radio = tk.Radiobutton(root, text="Active Mode", variable=mode_var, value="active")
    active_mode_radio.pack(anchor=tk.W, padx=20, pady=5)

    super_mode_radio = tk.Radiobutton(root, text="Super Mode", variable=mode_var, value="super")
    super_mode_radio.pack(anchor=tk.W, padx=20, pady=5)

    start_button = tk.Button(root, text="Start", width=10, command=start_game)
    start_button.pack(pady=10)

    quit_button = tk.Button(root, text="Quit", width=10, command=quit_game)
    quit_button.pack(pady=5)

    root.mainloop()

# Quit the game
def quit_game():
    pygame.quit()
    sys.exit()

# Pause the game
def pause_game():
    global paused
    paused = True

# Resume the game
def resume_game():
    global paused
    paused = False

# Replay the game
def replay_game():
    global score, current_hits, target_hits, current_play
    score = 0
    current_hits = 0
    target_hits = hit_counts[0]
    main(mode_var.get())

# Run the mode selection window
create_mode_selection_window()
