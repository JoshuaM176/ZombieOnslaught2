from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from math import sqrt
from typing import override

import pygame as pg

from objects.generic.blood import Blood
from objects.hitreg import HitBox
from objects.projectiles import Projectile
from objects.weapons import Weapon
from objects.zombie_effects import EntityEffect, effect_map
from registries.weapon_registries import EquippedWeaponRegistry, WeaponRegistry
from util.event_bus import event_bus
from util.resource_loading import ResourceLoader, load_sprite
from util.ui_objects import FloatingNumber, ProgressBar

logger = logging.getLogger(__name__)


@dataclass(kw_only=True)
class EntityProperties:
    speed: float
    health: float
    body_armour: float
    head_armour: float
    name: str
    blood: bool = True

    def __post_init__(self):
        self.current_speed = self.speed
        self.max_health = self.health
        self.invincible = False


@dataclass
class TimerEffect:
    effect: EntityEffect
    frequency: float
    time_passed: float = 0

    def execute(self, frame_time: float) -> bool:
        self.time_passed += frame_time
        if self.time_passed > self.frequency:
            self.time_passed -= self.frequency
            return self.effect.execute(frame_time)
        return True


@dataclass(kw_only=True)
class EntityEquipment: ...


class Entity[P: EntityProperties](pg.sprite.Sprite):
    def __init__(
        self,
        screen: pg.Surface,
        x: int,
        y: int,
        hitbox: list[int],
        head_hitbox: list[int],
        sprite: pg.Surface,
        properties: dict,
        property_class: type[P] = EntityProperties,
        damage_numbers: bool = False,
        **_,
    ):
        super().__init__()
        self.screen = screen
        self.x = x
        self.y = y
        self.hitbox = HitBox(x, y, *hitbox)
        self.head_hitbox = HitBox(x, y, *head_hitbox)
        self.image, self.rect = sprite, sprite.get_rect()
        self.damage_numbers = damage_numbers
        self.movement = {"horizontal": 0, "vertical": 0}
        if self.damage_numbers:
            self.damage_number = FloatingNumber(2)
        self.properties: P = property_class(**properties)

    def update(self):
        self.rect.topleft = (self.x, self.y)

    def update_movement(self, frame_time):
        self.x += self.movement["horizontal"] * self.properties.current_speed * frame_time
        self.y += self.movement["vertical"] * self.properties.current_speed * frame_time
        if self.x < -150:
            self.x = -50
        self.x = min(self.x, self.screen.get_width())
        self.y = min(self.y, self.screen.get_height() - 350)
        self.y = max(self.y, -100)

    def hit_check(self, bullet: Projectile):
        if bullet is None or bullet.damage < 0 or self.properties.health < 0 or self in bullet.recent_hits:
            return
        if self.head_hitbox.check(bullet.x, bullet.y):
            self.head_hit(bullet)
            bullet.hit(self)
        elif self.hitbox.check(bullet.x, bullet.y):
            self.body_hit(bullet)
            bullet.hit(self)

    def head_hit(self, bullet: Projectile) -> None:
        damage = bullet.damage * bullet.head_mult
        damage *= 1 - max(self.properties.head_armour - bullet.armour_pierce, 0)
        self.blood(bullet.x, bullet.y, self.damage(damage))

    def body_hit(self, bullet: Projectile) -> None:
        damage = bullet.damage
        damage *= 1 - max(self.properties.body_armour - bullet.armour_pierce, 0)
        self.blood(bullet.x, bullet.y, self.damage(damage))

    def blood(self, x: float, y: float, size: float) -> None:
        event_bus.add_event("generic_registry_l1_bus", Blood(x, y, size))

    def damage(self, damage: float) -> float:
        damage_dealt = min(damage, self.properties.health)
        if self.damage_numbers:
            self.damage_number.add(self.x, self.y, damage_dealt)
        self.properties.health -= damage
        return damage_dealt


