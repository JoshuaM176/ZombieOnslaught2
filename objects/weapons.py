import pygame as pg

class Weapon(pg.sprite.Sprite):
    def __init__(
            self,
            name: str,
            player: dict,
            weapon: dict,
            bullet: dict):
        super().__init__()
        self.name = name
        self.sprites = weapon.pop("sprites")
        self.image, self.rect = self.sprites["default"], self.sprites["default"].get_rect()
        for key, value in weapon.items():
            setattr(self, key, value)
        self.bullet = bullet
        self.player = player

    def draw(self, x, y):
        self.rect.topleft = x+self.shiftX, y+self.shiftY

    def update(self):
        pass