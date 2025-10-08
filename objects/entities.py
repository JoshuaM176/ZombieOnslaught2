import pygame as pg
from objects.hitreg import HitBox
from objects.weapons import Weapon
from objects.generic.blood import Blood
from util.resource_loading import load_sprite, ResourceLoader
from util.event_bus import event_bus
from util.ui_objects import FloatingNumber, ProgressBar
from registries.weapon_registries import EquippedWeaponRegistry, WeaponRegistry
from registries.generic_registries import GenericRegistry
from math import sqrt
from objects.zombie_effects import effect_map
from objects.projectiles.bullet import Bullet
import random
from dataclasses import dataclass
from typing import Type

@dataclass
class EntityProperties:
    speed: int
    health: int
    body_armour: int
    head_armour: int
    name: str

    def __post_init__(self):
        self.current_speed = self.speed
        self.max_health = self.health
        self.invincible = False


class Entity(pg.sprite.Sprite):
    def __init__(
        self,
        screen: pg.Surface,
        generic_registry: GenericRegistry,
        x: int,
        y: int,
        hitbox: list[int],
        head_hitbox: list[int],
        sprite: pg.Surface,
        properties: dict,
        property_class: Type[EntityProperties] = None,
        damage_numbers: bool = False,
        **_,
    ):
        super().__init__()
        self.screen = screen
        self.generic_registry = generic_registry
        self.x = x
        self.y = y
        self.hitbox = HitBox(x, y, *hitbox)
        self.head_hitbox = HitBox(x, y, *head_hitbox)
        self.image, self.rect = sprite, sprite.get_rect()
        self.damage_numbers = damage_numbers
        self.movement = {"horizontal": 0, "vertical": 0}
        if self.damage_numbers:
            self.damage_number = FloatingNumber(2)
        if property_class:
            self.properties = property_class(**properties)
        else:
            self.properties = EntityProperties(**properties)

    def update(self):
        self.rect.topleft = (self.x, self.y)

    def update_movement(self, frame_time):
        self.x += self.movement["horizontal"] * self.properties.current_speed * frame_time
        self.y += self.movement["vertical"] * self.properties.current_speed * frame_time
        if self.x < -150:
            self.x = -50
        if self.x > self.screen.get_width():
            self.x = self.screen.get_width()
        if self.y > self.screen.get_height() - 350:
            self.y = self.screen.get_height() - 350
        if self.y < -100:
            self.y = -100

    def hit_check(self, bullet: Bullet):
        if bullet is not None and bullet.damage > 0:
            if self not in bullet.recent_hits:
                if self.head_hitbox.check(bullet.x, bullet.y):
                    self.hit(bullet, True)
                    bullet.hit(self)
                elif self.hitbox.check(bullet.x, bullet.y):
                    self.hit(bullet, False)
                    bullet.hit(self)

    def hit(self, bullet: Bullet, head: bool):
        damage = bullet.damage
        if head:
            damage *= bullet.head_mult
            damage *= 1 - max(self.properties.head_armour - bullet.armour_pierce, 0)
        else:
            damage *= 1 - max(self.properties.body_armour - bullet.armour_pierce, 0)
        if self.damage_numbers:
            self.damage_number.add(self.x, self.y, damage)
        self.properties.health -= damage
        self.generic_registry.add(Blood(bullet.x, bullet.y, damage))
        


