import pygame as pg

from util.resource_loading import load_sprite


def convert_file_to_sprite(file: str, category: str, scale: int = 8) -> pg.Surface:
    return load_sprite(file, category, -1, scale)
