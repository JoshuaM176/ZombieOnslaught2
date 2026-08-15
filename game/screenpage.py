from __future__ import annotations

import pygame as pg

screen_pages: dict[str, ScreenPage] = {}


class ScreenPage:
    def __init__(self, screen: pg.Surface, page_name: str, screen_init: bool = True):
        screen_pages[page_name] = self
        self.screen = screen
        self.page_name = page_name
        self.go2 = page_name
        if screen_init:
            self.__screen_init__()

    def __screen_init__(self) -> None:
        """Called whenever screen size changes"""

    def update(self) -> None:
        return self.go2

    def set_screen(self, go2: str) -> None:
        self.go2 = go2