class Zombie(Entity):
    def __init__(
        self,
        screen: pg.Surface,
        x: int,
        y: int,
        weapon_registry,
        projectile_registry,
        generic_registry,
        round_scaling: int = 0,
        parent=None,
        zombies=None,
        **attrs,
    ):
        self.parent = parent
        self.zombies = zombies
        self.summoned_zombies = []
        self.remove_effects = []
        super().__init__(screen, generic_registry, x, y, damage_numbers=True, property_class=ZombieProperties, **attrs)
        self.properties._round_scale_init(round_scaling)
        weapon = weapon_registry.get_weapon(
            attrs["weapon_stats"]["category"], attrs["weapon_stats"]["name"]
        )
        self.projectile_registry=projectile_registry
        self.weapon = Weapon(**weapon, bullet_registry=projectile_registry, bus="trash")
        if attrs["weapon_stats"].get("bullet"):
            self.weapon.bullet.update(attrs["weapon_stats"]["bullet"])
        self.weapon.flip_sprites()
        self.progress_bar = ProgressBar(1, self.x - 16, self.y - 24, 80, 20, text = str(round(self.properties.health)))
        self.movement["horizontal"] = -1

        self.effects = []
        for effect in attrs["effects"]:
            func = effect_map.get(effect["effect"])
            values = {}
            conditions = []
            for value_dict in effect["values"]:
                match value_dict.get("type") or "default":
                    case "format":
                        value = format(self=self)
                    case "eval":
                        value = eval(value_dict["value"])
                    case "format_eval":
                        value = eval(value_dict["value"].format(self=self))
                    case "repeat_format_eval":
                        value = value_dict["value"]
                    case "default":
                        value = value_dict["value"]
                if value_dict.get("attribute"):
                    setattr(self, value_dict["name"], value)
                    values[value_dict["name"]] = {"attribute": True}
                else:
                    values[value_dict["name"]] = {"value": value}
                    if value_dict.get("type") == "repeat_format_eval":
                        values[value_dict["name"]].update({"repeat_format_eval": True})
            if effect.get("conditions"):
                for condition in effect["conditions"]:
                    conditions.append(condition)
            trigger = effect.get("trigger") or "default"
            if trigger == "timer":
                values["time"] = {"value": 0}
            self.effects.append(
                {
                    "func": func,
                    "values": values,
                    "conditions": conditions,
                    "trigger": trigger,
                    "id": len(self.effects),
                }
            )
            if trigger == "init":
                self.use_effect(None, self.effects[-1])

        self.animation_sprites = attrs["sprites"]["animation"]
        self.animation_length = attrs["animation_length"]
        self.animation_step_length = self.animation_length / len(self.animation_sprites)
        self.animation_time = random.uniform(0, self.animation_length)
        self.animation_step = 0

    def use_effect(self, frame_time, effect):
        if self.check_effect_conditions(effect["conditions"]):
            func = effect["func"]
            kwargs = {"id": effect["id"]}
            for arg, value in effect["values"].items():
                if value.get("attribute"):
                    kwargs.update({arg: getattr(self, arg)})
                elif value.get("repeat_format_eval"):
                    kwargs.update({arg: eval(value["value"].format(self=self))})
                else:
                    kwargs.update({arg: value["value"]})
            func(self=self, frame_time=frame_time, **kwargs)
            return True
        return False

    def check_effect_conditions(self, conditions: list[str]):
        for condition in conditions:
            if not eval(condition.format(self=self)):
                return False
        return True
    
    def update_health_bar(self):
        self.progress_bar.update_progress(self.properties.health/self.properties.max_health)
        self.progress_bar.update_text(str(max(round(self.properties.health),0)))
    
    def hit(self, bullet: Bullet, head: bool):
        super().hit(bullet, head)
        self.update_health_bar()

    def update(self, frame_time, screen: pg.Surface):
        for effect in self.remove_effects:
            self.effects[effect] = None
        self.remove_effects = []
        if not self.properties.frozen:
            self.update_movement(frame_time)
            self.animation_time += frame_time
            if self.animation_time > self.animation_length:
                self.animation_time = 0
        self.image = self.animation_sprites[
            int(self.animation_time / self.animation_step_length)
        ]
        if self.x < -100:
            event_bus.add_event("game_event_bus", {"damage_village": {"damage": 1}})
            self.x = screen.get_width() + 100
        for effect in [effect for effect in self.effects if effect is not None]:
            match effect["trigger"]:
                case "default":
                    self.use_effect(frame_time, effect)
                case "death":
                    if self.properties.health < 0:
                        self.use_effect(frame_time, effect)
                case "timer":
                    effect["values"]["time"]["value"] += frame_time
                    if (
                        effect["values"]["time"]["value"]
                        >= effect["values"]["frequency"]["value"]
                    ):
                        if self.use_effect(frame_time, effect):
                            effect["values"]["time"]["value"] = 0
        self.hitbox.update(self.x, self.y)
        self.head_hitbox.update(self.x, self.y)
        self.rect.topleft = (self.x, self.y)
        self.weapon.draw(self.x, self.y, frame_time, True, False)
        x, y, _, _ = self.head_hitbox.get()
        self.progress_bar.update_pos(x - 16, y - 24)
        self.progress_bar.update(screen)

