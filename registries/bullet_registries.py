from objects.bullets import Bullet


class BulletRegistry:
    def __init__(self, size: int):
        self.index = 0
        self.size = size
        self.bullets: list[Bullet] = [None] * size

    def update(self):
        for bullet in self.bullets:
            bullet.update()

    def add(self, bullet: Bullet):
        self.bullets[self.index] = bullet
        self.index += 1
        if self.index >= self.size:
            self.index = 0
