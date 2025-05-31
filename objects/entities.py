import pygame as pg
from game.entities.hitreg import HitBox
from util.resource_loading import load_sprite, ResourceLoader

class Entity(pg.sprite.Sprite):
    def __init__(
            self,
            x: int,
            y: int,
            hitbox: list[int],
            head_hitbox: list[int],
            sprite: pg.Surface,
            **_):
        super().__init__()
        self.x = x
        self.y = y
        self.hitbox = HitBox(x, y, *hitbox)
        self.head_hitbox = HitBox(x, y, *head_hitbox)
        self.image, self.rect = sprite, sprite.get_rect()

    def update(self):
        self.rect.topleft = (self.x, self.y)

class Zombie(Entity):
    def __init__(self, x: int, y: int, round_scaling: bool = True, **attrs):
        super().__init__(x, y, **attrs)

    def update(self):
        self.hitbox.update(self.x, self.y)
        self.rect.topleft = (self.x, self.y)

class Player(Entity):
    def __init__(self, x, y):
        resource_loader = ResourceLoader("player", "attributes")
        resource_loader.load_all()
        resources = resource_loader.get("player")
        resources["sprite"] = load_sprite("player", "player", -1)
        super().__init__(x, y, **resources)
        self.render_plain = pg.sprite.RenderPlain((self))

    def update(self):
        self.rect.topleft = (self.x, self.y)
        self.render_plain.draw()