from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from math import log
from typing import TYPE_CHECKING, Any, override

from objects.generic.smoke import Smoke
from objects.projectiles.toxin import Toxin
from util.event_bus import event_bus

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from objects.entities import Zombie


class EntityEffect(ABC):
    def __init__(self, zombie: Zombie, values: list[dict[str, Any]]) -> None:
        logger.info(f"Initializing effect: {type(self).__name__}")
        self.zombie = zombie
        values_ = {value["name"]: _get_value(value, zombie) for value in values}
        for name, value in values_.items():
            setattr(self, name, value)

    def value(self, name: str) -> Any:
        try:
            value = getattr(self, name)
        except AttributeError:
            raise AttributeError(f"Missing value: {name} for effect {type(self).__name__}")
        if not isinstance(value, EffectValue):
            raise TypeError(f"Missing value: {name} for effect {type(self).__name__}")
        return value.get()

    def get_value(self, name: str, default: Any = None) -> Any:
        if not hasattr(self, name):
            return default
        return self.value(name)

    @abstractmethod
    def execute(self, frame_time: float) -> bool:
        """Return false if effect is over."""
        ...


def _get_value(value: dict[str, Any], zombie: Zombie) -> EffectValue:
    return {"default": EffectValue, "eval": Eval, "repeat_eval": RepeatEval}[value.get("type", "default")](
        zombie, value["value"]
    )


class EffectValue:
    def __init__(self, zombie: Zombie, value: Any) -> None:
        self._zombie = zombie
        self._value = value

    def get(self) -> Any:
        return self._value


class Eval(EffectValue):
    def __init__(self, zombie: Zombie, value: Any) -> None:
        super().__init__(zombie, value)
        if not isinstance(self._value, str):
            e = "EffectValue:Format requires a string value."
            raise TypeError(e)
        self._value = eval(self._value)


class RepeatEval(EffectValue):
    def __init__(self, zombie: Zombie, value: Any) -> None:
        super().__init__(zombie, value)
        if not isinstance(self._value, str):
            e = "EffectValue:Format requires a string value."
            raise TypeError(e)

    @override
    def get(self) -> Any:
        return eval(self._value)


class Regen(EntityEffect):
    @override
    def execute(self, frame_time: float) -> bool:
        if self.zombie.properties.health < self.zombie.properties.max_health:
            self.zombie.properties.health += self.value("regen") * frame_time
            self.zombie.update_health_bar()
        return True


class SpawnZombie(EntityEffect):
    @override
    def execute(self, frame_time: float) -> bool:
        for i in range(self.value("count")):
            event_bus.add_event(
                "game_event_bus",
                {
                    "spawn_zombie": {
                        "x": self.get_value("x") or self.zombie.x,
                        "y": self.get_value("y") or self.zombie.y,
                        "round": 0,
                        "zombie": self.value("zombie"),
                        "parent": self.zombie,
                    }
                },
            )
        return True


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


class SpawnToxin(EntityEffect):
    @override
    def execute(self, frame_time: float) -> bool:
        x, y, w, h = self.zombie.hitbox.get()
        self.zombie.projectile_registry.add(Toxin(x + w / 2, y + h / 2, 1, 1))
        return True


class CreateSmoke(EntityEffect):
    @override
    def execute(self, frame_time: float) -> bool:
        event_bus.add_event("generic_registry_l2_bus", Smoke(self.value("x"), self.value("y"), self.value("size")))
        return True


class SetAttr(EntityEffect):
    @override
    def execute(self, frame_time: float) -> bool:
        setattr(self.zombie, self.value("name"), self.value("value"))
        return True


effect_map = {
    "create_smoke": CreateSmoke,
    "regen": Regen,
    "set_attr": SetAttr,
    "spawn_toxin": SpawnToxin,
    "spawn_zombie": SpawnZombie,
}
