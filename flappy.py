import pygame, random, time
from pygame.locals import *
import sys

# VARIABLES
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 20
GRAVITY = 2.5
GAME_SPEED = 15

GROUND_WIDTH = 2 * SCREEN_WIDTH
GROUND_HEIGHT = 100

PIPE_WIDTH = 80
PIPE_HEIGHT = 500

PIPE_GAP = 150

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

        # Load and scale the bird images (enlarged by 20%)
        self.images = [pygame.transform.scale(pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha(),
                                              (int(34 * 1.2), int(24 * 1.2))),
                       pygame.transform.scale(pygame.image.load('assets/sprites/bluebird-midflap.png').convert_alpha(),
                                              (int(34 * 1.2), int(24 * 1.2))),
                       pygame.transform.scale(pygame.image.load('assets/sprites/bluebird-downflap.png').convert_alpha(),
                                              (int(34 * 1.2), int(24 * 1.2)))]

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

        # UPDATE HEIGHT
        self.rect[1] += self.speed

    def bump(self):
        self.speed = -SPEED

    def begin(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]


class Pipe(pygame.sprite.Sprite):

    def __init__(self, inverted, xpos, ysize):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load('assets/sprites/pipe-green.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PIPE_WIDTH, PIPE_HEIGHT))

        self.rect = self.image.get_rect()
        self.rect[0] = xpos

        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect[1] = - (self.rect[3] - ysize)
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
    size = random.randint(100, 300)
    pipe = Pipe(False, xpos, size)
    pipe_inverted = Pipe(True, xpos, SCREEN_HEIGHT - size - PIPE_GAP)
    return pipe, pipe_inverted


def display_score(score, screen, font):
    score_surface = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_surface, (10, 10))


def game_over_popup(screen, score, font):
    # Game Over text (wrapped into two lines)
    game_over_surface1 = font.render("Game Over!", True, (255, 255, 255))
    game_over_surface2 = font.render(f"Your Score: {score}", True, (255, 255, 255))

    # Restart text (wrapped)
    restart_surface = font.render("Press 'R' to Respawn", True, (255, 255, 255))

    # Get the rectangle of the text for centering
    game_over_rect1 = game_over_surface1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    game_over_rect2 = game_over_surface2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10))
    restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))

    # Blit (draw) the surfaces to the screen
    screen.blit(game_over_surface1, game_over_rect1)
    screen.blit(game_over_surface2, game_over_rect2)
    screen.blit(restart_surface, restart_rect)

def game_loop():
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

    # Initialize score
    score = 0
    font = pygame.font.SysFont(None, 40)

    running = True

    while running:
        clock.tick(15)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_SPACE or event.key == K_UP:
                    bird.bump()
                    wing_sound.play()  # Play wing sound when space or up is pressed

        screen.blit(BACKGROUND, (0, 0))

        # Update pipe and score
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

            # Increment score for each pipe passed
            score += 1

            # Play point sound when a point is earned
            point_sound.play()

        bird_group.update()
        ground_group.update()
        pipe_group.update()

        bird_group.draw(screen)
        pipe_group.draw(screen)
        ground_group.draw(screen)

        # Display score
        display_score(score, screen, font)

        pygame.display.update()

        # Check for collisions
        if (pygame.sprite.groupcollide(bird_group, ground_group, False, False, pygame.sprite.collide_mask) or
                pygame.sprite.groupcollide(bird_group, pipe_group, False, False, pygame.sprite.collide_mask)):
            hit_sound.play()  # Play hit sound when bird hits the ground or pipe
            time.sleep(1)

            # Game Over Popup
            game_over_popup(screen, score, font)
            pygame.display.update()

            # Wait for player to respawn or quit
            while True:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == KEYDOWN:
                        if event.key == K_r:  # Respawn if 'R' is pressed
                            return game_loop()  # Restart game loop
                time.sleep(0.1)



pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird')

BACKGROUND = pygame.image.load('assets/sprites/background-day.png')
BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))

game_loop()
