import pygame as pg
from time import time
from util.event_bus import event_bus
from game.settings import Settings
import sys
from game.screenpage import screen_pages

pg.init()
clock = pg.time.Clock()
if len(sys.argv) > 2:
    screen = pg.display.set_mode((int(sys.argv[1]), int(sys.argv[2])), pg.RESIZABLE)
else:
    screen = pg.display.set_mode((pg.display.Info().current_w, pg.display.Info().current_h-100), pg.RESIZABLE)
from game.gameplay import Game  # noqa: E402
from game.main_menu import MainMenu  # noqa E402

running = True

# Set so that first frame runs as if at 60fps
frame_start_time = time() - 0.017
event_bus.create_bus("input_bus")
event_bus.create_bus("ui_bus")
event_bus.create_bus("game_event_bus")
event_bus.create_bus("game_end_of_round_bus")
event_bus.create_bus("trash")
game = Game(screen)
main_menu = MainMenu(screen)
settings = Settings(screen)
curr_screen = "main_menu"

while running:
    event_bus.clear_events("trash")
    current_time = time()
    time_since_last_frame = min(current_time - frame_start_time, 1/45)
    frame_start_time = current_time
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type in (
            pg.KEYDOWN,
            pg.KEYUP,
            pg.MOUSEBUTTONDOWN,
            pg.MOUSEBUTTONUP,
            pg.MOUSEWHEEL,
        ):
            event_bus.add_event("input_bus", event)
        if event.type == pg.VIDEORESIZE:
            for name, screen_obj in screen_pages.items():
                screen_obj.__screen_init__()
    match curr_screen:
        case "main_menu":
            curr_screen = main_menu.update()
            if curr_screen != "main_menu":
                game = Game(screen)
        case "game":
            curr_screen = game.update(time_since_last_frame)
        case _:
            curr_screen = screen_pages[curr_screen].update()
    pg.display.flip()
    clock.tick(180)

pg.quit()
