from __future__ import absolute_import
import pygame

from consts import CELL_SIZE
from npc import Npc


class Smalldrug(Npc):
    images = ["smalldrug.png"]
    heal = 130

    def __init__(self, location):
        super(Smalldrug, self).__init__(location, (CELL_SIZE, CELL_SIZE))

    def do_collide(self, player):
        player.health += self.heal
        self.kill()


class Middledrug(Smalldrug):
    images = ["middledrug.png"]
    heal = 300


class Largedrug(Smalldrug):
    images = ["largedrug.png"]
    heal = 500
