from util.event_bus import event_bus
from math import log
from objects.projectiles.toxin import Toxin
from objects.generic.smoke import Smoke

# the arguments self, frame_time and id are passed in to all effects
# self represents the zombie calling it, and id representing the position of the effect in the zombie's effects property


def regen(self, frame_time, regen, **_):
    if self.properties.health < self.properties.max_health:
        self.properties.health += regen * frame_time
        self.update_health_bar()


def spawn_zombie(self, spawn_zombie, count, x=None, y=None, **_):
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
                }
            },
        )


def initial_velocity(
    self, frame_time, id, x_vel, y_vel, decay, **_
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


def invincibility_frames(self, frame_time, id, seconds, **_):
    if seconds > 0:
        self.properties.invincible = True
        self.effects[id]["values"]["seconds"]["value"] -= frame_time
    else:
        self.properties.invincible = False
        self.remove_effects.append(id)


def freeze_frames(self, frame_time, id, seconds, **_):
    if seconds > 0:
        self.properties.frozen = True
        self.effects[id]["values"]["seconds"]["value"] -= frame_time
    else:
        self.properties.frozen = False
        self.remove_effects.append(id)

def spawn_toxin(self, **_):
    x, y, w, h = self.hitbox.get()
    self.projectile_registry.add(Toxin(x + w/2, y + h/2, 1, 1))

def create_smoke(self, x, y, size, **_):
    _, _, w, h = self.hitbox.get()
    event_bus.add_event("generic_registry_l2_bus", Smoke(x, y, size))

def set_attr(self, name, value, **_):
    setattr(self, name, value)


effect_map = {
    "regen": regen,
    "spawn_zombie": spawn_zombie,
    "initial_velocity": initial_velocity,
    "set_attr": set_attr,
    "invincibility_frames": invincibility_frames,
    "freeze_frames": freeze_frames,
    "spawn_toxin": spawn_toxin,
    "create_smoke": create_smoke
}
