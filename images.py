import pygame

LIGHTNING_IMAGE = None

def get_lightning_image():

    global LIGHTNING_IMAGE

    if LIGHTNING_IMAGE:
        return LIGHTNING_IMAGE
    else:
        LIGHTNING_IMAGE = pygame.image.load("assets/lightning.png")
        return LIGHTNING_IMAGE
