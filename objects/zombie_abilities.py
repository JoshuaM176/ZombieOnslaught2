# all abilities should take self representing the zombie calling it, frame_time even if unused, followed by an other arguments

def regen(self, frame_time, regen):
    if self.health < self.max_health:
        self.health += regen * frame_time

ability_map = {
    "regen": regen
}