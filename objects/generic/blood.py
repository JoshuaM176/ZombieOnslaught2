import pygame as pg
import random
from math import sqrt

class Blood():
    def __init__(
            self,
            x,
            y,
            damage
    ):
        self.x = x
        self.y = y
        mult = sqrt(damage)*0.1 + min(damage*0.1, 1)
        size = 10 * mult
        self.time = 5 * mult
        self.start_time = self.time
        self.image = pg.Surface((size * 4, size * 4), pg.SRCALPHA)

        for i in range(round(10*mult)):
            size_mult = size * i / mult / 10
            x = random.uniform(size/2, 3*size/2)
            y = random.uniform(size/2, 3*size/2)
            width = random.uniform(3*size_mult/4, size_mult)
            height = random.uniform(3*size_mult/4, size_mult)
            pg.draw.ellipse(
                    self.image,
                    (random.uniform(150, 170), random.uniform(0, 20), random.uniform(0, 20), random.uniform(200, 255)),
                    (x - width / 2, y - height / 2, width, height)
                    )
        
        

    def update(self, frame_time, screen: pg.Surface, _):
        self.time -= frame_time
        if self.time < 0:
            return False
        self.image.set_alpha(self.time/self.start_time*255)
        screen.blit(self.image, (self.x, self.y))
        return True