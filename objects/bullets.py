from math import sqrt


class Bullet:
    def __init__(
        self, x, y, damage, dropoff, speed, recoil, penetration, head_mult, tracer
    ):
        self.x = x
        self.y = y
        self.start_damge = damage
        self.damage = damage
        self.dropoff = dropoff
        self.penetration = penetration
        self.head_mult = head_mult
        self.tracer = tracer
        self.horizontal_movement = speed / sqrt(recoil + 1)
        self.vertical_movement = -self.horizontal_movement * recoil

    def update(self, frame_time):
        self.damage -= self.dropoff * frame_time
        if self.damage > 0:
            start_x = self.x
            start_y = self.y
            self.x += self.horizontal_movement * frame_time
            self.y += self.vertical_movement * frame_time
            return (
                Tracer(
                    start_x,
                    start_y,
                    self.x,
                    self.y,
                    255 * self.damage / self.start_damge,
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
    ):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.alpha = alpha
        self.color = color

    def update(self, frame_time):
        alpha = self.alpha
        self.alpha -= 9000 * frame_time
        if alpha > 0:
            return (
                (200, 200, 0, alpha),
                (self.start_x, self.start_y),
                (self.end_x, self.end_y),
            )
        return None
