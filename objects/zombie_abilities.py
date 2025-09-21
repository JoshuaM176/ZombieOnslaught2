from util.event_bus import event_bus
from math import log

# all abilities should take self representing the zombie calling it, frame_time even if unused, followed by an other arguments


def regen(self, frame_time, regen):
    if self.health < self.max_health:
        self.health += regen * frame_time


def spawn_zombie(self, _, spawn_zombie, count):
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
    self, frame_time, x_vel, y_vel, decay
):  # velocity formula is velocity*decay^seconds_passed
    if self.x_vel > 1 or self.y_vel > 1:
        decay = 1 - decay
        log_decay = log(decay)
        decay = pow(decay, frame_time)
        self.x += self.x_vel * (decay / log_decay - 1 / log_decay)
        self.y += self.y_vel * (decay / log_decay - 1 / log_decay)
        self.x_vel *= decay
        self.y_vel *= decay


ability_map = {
    "regen": regen,
    "spawn_zombie": spawn_zombie,
    "initial_velocity": initial_velocity,
}
