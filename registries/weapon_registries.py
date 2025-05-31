from util.resource_loading import ResourceLoader, load_sprite
import pygame as pg
#Fire animation length needs added back to json

def get_convert_file_to_sprite(resource: dict):
    return

class WeaponRegistry():
    def __init__(self):
        self.render_plain=pg.sprite.RenderPlain(())
        resource_loader = ResourceLoader("weapons", "attributes")
        resource_loader.load_all()
        resource_loader.set_defaults()
        self.resources = resource_loader.get_all()
        return