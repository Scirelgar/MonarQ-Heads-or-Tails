"""This module defines the theme configuration for the MonarQ Heads or Tails demo."""

from enum import Enum

from flet import Colors


class Theme(Enum):
    """Defines the color scheme and styling for the MonarQ Heads or Tails application."""

    PRIMARY_COLOR = "#013D5B"
    ACCENT_COLOR = "#6095C1"
    TEXT_COLOR_PRIMARY = "#052148"
    TEXT_COLOR_SECONDARY = "#041635"
    BACKGROUND_COLOR = "#F0F0F0"
