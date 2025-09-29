from util.resource_loading import ResourceLoader, load_sprite
from objects.weapons import Weapon
import pygame as pg

weapon_categories = ["melee", "pistol", "smg", "rifle", "shotgun", "sniper"]


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
        self.weapons = {}
        for cat in weapon_categories:
            self.weapons.update({cat: {}})
        self.render_plain = pg.sprite.RenderPlain(())
        resource_loader = ResourceLoader("weapons", "attributes")
        resource_loader.load_all()
        resource_loader.set_defaults()
        resources = resource_loader.get_all()
        for name, data in resources.items():
            data["weapon"]["sprites"] = convert_files_to_sprites(
                data["weapon"]["sprites"]
            )
            weapon = {name: resources[name]}
            weapon[name].update({"name": name})
            self.weapons[data["weapon"]["type"]].update(weapon)
        self._calc_total_weapons_cost()

    def _calc_total_weapons_cost(self):
        for cat, weapons in self.weapons.items():
            for weapon, data in weapons.items():
                data["store"]["total_cost"] = self._calc_weapon_cost(cat, weapon, [])

    def _calc_weapon_cost(self, cat, name, visited):
        if name in visited:
            raise Exception(f"Circular dependency in requirements, {name} {cat}")
        visited.append(name)
        weapon = self.weapons[cat].get(name)
        if not weapon:
            print(f"{name} {cat} not found, skipping")
            return 0
        total_cost = weapon["store"]["price"]
        for req in weapon["store"]["requirements"]:
            if (req["type"]) == "weapon":
                total_cost += self._calc_weapon_cost(req["cat"], req["name"], visited)
        return total_cost

    def check_requirements(self, cat, name):
        weapon = self.weapons[cat][name]
        for req in weapon["store"]["requirements"]:
            if (req["type"]) == "weapon":
                if not self.weapons[req["cat"]][req["name"]]["player"]["owned"]:
                    return False
        return True

    def get_weapon(self, cat: str, name: str) -> dict:
        return self.weapons.get(cat).get(name)

    def get_default_weapons(self) -> dict[str, dict]:
        defaults = {}
        for cat, weapons in self.weapons.items():
            for weapon, data in weapons.items():
                if data["player"].get("default"):
                    defaults[cat] = data
        return defaults

    def get_available_weapons(self, cat) -> list[Weapon]:
        available = []
        for weapon, data in self.weapons[cat].items():
            if data["player"].get("available"):
                available.append(data)
        return available


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
        self.weapons = {}
        for cat in weapon_categories:
            self.weapons.update({cat: None})
        self.equipped_list: list = weapon_categories
        self.equipped = self.equipped_list[0]
        self.render_plain = pg.sprite.RenderPlain(())

    def equip(self, weapon: dict, cat: str):
        self.weapons[cat] = Weapon(
            **weapon, bullet_registry=self.bullet_registry, bus="ui_bus"
        )

    def get(self, cat: str):
        return self.weapons.get(cat)

    def set_next(self):
        next_cat = self.get_next()
        if self.weapons.get(next_cat):
            self.equipped = next_cat
            return self.equipped
        return False

    def set_previous(self):
        prev_cat = self.get_prev()
        if self.weapons.get(prev_cat):
            self.equipped = prev_cat
            return self.equipped
        return False

    def get_next(self):
        if self.equipped_list.index(self.equipped) < len(self.equipped_list) - 1:
            return self.equipped_list[self.equipped_list.index(self.equipped) + 1]
        return False

    def get_prev(self):
        if self.equipped_list.index(self.equipped) > 0:
            return self.equipped_list[self.equipped_list.index(self.equipped) - 1]
        return False

    def get_next_name(self):
        cat = self.get_next()
        if self.get(cat):
            return self.get(cat).name
        return False

    def get_prev_name(self):
        cat = self.get_prev()
        if self.get(cat):
            return self.get(cat).name
        return False

    def update(self, frame_time):
        for _, weapon in self.weapons.items():
            if weapon:
                weapon.update(frame_time)

    def reset(self):
        for _, weapon in self.weapons.items():
            if weapon:
                weapon.reset()
