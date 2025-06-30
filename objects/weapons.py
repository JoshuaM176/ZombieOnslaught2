import pygame as pg
from registries.bullet_registries import BulletRegistry
from objects.bullets import Bullet
from random import uniform
from math import floor


class Weapon(pg.sprite.Sprite):
    def __init__(
        self,
        name: str,
        player: dict,
        weapon: dict,
        bullet: dict,
        bullet_registry: BulletRegistry,
    ):
        super().__init__()
        self.name = name
        self.sprites = weapon.pop("sprites")
        self.image, self.rect = (
            self.sprites["default"],
            self.sprites["default"].get_rect(),
        )
        for key, value in weapon.items():
            setattr(self, key, value)
        self.bullets = self.bullets_per_mag
        if self.bullet_in_chamber:
            self.rounds_in_chamber = 1
        else:
            self.rounds_in_chamber = 0
        self.mags = self.max_mags
        self.time_per_bullet = 60 / self.firerate
        self.time_since_last_bullet = 0
        self.bullet = bullet
        self.bullet_shift_x = self.bullet.pop("shiftX")
        self.bullet_shift_y = self.bullet.pop("shiftY")
        self.player = player
        self.shooting = False
        self.bullet_registry = bullet_registry
        self.recoil = 0
        self.reloading = False
        self.reload_progress = 0
        self.sprite_time = 0
        self.temp_sprite = None

    def shoot(self, x, y):
        if self.rounds_in_chamber > 0:
            self.fire_bullet(x, y)
            self.rounds_in_chamber -= 1
        elif self.bullets > 0 and not self.bullet_in_chamber:
            self.fire_bullet(x, y)
            self.bullets -= 1

    def fire_bullet(self, x, y):
        self.set_sprite(self.sprites["fire_sprite"], self.fire_animation_length)
        bullet = Bullet(
            x + self.bullet_shift_x,
            y + self.bullet_shift_y,
            **self.bullet,
            recoil=self.recoil + uniform(0, 0.005),
        )
        self.bullet_registry.add(bullet)
        self.recoil += self.recoil_per_shot
        if self.recoil > self.max_recoil:
            self.recoil = self.max_recoil
        self.time_since_last_bullet -= self.time_per_bullet
        if self.reload_type == 1:
            self.reloading = False

    def reload(self, frame_time):
        if self.bullets == self.bullets_per_mag or self.mags == 0:
            self.reloading = False
            return
        if self.reload_type == 0:
            self.bullets = 0
        time = self.reload_time
        if self.rounds_in_chamber + self.bullets == 0:
            time += self.reload_on_empty
        self.reload_progress += frame_time
        if self.reload_progress < time:
            steps = len(self.sprites["reloading"])
            ind = floor(self.reload_progress / self.reload_time * steps)
            if ind >= steps:
                self.set_sprite(self.sprites["extra_reload_sprite"], 0.1)
            else:
                self.set_sprite(self.sprites["reloading"][ind], 0.1)
        if self.reload_progress >= time:
            self.reload_progress = 0
            self.mags -= 1
            if self.reload_type == 0:
                self.reloading = False
                self.bullets = self.bullets_per_mag
            elif self.reload_type == 1:
                self.bullets += 1

    def set_sprite(self, sprite, time):
        self.temp_sprite = sprite
        self.sprite_time = time

    def get_sprite(self, frame_time):
        if self.sprite_time <= 0:
            self.sprite_time = 0
            self.image = self.sprites["default"]
        else:
            self.sprite_time -= frame_time
            self.image = self.temp_sprite

    def draw(self, x, y, frame_time, shooting, reloading):
        self.get_sprite(frame_time)
        self.shooting = shooting
        if reloading:
            self.reloading = reloading
        if self.recoil > 0:
            self.recoil -= self.recoil_control * frame_time
            if self.recoil < 0:
                self.recoil = 0
        if self.time_since_last_bullet < self.time_per_bullet:
            self.time_since_last_bullet += frame_time
        if self.shooting and self.time_since_last_bullet > self.time_per_bullet:
            self.shoot(x, y)
            if (
                self.bullet_in_chamber
                and self.bullets > 0
                and self.rounds_in_chamber == 0
            ):
                self.bullets -= 1
                self.rounds_in_chamber += 1
        if self.reloading:
            self.reload(frame_time)
        self.rect.topleft = x + self.shiftX, y + self.shiftY

    def update(self):
        pass
