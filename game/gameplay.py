from game.screenpage import ScreenPage
from registries.entity_registries import ZombieRegistry
from registries.weapon_registries import WeaponRegistry, weapon_categories
from registries.projectile_registries import ProjectileRegistry
from registries.generic_registries import GenericRegistry
from objects.entities import Player
from game.game_ui import UI
from game.game_over import GameOver
from game.store import Store
from game.settings.settings import Settings
from game.zombiepedia import Zombiepedia
from dataclasses import dataclass, field
from random import choice, uniform
from math import sqrt, floor
from util.event_bus import event_bus
from util.resource_loading import ResourceLoader, save_data
from util.ui_objects import FloatingNumber
from game.hut import Hut
import pygame as pg

class Game(ScreenPage):
    def __init__(self, screen: pg.Surface):
        resource_loader = ResourceLoader("game", "attributes")
        resource_loader.load_all()
        super().__init__(screen, "game", screen_init=False)
        self.alpha_screen = pg.Surface(screen.get_size(), pg.SRCALPHA)
        self.money_number = FloatingNumber(2, size=25, color=(0, 200, 0))
        self._create_registries()
        self._game_prop_init(resource_loader)
        self._create_player()
        self._create_screens(resource_loader)
        self.__screen_init__()

    def _create_registries(self):
        self.generic_registry = GenericRegistry(self.screen, self.alpha_screen)
        self.weapon_registry = WeaponRegistry()
        self.zombie_projectile_registry = ProjectileRegistry(400, self.screen, self.alpha_screen)
        self.zombie_registry = ZombieRegistry(self.weapon_registry, self.zombie_projectile_registry, self.generic_registry, self.screen)
        self.player_projectile_registry = ProjectileRegistry(200, self.screen, self.alpha_screen)

    def _game_prop_init(self, rsrc_ldr: ResourceLoader):
        self.event_map = {
            "add_money": self.add_money,
            "spawn_zombie": self.create_zombie,
            "set_screen": self.set_screen,
            "reset": self.reset,
            "damage_village": self.damage_village,
            "killed_zombie": self.killed_zombie,
            "save_game": self.save_game,
        }
        self.game_info = GameInfo(**rsrc_ldr.get("game_info"))
        self.stats = Stats(self.zombie_registry.resources, **rsrc_ldr.get("stats"))
        self.settings = Settings(self.screen, rsrc_ldr.get("settings")).settings_data

    def _create_player(self):
        player_key_map = self.settings.player_key_map
        self.player = Player(200, 500, self.player_projectile_registry, self.weapon_registry, self.generic_registry, player_key_map, self.screen)
        self.player.set_equipped_weapon(weapon_categories[0])

    def _create_screens(self, rsrc_ldr: ResourceLoader):
        self.game_over = GameOver(self.screen)
        self.store = Store(self.screen, self.weapon_registry, self.player.weapons, self.game_info)
        self.zombiepedia = Zombiepedia(self.screen, self.zombie_registry, self.stats.zombies_killed, **rsrc_ldr.get("zombiepedia"))

    def _ui_init(self):
        if hasattr(self, "ui"):
            curr_ui = self.ui.data
            event_bus.add_event("ui_bus", curr_ui)
        self.ui = UI(self.screen)

    def __screen_init__(self):
        self._ui_init()
        self.hut_render_plain = pg.sprite.RenderPlain(())
        self.huts = []
        for i in range(round(self.screen.get_width() / 500)):
            hut = Hut(
                500 * i + uniform(0, 100),
                self.screen.get_height() - 250 - uniform(0, 50),
                self.game_info.village_health / self.game_info.max_village_health,
            )
            self.huts.append(hut)
            self.hut_render_plain.add(hut)
        self.rect = pg.Rect(0, 0, self.screen.get_width(), self.screen.get_height() - 250)

    def update(self, frame_time: float):
        self.go2 = self.page_name
        game_event_bus = event_bus.get_events("game_event_bus")
        for event in game_event_bus:
            for event_type, value in event.items():
                self.event_map.get(event_type)(**value)
        if self.zombie_registry.is_empty():
            self.new_round()
        self.screen.fill(color=(150, 150, 150), rect=self.rect)
        self.alpha_screen.fill((0, 0, 0, 0), rect=self.rect)
        self.hut_render_plain.draw(self.screen)
        self.generic_registry.update(frame_time)
        self.zombie_registry.hit_check(self.player_projectile_registry)
        for projectile in self.zombie_projectile_registry.projectiles:
            self.player.hit_check(projectile)
        self.player_projectile_registry.update(frame_time)
        self.zombie_registry.update(frame_time)
        self.zombie_projectile_registry.update(frame_time)
        self.screen.blit(self.alpha_screen, (0, 0))
        self.player.update(frame_time)
        self.ui.update()
        self.money_number.update(frame_time, self.screen)
        if self.player.properties.health < 0:
            self.end_game()
        return self.go2

    def end_game(self):
        self.reset()
        self.set_screen("game_over")

    def reset(self):
        self.zombie_registry.clear()
        self.game_info.reset()
        self.player.reset()
        for hut in self.huts:
            hut.reset()

    def killed_zombie(self, money: float, zombie):
        self.add_money(money)
        self.stats.zombies_killed[zombie] += 1
        if self.stats.zombies_killed[zombie] == 1 and zombie in self.zombiepedia.zombie_list:
            self.set_screen("zombiepedia")
            self.zombiepedia.set_zombie_buttons()
            self.zombiepedia.select_zombie(zombie)
            self.player.reset_input()

    def add_money(self, money: float):
        self.game_info.money += money
        self.money_number.add(140, self.screen.get_height() - 250, money)
        event_bus.add_event("ui_bus", {"money": self.game_info.money})

    def damage_village(self, damage: float):
        self.game_info.village_health -= damage
        event_bus.add_event("ui_bus", {"village_health": self.game_info.village_health})
        for hut in self.huts:
            hut.damage(self.game_info.village_health / self.game_info.max_village_health)
        if self.game_info.village_health <= 0:
            self.end_game()

    def new_round(self):
        end_of_round_event_bus = event_bus.get_events("game_end_of_round_bus")
        for event in end_of_round_event_bus:
            for event_type, value in event.items():
                self.event_map.get(event_type)(**value)
        self.save_game()
        self.game_info.money += self.game_info.round
        self.game_info.round += 1
        self.game_info.update_spawn_rates()
        self.generate_zombies()
        event_bus.add_event("ui_bus", {"round": self.game_info.round})

    def generate_zombies(self):
        set_round = self.game_info.set_rounds.get(str(self.game_info.round))
        if set_round:
            for zombie in set_round["zombies"]:
                self.create_zombie(**zombie)
            if set_round.get("replace"):
                return
        for i in range(0, floor(sqrt(self.game_info.round))):
            self.create_zombie(
                zombie=choice(self.game_info.pool),
            )

    def create_zombie(self, x=None, y=None, round=None, zombie="zombie", parent=None):
        x = self.screen.get_width() + uniform(0, 100) if x is None else x
        y = uniform(0, self.screen.get_height() - 375) if y is None else y
        round = self.game_info.round + uniform(-5, 5) if round is None else round
        self.zombie_registry.create_zombie(x, y, round, zombie, parent)

    def save_game(self):
        game_info = {"game_info": {"money": self.game_info.money}}
        game_info.update({"stats": {"zombies_killed": self.stats.zombies_killed}})
        game_info.update({"settings": {"key_map": self.settings.key_map}})
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
                player_weapons.append({"name": self.player.weapons.get(cat).properties.name, "cat": cat})
        player_info.update({"player": {"equipped_weapons": player_weapons}})
        save_data("player", "attributes", player_info)


@dataclass
class GameInfo:
    round: int = 0
    money: int = 0
    pool_index: int = 0
    village_health: int = 10
    spawn_data: dict = field(default_factory=dict)
    set_rounds: dict = field(default_factory=dict)

    def __post_init__(self):
        self.pool = ["zombie"] * 200
        self.max_village_health = self.village_health
        self.set_ui()

    def update_spawn_rates(self):
        for data in self.spawn_data:
            if self.round >= data.get("start_round") and self.round <= data.get("end_round"):
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
        self.round = 0
        self.pool_index = 0
        self.pool = ["zombie"] * 200
        self.village_health = self.max_village_health
        self.set_ui()

    def set_ui(self):
        event_bus.add_event(
            "ui_bus",
            {
                "money": self.money,
                "round": self.round,
                "village_health": self.village_health,
                "max_village_health": self.max_village_health,
            },
        )


@dataclass
class Stats:
    resources: dict
    zombies_killed: dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        for key in self.resources.keys():
            if key not in self.zombies_killed.keys():
                self.zombies_killed[key] = 0
