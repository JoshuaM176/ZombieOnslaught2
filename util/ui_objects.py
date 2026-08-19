from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass, field
from typing import Any, Literal, Self, override

import pygame as pg

from util.event_bus import event_bus


class Text:
    def __init__(
        self,
        text: str,
        size: int,
        x: float,
        y: float,
        color: tuple = (0, 0, 0),
        align: Literal["LEFT", "RIGHT", "CENTER"] = "LEFT",
        font: str | None = None,
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

    def update_text(self, text: str):
        self.text = self.font.render(text, True, self.color)

    def update_color(self, color: tuple) -> None:
        self.color = color

    def update_pos(self, x: float, y: float):
        self.x = x
        self.y = y

    def update(self, screen: pg.Surface):
        match self.align:
            case "LEFT":
                screen.blit(self.text, self.text.get_rect(topleft=(self.x, self.y)))
            case "CENTER":
                screen.blit(self.text, self.text.get_rect(center=(self.x, self.y)))
            case "RIGHT":
                screen.blit(self.text, self.text.get_rect(topright=(self.x, self.y)))


@dataclass
class TextKwargs:
    size: int = 50
    align: Literal["LEFT", "CENTER", "RIGHT"] = "CENTER"


class ProgressBar:
    def __init__(self, progress: float, x: float, y: float, width: float, height: float, color=(0, 255, 0), text=None):
        self.progress = progress
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.text = Text(text, int(height), x + width / 2, y + height / 2, align="CENTER") if text is not None else None

    def update_pos(self, x: float, y: float):
        self.x = x
        self.y = y
        if self.text:
            self.text.update_pos(x + self.width / 2, y + self.height / 2)

    def update_text(self, text: str):
        if self.text:
            self.text.update_text(text)

    def update_progress(self, progress: float):
        self.progress = progress

    def update(self, screen: pg.Surface):
        pg.draw.rect(screen, self.color, (self.x, self.y, self.progress * self.width, self.height))
        pg.draw.rect(screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 1)
        if self.text:
            self.text.update(screen)


def get_font(name: str):
    return pg.font.match_font(name) or pg.font.get_default_font()


class ButtonContainer:
    def __init__(self):
        self.buttons: list[Button] = []
        self.nested_containers: list[ButtonContainer] = []

    def check_buttons(self, event: pg.event.Event, x: int, y: int) -> bool:
        for button in self.buttons:
            if x > button.x and x < button.x + button.width and y > button.y and y < button.y + button.height:
                match event.type:
                    case pg.MOUSEBUTTONDOWN:
                        button.click(x, y, event.button)
                    case pg.MOUSEWHEEL:
                        match event.y:
                            case 1:
                                button.scroll(scroll = True)
                            case -1:
                                button.scroll(scroll = False)
                return True
        return any(container.check_buttons(event, x, y) for container in self.nested_containers)

    def get_input(self) -> None:
        mouse_x, mouse_y = pg.mouse.get_pos()
        input_bus = event_bus.get_events("input_bus")
        for event in input_bus:
            self.check_buttons(event, mouse_x, mouse_y)

    def update(self) -> Any:
        for button in self.buttons:
            button.update()
        for container in self.nested_containers:
            container.update()


@dataclass
class ButtonInfo:
    text: str
    func: Callable[[], Any]
    text_kwargs: TextKwargs = field(default_factory=TextKwargs)


def horizontal_button_layout(
    x: float, y: float, width: float, height: float, margin: float, screen: pg.Surface, buttons: Sequence[ButtonInfo]
) -> ButtonContainer:
    scr_w = screen.get_width()
    scr_h = screen.get_height()
    if x <= 1:
        x = x * scr_w
    if y <= 1:
        y = y * scr_h
    if width <= 1:
        width = width * scr_w
    if height <= 1:
        height = height * scr_h
    if margin <= 1:
        margin = margin * scr_w
    width = width + margin
    num_buttons = len(buttons)
    full_width = width // num_buttons  # includes margin
    button_width = full_width - margin
    container = ButtonContainer()
    for i, button in enumerate(buttons):
        container.buttons.append(
            TextButton(
                int(x + full_width * i),
                int(y),
                int(button_width),
                int(height),
                screen,
                button.func,
                button.text,
                button.text_kwargs,
            )
        )
    return container


class Button:
    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        screen: pg.Surface,
        on_click: Callable[[], Any],
        on_update: Callable[[Self], Any] | None = None,
        calc_percentages: bool = False,
    ) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.screen = screen
        if calc_percentages:
            self._calc_percentages()
        self.on_click = on_click
        self.on_update = on_update or (lambda _: None)

    def _calc_percentages(self) -> None:
        scr_w = self.screen.get_width()
        scr_h = self.screen.get_height()
        self.x = self.x if self.x > 1 else self.x * scr_w
        self.width = self.width if self.width > 1 else self.width * scr_w
        self.y = self.y if self.y > 1 else self.y * scr_h
        self.height = self.height if self.height > 1 else self.height * scr_h

    def click(self, x: float, y: float, button: int) -> None:  # NOQA: ARG002
        if button == 1:
            self.on_click()

    def scroll(self, scroll: bool) -> None:
        pass

    def update(self) -> None:
        pg.draw.rect(self.screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 10)
        self.on_update(self)


class TextButton(Button):
    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        screen: pg.Surface,
        on_click: Callable[[], Any],
        text: str,
        text_kwargs: TextKwargs | None = None,
        on_update: Callable[[Self], Any] | None = None,
        calc_percentages: bool = False,
    ) -> None:
        super().__init__(x, y, width, height, screen, on_click, on_update, calc_percentages)
        text_kwargs = text_kwargs or TextKwargs()
        kwargs = {
            "text": text,
            "x": self.x + self.width / 2,
            "y": self.y + self.height / 2,
            "size": 50,
            "align": "CENTER",
        }
        kwargs.update(asdict(text_kwargs) or {})
        self.text = Text(**kwargs)

    @override
    def update(self) -> None:
        self.on_update(self)
        pg.draw.rect(self.screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 10)
        self.text.update(self.screen)


class FloatingNumber:
    def __init__(self, time: float, size: int = 15, color: tuple[int, int, int] = (255, 0, 0)) -> None:
        self.x: float = 0
        self.y: float = 0
        self.damage: float = 0
        self.time: float = 0
        self.start_time = time
        self.size = size
        self.text = Text(str(round(self.damage)), size, 0, 0, color=color)
        self.temp_surface = pg.Surface((self.size * 2, self.size), pg.SRCALPHA)

    def add(self, x: float, y: float, damage: float) -> None:
        if self.time > 0:
            self.damage += damage
        else:
            self.x = x
            self.y = y
            self.damage = damage
        if abs(x - self.x) > 150:
            self.x = x
            self.y = y
        self.text.update_text(str(round(self.damage)))
        self.time = self.start_time

    def update(self, frame_time: float, surface: pg.Surface) -> None:
        self.time -= frame_time
        percent_time_left = self.time / self.start_time
        if self.damage > 0 and self.time > 0:
            self.temp_surface.fill((0, 0, 0, 0))
            self.text.update(self.temp_surface)
            self.temp_surface.set_alpha(int(255 * percent_time_left))
            surface.blit(self.temp_surface, (self.x, self.y))
