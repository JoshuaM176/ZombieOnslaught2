import pygame as pg
from registries.projectile_registries import ProjectileRegistry
from objects.projectiles.arrow import Arrow
from random import uniform
from math import floor
from util.event_bus import event_bus
from dataclasses import dataclass

@dataclass(kw_only=True)
class WeaponProperties():
    name: str
    type: str
    firerate: int
    fire_animation_length: float
    burst: int
    burst_delay: float
    projectile_count: int
    shiftX: int
    shiftY: int
    downwards_recoil: bool
    recoil_per_shot: float
    recoil_control: float
    max_recoil: float
    projectile_type: str

    def __post_init__(self):
        self.time_per_bullet = 60 / self.firerate
        self.time_since_last_bullet = 0
        self.time_since_last_burst = 0
        self.shooting = False
        self.recoil = 0
        self.reloading = False
        self.burst_fired = 0
        self.sprite_time = 0

class Weapon(pg.sprite.Sprite):
    def __init__(
        self,
        name: str,
        player: dict,
        properties: dict,
        sprites: dict,
        ammo: dict,
        projectile: dict,
        projectile_registry: ProjectileRegistry | None = None,
        projectile_registries: ProjectileRegistry | None = None,
        bus: str = "trash",
        **_,
    ):
        super().__init__()
        self.sprites = sprites
        self.image, self.rect = (
            self.sprites["default"],
            self.sprites["default"].get_rect(),
        )
        self.temp_sprite = None
        self.projectile = projectile.copy()
        self.properties = WeaponProperties(name = name, projectile_type = self.projectile.pop("type"), **properties)
        self.player = player
        self.projectile_registry = projectile_registry
        if not self.projectile_registry:
            self.projectile_registry = projectile_registries["zombie_bullet_registry"] if self.properties.projectile_type == "bullet" else projectile_registries["zombie_projectile_registry"]
        self.ammo = Ammo(**ammo)
        self.ui_bus = event_bus.put_events(bus)
        self.ui_bus.send(None)

    def flip_sprites(self):
        new_sprites = {}
        for key, sprite in self.sprites.items():
            if isinstance(sprite, list):
                new_list = []
                for each in sprite:
                    new_list.append(pg.transform.flip(each, True, False))
                new_sprites[key] = new_list
            else:
                new_sprites[key] = pg.transform.flip(sprite, True, False)
        self.sprites = new_sprites
        self.properties.shiftX *= -1
        self.projectile["speed"] *= -1

    def shoot(self, x, y):
        if self.ammo.get():
            if not self.properties.burst or self.properties.burst_fired < self.properties.burst:
                self.properties.burst_fired += 1
                self.fire(x, y)
                ammo = self.ammo.get()
                self.ui_bus.send({"bullets": ammo})
                if ammo == 0:
                    self.properties.reloading = True

    def fire(self, x, y):
        self.ammo.shoot()
        self.set_sprite(self.sprites["fire_sprite"], self.properties.fire_animation_length)
        for i in range(self.properties.projectile_count):
            match self.properties.projectile_type:
                case "bullet":
                    self.projectile_registry.add(
                        x,
                        y,
                        **self.projectile,
                        recoil = uniform(self.properties.recoil * -self.properties.downwards_recoil, self.properties.recoil)
                    )
                case "arrow":
                    projectile = Arrow(
                        x,
                        y,
                        **self.projectile,
                        recoil=uniform(self.properties.recoil * -self.properties.downwards_recoil, self.properties.recoil),
                    )
                    self.projectile_registry.add(projectile)
            self.properties.recoil += self.properties.recoil_per_shot
            if self.properties.recoil > self.properties.max_recoil:
                self.properties.recoil = self.properties.max_recoil
        self.properties.time_since_last_bullet -= self.properties.time_per_bullet
        if self.ammo.reload_type == 1:
            self.properties.reloading = False

    def reload(self, frame_time):
        if not self.ammo.mags:
            self.properties.reloading = False
            return
        self.properties.shooting = False
        steps = len(self.sprites["reloading"])
        animation, self.properties.reloading = self.ammo.reload(frame_time)
        ind = floor(animation * steps)
        if ind >= steps:
            self.set_sprite(self.sprites["extra_reload_sprite"], 0.1)
        else:
            self.set_sprite(self.sprites["reloading"][ind], 0.1)
        self.ui_bus.send({"bullets": self.ammo.get(), "mags": self.ammo.mags})

    def set_sprite(self, sprite, time):
        self.temp_sprite = sprite
        self.properties.sprite_time = time

    def get_sprite(self, frame_time):
        if self.properties.sprite_time <= 0:
            self.properties.sprite_time = 0
            self.image = self.sprites["default"]
        else:
            self.properties.sprite_time -= frame_time
            self.image = self.temp_sprite

    def draw(self, x, y, frame_time, shooting, reloading):
        self.get_sprite(frame_time)
        if self.properties.burst_fired >= self.properties.burst and not shooting:
            self.properties.shooting = False
        if shooting and self.properties.time_since_last_burst >= self.properties.burst_delay:
            self.properties.shooting = shooting
            self.properties.time_since_last_burst = 0
        if not self.properties.shooting:
            self.properties.burst_fired = 0
        if reloading and self.ammo.bullets < self.ammo.max_bullets:
            self.properties.reloading = reloading
        if self.properties.recoil > 0:
            self.properties.recoil -= self.properties.recoil_control * frame_time
            if self.properties.recoil < 0:
                self.properties.recoil = 0
        if self.properties.time_since_last_burst < self.properties.burst_delay and not self.properties.shooting:
            self.properties.time_since_last_burst += frame_time
        if self.properties.time_since_last_bullet < self.properties.time_per_bullet:
            self.properties.time_since_last_bullet += frame_time
        if self.properties.shooting and self.properties.time_since_last_bullet > self.properties.time_per_bullet:
            self.shoot(x, y)
        if self.properties.reloading:
            self.reload(frame_time)
        self.ui_bus.send(
            {
                "mags": self.ammo.mags,
                "mag_progress": self.ammo.mag_progress / self.ammo.mag_time,
            }
        )
        self.rect.topleft = x + self.properties.shiftX, y + self.properties.shiftY

    def update(self, frame_time, *_):
        self.ammo.update(frame_time)

    def reset(self):
        self.ammo.reset()


