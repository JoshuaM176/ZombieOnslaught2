from __future__ import annotations

from enum import StrEnum, auto
from typing import Annotated, Any

import pygame as pg
from pydantic import BaseModel, BeforeValidator, ConfigDict

from data.util import convert_file_to_sprite


def convert_weapon_to_sprite(file: str) -> pg.Surface:
    return convert_file_to_sprite(file, "weapons")


def convert_weapons_to_sprite(files: list[str]) -> list[pg.Surface]:
    return [convert_file_to_sprite(f, "weapons") for f in files]


class WeaponCategory(StrEnum):
    melee = auto()
    pistol = auto()
    smg = auto()
    rifle = auto()
    shotgun = auto()
    sniper = auto()


class WeaponData(BaseModel):
    name: str
    player: WeaponPlayerData
    sprites: WeaponSprites
    properties: WeaponPropertiesData
    ammo: WeaponAmmoData
    projectile: WeaponProjectileData
    store: WeaponStoreData


class WeaponPlayerData(BaseModel):
    movement: int
    owned: bool
    available: bool
    default: bool


class WeaponSprites(BaseModel):
    default: Annotated[pg.Surface, BeforeValidator(convert_weapon_to_sprite)]
    reloading: Annotated[list[pg.Surface], BeforeValidator(convert_weapons_to_sprite)]
    extra_reload_sprite: Annotated[pg.Surface, BeforeValidator(convert_weapon_to_sprite)]
    fire_sprite: Annotated[pg.Surface, BeforeValidator(convert_weapon_to_sprite)]

    model_config = ConfigDict(arbitrary_types_allowed=True)


class WeaponPropertiesData(BaseModel):
    type: WeaponCategory
    firerate: int
    fire_animation_length: float
    shiftX: int
    shiftY: int
    recoil_per_shot: float
    recoil_control: int
    max_recoil: int


class WeaponAmmoData(BaseModel):
    bullets: int
    mags: int
    mag_time: float
    reload_time: float
    reload_on_empty: float


class WeaponProjectileData(BaseModel):
    damage: float
    head_mult: float
    dropoff: float
    speed: int
    penetration: int
    shiftX: int
    shiftY: int


def parse_requirement(data: dict[str, Any]) -> WeaponRequirement:
    if data.pop("type") == "weapon":
        return WeaponPrevPurchaseRequirement(**data)
    raise AttributeError("Requirement: type did not match any valid options")


def parse_requirements(data: list[dict[str, Any]]) -> list[WeaponRequirement]:
    return [parse_requirement(each) for each in data]


class WeaponStoreData(BaseModel):
    price: int
    shiftX: int
    shiftY: int
    requirements: Annotated[list[WeaponRequirement], BeforeValidator(parse_requirements)]


class WeaponRequirement(BaseModel): ...



class WeaponPrevPurchaseRequirement(WeaponRequirement):
    name: str
    cat: WeaponCategory
