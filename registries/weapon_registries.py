from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from data.weapons import WeaponCategory, WeaponData, WeaponPrevPurchaseRequirement
from objects.weapons import Weapon
from util.resource_loading import ResourceLoader

if TYPE_CHECKING:
    from registries import BulletRegistry


class WeaponRegistry:
    def __init__(self) -> None:
        self.weapons: dict[WeaponCategory, dict[str, WeaponData]] = {cat: {} for cat in WeaponCategory}
        self.render_plain = pg.sprite.RenderPlain(())
        resource_loader = ResourceLoader("weapons", "attributes")
        resource_loader.load_all()
        resource_loader.set_defaults()
        resources = resource_loader.get_all()
        for name, data in resources.items():
            data.update({"name": name})
            weapon = WeaponData(**data)
            category = weapon.properties.type
            self.weapons[category].update({name: weapon})

    def check_requirements(self, cat, name):
        weapon = self.weapons[cat][name]
        for req in weapon.store.requirements:
            if isinstance(req, WeaponPrevPurchaseRequirement):
                return self.weapons[req.cat][req.name].player.owned

    def get_weapon(self, cat: WeaponCategory, name: str) -> WeaponData:
        return self.weapons[cat][name]

    def get_default_weapons(self) -> dict[WeaponCategory, WeaponData]:
        defaults = {}
        for cat, weapons in self.weapons.items():
            for weapon in weapons.values():
                if weapon.player.default:
                    defaults[cat] = weapon
        return defaults

    def get_available_weapons(self, cat: WeaponCategory) -> list[WeaponData]:
        return [weapon for weapon in self.weapons[cat].values() if weapon.player.available]


class EquippedWeaponRegistry:
    def __init__(self, bullet_registry: BulletRegistry):
        self.bullet_registry = bullet_registry
        self.weapons: dict[str, Weapon | None] = {}
        for cat in WeaponCategory:
            self.weapons.update({cat: None})
        self.categories = list(WeaponCategory)
        self.equipped = self.categories[0]
        self.equipped_index = 0
        self.render_plain = pg.sprite.RenderPlain(())

    def equip(self, weapon: WeaponData, cat: str):
        self.weapons[cat] = Weapon(**weapon.model_dump(), projectile_registry=self.bullet_registry, bus="ui_bus")

    def get(self, cat: str) -> Weapon | None:
        return self.weapons[cat]

    def set_next(self) -> str:
        equipped_index = min(self.equipped_index + 1, len(self.categories) - 1)
        equipped = self.categories[equipped_index]
        if not self.get(equipped):
            return self.equipped
        self.equipped_index = equipped_index
        self.equipped = equipped
        return self.equipped

    def set_previous(self):
        equipped_index = max(self.equipped_index - 1, 0)
        equipped = self.categories[equipped_index]
        if not self.get(equipped):
            return self.equipped
        self.equipped_index = equipped_index
        self.equipped = equipped
        return self.equipped

    def get_next_name(self):
        if self.equipped_index < len(self.categories):
            weapon = self.get(self.categories[self.equipped_index + 1])
            if weapon:
                return weapon.properties.name
        return False

    def get_prev_name(self):
        if self.equipped_index > 0:
            weapon = self.get(self.categories[self.equipped_index - 1])
            if weapon:
                return weapon.properties.name
        return False

    def update(self, frame_time):
        for weapon in self.weapons.values():
            if weapon:
                weapon.update(frame_time)

    def reset(self):
        for weapon in self.weapons.values():
            if weapon:
                weapon.reset()
