from util.resource_loading import ResourceLoader, load_sprite
from objects.weapons import Weapon
import pygame as pg
# Fire animation length needs added back to json


def convert_files_to_sprites(resource: dict):
    for key, value in resource.items():
        if isinstance(value, list):
            for item in range(len(value)):
                value[item] = load_sprite(value[item], "weapons", -1)
        else:
            resource[key] = load_sprite(resource[key], "weapons", -1)
    return resource


class WeaponRegistry:
    def __init__(self):
        self.weapons: dict[str, list[dict]] = {"melee": [], "smg": []}
        self.render_plain = pg.sprite.RenderPlain(())
        resource_loader = ResourceLoader("weapons", "attributes")
        resource_loader.load_all()
        resource_loader.set_defaults()
        resources = resource_loader.get_all()
        for key, value in resources.items():
            value["weapon"]["sprites"] = convert_files_to_sprites(
                value["weapon"]["sprites"]
            )
            weapon = {"name": key}
            weapon.update(resources[key])
            self.weapons[value["weapon"]["type"]].append(weapon)

    def get_default_weapons(self) -> dict[str, dict]:
        defaults = {}
        for cat, weapons in self.weapons.items():
            for weapon in weapons:
                if weapon["player"].get("default"):
                    defaults[cat] = weapon
        return defaults


class CustomWeaponRegistry:
    def __init__(self):
        self.weapons: dict[str, list[Weapon]] = {"melee": [], "smg": []}

    def add_weapon(self, weapon: Weapon, cat: str):
        self.weapons[cat].append(weapon)

    def get(self, cat: str):
        return self.weapons.get(cat)


class EquippedWeaponRegistry:
    def __init__(self, bullet_registry):
        self.bullet_registry = bullet_registry
        self.weapons: dict[str, Weapon] = {}
        self.equipped_list: list = ["melee", "smg"]
        self.equipped = "smg"
        self.render_plain = pg.sprite.RenderPlain(())

    def equip(self, weapon: dict, cat: str):
        self.equipped = cat
        self.weapons[cat] = Weapon(**weapon, bullet_registry=self.bullet_registry)

    def get(self, cat: str):
        return self.weapons.get(cat)

    def set_next(self):
        if self.equipped_list.index(self.equipped) < len(self.equipped_list) - 1:
            self.equipped = self.equipped_list[
                self.equipped_list.index(self.equipped) + 1
            ]
            return self.equipped
        return False

    def set_previous(self):
        if self.equipped_list.index(self.equipped) > 0:
            self.equipped = self.equipped_list[
                self.equipped_list.index(self.equipped) - 1
            ]
            return self.equipped
        return False

    def get_next(self):
        if self.equipped_list.index(self.equipped) < len(self.equipped_list) - 1:
            return self.equipped_list[self.equipped_list.index(self.equipped) + 1]
        return False

    def get_previous(self):
        if self.equipped_list.index(self.equipped) > 0:
            return self.equipped_list[self.equipped_list.index(self.equipped) - 1]
        return False

    def update(self, frame_time):
        for _, weapon in self.weapons.items():
            weapon.update(frame_time)
