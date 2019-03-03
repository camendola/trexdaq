import pygame
import numpy as np


def draw_button(surface, position, action, active, label, size=30, padding=10, colors={}, font=None):
    global clicked

    xpos, ypos = position

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    # Default colors for inactive state
    color, label_color = colors["inactive"]

    if active:
        # the button changes color when the mouse passes over it and makes an action if it gets clicked
        if xpos + size > mouse[0] > xpos and ypos + size > mouse[1] > ypos:
            color, label_color = colors["hover"]
            if click[0] == 1 and action != None and not clicked:
                action()
                clicked = True
            elif click[0] == 0:
                clicked = False
        else:
            color, label_color = colors["active"]
    pygame.draw.rect(surface, color, (xpos, ypos, size, size))

    if isinstance(label, str):
        if font is None:
            raise ValueError("The font keyword needs to be specified when drawing a button with text label")
        text_surf = font.render(label, True, label_color)
        text_rect = text_surf.get_rect()
        text_rect.center = ((xpos + (size / 2)), (ypos + (size / 2)))
        surface.blit(text_surf, text_rect)
    elif isinstance(label, list) or isinstance(label, np.ndarray):
        if isinstance(label, list):
            label = np.array(label)
        label = label * (size - 2 * padding)
        label[:, 1] = label[:, 1] + ypos + padding
        label[:, 0] = label[:, 0] + xpos + padding
        pygame.draw.polygon(surface, label_color, label)
    else:
        raise ValueError("label argument must either be string or array-like correspondig to polygon vertices")
