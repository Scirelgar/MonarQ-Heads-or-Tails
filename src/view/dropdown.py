"""This module defines the Dropdown class for UI elements in the MonarQ Heads or Tails demo."""

import flet as ft
from flet import Dropdown, Colors
from .theme import Theme


class DemoDropdown(Dropdown):
    """Custom Dropdown class for the MonarQ Heads or Tails game."""

    def __init__(
        self, label: str, options: list[ft.dropdown.Option], on_select=None, value=None
    ):
        """
        Initialize the DemoDropdown with specific styling and behavior.

        :param label: The label to display above the dropdown.
        :param options: A list of Dropdown options to populate the dropdown menu.
        :param on_select: Optional callback function to execute when the dropdown value changes.
        """
        super().__init__(options=options, label=label, on_select=on_select, value=value)

        # Apply custom styling to match the theme
        self.border_color = Theme.PRIMARY_COLOR
        self.label_style = ft.TextStyle(
            color=Theme.TEXT_COLOR_SECONDARY,
            size=16,
            weight="bold",
        )
        self.border_radius = 15
        self.text_style = ft.TextStyle(
            color=Theme.TEXT_COLOR_PRIMARY,
            size=18,
        )
        self.width = 225
