"""
Coin module for the MonarQ Heads or Tails application.

This module contains the Coin class that handles coin flip animations.
"""

import pygame
import random
import math


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
        coin_edge=(180, 150, 30),
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
        :param coin_edge: RGB color tuple for the coin edge, defaults to (180, 150, 30)
        :type coin_edge: tuple, optional
        :param text_color: RGB color tuple for the H/T text, defaults to (10, 10, 10)
        :type text_color: tuple, optional
        :param font: Pygame font object for rendering text
        :type font: pygame.font.Font, optional
        """
        self.x = x
        self.base_y = y
        self.radius = radius
        self.coin_color = coin_color
        self.coin_edge = coin_edge
        self.text_color = text_color
        self.font = font if font else pygame.font.SysFont(None, 48)

        # Animation state - start in static mode showing Heads
        self.state = "static"  # Can be: "static", "waiting", "final_flip", "done"
        self.frame = 0
        self.flip_duration = 0
        self.result = "H"  # Start with Heads

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
        - static/done: Full coin with H or T letter
        - waiting/final_flip: Animated 3D flip effect with squashing/stretching

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
