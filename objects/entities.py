import pygame as pg
from objects.hitreg import HitBox
from objects.weapons import Weapon
from util.resource_loading import load_sprite, ResourceLoader
from util.event_bus import event_bus
from util.ui_objects import health_bar
from registries.weapon_registries import EquippedWeaponRegistry
from math import sqrt
from objects.zombie_abilities import ability_map
import random


class Entity(pg.sprite.Sprite):
    def __init__(
        self,
        x: int,
        y: int,
        hitbox: list[int],
        head_hitbox: list[int],
        sprite: pg.Surface,
        speed: int,
        health: int,
        **_,
    ):
        super().__init__()
        self.x = x
        self.y = y
        self.hitbox = HitBox(x, y, *hitbox)
        self.head_hitbox = HitBox(x, y, *head_hitbox)
        self.image, self.rect = sprite, sprite.get_rect()
        self.speed = speed
        self.health = health
        self.max_health = health
        self.horizontal_movement = 0
        self.vertical_movement = 0

    def update(self):
        self.rect.topleft = (self.x, self.y)

    def hit_check(self, bullet):
        if bullet is not None and bullet.damage > 0:
            if self not in bullet.recent_hits:
                if self.head_hitbox.check(bullet.x, bullet.y):
                    self.hit(bullet.damage * bullet.head_mult)
                    bullet.hit(self)
                elif self.hitbox.check(bullet.x, bullet.y):
                    self.hit(bullet.damage)
                    bullet.hit(self)

    def hit(self, damage):
        self.health -= damage


class Zombie(Entity):
    def __init__(
        self,
        x: int,
        y: int,
        weapon_registry,
        bullet_registry,
        round_scaling: int = 0,
        **attrs,
    ):
        if round_scaling:
            round_scaling = max(round_scaling - attrs["base_round"], 0)
        scale = sqrt(round_scaling) * 0.1 + 1
        super().__init__(x, y, **attrs)
        self.reward = attrs["reward"] * scale
        self.speed *= scale
        self.health *= scale
        self.max_health *= scale
        weapon = weapon_registry.get_weapon(
            attrs["weapon_stats"]["category"], attrs["weapon_stats"]["name"]
        )
        self.weapon = Weapon(**weapon, bullet_registry=bullet_registry, bus="trash")
        self.weapon.flip_sprites()
        self.abilities = []
        self.death_abilities = []
        for ability in attrs["abilities"]:
            func = ability_map.get(ability["ability"])
            values = []
            for value_dict in ability["values"]:
                match value_dict["type"]:
                    case "format":
                        value = format(self=self)
                    case "eval":
                        value = eval(value_dict["value"])
                    case "format_eval":
                        value = eval(value_dict["value"].format(self=self))
                    case "default":
                        value = value_dict["value"]
                if value_dict.get("attribute"):
                    self.__setattr__(value_dict["name"], value)
                    values.append({"attribute": True, "name": value_dict["name"]})
                else:
                    values.append(
                        {"name": value_dict["name"], "value": value_dict["value"]}
                    )
            match ability.get("trigger"):
                case "death":
                    self.death_abilities.append((func, values))
                case _:
                    self.abilities.append((func, values))
        self.animation_sprites = attrs["sprites"]["animation"]
        self.animation_length = attrs["animation_length"]
        self.animation_step_length = self.animation_length / len(self.animation_sprites)
        self.animation_time = random.uniform(0, self.animation_length)
        self.animation_step = 0

    def use_ability(self, frame_time, ability):
        func = ability[0]
        kwargs = {}
        for arg in ability[1]:
            if arg.get("attribute"):
                kwargs.update({arg["name"]: self.__getattribute__(arg["name"])})
            else:
                kwargs.update({arg["name"]: arg["value"]})
        func(self, frame_time, **kwargs)

    def update(self, frame_time, screen_width, screen_height):
        self.x -= self.speed * frame_time
        if self.y < 0:
            self.y += self.speed * frame_time
        if self.y > screen_height-300:
            self.y -= self.speed * frame_time
        self.animation_time += frame_time
        if self.animation_time > self.animation_length:
            self.animation_time = 0
        self.image = self.animation_sprites[
            int(self.animation_time / self.animation_step_length)
        ]
        if self.x < -100:
            self.x = screen_width+100
        for ability in self.abilities:
            self.use_ability(frame_time, ability)
        if self.health < 0:
            for ability in self.death_abilities:
                self.use_ability(frame_time, ability)
        self.hitbox.update(self.x, self.y)
        self.head_hitbox.update(self.x, self.y)
        self.rect.topleft = (self.x, self.y)
        self.weapon.draw(self.x, self.y, frame_time, True, False)


