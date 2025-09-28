from game.screenpage import ScreenPage
from registries.entity_registries import ZombieRegistry
from registries.weapon_registries import WeaponRegistry, weapon_categories
from registries.bullet_registries import BulletRegistry
from objects.entities import Player
from game.game_ui import UI
from game.game_over import GameOver
from game.store import Store
from game.zombiepedia import Zombiepedia
from dataclasses import dataclass, field
from random import choice, uniform
from math import sqrt, floor
from util.event_bus import event_bus
from util.resource_loading import ResourceLoader, save_data
from game.hut import Hut
import pygame as pg


class Game(ScreenPage):
    def __init__(self, screen: pg.Surface):
        resource_loader = ResourceLoader("game", "attributes")
        resource_loader.load_all()
        self.game_info = GameInfo(**resource_loader.get("game_info"))
        super().__init__(screen, "game")
        self.alpha_screen = pg.Surface(screen.get_size(), pg.SRCALPHA)
        self.event_map = {
            "add_money": self.add_money,
            "spawn_zombie": self.create_zombie,
            "set_screen": self.set_screen,
            "reset": self.reset,
            "damage_village": self.damage_village,
            "killed_zombie": self.killed_zombie,
            "save_game": self.save_game
        }
        self.weapon_registry = WeaponRegistry()
        self.zombie_bullet_registry = BulletRegistry(400, self.alpha_screen)
        self.zombie_registry = ZombieRegistry(
            self.weapon_registry, self.zombie_bullet_registry, self.screen
        )
        self.stats = Stats(self.zombie_registry.resources, resource_loader.get("zombies_killed"))
        self.zombiepedia = Zombiepedia(self.screen, self.zombie_registry, self.stats.zombies_killed)
        self.player_bullet_registry = BulletRegistry(200, self.alpha_screen)
        self.player = Player(200, 500, self.player_bullet_registry, self.weapon_registry, screen)
        self.ui = UI(screen)
        self.player.set_equipped_weapon(weapon_categories[0])
        event_bus.add_event("ui_bus", {"money": self.game_info.money})
        self.game_info.spawn_data = resource_loader.get("spawn_rates")
        self.store = Store(
            screen, self.weapon_registry, self.player.weapons, self.game_info
        )
        self.game_over = GameOver(screen)

    def __screen_init__(self):
        self.hut_render_plain = pg.sprite.RenderPlain(())
        self.huts = []
        for i in range(round(self.screen.get_width()/500)):
            hut = Hut(500*i + uniform(0, 100), self.screen.get_height()-250-uniform(0, 50), self.game_info.village_health/self.game_info.max_village_health)
            self.huts.append(hut)
            self.hut_render_plain.add(hut)

    def update(self, frame_time: float):
        self.go2 = self.page_name
        game_event_bus = event_bus.get_events("game_event_bus")
        for event in game_event_bus:
            for event_type, value in event.items():
                self.event_map.get(event_type)(**value)
        if self.zombie_registry.is_empty():
            self.new_round()
        self.screen.fill(color=(150, 150, 150))
        self.alpha_screen.fill((0,0,0,0))
        self.hut_render_plain.draw(self.screen)
        self.zombie_registry.hit_check(self.player_bullet_registry)
        for bullet in self.zombie_bullet_registry.bullets:
            self.player.hit_check(bullet)
        self.player_bullet_registry.update(frame_time)
        self.zombie_registry.update(frame_time)
        self.zombie_bullet_registry.update(frame_time)
        self.screen.blit(self.alpha_screen, (0,0))
        self.player.update(frame_time)
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
        for hut in self.huts:
            hut.reset()

    def killed_zombie(self, money, zombie):
        self.add_money(money)
        self.stats.zombies_killed[zombie]+=1
        if self.stats.zombies_killed[zombie] == 1:
            self.set_screen("zombiepedia")
            self.zombiepedia.set_zombie_buttons()
            self.player.reset_input()

    def add_money(self, money):
        self.game_info.money += money
        event_bus.add_event("ui_bus", {"money": self.game_info.money})

    def damage_village(self, damage):
        self.game_info.village_health -= damage
        event_bus.add_event("ui_bus", {"village_health": self.game_info.village_health})
        for hut in self.huts:
            hut.damage(self.game_info.village_health/self.game_info.max_village_health)
        if self.game_info.village_health <= 0:
            self.end_game()

    def new_round(self):
        end_of_round_event_bus = event_bus.get_events("game_end_of_round_bus")
        for event in end_of_round_event_bus:
            for event_type, value in event.items():
                self.event_map.get(event_type)(**value)
        self.save_game()
        if self.game_info.round == 0:
            self.player.reset()
        self.game_info.money += self.game_info.round
        self.game_info.round += 1
        self.game_info.update_spawn_rates()
        self.generate_zombies(self.game_info.round)
        event_bus.add_event("ui_bus", {"round": self.game_info.round})

    def generate_zombies(self, round: int):
        for i in range(0, floor(sqrt(round))):
            self.create_zombie(
                self.screen.get_width() + uniform(0, 100),
                uniform(0, self.screen.get_height() - 375),
                round + uniform(-5, 5),
                choice(self.game_info.pool),
            )

    def create_zombie(self, x, y, round, zombie):
        self.zombie_registry.create_zombie(x, y, round, zombie)

    def save_game(self):
        game_info = {"game_info": {"money": self.game_info.money}}
        game_info.update({"zombies_killed": self.stats.zombies_killed})
        save_data("game", "attributes", game_info)
        weapon_info = {}
        for cat in weapon_categories:
            for weapon in self.weapon_registry.get_available_weapons(cat):
                weapon_info.update({weapon["name"]: {"player": {"owned": weapon["player"]["owned"]}}})
        save_data("weapons", "attributes", weapon_info)
        player_info = {}
        player_weapons = []
        for cat in self.player.weapons.equipped_list:
            if self.player.weapons.get(cat):
                player_weapons.append({"name": self.player.weapons.get(cat).name, "cat": cat})
        player_info.update({"player": {"equipped_weapons": player_weapons}})
        save_data("player", "attributes", player_info)

        


@dataclass
class GameInfo:
    round: int = 0
    money: int = 0
    pool_index: int = 0
    village_health: int = 10
    spawn_data: dict = field(default_factory=dict)

    def __post_init__(self):
        self.pool = ["zombie"] * 200
        self.max_village_health = self.village_health
        event_bus.add_event("ui_bus", {"village_health": self.village_health, "max_village_health": self.max_village_health})

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
        self.village_health = self.max_village_health

@dataclass
class Stats:
    resources: dict
    zombies_killed: dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
       for key in self.resources.keys():
           if key not in self.zombies_killed.keys():
               self.zombies_killed[key] = 0