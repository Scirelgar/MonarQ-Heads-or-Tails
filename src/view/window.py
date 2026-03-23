"""This module defines properties and methods for the app's window."""

import flet as ft
from .theme import Theme


class AppWindow:
    """Wrapper that configures and manages the Flet page instance."""

    def __init__(self, page: ft.Page):
        """
        Initialize the app window by configuring the provided page instance.

        This wrapper allows UI composition logic to stay separate from main.py
        while working with Flet's canonical page management.

        :param page: The Flet page instance provided by ft.run()
        :type page: ft.Page
        """
        self.page = page
        self._configure_page()

    def _configure_page(self):
        """Configure the page properties and add initial UI components."""
        self.page.title = "MonarQ Heads or Tails"
        self.page.vertical_alignment = "center"
        self.page.horizontal_alignment = "center"
        self.page.bgcolor = Theme.BACKGROUND_COLOR
        self.page.window.icon = "assets/monarq-icon.ico"
        self.page.update()
