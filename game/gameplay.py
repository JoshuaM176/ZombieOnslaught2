from registries.entity_registries import ZombieRegistry
from registries.weapon_registries import WeaponRegistry
from registries.bullet_registries import BulletRegistry
from objects.entities import Player

zombie_registry = ZombieRegistry()
weapon_registry = WeaponRegistry()
player_bullet_registry = BulletRegistry(200)
player = Player(200, 500, player_bullet_registry)
for cat, weapon in weapon_registry.get_default_weapons().items():
    player.set_weapon(weapon, cat)
player.set_equipped_weapon("smg")


class Game:
    def __init__(self):
        return

    def update(self, screen, frame_time):
        screen.fill(color=(200, 200, 200))
        player.update(screen, frame_time)
