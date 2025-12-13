"""
Menu bar module for MonarQ Heads or Tails.

This module contains the MenuBar class that handles menu rendering and interactions.
"""

import pygame
import logging

logger = logging.getLogger(__name__)


class MenuBar:
    """
    Menu bar controller for the application.

    Manages menu structure, rendering, event handling, and user interactions.
    """

    def __init__(self, window_width, menu_height=30):
        """
        Initialize the menu bar.

        :param window_width: Width of the application window
        :type window_width: int
        :param menu_height: Height of the menu bar in pixels
        :type menu_height: int
        """
        self.window_width = window_width
        self.menu_height = menu_height
        self.menu_font = pygame.font.SysFont(None, 20)

        # Menu structure
        self.menu_items = [
            {
                "text": "File",
                "rect": None,
                "submenu": [{"text": "Exit", "action": "exit"}],
            },
            {
                "text": "Settings",
                "rect": None,
                "submenu": [
                    {
                        "text": "Device",
                        "submenu": [
                            {"text": "MonarQ", "action": "device_monarq"},
                            {"text": "MonarQ-Backup", "action": "device_monarq_backup"},
                            {"text": "Yukon", "action": "device_yukon"},
                            {"text": "Simulation", "action": "device_simulation"},
                        ],
                    },
                    {
                        "text": "Number of Qubits",
                        "enabled": False,  # Disabled unless Simulation is selected
                        "submenu": [
                            {"text": "Increase Ctrl + +", "action": "increase_qubits"},
                            {"text": "Decrease Ctrl + -", "action": "decrease_qubits"},
                        ],
                    },
                ],
            },
            {
                "text": "Help",
                "rect": None,
                "submenu": [{"text": "About", "action": "about"}],
            },
        ]

        # Menu state
        self.active_menu = None
        self.active_submenu = None
        self.submenu_visible = False
        self.current_device = "MonarQ"  # Track current device selection

    def handle_click(self, pos):
        """
        Handle mouse clicks on menu items.

        :param pos: Mouse position tuple (x, y)
        :type pos: tuple
        :return: Action string if an action was triggered, None otherwise
        :rtype: str or None
        """
        # Check if click is outside both menu bar and submenu areas
        if pos[1] > self.menu_height:
            # Only close menus if click is not in a submenu area
            if not (self.submenu_visible and self._is_mouse_over_submenu_area(pos)):
                # Click outside menu and submenu areas, close any open menus
                self.active_menu = None
                self.active_submenu = None
                self.submenu_visible = False
                return None

        # Check if clicking on submenu items
        if self.submenu_visible and self.active_menu is not None:
            action = self._handle_submenu_click(pos)
            if action:
                return action

        # Check which menu item was clicked
        for i, menu_item in enumerate(self.menu_items):
            if menu_item["rect"] and menu_item["rect"].collidepoint(pos):
                if self.active_menu == i:
                    # Close menu if already active
                    self.active_menu = None
                    self.submenu_visible = False
                else:
                    # Open new menu
                    self.active_menu = i
                    self.submenu_visible = True
                    self.active_submenu = None
                break

        return None

    def handle_hover(self, pos):
        """
        Handle mouse hover over menu items.

        :param pos: Mouse position tuple (x, y)
        :type pos: tuple
        """
        # If submenu is visible, check if mouse is over submenu area first
        if self.submenu_visible and self.active_menu is not None:
            if self._is_mouse_over_submenu_area(pos):
                return  # Keep current menu active

        # Only handle hover if we're in the menu bar area
        if pos[1] <= self.menu_height:
            for i, menu_item in enumerate(self.menu_items):
                if menu_item["rect"] and menu_item["rect"].collidepoint(pos):
                    # If a menu is already open, switch to hovered menu
                    if self.submenu_visible:
                        self.active_menu = i
                    break
        elif self.submenu_visible:
            # Mouse is outside menu bar and not over submenu, close menu after a small delay
            # We'll implement this by checking if mouse is completely outside menu areas
            if not self._is_mouse_over_submenu_area(pos):
                # Only close if mouse is far from menu areas
                if pos[1] > self.menu_height + 200:  # Allow some buffer space
                    self.active_menu = None
                    self.submenu_visible = False

    def render(self, screen):
        """
        Render the menu bar to the screen.

        :param screen: Pygame screen surface to render to
        :type screen: pygame.Surface
        """
        self._render_menu_bar(screen)

    def set_current_device(self, device_name):
        """
        Update the current device selection.

        :param device_name: Name of the currently selected device
        :type device_name: str
        """
        self.current_device = device_name

        # Update Number of Qubits enabled state
        settings_menu = self.menu_items[1]  # Settings menu
        for item in settings_menu["submenu"]:
            if item["text"] == "Number of Qubits":
                item["enabled"] = device_name == "Simulation"

    def _handle_submenu_click(self, pos):
        """
        Handle clicks on submenu items.

        :param pos: Mouse position tuple (x, y)
        :type pos: tuple
        :return: Action string if an action was triggered, None otherwise
        :rtype: str or None
        """
        if self.active_menu is None:
            return None

        menu_item = self.menu_items[self.active_menu]
        submenu_items = menu_item.get("submenu", [])

        if not submenu_items:
            return None

        # Calculate submenu position and dimensions
        menu_rect = menu_item["rect"]
        submenu_x = menu_rect.left
        submenu_y = menu_rect.bottom
        max_width = 200
        item_height = 25

        # First check if click is on a nested submenu (Device or Number of Qubits options)
        # Use the same vertical distance logic as rendering to prevent clicking wrong submenu

        # Create a list of all enabled items with submenus
        submenu_candidates = []

        for i, item in enumerate(submenu_items):
            if "submenu" in item and (
                item["text"] == "Device" or item["text"] == "Number of Qubits"
            ):
                item_y = submenu_y + i * item_height
                nested_submenu_x = submenu_x + max_width
                nested_items = item.get("submenu", [])
                nested_height = len(nested_items) * item_height

                # Check if item is enabled (for Number of Qubits)
                enabled = item.get("enabled", True)
                if "enabled" in item:
                    enabled = item["enabled"]
                elif item["text"] == "Number of Qubits":
                    enabled = self.current_device == "Simulation"

                if not enabled:
                    continue

                submenu_candidates.append(
                    {
                        "index": i,
                        "item": item,
                        "item_y": item_y,
                        "nested_x": nested_submenu_x,
                        "nested_height": nested_height,
                        "nested_items": nested_items,
                    }
                )

        # Find which nested submenu the click should go to using vertical distance logic
        best_candidate = None
        min_vertical_distance = float("inf")

        for candidate in submenu_candidates:
            nested_rect = pygame.Rect(
                candidate["nested_x"],
                candidate["item_y"],
                max_width,
                candidate["nested_height"],
            )

            if nested_rect.collidepoint(pos):
                # Calculate vertical distance from click to parent item center
                parent_center_y = candidate["item_y"] + (item_height // 2)
                distance = abs(pos[1] - parent_center_y)

                if distance < min_vertical_distance:
                    min_vertical_distance = distance
                    best_candidate = candidate

        # Handle click on the best matching nested submenu
        if best_candidate:
            for j, nested_item in enumerate(best_candidate["nested_items"]):
                nested_item_y = best_candidate["item_y"] + j * item_height
                nested_item_rect = pygame.Rect(
                    best_candidate["nested_x"], nested_item_y, max_width, item_height
                )

                if nested_item_rect.collidepoint(pos) and "action" in nested_item:
                    action = nested_item["action"]
                    # Close menu after action
                    self.active_menu = None
                    self.submenu_visible = False
                    return action

        # Then check main submenu items
        for i, item in enumerate(submenu_items):
            item_y = submenu_y + i * item_height
            item_rect = pygame.Rect(submenu_x, item_y, max_width, item_height)

            if item_rect.collidepoint(pos):
                # Handle different types of menu items
                if "action" in item:
                    action = item["action"]
                    # Close menu after action
                    self.active_menu = None
                    self.submenu_visible = False
                    return action
                elif "submenu" in item:
                    # For items with submenus (like Device), don't close the menu
                    # Just let the nested submenu stay open
                    return None

        return None

    def _is_mouse_over_submenu_area(self, pos):
        """
        Check if mouse is over any submenu area (including nested submenus).

        :param pos: Mouse position tuple (x, y)
        :type pos: tuple
        :return: True if mouse is over submenu area
        :rtype: bool
        """
        if self.active_menu is None:
            return False

        menu_item = self.menu_items[self.active_menu]
        submenu_items = menu_item.get("submenu", [])

        if not submenu_items:
            return False

        # Calculate main submenu area
        menu_rect = menu_item["rect"]
        submenu_x = menu_rect.left
        submenu_y = menu_rect.bottom
        max_width = 200
        item_height = 25
        submenu_height = len(submenu_items) * item_height

        main_submenu_rect = pygame.Rect(submenu_x, submenu_y, max_width, submenu_height)

        if main_submenu_rect.collidepoint(pos):
            return True

        # Check nested submenu areas (Device and Number of Qubits)
        for i, item in enumerate(submenu_items):
            if "submenu" in item and (
                item["text"] == "Device" or item["text"] == "Number of Qubits"
            ):
                item_y = submenu_y + i * item_height
                item_rect = pygame.Rect(submenu_x, item_y, max_width, item_height)
                nested_submenu_x = submenu_x + max_width
                nested_items = item.get("submenu", [])
                nested_height = len(nested_items) * item_height

                # Check if item is enabled (for Number of Qubits)
                enabled = item.get("enabled", True)
                if "enabled" in item:
                    enabled = item["enabled"]
                elif item["text"] == "Number of Qubits":
                    enabled = self.current_device == "Simulation"

                if not enabled:
                    continue

                # Check if mouse is directly over this parent item
                if item_rect.collidepoint(pos):
                    return True

                # Check if mouse is over the nested submenu area for this specific item
                nested_rect = pygame.Rect(
                    nested_submenu_x, item_y, max_width, nested_height
                )
                if nested_rect.collidepoint(pos):
                    return True

                # Check if mouse is in the specific corridor for this item only
                corridor_rect = pygame.Rect(
                    submenu_x + max_width,  # Start at the right edge of main submenu
                    item_y,  # Start at this item's top
                    10,  # Small corridor width
                    item_height,  # Only this item's height
                )
                if corridor_rect.collidepoint(pos):
                    return True

        return False

    def _should_show_nested_submenu(self, parent_rect, nested_x, nested_y, mouse_pos):
        """
        Determine if a nested submenu should be shown based on mouse position.
        This method is now used only by _is_mouse_over_submenu_area for corridor detection.

        :param parent_rect: Rectangle of the parent menu item
        :type parent_rect: pygame.Rect
        :param nested_x: X position where nested submenu would appear
        :type nested_x: int
        :param nested_y: Y position where nested submenu would appear
        :type nested_y: int
        :param mouse_pos: Current mouse position
        :type mouse_pos: tuple
        :return: True if nested submenu should be shown
        :rtype: bool
        """
        # Show if hovering over parent item
        if parent_rect.collidepoint(mouse_pos):
            return True

        # Show if mouse is in a very narrow corridor specific to this parent item
        # The corridor must be vertically aligned with this specific parent item
        corridor_rect = pygame.Rect(
            parent_rect.right,
            parent_rect.top,
            10,  # Very narrow corridor
            parent_rect.height,  # Only cover this parent item's height
        )
        if corridor_rect.collidepoint(mouse_pos):
            return True

        return False

    def _render_menu_bar(self, screen):
        """
        Render the top menu bar with menu items and submenus.

        :param screen: Pygame screen surface to render to
        :type screen: pygame.Surface
        """
        # Draw menu bar background
        menu_rect = pygame.Rect(0, 0, self.window_width, self.menu_height)
        pygame.draw.rect(screen, (60, 60, 70), menu_rect)
        pygame.draw.line(
            screen,
            (100, 100, 120),
            (0, self.menu_height),
            (self.window_width, self.menu_height),
            1,
        )

        # Draw menu items
        x_offset = 0
        for i, menu_item in enumerate(self.menu_items):
            # Render menu text
            text_color = (220, 220, 220) if i == self.active_menu else (180, 180, 180)
            text_surf = self.menu_font.render(menu_item["text"], True, text_color)

            # Calculate menu item rectangle
            padding = 15
            item_width = text_surf.get_width() + padding * 2
            item_rect = pygame.Rect(x_offset, 0, item_width, self.menu_height)
            menu_item["rect"] = item_rect

            # Highlight active menu item
            if i == self.active_menu:
                pygame.draw.rect(screen, (80, 80, 90), item_rect)

            # Draw text centered in menu item
            text_rect = text_surf.get_rect(center=item_rect.center)
            screen.blit(text_surf, text_rect)

            x_offset += item_width

        # Draw submenu if active
        if self.submenu_visible and self.active_menu is not None:
            self._render_submenu(screen)

    def _render_submenu(self, screen):
        """
        Render the active submenu dropdown.

        :param screen: Pygame screen surface to render to
        :type screen: pygame.Surface
        """
        if self.active_menu is None:
            return

        menu_item = self.menu_items[self.active_menu]
        submenu_items = menu_item.get("submenu", [])

        if not submenu_items:
            return

        # Calculate submenu position
        menu_rect = menu_item["rect"]
        submenu_x = menu_rect.left
        submenu_y = menu_rect.bottom

        # Calculate submenu dimensions
        max_width = 200
        item_height = 25
        submenu_height = len(submenu_items) * item_height

        # Draw submenu background
        submenu_rect = pygame.Rect(submenu_x, submenu_y, max_width, submenu_height)
        pygame.draw.rect(screen, (70, 70, 80), submenu_rect)
        pygame.draw.rect(screen, (100, 100, 120), submenu_rect, 1)

        # Get mouse position for hover detection
        mouse_pos = pygame.mouse.get_pos()

        # Determine which nested submenu to show (if any) - only show one at a time
        nested_to_show = None

        # First priority: Check if mouse is directly over any parent item
        for i, item in enumerate(submenu_items):
            if "submenu" not in item:
                continue

            item_y = submenu_y + i * item_height
            item_rect = pygame.Rect(submenu_x, item_y, max_width, item_height)

            # Check if item is enabled
            enabled = item.get("enabled", True)
            if "enabled" in item:
                enabled = item["enabled"]
            elif item["text"] == "Number of Qubits":
                enabled = self.current_device == "Simulation"

            if not enabled:
                continue

            # If mouse is directly over this parent item, show its nested submenu
            if item_rect.collidepoint(mouse_pos):
                nested_to_show = (i, item, submenu_x + max_width, item_y)
                break

        # Second priority: Check nested submenu areas and corridors
        # We need to check this in a specific order to avoid conflicts
        if nested_to_show is None:
            # Create a list of all enabled items with submenus and their areas
            submenu_candidates = []

            for i, item in enumerate(submenu_items):
                if "submenu" not in item:
                    continue

                # Check if item is enabled
                enabled = item.get("enabled", True)
                if "enabled" in item:
                    enabled = item["enabled"]
                elif item["text"] == "Number of Qubits":
                    enabled = self.current_device == "Simulation"

                if not enabled:
                    continue

                item_y = submenu_y + i * item_height
                nested_x = submenu_x + max_width
                nested_items_list = item.get("submenu", [])
                nested_height = len(nested_items_list) * item_height

                submenu_candidates.append(
                    {
                        "index": i,
                        "item": item,
                        "item_y": item_y,
                        "nested_x": nested_x,
                        "nested_height": nested_height,
                    }
                )

            # Check if mouse is in any nested submenu area first (highest priority)
            # Use vertical alignment to resolve conflicts between overlapping areas

            # Find the candidate whose parent item is closest vertically to the mouse
            best_candidate = None
            min_vertical_distance = float("inf")

            for candidate in submenu_candidates:
                nested_area = pygame.Rect(
                    candidate["nested_x"],
                    candidate["item_y"],
                    max_width,
                    candidate["nested_height"],
                )

                if nested_area.collidepoint(mouse_pos):
                    # Calculate vertical distance from mouse to parent item center
                    parent_center_y = candidate["item_y"] + (item_height // 2)
                    distance = abs(mouse_pos[1] - parent_center_y)

                    if distance < min_vertical_distance:
                        min_vertical_distance = distance
                        best_candidate = candidate

            if best_candidate:
                nested_to_show = (
                    best_candidate["index"],
                    best_candidate["item"],
                    best_candidate["nested_x"],
                    best_candidate["item_y"],
                )

            # If not in any nested area, check corridors (lower priority)
            if nested_to_show is None:
                for candidate in submenu_candidates:
                    # Very narrow corridor specific to this item's vertical space
                    corridor_rect = pygame.Rect(
                        submenu_x + max_width,  # Start at right edge of main submenu
                        candidate["item_y"],  # This item's exact vertical position
                        8,  # Very narrow corridor
                        item_height,  # Only this item's height
                    )

                    if corridor_rect.collidepoint(mouse_pos):
                        nested_to_show = (
                            candidate["index"],
                            candidate["item"],
                            candidate["nested_x"],
                            candidate["item_y"],
                        )
                        break

        # Draw submenu items
        for i, item in enumerate(submenu_items):
            item_y = submenu_y + i * item_height
            item_rect = pygame.Rect(submenu_x, item_y, max_width, item_height)

            # Check if item is enabled (for Number of Qubits)
            enabled = item.get("enabled", True)
            if "enabled" in item:
                enabled = item["enabled"]
            elif item["text"] == "Number of Qubits":
                # Enable only if Simulation device is selected
                enabled = self.current_device == "Simulation"

            # Highlight hovered item
            if enabled and item_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, (90, 90, 100), item_rect)

            # Color based on enabled state
            text_color = (200, 200, 200) if enabled else (100, 100, 100)

            # Render item text
            display_text = item["text"]
            if "submenu" in item and enabled:
                display_text += " >"

            text_surf = self.menu_font.render(display_text, True, text_color)
            text_rect = text_surf.get_rect(x=submenu_x + 10, centery=item_rect.centery)
            screen.blit(text_surf, text_rect)

        # Render the nested submenu (only one at a time)
        if nested_to_show:
            i, item, nested_x, nested_y = nested_to_show
            self._render_nested_submenu(screen, item, nested_x, nested_y)

    def _render_nested_submenu(self, screen, parent_item, submenu_x, submenu_y):
        """
        Render a nested submenu (Device options or Number of Qubits options).

        :param screen: Pygame screen surface to render to
        :type screen: pygame.Surface
        :param parent_item: The parent submenu item
        :type parent_item: dict
        :param submenu_x: X position for the nested submenu
        :type submenu_x: int
        :param submenu_y: Y position for the nested submenu
        :type submenu_y: int
        """
        nested_items = parent_item.get("submenu", [])
        if not nested_items:
            return

        max_width = 200
        item_height = 25
        nested_height = len(nested_items) * item_height

        # Draw nested submenu background
        nested_rect = pygame.Rect(submenu_x, submenu_y, max_width, nested_height)
        pygame.draw.rect(screen, (70, 70, 80), nested_rect)
        pygame.draw.rect(screen, (100, 100, 120), nested_rect, 1)

        # Get mouse position for hover detection
        mouse_pos = pygame.mouse.get_pos()

        # Check if this is a Device submenu or Number of Qubits submenu
        is_device_menu = parent_item["text"] == "Device"
        is_qubits_menu = parent_item["text"] == "Number of Qubits"

        # Draw nested submenu items
        for i, item in enumerate(nested_items):
            item_y = submenu_y + i * item_height
            item_rect = pygame.Rect(submenu_x, item_y, max_width, item_height)

            # Highlight hovered item
            if item_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, (90, 90, 100), item_rect)

            # Handle different types of nested submenus
            if is_device_menu:
                # Device submenu - highlight current device
                device_name = item["text"]
                is_current_device = device_name == self.current_device
                text_color = (255, 255, 100) if is_current_device else (200, 200, 200)

                # Add asterisk for current device
                display_text = (
                    f"* {device_name}" if is_current_device else f"  {device_name}"
                )
            elif is_qubits_menu:
                # Number of Qubits submenu - standard styling
                text_color = (200, 200, 200)
                display_text = f"  {item['text']}"
            else:
                # Default styling
                text_color = (200, 200, 200)
                display_text = f"  {item['text']}"

            text_surf = self.menu_font.render(display_text, True, text_color)
            text_rect = text_surf.get_rect(x=submenu_x + 10, centery=item_rect.centery)
            screen.blit(text_surf, text_rect)
