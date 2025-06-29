import pygame as pg
from registries.bullet_registries import BulletRegistry
from objects.bullets import Bullet


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
        self.time_per_bullet = 60 / self.firerate
        self.time_since_last_bullet = 0
        self.bullet = bullet
        self.bullet_shift_x = self.bullet.pop("shiftX")
        self.bullet_shift_y = self.bullet.pop("shiftY")
        self.player = player
        self.shooting = True
        self.bullet_registry = bullet_registry
        self.recoil = 0

    def shoot(self, x, y):
        bullet = Bullet(
            x + self.bullet_shift_x,
            y + self.bullet_shift_y,
            **self.bullet,
            recoil=self.recoil,
        )
        self.bullet_registry.add(bullet)
        self.recoil += self.recoil_per_shot

    def draw(self, x, y, frame_time):
        if self.time_since_last_bullet < self.time_per_bullet:
            self.time_since_last_bullet += frame_time
        if self.shooting and self.time_since_last_bullet > self.time_per_bullet:
            self.shoot(x, y)
        self.rect.topleft = x + self.shiftX, y + self.shiftY

    def update(self):
        pass
