import pygame as pg
from util.event_bus import event_bus
from util.ui_objects import text, get_font, progress_bar


class UI:
    def __init__(self, screen: pg.Surface):
        self.screen = screen
        self.data = {
            "weapon": "MP7",
            "bullets": 0,
            "mags": 0,
            "max_bullets": 0,
            "max_mags": 0,
            "money": 0,
            "round": 0,
            "next_weapon": False,
            "prev_weapon": False,
            "mag_progress": 0,
            "health": 10,
            "max_health": 10,
            "stamina": 100,
            "max_stamina": 100
        }
        self.consolas = get_font("consolas")

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
        text(
            self.screen,
            f"{self.data.get('bullets')}/{self.data.get('max_bullets')}",
            75,
            50,
            scr_height - 125,
        )
        text(
            self.screen,
            f"{self.data.get('mags')}/{self.data.get('max_mags')}",
            25,
            50,
            scr_height - 50,
        )
        text(self.screen, self.data.get("weapon"), 25, 50, scr_height - 150)
        text(
            self.screen,
            f"Money: {self.data.get('money'):.0f}",
            30,
            25,
            scr_height - 215,
        )
        text(self.screen, f"Round: {self.data.get('round'):.0f}", 30, 25, 35)
        next_weapon = self.data.get("next_weapon") or ""
        prev_weapon = self.data.get("prev_weapon") or ""
        text(
            self.screen,
            f"{prev_weapon:<10} <--> {next_weapon:>10}",
            10,
            5,
            scr_height - 165,
            font=self.consolas,
        )
        if self.data["mag_progress"]:
            progress_bar(
                self.screen, self.data["mag_progress"], 50, scr_height - 25, 100, 20
            )
        progress_bar(
            self.screen, self.data["stamina"]/self.data["max_stamina"], self.screen.get_width()*0.25, self.screen.get_height()-250, self.screen.get_width()*0.5, 20, color=(0, 100, 255), text_display=str(round(self.data["stamina"]*10))
        )
        progress_bar(
            self.screen, self.data["health"]/self.data["max_health"], self.screen.get_width()*0.25, self.screen.get_height()-230, self.screen.get_width()*0.5, 20, color=(0, 200, 0), text_display=str(round(self.data["health"],1))
        )
