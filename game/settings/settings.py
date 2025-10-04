import pygame as pg
from game.screenpage import ScreenPage
from util.ui_objects import Text, ButtonContainer, FuncButton, Button
from util.event_bus import event_bus
from game.settings.keybind_settings import KeybindSettings
from dataclasses import dataclass, field


class Settings(ScreenPage, ButtonContainer):
    def __init__(self, screen: pg.Surface, settings: dict):
        self.settings_screens = ["keybind_settings"]
        self.settings_data = SettingsData(**settings)
        super().__init__(screen, "settings")
        self.keybind_settings = KeybindSettings(screen, self.settings_data.key_map)
        self.settings_data.player_key_map = self.keybind_settings.player_key_map

    def __screen_init__(self):
        self.buttons = []
        scr_w = self.screen.get_width()
        scr_h = self.screen.get_height()
        self.settings_text = Text("Settings", 75, scr_w / 2, 100, align="CENTER")
        self.buttons.append(FuncButton(scr_w - 550, scr_h - 150, 500, 100, self.screen, self.go_to_store, [], "Go To Store"))
        self.buttons.append(FuncButton(50, scr_h - 150, 500, 100, self.screen, self.set_screen, ["game"], "Return to Game"))
        self.buttons.append(FuncButton(scr_w / 2 - 250, scr_h - 150, 500, 100, self.screen, self.set_screen, ["main_menu"], "Main Menu",))
        self.buttons.append(FuncButton(50, 50, 500, 100, self.screen, self.quit, [], "Quit Game"))
        self.buttons.append(FuncButton(50, scr_h - 300, 500, 100, self.screen, self.set_screen, ["zombiepedia"], "View Zombiepedia"))
        self.buttons.append(SelectSettingsScreen(scr_w / 2 - 400, scr_h * 0.3, 800, scr_h * 0.3, self.screen, self.set_screen, self.settings_screens))

    def quit(self):
        pg.event.post(pg.event.Event(pg.QUIT))

    def go_to_store(self):
        event_bus.add_event("game_event_bus", {"reset": {}})
        self.set_screen("store")

    def update(self):
        self.go2 = self.page_name
        self.screen.fill((100, 100, 100))
        self.settings_text.update(self.screen)
        self.get_input()
        for button in self.buttons:
            button.update()
        return self.go2

class SelectSettingsScreen(Button):
    def __init__(self, x: int, y: int, width: int, height: int, screen: pg.Surface, func, settings_screens):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.screen = screen
        self.scroll_index = 0
        self.func = func
        self.settings_screens = settings_screens
        self.settings_text = []
        for screen in self.settings_screens:
            self.settings_text.append(Text(screen.upper().replace("_", " "), 60, self.screen.get_width() / 2, 0, align="CENTER"))

    def update(self, **_):
        pg.draw.rect(self.screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 10)
        for i in range(self.scroll_index, min(self.scroll_index + round((self.height - 50) / 60), len(self.settings_screens))):
            self.settings_text[i].update_pos(self.screen.get_width() / 2, self.y + 50 + (i - self.scroll_index) * 60)
            self.settings_text[i].update(self.screen)

    def click(self, _, mouse_y, button):
        if button == 1:
            area_clicked = int((mouse_y - self.y - 20) / 60) + self.scroll_index
            if area_clicked >= 0 and area_clicked < len(self.settings_screens):
                self.func(self.settings_screens[area_clicked])

    def scroll(self, scroll):
        if scroll and self.scroll_index < len(self.settings_screens) - 1:
            self.scroll_index += 1
        elif not scroll and self.scroll_index > 0:
            self.scroll_index -= 1


@dataclass
class SettingsData:
    key_map: dict
    player_key_map: dict = field(default_factory=dict)
