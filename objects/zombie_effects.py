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
        object.__setattr__(self, "_values", {})
        logger.info(f"Initializing effect: {type(self).__name__}")
        self.zombie = zombie
        self._values: dict[str, EffectValue] = {value["name"]: _get_value(value, zombie) for value in values}

    def __getattr__(self, name: str) -> Any:
        if name in self._values:
            return self._values[name].get()
        raise AttributeError(f"Missing effect value: {name}")

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self._values:
            self._values[name].set_value(value)
        else:
            object.__setattr__(self, name, value)

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

    def set_value(self, value: Any) -> None:
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
    regen: float

    @override
    def execute(self, frame_time: float) -> bool:
        if self.zombie.properties.health < self.zombie.properties.max_health:
            self.zombie.properties.health += self.regen * frame_time
            self.zombie.update_health_bar()
        return True


class SpawnZombie(EntityEffect):
    x: float
    y: float
    count: int
    zombie_type: str

    @override
    def execute(self, frame_time: float) -> bool:
        for i in range(self.count):
            event_bus.add_event(
                "game_event_bus",
                {
                    "spawn_zombie": {
                        "x": self.x,
                        "y": self.y,
                        "round": 0,
                        "zombie": self.zombie_type,
                        "parent": self.zombie,
                    }
                },
            )
        return True


class Velocity(EntityEffect):
    decay: float
    x_vel: float
    y_vel: float

    @override
    def execute(self, frame_time: float) -> bool:
        # velocity formula is velocity*decay^seconds_passed
        # using derivative to calc dist
        if abs(self.x_vel) > 1 or abs(self.y_vel) > 1:
            decay = 1 - self.decay
            log_decay = log(decay)
            decay = pow(decay, frame_time)
            self.zombie.x += self.x_vel * (decay / log_decay - 1 / log_decay)
            self.zombie.y += self.y_vel * (decay / log_decay - 1 / log_decay)
            self.effects[id]["values"]["x_vel"]["value"] *= decay
            self.effects[id]["values"]["y_vel"]["value"] *= decay
            return True
        return False


class Invincibility(EntityEffect):
    seconds: float

    @override
    def execute(self, frame_time: float) -> bool:
        if self.seconds > 0:
            self.zombie.properties.invincible = True
            self.seconds -= frame_time
            return True
        self.zombie.properties.invincible = False
        return False


class Freeze(EntityEffect):
    seconds: float

    @override
    def execute(self, frame_time: float) -> bool:
        if self.seconds > 0:
            self.zombie.properties.frozen = True
            self.seconds -= frame_time
            return True
        self.zombie.properties.frozen = False
        return False


class SpawnToxin(EntityEffect):
    @override
    def execute(self, frame_time: float) -> bool:
        x, y, w, h = self.zombie.hitbox.get()
        self.zombie.projectile_registry.add(Toxin(x + w / 2, y + h / 2, 1, 1))
        return True


class CreateSmoke(EntityEffect):
    x: float
    y: float
    size: int

    @override
    def execute(self, frame_time: float) -> bool:
        event_bus.add_event("generic_registry_l2_bus", Smoke(self.x, self.y, self.size))
        return True


class SetAttr(EntityEffect):
    name: str
    value: Any

    @override
    def execute(self, frame_time: float) -> bool:
        setattr(self.zombie, self.name, self.value)
        return True


effect_map = {
    "create_smoke": CreateSmoke,
    "freeze": Freeze,
    "invincibility": Invincibility,
    "regen": Regen,
    "set_attr": SetAttr,
    "spawn_toxin": SpawnToxin,
    "spawn_zombie": SpawnZombie,
    "velocity": Velocity,
}
