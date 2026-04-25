import pygame as pg
from util.event_bus import event_bus
from util.ui_objects import get_font, Text, ProgressBar


class UI:
    def __init__(self, screen: pg.Surface):
        self.screen = screen
        self.data = {
            "weapon": "MP7",
            "bullets": 0,
            "mags": 0,
            "max_bullets": 0,
            "max_mags": 0,
            "money": 0,
            "round": 0,
            "next_weapon": False,
            "prev_weapon": False,
            "mag_progress": 0,
            "health": 10,
            "max_health": 10,
            "stamina": 100,
            "max_stamina": 100,
            "village_health": 10,
            "max_village_health": 10,
            "experience": 0,
            "experience_required": 100,
        }
        self.data_text_map = {
            "weapon": "weapon_info",
            "bullets": "bullet_info",
            "mags": "mag_info",
            "max_bullets": "bullet_info",
            "max_mags": "mag_info",
            "money": "money_info",
            "round": "round_info",
            "next_weapon": "next_prev_weapon_info",
            "prev_weapon": "next_prev_weapon_info",
            "mag_progress": "mag_progress_info",
            "health": "health_info",
            "max_health": "health_info",
            "stamina": "stamina_info",
            "max_stamina": "stamina_info",
            "village_health": "village_info",
            "max_village_health": "village_info",
            "level": "level_info",
            "experience": "experience_info",
            "experience_required": "experience_info",
        }
        self.text_map = {
            "weapon_info": self.WeaponText(screen),
            "bullet_info": self.BulletText(screen),
            "mag_info": self.MagText(screen),
            "money_info": self.MoneyText(screen),
            "round_info": self.RoundText(screen),
            "next_prev_weapon_info": self.NextPrevWeapon(screen, get_font("consolas")),
            "mag_progress_info": self.MagBar(screen),
            "health_info": self.HealthBar(screen),
            "stamina_info": self.StaminaBar(screen),
            "village_info": self.VillageHealthBar(screen),
            "experience_info": self.ExperienceBar(screen),
            "level_info": self.LevelText(screen),
        }

    def update(self):
        ui_bus = event_bus.get_events("ui_bus")
        for item in ui_bus:
            for atr, val in item.items():
                self.data[atr] = val
                func = self.text_map.get(self.data_text_map.get(atr))
                if func:
                    func.update_text(self.data)
        pg.draw.rect(
            self.screen,
            (200, 255, 200),
            (0, self.screen.get_height() - 250, self.screen.get_width(), 250),
        )
        for _, info in self.text_map.items():
            info.update(self.screen)

    class BulletText(Text):
        def __init__(self, screen: pg.Surface):
            super().__init__("", 75, 50, screen.get_height() - 125)

        def update_text(self, data: dict):
            ammo_percentage = 1 if data['max_bullets'] == 0 else data['bullets']/data['max_bullets']
            if ammo_percentage < 0.2:
                color = ((0.2-ammo_percentage)*5*150+100,0,0)
            else:
                color = (0,0,0)
            self.update_color(color)
            super().update_text(f"{data['bullets']}/{data['max_bullets']}")

    class MagText(Text):
        def __init__(self, screen: pg.Surface):
            super().__init__("", 25, 50, screen.get_height() - 50)

        def update_text(self, data: dict):
            super().update_text(f"{data['mags']}/{data['max_mags']}")

    class WeaponText(Text):
        def __init__(self, screen: pg.Surface):
            super().__init__("", 25, 50, screen.get_height() - 150)

        def update_text(self, data: dict):
            super().update_text(data["weapon"])

    class MoneyText(Text):
        def __init__(self, screen: pg.Surface):
            super().__init__("", 30, 25, screen.get_height() - 213)

        def update_text(self, data: dict):
            super().update_text(f"${data['money']:.0f}")

    class RoundText(Text):
        def __init__(self, screen: pg.Surface):
            super().__init__("", 30, 25, 35)

        def update_text(self, data: dict):
            super().update_text(f"Round {data['round']:.0f}")

    class NextPrevWeapon(Text):
        def __init__(self, screen: pg.Surface, font):
            super().__init__("", 10, 5, screen.get_height() - 165, font=font)

        def update_text(self, data: dict):
            super().update_text(
                f"{data['prev_weapon'] or '':<10} <--> {data['next_weapon'] or '':>10}"
            )

    class MagBar(ProgressBar):
        def __init__(self, screen):
            super().__init__(1, 50, screen.get_height() - 25, 100, 20)

        def update_text(self, data: dict):
            self.update_progress(data["mag_progress"])

    class StaminaBar(ProgressBar):
        def __init__(self, screen):
            super().__init__(
                1,
                screen.get_width() * 0.25,
                screen.get_height() - 250,
                screen.get_width() * 0.5,
                20,
                color=(0, 100, 255),
                text="",
            )

        def update_text(self, data: dict):
            self.update_progress(data["stamina"] / data["max_stamina"])
            super().update_text(str(max(round(data["stamina"] * 10), 0)))

    class HealthBar(ProgressBar):
        def __init__(self, screen):
            super().__init__(
                1,
                screen.get_width() * 0.25,
                screen.get_height() - 230,
                screen.get_width() * 0.5,
                20,
                color=(0, 200, 0),
                text="",
            )

        def update_text(self, data: dict):
            self.update_progress(data["health"] / data["max_health"])
            super().update_text(str(max(round(data["health"]), 1)))

    class VillageHealthBar(ProgressBar):
        def __init__(self, screen):
            super().__init__(
                1,
                screen.get_width() * 0.25,
                screen.get_height() - 210,
                screen.get_width() * 0.5,
                20,
                color=(200, 200, 0),
                text="",
            )

        def update_text(self, data: dict):
            self.update_progress(data["village_health"] / data["max_village_health"])
            super().update_text(str(max(round(data["village_health"]), 1)))

    class ExperienceBar(ProgressBar):
        def __init__(self, screen):
            super().__init__(
                1,
                screen.get_width() * 0.3,
                screen.get_height() - 190,
                screen.get_width() * 0.4,
                20,
                color=(100, 255, 100),
                text="",
            )

        def update_text(self, data: dict):
            self.update_progress(data["experience"] / data["experience_required"])
            super().update_text(f"{data['experience']} / {data['experience_required']}")

    class LevelText(Text):
        def __init__(self, screen: pg.Surface):
            super().__init__("", 30, 25, screen.get_height() - 242)

        def update_text(self, data: dict):
            super().update_text(f"Lvl. {data['level']}")
