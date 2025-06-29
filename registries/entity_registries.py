import pygame as pg
from util.resource_loading import ResourceLoader, load_sprite
from objects.entities import Entity, Zombie


class EntityRegistry:
    def __init__(self, entity_type: str):
        self.render_plain = pg.sprite.RenderPlain(())
        resource_loader = ResourceLoader(entity_type, "attributes")
        resource_loader.load_all()
        resource_loader.set_defaults()
        self.resources = resource_loader.get_all()
        for key in self.resources.keys():
            self.resources[key]["sprite"] = load_sprite(
                self.resources[key]["sprite"], entity_type, -1
            )
        self.entities: list[Entity] = []

    def update(self, screen: pg.Surface):
        self.render_plain.update()
        self.render_plain.draw(screen)

    def register(self, entity: Entity):
        self.entities.append(entity)
        self.render_plain.add(entity)

    def deregister(self, entity: Entity):
        self.entities.remove(entity)
        self.render_plain.remove(entity)

    def get(self):
        return self.entities

    def is_empty(self):
        if len(self.entities > 0):
            return False
        return True


class ZombieRegistry(EntityRegistry):
    def __init__(self):
        super().__init__("zombies")

    def create_zombie(self, x, y, zombie_type: str):
        zombie = Zombie(x, y, True, **self.resources[zombie_type])
        self.register(zombie)
