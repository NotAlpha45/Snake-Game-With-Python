import pygame
from pygame import mixer
import random
import os
from math import *

pygame.init()
mixer.init()
pygame.font.init()

WIDTH = 700
HEIGHT = 600
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake game!")
SNAKE_HEAD = pygame.transform.scale(pygame.image.load(os.path.join("snake game asset", "snake head.png")),
                                    (50, 25))

SNAKE_BODY = pygame.transform.scale(pygame.image.load(os.path.join("snake game asset", "snake body.png")), (25, 22))
FOOD = pygame.transform.scale(pygame.image.load(os.path.join("snake game asset", "food.png")), (30, 30))
BLACK = pygame.transform.scale(pygame.image.load(os.path.join("snake game asset", "black.png")), (5, 5))
FOOD_BIG = pygame.transform.scale(pygame.image.load(os.path.join("snake game asset", "food big.png")), (50, 50))
FOOD_BIG2 = pygame.transform.scale(pygame.image.load(os.path.join("snake game asset", "banana.png")), (50, 50))
BG = pygame.transform.scale(pygame.image.load(os.path.join("snake game asset", "bg.png")), (WIDTH, HEIGHT))
FG = pygame.transform.scale(pygame.image.load(os.path.join("snake game asset", "fg.png")), (WIDTH, HEIGHT))
PM = pygame.transform.scale(pygame.image.load(os.path.join("snake game asset", "pm.png")), (WIDTH, HEIGHT))
score_font = pygame.font.SysFont("conolas", 40)
HIT_SOUND = mixer.Sound(os.path.join("snake game asset", "hit.wav"))
mixer.music.load(os.path.join("snake game asset", "bg.wav"))


