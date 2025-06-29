import pygame, random, time
from pygame.locals import *
import sys
import os
import logging
from datetime import datetime

# Create "logs" folder if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')
if not os.path.exists('logs/game'):
    os.makedirs('logs/game')

# Create a log file with timestamp
timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
log_filename = f"logs/game/{timestamp}.txt"

# Set up logging to file
logging.basicConfig(
    filename=log_filename,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

# Redirect stdout and stderr to log file
sys.stdout = open(log_filename, 'a')
sys.stderr = open(log_filename, 'a')

# Log the initial startup message
logging.info("Game started")

# Initialize pygame
pygame.init()

# Get the screen resolution
screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h

# VARIABLES
SPEED = 10
GRAVITY = 0.4
GAME_SPEED = 10
FRAME_RATE = 60

GROUND_WIDTH = 2 * SCREEN_WIDTH
GROUND_HEIGHT = 100

PIPE_WIDTH = 150
PIPE_HEIGHT = SCREEN_HEIGHT

BIRD_WIDTH = 34
BIRD_HEIGHT = 24
BIRD_SCALE = 2

# Load sounds
wing = 'assets/audio/wing.wav'
hit = 'assets/audio/hit.wav'
point = 'assets/audio/point.wav'

pygame.mixer.init()
wing_sound = pygame.mixer.Sound(wing)
hit_sound = pygame.mixer.Sound(hit)
point_sound = pygame.mixer.Sound(point)

# Set display mode (start in windowed mode)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption('Flappy Bird')

# Load images (scaled once)
BACKGROUND = pygame.image.load('assets/sprites/background-day.png').convert()
BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))
GROUND_IMAGE = pygame.image.load('assets/sprites/base.png').convert()
GROUND_IMAGE = pygame.transform.scale(GROUND_IMAGE, (GROUND_WIDTH, GROUND_HEIGHT))

is_fullscreen = False


def toggle_fullscreen():
    global is_fullscreen, screen
    if is_fullscreen:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    else:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    is_fullscreen = not is_fullscreen


class Bird(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.images = [pygame.transform.scale(pygame.image.load(f'assets/sprites/bluebird-{flap}.png').convert_alpha(),
                                              (int(BIRD_WIDTH * BIRD_SCALE), int(BIRD_HEIGHT * BIRD_SCALE)))
                       for flap in ['upflap', 'midflap', 'downflap']]
        self.speed = 0
        self.current_image = 0
        self.image = self.images[self.current_image]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect[0] = SCREEN_WIDTH / 6
        self.rect[1] = SCREEN_HEIGHT / 2

    def update(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]
        self.speed += GRAVITY
        self.rect[1] += self.speed

    def bump(self):
        self.speed = -SPEED


class Pipe(pygame.sprite.Sprite):
    def __init__(self, inverted, xpos, ysize):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/sprites/pipe-green.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PIPE_WIDTH, PIPE_HEIGHT))
        self.rect = self.image.get_rect()
        self.rect[0] = xpos

        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect[1] = -(self.rect[3] - ysize)
        else:
            self.rect[1] = SCREEN_HEIGHT - ysize
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect[0] -= GAME_SPEED


class Ground(pygame.sprite.Sprite):
    def __init__(self, xpos):
        pygame.sprite.Sprite.__init__(self)
        self.image = GROUND_IMAGE
        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.rect[1] = SCREEN_HEIGHT - GROUND_HEIGHT

    def update(self):
        self.rect[0] -= GAME_SPEED
        if self.rect[0] <= -GROUND_WIDTH:
            self.rect[0] = SCREEN_WIDTH


def get_random_pipes(xpos):
    gap_size = random.randint(200, 400)  # Randomize gap size
    size = random.randint(100, SCREEN_HEIGHT - gap_size - 100)  # Randomize pipe height
    return Pipe(False, xpos, size), Pipe(True, xpos, SCREEN_HEIGHT - size - gap_size)


def display_score(score, screen, font):
    score_surface = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_surface, (10, 10))


def show_start_screen():
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 80)
    text = font.render("Press SPACE to Start", True, (255, 255, 255))
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
    screen.blit(text, text_rect)
    pygame.display.update()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_SPACE:
                waiting = False


def game_over_screen(score):
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 80)
    text = font.render(f"Game Over! Score: {score}", True, (255, 255, 255))
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
    screen.blit(text, text_rect)
    pygame.display.update()
    time.sleep(2)


def game_loop():
    show_start_screen()
    font = pygame.font.SysFont(None, 40)
    bird = Bird()
    bird_group = pygame.sprite.GroupSingle(bird)
    ground_group = pygame.sprite.Group(Ground(0), Ground(GROUND_WIDTH))
    pipe_group = pygame.sprite.Group()

    score = 0
    clock = pygame.time.Clock()
    passed_pipes = set()
    pipe_spawn_delay = 3000
    last_pipe_spawn_time = pygame.time.get_ticks()

    while True:
        clock.tick(FRAME_RATE)
        current_time = pygame.time.get_ticks()

        if current_time - last_pipe_spawn_time > pipe_spawn_delay:
            pipe_group.add(*get_random_pipes(SCREEN_WIDTH))
            last_pipe_spawn_time = current_time

        for pipe in pipe_group:
            if pipe.rect.right < bird.rect.left and pipe not in passed_pipes:
                passed_pipes.add(pipe)
                if len(passed_pipes) % 2 == 0:
                    score += 1
                    point_sound.play()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_SPACE:
                bird.bump()
                wing_sound.play()

        screen.blit(BACKGROUND, (0, 0))
        pipe_group.update()
        pipe_group.draw(screen)
        ground_group.update()
        ground_group.draw(screen)
        bird_group.update()
        bird_group.draw(screen)
        display_score(score, screen, font)
        pygame.display.update()

        if pygame.sprite.spritecollideany(bird, pipe_group) or pygame.sprite.spritecollideany(bird, ground_group):
            hit_sound.play()
            game_over_screen(score)
            return


game_loop()