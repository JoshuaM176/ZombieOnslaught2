import pygame as pg
from util.event_bus import event_bus
from registries.entity_registries import ZombieRegistry
from objects.entities import Player

zombie_registry = ZombieRegistry()
player = Player(200, 500)

class Game():

    def __init__(self):
        return

    def update(self, screen):
        player.update(screen)