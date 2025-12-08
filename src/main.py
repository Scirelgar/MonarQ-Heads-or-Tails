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
from menu_bar import MenuBar

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


class CoinFlipApp:
    """
    Main application controller for the coin flip game.

    Manages the game window, coin creation, event handling, and game loop.
    """

    # Configuration constants
    CIRCUIT_SECTION_WIDTH = 800
    COIN_SECTION_WIDTH = 800
    WINDOW_WIDTH = CIRCUIT_SECTION_WIDTH + COIN_SECTION_WIDTH
    WINDOW_HEIGHT = CIRCUIT_SECTION_WIDTH
    MENU_HEIGHT = 30
    BACKGROUND_COLOR = (30, 30, 40)
    COIN_COLOR = (240, 200, 50)
    COIN_EDGE_COLOR = (180, 150, 30)
    TEXT_COLOR = (10, 10, 10)
    FPS = 60

    def __init__(self):
        """
        Initialize the coin flip application.

        Sets up pygame, creates the window, fonts, initializes quantum backend, and coins.
        The number of coins is determined by the quantum device.
        """
        pygame.init()
        # Add menu height to total window height
        total_height = self.WINDOW_HEIGHT + self.MENU_HEIGHT
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, total_height))
        pygame.display.set_caption("MonarQ Quantum Coin Flips")

        # Set application icon
        try:
            icon = pygame.image.load("assets/monarq-icon.ico")
            pygame.display.set_icon(icon)
        except Exception as e:
            logger.warning(f"Could not load application icon: {e}")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 48)
        self.hint_font = pygame.font.SysFont(None, 28)
        self.status_font = pygame.font.SysFont(None, 24)
        self.running = True

        # Initialize menu bar
        self.menu_bar = MenuBar(self.WINDOW_WIDTH, self.MENU_HEIGHT)
        self.current_device = "MonarQ"  # Track current device selection

        # Initialize quantum backend (defaults to simulator if device_name is None)
        self.quantum_flipper = QuantumCoinFlipper()

        # Status message
        self.status_message = "Loading quantum device..."
        self.circuit_surface = None

        # Initialize quantum device
        status = self.quantum_flipper.initialize_device()
        self.status_message = status

        # Generate circuit diagram
        self._generate_circuit_surface()

        self.coins = self._create_coins(self.quantum_flipper.num_coins)

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
                    self.CIRCUIT_SECTION_WIDTH / img_height,
                )
                * 0.9
            )  # 90% to leave some padding

            new_width = int(img_width * scale_factor)
            new_height = int(img_height * scale_factor)

            self.circuit_surface = pygame.transform.scale(
                circuit_img, (new_width, new_height)
            )
            # self.status_message = "Quantum circuit ready!"

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

    def _start_quantum_flip(self):
        """
        Start the quantum coin flip process.

        Initiates coin animations and starts quantum circuit execution in a background thread.
        Only starts if not already executing to prevent multiple concurrent executions.
        """
        if self.current_device == "MonarQ":
            return

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

    def _create_coins(self, num_coins):
        """
        Create and position all coins for the game.

        Arranges coins in a grid layout within the right section of the window,
        with a maximum of 6 coins per row and uniform spacing.

        :param num_coins: Number of coins to create (determined by quantum device)
        :type num_coins: int
        :return: List of Coin objects positioned in a grid layout
        :rtype: list
        """
        coins = []
        max_coins_per_row = 6

        # Calculate number of rows needed
        num_rows = (num_coins + max_coins_per_row - 1) // max_coins_per_row

        # Calculate spacing for the coin section (right half of the window)
        coin_section_x_start = self.CIRCUIT_SECTION_WIDTH
        coin_section_width = self.COIN_SECTION_WIDTH
        coin_section_height = self.WINDOW_HEIGHT

        for i in range(num_coins):
            # Calculate row and column for current coin
            row = i // max_coins_per_row
            col = i % max_coins_per_row

            # Calculate number of coins in current row
            coins_in_current_row = min(
                max_coins_per_row, num_coins - row * max_coins_per_row
            )

            # Calculate horizontal position with uniform spacing
            horizontal_spacing = coin_section_width // (coins_in_current_row + 1)
            x = coin_section_x_start + horizontal_spacing * (col + 1)

            # Calculate vertical position with uniform spacing (offset by menu height)
            vertical_spacing = coin_section_height // (num_rows + 1)
            y = vertical_spacing * (row + 1) + self.MENU_HEIGHT

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

    def _handle_menu_click(self, pos):
        """
        Handle mouse clicks on menu items.

        :param pos: Mouse position tuple (x, y)
        :type pos: tuple
        """
        action = self.menu_bar.handle_click(pos)
        if action:
            logger.debug(f"Menu click at {pos}, action: {action}")
            self._handle_menu_action(action)

    def _handle_menu_action(self, action):
        """
        Handle menu action execution.

        :param action: The action string to execute
        :type action: str
        """
        if action == "exit":
            self.running = False
        elif action.startswith("device_"):
            device_name = action.replace("device_", "").replace("_", "-").title()
            logger.debug(f"Parsing device name: {device_name}")
            if device_name == "Monarq":
                device_name = "MonarQ"
            elif device_name == "Monarq-Backup":
                device_name = "MonarQ-Backup"

            self._change_device(device_name)
        elif action == "about":
            self._show_about_dialog()
        elif action == "increase_qubits":
            if self.current_device == "Simulation":
                self._change_num_qubits(1)
        elif action == "decrease_qubits":
            if self.current_device == "Simulation":
                self._change_num_qubits(-1)

    def _change_device(self, device_name):
        """
        Change the quantum device and update the application state.

        :param device_name: Name of the device to switch to
        :type device_name: str
        """
        self.current_device = device_name
        self.menu_bar.set_current_device(device_name)  # Sync with menu bar
        self.status_message = f"Switching to {device_name}..."

        # Change device in quantum backend
        try:
            status = self.quantum_flipper.change_device(device_name)
            self.status_message = status

            # Regenerate circuit surface with new device
            self._generate_circuit_surface()

            # Recreate coins with new device's coin count
            self.coins = self._create_coins(self.quantum_flipper.num_coins)

        except Exception as e:
            self.status_message = f"Error switching device: {str(e)}"

    def _show_about_dialog(self):
        """
        Show information about the application.
        """
        self.status_message = (
            "MonarQ Quantum Coin Flips - Powered by real quantum devices!"
        )

    def _change_num_qubits(self, delta):
        """
        Change the number of qubits (only in simulation mode).

        :param delta: Change in number of qubits (+1 or -1)
        :type delta: int
        """
        if self.current_device == "Simulation":
            current_coins = self.quantum_flipper.num_coins
            new_num_coins = max(1, min(24, current_coins + delta))
            if new_num_coins != current_coins:
                self.quantum_flipper.num_coins = new_num_coins

                # Reinitialize device with new qubit count
                status = self.quantum_flipper.initialize_device()
                self.status_message = f"Changed to {new_num_coins} qubits - {status}"

                # Regenerate circuit and coins
                self._generate_circuit_surface()
                self.coins = self._create_coins(self.quantum_flipper.num_coins)

    def _handle_menu_hover(self, pos):
        """
        Handle mouse hover over menu items.

        :param pos: Mouse position tuple (x, y)
        :type pos: tuple
        """
        self.menu_bar.handle_hover(pos)

    def handle_events(self):
        """
        Process all pygame events.

        Handles window close events, menu interactions, and spacebar presses for coin flipping.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Handle mouse clicks for menu
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._handle_menu_click(event.pos)

            # Handle mouse motion for menu highlighting
            if event.type == pygame.MOUSEMOTION:
                self._handle_menu_hover(event.pos)

            # Press SPACE to flip all coins and execute quantum circuit
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self._start_quantum_flip()

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

        Draws the background, menu bar, circuit diagram, coins, status message, and hint text.
        """
        self.screen.fill(self.BACKGROUND_COLOR)

        # Draw circuit section background (offset by menu height)
        circuit_bg_color = (45, 45, 55)
        pygame.draw.rect(
            self.screen,
            circuit_bg_color,
            (0, self.MENU_HEIGHT, self.CIRCUIT_SECTION_WIDTH, self.WINDOW_HEIGHT),
        )

        # Draw separator line (offset by menu height)
        pygame.draw.line(
            self.screen,
            (100, 100, 120),
            (self.CIRCUIT_SECTION_WIDTH, self.MENU_HEIGHT),
            (self.CIRCUIT_SECTION_WIDTH, self.WINDOW_HEIGHT + self.MENU_HEIGHT),
            2,
        )

        # Draw circuit diagram if available (offset by menu height)
        if self.circuit_surface:
            circuit_rect = self.circuit_surface.get_rect(
                center=(
                    self.CIRCUIT_SECTION_WIDTH // 2,
                    (self.WINDOW_HEIGHT // 2) + self.MENU_HEIGHT,
                )
            )
            self.screen.blit(self.circuit_surface, circuit_rect)

        # Draw status message (offset by menu height)
        status_surf = self.status_font.render(
            self.status_message, True, (200, 200, 220)
        )
        status_rect = status_surf.get_rect(
            center=(self.CIRCUIT_SECTION_WIDTH // 2, 20 + self.MENU_HEIGHT)
        )
        self.screen.blit(status_surf, status_rect)

        # Draw all coins
        for coin in self.coins:
            coin.draw(self.screen)

        # Draw hint text (offset by menu height)
        hint = "Press SPACE to flip coins"
        hint_surf = self.hint_font.render(hint, True, (200, 200, 220))
        hint_rect = hint_surf.get_rect(
            center=(
                self.CIRCUIT_SECTION_WIDTH // 2,
                self.WINDOW_HEIGHT + self.MENU_HEIGHT - 20,
            )
        )
        self.screen.blit(hint_surf, hint_rect)

        # Draw menu bar (always on top)
        self.menu_bar.render(self.screen)

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
