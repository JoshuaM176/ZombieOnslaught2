from math import sqrt
import pygame as pg
from util.resource_loading import ResourceLoader, convert_files_to_sprites

resource_loader = ResourceLoader("projectiles", "attributes")
resource_loader.load_all()
arrow = resource_loader.get("arrow")
convert_files_to_sprites(arrow, "projectiles")

class Projectile:
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
        self.x = x + shiftX
        self.y = y + shiftY
        self.start_x = self.x
        self.start_y = self.y
        self.start_damge = damage
        self.damage = damage
        self.armour_pierce = armour_pierce
        self.dropoff = dropoff
        self.penetration = penetration
        self.head_mult = head_mult
        self.horizontal_movement = speed / sqrt(recoil + 1)
        self.vertical_movement = -self.horizontal_movement * recoil
        self.gravity = 0
        self.recent_hits = {}
        self.tracer = tracer

    def hit(self, entity):
        self.recent_hits[entity] = True
        self.damage *= self.penetration
        speed_mult = 0.75 + self.penetration * 0.1
        self.horizontal_movement *= speed_mult
        self.vertical_movement *= speed_mult


class Bullet(Projectile):

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
                    255 * self.damage / self.start_damge,
                    **self.tracer,
                )
                if self.tracer
                else None
            )
        return None

class Arrow(Projectile):
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
        self.x = x + shiftX
        self.y = y + shiftY
        self.start_x = self.x
        self.start_y = self.y
        self.start_damge = damage
        self.damage = damage
        self.armour_pierce = armour_pierce
        self.dropoff = dropoff
        self.penetration = penetration
        self.head_mult = head_mult
        self.horizontal_movement = speed / sqrt(recoil + 1)
        self.vertical_movement = -self.horizontal_movement * recoil
        self.gravity = 0
        self.recent_hits = {}
        self.tracer = tracer
        self.image, self.rect = (arrow["sprite"], arrow["sprite"].get_rect())

    def update(self, frame_time, screen: pg.Surface):
        if self.damage > 0:
            self.damage -= self.dropoff * frame_time
            self.rect.center = (self.x, self.y)
            self.x += self.horizontal_movement * frame_time
            self.y += self.vertical_movement * frame_time
            self.y += self.gravity * frame_time
            self.gravity += 100 * frame_time
            screen.blit(self.image, self.rect)
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
