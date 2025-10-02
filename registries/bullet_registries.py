from objects.bullets import Projectile, Tracer
import pygame as pg


class ProjectileRegistry:
    def __init__(self, size: int, screen, alpha_screen):
        self.screen = screen
        self.tracers = TracerRegistry(size * 4, alpha_screen)
        self.index = 0
        self.size = size
        self.projectiles: list[Projectile] = [None] * size

    def update(self, frame_time):
        self.tracers.update(frame_time)
        for projectile in self.projectiles:
            if projectile:
                self.tracers.add(projectile.update(frame_time, self.screen))

    def add(self, projectile: Projectile):
        self.projectiles[self.index] = projectile
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
