"""
Main application module for the MonarQ Heads or Tails game.

This module contains the CoinFlipApp class that controls the game logic.
"""

import pygame
import sys
import io
import threading
from coin import Coin
from quantum_backend import QuantumCoinFlipper


class CoinFlipApp:
    """
    Main application controller for the coin flip game.

    Manages the game window, coin creation, event handling, and game loop.
    """

    # Configuration constants
    WINDOW_WIDTH = 800
    CIRCUIT_SECTION_HEIGHT = 800
    COIN_SECTION_HEIGHT = 300
    WINDOW_HEIGHT = CIRCUIT_SECTION_HEIGHT + COIN_SECTION_HEIGHT
    BACKGROUND_COLOR = (30, 30, 40)
    COIN_COLOR = (240, 200, 50)
    COIN_EDGE_COLOR = (180, 150, 30)
    TEXT_COLOR = (10, 10, 10)
    FPS = 60
    NUM_COINS = 6

    def __init__(self, use_simulator=None):
        """
        Initialize the coin flip application.

        Sets up pygame, creates the window, fonts, initializes quantum backend, and coins.

        :param use_simulator: Whether to use quantum simulator instead of real device.
                             If None, reads from SIM_BOOL environment variable.
        :type use_simulator: bool or None
        """
        pygame.init()
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("MonarQ Quantum Coin Flips")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 48)
        self.hint_font = pygame.font.SysFont(None, 28)
        self.status_font = pygame.font.SysFont(None, 24)
        self.running = True

        # Initialize quantum backend (reads from .env if use_simulator is None)
        self.quantum_flipper = QuantumCoinFlipper(
            num_coins=self.NUM_COINS, use_simulator=use_simulator
        )

        # Status message
        self.status_message = "Loading quantum device..."
        self.circuit_surface = None

        # Initialize quantum device
        status = self.quantum_flipper.initialize_device()
        self.status_message = status

        # Generate circuit diagram
        self._generate_circuit_surface()

        self.coins = self._create_coins()

        # Quantum execution state
        self.quantum_executing = False
        self.quantum_thread = None
        self.quantum_results_ready = False
        self.quantum_results = None

    def _generate_circuit_surface(self):
        """
        Generate pygame surface from matplotlib circuit figure.

        Converts the quantum circuit diagram to a pygame surface that can be rendered.
        """
        try:
            fig = self.quantum_flipper.generate_circuit_figure()

            # Save figure to bytes buffer
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight", facecolor="white")
            buf.seek(0)

            # Load as pygame surface
            circuit_img = pygame.image.load(buf, "png")
            buf.close()

            # Scale to fit in circuit section
            img_width, img_height = circuit_img.get_size()
            scale_factor = (
                min(
                    self.WINDOW_WIDTH / img_width,
                    self.CIRCUIT_SECTION_HEIGHT / img_height,
                )
                * 0.9
            )  # 90% to leave some padding

            new_width = int(img_width * scale_factor)
            new_height = int(img_height * scale_factor)

            self.circuit_surface = pygame.transform.scale(
                circuit_img, (new_width, new_height)
            )
            self.status_message = "Quantum circuit ready!"

        except Exception as e:
            self.status_message = f"Error generating circuit: {str(e)}"
            self.circuit_surface = None

    def _execute_quantum_circuit_thread(self):
        """
        Execute the quantum circuit in a background thread.

        This runs in parallel with the game loop, allowing coins to animate
        while waiting for quantum results.
        """
        try:
            self.status_message = "Executing quantum circuit..."
            result_str = self.quantum_flipper.execute_circuit()
            self.quantum_results = self.quantum_flipper.parse_results(result_str)
            stats = self.quantum_flipper.get_statistics(result_str)
            self.status_message = (
                f"Results: {stats['heads']} Heads, {stats['tails']} Tails"
            )
            self.quantum_results_ready = True
        except Exception as e:
            self.status_message = f"Quantum execution error: {str(e)}"
            self.quantum_results_ready = False
            self.quantum_executing = False

    def _create_coins(self):
        """
        Create and position all coins for the game.

        Returns:
            list: A list of Coin objects positioned across the screen.
        """
        coins = []
        spacing = self.WINDOW_WIDTH // (self.NUM_COINS + 1)
        # Position coins in the bottom section
        y = self.CIRCUIT_SECTION_HEIGHT + (self.COIN_SECTION_HEIGHT // 2)
        for i in range(self.NUM_COINS):
            x = spacing * (i + 1)
            coins.append(
                Coin(
                    x,
                    y,
                    coin_color=self.COIN_COLOR,
                    coin_edge_color=self.COIN_EDGE_COLOR,
                    text_color=self.TEXT_COLOR,
                    font=self.font,
                )
            )
        return coins

    def handle_events(self):
        """
        Process all pygame events.

        Handles window close events and spacebar presses for coin flipping.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Press SPACE to flip all coins and execute quantum circuit
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                # Only start if not already executing
                if not self.quantum_executing:
                    # Start coins bouncing
                    for coin in self.coins:
                        coin.flip()

                    # Start quantum circuit execution in background thread
                    self.quantum_executing = True
                    self.quantum_results_ready = False
                    self.quantum_results = None
                    self.quantum_thread = threading.Thread(
                        target=self._execute_quantum_circuit_thread, daemon=True
                    )
                    self.quantum_thread.start()

    def update(self):
        """
        Update the state of all game objects.

        Updates all coin animations and checks for quantum results.
        When results arrive, triggers final coin flips with the quantum outcomes.
        """
        # Check if quantum results just arrived
        if self.quantum_results_ready and self.quantum_executing:
            # Apply results to coins and trigger final flip
            for i, coin in enumerate(self.coins):
                coin.set_result(self.quantum_results[i])

            self.quantum_executing = False
            self.quantum_results_ready = False

        # Update all coins
        for coin in self.coins:
            coin.update()

    def render(self):
        """
        Render all game objects to the screen.

        Draws the background, circuit diagram, coins, status message, and hint text.
        """
        self.screen.fill(self.BACKGROUND_COLOR)

        # Draw circuit section background
        circuit_bg_color = (45, 45, 55)
        pygame.draw.rect(
            self.screen,
            circuit_bg_color,
            (0, 0, self.WINDOW_WIDTH, self.CIRCUIT_SECTION_HEIGHT),
        )

        # Draw separator line
        pygame.draw.line(
            self.screen,
            (100, 100, 120),
            (0, self.CIRCUIT_SECTION_HEIGHT),
            (self.WINDOW_WIDTH, self.CIRCUIT_SECTION_HEIGHT),
            2,
        )

        # Draw circuit diagram if available
        if self.circuit_surface:
            circuit_rect = self.circuit_surface.get_rect(
                center=(self.WINDOW_WIDTH // 2, self.CIRCUIT_SECTION_HEIGHT // 2)
            )
            self.screen.blit(self.circuit_surface, circuit_rect)

        # Draw status message
        status_surf = self.status_font.render(
            self.status_message, True, (200, 200, 220)
        )
        status_rect = status_surf.get_rect(center=(self.WINDOW_WIDTH // 2, 20))
        self.screen.blit(status_surf, status_rect)

        # Draw all coins
        for coin in self.coins:
            coin.draw(self.screen)

        # Draw hint text
        hint = "Press SPACE to flip coins"
        hint_surf = self.hint_font.render(hint, True, (200, 200, 220))
        hint_rect = hint_surf.get_rect(
            center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT - 20)
        )
        self.screen.blit(hint_surf, hint_rect)

        pygame.display.flip()

    def run(self):
        """
        Run the main game loop.

        Handles events, updates game state, and renders until the user quits.
        """
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.FPS)

        self.quit()

    def quit(self):
        """
        Clean up and exit the application.

        Quits pygame and exits the program.
        """
        pygame.quit()
        sys.exit()


def main():
    """
    Entry point for the application.

    Creates and runs the CoinFlipApp.
    """
    app = CoinFlipApp()
    app.run()


if __name__ == "__main__":
    main()
