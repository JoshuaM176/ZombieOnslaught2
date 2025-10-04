from game.screenpage import ScreenPage
from util.ui_objects import FuncButton, ButtonContainer, Button, Text
from registries.entity_registries import ZombieRegistry
import pygame as pg


class Zombiepedia(ScreenPage, ButtonContainer):
    def __init__(self, screen, zombie_registry: ZombieRegistry, stats: dict, zombie_list: list[str]):
        self.zombie_list = zombie_list
        self.zombies = zombie_registry.resources
        self.num_zombies = 0
        self.stats = stats
        self.selected_zombie = "zombie"
        self.page = 0
        super().__init__(screen, "zombiepedia")

    def __screen_init__(self):
        self.zombies_per_page = round((self.screen.get_width() - 50) / 300)
        self.ui_buttons = []
        self.zombie_buttons = []
        self.description_text = []
        self.stats_text = []
        scr_w = self.screen.get_width()
        self.ui_buttons.append(FuncButton(50, 50, 500, 100, self.screen, self.set_screen, ["game"], "Back to Game"))
        self.ui_buttons.append(FuncButton(scr_w / 2 - 600, 500, 300, 100, self.screen, self.prev_page, [], "<---"))
        self.ui_buttons.append(FuncButton(scr_w / 2 + 100, 500, 300, 100, self.screen, self.next_page, [], "--->"))
        self.set_zombie_buttons()

    def next_page(self):
        if self.page + 1 * self.zombies_per_page < self.num_zombies:
            self.page += 1
            self.set_zombie_buttons()

    def prev_page(self):
        if self.page > 0:
            self.page -= 1
            self.set_zombie_buttons()

    def set_zombie_buttons(self):
        start_index = self.page * self.zombies_per_page
        self.zombie_buttons.clear()
        zombies = [self.zombies[zombie] | {"name": zombie} for zombie in self.zombie_list]
        self.num_zombies = len(zombies)
        x = 50
        y = 250
        for i in range(start_index, min(start_index + self.zombies_per_page, len(zombies))):
            self.zombie_buttons.append(self.ZombieButton(x, y, 200, 200, self.screen, zombies[i], self.select_zombie, self.stats[zombies[i]["name"]]))
            x += 300
            if x > self.screen.get_width() - 100:
                x = 50
                y += 300
        self.buttons = self.ui_buttons + self.zombie_buttons

    def select_zombie(self, zombie):
        self.selected_zombie = zombie
        zombie_dict = self.zombies[self.selected_zombie]
        self.description_text = []
        self.stats_text = []
        for i, desc in enumerate(zombie_dict["zombiepedia"]["description"].split("\n")):
            self.description_text.append(Text(desc, 25, 750, self.screen.get_height()-300+30*i))
        x = 300
        y = self.screen.get_height()-300
        for stat in [
            f"Health: {zombie_dict['health']}",
            f"Body Armour: {round(zombie_dict['body_armour'] * 100)}",
            f"Head Armour: {round(zombie_dict['head_armour'] * 100)}",
            f"Speed: {zombie_dict['speed']}",
            f"Number Killed: {self.stats[self.selected_zombie]}",
        ]:
            self.stats_text.append(Text(stat, 40, x, y))
            y += 50
            if y > self.screen.get_height():
                y = self.screen.get_height() - 350
                x += 100

    def update(self):
        self.go2 = self.page_name
        self.screen.fill((100, 50, 50))
        self.get_input()
        for button in self.buttons:
            button.update()
        if self.selected_zombie:
            zombie = self.zombies[self.selected_zombie]
            self.screen.blit(
                zombie["sprites"]["default"],
                (
                    50 + zombie["zombiepedia"]["shiftX"],
                    self.screen.get_height() - 300 + zombie["zombiepedia"]["shiftY"],
                    100,
                    100,
                ),
            )
        for text in self.stats_text:
            text.update(self.screen)
        for text in self.description_text:
            text.update(self.screen)
        pg.draw.rect(self.screen, (100, 100, 100), (0, self.screen.get_height() - 400, self.screen.get_width(), 50))
        return self.go2

    class ZombieButton(Button):
        def __init__(self, x, y, width, height, screen, zombie, func, seen):
            self.func = func
            self.zombie_dict = zombie
            self.zombie = pg.sprite.Sprite()
            self.zombie.sprite = zombie["sprites"]["default"]
            self.zombie.rect = zombie["sprites"]["default"].get_rect()
            self.zombie.rect.topleft = (x + zombie["zombiepedia"]["shiftX"], y + zombie["zombiepedia"]["shiftY"])
            self.seen = seen
            super().__init__(x, y, width, height, screen)

        def click(self, x, y):
            if self.seen:
                self.func(self.zombie_dict["name"])

        def update(self):
            if self.seen:
                pg.draw.rect(self.screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 10)
                self.screen.blit(self.zombie.sprite, self.zombie.rect)
            else:
                pg.draw.rect(self.screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 0)
