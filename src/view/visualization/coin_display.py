"""This module defines the CoinDisplay class for showing the current coin state in the MonarQ Heads or Tails demo."""

import flet as ft
from flet import Image, Container, Row, Column
from ..theme import Theme


class CoinDisplay(Container):
    """Container for displaying coins on an even grid illustrating binary results for the demonstration"""

    def __init__(self, coins: list[Image] = None):
        """
        Initialize the container, its displaying properties and the default alignment.

        :param coins: A list of Image controls representing the coins to be displayed.
        :type coins: list[Image]
        """
        super().__init__(
            padding=20, bgcolor=Theme.ACCENT_COLOR, border_radius=10, expand=True
        )
