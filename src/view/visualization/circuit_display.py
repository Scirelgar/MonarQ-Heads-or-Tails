"""This module defines the CircuitDisplay class for visualizing the circuit in the MonarQ Heads or Tails demo."""

import flet as ft
from flet import Container


class CircuitDisplay(Container):
    """Custom Container class for displaying the circuit visualization in the game."""

    def __init__(self, image_path: str):
        """
        Initialize the CircuitDisplay with a specific image.

        :param image_path: The file path to the circuit image to display.
        """
        super().__init__(
            border=ft.Border.all(2, "#FF0000"),
            border_radius=10,
            content=ft.Image(src=image_path, fit=ft.BoxFit.FIT_WIDTH, expand=True),
        )
