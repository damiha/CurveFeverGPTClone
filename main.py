import pygame
from player import Player
import time
import math
from speed_item import SpeedItem
from settings import *
import random
from images import *

# Initialize Pygame
pygame.init()

# preload the item graphics, so it doesn't lack in game
get_lightning_image()

# Game window dimensions
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game Window")

# Colors
DARK_GREY = (50, 50, 50)

# Create a player
player_one = Player(1, (100, 100), (0, -1))
player_two = Player(2, (400, 400), (0, 1))


who_won = None


def draw_path(canvas, points, color, thickness):
    if len(points) > 1:
        for i in range(len(points) - 1):

            x, y = points[i]
            nx, ny = points[i + 1]

            # only connect non-looping points
            if (x - nx) ** 2 + (y - ny) ** 2 < MAX_DISTANCE_BETWEEN_POINTS ** 2:
                pygame.draw.line(canvas, color, points[i], points[i + 1], thickness)


def intersects_circle_and_path(circle_pos, radius, path):
    def distance_point_to_line_segment(p, p1, p2):
        line_mag = math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)
        if line_mag < 1e-10:
            return math.sqrt((p[0] - p1[0]) ** 2 + (p[1] - p1[1]) ** 2)

        u = ((p[0] - p1[0]) * (p2[0] - p1[0]) + (p[1] - p1[1]) * (p2[1] - p1[1])) / (line_mag ** 2)
        if u < 0.0 or u > 1.0:
            # Closest point does not fall within the line segment
            dx = min(math.sqrt((p[0] - p1[0]) ** 2 + (p[1] - p1[1]) ** 2),
                     math.sqrt((p[0] - p2[0]) ** 2 + (p[1] - p2[1]) ** 2))
            return dx
        else:
            # Compute the point on the line segment nearest to the point
            ix = p1[0] + u * (p2[0] - p1[0])
            iy = p1[1] + u * (p2[1] - p1[1])
            return math.sqrt((p[0] - ix) ** 2 + (p[1] - iy) ** 2)

    for i in range(len(path) - 1):

        x, y = path[i]
        nx, ny = path[i + 1]

        # skip looping points
        if (x - nx) ** 2 + (y - ny) ** 2 > MAX_DISTANCE_BETWEEN_POINTS ** 2:
            continue

        dist = distance_point_to_line_segment(circle_pos, path[i], path[i + 1])
        if dist <= radius:
            return True
    return False


def draw_game_screen():
    global who_won, game_state

    draw_path(screen, player_one.past_positions, player_one.color, thickness=10)
    draw_path(screen, player_two.past_positions, player_two.color, thickness=10)

    for item in items:
        item.draw(screen)

    # how much distance in one time step
    distance_per_timestep = delta_time * player_one.speed
    time_steps_per_double_radius = 2 * player_one.radius / distance_per_timestep
    ignore_last_n = math.ceil(time_steps_per_double_radius / player_one.record_every_nth_timestep)

    if intersects_circle_and_path(player_one.position, player_one.radius,
                                  player_one.past_positions[:-ignore_last_n]) or (
            intersects_circle_and_path(player_one.position, player_one.radius, player_two.past_positions)):
        who_won = 2
        game_state = GameState.GAME_OVER

    if intersects_circle_and_path(player_two.position, player_two.radius,
                                  player_two.past_positions[:-ignore_last_n]) or (
            intersects_circle_and_path(player_two.position, player_two.radius, player_one.past_positions)):
        who_won = 1
        game_state = GameState.GAME_OVER

    player_one.draw(screen)
    player_two.draw(screen)