@dataclass
class Ammo:
    bullets: int
    bullet_in_chamber: bool
    mags: int
    mag_time: int
    reload_time: float
    reload_on_empty: float
    reload_type: int

    def __post_init__(self):
        self.reload_progress = 0
        self.mag_progress = 0
        self.max_bullets = self.bullets
        self.max_mags = self.mags
        if self.bullet_in_chamber:
            self.rounds_in_chamber = 1
        else:
            self.rounds_in_chamber = 0

    def get(self):
        return self.bullets + self.rounds_in_chamber

    def shoot(self):
        if self.rounds_in_chamber:
            self.rounds_in_chamber -= 1
        elif self.bullets:
            self.bullets -= 1

    def update(self, frame_time):
        if self.bullet_in_chamber:
            if not self.rounds_in_chamber and self.bullets:
                self.rounds_in_chamber += 1
                self.bullets -= 1
        if self.mags < self.max_mags:
            self.mag_progress += frame_time
            if self.mag_progress >= self.mag_time:
                self.mag_progress = 0
                self.mags += 1

    def reload(self, frame_time):
        if self.reload_type == 0:
            self.bullets = 0
        time = (
            self.reload_time if self.get() else self.reload_time + self.reload_on_empty
        )
        rtn = self.reload_progress / self.reload_time
        self.reload_progress += frame_time
        if self.reload_progress >= time:
            self.mags -= 1
            self.reload_progress = 0
            if self.reload_type == 0:
                self.bullets = self.max_bullets
            elif self.reload_type == 1:
                self.bullets += 1
        return rtn, False if self.bullets >= self.max_bullets else True

    def reset(self):
        self.bullets = self.max_bullets
        self.mags = self.max_mags
        if self.bullet_in_chamber:
            self.rounds_in_chamber = 1
