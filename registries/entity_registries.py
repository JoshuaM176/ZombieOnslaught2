import pygame as pg
from util.resource_loading import ResourceLoader, load_sprite
from objects.entities import Entity, Zombie
from registries.bullet_registries import BulletRegistry
from registries.weapon_registries import WeaponRegistry


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

    def update(self, screen: pg.Surface, frame_time):
        #debug
        #for entity in self.entities:
            #entity.head_hitbox.display(screen)
            #entity.hitbox.display(screen)
        self.render_plain.update(frame_time)
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
        if len(self.entities) > 0:
            return False
        return True
    
    def hit_check(self, bullets: BulletRegistry):
        for entity in self.entities:
            for bullet in bullets.bullets:
                if bullet is not None and bullet.damage > 0:
                    if entity not in bullet.recent_hits:
                        if entity.head_hitbox.check(bullet.x, bullet.y):
                            entity.hit(bullet.damage*bullet.head_mult)
                            bullet.hit(entity)
                        elif entity.hitbox.check(bullet.x, bullet.y):
                            entity.hit(bullet.damage)
                            bullet.hit(entity)


class ZombieRegistry(EntityRegistry):
    def __init__(self, weapon_registry: WeaponRegistry, bullet_registry: BulletRegistry):
        super().__init__("zombies")
        self.bullet_registry = bullet_registry
        self.weapon_registry = weapon_registry

    def create_zombie(self, x, y, round: int, zombie_type: str):
        zombie = Zombie(x, y, round, **self.resources[zombie_type])
        self.register(zombie)

    def update(self, screen: pg.Surface, frame_time):
        #debug
        #for entity in self.entities:
            #entity.head_hitbox.display(screen)
            #entity.hitbox.display(screen)
        self.render_plain.update(frame_time)
        self.render_plain.draw(screen)
        for zombie in self.entities:
            if zombie.health <= 0:
                self.deregister(zombie)
            else:
                x, y, _, _ = zombie.head_hitbox.get()
                pg.draw.rect(screen, (0,255,0), (x - 16, y - 24, zombie.health/zombie.max_health*80, 20))
                pg.draw.rect(screen, (0,0,0), (x - 16, y - 24, 80, 20), 1)
                font = pg.font.Font(pg.font.get_default_font(), 20)
                text = font.render(str(round(zombie.health)), 1, (0,0,0))
                text_rect = text.get_rect(center=(x+24, y-14))
                screen.blit(text, text_rect)
                
