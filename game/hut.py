import pygame as pg
from util.resource_loading import ResourceLoader, convert_files_to_sprites
from random import uniform

resource_loader = ResourceLoader("game", "attributes")
resource_loader.load_all()
data = resource_loader.get("hut")
convert_files_to_sprites(data, "game")

class Hut(pg.sprite.Sprite):
    def __init__(self, x, y, village_health):
        super().__init__()
        self.x = x
        self.y = y
        self.sprites = data["sprites"]
        self.max_status = len(self.sprites)
        self.status = round((1-village_health)*(self.max_status-1))
        self.image, self.rect = (self.sprites[self.status], self.sprites[self.status].get_rect())
        self.rect.bottomleft = (self.x, self.y)

    def damage(self, village_health):
        if self.status < self.max_status-1:
            rand_float = uniform(0, 2.2) - self.status/self.max_status
            if rand_float > village_health:
                self.status += 1
                self.image = self.sprites[self.status]

    def reset(self):
        self.status = 0
        self.image, self.rect = (self.sprites[self.status], self.sprites[self.status].get_rect())
        self.rect.bottomleft = (self.x, self.y)
