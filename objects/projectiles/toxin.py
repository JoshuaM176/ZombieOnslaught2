from objects.projectiles.projectile import Projectile
import pygame as pg
import random

class Toxin(Projectile):

    def __init__(
        self,
        x,
        y,
        damage,
        dropoff,
    ):
        self.x = x + random.uniform(-200, 100)
        self.y = y + random.uniform(-100, 100)
        self.start_x = self.x
        self.start_y = self.y
        self.damage = damage
        self.start_damage = damage
        self.dropoff = dropoff
        self.head_mult = 1
        self.armour_pierce = 0
        self.horizontal_movement = random.uniform(-300, 100)
        self.vertical_movement = 0
        self.gravity = random.uniform(-200, 100)
        self.recent_hits = {}

    def hit(self, entity):
        self.recent_hits[entity] = True

    def update(self, frame_time, _, screen: pg.Surface):
        if self.damage > 0:
            pg.draw.rect(screen, color=(200,0,200, 255*self.damage/self.start_damage), rect=(self.x, self.y, 2, 2))
            self.damage -= self.dropoff * frame_time
            self.x += self.horizontal_movement * frame_time
            self.y += self.vertical_movement * frame_time
            self.y += self.gravity * frame_time
            self.gravity += 10 * frame_time
        return None