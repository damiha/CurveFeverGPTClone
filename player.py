import pygame
import pygame.math as pymath
import math

class Player:
    def __init__(self, player_id, position, direction, speed=100, rotation_speed=math.radians(90)):
        self.player_id = player_id
        self.position = pymath.Vector2(position)
        self.direction = pymath.Vector2(direction).normalize()

        self.initial_position = pymath.Vector2(position)
        self.initial_direction = pymath.Vector2(direction).normalize()

        self.speed = speed
        self.rotation_speed = rotation_speed
        self.radius = 10
        self.color = (0, 0, 255) if player_id == 1 else (255, 0, 0)

        self.past_positions = []
        self.record_every_nth_timestep = 5
        self.timestep_counter = 0

    def reset(self):
        self.position = self.initial_position
        self.direction = self.initial_direction
        self.past_positions = []
        self.timestep_counter = 0

    def update(self, delta_time):
        # Update the position based on the direction and speed
        self.position += self.direction * self.speed * delta_time

        # Screen dimensions
        screen_width, screen_height = 800, 800

        # Loop the position horizontally
        if self.position.x < 0:
            self.position.x = screen_width
        elif self.position.x > screen_width:
            self.position.x = 0

        # Loop the position vertically
        if self.position.y < 0:
            self.position.y = screen_height
        elif self.position.y > screen_height:
            self.position.y = 0

        self.timestep_counter += 1

        if self.timestep_counter > self.record_every_nth_timestep:
            self.timestep_counter = 0
            self.past_positions.append((self.position.x, self.position.y))

    def draw(self, canvas):
        # Draw the player as a circle
        center = (int(self.position.x), int(self.position.y))
        pygame.draw.circle(canvas, self.color, center, self.radius)

        # Calculate the end point of the line
        end_point = self.position + self.direction * self.radius

        # Draw a line from the center to the outline in the direction of the player
        pygame.draw.line(canvas, (0, 0, 0), center, (int(end_point.x), int(end_point.y)), 2)

    def goLeft(self, delta_time):
        self.direction = self.direction.rotate_rad(delta_time * -self.rotation_speed)

    def goRight(self, delta_time):
        self.direction = self.direction.rotate_rad(delta_time * self.rotation_speed)

# Example usage
# player = Player(1, (400, 400), (1, 0))
# player.update(0.016)  # Assuming 60 FPS, delta time is about 1/60
# player.draw(screen)
