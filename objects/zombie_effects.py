from util.event_bus import event_bus
from math import log

# all abilities should take self representing the zombie calling it, frame_time, id, even if unused, followed by an other arguments


def regen(self, frame_time, regen, **_):
    if self.health < self.max_health:
        self.health += regen * frame_time


def spawn_zombie(self, spawn_zombie, count, **_):
    for i in range(count):
        event_bus.add_event(
            "game_event_bus",
            {
                "spawn_zombie": {
                    "x": self.x,
                    "y": self.y,
                    "round": 0,
                    "zombie": spawn_zombie,
                }
            },
        )


def initial_velocity(
    self, frame_time, id, x_vel, y_vel, decay, **_
):  # velocity formula is velocity*decay^seconds_passed
    if x_vel > 1 or y_vel > 1:
        decay = 1 - decay
        log_decay = log(decay)
        decay = pow(decay, frame_time)
        self.x += x_vel * (decay / log_decay - 1 / log_decay)
        self.y += y_vel * (decay / log_decay - 1 / log_decay)
        self.effects[id]['values']['x_vel']['value'] *= decay
        self.effects[id]['values']['y_vel']['value'] *= decay


effect_map = {
    "regen": regen,
    "spawn_zombie": spawn_zombie,
    "initial_velocity": initial_velocity,
}
