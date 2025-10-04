import pygame as pg
from game.screenpage import ScreenPage
from util.ui_objects import Text, ButtonContainer, Button, FuncButton
from util.event_bus import event_bus

class KeybindSettings(ScreenPage, ButtonContainer):
    def __init__(self, screen: pg.Surface, key_map):
        self.checked_exit = False
        self.player_key_map = {}
        self.key_map = key_map
        self.actions = [key for key in self.key_map.keys()]
        super().__init__(screen, "keybind_settings")
        self.save()

    def reset_key_bind_button(self):
        self.key_map.clear()
        for key, action in self.player_key_map.items():
            if action in self.key_map:
                self.key_map[action].append(key)
            else:
                self.key_map[action] = [key]
        for action in self.actions:
            if action not in self.key_map.keys():
                self.key_map[action] = [0]
        self.set_key_binds_button.update_key_map_text()

    def __screen_init__(self):
        self.buttons = []
        scr_w = self.screen.get_width()
        scr_h = self.screen.get_height()
        self.set_key_binds_button = SetKeyBindsButton(scr_w / 2 - 500,250,1000,800,self.screen,self.key_map,self.actions)
        self.exit_check_save_button = FuncButton(50, scr_h - 150, 550, 100, self.screen, self.exit_check_save, [], "Back")
        self.buttons += [self.set_key_binds_button, self.exit_check_save_button]
        self.buttons.append(FuncButton(scr_w - 550, scr_h - 150, 500, 100, self.screen, self.save, [], "Save"))

    def update(self):
        self.go2 = self.page_name
        self.screen.fill((100, 100, 100))
        self.get_input()
        for button in self.buttons:
            button.update()
        return self.go2
    
    def get_input(self):
        mouse_x, mouse_y = pg.mouse.get_pos()
        input_bus = event_bus.get_events("input_bus")
        for event in input_bus:
            self.check_buttons(event, mouse_x, mouse_y)
            if event.type == pg.KEYDOWN:
                self.keyboard_input(event)

    def keyboard_input(self, event):
        self.set_key_binds_button.key_press(event)

    def exit_check_save(self):
        if self.set_key_binds_button.saved:
            self.set_screen("settings")
            return
        elif self.checked_exit:
            self.set_screen("settings")
            self.checked_exit = False
            self.set_key_binds_button.saved = True
            self.exit_check_save_button.text.update_text("Back")
            self.reset_key_bind_button()
        else:
            self.checked_exit = True
            self.exit_check_save_button.text.update_text("Exit Without Saving?")


    def save(self):
        self.player_key_map.clear()
        for key, values in self.key_map.items():
            for value in values:
                self.player_key_map[value] = key
        self.reset_key_bind_button()
        self.set_key_binds_button.saved = True
        self.checked_exit = False
        self.exit_check_save_button.text.update_text("Back")
    

class SetKeyBindsButton(Button):
    def __init__(self, x: int, y: int, width: int, height: int, screen: pg.Surface, key_map, actions):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.screen = screen
        self.scroll_index = 0
        self.key_map = key_map
        self.actions = actions
        self.action_text = []
        self.key1_text = []
        self.key2_text = []
        self.update_key_map_text()
        self.action_selected = None
        self.key_selected = 0
        self.saved = True

    def update_key_map_text(self):
        self.key_name_map = {
            1073742049: "SHIFT",
            32: "_",
            0: ""
        }
        self.action_text = []
        self.key1_text = []
        self.key2_text = []
        for action in self.actions:
            values = self.key_map[action]
            self.action_text.append(Text(f"{action.upper()}:", 60, self.x, 0))
            key1 = self.key_name_map.get(values[0]) if self.key_name_map.get(values[0]) is not None else f"Mouse{values[0]}" if values[0] < 10 else chr(values[0])
            key2 = ""
            if len(values)>1:
                key2 = self.key_name_map.get(values[1]) if self.key_name_map.get(values[1]) is not None else f"Mouse{values[1]}" if values[1] < 10 else chr(values[1])
            self.key1_text.append(Text(f"{key1}", 60, self.x + 500, 0))
            self.key2_text.append(Text(f"{key2}", 60, self.x + 750, 0))

    def update(self, **_):
        if self.action_selected:
            if self.actions.index(self.action_selected) - self.scroll_index < 0:
                self.action_selected = None
            else:
                pg.draw.rect(
                self.screen, (100, 100, 0), (self.x + 500 + 250 * self.key_selected, self.y + (self.actions.index(self.action_selected) - self.scroll_index)*60 + 20, 250, 60)
                )
        pg.draw.rect(
            self.screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 10
        )
        pg.draw.line(self.screen, (0, 0, 0), (self.x + 750, self.y), (self.x + 750, self.y + self.height-5), 10)
        for i in range(
            self.scroll_index,
            min(self.scroll_index + round((self.height - 50) / 60), len(self.key_map)),
        ):
            self.action_text[i].update_pos(self.x + 10, self.y + 20 + (i - self.scroll_index) * 60)
            self.action_text[i].update(self.screen)
            self.key1_text[i].update_pos(self.x + 500, self.y + 20 + (i - self.scroll_index) * 60)
            self.key1_text[i].update(self.screen)
            self.key2_text[i].update_pos(self.x + 760, self.y + 20 + (i - self.scroll_index) * 60)
            self.key2_text[i].update(self.screen)

    def click(self, mouse_x, mouse_y, mouse_button):
        if self.action_selected is None:
            if mouse_button == 1:
                area_clicked = int((mouse_y - self.y - 20) / 60) + self.scroll_index
                key_selected = max(int((mouse_x - self.x - 500) / 250), 0)
                if area_clicked >= 0 and area_clicked < len(self.action_text):
                    self.action_selected = self.actions[area_clicked]
                    self.key_selected = key_selected
        else:
            keys = self.key_map[self.action_selected]
            if self.key_selected == 0:
                keys[0] = mouse_button
            elif len(keys)>1:
                keys[1] = mouse_button
            else:
                keys.append(mouse_button)
            self.update_key_map_text()
            self.action_selected = None
            self.saved = False

    def scroll(self, scroll):
        if not self.action_selected:
            if scroll and self.scroll_index < len(self.action_text) - 1:
                self.scroll_index += 1
            elif not scroll and self.scroll_index > 0:
                self.scroll_index -= 1

    def key_press(self, event):
        if event.key == 27:
            self.action_selected = None
            return
        if self.action_selected:
            keys = self.key_map[self.action_selected]
            if self.key_selected == 0:
                keys[0] = event.key
            elif len(keys)>1:
                keys[1] = event.key
            else:
                keys.append(event.key)
        self.update_key_map_text()
        self.action_selected = None
        self.saved = False
