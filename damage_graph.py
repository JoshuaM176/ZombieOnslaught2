import pygame as pg
from util.resource_loading import ResourceLoader
import pandas as pd
from matplotlib import pyplot as plt

pg.init()
screen = pg.display.set_mode((1920, 1080))

resource_loader = ResourceLoader("weapons", "attributes")
resource_loader.load_all()
resource_loader.set_defaults()
weapons = resource_loader.get_all()

weapon_names = []
df = pd.DataFrame()

if True:
    for weapon, data in [data for data in weapons.items() if data[1]["properties"]["type"] in ("rifle", "sniper")]:
        weapon_names.append(weapon)
        for i in range(2000):
            df.loc[i, weapon] = (
                (
                    data["projectile"]["damage"]
                    - data["projectile"]["dropoff"] * i / data["projectile"]["speed"]
                )
                * data["properties"]["projectile_count"]
                * data["properties"]["firerate"]
                / 60
            )

if False:
    for weapon, data in [data for data in weapons.items() if data[1]["properties"]["type"] in ("rifle")]:
        weapon_names.append(weapon)
        if data["ammo"]["reload_type"] == 0:
            total_time = (
                data["ammo"]["bullets"] / data["weapon"]["firerate"] * 60
                + data["ammo"]["reload_time"]
            )
        elif data["ammo"]["reload_type"] == 1:
            total_time = (
                data["ammo"]["bullets"] / data["properties"]["firerate"] * 60
                + data["ammo"]["reload_time"] * data["ammo"]["bullets"]
            )
        for i in range(2000):
            df.loc[i, weapon] = (
                (
                    data["projectile"]["damage"]
                    - data["projectile"]["dropoff"] * i / data["projectile"]["speed"]
                )
                * data["properties"]["projectile_count"]
                * data["ammo"]["bullets"]
                / total_time
            )



for weapon in weapon_names:
    plt.plot(df[:][weapon], label=weapon)
    plt.ylim((0, 500))
    plt.legend()
plt.show()
