# 10.11.24

import os

# External libraries
import pygame
from pyboy import PyBoy


# Internal utilities
from Src.Engine.dataclass import Entity
from Src.Engine.engine import MarioLandMonitor


# Initialize Pygame and PyBoy
pygame.init()
pyboy = PyBoy(os.path.join('rom', 'mario.gb'))
monitor = MarioLandMonitor(pyboy)


# Game window settings
GB_WIDTH, GB_HEIGHT = pyboy.screen.raw_buffer_dims
SCALE = 3 
WIN_WIDTH, WIN_HEIGHT = GB_HEIGHT * SCALE, GB_WIDTH * SCALE
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("PyBoy Game")


# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255) 
YELLOW = (255, 255, 0) 
TEXT_COLOR = (255, 0, 128)
TEXT_BG_COLOR = (0, 0, 0, 128) 


# Function to draw the game state on the Pygame screen
def draw_game_state(pyboy, screen):

    # Get Mario's and other entities' states from the monitor
    localPlayer, landGame, entityList = monitor.get_game_state()
    mario = localPlayer
    
    # Mario's position
    position = mario.position
    mario_x = position.x 
    mario_y = position.y

    # Get PyBoy's screen buffer as a NumPy array
    screen_array = pyboy.screen.ndarray[:, :, :3]
    screen_surface = pygame.surfarray.make_surface(screen_array)
    rotated_surface = pygame.transform.rotate(screen_surface, 270)
    flipped_surface = pygame.transform.flip(rotated_surface, True, False)
    scaled_surface = pygame.transform.scale(flipped_surface, (WIN_WIDTH, WIN_HEIGHT))
    screen.fill(BLACK)

    # Update Pygame window with the scaled and rotated PyBoy screen
    screen.blit(scaled_surface, (0, 0))

    # Draw a red dot at Mario's position
    mario_center_x = mario_x * SCALE
    mario_center_y = mario_y * SCALE
    pygame.draw.circle(screen, RED, (mario_center_x, mario_center_y), 4)

    # Draw Mario's rectangle
    mario_rect = pygame.Rect(localPlayer.rect.left, localPlayer.rect.top, localPlayer.rect.width, localPlayer.rect.height)
    pygame.draw.rect(screen, RED, mario_rect, 2)

    # Draw enemy entities
    for idx, entity in enumerate(entityList):
        entity: Entity = entity
        enemy_x = entity.position.x
        enemy_y = entity.position.y
        
        # Display collision status text
        collision_text = f"{idx}: {entity.collisione}"

        # Draw enemy rectangle
        enemy_rect = pygame.Rect(entity.rect.left, entity.rect.top, entity.rect.width, entity.rect.height)
        pygame.draw.rect(screen, BLUE, enemy_rect, 2)

        # Draw a yellow dot at the enemy's position
        enemy_center_x = enemy_x * SCALE
        enemy_center_y = enemy_y * SCALE 
        pygame.draw.circle(screen, YELLOW, (enemy_center_x, enemy_center_y), 4)

        # Display collision text above the enemy with a semi-transparent background
        font = pygame.font.SysFont(None, 24)
        text = font.render(collision_text, True, TEXT_COLOR)
        
        # Calculate text width and height for proper positioning
        text_width, text_height = text.get_size()
        
        # Draw semi-transparent rectangle behind the text
        text_rect = pygame.Rect(enemy_center_x - text_width // 2, enemy_center_y - text_height - 10, text_width, text_height)
        pygame.draw.rect(screen, TEXT_BG_COLOR, text_rect)
        
        # Add text above the enemy
        screen.blit(text, (enemy_center_x - text_width // 2, enemy_center_y - text_height - 10))  # Text above the enemy

        # Draw a red line between Mario and the enemy if they are colliding
        if entity.collisione:
            pygame.draw.line(screen, RED, (mario_center_x, mario_center_y), (enemy_center_x, enemy_center_y), 2)

    # Update the window
    pygame.display.flip()


# Main game loop
running = True
while running:
    for event in pygame.event.get():
        # Handle quit events
        if event.type == pygame.QUIT:
            running = False
        # Handle keyboard exit on pressing Escape key
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # Advance the game by one tick
    pyboy.tick()
    
    # Draw the game state on the screen
    draw_game_state(pyboy, screen)

# Stop PyBoy and quit Pygame after exiting the loop
pyboy.stop()
pygame.quit()