def draw_game_over_screen():

    global running, button1_rect, button2_rect

    screen.fill((0, 0, 0))  # Clear the screen (fill with black or any other color)

    # Font settings
    font_color = (0, 0, 255) if who_won == 1 else (255, 0, 0)
    font = pygame.font.Font(None, 36)
    text = font.render(f"Player {who_won} has won!", True, font_color, None)
    text_rect = text.get_rect(center=(screen.get_width() / 2, 0))

    # Button settings
    button1_rect = pygame.Rect(screen.get_width() / 2 - 100, 0, 200, 50)
    button2_rect = pygame.Rect(screen.get_width() / 2 - 100, 0, 200, 50)

    # Vertical Spacing and Alignment
    total_height = text_rect.height + button1_rect.height + button2_rect.height + 10  # 10 is the space between buttons
    start_y = (screen.get_height() - total_height) // 2

    text_rect.centery = start_y
    button1_rect.y = text_rect.bottom + 20  # 20 pixels below the text
    button2_rect.y = button1_rect.bottom + 10  # 10 pixels below the first button

    # Draw text and buttons
    screen.blit(text, text_rect)

    # Black background with white outline and rounded corners for the first button
    pygame.draw.rect(screen, (0, 0, 0), button1_rect, 0, border_radius=10)
    pygame.draw.rect(screen, (255, 255, 255), button1_rect, 2, border_radius=10)

    # Black background with white outline and rounded corners for the second button
    pygame.draw.rect(screen, (0, 0, 0), button2_rect, 0, border_radius=10)
    pygame.draw.rect(screen, (255, 255, 255), button2_rect, 2, border_radius=10)

    # Button text
    button_font = pygame.font.Font(None, 24)
    try_again_text = button_font.render("Try Again", True, (255, 255, 255), None)
    main_menu_text = button_font.render("To Main Menu", True, (255, 255, 255), None)

    try_again_rect = try_again_text.get_rect(center=button1_rect.center)
    main_menu_rect = main_menu_text.get_rect(center=button2_rect.center)

    screen.blit(try_again_text, try_again_rect)
    screen.blit(main_menu_text, main_menu_rect)


def draw_main_menu():

    global play_button_rect, about_rect

    screen.fill((0, 0, 0))  # Fill the screen with black (or any other color)

    # Load the Ubuntu font or a default font if it's not available
    try:
        font = pygame.font.Font("/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf", 60)  # Adjust the path to the Ubuntu font
    except IOError:
        font = pygame.font.Font(None, 60)  # Fallback to default font

    # Draw the game title
    title_text = font.render("Curve Fever", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(400, 250))

    screen.blit(title_text, title_rect)

    # Draw the buttons
    button_font = pygame.font.Font(None, 40)
    button1_text = button_font.render("Play", True, (255, 255, 255))
    button2_text = button_font.render("About", True, (255, 255, 255))

    play_button_rect = pygame.Rect(300, 350, 200, 50)
    about_rect = pygame.Rect(300, 420, 200, 50)

    # Black background with white outline and rounded corners for the play button
    pygame.draw.rect(screen, (0, 0, 0), play_button_rect, 0, border_radius=10)
    pygame.draw.rect(screen, (255, 255, 255), play_button_rect, 2, border_radius=10)

    # Black background with white outline and rounded corners for the about button
    pygame.draw.rect(screen, (0, 0, 0), about_rect, 0, border_radius=10)
    pygame.draw.rect(screen, (255, 255, 255), about_rect, 2, border_radius=10)

    # Blit the text onto the buttons
    screen.blit(button1_text, button1_text.get_rect(center=play_button_rect.center))
    screen.blit(button2_text, button2_text.get_rect(center=about_rect.center))


def draw_about_screen(screen):

    global about_to_main_rect

    screen.fill((0, 0, 0))  # Clear the screen (fill with black)

    # Define colors and font
    white = (255, 255, 255)
    font = pygame.font.Font(None, 36)

    # Box in the center
    box_rect = pygame.Rect(150, 150, 500, 400)
    pygame.draw.rect(screen, (0, 0, 0), box_rect, 0, border_radius=10)
    pygame.draw.rect(screen, white, box_rect, 2, border_radius=10)

    # Load and display logos
    damiha_logo = pygame.image.load('assets/damiha_logo.png')
    gpt4_logo = pygame.image.load('assets/gpt4_logo.png')
    damiha_logo = pygame.transform.scale(damiha_logo, (50, 50))
    gpt4_logo = pygame.transform.scale(gpt4_logo, (50, 50))

    # Display "Developers" text
    developers_text = font.render("Developers", True, white)
    screen.blit(developers_text, (170, 170))

    # Blit logos and names
    screen.blit(damiha_logo, (170, 220))
    screen.blit(gpt4_logo, (170, 290))
    screen.blit(font.render('damiha', True, white), (230, 220))
    screen.blit(font.render('GPT-4', True, white), (230, 290))

    # Haiku text lines
    haiku_lines = [
        "Coding together,",
        "Man and machine intertwined,",
        "Harmony in code."
    ]
    y_offset = 370
    for line in haiku_lines:
        line_text = font.render(line, True, white)
        screen.blit(line_text, (200, y_offset))
        y_offset += 40  # Adjust the vertical spacing between lines

    # Signature
    signature = font.render("GPT-4", True, white)
    screen.blit(signature, (200, y_offset))  # Adjusted gap after Haiku

    # Button with text "<--"
    button_text = font.render("<--", True, white)
    button_rect = pygame.Rect(150, y_offset + 100, 50, 50)  # Position below the signature with a gap
    about_to_main_rect = button_rect
    pygame.draw.rect(screen, (0, 0, 0), button_rect, 0, border_radius=10)  # Black background, rounded corners
    pygame.draw.rect(screen, white, button_rect, 2, border_radius=10)  # White outline
    screen.blit(button_text, (button_rect.x + 10, button_rect.y + 10))