class Player(Entity):
    def __init__(self, x, y, bullet_registry):
        self.bullet_registry = bullet_registry
        resource_loader = ResourceLoader("player", "attributes")
        resource_loader.load_all()
        resources = resource_loader.get("player")
        resources["sprite"] = load_sprite("player.png", "player", -1)
        super().__init__(x, y, **resources)
        self.render_plain = pg.sprite.RenderPlain((self))
        self.movement = {"horizontal": 0, "vertical": 0}
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
        }
        self.key_map = {
            pg.K_w: (self.input_dict, "up", self.update_movement),
            pg.K_a: (self.input_dict, "left", self.update_movement),
            pg.K_s: (self.input_dict, "down", self.update_movement),
            pg.K_d: (self.input_dict, "right", self.update_movement),
            pg.K_LSHIFT: (self.input_dict, "sprint", self.update_movement),
            pg.K_SPACE: (self.input_dict, "shooting", self.update_shooting),
            "lmb": (self.input_dict, "shooting", self.update_shooting),
            "mwup": (self.input_dict, "next", self.switch_weapon),
            "mwdown": (self.input_dict, "previous", self.switch_weapon),
            pg.K_r: (self.input_dict, "reloading", self.update_shooting),
            pg.K_p: ({}, "", self.go_to_settings),
        }
        self.weapons = EquippedWeaponRegistry(self.bullet_registry)
        self.equipped_weapon = None
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
        event_bus.add_event("game_event_bus", {"set_screen": {"go2": "settings"}})

    def get_input(self):  # TODO fix this
        input_bus = event_bus.get_events("input_bus")

        def apply_input(key_pressed: bool, input_map, inp, func=None):
            return (
                input_map.update({inp: key_pressed}),
                func() if func else None,
            )

        def parse_input(key_pressed, key):
            return apply_input(key_pressed, *self.key_map.get(key, [{}, None]))

        for event in input_bus:
            if event.type == pg.KEYDOWN:
                parse_input(True, event.key)
            if event.type == pg.KEYUP:
                parse_input(False, event.key)
            if event.type == pg.MOUSEWHEEL:
                if event.y == 1:
                    parse_input(True, "mwup")
                else:
                    parse_input(True, "mwdown")
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    parse_input(True, "lmb")
            if event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    parse_input(False, "lmb")

    def reset(self):
        self.x = 100
        self.health = self.max_health
        self.movement.update({"horizontal": 0, "vertical": 0})
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
        self.update_movement()
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

    def update_movement(self):
        hor = self.input_dict["right"] - self.input_dict["left"]
        ver = self.input_dict["down"] - self.input_dict["up"]
        sprint = self.input_dict["sprint"] + 1
        speed = self.speed * sprint
        self.horizontal_movement = hor * speed
        self.vertical_movement = ver * speed
        if hor and ver:
            self.horizontal_movement *= 0.7071
            self.vertical_movement *= 0.7071

    def update_shooting(self, shooting: bool = None, reloading: bool = None):
        self.shooting = shooting or self.input_dict["shooting"]
        self.reloading = reloading or self.input_dict["reloading"]

    def update(self, screen, frame_time):
        self.get_input()
        self.x += self.horizontal_movement * frame_time
        self.y += self.vertical_movement * frame_time
        self.rect.topleft = (self.x, self.y)
        self.hitbox.update(self.x, self.y)
        self.head_hitbox.update(self.x, self.y)
        self.equipped_weapon.draw(
            self.x, self.y, frame_time, self.shooting, self.reloading
        )
        self.weapons.update(frame_time)
        if self.x < -50:
            self.x = -50
        if self.x > screen.get_width():
            self.x = screen.get_width()
        if self.y > screen.get_height()-250:
            self.y = screen.get_height()-250
        if self.y < -100:
            self.y = -100
        self.render_plain.draw(screen)
        x, y, _, _ = self.head_hitbox.get()
        health_bar(screen, self.health, self.max_health, x - 16, y - 24, 80, 20)
