import pygame as pg

def text(screen, text, size, x, y, color = (0,0,0), align="LEFT"):
    font = pg.font.Font(pg.font.get_default_font(), size)
    text = font.render(text, True, color)
    match align:
        case "LEFT":
            screen.blit(text, (x, y))
        case "CENTER":
            screen.blit(text, text.get_rect(center=(x,y)))

def health_bar(screen, health, max_health, x, y, width, height):
    pg.draw.rect(screen, (0,255,0), (x, y, health/max_health*width, height))
    pg.draw.rect(screen, (0,0,0), (x , y, width, height), 1)
    text(screen, f"{health:.0f}", height, x+width/2, y+height/2, align="CENTER")

def check_buttons(x: int, y: int, buttons: list):
    for button in buttons:
        if(x > button.x and x < button.x + button.width and y > button.y and y < button.y + button.height):
            button.click()
            break

class Button():
    def __init__(self, x, y, width, height, screen):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.screen = screen

    def click():
        pass

    def update():
        pass

    