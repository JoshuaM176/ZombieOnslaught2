import pygame as pg
from util.resource_loading import ResourceLoader, convert_files_to_sprites, load_sprite
from objects.entities import Entity, Zombie
from registries.bullet_registries import BulletRegistry
from registries.weapon_registries import WeaponRegistry
from util.event_bus import event_bus
from util.ui_objects import health_bar


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
            convert_files_to_sprites(self.resources[key]["sprites"], "zombies")
        self.entities: list[Entity] = []

    def update(self, screen: pg.Surface, frame_time):
        # debug
        # for entity in self.entities:
        # entity.head_hitbox.display(screen)
        # entity.hitbox.display(screen)
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
            if not entity.invincible:
                for bullet in bullets.bullets:
                    entity.hit_check(bullet)


class ZombieRegistry(EntityRegistry):
    def __init__(
        self, weapon_registry: WeaponRegistry, bullet_registry: BulletRegistry, screen: pg.Surface
    ):
        super().__init__("zombies")
        self.bullet_registry = bullet_registry
        self.weapon_registry = weapon_registry
        self.orphaned_damage_numbers = []
        self.screen = screen

    def create_zombie(self, x, y, round: int, zombie_type: str, parent):
        zombie = Zombie(
            x,
            y,
            zombie_type,
            self.weapon_registry,
            self.bullet_registry,
            round,
            parent,
            self.entities,
            **self.resources[zombie_type],
        )
        self.register(zombie)
        if parent:
            parent.summoned_zombies.append(zombie)

    def register(self, entity: Entity):
        self.entities.append(entity)
        self.render_plain.add(entity)
        self.render_plain.add(entity.weapon)

    def deregister(self, entity: Entity):
        if entity.damage_number.time > 0:
            self.orphaned_damage_numbers.append(entity.damage_number)
        self.entities.remove(entity)
        self.render_plain.remove(entity)
        self.render_plain.remove(entity.weapon)
        if entity.parent:
            entity.parent.summoned_zombies.remove(entity)

    def clear(self):
        for entity in self.entities:
            self.deregister(entity)

    def update(self, frame_time):
        # debug
        # for entity in self.entities:
        # entity.head_hitbox.display(screen)
        # entity.hitbox.display(screen)
        self.render_plain.update(frame_time, self.screen.get_width(), self.screen.get_height())
        self.render_plain.draw(self.screen)
        expired_orphaned_damage_numbers = []
        for damage_number in self.orphaned_damage_numbers:
            if damage_number.time > 0:
                damage_number.update(frame_time, self.screen)
            else:
                expired_orphaned_damage_numbers.append(damage_number)
        self.orphaned_damage_numbers = [damage_number for damage_number in self.orphaned_damage_numbers if damage_number not in expired_orphaned_damage_numbers]
        for zombie in self.entities:
            zombie.damage_number.update(frame_time, self.screen)
            if zombie.health <= 0:
                event_bus.add_event(
                    "game_end_of_round_bus", {"killed_zombie": {"money": zombie.reward, "zombie": zombie.zombie_type}},
                )
                self.deregister(zombie)
            else:
                x, y, _, _ = zombie.head_hitbox.get()
                health_bar(
                    self.screen, zombie.health, zombie.max_health, x - 16, y - 24, 80, 20
                )
