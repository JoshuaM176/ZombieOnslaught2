import pygame as pg

class ScreenPage():

    def __init__(self, screen: pg.Surface, page_name: str):
        self.screen = screen
        self.page_name = page_name
        self.go2 = page_name
        self.updatables = []

    def update(self):
        return self.go2