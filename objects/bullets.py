from math import sqrt


class Bullet:
    def __init__(
        self, x, y, damage, dropoff, speed, recoil, penetration, head_mult, tracer
    ):
        self.x = x
        self.y = y
        self.damage = damage
        self.dropoff = dropoff
        self.penetration = penetration
        self.head_mult = head_mult
        self.tracer = tracer
        self.horizontal_movement = speed / sqrt(recoil + 1)
        self.vertical_movement = self.horizontal_movement * recoil

    def update(self):
        self.x += self.horizontal_movement
        self.y += self.vertical_movement


class Tracer:
    def __init__(
        self, start_x: float, start_y: float, end_x: float, end_y: float, color: tuple
    ):
        pass
