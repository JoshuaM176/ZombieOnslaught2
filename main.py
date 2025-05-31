import pygame as pg
from time import time
from util.event_bus import event_bus
from game.gameplay import Game

clock = pg.time.Clock()
screen = pg.display.set_mode((1920, 1080))
running = True
clock.tick(60)
#Set so that first frame runs as if at 60fps
frame_start_time = time()-0.017
event_bus.create_bus("input_bus")
game = Game()

while running:
    current_time = time()
    time_since_last_frame = current_time-frame_start_time
    frame_start_time = current_time
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type in (pg.KEYDOWN, pg.KEYUP, pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP, pg.MOUSEWHEEL):
            event_bus.add_event("input_bus", event)
    game.update()
    pg.display.flip()
    
pg.quit()