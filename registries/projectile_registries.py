from objects.projectiles.projectile import Projectile
from objects.projectiles.bullet import Tracer, Bullet
import pygame as pg


class ProjectileRegistry:
    def __init__(self, size: int, screen, alpha_screen):
        self.screen = screen
        self.alpha_screen = alpha_screen
        self.index = 0
        self.size = size
        self.projectiles: list[Projectile] = [None] * size

    def update(self, frame_time):
        for projectile in self.projectiles:
            if projectile:
                projectile.update(frame_time, self.screen, self.alpha_screen)

    def add(self, projectile: Projectile):
        self.projectiles[self.index] = projectile
        self.index += 1
        if self.index >= self.size:
            self.index = 0

    def __iter__(self):
        return iter(self.projectiles)


class BulletRegistry(ProjectileRegistry):
    def __init__(self, size: int, screen: pg.Surface, alpha_screen: pg.Surface):
        super().__init__(size, screen, alpha_screen)
        self.projectiles = [Bullet(0,0,0,0,0,0,0,0,0,0,0,None) for x in self.projectiles]
        self.tracers = TracerRegistry(self.size * 4, alpha_screen)

    def add(self, x, y, shiftX, shiftY, damage, armour_pierce, dropoff, speed, recoil, penetration, head_mult, tracer):
        self.projectiles[self.index].__init__(
            x,
            y,
            shiftX,
            shiftY,
            damage,
            armour_pierce,
            dropoff,
            speed,
            recoil,
            penetration,
            head_mult,
            tracer
        )
        self.index += 1
        if self.index >= self.size:
            self.index = 0

    def update(self, frame_time):
        self.tracers.update(frame_time)
        for projectile in self.projectiles:
            if projectile:
                self.tracers.add(projectile.update(frame_time, self.screen, self.alpha_screen))


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
