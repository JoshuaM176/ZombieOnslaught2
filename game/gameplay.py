from registries.entity_registries import ZombieRegistry
from registries.weapon_registries import WeaponRegistry
from registries.bullet_registries import BulletRegistry
from objects.entities import Player


class Game:
    def __init__(self, screen):
        self.zombie_registry = ZombieRegistry()
        self.weapon_registry = WeaponRegistry()
        self.player_bullet_registry = BulletRegistry(200, screen)
        self.player = Player(200, 500, self.player_bullet_registry)
        for cat, weapon in self.weapon_registry.get_default_weapons().items():
            self.player.set_weapon(weapon, cat)
        self.player.set_equipped_weapon("smg")

    def update(self, screen, frame_time):
        screen.fill(color=(150, 150, 150))
        self.player_bullet_registry.update(frame_time)
        self.player.update(screen, frame_time)
