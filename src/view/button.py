"""This module defines the Button class for interactive elements in the MonarQ Heads or Tails demo."""

import flet as ft
from flet import Button
from .theme import Theme


class DemoButton(Button):
    """Custom button class for the MonarQ Heads or Tails game."""

    def __init__(self, text: str, on_click=None):
        """
        Initialize the DemoButton with specific styling and behavior.

        :param text: The text to display on the button.
        :param on_click: Optional callback function to execute when the button is clicked.
        """
        super().__init__(
            content=text,
            bgcolor=Theme.PRIMARY_COLOR,
            on_click=on_click,
        )
