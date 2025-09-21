import pygame as pg
from game.screenpage import ScreenPage
from util.ui_objects import text, check_buttons, FuncButton
from util.event_bus import event_bus


class GameOver(ScreenPage):
    def __init__(self, screen: pg.Surface):
        super().__init__(screen, "game_over")
        self.buttons = []
        self.buttons.append(
            FuncButton(
                self.screen.get_width() / 2 + 100,
                300,
                500,
                100,
                self.screen,
                self.set_screen,
                ["store"],
                "Go To Store",
            )
        )
        self.buttons.append(
            FuncButton(
                self.screen.get_width() / 2 - 600,
                300,
                500,
                100,
                self.screen,
                self.set_screen,
                ["game"],
                "Play Again",
            )
        )

    def get_input(self):
        mouse_x, mouse_y = pg.mouse.get_pos()
        input_bus = event_bus.get_events("input_bus")

        for event in input_bus:
            match event.type:
                case pg.MOUSEBUTTONUP:
                    check_buttons(mouse_x, mouse_y, self.buttons)

    def update(self):
        self.go2 = self.page_name
        self.screen.fill((0, 100, 0))
        text(
            self.screen,
            "GAME OVER!",
            100,
            self.screen.get_width() / 2,
            100,
            align="CENTER",
        )
        self.get_input()
        for button in self.buttons:
            button.update()
        return self.go2
