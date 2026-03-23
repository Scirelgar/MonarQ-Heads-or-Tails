"""This module defines the Text class for displaying status messages in the MonarQ Heads or Tails demo."""

import flet as ft

from view.theme import Theme


class StatusText(ft.Text):
    """Custom Text class for displaying status messages in the game."""

    def __init__(self, text: str = "", color: str = "#FFFFFF", size: int = 20):
        """
        Initialize the StatusText with specific styling.

        :param text: The initial text to display.
        :param color: The color of the text.
        :param size: The font size of the text.
        """
        super().__init__(
            value=text, color=Theme.TEXT_COLOR_PRIMARY, size=size, weight="bold"
        )
