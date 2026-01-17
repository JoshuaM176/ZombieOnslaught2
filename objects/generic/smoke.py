import pygame as pg
import random

class Smoke():

            
    def __init__(
            self,
            x,
            y,
            size
        ):
        self.x = x - size/2
        self.y = y - size/2
        self.time = 5 
        self.start_time = self.time
        self.image = pg.Surface((size * 4, size * 4), pg.SRCALPHA)

        for i in range(10):
            rand_size = size + random.uniform(-1, 1)
            x = random.uniform(rand_size/2, 3*rand_size/2)
            y = random.uniform(size/2, 3*size/2)
            width = random.uniform(3*rand_size/4, rand_size)
            height = random.uniform(3*rand_size/4, rand_size)
            pg.draw.ellipse(
                    self.image,
                    (random.uniform(200, 220), random.uniform(200, 220), random.uniform(200, 220), random.uniform(250, 255)),
                    (x - width / 2, y - height / 2, width, height)
                )
        

    def update(self, frame_time, screen: pg.Surface, _):
        self.time -= frame_time
        if self.time < 0:
            return False
        self.image.set_alpha(min(self.time/self.start_time*500, 255))
        screen.blit(self.image, (self.x, self.y))
        return True