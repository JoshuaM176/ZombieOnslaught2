import pygame as pg
from util.resource_loading import ResourceLoader, convert_files_to_sprites, load_sprite
from objects.entities import Entity, Zombie
from registries.projectile_registries import ProjectileRegistry
from registries.weapon_registries import WeaponRegistry
from util.event_bus import event_bus

class EntityRegistry:
    def __init__(self, entity_type: str):
        self.render_plain = pg.sprite.RenderPlain(())
        resource_loader = ResourceLoader(entity_type, "attributes")
        resource_loader.load_all()
        resource_loader.set_defaults()
        self.resources = resource_loader.get_all()
        for key, item in self.resources.items():
            item["properties"]["name"] = key
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
    
    def clear(self):
        for i in range(len(self.entities)-1, -1, -1):
            self.deregister(self.entities[i])

    def hit_check(self, projectiles: ProjectileRegistry):
        for entity in self.entities:
            if not entity.properties.invincible:
                for bullet in projectiles.projectiles:
                    entity.hit_check(bullet)


class ZombieRegistry(EntityRegistry):
    def __init__(
        self,
        weapon_registry: WeaponRegistry,
        projectile_registry: ProjectileRegistry,
        screen: pg.Surface,
    ):
        super().__init__("zombies")
        self.projectile_registry = projectile_registry
        self.weapon_registry = weapon_registry
        self.orphaned_damage_numbers = []
        self.screen = screen

    def create_zombie(self, x, y, round: int, zombie_type: str, parent: Zombie = None):
        zombie = Zombie(
            self.screen,
            x,
            y,
            self.weapon_registry,
            self.projectile_registry,
            round_scaling = round,
            parent = parent,
            zombies = self.entities,
            **self.resources[zombie_type],
        )
        self.register(zombie)
        if parent:
            parent.summoned_zombies.append(zombie)

    def register(self, zombie: Zombie):
        self.entities.append(zombie)
        self.render_plain.add(zombie)
        self.render_plain.add(zombie.weapon)

    def deregister(self, zombie: Zombie):
        if zombie.damage_number.time > 0:
            self.orphaned_damage_numbers.append(zombie.damage_number)
        self.entities.remove(zombie)
        self.render_plain.remove(zombie)
        self.render_plain.remove(zombie.weapon)
        if zombie.parent:
            zombie.parent.summoned_zombies.remove(zombie)

    def update(self, frame_time):
        # debug
        #for entity in self.entities:
            #entity.head_hitbox.display(self.screen)
        # entity.hitbox.display(screen)
        self.render_plain.update(frame_time, self.screen)
        self.render_plain.draw(self.screen)
        expired_orphaned_damage_numbers = []
        for damage_number in self.orphaned_damage_numbers:
            if damage_number.time > 0:
                damage_number.update(frame_time, self.screen)
            else:
                expired_orphaned_damage_numbers.append(damage_number)
        self.orphaned_damage_numbers = [
            damage_number
            for damage_number in self.orphaned_damage_numbers
            if damage_number not in expired_orphaned_damage_numbers
        ]
        for zombie in self.entities:
            zombie.damage_number.update(frame_time, self.screen)
            if zombie.properties.health <= 0:
                event_bus.add_event(
                    "game_event_bus",
                    {
                        "killed_zombie": {
                            "money": zombie.properties.reward,
                            "experience": zombie.properties.experience,
                            "zombie": zombie.properties.name,
                        }
                    },
                )
                self.deregister(zombie)
