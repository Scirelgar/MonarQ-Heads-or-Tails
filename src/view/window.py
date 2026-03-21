"""This module defines properties and methods for the app's window."""

from flet import Window


class AppWindow(Window):
    """Defines properties and methods for the app's window."""

    def __init__(self, page):
        """Initializes the AppWindow instance."""
        super().__init__(page)
        self.title = "Flet ChatGPT"
        self.width = 400
        self.height = 600
        self.resizable = False
