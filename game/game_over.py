import pygame as pg

from game.screenpage import ScreenPage
from util.ui_objects import ButtonContainer, Text, TextButton


class GameOver(ScreenPage, ButtonContainer):
    def __init__(self, screen: pg.Surface) -> None:
        super().__init__(screen, "game_over")

    def __screen_init__(self) -> None:
        self.buttons = []
        scr_w = self.screen.get_width()
        self.buttons.append(
            TextButton(scr_w // 2 + 100, 300, 500, 100, self.screen, lambda: self.set_screen("store"), "Go To Store"),
        )
        self.buttons.append(
            TextButton(scr_w // 2 - 600, 300, 500, 100, self.screen, lambda: self.set_screen("game"), "Play Again"),
        )
        self.game_over_text = Text("GAME OVER!", 100, self.screen.get_width() / 2, 100, align="CENTER")

    def update(self) -> str:
        self.go2 = self.page_name
        self.screen.fill((0, 100, 0))
        self.game_over_text.update(self.screen)
        self.get_input()
        for button in self.buttons:
            button.update()
        return self.go2
