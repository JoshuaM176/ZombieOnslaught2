import pygame as pg
from pathlib import Path
import json
import os
import shutil
from copy import deepcopy

ROOT = os.path.abspath(os.curdir)
save_profile = "default"


def set_save_profile(profile):
    global save_profile
    save_profile = profile

def delete_save_profile(profile):
    path = Path(ROOT, "saves", profile)
    if path.exists():
        shutil.rmtree(Path(ROOT, "saves", profile))


def load_sprite(name: str, category: str, colorkey=None, scale=8):
    fullname = Path(ROOT, "resources", "textures", category, name)
    image = pg.image.load(fullname)
    size = image.get_size()
    size = (size[0] * scale, size[1] * scale)
    image = pg.transform.scale(image, size)
    image = image.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pg.RLEACCEL)
    return image


def save_data(resource, location, data):
    os.makedirs(Path(ROOT, "saves", save_profile, location, resource), exist_ok=True)
    path = Path(ROOT, "saves", save_profile, location, resource, "save.json")
    with open(path, "w") as f:
        json.dump(data, f)


class ResourceLoader:
    def __init__(self, resource: str, location: str):
        self.resources = {}
        self.save_resources = {}
        path = Path(ROOT, "resources", location, resource)
        save_path = Path(ROOT, "saves", save_profile, location, resource)
        self.files = path.glob("*json")
        self.save_files = save_path.glob("*json")

    def load(self, path: Path):
        with open(path, "r") as f:
            data = json.load(f)
        for key, value in data.items():
            self.resources[key] = value

    def load_all(self):
        for file in self.files:
            self.load(file)
        for file in self.save_files:
            with open(file, "r") as f:
                save_data = json.load(f)
            for key in save_data.keys():
                self.resources[key] = self.update(self.resources[key], save_data[key])

    def update(self, data: dict, new_data: dict):
        rtn_data = deepcopy(data)
        for key, value in new_data.items():
            if isinstance(new_data[key], dict):
                if rtn_data.get(key) is not None:
                    rtn_data[key] = self.update(rtn_data[key], new_data[key])
                else:
                    rtn_data[key] = new_data[key]
            else:
                rtn_data[key] = value
        return rtn_data

    def set_defaults(self):
        for key in self.resources.keys():
            self.resources[key] = self.update(
                self.resources["default"], self.resources[key]
            )

    def get(self, name: str):
        return self.resources[name]

    def get_all(self):
        return self.resources
