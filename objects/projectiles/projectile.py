from math import sqrt

class Projectile:
    def __init__(
        self,
        x,
        y,
        damage,
        armour_pierce,
        dropoff,
        speed,
        recoil,
        penetration,
        head_mult,
        **_
    ):
        self.x = x
        self.y = y
        self.start_x = self.x
        self.start_y = self.y
        self.damage = damage
        self.armour_pierce = armour_pierce
        self.dropoff = dropoff
        self.penetration = penetration
        self.head_mult = head_mult
        self.horizontal_movement = speed / sqrt(recoil + 1)
        self.vertical_movement = -self.horizontal_movement * recoil
        self.gravity = 0
        self.recent_hits = {}

    def hit(self, entity):
        self.recent_hits[entity] = True
        self.damage *= self.penetration
        speed_mult = 0.75 + self.penetration * 0.1
        self.horizontal_movement *= speed_mult
        self.vertical_movement *= speed_mult

    def update(self, screen):
        pass