import pygame as pg
from util.event_bus import event_bus
from util.ui_objects import text, Button, FuncButton, ButtonContainer
from game.screenpage import ScreenPage
from registries.weapon_registries import (
    WeaponRegistry,
    EquippedWeaponRegistry,
    weapon_categories,
)
from util.resource_loading import load_sprite

player_sprite = load_sprite("player.png", "player", -1)


class Store(ScreenPage, ButtonContainer):
    def __init__(
        self,
        screen: pg.Surface,
        weapon_registry: WeaponRegistry,
        equipped_weapons: EquippedWeaponRegistry,
        game_info,
    ):
        super().__init__(screen, "store")
        self.weapon_registry = weapon_registry
        self.game_info = game_info
        self.equipped_weapons = equipped_weapons
        self.category = "smg"
        self.weapon = None
        self.weapon_sprite = None
        self.ui_buttons = []
        self.weapon_buttons = []
        self.select_weapon(self.weapon_registry.get_weapon("smg", "MP7"))
        self.set_weapon_buttons()
        self.ui_buttons.append(
            self.BuyOrEquip(
                self.screen.get_width() / 2 - 100,
                120,
                200,
                100,
                self.screen,
                self.weapon,
                self.buy_or_equip_selected,
            )
        )
        self.ui_buttons.append(
            FuncButton(
                self.screen.get_width() - 100,
                self.screen.get_height() - 100,
                50,
                50,
                self.screen,
                self.set_screen,
                ["game"],
                "X",
            )
        )
        self.ui_buttons.append(
            FuncButton(
                self.screen.get_width() / 2 + 100,
                50,
                50,
                50,
                self.screen,
                self.next_page,
                [],
                ">",
            )
        )
        self.ui_buttons.append(
            FuncButton(
                self.screen.get_width() / 2 - 150,
                50,
                50,
                50,
                self.screen,
                self.prev_page,
                [],
                "<",
            )
        )
        self.reload_type = {0: "Full", 1: "Single"}
        self.buttons = self.ui_buttons + self.weapon_buttons

    def next_page(self):
        if weapon_categories.index(self.category) < len(weapon_categories) - 1:
            self.category = weapon_categories[
                weapon_categories.index(self.category) + 1
            ]
        self.set_weapon_buttons()
        self.select_weapon(
            self.weapon_registry.get_weapon(
                self.category,
                self.weapon_registry.get_available_weapons(self.category)[0]["name"],
            )
        )

    def prev_page(self):
        if weapon_categories.index(self.category) > 0:
            self.category = weapon_categories[
                weapon_categories.index(self.category) - 1
            ]
        self.set_weapon_buttons()
        self.select_weapon(
            self.weapon_registry.get_weapon(
                self.category,
                self.weapon_registry.get_available_weapons(self.category)[0]["name"],
            )
        )

    def get_input(self):
        mouse_x, mouse_y = pg.mouse.get_pos()
        input_bus = event_bus.get_events("input_bus")

        for event in input_bus:
            self.check_buttons(event, mouse_x, mouse_y)

    def update(self):
        self.go2 = self.page_name
        self.get_input()
        self.screen.fill(color=(100, 200, 100))
        text(
            self.screen,
            self.category.upper(),
            50,
            self.screen.get_width() / 2,
            50,
            align="CENTER",
        )
        text(
            self.screen,
            self.weapon["name"],
            40,
            self.screen.get_width() / 2,
            100,
            align="CENTER",
        )
        text(self.screen, f"${round(self.game_info.money)}", 30, 25, 25)
        for button in self.weapon_buttons:
            button.update()
        if self.weapon["player"]["owned"]:
            self.ui_buttons[0].update(self.weapon)
        elif self.weapon_registry.check_requirements(
            self.category, self.weapon["name"]
        ):
            self.ui_buttons[0].update(self.weapon)
            text(
                self.screen,
                f"${self.weapon['store']['price']}",
                25,
                self.screen.get_width() / 2 + 100,
                160,
            )
        else:
            y = 0
            text(
                self.screen,
                "Requirements",
                25,
                self.screen.get_width() / 2,
                130,
                align="CENTER",
            )
            for req in self.weapon["store"]["requirements"]:
                text(
                    self.screen,
                    req["name"],
                    25,
                    self.screen.get_width() / 2,
                    y + 155,
                    align="CENTER",
                )
                y += 25
        self.ui_buttons[1].update()
        self.ui_buttons[2].update()
        self.ui_buttons[3].update()
        text(self.screen, "Stats", 30, self.screen.get_width() / 2, 240, align="CENTER")
        self.stats(
            [
                f"Damage: {self.weapon['bullet']['damage']}",
                f"Dropoff: {self.weapon['bullet']['dropoff']}",
                f"Firerate: {self.weapon['weapon']['firerate']}",
                f"Headshot Damage: {self.weapon['bullet']['head_mult']}",
                f"Reload Time: {self.weapon['ammo']['reload_time']}(+{self.weapon['ammo']['reload_on_empty']})",
                f"Ammo Capacity: {self.weapon['ammo']['bullets']}",
                f"Bullet in Chamber: {self.weapon['ammo']['bullet_in_chamber']}",
                f"Bullet Speed: {self.weapon['bullet']['speed']}",
                f"Bullet Penetration: {self.weapon['bullet']['penetration'] * 100}%",
                f"Movement Speed: {self.weapon['player']['movement']}",
                f"Recoil {self.weapon['weapon']['recoil_per_shot'] * 100}",
                f"Recoil Control {self.weapon['weapon']['recoil_control'] * 100}",
                f"Max Recoil: {self.weapon['weapon']['max_recoil'] * 100}",
                f"Magazines: {self.weapon['ammo']['mags']}",
                f"Resupply Time: {self.weapon['ammo']['mag_time']}",
                f"Reload Type: {self.reload_type[self.weapon['ammo']['reload_type']]}",
            ]
        )
        equipped_weapon = self.equipped_weapons.get(self.category)
        if equipped_weapon:
            self.screen.blit(player_sprite, (50, 60, 50, 50))
            self.screen.blit(
                equipped_weapon.sprites["default"],
                (50 + equipped_weapon.shiftX, 60 + equipped_weapon.shiftY, 50, 50),
            )
        return self.go2

    def stats(self, stats: list):
        x = -300
        y = 255
        for stat in stats:
            text(self.screen, stat, 25, self.screen.get_width() / 2 + x, y)
            y += 25
            if y > 450:
                y = 255
                x += 350

    def set_weapon_buttons(self):
        self.weapon_buttons.clear()
        available_weapons = self.weapon_registry.get_available_weapons(self.category)
        available_weapons.sort(key=lambda weapon: weapon["store"]["total_cost"])
        x = 50
        y = 450
        for weapon in available_weapons:
            self.weapon_buttons.append(
                self.WeaponButton(
                    x,
                    y,
                    100,
                    100,
                    self.screen,
                    weapon,
                    self.select_weapon,
                    self.weapon_registry.check_requirements(
                        self.category, weapon["name"]
                    ),
                )
            )
            x += 150
            if x > 1000:
                x = 50
                y += 150
        self.buttons = self.ui_buttons + self.weapon_buttons

    def select_weapon(self, weapon):
        self.weapon = weapon

    def buy_or_equip_selected(self):
        if self.weapon["player"]["owned"]:
            self.equipped_weapons.equip(self.weapon, self.category)
        elif self.game_info.money >= self.weapon["store"][
            "price"
        ] and self.weapon_registry.check_requirements(
            self.category, self.weapon["name"]
        ):
            self.game_info.money -= self.weapon["store"]["price"]
            self.weapon["player"]["owned"] = True
            self.set_weapon_buttons()

    class WeaponButton(Button):
        def __init__(self, x, y, width, height, screen, weapon, func, reqs_met):
            self.func = func
            self.weapon_dict = weapon
            self.weapon = pg.sprite.Sprite()
            self.weapon.sprite = weapon["weapon"]["sprites"]["default"]
            self.weapon.rect = weapon["weapon"]["sprites"]["default"].get_rect()
            self.weapon.rect.topleft = (
                x + weapon["store"]["shiftX"],
                y + weapon["store"]["shiftY"],
            )
            self.price = weapon["store"]["price"]
            self.reqs_met = reqs_met
            super().__init__(x, y, width, height, screen)

        def click(self, x, y):
            self.func(self.weapon_dict)

        def update(self):
            if not self.weapon_dict["player"]["owned"]:
                if self.reqs_met:
                    pg.draw.rect(
                        self.screen,
                        (100, 100, 100),
                        (self.x, self.y, self.width, self.height),
                        0,
                    )
                else:
                    pg.draw.rect(
                        self.screen,
                        (100, 20, 20),
                        (self.x, self.y, self.width, self.height),
                        0,
                    )
            pg.draw.rect(
                self.screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 10
            )
            self.screen.blit(self.weapon.sprite, self.weapon.rect)

    class BuyOrEquip(Button):
        def __init__(self, x, y, width, height, screen, weapon, func):
            self.func = func
            self.weapon = weapon
            super().__init__(x, y, width, height, screen)

        def click(self, *_):
            self.func()

        def update(self, weapon):
            self.weapon = weapon
            pg.draw.rect(
                self.screen,
                (0, 100, 0),
                (self.x, self.y, self.width, self.height),
                10,
                10,
            )
            if self.weapon["player"]["owned"]:
                text(
                    self.screen,
                    "Equip",
                    50,
                    self.x + self.width / 2,
                    self.y + self.height / 2,
                    align="CENTER",
                )
            else:
                text(
                    self.screen,
                    "Buy",
                    50,
                    self.x + self.width / 2,
                    self.y + self.height / 2,
                    align="CENTER",
                )
