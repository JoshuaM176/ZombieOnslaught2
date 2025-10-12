import pygame as pg
from util.ui_objects import Text, Button, FuncButton, ButtonContainer
from game.screenpage import ScreenPage
from registries.weapon_registries import (
    WeaponRegistry,
    EquippedWeaponRegistry,
    weapon_categories,
)
from util.resource_loading import load_sprite
from util.event_bus import event_bus

player_sprite = load_sprite("player.png", "player", -1)


class Store(ScreenPage, ButtonContainer):
    def __init__(
        self,
        screen: pg.Surface,
        weapon_registry: WeaponRegistry,
        equipped_weapons: EquippedWeaponRegistry,
        game_info,
    ):
        self.weapon_registry = weapon_registry
        self.game_info = game_info
        self.equipped_weapons = equipped_weapons
        self.category = "smg"
        self.weapon = None
        self.weapon_sprite = None
        self.weapon_buttons = []
        self.reload_type = {0: "Full", 1: "Single"}
        super().__init__(screen, "store")
        self.select_weapon(self.weapon_registry.get_weapon("smg", "MP7"))

    def __screen_init__(self):
        self.ui_buttons = []
        self.text = []
        scr_w = self.screen.get_width()
        scr_h = self.screen.get_height()
        self.ui_buttons.append(self.BuyOrEquip(scr_w / 2 - 100, 120, 200, 100, self.screen, self.weapon, self.buy_or_equip_selected))
        self.ui_buttons.append(FuncButton(scr_w - 550, scr_h - 150, 500, 100, self.screen, self.return_to_game, [], "Return to Game"))
        self.ui_buttons.append(FuncButton(scr_w / 2 + 100, 50, 50, 50, self.screen, self.next_page, [], ">"))
        self.ui_buttons.append(FuncButton(scr_w / 2 - 150, 50, 50, 50, self.screen, self.prev_page, [], "<"))
        self.set_weapon_buttons()
        self.category_text = Text(self.category.upper(), 50, scr_w / 2, 50, align="CENTER")
        self.weapon_text = Text("", 40, scr_w / 2, 100, align="CENTER")
        self.money_text = Text(f"${round(self.game_info.money)}", 30, 25, 25)
        self.price_text = Text("$0", 25, scr_w / 2 + 100, 160)
        self.requirement_text = Text("Requirements", 25, scr_w / 2, 130, align="CENTER")
        self.requirements_text = []
        self.stat_text = Text("Stats", 30, scr_w / 2, 240, align="CENTER")
        self.stats_text = []
        self.text += [self.category_text, self.weapon_text, self.money_text, self.stat_text]

    def return_to_game(self):
        self.set_screen("game")
        event_bus.add_event("game_event_bus", {"save_game": {}})

    def next_page(self):
        if weapon_categories.index(self.category) < len(weapon_categories) - 1:
            self.category = weapon_categories[weapon_categories.index(self.category) + 1]
        self.set_weapon_buttons()
        self.select_weapon(
            self.weapon_registry.get_weapon(self.category, self.weapon_registry.get_available_weapons(self.category)[0]["name"]))
        self.category_text.update_text(self.category.upper())

    def prev_page(self):
        if weapon_categories.index(self.category) > 0:
            self.category = weapon_categories[
                weapon_categories.index(self.category) - 1]
        self.set_weapon_buttons()
        self.select_weapon(
            self.weapon_registry.get_weapon(self.category, self.weapon_registry.get_available_weapons(self.category)[0]["name"]))
        self.category_text.update_text(self.category.upper())

    def update(self):
        if self.go2 != self.page_name:
            self.money_text.update_text(f"${round(self.game_info.money)}")
        self.go2 = self.page_name
        self.get_input()
        self.screen.fill(color=(100, 200, 100))
        for text in self.text:
            text.update(self.screen)
        for button in self.weapon_buttons:
            button.update()
        if self.weapon["player"]["owned"]:
            self.ui_buttons[0].update(self.weapon)
        elif self.weapon_registry.check_requirements(self.category, self.weapon["name"]):
            self.ui_buttons[0].update(self.weapon)
            self.price_text.update(self.screen)
        else:
            self.requirement_text.update(self.screen)
            for req in self.requirements_text:
                req.update(self.screen)
        self.ui_buttons[1].update()
        self.ui_buttons[2].update()
        self.ui_buttons[3].update()
        for stat in self.stats_text:
            stat.update(self.screen)
        equipped_weapon = self.equipped_weapons.get(self.category)
        if equipped_weapon:
            self.screen.blit(player_sprite, (50, 60, 50, 50))
            self.screen.blit(equipped_weapon.sprites["default"], (50 + equipped_weapon.properties.shiftX, 60 + equipped_weapon.properties.shiftY, 50, 50))
        return self.go2

    def set_weapon_buttons(self):
        self.weapon_buttons.clear()
        available_weapons = self.weapon_registry.get_available_weapons(self.category)
        available_weapons.sort(key=lambda weapon: weapon["store"]["total_cost"])
        x = 50
        y = 480
        for weapon in available_weapons:
            self.weapon_buttons.append(
                self.WeaponButton(x, y, 110, 110, self.screen, weapon, self.select_weapon, self.weapon_registry.check_requirements(self.category, weapon["name"])))
            x += 150
            if x > self.screen.get_width() - 100:
                x = 50
                y += 150
        self.buttons = self.ui_buttons + self.weapon_buttons

    def select_weapon(self, weapon):
        self.weapon = weapon
        self.weapon_text.update_text(self.weapon["name"])
        self.price_text.update_text(f"${self.weapon["store"]["price"]}")
        y = 0
        self.requirements_text = []
        for req in self.weapon["store"]["requirements"]:
            self.requirements_text.append(Text(req["name"], 25, self.screen.get_width() / 2, y + 155, align = "CENTER"))
            y += 25
        self.set_stats()

    def set_stats(self):
        self.stats_text = []
        x = -300
        y = 255
        stats = [
            f"Damage: {self.weapon['projectile']['damage'] * self.weapon['properties']['projectile_count']}",
            f"Dropoff: {self.weapon['projectile']['dropoff'] * self.weapon['properties']['projectile_count']}",
            f"Firerate: {self.weapon['properties']['firerate']}",
            f"Headshot Damage: {self.weapon['projectile']['head_mult']}",
            f"Reload Time: {self.weapon['ammo']['reload_time']}(+{self.weapon['ammo']['reload_on_empty']})",
            f"Ammo Capacity: {self.weapon['ammo']['bullets']}",
            f"Bullet in Chamber: {self.weapon['ammo']['bullet_in_chamber']}",
            f"Projectile Speed: {self.weapon['projectile']['speed']}",
            f"Bullet Penetration: {round(self.weapon['projectile']['penetration'] * 100)}%",
            f"Movement Speed: {self.weapon['player']['movement']}",
            f"Recoil {self.weapon['properties']['recoil_per_shot'] * 100}",
            f"Recoil Control {self.weapon['properties']['recoil_control'] * 100}",
            f"Max Recoil: {self.weapon['properties']['max_recoil'] * 100}",
            f"Magazines: {self.weapon['ammo']['mags']}",
            f"Resupply Time: {self.weapon['ammo']['mag_time']}",
            f"Reload Type: {self.reload_type[self.weapon['ammo']['reload_type']]}"
        ]
        if self.weapon['properties']['burst'] > 1:
            stats.append(f"Fire Type: Burst-{self.weapon['properties']['burst']}")
            stats.append(f"Burst Delay: {self.weapon['properties']['burst_delay']}")
        elif self.weapon['properties']['burst'] == 1:
            stats.append("Fire Type: Semi-Automatic")
        else:
            stats.append("Fire Type: Automatic")
        for stat in stats:
            self.stats_text.append(Text(stat, 25, self.screen.get_width()/2 + x, y))
            y += 25
            if y > 475:
                y = 255
                x += 350

    def buy_or_equip_selected(self):
        if self.weapon["player"]["owned"]:
            self.equipped_weapons.equip(self.weapon, self.category)
        elif self.game_info.money >= self.weapon["store"]["price"] and self.weapon_registry.check_requirements(self.category, self.weapon["name"]):
            self.game_info.money -= self.weapon["store"]["price"]
            event_bus.add_event("ui_bus", {"money": self.game_info.money})
            self.weapon["player"]["owned"] = True
            self.set_weapon_buttons()
        self.money_text.update_text(f"${round(self.game_info.money)}")

    class WeaponButton(Button):
        def __init__(self, x, y, width, height, screen, weapon, func, reqs_met):
            self.func = func
            self.weapon_dict = weapon
            self.weapon = pg.sprite.Sprite()
            self.weapon.sprite = weapon["sprites"]["default"]
            self.weapon.rect = weapon["sprites"]["default"].get_rect()
            self.weapon.rect.topleft = (x + weapon["store"]["shiftX"],y + weapon["store"]["shiftY"])
            self.price = weapon["store"]["price"]
            self.reqs_met = reqs_met
            super().__init__(x, y, width, height, screen)

        def click(self, x, y, button):
            if button == 1:
                self.func(self.weapon_dict)

        def update(self):
            if not self.weapon_dict["player"]["owned"]:
                if self.reqs_met:
                    pg.draw.rect(self.screen, (100, 100, 100), (self.x, self.y, self.width, self.height), 0)
                else:
                    pg.draw.rect(self.screen, (100, 20, 20), (self.x, self.y, self.width, self.height), 0)
            pg.draw.rect(self.screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 10)
            self.screen.blit(self.weapon.sprite, self.weapon.rect)

    class BuyOrEquip(Button):
        def __init__(self, x, y, width, height, screen, weapon, func):
            super().__init__(x, y, width, height, screen)
            self.func = func
            self.weapon = weapon
            self.text = Text("", 50, self.x + self.width / 2, self.y + self.height / 2, align = "CENTER")

        def click(self, x, y, button):
            if button == 1:
                self.func()

        def update(self, weapon):
            self.weapon = weapon
            pg.draw.rect(self.screen, (0, 100, 0), (self.x, self.y, self.width, self.height), 10, 10)
            if weapon["player"]["owned"] != self.text.text:
                if weapon["player"]["owned"]:
                    self.text.update_text("Equip")
                else:
                    self.text.update_text("Buy")
            self.text.update(self.screen)
