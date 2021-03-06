#! /usr/bin/env python
#coding=utf-8
import pygame
import sys
import os.path
import time
import random

from consts import *
from msgbox import Msgbox
from floor import Floor
from npcs import UpStair, DownStair
from snakes import KingSnake
from character import load_images, Character


class Player(Character):
    images = load_images(["worior.png", "worior2.png"])

    def __init__(self, game, speed, location, gameboard):
        super(Player, self).__init__(location, (CELL_SIZE,CELL_SIZE))
        self.game = game
        self.root = game.root
        self.gameboard = gameboard
        self.speed = speed
        self.flyable = False
        self.condition = "NORMAL"
        self.on_power = False
        self.get_top = False
        self.health = 500
        self.magic = 200
        self.feature = "NONE"
        self.defence = 0
        self.ykeynum = 0
        self.bkeynum = 0
        self.rkeynum = 0
        self.gkeynum = 0
        self.swordkeynum = 0
        self.snakedp = 0
        self.snakerocknum = 0
        self.money = 0
        self.exp = 0
        self.level = 1
        STARTFLOOR = 1
        self.currentfloor = Floor(STARTFLOOR)
        self.visited_floors = {STARTFLOOR: self.currentfloor}
        self.quests = []

    def is_out(self):
        if self.rect.left < self.gameboard.get_rect().left:
            return True
        if self.rect.right > self.gameboard.get_rect().right:
            return True
        if self.rect.top < self.gameboard.get_rect().top:
            return True
        if self.rect.bottom > self.gameboard.get_rect().bottom:
            return True
        return False

    def update(self):
        super(Player, self).update()
        self.oldpos = self.rect.copy()
        """if self.speed != [0, 0]:
            for i in range(CELL_SIZE/STEP):
                self.rect.move_ip(self.speed)
                self.image = self.next_image()
                self.gameboard.blit(self.image, self.rect)
                pygame.display.update()
                pygame.time.delay(500)
        """
        self.rect.move_ip(self.speed)
        if self.is_out():
            self.rect = self.oldpos

        for npc in pygame.sprite.spritecollide(self, self.currentfloor.group, dokill=False):
            for quest in self.quests:
                if npc in quest.targets:
                    quest.execute(player, npc)
            npc.do_collide(self)

        if self.condition == "POISON":
            if time.time() > self.condition_endtime:
                self.condition = "NORMAL"
            else:
                if time.time() > self.condition_time + 1:
                    self.health -= 10
                    self.condition_time = time.time()
        elif self.condition == "DIZZY":
            if time.time() > self.condition_endtime:
                self.condition = "NORMAL"
            else:
                if self.speed != [0, 0]:
                    hurt = random.randint(1, 2)
                    if hurt == 1:
                        self.health -= 100 if self.health > 0 else 0
                        self.magic -= 80 if self.magic > 0 else 0
                        self.feature = random.choice(["FIRE", "GRASS", "WATER", "SOIL", "SKY", "LIGHT", "SNOW"])
                        self.defence -= 60

        self.speed = [0, 0]

        if self.is_dead():
            self.suicide()

    def hurt(self, damage):
        if damage - self.defence >= 0:
            self.health -= damage - self.defence

    def weaken(self, damage):
        self.magic -= damage
        if self.magic < 0:
            self.hurt(damage - self.magic * 3)
            self.magic = 0

    def undo(self):
        self.rect = self.oldpos

    def is_dead(self):
        if self.health <= 0:
            return True

    def suicide(self):
        self.health = 0
        pygame.mixer.music.stop()
        pygame.mixer.music.load(os.path.join("sound","dead.aif"))
        pygame.mixer.music.play(1)
        msgbox = Msgbox("Game over!!!", (100,100))
        msgbox.show()
        self.kill()
        sys.exit()

    def goto_floor(self, floornum):
        """ 跳转至指定楼层。
            floornum: 去往楼层号
        """
        if floornum == self.currentfloor.floornum:
            return
        f = self.visited_floors.get(floornum)
        if f is None:
            f = Floor(floornum)
            self.visited_floors[floornum] = f
        self.root.remove(self.currentfloor.group)
        oldfloornum = self.currentfloor.floornum
        self.currentfloor = f
        self.root.add(self.currentfloor.group)
        if floornum > oldfloornum:
            for npc in self.currentfloor.group.sprites():
                if isinstance(npc, DownStair):
                    self.rect.left = npc.rect.left + CELL_SIZE
                    self.rect.top = npc.rect.top
                    if self.currentfloor.floornum == 10:
                        if KingSnake.first_ften == True:
                            Msgbox("You get here, now. But you can't continue.").show()
                            KingSnake.first_ften = False
        else:
            for npc in self.currentfloor.group.sprites():
                if isinstance(npc, UpStair):
                    if self.currentfloor.floornum == 7:
                        self.rect.left = npc.rect.left + CELL_SIZE
                        self.rect.top = npc.rect.top
                    elif self.currentfloor.floornum in [8, 12]:
                        self.rect.left = npc.rect.left
                        self.rect.top = npc.rect.top - CELL_SIZE
                    elif self.currentfloor.floornum == 9:
                        self.rect.left = npc.rect.left
                        self.rect.top = npc.rect.top + CELL_SIZE
                    else:
                        self.rect.left = npc.rect.left - CELL_SIZE
                        self.rect.top = npc.rect.top
            
    def go_upstair(self):
        self.goto_floor(self.currentfloor.floornum+1)
        
    def go_downstair(self):
        self.goto_floor(self.currentfloor.floornum-1)
        
    def poison(self):
        self.condition = "POISON"
        Msgbox("Ouch! You've got POISON condition to hurt health!").show()
        self.condition_time = time.time()
        self.condition_endtime = time.time() + 30

    def dizzy(self):
        self.condition = "DIZZY"
        Msgbox("Oops! You've got DIZZY condition to have a scaring time!").show()
        self.condition_time = time.time()
        self.condition_endtime = time.time() + 30

    def buy_y(self):
        if self.money >= 20:
            self.money -= 20
            self.ykeynum += 1

    def buy_y2(self):
        if self.money >= 80:
            self.money -= 80
            self.ykeynum += 5

    def buy_b(self):
        if self.money >= 30:
            self.money -= 30
            self.bkeynum += 1

    def buy_b2(self):
        if self.money >= 130:
            self.money -= 130
            self.bkeynum += 5

    def buy_r(self):
        if self.money >= 50:
            self.money -= 50
            self.rkeynum += 1

    def buy_r2(self):
        if self.money >= 220:
            self.money -= 220
            self.rkeynum += 5

    def buy_g(self):
        if self.money >= 80:
            self.money -= 80
            self.gkeynum += 1

    def buy_g2(self):
        if self.money >= 360:
            self.money -= 360
            self.gkeynum += 5

    def buy_smalldr(self):
        if self.exp >= 20:
            self.exp -= 20
            self.health += 130

    def buy_largedr(self):
        if self.exp >= 70:
            self.exp -= 70
            self.health += 500

    def buy_defrk(self):
        if self.exp >= 20:
            self.exp -= 20
            self.defence += 8

    def buy_largedef(self):
        if self.exp >= 150:
            self.exp -= 150
            self.defence += 60

    def buy_snakerk(self):
        if self.exp >= 20:
            self.exp -= 20
            self.snakerocknum += 1

    def buy_magic(self):
        if self.exp >= 80:
            self.exp -= 80
            self.magic += 90

    def buy_level(self):
        if self.exp >= 100:
            self.exp -= 100
            self.level += 1
            self.health += 300
            self.defence += 30

    def buy_level2(self):
        if self.exp >= 270:
            self.exp -= 270
            self.level += 3
            self.health += 900
            self.defence += 90
    
    def pick_key(self, key):
        attr = key + 'keynum'
        setattr(self, attr, getattr(self, attr) + 1)
    
    def use_key(self, key):
        attr = key + 'keynum'
        keynum = getattr(self, attr)
        if keynum > 0:
            setattr(self, attr, keynum - 1)
            return True
        return False


class CheatPlayer(Player):

    def __init__(self, game, speed, location, gameboard):
        super(CheatPlayer, self).__init__(game, speed, location, gameboard)
        self.condition = "NORMAL"
        self.flyable = True
        self.on_power = False
        self.get_top = False
        self.health = 500000
        self.magic = 200000
        self.feature = "NONE"
        self.defence = 100000
        self.ykeynum = 100
        self.bkeynum = 100
        self.rkeynum = 100
        self.gkeynum = 100
        self.swordkeynum = 100
        self.snakedp = 0
        self.snakerocknum = 0
        self.money = 1000
        self.exp = 1000
        self.level = 1
        STARTFLOOR = 20
        self.currentfloor = Floor(STARTFLOOR)
        self.visited_floors = {STARTFLOOR: self.currentfloor}
        self.quests = []
