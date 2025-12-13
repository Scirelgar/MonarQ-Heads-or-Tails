"""
Minimalistic test to ensure the app can initialize and be closed.
"""

import pygame
from main import CoinFlipApp


def test_app_initialization():
    """Test that the CoinFlipApp can be initialized and closed properly."""
    # Create the app instance - this tests initialization
    app = CoinFlipApp()

    # Verify that basic components were created
    assert app.screen is not None
    assert app.clock is not None
    assert app.quantum_flipper is not None
    assert app.coins is not None

    # Set running to False to prevent main loop from starting
    app.running = False
