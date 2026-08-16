from abc import ABC, abstractmethod
from math import sqrt
from typing import Any

import pygame as pg


class Projectile(ABC):
    def __init__(
        self,
        x: float,
        y: float,
        damage: float,
        armour_pierce: float,
        dropoff: float,
        speed: float,
        recoil: float,
        penetration: float,
        head_mult: float,
        **_,
    ):
        self.x = x
        self.y = y
        self.start_x = self.x
        self.start_y = self.y
        self.damage = damage
        self.armour_pierce = armour_pierce
        self.dropoff = dropoff
        self.penetration = penetration
        self.head_mult = head_mult
        self.horizontal_movement = speed / sqrt(recoil + 1)
        self.vertical_movement = -self.horizontal_movement * recoil
        self.gravity: float = 0
        self.recent_hits = set()

    def hit(self, entity):
        self.recent_hits.add(entity)
        self.damage *= self.penetration
        speed_mult = 0.75 + self.penetration * 0.1
        self.horizontal_movement *= speed_mult
        self.vertical_movement *= speed_mult

    @abstractmethod
    def update(self, frame_time: float, screen: pg.Surface, alpha_screen: pg.Surface) -> Any:
        pass
