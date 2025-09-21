import pygame as pg
from util.resource_loading import ResourceLoader
import pandas as pd
from matplotlib import pyplot as plt

pg.init()
screen = pg.display.set_mode((1920, 1080))
from game.gameplay import GameInfo #noqa

resource_loader = ResourceLoader("game", "attributes")
resource_loader.load_all()
spawn_data = resource_loader.get("spawn_rates")

psuedo_game_info = GameInfo()
psuedo_game_info.spawn_data = spawn_data
zombies = set()
for spawn in spawn_data:
    zombies.add(spawn["zombie"])

df = pd.DataFrame(columns=list(zombies))
for i in range(100):
    psuedo_game_info.round += 1
    psuedo_game_info.update_spawn_rates()
    for zombie in zombies:
        df.loc[i, zombie] = psuedo_game_info.pool.count(zombie)/len(psuedo_game_info.pool)

for zombie in zombies:
    plt.plot(df[:][zombie], label = zombie)
    plt.legend()
plt.show()