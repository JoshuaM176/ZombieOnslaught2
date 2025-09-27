from objects.bullets import Bullet, Tracer
import pygame as pg


class BulletRegistry:
    def __init__(self, size: int, screen):
        self.tracers = TracerRegistry(size * 4, screen)
        self.index = 0
        self.size = size
        self.bullets: list[Bullet] = [None] * size

    def update(self, frame_time):
        self.tracers.update(frame_time)
        for bullet in self.bullets:
            if bullet:
                self.tracers.add(bullet.update(frame_time))

    def add(self, bullet: Bullet):
        self.bullets[self.index] = bullet
        self.index += 1
        if self.index >= self.size:
            self.index = 0


class TracerRegistry:
    def __init__(self, size: int, alpha_screen: pg.Surface):
        self.screen = alpha_screen
        self.index = 0
        self.size = size
        self.tracers: list[Tracer] = [None] * size

    def add(self, tracer: Tracer):
        if tracer:
            self.tracers[self.index] = tracer
            self.index += 1
            if self.index >= self.size:
                self.index = 0

    def update(self, frame_time):
        for tracer in self.tracers:
            if tracer:
                tracer.update(frame_time, self.screen)
