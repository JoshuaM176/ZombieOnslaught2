import pygame as pg
from util.event_bus import event_bus
from util.ui_objects import text

class MainMenu():
    def __init__(self, screen: pg.Surface):
        self.screen = screen

    def update(self):
        self.screen.fill(color=(0, 100, 0))
        input_bus = event_bus.get_events("input_bus")
        for input in input_bus:
            return "game"
        return "main_menu"

class UI:
    def __init__(self, screen: pg.Surface):
        self.screen = screen
        self.data = {
            "weapon": "MP7",
            "bullets": 0,
            "mags": 0,
            "max_bullets": 0,
            "max_mags": 0,
        }

    def update(self):
        ui_bus = event_bus.get_events("ui_bus")
        for item in ui_bus:
            for atr, val in item.items():
                self.data[atr] = val
        pg.draw.rect(
            self.screen,
            (200, 255, 200),
            (0, self.screen.get_height() - 250, self.screen.get_width(), 250),
        )
        scr_width = self.screen.get_width()  # noqa
        scr_height = self.screen.get_height()
        # ammo
        text(self.screen, f"{self.data.get('bullets')}/{self.data.get('max_bullets')}", 75, 50, scr_height-125)
        text(self.screen, f"{self.data.get('mags')}/{self.data.get('max_mags')}", 25, 50, scr_height-50)
        text(self.screen, self.data.get('weapon'), 25, 50, scr_height-150)
