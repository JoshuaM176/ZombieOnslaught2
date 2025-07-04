import pygame as pg
from time import time
from util.event_bus import event_bus

pg.init()
clock = pg.time.Clock()
screen = pg.display.set_mode((1920, 1080))
from game.gameplay import Game  # noqa: E402

running = True

# Set so that first frame runs as if at 60fps
frame_start_time = time() - 0.017
event_bus.create_bus("input_bus")
event_bus.create_bus("ui_bus")
game = Game(screen)

while running:
    current_time = time()
    time_since_last_frame = current_time - frame_start_time
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
    game.update(screen, time_since_last_frame)
    pg.display.flip()
    clock.tick(180)

pg.quit()