def get_new_item_position(player_one, player_two):
    while True:
        # Generate a random position within the 800x800 area
        position = (random.randint(25, 775), random.randint(25, 775))

        # Check if the position is at least 25 pixels away from both players' paths
        if not intersects_circle_and_path(position, 25, player_one.past_positions) and \
           not intersects_circle_and_path(position, 25, player_two.past_positions):
            return position


game_state = GameState.MAIN_MENU

clock = pygame.time.Clock()

# for the game over screen
button1_rect = None
button2_rect = None

# for the main menu
play_button_rect = None
about_rect = None

# for the about page
about_to_main_rect = None

items = []
applied_items = []

def reset_game():
    global who_won, items, applied_items

    who_won = None

    for item in applied_items:
        item.take_back_change()

    applied_items = []
    items = []
    player_one.reset()
    player_two.reset()


mean_wait_time = 5
std_wait_time = 1
spawn_timer = 0
wait_time = max(0, random.normalvariate(mean_wait_time, std_wait_time)) * 1000  # Convert to milliseconds

def spawn_item():

    position = get_new_item_position(player_one, player_two)
    new_item = SpeedItem(position=position, player_one=player_one, player_two=player_two)
    items.append(new_item)

# Game loop
running = True
last_time = time.time()

while running:
    current_time = time.time()
    delta_time = current_time - last_time
    last_time = current_time
    spawn_timer += (delta_time * 1000)

    current_ticks = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == GameState.GAME_OVER:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button1_rect.collidepoint(event.pos):
                    reset_game()
                    game_state = GameState.IN_GAME

                elif button2_rect.collidepoint(event.pos):
                    reset_game()
                    game_state = GameState.MAIN_MENU

        elif game_state == GameState.MAIN_MENU:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button_rect.collidepoint(event.pos):
                    reset_game()
                    game_state = GameState.IN_GAME

                elif about_rect.collidepoint(event.pos):
                   game_state = GameState.ABOUT

        elif game_state == GameState.ABOUT:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if about_to_main_rect.collidepoint(event.pos):
                    game_state = GameState.MAIN_MENU

    if game_state == GameState.IN_GAME:
        # Check for key presses
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            player_one.goLeft(delta_time)
        if keys[pygame.K_d]:
            player_one.goRight(delta_time)
        if keys[pygame.K_LEFT]:
            player_two.goLeft(delta_time)
        if keys[pygame.K_RIGHT]:
            player_two.goRight(delta_time)

        player_one.update(delta_time)
        player_two.update(delta_time)

        if spawn_timer >= wait_time:
            spawn_item()
            spawn_timer = 0
            wait_time = max(0, random.normalvariate(mean_wait_time, std_wait_time)) * 1000

        items_after_application = []

        for item in items:
            if item.intersects(player=player_one) or item.intersects(player=player_two):
                item.apply()
                applied_items.append(item)
            else:
                items_after_application.append(item)

        items = items_after_application

        for item in applied_items:
            item.update(current_time=current_ticks)

    # Fill the background and draw the player
    screen.fill(DARK_GREY)

    if game_state == GameState.MAIN_MENU:
        draw_main_menu()
    elif game_state == GameState.IN_GAME:
        draw_game_screen()
    elif game_state == GameState.GAME_OVER:
        draw_game_over_screen()
    elif game_state == GameState.ABOUT:
        draw_about_screen(screen)

    # Update the display
    pygame.display.flip()

    # update the clock
    clock.tick(60)

# Quit Pygame
pygame.quit()
