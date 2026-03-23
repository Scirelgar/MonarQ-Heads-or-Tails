"""This module defines the theme configuration for the MonarQ Heads or Tails demo."""

from enum import Enum

from flet import Colors


class Theme(Enum):
    """Defines the color scheme and styling for the MonarQ Heads or Tails application."""

    PRIMARY_COLOR = "#013D5B"  # Deep blue for backgrounds and main UI elements
    ACCENT_COLOR = "#6095C1"  # Bright accent color for buttons and highlights
    TEXT_COLOR_PRIMARY = "#052148"  # Dark blue for primary text
    BACKGROUND_COLOR = "#F0F0F0"  # Same as primary for consistency
