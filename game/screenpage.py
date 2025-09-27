import pygame as pg

screen_pages = {}

class ScreenPage:
    def __init__(self, screen: pg.Surface, page_name: str):
        screen_pages[page_name] = self
        self.screen = screen
        self.page_name = page_name
        self.go2 = page_name
        self.__screen_init__()

    def __screen_init__(self):
        """Called whenever screen size changes"""
        pass

    def update(self):
        return self.go2

    def set_screen(self, go2: str):
        self.go2 = go2