@dataclass
class ZombieProperties(EntityProperties):
    reward: int
    base_round: int

    def __post_init__(self):
        self.frozen = False
        super().__post_init__()

    def _round_scale_init(self, round_scaling: int):
        if round_scaling:
            round_scaling = max(round_scaling - self.base_round, 0)
        small_scale = sqrt(round_scaling) * 0.1 + 1
        large_scale = round_scaling/25 + 1
        self.reward *= small_scale
        self.current_speed *= small_scale
        self.health *= large_scale
        self.max_health *= large_scale



class Player(Entity):
    def __init__(self, x, y, bullet_registry, weapon_registry: WeaponRegistry, generic_registry: GenericRegistry, key_map, screen):
        self.bullet_registry = bullet_registry
        resource_loader = ResourceLoader("player", "attributes")
        resource_loader.load_all()
        resources = resource_loader.get("player")
        resources["sprite"] = load_sprite("player.png", "player", -1)
        self.properties = PlayerProperties(**resources["properties"])
        super().__init__(screen, generic_registry, x, y, property_class = PlayerProperties, **resources)
        self.render_plain = pg.sprite.RenderPlain((self))
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
                    "weapon": self.equipped_weapon.name,
                    "bullets": self.equipped_weapon.ammo.get(),
                    "max_bullets": self.equipped_weapon.ammo.max_bullets,
                    "mags": self.equipped_weapon.ammo.mags,
                    "max_mags": self.equipped_weapon.ammo.max_mags,
                    "next_weapon": self.weapons.get_next_name(),
                    "prev_weapon": self.weapons.get_prev_name(),
                }
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
        self.health = self.properties.max_health
        self.reset_input()
        self.weapons.reset()
        self.ui_bus.send(
            {
                "weapon": self.equipped_weapon.name,
                "bullets": self.equipped_weapon.ammo.get(),
                "max_bullets": self.equipped_weapon.ammo.max_bullets,
                "mags": self.equipped_weapon.ammo.mags,
                "max_mags": self.equipped_weapon.ammo.max_mags,
                "next_weapon": self.weapons.get_next_name(),
                "prev_weapon": self.weapons.get_prev_name(),
            }
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
            }
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
            if self.properties.time_resting > 0:
                if self.properties.stamina < self.properties.max_stamina:
                    self.properties.stamina = min(
                        self.properties.stamina
                        + self.properties.time_resting * frame_time * self.properties.stamina_regen,
                        self.properties.max_stamina
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
                self.properties.current_speed *= 0.7071 # For consistent movement speed diagonally
        super().update_movement(frame_time)

    def update_shooting(self, shooting: bool = None, reloading: bool = None):
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
            }
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
        self.equipped_weapon.draw(
            self.x, self.y, frame_time, self.shooting, self.reloading
        )
        self.weapons.update(frame_time)
        self.render_plain.draw(self.screen)


@dataclass
class PlayerProperties(EntityProperties):
    stamina: int
    stamina_regen_delay: int
    stamina_regen: int

    def __post_init__(self):
        self.max_stamina = self.stamina
        self.time_resting = -self.stamina_regen_delay
        return super().__post_init__()