@dataclass
class ZombieProperties(EntityProperties):
    reward: float
    experience: int
    base_round: int

    def __post_init__(self):
        self.frozen = False
        super().__post_init__()

    def _round_scale_init(self, round_scaling: int):
        if round_scaling:
            round_scaling = max(round_scaling - self.base_round, 0)
        small_scale = sqrt(round_scaling) * 0.1 + 1
        large_scale = round_scaling / 25 + 1
        self.reward *= small_scale
        self.current_speed *= small_scale
        self.health *= large_scale
        self.max_health *= large_scale


class Zombie(Entity[ZombieProperties]):
    def __init__(
        self,
        screen: pg.Surface,
        x: int,
        y: int,
        weapon_registry,
        projectile_registries,
        round_scaling: int = 0,
        parent=None,
        zombies=None,
        **attrs,
    ):
        self.parent = parent
        self.zombies = zombies
        self.summoned_zombies = []
        super().__init__(screen, x, y, damage_numbers=True, property_class=ZombieProperties, **attrs)
        self.properties._round_scale_init(round_scaling)
        weapon = weapon_registry.get_weapon(attrs["weapon_stats"]["category"], attrs["weapon_stats"]["name"])
        self.projectile_registry = projectile_registries["zombie_projectile_registry"]
        self.bullet_registry = projectile_registries["zombie_bullet_registry"]
        self.weapon = Weapon(**weapon, projectile_registry=self.bullet_registry, bus="trash")
        if attrs["weapon_stats"].get("projectile"):
            self.weapon.projectile.update(attrs["weapon_stats"]["projectile"])
        self.weapon.flip_sprites()
        self.health_bar = ProgressBar(1, self.x - 16, self.y - 24, 80, 20, text=str(round(self.properties.health)))
        self.movement["horizontal"] = -1

        self.death_effects: list[EntityEffect] = []
        self.effects: list[EntityEffect | TimerEffect] = []
        for each in attrs["effects"]:
            effect = effect_map.get(each["effect_name"])
            if not effect:
                continue  # TEMPORARY
            effect = effect(self, each["values"])
            trigger = each.get("trigger", "default")
            match trigger:
                case "default":
                    self.effects.append(effect)
                case "death":
                    self.death_effects.append(effect)
                case "init":
                    self.use_effect(effect, 0)
                case "timer":
                    self.effects.append(TimerEffect(effect, each["frequency"]))
                case _:
                    raise AttributeError(f"Unknown effect trigger: {trigger} on effect: {type(effect).__name__}")

        self.animation_sprites = attrs["sprites"]["animation"]
        self.animation_length = attrs["animation_length"]
        self.animation_step_length = self.animation_length / len(self.animation_sprites)
        self.animation_time = random.uniform(0, self.animation_length)
        self.animation_step = 0
        logger.info(f"Zombie initialized with properties: {self.properties}")
        logger.info(f"Zombie initialized with effects: {self.effects}")

    def use_effect(self, effect: EntityEffect | TimerEffect, frame_time: float) -> bool:
        """Use an affect and return false if effect is over."""
        return effect.execute(frame_time)

    def use_effects(self, frame_time: float) -> None:
        remove_effects = []
        for effect in self.effects:
            if not self.use_effect(effect, frame_time):
                remove_effects.append(effect)
        for effect in remove_effects:
            self.effects.remove(effect)

    def use_death_effects(self) -> None:
        for effect in self.death_effects:
            self.use_effect(effect, 0)

    def update_health_bar(self):
        self.health_bar.update_progress(self.properties.health / self.properties.max_health)
        self.health_bar.update_text(str(max(round(self.properties.health), 1)))

    @override
    def head_hit(self, bullet: Projectile) -> None:
        super().head_hit(bullet)
        self.update_health_bar()

    @override
    def body_hit(self, bullet: Projectile) -> None:
        super().body_hit(bullet)
        self.update_health_bar()

    def update(self, frame_time: float, screen: pg.Surface):
        if not self.properties.frozen:
            self.update_movement(frame_time)
            self.animation_time += frame_time
            if self.animation_time > self.animation_length:
                self.animation_time = 0
        self.image = self.animation_sprites[int(self.animation_time / self.animation_step_length)]
        if self.x < -100:
            event_bus.add_event("game_event_bus", {"damage_village": {"damage": 1}})
            self.x = screen.get_width() + 100
        self.use_effects(frame_time)
        self.hitbox.update(self.x, self.y)
        self.head_hitbox.update(self.x, self.y)
        self.rect.topleft = (self.x, self.y)
        self.weapon.draw(self.x, self.y, frame_time, True, False)
        x, y, _, _ = self.head_hitbox.get()
        self.health_bar.update_pos(x - 16, y - 24)
        self.health_bar.update(screen)


