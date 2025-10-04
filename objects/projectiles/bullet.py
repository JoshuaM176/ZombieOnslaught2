from objects.projectiles.projectile import Projectile
import pygame as pg

class Bullet(Projectile):

    def __init__(
        self,
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
    ):
        super().__init__(
            x + shiftX,
            y + shiftY,
            damage,
            armour_pierce,
            dropoff,
            speed,
            recoil,
            penetration,
            head_mult
        )
        self.start_damage = damage
        self.tracer = tracer

    def update(self, frame_time, *_):
        if self.damage > 0:
            self.damage -= self.dropoff * frame_time
            start_x = self.x
            start_y = self.y
            self.x += self.horizontal_movement * frame_time
            self.y += self.vertical_movement * frame_time
            self.y += self.gravity * frame_time
            self.gravity += 100 * frame_time
            return (
                Tracer(
                    start_x,
                    start_y,
                    self.x,
                    self.y,
                    255 * self.damage / self.start_damage,
                    **self.tracer,
                )
                if self.tracer
                else None
            )
        return None
    
class Tracer:
    def __init__(
        self,
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float,
        alpha,
        color: tuple = (200, 200, 0),
        size: int = 2,
    ):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.alpha = alpha
        self.color = color
        self.size = size

    def update(self, frame_time, screen):
        alpha = self.alpha
        self.alpha -= 9000 * frame_time
        if alpha > 0:
            pg.draw.line(
                screen,
                self.color + [alpha],
                (self.start_x, self.start_y),
                (self.end_x, self.end_y),
                self.size,
            )