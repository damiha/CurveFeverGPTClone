import pygame


class Item:
    def __init__(self, position, player_one, player_two):
        self.position = position
        self.player_one = player_one
        self.player_two = player_two

        # (50, 50) for the picture
        self.radius = 25

        self.effect_duration = 5  # Duration in seconds
        self.effect_applied = False
        self.apply_time = None

    def draw(self, screen):
        raise NotImplementedError("Subclass must implement the draw method.")

    def intersects(self, player):
        px, py = player.position
        x, y = self.position
        return (x - px)**2 + (y - py)**2 < (self.radius + player.radius)**2

    def change(self):
        raise NotImplementedError

    def take_back_change(self):
        raise NotImplementedError

    def apply(self):
        if not self.effect_applied:

            self.change()

            self.effect_applied = True
            self.apply_time = pygame.time.get_ticks()  # Record the time of effect application

    def update(self, current_time):
        if self.effect_applied and (current_time - self.apply_time) > self.effect_duration * 1000:

            self.take_back_change()

            self.effect_applied = False
