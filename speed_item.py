
import pygame

from images import get_lightning_image
from item import Item
import random


class SpeedItem(Item):

    def __init__(self, position, player_one, player_two):
        super().__init__(position, player_one, player_two)

        # Load the lightning image
        self.lightning_image = pygame.transform.scale(get_lightning_image(), (self.radius * 2, self.radius * 2))
        self.lightning_rect = self.lightning_image.get_rect(center=self.position)

        self.applied_to = random.sample([1, 2], k=1)[0]
        self.player_to_apply_to = player_one if self.applied_to == 1 else player_two

        self.speed_factor = 2

    def draw(self, screen):

        if self.applied_to == 1:
            outline_color = (0, 0, 255)
        else:
            outline_color = (255, 0, 0)

        # Draw the surrounding circle
        pygame.draw.circle(screen, outline_color, self.position, self.lightning_rect.width // 2, 2)

        # Blit the lightning image
        screen.blit(self.lightning_image, self.lightning_rect)

    def change(self):
        self.player_to_apply_to.speed *= self.speed_factor

    def take_back_change(self):
        self.player_to_apply_to.speed /= self.speed_factor