@dataclass
class PlayerProperties(EntityProperties):
    stamina: int
    stamina_regen_delay: int
    stamina_regen: int
    experience: int = 0
    experience_required: int = 100
    level: int = 0
    level_tokens: int = 0

    def __post_init__(self) -> None:
        self.max_stamina = self.stamina
        self.time_resting = -self.stamina_regen_delay
        event_bus.add_event(
            "ui_bus",
            {
                "level": self.level,
                "level_tokens": self.level_tokens,
                "experience": self.experience,
                "experience_required": self.experience_required,
            },
        )
        return super().__post_init__()

    def add_experience(self, experience: int):
        self.experience += experience
        if self.experience >= self.experience_required:
            self.experience -= self.experience_required
            self.experience_required = round(self.experience_required * 1.1)
            self.level += 1
            self.level_tokens += 1
        event_bus.add_event(
            "ui_bus",
            {
                "level": self.level,
                "level_tokens": self.level_tokens,
                "experience": self.experience,
                "experience_required": self.experience_required,
            },
        )


class Player(Entity[PlayerProperties]):
    def __init__(self, x, y, projectile_registries: dict, weapon_registry: WeaponRegistry, key_map, screen):
        self.bullet_registry = projectile_registries["player_bullet_registry"]
        resource_loader = ResourceLoader("player", "attributes")
        resource_loader.load_all()
        resources = resource_loader.get("player")
        resources["sprite"] = load_sprite("player.png", "player", -1)
        self.properties = PlayerProperties(**resources["properties"])
        super().__init__(screen, x, y, property_class=PlayerProperties, **resources)
        self.render_plain = pg.sprite.RenderPlain(self)
        self.sprinting = False
        self.shooting = False
        self.reloading = False
        self.input_dict = {
            "up": False,
            "left": False,
            "down": False,
            "right": False,
            "sprint": False,
            "shooting": False,
            "reloading": False,
            "go2settings": False,
        }
        self.key_map = key_map
        self.weapons = EquippedWeaponRegistry(self.bullet_registry)
        self.equipped_weapon = None
        for weapon in resources["equipped_weapons"]:
            weapon_dict = weapon_registry.get_weapon(weapon["cat"], weapon["name"])
            self.set_weapon(weapon_dict, weapon["cat"])
        self.ui_bus = event_bus.put_events("ui_bus")
        self.ui_bus.send(None)

    def set_weapon(self, weapon: dict, cat: str):
        self.weapons.equip(weapon, cat)

    def set_equipped_weapon(self, cat: str):
        if cat:
            if self.equipped_weapon:
                self.render_plain.remove(self.equipped_weapon)
            self.equipped_weapon = self.weapons.get(cat)
            self.render_plain.add(self.equipped_weapon)
            self.ui_bus.send(
                {
                    "weapon": self.equipped_weapon.properties.name,
                    "bullets": self.equipped_weapon.ammo.get(),
                    "max_bullets": self.equipped_weapon.ammo.max_bullets,
                    "mags": self.equipped_weapon.ammo.mags,
                    "max_mags": self.equipped_weapon.ammo.max_mags,
                    "next_weapon": self.weapons.get_next_name(),
                    "prev_weapon": self.weapons.get_prev_name(),
                },
            )

    def switch_weapon(self):
        if self.input_dict.pop("next", None):
            self.set_equipped_weapon(self.weapons.set_next())
        if self.input_dict.pop("previous", None):
            self.set_equipped_weapon(self.weapons.set_previous())

    def go_to_settings(self):
        if self.input_dict["go2settings"]:
            event_bus.add_event("game_event_bus", {"set_screen": {"go2": "settings"}})
        self.input_dict["go2settings"] = False

    def get_input(self):
        input_bus = event_bus.get_events("input_bus")

        def parse_input(key_pressed, key):
            self.input_dict.update({self.key_map.get(key): key_pressed})

        for event in input_bus:
            if event.type == pg.KEYDOWN:
                parse_input(True, event.key)
            if event.type == pg.KEYUP:
                parse_input(False, event.key)
            if event.type == pg.MOUSEBUTTONDOWN:
                parse_input(True, event.button)
            if event.type == pg.MOUSEBUTTONUP:
                parse_input(False, event.button)

    def reset(self):
        self.x = 100
        self.properties.health = self.properties.max_health
        self.reset_input()
        self.weapons.reset()
        self.ui_bus.send(
            {
                "weapon": self.equipped_weapon.properties.name,
                "bullets": self.equipped_weapon.ammo.get(),
                "max_bullets": self.equipped_weapon.ammo.max_bullets,
                "mags": self.equipped_weapon.ammo.mags,
                "max_mags": self.equipped_weapon.ammo.max_mags,
                "next_weapon": self.weapons.get_next_name(),
                "prev_weapon": self.weapons.get_prev_name(),
            },
        )

    def reset_input(self):
        self.shooting = False
        self.reloading = False
        self.input_dict.update(
            {
                "up": False,
                "left": False,
                "down": False,
                "right": False,
                "sprint": False,
                "shooting": False,
                "reloading": False,
            },
        )

    def update_movement(self, frame_time):
        self.properties.current_speed = self.properties.speed * self.equipped_weapon.player["movement"]
        self.movement["horizontal"] = self.input_dict["right"] - self.input_dict["left"]
        self.movement["vertical"] = self.input_dict["down"] - self.input_dict["up"]
        sprint = self.input_dict["sprint"] + 1
        if self.properties.stamina < 0:
            sprint = 1
            self.properties.current_speed *= 0.5
        if not self.movement["horizontal"] and not self.movement["vertical"]:
            if self.properties.time_resting > 0 and self.properties.stamina < self.properties.max_stamina:
                self.properties.stamina = min(
                    self.properties.stamina + self.properties.time_resting * frame_time * self.properties.stamina_regen,
                    self.properties.max_stamina,
                )
            if self.properties.time_resting < 1:
                self.properties.time_resting = min(self.properties.time_resting + frame_time, 1)
        else:
            self.properties.time_resting = -self.properties.stamina_regen_delay
            if self.properties.stamina > 0:
                self.properties.stamina -= frame_time / 2
                if sprint > 1:
                    self.properties.stamina -= frame_time
            self.properties.current_speed *= sprint
            if self.movement["horizontal"] and self.movement["vertical"]:
                self.properties.current_speed *= 0.7071  # For consistent movement speed diagonally
        super().update_movement(frame_time)

    def update_shooting(self, shooting: bool | None = None, reloading: bool | None = None):
        self.shooting = shooting or self.input_dict["shooting"]
        self.reloading = reloading or self.input_dict["reloading"]
        self.input_dict["reloading"] = False

    def send_data_to_ui(self):
        self.ui_bus.send(
            {
                "health": self.properties.health,
                "max_health": self.properties.max_health,
                "stamina": self.properties.stamina,
                "max_stamina": self.properties.max_stamina,
            },
        )

    def update(self, frame_time):
        self.get_input()
        self.update_movement(frame_time)
        self.update_shooting()
        self.switch_weapon()
        self.go_to_settings()
        self.send_data_to_ui()
        self.rect.topleft = (self.x, self.y)
        self.hitbox.update(self.x, self.y)
        self.head_hitbox.update(self.x, self.y)
        self.equipped_weapon.draw(self.x, self.y, frame_time, self.shooting, self.reloading)
        self.weapons.update(frame_time)
        self.render_plain.draw(self.screen)
