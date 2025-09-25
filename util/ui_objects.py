import pygame as pg


class ButtonContainer():
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

def text(screen, text, size, x, y, color=(0, 0, 0), align="LEFT", font=None):
    if font:
        font = pg.font.Font(font, size)
    else:
        font = pg.font.Font(pg.font.get_default_font(), size)
    text = font.render(text, True, color)
    match align:
        case "LEFT":
            screen.blit(text, (x, y))
        case "CENTER":
            screen.blit(text, text.get_rect(center=(x, y)))


def health_bar(screen, health, max_health, x, y, width, height):
    pg.draw.rect(screen, (0, 255, 0), (x, y, health / max_health * width, height))
    pg.draw.rect(screen, (0, 0, 0), (x, y, width, height), 1)
    text(screen, f"{health:.0f}", height, x + width / 2, y + height / 2, align="CENTER")


def progress_bar(screen, progress, x, y, width, height):
    pg.draw.rect(screen, (0, 255, 0), (x, y, progress * width, height))
    pg.draw.rect(screen, (0, 0, 0), (x, y, width, height), 1)

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
