import pygame as pg
from game.screenpage import ScreenPage
from util.ui_objects import text, ButtonContainer, FuncButton
from util.event_bus import event_bus


class Settings(ScreenPage, ButtonContainer):
    def __init__(self, screen: pg.Surface):
        super().__init__(screen, "settings")
        self.buttons = []
        self.buttons.append(
            FuncButton(
                self.screen.get_width() - 550,
                self.screen.get_height() - 150,
                500,
                100,
                self.screen,
                self.go_to_store,
                [],
                "Go To Store",
            )
        )
        self.buttons.append(
            FuncButton(
                50,
                self.screen.get_height() - 150,
                500,
                100,
                self.screen,
                self.set_screen,
                ["game"],
                "Return to Game",
            )
        )
        self.buttons.append(
            FuncButton(
                self.screen.get_width()/2-250,
                self.screen.get_height() - 150,
                500,
                100,
                self.screen,
                self.set_screen,
                ["main_menu"],
                "Main Menu",
            )
        )

    def go_to_store(self):
        event_bus.add_event("game_event_bus", {"reset": {}})
        self.set_screen("store")

    def get_input(self):
        mouse_x, mouse_y = pg.mouse.get_pos()
        input_bus = event_bus.get_events("input_bus")
        for event in input_bus:
            self.check_buttons(event, mouse_x, mouse_y)

    def update(self):
        self.go2 = self.page_name
        self.screen.fill((100, 100, 100))
        text(
            self.screen,
            "Settings",
            75,
            self.screen.get_width() / 2,
            100,
            align="CENTER",
        )
        self.get_input()
        for button in self.buttons:
            button.update()
        return self.go2
