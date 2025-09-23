from game.screenpage import ScreenPage
from registries.entity_registries import ZombieRegistry
from registries.weapon_registries import WeaponRegistry, weapon_categories
from registries.bullet_registries import BulletRegistry
from objects.entities import Player
from game.game_ui import UI
from game.game_over import GameOver
from game.store import Store
from dataclasses import dataclass, field
from random import choice, uniform
from math import sqrt, floor
from util.event_bus import event_bus
from util.resource_loading import ResourceLoader, save_data


class Game(ScreenPage):
    def __init__(self, screen):
        super().__init__(screen, "game")
        self.event_map = {
            "add_money": self.add_money,
            "spawn_zombie": self.create_zombie,
            "set_screen": self.set_screen,
            "reset": self.reset,
        }
        self.weapon_registry = WeaponRegistry()
        self.zombie_bullet_registry = BulletRegistry(400, screen)
        self.zombie_registry = ZombieRegistry(
            self.weapon_registry, self.zombie_bullet_registry
        )
        self.player_bullet_registry = BulletRegistry(200, screen)
        self.player = Player(200, 500, self.player_bullet_registry)
        for cat, weapon in self.weapon_registry.get_default_weapons().items():
            self.player.set_weapon(weapon, cat)
        self.ui = UI(screen)
        self.player.set_equipped_weapon(weapon_categories[0])
        resource_loader = ResourceLoader("game", "attributes")
        resource_loader.load_all()
        self.game_info = GameInfo(**resource_loader.get("game_info"))
        event_bus.add_event("ui_bus", {"money": self.game_info.money})
        self.game_info.spawn_data = resource_loader.get("spawn_rates")
        self.store = Store(
            screen, self.weapon_registry, self.player.weapons, self.game_info
        )
        self.game_over = GameOver(screen)

    def update(self, screen, frame_time: float):
        self.go2 = self.page_name
        game_event_bus = event_bus.get_events("game_event_bus")
        for event in game_event_bus:
            for event_type, value in event.items():
                self.event_map.get(event_type)(**value)
        if self.zombie_registry.is_empty():
            self.new_round(screen)
        screen.fill(color=(150, 150, 150))
        self.zombie_registry.hit_check(self.player_bullet_registry)
        for bullet in self.zombie_bullet_registry.bullets:
            self.player.hit_check(bullet)
        self.player_bullet_registry.update(frame_time)
        self.zombie_registry.update(screen, frame_time)
        self.zombie_bullet_registry.update(frame_time)
        self.player.update(screen, frame_time)
        self.ui.update()
        if self.player.health < 0:
            self.end_game()
        return self.go2

    def end_game(self):
        self.reset()
        self.set_screen("game_over")

    def reset(self):
        self.game_info.round = 0
        self.zombie_registry.clear()
        self.game_info.reset()

    def add_money(self, money):
        self.game_info.money += money
        event_bus.add_event("ui_bus", {"money": self.game_info.money})

    def new_round(self, screen):
        self.save_game()
        if self.game_info.round == 0:
            self.player.reset()
        self.game_info.money += self.game_info.round
        self.game_info.round += 1
        self.game_info.update_spawn_rates()
        self.generate_zombies(self.game_info.round, screen)
        event_bus.add_event("ui_bus", {"round": self.game_info.round})

    def generate_zombies(self, round: int, screen):
        for i in range(0, floor(sqrt(round))):
            self.create_zombie(
                screen.get_width() + uniform(0, 100),
                uniform(0, screen.get_height() - 375),
                round + uniform(-5, 5),
                choice(self.game_info.pool),
            )

    def create_zombie(self, x, y, round, zombie):
        self.zombie_registry.create_zombie(x, y, round, zombie)

    def save_game(self):
        game_info = {"game_info": {"money": self.game_info.money}}
        save_data("game", "attributes", game_info)
        weapon_info = {}
        for cat in weapon_categories:
            for weapon in self.weapon_registry.get_available_weapons(cat):
                weapon_info.update({weapon["name"]: {"player": {"owned": weapon["player"]["owned"]}}})
        save_data("weapons", "attributes", weapon_info)


@dataclass
class GameInfo:
    round: int = 0
    money: int = 0
    pool_index: int = 0
    spawn_data: dict = field(default_factory=dict)

    def __post_init__(self):
        self.pool = ["zombie"] * 200

    def update_spawn_rates(self):
        for data in self.spawn_data:
            if self.round >= data.get("start_round") and self.round <= data.get(
                "end_round"
            ):
                func = data["rate"]["function"]
                mult = data["rate"]["mult"]
                match func["name"]:
                    case "flat":
                        for i in range(mult):
                            self.update_pool(data["zombie"])
                    case "slope_up":
                        rounds_passed = self.round - data.get("start_round")
                        for i in range(round(mult * rounds_passed)):
                            self.update_pool(data["zombie"])
                    case "slope_down":
                        rounds_left = data.get("end_round") - self.round
                        for i in range(round(mult * rounds_left)):
                            self.update_pool(data["zombie"])
                    case _:
                        pass
        if False:
            zombies = set(self.pool)
            for zombie in zombies:
                print(f"{zombie}: {self.pool.count(zombie) / len(self.pool)}")

    def update_pool(self, zombie: str):
        self.pool[self.pool_index] = zombie
        self.pool_index += 1
        if self.pool_index >= 200:
            self.pool_index = 0

    def reset(self):
        self.pool_index = 0
        self.pool = ["zombie"] * 200
