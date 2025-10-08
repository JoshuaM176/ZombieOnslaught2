import pygame as pg
from util.resource_loading import ResourceLoader
import pandas as pd
from matplotlib import pyplot as plt

pg.init()
screen = pg.display.set_mode((1920, 1080))
from game.gameplay import GameInfo  # noqa

resource_loader = ResourceLoader("game", "attributes")
resource_loader.load_all()
spawn_data = resource_loader.get("game_info")["spawn_data"]

pool = ["zombie"] * 200
pool_index = 0
curr_round = 0

def update_pool(zombie: str):
        global pool
        global pool_index
        pool[pool_index] = zombie
        pool_index += 1
        if pool_index >= 200:
            pool_index = 0

def update_spawn_rates():
        global pool
        global pool_index
        for data in spawn_data:
            if curr_round >= data.get("start_round") and curr_round <= data.get(
                "end_round"
            ):
                func = data["rate"]["function"]
                mult = data["rate"]["mult"]
                match func["name"]:
                    case "flat":
                        for i in range(mult):
                            update_pool(data["zombie"])
                    case "slope_up":
                        rounds_passed = curr_round - data.get("start_round")
                        for i in range(round(mult * rounds_passed)):
                            update_pool(data["zombie"])
                    case "slope_down":
                        rounds_left = data.get("end_round") - curr_round
                        for i in range(round(mult * rounds_left)):
                            update_pool(data["zombie"])
                    case _:
                        pass
zombies = set()
for spawn in spawn_data:
    zombies.add(spawn["zombie"])

df = pd.DataFrame(columns=list(zombies))
for i in range(200):
    curr_round += 1
    update_spawn_rates()
    for zombie in zombies:
        df.loc[i, zombie] = pool.count(zombie) / len(
            pool
        )

for zombie in zombies:
    plt.plot(df[:][zombie], label=zombie)
    plt.legend()
plt.show()
