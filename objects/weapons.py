import pygame as pg
from registries.bullet_registries import BulletRegistry
from objects.bullets import Bullet
from random import uniform
from math import floor
from util.event_bus import event_bus
from dataclasses import dataclass


class Weapon(pg.sprite.Sprite):
    def __init__(
        self,
        name: str,
        player: dict,
        weapon: dict,
        ammo: dict,
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
        self.time_per_bullet = 60 / self.firerate
        self.time_since_last_bullet = 0
        self.bullet = bullet
        self.player = player
        self.shooting = False
        self.bullet_registry = bullet_registry
        self.recoil = 0
        self.reloading = False
        self.sprite_time = 0
        self.temp_sprite = None
        self.ammo = Ammo(**ammo)
        self.ui_bus = event_bus.put_events("ui_bus")
        self.ui_bus.send(None)

    def shoot(self, x, y):
        if self.ammo.get():
            self.fire_bullet(x, y)
            self.ui_bus.send({"bullets": self.ammo.get()})

    def fire_bullet(self, x, y):
        self.ammo.shoot()
        self.set_sprite(self.sprites["fire_sprite"], self.fire_animation_length)
        bullet = Bullet(
            x,
            y,
            **self.bullet,
            recoil=self.recoil + uniform(0, 0.005),
        )
        self.bullet_registry.add(bullet)
        self.recoil += self.recoil_per_shot
        if self.recoil > self.max_recoil:
            self.recoil = self.max_recoil
        self.time_since_last_bullet -= self.time_per_bullet
        if self.ammo.reload_type == 1:
            self.reloading = False

    def reload(self, frame_time):
        if not self.ammo.mags:
            self.reloading = False
            return
        steps = len(self.sprites["reloading"])
        animation, self.reloading = self.ammo.reload(frame_time)
        ind = floor(animation * steps)
        if ind >= steps:
            self.set_sprite(self.sprites["extra_reload_sprite"], 0.1)
        else:
            self.set_sprite(self.sprites["reloading"][ind], 0.1)
        self.ui_bus.send({"bullets": self.ammo.get(), "mags": self.ammo.mags})

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
        if self.reloading:
            self.reload(frame_time)
        self.ui_bus.send({"mags": self.ammo.mags})
        self.rect.topleft = x + self.shiftX, y + self.shiftY

    def update(self, frame_time):
        self.ammo.update(frame_time)


@dataclass
class Ammo:
    bullets: int
    bullet_in_chamber: bool
    mags: int
    mag_time: int
    reload_time: float
    reload_on_empty: float
    reload_type: int

    def __post_init__(self):
        self.reload_progress = 0
        self.mag_progress = 0
        self.max_bullets = self.bullets
        self.max_mags = self.mags
        if self.bullet_in_chamber:
            self.rounds_in_chamber = 1
        else:
            self.rounds_in_chamber = 0

    def get(self):
        return self.bullets + self.rounds_in_chamber

    def shoot(self):
        if self.rounds_in_chamber:
            self.rounds_in_chamber -= 1
        elif self.bullets:
            self.bullets -= 1

    def update(self, frame_time):
        if self.bullet_in_chamber:
            if not self.rounds_in_chamber and self.bullets:
                self.rounds_in_chamber += 1
                self.bullets -= 1
        if self.mags < self.max_mags:
            self.mag_progress += frame_time
            if self.mag_progress >= self.mag_time:
                self.mag_progress = 0
                self.mags +=1

    def reload(self, frame_time):
        if self.reload_type == 0:
            self.bullets = 0
        time = (
            self.reload_time if self.get() else self.reload_time + self.reload_on_empty
        )
        self.reload_progress += frame_time
        rtn = self.reload_progress / self.reload_time
        if self.reload_progress >= time:
            self.mags -= 1
            self.reload_progress = 0
            if self.reload_type == 0:
                self.bullets = self.max_bullets
            elif self.reload_type == 1:
                self.bullets += 1
        return rtn, False if self.bullets == self.max_bullets else True
