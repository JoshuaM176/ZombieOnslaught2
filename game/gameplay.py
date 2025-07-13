from registries.entity_registries import ZombieRegistry
from registries.weapon_registries import WeaponRegistry
from registries.bullet_registries import BulletRegistry
from objects.entities import Player
from game.menus import UI
from dataclasses import dataclass, field
from random import choice, uniform
from math import sqrt, floor
from util.event_bus import event_bus
from util.resource_loading import ResourceLoader

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.event_map = {"add_money": self.add_money}
        self.zombie_registry = ZombieRegistry()
        self.weapon_registry = WeaponRegistry()
        self.player_bullet_registry = BulletRegistry(200, screen)
        self.player = Player(200, 500, self.player_bullet_registry)
        for cat, weapon in self.weapon_registry.get_default_weapons().items():
            self.player.set_weapon(weapon, cat)
        self.player.set_equipped_weapon("smg")
        self.ui = UI(screen)
        self.game_info = GameInfo()
        resource_loader = ResourceLoader("game", "attributes")
        resource_loader.load_all()
        self.game_info.spawn_data = resource_loader.get("spawn_rates")


    def update(self, screen, frame_time: float):
        game_event_bus = event_bus.get_events("game_event_bus")
        for event in game_event_bus:
            for event_type, value in event.items():
                self.event_map.get(event_type)(value)
        if self.zombie_registry.is_empty():
            self.new_round(screen)
        screen.fill(color=(150, 150, 150))
        self.zombie_registry.hit_check(self.player_bullet_registry)
        self.player_bullet_registry.update(frame_time)
        self.zombie_registry.update(screen, frame_time)
        self.player.update(screen, frame_time)
        self.ui.update()

    def add_money(self, money):
        self.game_info.money += money

    def new_round(self, screen):
        self.game_info.money+=self.game_info.round
        self.game_info.round+=1
        self.game_info.update_spawn_rates()
        self.generate_zombies(self.game_info.round, screen)

    def generate_zombies(self, round: int, screen):
        for i in range(0,floor(sqrt(round))):
            self.zombie_registry.create_zombie(screen.get_width()+uniform(0,100), uniform(0,screen.get_height()-350), round, choice(self.game_info.pool))

@dataclass
class GameInfo():
    round: int = 0
    money: int = 0
    pool_index: int = 0
    spawn_data: dict = field(default_factory=dict)

    def __post_init__(self):
        self.pool = ["zombie"] * 200

    def update_spawn_rates(self):
        for data in self.spawn_data:
            if self.round >= data.get("start_round") and self.round <= data.get("end_round"):
                func = data["rate"]["function"]
                mult = data["rate"]["mult"]
                match func["name"]:
                    case "flat":
                        for i in range(mult):
                            self.update_pool(data["zombie"])
                    case _:
                        pass

    def update_pool(self, zombie: str):
        self.pool[self.pool_index] = zombie
        self.pool_index += 1
        if self.pool_index >= 200:
            self.pool_index = 0
