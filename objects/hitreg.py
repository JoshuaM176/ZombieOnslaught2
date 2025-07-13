import pygame as pg


class HitBox:
    def __init__(self, x, y, x_shift, y_shift, width, height):
        self.x_shift = x_shift
        self.y_shift = y_shift
        self.width = width
        self.height = height
        self.start_x = x + x_shift
        self.start_y = y + y_shift
        self.end_x = self.start_x + width
        self.end_y = self.start_y + height

    def get(self):
        return (
            self.start_x,
            self.start_y,
            self.end_x-self.start_x,
            self.end_y-self.start_y,
        )

    def update(self, x, y):
        self.start_x = x + self.x_shift
        self.start_y = y + self.y_shift
        self.end_x = self.start_x + self.width
        self.end_y = self.start_y + self.height

    def display(self, screen: pg.Surface):
        points = self.get()
        pg.draw.rect(screen, (100, 0, 0), points)

    def check(self, x, y):
        if y >= self.start_y and y <= self.end_y:
            if x >= self.start_x and x <= self.end_x:
                return True
        return False
