from util.event_bus import event_bus
import pygame as pg
from util.ui_objects import Text, ButtonContainer, Button, FuncButton
from util.resource_loading import ROOT, set_save_profile, delete_save_profile
from pathlib import Path
from game.screenpage import ScreenPage

saves = list(Path(ROOT, "saves").glob("*"))
save_names = [file.name for file in saves]


class MainMenu(ScreenPage, ButtonContainer):
    def __init__(self, screen: pg.Surface):
        self.profile = save_names.index("default")
        self.typed_input = ""
        self.creating_profile = False
        self.deleting_profile = False
        super().__init__(screen, "main_menu")

    def __screen_init__(self):
        self.buttons = []
        self.texts  = []
        scr_w = self.screen.get_width()
        scr_h = self.screen.get_height()
        self.select_save_button = SelectSaveButton(scr_w / 2 - 300, scr_h * 0.3, 600, scr_h * 0.3, self.screen, self.set_profile, self.deleting_profile, self.profile)
        self.buttons.append(self.select_save_button)
        self.buttons.append(FuncButton(scr_w / 2 - 250, scr_h - 150, 500, 100, self.screen, self.set_screen, ["game"], "Start Game"))
        self.buttons.append(FuncButton(scr_w / 2 - 250, scr_h * 0.7, 500, 100, self.screen, self.select_create_profile, [], "Create Profile"))
        self.buttons.append(DeleteProfileButton(scr_w / 2 + 325, scr_h * 0.35, 300, 150, self.screen, self.delete_profile, [], "Delete Profile", {"size": 35}))
        self.texts.append(Text("Zombie Onslaught", 100, scr_w / 2, 100, align="CENTER"))
        self.profile_text = Text(f"Profile: {save_names[self.profile].upper()}", 75, scr_w / 2, scr_h / 5, align = "CENTER")
        self.typed_input_display = Text(f"|{self.typed_input}", round(min(75, scr_h / 15)), scr_w / 2, scr_h * 0.65, align = "CENTER")
        self.texts += [self.profile_text]

    def update(self):
        self.go2 = self.page_name
        self.screen.fill(color=(0, 100, 0))
        for text in self.texts:
            text.update(self.screen)
        for button in self.buttons:
            button.update(deleting_profile=self.deleting_profile, selected_profile=self.profile)
        self.get_input()
        if self.creating_profile:
            self.typed_input_display.update(self.screen)
        return self.go2

    def get_input(self):
        mouse_x, mouse_y = pg.mouse.get_pos()
        input_bus = event_bus.get_events("input_bus")
        for event in input_bus:
            self.check_buttons(event, mouse_x, mouse_y)
            if event.type == pg.KEYDOWN:
                self.keyboard_input(event)

    def select_create_profile(self):
        self.typed_input = ""
        self.creating_profile = True

    def create_profile(self, profile_name):
        save_names.append(profile_name)
        self.set_profile(len(save_names) - 1)

    def set_profile(self, profile):
        self.deleting_profile = False
        self.profile = profile
        set_save_profile(save_names[profile])
        self.profile_text.update_text(save_names[profile].upper())
        self.select_save_button.update_profiles(self.deleting_profile, self.profile)

    def delete_profile(self):
        if self.deleting_profile and save_names[self.profile] != "default":
            delete_save_profile(save_names[self.profile])
            self.deleting_profile = False
            save_names.pop(self.profile)
            if self.profile > 0:
                self.set_profile(self.profile-1)
            else:
                self.set_profile(self.profile)
            set_save_profile(save_names[self.profile])
            self.profile_text.update_text(save_names[self.profile].upper())
        else:
            self.deleting_profile = True

    def keyboard_input(self, event):
        match event.key:
            case pg.K_BACKSPACE:
                self.typed_input = self.typed_input[:-1]
            case pg.K_ESCAPE:
                self.typed_input = ""
                self.creating_profile = False
            case pg.K_RETURN:
                if self.creating_profile:
                    self.create_profile(self.typed_input)
                    self.creating_profile = False
                self.typed_input = ""
            case _:
                self.typed_input += event.unicode
        self.typed_input_display.update_text(self.typed_input)


class SelectSaveButton(Button):
    def __init__(self, x, y, width, height, screen, func, deleting_profile, selected_profile):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.screen = screen
        self.scroll_index = 0
        self.func = func
        self.update_profiles(deleting_profile, selected_profile)

    def update_profiles(self, deleting_profile, selected_profile, **_):
        self.profiles_text = []
        for profile in save_names:
            if deleting_profile and profile == save_names[selected_profile]:
                self.profiles_text.append(Text(profile.upper(), 60, self.screen.get_width() / 2, 0, color = (100, 0, 0), align="CENTER"))
            else:
                self.profiles_text.append(Text(profile.upper(), 60, self.screen.get_width() / 2, 0, align="CENTER")) 

    def update(self, **_):
        pg.draw.rect(self.screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 10)
        for i in range(self.scroll_index, min(self.scroll_index + round((self.height - 50) / 60), len(save_names))):
            self.profiles_text[i].update_pos(self.screen.get_width() / 2, self.y + 50 + (i - self.scroll_index) * 60)
            self.profiles_text[i].update(self.screen)

    def click(self, _, mouse_y, mouse_button):
        if mouse_button == 1:
            area_clicked = int((mouse_y - self.y - 20) / 60) + self.scroll_index
            if area_clicked >= 0 and area_clicked < len(save_names):
                self.func(area_clicked)

    def scroll(self, scroll):
        if scroll and self.scroll_index < len(save_names) - 1:
            self.scroll_index += 1
        elif not scroll and self.scroll_index > 0:
            self.scroll_index -= 1


class DeleteProfileButton(FuncButton):
    def update(self, deleting_profile, **kwargs):
        if deleting_profile:
            pg.draw.rect(self.screen, (100, 0, 0), (self.x, self.y, self.width, self.height), 10)
        else:
            pg.draw.rect(self.screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 10)
        self.text.update(self.screen)
