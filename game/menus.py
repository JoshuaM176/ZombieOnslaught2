import pygame as pg
from util.event_bus import event_bus
from util.ui_objects import text, Button, check_buttons
from registries.weapon_registries import WeaponRegistry, EquippedWeaponRegistry
from game.screenpage import ScreenPage

class MainMenu():
    def __init__(self, screen: pg.Surface):
        self.screen = screen

    def update(self):
        self.screen.fill(color=(0, 100, 0))
        input_bus = event_bus.get_events("input_bus")
        for input in input_bus:
            return "game"
        return "main_menu"
    
class Store(ScreenPage):
    def __init__(self, screen: pg.Surface, weapon_registry: WeaponRegistry, equipped_weapons: EquippedWeaponRegistry, game_info):
        super().__init__(screen, "store")
        self.weapon_registry = weapon_registry
        self.game_info = game_info
        self.equipped_weapons = equipped_weapons
        self.category = "smg"
        self.weapon = None
        self.ui_buttons = []
        self.weapon_buttons = []
        self.buttons = [self.ui_buttons, self.weapon_buttons]
        self.set_weapon_buttons()
        self.select_weapon(self.weapon_registry.get_weapon("smg", "MP7"))
        self.ui_buttons.append(self.BuyOrEquip(self.screen.get_width()/2-100, 150, 200, 100, self.screen, self.weapon, self.buy_or_equip_selected))
        
        

    def get_input(self):
        mouse_x, mouse_y = pg.mouse.get_pos()
        input_bus = event_bus.get_events("input_bus")

        for event in input_bus:
            match event.type:
                case pg.MOUSEBUTTONUP:
                    temp = []
                    for button in self.buttons:
                        temp += button
                    check_buttons(mouse_x, mouse_y, temp)

    def update(self):
        self.get_input()
        self.screen.fill(color=(100, 200, 100))
        text(self.screen, self.category.upper(), 50, self.screen.get_width()/2, 50, align="CENTER")
        text(self.screen, self.weapon["name"], 40, self.screen.get_width()/2, 100, align="CENTER")
        text(self.screen, f"${round(self.game_info.money)}", 30, 25, 25)
        for button in self.weapon_buttons:
            button.update()
        self.ui_buttons[0].update(self.weapon)
        return self.go2

    def set_weapon_buttons(self):
        self.weapon_buttons.clear()
        available_weapons = self.weapon_registry.get_available_weapons(self.category)
        available_weapons.sort(key=lambda weapon: weapon["store"]["price"])
        x = 50
        y = 450
        for weapon in available_weapons:
            self.weapon_buttons.append(self.WeaponButton(x, y, 100, 100, self.screen, weapon, self.select_weapon))
            x += 150
            if x > 1000:
                x = 50
                y += 150

    def select_weapon(self, weapon):
        self.weapon = weapon

    def buy_or_equip_selected(self):
        if self.weapon["player"]["owned"]:
            self.equipped_weapons.equip(self.weapon, self.category)
        elif self.game_info.money >= self.weapon["store"]["price"]:
            self.game_info.money -= self.weapon["store"]["price"]
            self.weapon["player"]["owned"] = True

    class WeaponButton(Button):
        def __init__(self, x, y, width, height, screen, weapon, func):
            self.func = func
            self.weapon_dict = weapon
            self.weapon = pg.sprite.Sprite()
            self.weapon.sprite = weapon["weapon"]["sprites"]["default"]
            self.weapon.rect = weapon["weapon"]["sprites"]["default"].get_rect()
            self.weapon.rect.topleft = (x + weapon["store"]["shiftX"], y + weapon["store"]["shiftY"])
            self.price = weapon["store"]["price"]
            super().__init__(x, y, width, height, screen)

        def click(self):
            self.func(self.weapon_dict)

        def update(self):
            if not self.weapon_dict["player"]["owned"]:
                pg.draw.rect(self.screen, (100, 50, 50), (self.x, self.y, self.width, self.height), 0)
            pg.draw.rect(self.screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 10)
            self.screen.blit(self.weapon.sprite, self.weapon.rect)

    class BuyOrEquip(Button):
        def __init__(self, x, y, width, height, screen, weapon, func):
            self.func = func
            self.weapon = weapon
            super().__init__(x, y, width, height, screen)

        def click(self):
            self.func()

        def update(self, weapon):
            self.weapon = weapon
            pg.draw.rect(self.screen, (0, 100, 0), (self.x, self.y, self.width, self.height), 10, 10)
            if self.weapon["player"]["owned"]:
                text(self.screen, "Equip", 50, self.x + self.width/2, self.y + self.height/2, align="CENTER")
            else:
                text(self.screen, "Buy", 50, self.x + self.width/2, self.y + self.height/2, align="CENTER")

class GameOver(ScreenPage):
    def __init__(self, screen: pg.Surface):
        super().__init__(screen, "game_over")
        self.buttons = []
        self.buttons.append(FuncButton(self.screen.get_width()/2 + 100, 300, 500, 100, self.screen, self.set_screen, ["store"], "Go To Store"))
        self.buttons.append(FuncButton(self.screen.get_width()/2 - 600, 300, 500, 100, self.screen, self.set_screen, ["game"], "Play Again"))

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
        text(self.screen, "GAME OVER!", 100, self.screen.get_width()/2, 100, align = "CENTER")
        self.get_input()
        for button in self.buttons:
            button.update()
        return self.go2

    def set_screen(self, go2: str):
        self.go2 = go2

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
        text(self.screen, f"Money: {self.data.get("money"):.0f}", 30, 25, scr_height-215)

class FuncButton(Button):
    def __init__(self, x, y, width, height, screen, func, args, text, text_kwargs: dict = {}):
        super().__init__(x, y, width, height, screen)
        self.func = func
        self.args = args
        self.text = text
        self.text_kwargs = {"text": text, "x": self.x+self.width/2, "y": self.y+self.height/2, "size": 50, "align": "CENTER"}
        self.text_kwargs.update(text_kwargs)

    def click(self):
        self.func(*self.args)

    def update(self):
        pg.draw.rect(self.screen, (0,0,0),(self.x,self.y,self.width,self.height),10)
        text(self.screen, **self.text_kwargs)