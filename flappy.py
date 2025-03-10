import pygame, random, time
from pygame.locals import *
import sys
import os

# Initialize pygame
pygame.init()

# Get the screen resolution
screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w  # Fullscreen width
SCREEN_HEIGHT = screen_info.current_h  # Fullscreen height

# VARIABLES
SPEED = 20
GRAVITY = 2.5
GAME_SPEED = 15

GROUND_WIDTH = 2 * SCREEN_WIDTH
GROUND_HEIGHT = 100

PIPE_WIDTH = 150
PIPE_HEIGHT = SCREEN_HEIGHT  # This should fill the screen height for better gameplay experience
PIPE_GAP = 400

BIRD_WIDTH = 34  # Default width of the bird
BIRD_HEIGHT = 24  # Default height of the bird
BIRD_SCALE = 2.5  # Scaling factor for the bird (optional for adjusting size)

wing = 'assets/audio/wing.wav'
hit = 'assets/audio/hit.wav'
point = 'assets/audio/point.wav'

pygame.mixer.init()
wing_sound = pygame.mixer.Sound(wing)
hit_sound = pygame.mixer.Sound(hit)
point_sound = pygame.mixer.Sound(point)

class Bird(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # Scale the bird images using the width and height variables
        self.images = [pygame.transform.scale(pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha(),
                                              (int(BIRD_WIDTH * BIRD_SCALE), int(BIRD_HEIGHT * BIRD_SCALE))),
                       pygame.transform.scale(pygame.image.load('assets/sprites/bluebird-midflap.png').convert_alpha(),
                                              (int(BIRD_WIDTH * BIRD_SCALE), int(BIRD_HEIGHT * BIRD_SCALE))),
                       pygame.transform.scale(pygame.image.load('assets/sprites/bluebird-downflap.png').convert_alpha(),
                                              (int(BIRD_WIDTH * BIRD_SCALE), int(BIRD_HEIGHT * BIRD_SCALE)))]
        self.speed = SPEED
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
        self.image = pygame.image.load('assets/sprites/base.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (GROUND_WIDTH, GROUND_HEIGHT))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.rect[1] = SCREEN_HEIGHT - GROUND_HEIGHT

    def update(self):
        self.rect[0] -= GAME_SPEED


def is_off_screen(sprite):
    return sprite.rect[0] < -(sprite.rect[2])


def get_random_pipes(xpos):
    size = random.randint(100, SCREEN_HEIGHT - PIPE_GAP - 100)
    pipe = Pipe(False, xpos, size)
    pipe_inverted = Pipe(True, xpos, SCREEN_HEIGHT - size - PIPE_GAP)
    return pipe, pipe_inverted


def display_score(score, screen, font):
    score_surface = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_surface, (10, 10))


def game_over_popup(screen, score, font):
    game_over_surface1 = font.render("Game Over!", True, (255, 255, 255))
    game_over_surface2 = font.render(f"Your Score: {score}", True, (255, 255, 255))

    # Draw the game over message
    game_over_rect1 = game_over_surface1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    game_over_rect2 = game_over_surface2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10))

    screen.blit(game_over_surface1, game_over_rect1)
    screen.blit(game_over_surface2, game_over_rect2)

    # Add the "Press Any Key to Exit" message
    exit_message = font.render("Press Any Key to Exit", True, (255, 255, 255))
    exit_message_rect = exit_message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
    screen.blit(exit_message, exit_message_rect)

    pygame.display.update()

    # Wait for a key press and then quit
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                pygame.quit()
                sys.exit()


def show_start_screen(screen, font):
    start_surface = font.render("Press Any Key to Start", True, (255, 255, 255))
    start_rect = start_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(BACKGROUND, (0, 0))
    screen.blit(start_surface, start_rect)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                waiting = False


def display_timer(start_time, screen, font):
    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000  # Convert to seconds
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    timer_surface = font.render(f"Time: {minutes:02}:{seconds:02}", True, (255, 255, 255))
    screen.blit(timer_surface, (SCREEN_WIDTH - 150, 10))  # Adjust position


def game_loop(first_launch=False):
    global GAME_SPEED
    font = pygame.font.SysFont(None, 40)
    if first_launch:
        show_start_screen(screen, font)

    bird_group = pygame.sprite.Group()
    bird = Bird()
    bird_group.add(bird)

    ground_group = pygame.sprite.Group()
    for i in range(2):
        ground = Ground(GROUND_WIDTH * i)
        ground_group.add(ground)

    pipe_group = pygame.sprite.Group()
    for i in range(2):
        pipes = get_random_pipes(SCREEN_WIDTH * i + 800)
        pipe_group.add(pipes[0])
        pipe_group.add(pipes[1])

    clock = pygame.time.Clock()
    score = 0
    running = True
    start_time = pygame.time.get_ticks()

    last_update_time = time.time()

    while running:
        clock.tick(15)

        # Track if the program has frozen for 3 seconds
        if time.time() - last_update_time > 2:
            print("Program froze for more than 3 seconds. Exiting...")
            pygame.quit()
            sys.exit()

        last_update_time = time.time()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_SPACE or event.key == K_UP:
                    bird.bump()
                    wing_sound.play()

                # Handle Alt + F4 (Alt key + F4 key press)
                if event.key == K_F4 and pygame.key.get_pressed()[K_LALT] or pygame.key.get_pressed()[K_RALT]:
                    pygame.quit()
                    sys.exit()

        screen.blit(BACKGROUND, (0, 0))

        if is_off_screen(ground_group.sprites()[0]):
            ground_group.remove(ground_group.sprites()[0])
            new_ground = Ground(GROUND_WIDTH - 20)
            ground_group.add(new_ground)

        if is_off_screen(pipe_group.sprites()[0]):
            pipe_group.remove(pipe_group.sprites()[0])
            pipe_group.remove(pipe_group.sprites()[0])
            pipes = get_random_pipes(SCREEN_WIDTH * 2)
            pipe_group.add(pipes[0])
            pipe_group.add(pipes[1])
            score += 1
            if score % 1 == 0:
                GAME_SPEED = GAME_SPEED + 1.5
            print(GAME_SPEED)
            point_sound.play()

        bird_group.update()
        ground_group.update()
        pipe_group.update()

        bird_group.draw(screen)
        pipe_group.draw(screen)
        ground_group.draw(screen)

        display_score(score, screen, font)
        display_timer(start_time, screen, font)

        pygame.display.update()

        if (pygame.sprite.groupcollide(bird_group, ground_group, False, False, pygame.sprite.collide_mask) or
                pygame.sprite.groupcollide(bird_group, pipe_group, False, False, pygame.sprite.collide_mask)):
            hit_sound.play()
            time.sleep(1)
            game_over_popup(screen, score, font)
            pygame.display.update()
            while True:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == KEYDOWN:
                        pygame.quit()
                        sys.exit()


# Set the display mode to fullscreen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption('Flappy Bird')

BACKGROUND = pygame.image.load('assets/sprites/background-day.png')
BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))

game_loop(first_launch=True)