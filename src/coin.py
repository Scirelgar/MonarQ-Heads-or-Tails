"""
Coin module for the MonarQ Heads or Tails application.

This module contains the Coin class that handles coin flip animations.
"""

import pygame
import random
import math
import os


class Coin:
    """
    A coin that can be flipped with animation.

    The coin starts in a static state showing Heads and can be flipped
    to randomly land on Heads or Tails with a 3D animation effect.
    """

    def __init__(
        self,
        x,
        y,
        radius=40,
        coin_color=(240, 200, 50),
        coin_edge_color=(180, 150, 30),
        text_color=(10, 10, 10),
        font=None,
    ):
        """
        Initialize a coin at the specified position.

        :param x: The x-coordinate of the coin center
        :type x: int
        :param y: The y-coordinate of the coin center
        :type y: int
        :param radius: The radius of the coin in pixels, defaults to 40
        :type radius: int, optional
        :param coin_color: RGB color tuple for the coin face, defaults to (240, 200, 50)
        :type coin_color: tuple, optional
        :param coin_edge_color: RGB color tuple for the coin edge, defaults to (180, 150, 30)
        :type coin_edge_color: tuple, optional
        :param text_color: RGB color tuple for the H/T text, defaults to (10, 10, 10)
        :type text_color: tuple, optional
        :param font: Pygame font object for rendering text
        :type font: pygame.font.Font, optional
        """
        self.x = x
        self.base_y = y
        self.radius = radius
        self.coin_color = coin_color
        self.coin_edge = coin_edge_color
        self.text_color = text_color
        self.font = font if font else pygame.font.SysFont(None, 48)

        # Load coin sprites
        self._load_sprites()

        # Animation state - start in static mode showing Heads
        self.state = "static"  # Can be: "static", "waiting", "final_flip", "done"
        self.frame = 0
        self.flip_duration = 0
        self.result = "H"  # Start with Heads

    def _load_sprites(self):
        """
        Load the coin sprite images from the assets directory.

        :return: None
        :rtype: None
        """
        try:
            # Load the sprite images
            heads_path = os.path.join("assets", "goldcoin-heads.png")
            tails_path = os.path.join("assets", "silvercoin-tails.png")

            self.heads_sprite = pygame.image.load(heads_path)
            self.tails_sprite = pygame.image.load(tails_path)

            # Scale sprites to fit the coin radius (diameter = radius * 2)
            size = self.radius * 2
            self.heads_sprite = pygame.transform.scale(self.heads_sprite, (size, size))
            self.tails_sprite = pygame.transform.scale(self.tails_sprite, (size, size))

        except pygame.error as e:
            print(f"Warning: Could not load coin sprites: {e}")
            # Fallback to None - will use programmatic drawing
            self.heads_sprite = None
            self.tails_sprite = None

    def flip(self):
        """
        Start the coin flip animation in waiting mode.

        Sets the coin to continuous bouncing while waiting for quantum results.

        :return: None
        :rtype: None
        """
        if self.state == "static" or self.state == "done":
            self.state = "waiting"
            self.frame = 0
            self.flip_duration = 60  # Duration of one bounce cycle

    def set_result(self, result):
        """
        Set the final result and trigger final flip animation.

        :param result: The final result "H" for Heads or "T" for Tails
        :type result: str
        :return: None
        :rtype: None
        """
        self.result = result
        self.state = "final_flip"
        self.frame = 0
        self.flip_duration = random.randint(45, 90)  # Final settling animation

    def reset(self):
        """
        Reset the coin to its initial static state showing Heads.

        :return: None
        :rtype: None
        """
        self.state = "static"
        self.frame = 0
        self.flip_duration = 0
        self.result = "H"

    def update(self):
        """
        Update the coin's animation state.

        Should be called once per frame. Advances the flip animation
        and transitions between states appropriately.

        :return: None
        :rtype: None
        """
        if self.state == "waiting":
            # Continuous bouncing - loop the animation
            self.frame += 1
            if self.frame >= self.flip_duration:
                self.frame = 0  # Loop back to start
        elif self.state == "final_flip":
            # Final animation before settling
            self.frame += 1
            if self.frame >= self.flip_duration:
                self.state = "done"

    def draw(self, surface):
        """
        Draw the coin on the given surface.

        Renders the coin differently based on its current state:
        - static/done: Full coin sprite with H or T
        - waiting/final_flip: Animated 3D flip effect with sprite scaling

        :param surface: The pygame surface to draw on
        :type surface: pygame.Surface
        :return: None
        :rtype: None
        """
        # Choose the appropriate sprite based on result
        current_sprite = self.heads_sprite if self.result == "H" else self.tails_sprite

        # Fallback to programmatic drawing if sprites failed to load
        if current_sprite is None:
            self._draw_programmatic(surface)
            return

        # While flipping (waiting or final), create 3D effect by scaling width
        if self.state == "waiting" or self.state == "final_flip":
            t = self.frame / self.flip_duration

            # Width oscillates like |cos| to mimic edge-on view during flip
            scale_x = abs(math.cos(t * math.pi * 4))
            scale_x = max(0.1, scale_x)  # Minimum width to keep visible

            # Bounce vertically
            bounce = math.sin(t * math.pi) * 30
            y = int(self.base_y - bounce)

            # Alternate between heads and tails during flip based on rotation phase
            # When scale_x is decreasing (coin turning edge-on), switch the visible side
            rotation_phase = (t * math.pi * 4) % (2 * math.pi)
            show_heads = rotation_phase < math.pi

            # Choose sprite based on rotation phase during flip, not final result
            flip_sprite = self.heads_sprite if show_heads else self.tails_sprite

            # Scale the sprite horizontally for 3D flip effect
            scaled_width = int(flip_sprite.get_width() * scale_x)
            scaled_height = flip_sprite.get_height()

            scaled_sprite = pygame.transform.scale(
                flip_sprite, (scaled_width, scaled_height)
            )

            # Center the scaled sprite
            sprite_rect = scaled_sprite.get_rect(center=(self.x, y))
            surface.blit(scaled_sprite, sprite_rect)

        else:  # state == "static" or "done"
            # Draw the full sprite
            sprite_rect = current_sprite.get_rect(center=(self.x, self.base_y))
            surface.blit(current_sprite, sprite_rect)

    def _draw_programmatic(self, surface):
        """
        Fallback method to draw coin programmatically if sprites aren't available.

        :param surface: The pygame surface to draw on
        :type surface: pygame.Surface
        :return: None
        :rtype: None
        """
        # While flipping (waiting or final), we fake a 3D flip by squashing/stretching the height
        if self.state == "waiting" or self.state == "final_flip":
            t = self.frame / self.flip_duration
            # Height oscillates like |cos| to mimic edge-on view
            h = max(8, self.radius * abs(math.cos(t * math.pi * 4)))
            w = self.radius * 2

            # Bounce a little vertically
            bounce = math.sin(t * math.pi) * 30
            y = int(self.base_y - bounce)

            rect = pygame.Rect(0, 0, w, h)
            rect.center = (self.x, y)

            pygame.draw.ellipse(surface, self.coin_color, rect)
            pygame.draw.ellipse(surface, self.coin_edge, rect, 3)

        else:  # state == "static" or "done"
            # Draw a full coin with H or T
            pygame.draw.circle(
                surface, self.coin_color, (self.x, self.base_y), self.radius
            )
            pygame.draw.circle(
                surface, self.coin_edge, (self.x, self.base_y), self.radius, 3
            )

            text = self.font.render(self.result, True, self.text_color)
            text_rect = text.get_rect(center=(self.x, self.base_y))
            surface.blit(text, text_rect)
