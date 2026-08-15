from __future__ import annotations
from abc import abstractmethod, ABC

from math import log
from typing import TYPE_CHECKING, Any

from objects.generic.smoke import Smoke
from objects.projectiles.toxin import Toxin
from util.event_bus import event_bus

if TYPE_CHECKING:
    from objects.entities import Zombie

# the arguments self, frame_time and id are passed in to all effects
# self represents the zombie calling it, and id representing the position of the effect in the zombie's effects property


class EntityEffect(ABC):
    def __init__(self, zombie: Zombie, values: list[dict[str, Any]]) -> None:
        ...

    @abstractmethod
    def execute(self, frame_time: float) -> bool:
        """Return false if effect is over."""
        ...

class EffectValue(ABC):
    def __init__(self, zombie: Zombie, value: Any) -> None:
        self._zombie = zombie
        self._value = value

    @abstractmethod
    def get(self) -> Any:
        ...

class Format(EffectValue):
    def __init__(self, zombie: Zombie, value: Any) -> None:
        super().__init__(zombie, value)
        if not isinstance(self._value, str):
            e = "EffectValue:Format requires a string value."
            raise TypeError(e)
        self._value = self._value.format(self=zombie)

def regen(self: Zombie, frame_time: float, regen: float, **_):
    if self.properties.health < self.properties.max_health:
        self.properties.health += regen * frame_time
        self.update_health_bar()


def spawn_zombie(self: Zombie, spawn_zombie: str, count: int, x: int | None = None, y: int | None = None, **_):
    for i in range(count):
        event_bus.add_event(
            "game_event_bus",
            {
                "spawn_zombie": {
                    "x": x or self.x,
                    "y": y or self.y,
                    "round": 0,
                    "zombie": spawn_zombie,
                    "parent": self,
                },
            },
        )


def initial_velocity(
    self: Zombie,
    frame_time: float,
    id: int,
    x_vel: float,
    y_vel: float,
    decay: float,
    **_,
):  # velocity formula is velocity*decay^seconds_passed
    if abs(x_vel) > 1 or abs(y_vel) > 1:
        decay = 1 - decay
        log_decay = log(decay)
        decay = pow(decay, frame_time)
        self.x += x_vel * (decay / log_decay - 1 / log_decay)
        self.y += y_vel * (decay / log_decay - 1 / log_decay)
        self.effects[id]["values"]["x_vel"]["value"] *= decay
        self.effects[id]["values"]["y_vel"]["value"] *= decay
    else:
        self.remove_effects.append(id)


def invincibility_frames(self: Zombie, frame_time: float, id: int, seconds: float, **_):
    if seconds > 0:
        self.properties.invincible = True
        self.effects[id]["values"]["seconds"]["value"] -= frame_time
    else:
        self.properties.invincible = False
        self.remove_effects.append(id)


def freeze_frames(self: Zombie, frame_time: float, id: int, seconds: float, **_):
    if seconds > 0:
        self.properties.frozen = True
        self.effects[id]["values"]["seconds"]["value"] -= frame_time
    else:
        self.properties.frozen = False
        self.remove_effects.append(id)


def spawn_toxin(self: Zombie, **_):
    x, y, w, h = self.hitbox.get()
    self.projectile_registry.add(Toxin(x + w / 2, y + h / 2, 1, 1))


def create_smoke(self: Zombie, x: float, y: float, size: float, **_):
    event_bus.add_event("generic_registry_l2_bus", Smoke(x, y, size))


def set_attr(self: Zombie, name: str, value: Any, **_):
    setattr(self, name, value)


effect_map = {
    "regen": regen,
    "spawn_zombie": spawn_zombie,
    "initial_velocity": initial_velocity,
    "set_attr": set_attr,
    "invincibility_frames": invincibility_frames,
    "freeze_frames": freeze_frames,
    "spawn_toxin": spawn_toxin,
    "create_smoke": create_smoke,
}
