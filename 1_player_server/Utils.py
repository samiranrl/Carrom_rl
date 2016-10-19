# Utility functions for the carrom server

from pygame.locals import *
from pygame.color import *
from math import sqrt, sin, cos, tan
import numpy as np
from random import randrange, gauss
from collections import OrderedDict
import pygame
import pymunk
import pymunk.pygame_util
import random
import sys
import os
import copy


# Global Variables


STATIC = 1  # Velocity below which an object is considered to be static
MIN_FORCE = 500  # Min Force to hit the striker
MAX_FORCE = 34000  # Max force to hit the striker
TIME_STEP = 20.0  # Step size for pymunk
TICKS_LIMIT = 3000  # Max ticks to consider


BOARD_SIZE = 800
BOARD_DAMPING = 0.95  # Velocity fall per second

BOARD_WALLS_SIZE = BOARD_SIZE * 2 / 75
WALLS_ELASTICITY = 0.7

COIN_MASS = 1
COIN_RADIUS = 15.01
COIN_ELASTICITY = 0.5

STRIKER_MASS = 2.8
STRIKER_RADIUS = 20.6
STRIKER_ELASTICITY = 0.7

POCKET_RADIUS = 22.51

STRIKER_COLOR = [65, 125, 212]
POCKET_COLOR = [0, 0, 0]
BLACK_COIN_COLOR = [43, 43, 43]
WHITE_COIN_COLOR = [169, 121, 47]
RED_COIN_COLOR = [169, 53, 53]
BOARD_WALLS_COLOR = [56, 32, 12]
BOARD_COLOR = [242, 209, 158]


# Array of initial coin positions
INITIAL = [(400, 403), (400, 368), (433, 385), (365, 390),
           (405, 437), (372, 428), (437, 420), (370, 350),
           (432, 350), (335, 406), (437, 455), (467, 402),
           (402, 332), (337, 367), (463, 367), (370, 465),
           (340, 443), (405, 474), (470, 437)]

INITIAL_STATE = {'White_Locations': [(400, 368), (437, 420), (372, 428), (337, 367), (402, 332),
                                     (463, 367), (470, 437), (405, 474), (340, 443)],
                 'Red_Location': [(400, 403)],
                 'Score': 0,
                 'Black_Locations': [(433, 385), (405, 437), (365, 390), (370, 350), (432, 350),
                                     (467, 402), (437, 455), (370, 465), (335, 406)]}

# Eucilidean Distance between two points


def dist(p1, p2):
    return sqrt(pow(p1[0] - p2[0], 2) + pow(p1[1] - p2[1], 2))

#  Given a state, return next free coin position


def ret_pos(state):
    s = state.copy()
    try:
        del s["Score"]
    except KeyError:
        pass
    x = s.values()
    x = reduce(lambda x, y: x + y, x)
    for i in INITIAL:
        free = 1
        for shape in x:
            if dist(shape, i) < 2 * COIN_RADIUS:
                free = 0
        if free == 1:
            return i

    return INITIAL[0]

# Initialize space


def init_space(space):
    space.damping = BOARD_DAMPING
    space.threads = 2

# Initialize walls


def init_walls(space):  # Initializes the four outer walls of the board
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    walls = [pymunk.Segment(body, (0, 0), (0, BOARD_SIZE), BOARD_WALLS_SIZE),
             pymunk.Segment(body, (0, 0), (BOARD_SIZE, 0), BOARD_WALLS_SIZE),
             pymunk.Segment(
                 body, (BOARD_SIZE, BOARD_SIZE), (BOARD_SIZE, 0), BOARD_WALLS_SIZE),
             pymunk.Segment(
                 body, (BOARD_SIZE, BOARD_SIZE), (0, BOARD_SIZE), BOARD_WALLS_SIZE)
             ]
    for wall in walls:
        wall.color = BOARD_WALLS_COLOR
        wall.elasticity = WALLS_ELASTICITY
    space.add(walls)

# Initialize pockets


def init_pockets(space):
    pockets = []
    for i in [(44.1, 44.1), (755.9, 44.1), (755.9, 755.9), (44.1, 755.9)]:
        inertia = pymunk.moment_for_circle(0.1, 0, POCKET_RADIUS, (0, 0))
        body = pymunk.Body(0.1, inertia)
        body.position = i
        shape = pymunk.Circle(body, POCKET_RADIUS, (0, 0))
        shape.color = POCKET_COLOR
        shape.collision_type = 2
        shape.filter = pymunk.ShapeFilter(categories=0b1000)
        space.add(body, shape)
        pockets.append(shape)
        del body
        del shape
    return pockets

