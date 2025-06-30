import pygame as pg
from objects.hitreg import HitBox
from util.resource_loading import load_sprite, ResourceLoader
from util.event_bus import event_bus
from registries.weapon_registries import EquippedWeaponRegistry


class Entity(pg.sprite.Sprite):
    def __init__(
        self,
        x: int,
        y: int,
        hitbox: list[int],
        head_hitbox: list[int],
        sprite: pg.Surface,
        **_,
    ):
        super().__init__()
        self.x = x
        self.y = y
        self.hitbox = HitBox(x, y, *hitbox)
        self.head_hitbox = HitBox(x, y, *head_hitbox)
        self.image, self.rect = sprite, sprite.get_rect()
        self.horizontal_movement = 0
        self.vertical_movement = 0

    def update(self):
        self.rect.topleft = (self.x, self.y)


class Zombie(Entity):
    def __init__(self, x: int, y: int, round_scaling: bool = True, **attrs):
        super().__init__(x, y, **attrs)

    def update(self):
        self.hitbox.update(self.x, self.y)
        self.rect.topleft = (self.x, self.y)


class Player(Entity):
    def __init__(self, x, y, bullet_registry):
        self.bullet_registry = bullet_registry
        resource_loader = ResourceLoader("player", "attributes")
        resource_loader.load_all()
        resources = resource_loader.get("player")
        resources["sprite"] = load_sprite("player.png", "player", -1)
        super().__init__(x, y, **resources)
        self.render_plain = pg.sprite.RenderPlain((self))
        self.speed = resources.get("speed") or 300
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
            "mwup": (self.input_dict, "next", self.switch_weapon),
            "mwdown": (self.input_dict, "previous", self.switch_weapon),
            pg.K_r: (self.input_dict, "reloading", self.update_shooting),
        }
        self.weapons = EquippedWeaponRegistry(self.bullet_registry)
        self.equipped_weapon = None

    def set_weapon(self, weapon, cat: str):
        self.weapons.equip(weapon, cat)

    def set_equipped_weapon(self, cat: str):
        if cat:
            if self.equipped_weapon:
                self.render_plain.remove(self.equipped_weapon)
            self.equipped_weapon = self.weapons.get(cat)
            self.render_plain.add(self.equipped_weapon)

    def switch_weapon(self):
        if self.input_dict.pop("next", None):
            self.set_equipped_weapon(self.weapons.set_next())
        if self.input_dict.pop("previous", None):
            self.set_equipped_weapon(self.weapons.set_previous())

    def get_input(self):
        input_bus = event_bus.get_events("input_bus")

        def apply_input(key_pressed, input_map, inp, func=None):
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
        self.equipped_weapon.draw(
            self.x, self.y, frame_time, self.shooting, self.reloading
        )
        self.render_plain.draw(screen)