class snake_maker:
    def __init__(self, x, y, body, size):

        self.x = x
        self.y = y
        self.body = body
        self.size = size
        self.body_img = SNAKE_BODY
        self.head_img = SNAKE_HEAD
        self.mask = pygame.mask.from_surface(self.head_img)
        self.angle = 0
        self.black_img = BLACK
        self.score = 0

    # Whenever the snake makes a turn, the head piece rotates and so will the body
    # parts. This will alter the blit coordinates and the images may be printed in
    # a different place. So, we need to calibrate their blit position with each
    # rotation.
    def make_body(self):
        self.snake_head = (self.x, self.y, self.head_img)
        self.body_part = ()
        if self.angle == 0:
            self.body_part = (self.x - 2, self.y + 2, self.body_img)
        if self.angle == -90:
            self.body_part = (self.x + 2, self.y - 2, self.body_img)
        if self.angle == 90:
            self.body_part = (self.x + 2, self.y + 15, self.body_img)
        if self.angle == -180:
            self.body_part = (self.x + 15, self.y + 2, self.body_img)
        # self.black_part = ()

        if len(self.body) > self.size:
            del self.body[1]
        else:

            self.body.append(self.body_part)
            # self.body.append(self.black)

    def draw(self):

        for part in self.body[1:]:
            if self.angle == -180:
                WINDOW.blit(pygame.transform.flip(pygame.transform.rotate(part[2], self.angle), False, True),
                            (part[0], part[1]))
            else:
                WINDOW.blit(pygame.transform.rotate(part[2], self.angle), (part[0], part[1]))

        # Remember to draw the head separately, otherwise it will repeat itself like the
        # body parts.
        if self.angle == -180:
            # If the snake rotates at -180, you'll need to flip it along the y axis so that it doesn't appear
            # upside down. First rotate it, then flip it.
            WINDOW.blit(pygame.transform.flip(pygame.transform.rotate(self.snake_head[2], self.angle), False, True),
                        (self.snake_head[0], self.snake_head[1]))
        else:
            WINDOW.blit(pygame.transform.rotate(self.snake_head[2], self.angle),
                        (self.snake_head[0], self.snake_head[1]))

    def tail_bite(self):
        # To check for point by point collision, you can use the distance between the two
        # blit point of the two objects.
        for x in self.body[1:]:
            d = sqrt((x[0] - self.snake_head[0]) ** 2 + (x[1] - self.snake_head[1]) ** 2)
            if d <= 2:
                mixer.Sound.play(HIT_SOUND)
                return True

    def boundary_hit(self):

        if not (0 < self.x < WIDTH - 50) or not (0 < self.y < HEIGHT - 50):
            mixer.music.pause()
            mixer.Sound.play(HIT_SOUND)
            return True

    def score_show(self):
        score_label = score_font.render(f'Score: {self.score}', 1, (255, 255, 255))
        WINDOW.blit(score_label, (WIDTH // 2 - score_label.get_width() // 2, 10))


class food_maker:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.food_img = FOOD
        self.mask = pygame.mask.from_surface(self.food_img)

    def draw(self):
        WINDOW.blit(self.food_img, (self.x, self.y))


# Making the big food
class big_food:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.img = random.choice([FOOD_BIG2, FOOD_BIG])
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self):
        WINDOW.blit(self.img, (self.x, self.y))


# To detect collision. If collides, will return true
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj2.mask.overlap(obj1.mask, (offset_x, offset_y)) != None


def main_func():
    mixer.music.play(-1)
    # This list will contain the incrementing body parts of the
    # snake
    body = []
    size = 5
    snake = snake_maker(100, 100, body, size)
    food_x = random.randrange(10, WIDTH - 40)
    food_y = random.randrange(10, HEIGHT - 40)
    food = food_maker(food_x, food_y)
    bonus_food = big_food(food_x, food_y)

    # The sign of vel_x and vel_y determines in which direction
    # the snake is moving. If positive, moving in one way, if
    # negative, moving in other way.
    vel_x = 2
    vel_y = 0
    lost = False
    lost_timer = 0
    bonus_timer = 0
    bonus_count = 0
    bonus_score = 600

    def draw():

        WINDOW.blit(BG, (0, 0))
        food.draw()
        # Draw the bonus food on the screen for 5 seconds.
        if 0 < bonus_timer < 60 * 8:
            bonus_food.draw()
        snake.draw()
        snake.score_show()

        # If Player is lost, show the lost label.
        if lost:
            lost_font = pygame.font.SysFont("comicsans", 50)
            lost_label = lost_font.render(f'You lost :(', 1, (255, 255, 255))
            WINDOW.blit(lost_label, (300, 300))
        pygame.display.update()

    clock = pygame.time.Clock()
    LOOP_IS_RUNNING = True

    while LOOP_IS_RUNNING:
        clock.tick(60)
        snake.make_body()

        snake.x += vel_x
        snake.y += vel_y

        if snake.tail_bite():
            lost = True
            lost_timer += 1

        if snake.boundary_hit():
            lost = True
            lost_timer += 1

        if lost:
            mixer.music.pause()
            lost_font = pygame.font.SysFont("comic sans", 60)
            lost_label = lost_font.render(f'You lost :(', 1, (255, 255, 255))
            WINDOW.blit(lost_label,
                        (WIDTH // 2 - lost_label.get_width() // 2, HEIGHT // 2 - lost_label.get_height() // 2))
            pygame.display.update()

            if lost_timer > 60 * 1:

                LOOP_IS_RUNNING = False

            else:
                continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                LOOP_IS_RUNNING = False
                quit()
        # To make sure the snake doesn't go in the exact opposite direction,
        # we need to check the sign of velocity as well. For example,
        # keypress[pygame.K_UP] and not(vel_y>0) means that if the snake
        # is not going down (vel.y>0), only then can you manipulate the control.

        keypress = pygame.key.get_pressed()
        if keypress[pygame.K_UP] and not (vel_y > 0):
            snake.angle = 90
            vel_y = 2
            vel_y = -vel_y
            vel_x = 0

        if keypress[pygame.K_DOWN] and not (vel_y < 0):
            snake.angle = -90
            vel_y = 2
            vel_x = 0

        if keypress[pygame.K_LEFT] and not (vel_x > 0):
            snake.angle = -180
            vel_x = 2
            vel_x = -vel_x
            vel_y = 0

        if keypress[pygame.K_RIGHT] and not (vel_x < 0):
            snake.angle = 0
            vel_x = 2
            vel_y = 0

        if keypress[pygame.K_ESCAPE]:
            pause_game()

        if collide(snake, food):
            exp_sound = mixer.Sound(os.path.join("snake game asset", "bite.wav"))
            exp_sound.play()
            snake.score += 1
            bonus_count += 1
            pos_x = random.randrange(50, WIDTH - 50)
            pos_y = random.randrange(50, HEIGHT - 50)
            for i in snake.body:
                if (i[0] != pos_x and i[1] != pos_y) or (pos_x != snake.snake_head[0] and pos_y != snake.snake_head[1]):
                    food.x = pos_x
                    food.y = pos_y
                else:
                    food.x = 50
                    food.y = 50
            snake.size += 3

        # bonus_count counts the interval of the bonus food.
        # bonus timer counts the time that the food stays
        # on the screen. Since the loop runs 60 times a
        # second, the bonus score must be a high number
        # to compensate for the decrease with each cycle
        # until bonus timer passes 60*8 cycles or 8 seconds.
        if bonus_count >= 10:
            bonus_timer += 1
            bonus_score -= 1
        if bonus_timer > 60 * 8:
            bonus_count = 0
            bonus_timer = 0
            bonus_score = 600

        # If the snake eats the food bonus.
        if collide(snake, bonus_food) and bonus_count >= 10:
            exp_sound = mixer.Sound(os.path.join("snake game asset", "bite.wav"))
            exp_sound.play()
            bonus_count = 0
            bonus_timer = 0
            snake.score += round(bonus_score / 60)
            snake.size += 8
            bonus_score = 600

        draw()


# This will pause the game upon pressing esc and resume it on pressing enter.
def pause_game():
    # Making the pause menu items
    mixer.music.pause()
    paused = True

    while paused:
        # When in the pause loop, show these
        WINDOW.blit(PM, (0, 0))
        pygame.display.update()
        # Detecting press on the quit button of the window.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        # Detecting keypress for enter. If enter is pressed, it will return
        # to the game loop.
        keypress = pygame.key.get_pressed()
        if keypress[pygame.K_RETURN]:
            paused = False
            mixer.music.unpause()


def main_menu():
    run = True

    while run:
        WINDOW.blit(FG, (0, 0))
        pygame.display.update()
        # Detecting press on the quit button of the window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        keypress = pygame.key.get_pressed()
        if keypress[pygame.K_RETURN]:
            main_func()
    # If the loop is not running, it means that the game is quit.
    pygame.quit()


main_menu()