# Initialize striker with force


def init_striker(space, x, passthrough, action, player):

    inertia = pymunk.moment_for_circle(STRIKER_MASS, 0, STRIKER_RADIUS, (0, 0))
    body = pymunk.Body(STRIKER_MASS, inertia)
    if player == 1:
        body.position = (action[0], 145)
    if player == 2:
        body.position = (action[0], BOARD_SIZE - 136)
    body.apply_force_at_world_point((cos(action[1]) * action[2], sin(
        action[1]) * action[2]), body.position + (STRIKER_RADIUS * 0, STRIKER_RADIUS * 0))

    shape = pymunk.Circle(body, STRIKER_RADIUS, (0, 0))
    shape.elasticity = STRIKER_ELASTICITY
    shape.color = STRIKER_COLOR

    mask = pymunk.ShapeFilter.ALL_MASKS ^ passthrough.filter.categories

    sf = pymunk.ShapeFilter(mask=mask)
    shape.filter = sf
    shape.collision_type = 2

    space.add(body, shape)
    return [body, shape]

# Adds coins to the board at the given coordinates


def init_coins(space, coords_black, coords_white, coord_red, passthrough):

    coins = []
    inertia = pymunk.moment_for_circle(COIN_MASS, 0, COIN_RADIUS, (0, 0))
    for coord in coords_black:
        body = pymunk.Body(COIN_MASS, inertia)
        body.position = coord
        shape = pymunk.Circle(body, COIN_RADIUS, (0, 0))
        shape.elasticity = COIN_ELASTICITY
        shape.color = BLACK_COIN_COLOR

        mask = pymunk.ShapeFilter.ALL_MASKS ^ passthrough.filter.categories

        sf = pymunk.ShapeFilter(mask=mask)
        shape.filter = sf
        shape.collision_type = 2

        space.add(body, shape)
        coins.append(shape)
        del body
        del shape

    for coord in coords_white:
        body = pymunk.Body(COIN_MASS, inertia)
        body.position = coord
        shape = pymunk.Circle(body, COIN_RADIUS, (0, 0))
        shape.elasticity = COIN_ELASTICITY
        shape.color = WHITE_COIN_COLOR

        mask = pymunk.ShapeFilter.ALL_MASKS ^ passthrough.filter.categories

        sf = pymunk.ShapeFilter(mask=mask)
        shape.filter = sf
        shape.collision_type = 2

        space.add(body, shape)
        coins.append(shape)
        del body
        del shape

    for coord in coord_red:
        body = pymunk.Body(COIN_MASS, inertia)
        body.position = coord
        shape = pymunk.Circle(body, COIN_RADIUS, (0, 0))
        shape.elasticity = COIN_ELASTICITY
        shape.color = RED_COIN_COLOR
        mask = pymunk.ShapeFilter.ALL_MASKS ^ passthrough.filter.categories

        sf = pymunk.ShapeFilter(mask=mask)
        shape.filter = sf
        shape.collision_type = 2

        space.add(body, shape)
        coins.append(shape)
        del body
        del shape
    return coins

 # Returns true is the speed of all objects on the board < STATIC


def is_ended(space):
    for shape in space._get_shapes():
        if abs(shape.body.velocity[0]) > STATIC or abs(shape.body.velocity[1]) > STATIC:
            return False
    return True




# A helpful visualization for the action
def draw_arrow(screen, position, angle, force, player):
    length = STRIKER_RADIUS + force / 500.0
    startpos_x = position
    if player == 2:
        startpos_y = 145
    else:
        startpos_y = BOARD_SIZE - 136
    endpos_x = (startpos_x + cos(angle) * length)
    endpos_y = (startpos_y - (length) * sin(angle))
    pygame.draw.line(
        screen, (50, 255, 50), (endpos_x, endpos_y), (startpos_x, startpos_y), 3)
    pygame.draw.circle(screen, (50, 255, 50),
                       (int(endpos_x), int(endpos_y)), 5)

# Everything done


def don(s1,conn1):
    s1.close()
    conn1.close()
    sys.exit()

# Parse the received action


def tuplise(s):
    return (round(float(s[0]), 4), round(float(s[1]), 4), round(float(s[2]), 4))

# Board background class


class BACKGROUND(pygame.sprite.Sprite):

    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


