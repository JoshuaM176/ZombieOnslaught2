import pygame as pg

def text(screen, text, size, x, y, color = (0,0,0)):
    font = pg.font.Font(pg.font.get_default_font(), size)
    text = font.render(text, True, color)
    screen.blit(text, (x, y))