import pygame as pg
from util.event_bus import event_bus


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
        font = pg.font.Font(pg.font.get_default_font(), 75)
        text = font.render(
            f"{self.data.get('bullets')}/{self.data.get('max_bullets')}",
            True,
            (0, 0, 0),
        )
        self.screen.blit(text, (50, scr_height - 125))
        font = pg.font.Font(pg.font.get_default_font(), 25)
        text = font.render(
            f"{self.data.get('mags')}/{self.data.get('max_mags')}", True, (0, 0, 0)
        )
        self.screen.blit(text, (50, scr_height - 50))
        text = font.render(self.data.get("weapon"), True, (0, 0, 0))
        self.screen.blit(text, (50, scr_height - 150))
