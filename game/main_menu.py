from util.event_bus import event_bus
import pygame as pg


class MainMenu:
    def __init__(self, screen: pg.Surface):
        self.screen = screen

    def update(self):
        self.screen.fill(color=(0, 100, 0))
        input_bus = event_bus.get_events("input_bus")
        for input in input_bus:
            return "game"
        return "main_menu"
