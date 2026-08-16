from math import sqrt
from typing import override

import pygame as pg

from objects.projectiles.projectile import Projectile
from util.resource_loading import ResourceLoader, convert_files_to_sprites

resource_loader = ResourceLoader("projectiles", "attributes")
resource_loader.load_all()
arrow = resource_loader.get("arrow")
del resource_loader
convert_files_to_sprites(arrow, "projectiles")


class Arrow(Projectile):
    def __init__(
        self,
        x: float,
        y: float,
        shiftX: float,
        shiftY: float,
        damage: float,
        armour_pierce: float,
        dropoff: float,
        speed: float,
        recoil: float,
        penetration: float,
        head_mult: float,
        flip_sprite: bool = False,
        **_,
    ):
        self.x = x + shiftX
        self.y = y + shiftY
        self.start_x = self.x
        self.start_y = self.y
        self.start_damge = damage
        self.damage = damage
        self.armour_pierce = armour_pierce
        self.dropoff = dropoff
        self.penetration = penetration
        self.head_mult = head_mult
        self.horizontal_movement = speed / sqrt(recoil + 1)
        self.vertical_movement = -self.horizontal_movement * recoil
        self.gravity = 0
        self.recent_hits = set()
        self.image, self.rect = (arrow["sprite"], arrow["sprite"].get_rect())
        if flip_sprite:
            self.image = pg.transform.flip(self.image, True, False)

    @override
    def update(self, frame_time: float, screen: pg.Surface, alpha_screen: pg.Surface):
        if self.damage > 0:
            self.damage -= self.dropoff * frame_time
            self.rect.center = (self.x, self.y)
            self.x += self.horizontal_movement * frame_time
            self.y += self.vertical_movement * frame_time
            self.y += self.gravity * frame_time
            self.gravity += 100 * frame_time
            screen.blit(self.image, self.rect)
