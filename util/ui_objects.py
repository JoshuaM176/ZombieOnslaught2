import pygame as pg
from util.event_bus import event_bus

class Text():
    def __init__(
            self,
            text,
            size,
            x,
            y,
            color=(0, 0, 0),
            align="LEFT",
            font=None
    ):
        self.align = align
        self.x = x
        self.y = y
        self.color = color
        if font:
            self.font = pg.font.Font(font, size)
        else:
            self.font = pg.font.Font(pg.font.get_default_font(), size)
        self.text = self.font.render(text, True, color)

    def update_text(self, text):
        self.text = self.font.render(text, True, self.color)

    def update_pos(self, x, y):
        self.x = x
        self.y = y

    def update(self, screen: pg.Surface):
        match self.align:
            case "LEFT":
                screen.blit(self.text, self.text.get_rect(topleft=(self.x, self.y)))
            case "CENTER":
                screen.blit(self.text, self.text.get_rect(center=(self.x, self.y)))


class ProgressBar():
    def __init__(
            self,
            progress,
            x,
            y,
            width,
            height,
            color = (0, 255, 0),
            text = None
                 ):
        self.progress = progress
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.text = Text(text, height, x + width/2, y + height/2, align="CENTER") if text is not None else None


    def update_pos(self, x, y):
        self.x = x
        self.y = y
        self.text.update_pos(x + self.width/2, y + self.height/2)

    def update_text(self, text: str):
        self.text.update_text(text)

    def update_progress(self, progress: float):
        self.progress = progress

    def update(self, screen: pg.Surface):
        pg.draw.rect(screen, self.color, (self.x, self.y, self.progress * self.width, self.height))
        pg.draw.rect(screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 1)
        if self.text:
            self.text.update(screen)


class ButtonContainer:
    def __init__(self):
        self.buttons = []

    def check_buttons(self, event, x: int, y: int):
        for button in self.buttons:
            if (
                x > button.x
                and x < button.x + button.width
                and y > button.y
                and y < button.y + button.height
            ):
                match event.type:
                    case pg.MOUSEBUTTONUP:
                        if event.button == 1:
                            button.click(x, y)
                    case pg.MOUSEWHEEL:
                        match event.y:
                            case 1:
                                button.scroll(True)
                            case -1:
                                button.scroll(False)
                break

    def get_input(self):
        mouse_x, mouse_y = pg.mouse.get_pos()
        input_bus = event_bus.get_events("input_bus")
        for event in input_bus:
            self.check_buttons(event, mouse_x, mouse_y)


def text(screen, text, size, x, y, color=(0, 0, 0), align="LEFT", font=None):
    if font:
        font = pg.font.Font(font, size)
    else:
        font = pg.font.Font(pg.font.get_default_font(), size)
    text = font.render(text, True, color)
    match align:
        case "LEFT":
            screen.blit(text, text.get_rect(topleft = (x, y)))
        case "CENTER":
            screen.blit(text, text.get_rect(center = (x, y)))


def get_font(name):
    return pg.font.match_font(name) or pg.font.get_default_font()


class Button:
    def __init__(self, x, y, width, height, screen):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.screen = screen

    def click():
        pass

    def scroll(scroll: bool):
        pass

    def update(**kwargs):
        pass


class FuncButton(Button):
    def __init__(
        self, x, y, width, height, screen, func, args, text, text_kwargs: dict = {}
    ):
        super().__init__(x, y, width, height, screen)
        self.func = func
        self.args = args
        self.text = text
        self.text_kwargs = {
            "text": text,
            "x": self.x + self.width / 2,
            "y": self.y + self.height / 2,
            "size": 50,
            "align": "CENTER",
        }
        self.text_kwargs.update(text_kwargs)

    def click(self, x, y):
        self.func(*self.args)

    def update(self, **kwargs):
        pg.draw.rect(
            self.screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 10
        )
        text(self.screen, **self.text_kwargs)


class DamageNumber:
    def __init__(self, time):
        self.x = 0
        self.y = 0
        self.damage = 0
        self.time = 0
        self.start_time = time

    def add_damage(self, x, y, damage):
        if self.time > 0:
            self.damage += damage
        else:
            self.damage = damage
        if abs(x - self.x) > 150:
            self.x = x
            self.y = y
        self.time = self.start_time

    def update(self, frame_time, surface: pg.Surface):
        self.time -= frame_time
        percent_time_left = self.time / self.start_time
        if self.damage > 0 and self.time > 0:
            temp_surface = pg.Surface((25, 15), pg.SRCALPHA)
            text(temp_surface, str(round(self.damage)), 15, 0, 0, color=(255, 0, 0))
            temp_surface.set_alpha(255 * percent_time_left)
            surface.blit(temp_surface, (self.x, self.y))
