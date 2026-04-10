"""This module defines the CoinDisplay class for showing the current coin state in the MonarQ Heads or Tails demo."""

import flet as ft
from flet import Image, Container, Row, Column, GridView
from ..theme import Theme


class Coin(Image):
    """Custom Image class for representing a coin in the game."""

    def __init__(self, src: str):
        """
        Initialize the Coin with a specific image source.

        :param src: The file path to the coin image to display.
        """
        super().__init__(
            src=src,
        )


class CoinDisplay(Container):
    """Container for displaying coins on an even grid illustrating binary results for the demonstration"""

    def __init__(self, coins: list[Image] = None):
        """
        Initialize the container, its displaying properties and the default alignment.


        :param coins: A list of Image controls representing the coins to be displayed.
        :type coins: list[Image]
        """
        super().__init__(
            padding=20,
            bgcolor=Theme.ACCENT_COLOR,
            border_radius=10,
            expand=True,
        )
        self._initialize_grid(len(coins) if coins is not None else 0)

    def _initialize_grid(self, num_elements: int = 0):
        """
        Initialize the grid layout displaying elements with somewhat even spacing.

        Elements will be arranged in a grid with a maximum of 4 rows, and the maximum number
        of elements it can render is 24.


        :param num_elements: Number of elements to display.
        :type num_elements: int
        :return:
        """

        if num_elements == 0:
            self.content = ft.Text("No coins to display.")
            return
