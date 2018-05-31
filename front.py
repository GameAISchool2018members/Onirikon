#!/usr/bin/env pythonw

import pygame
from pygame.locals import QUIT, K_SPACE, KEYDOWN

import sys

from game_utils import GameUtils
from level import Level, EmptyCell, BlockCell, StartPositionCell, ExitCell
from controllers import KeyboardController
from world import World
from trajectory import Trajectory


class GameEngine:
    SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 768
    CELL_SIZE = 20
    TICKS_PER_SECOND = 60
    ACTION_INTERVAL_TICKS = 1

    def init_display(self, fullscreen):
        if fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.HWSURFACE)
        else:
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE)
        surface = pygame.Surface(self.screen.get_size())
        self.surface = surface.convert()
        self.surface.fill((255, 255, 255))

    def init_clock(self):
        self.clock = pygame.time.Clock()

    def init_keyboard(self):
        pygame.key.set_repeat(1, 40)

    def __init__(self, fullscreen=False):
        pygame.init()
        self.init_display(fullscreen)
        self.init_keyboard()
        self.init_clock()

    def initialize_level(self, level_filename=None):
        if level_filename is None:
            self.level = Level(10, 10)
            trajectory = Trajectory()
            trajectory .initialize(self.level)
            self.level.generate_from_trajectory(trajectory, 0.2)
        else:
            self.level = Level.load_level(level_filename)
        self.level_width, self.level_height = self.level.size()
        self.game_objects = []
        for x in range(self.level_width):
            for y in range(self.level_height):
                cell = self.level.get_cell(x, y)
                if type(cell) is EmptyCell:
                    obj = None
                elif type(cell) is BlockCell:
                    obj = Block(x, y)
                elif type(cell) is StartPositionCell:
                    obj = Player(x, y)
                    self.player = obj
                elif type(cell) is ExitCell:
                    obj = Exit(x, y)
                    self.exit = obj
                else:
                    obj = None
                if obj is not None:
                    self.game_objects.append(obj)
        self.sprites = pygame.sprite.Group(self.game_objects)
        self.world = World(self.level)
        self.state = self.world.init_state

    def initialize_controller(self, controller):
        self.controller = controller

    def update_display(self):
        self.screen.blit(self.surface, (0, 0))
        self.sprites.update()
        self.sprites.draw(self.screen)
        pygame.display.flip()
        pygame.display.update()

    def loop(self):
        tick = 0
        keys = []
        while True:
            pygame.event.pump()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if K_SPACE == event.key:
                        print('space pressed')
                        pygame.quit()
                        sys.exit()
                    else:
                        keys.append(event)
            if tick % self.ACTION_INTERVAL_TICKS == 0:
                action = self.controller.get_action(data=keys)
                if action is not None:
                    state = self.world.perform(self.state, action)
                    if state is not None:
                        self.state = state
                        player_pos = self.world.get_player_position(self.state)
                        self.player.x, self.player.y = player_pos
                        self.player.update_coords()
                        if self.player.x == self.exit.x and self.player.y == self.exit.y:
                            print("WIN")
                keys = []
            self.update_display()
            self.clock.tick(self.TICKS_PER_SECOND)
            tick += 1


class GameObject(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.update_coords()
        super().__init__()

    def update_coords(self):
        self.rect.x = self.x * GameEngine.CELL_SIZE
        self.rect.y = self.y * GameEngine.CELL_SIZE


class Block(GameObject):
    def __init__(self, x, y):
        self.image, self.rect = GameUtils.load_image('block.png')
        super().__init__(x, y)


class Player(GameObject):
    def __init__(self, x, y):
        self.image, self.rect = GameUtils.load_image('player.png')
        super().__init__(x, y)


class Exit(GameObject):
    def __init__(self, x, y):
        self.image, self.rect = GameUtils.load_image('exit.png')
        super().__init__(x, y)


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        level_filename = sys.argv[1]
    else:
        level_filename = None
    engine = GameEngine(fullscreen=False)
    engine.initialize_level(level_filename)
    engine.initialize_controller(KeyboardController())
    engine.loop()
