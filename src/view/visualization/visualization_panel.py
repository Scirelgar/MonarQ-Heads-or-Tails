import flet as ft
from flet import Container, Row, MainAxisAlignment, LayoutControl


class VisualizationPanel(Container):

    def __init__(self, panel_elements: list[LayoutControl]):
        super().__init__(expand=True)
        self._min_left_width = 200.0
        self._max_left_width = 700.0
        self._left_width = self._min_left_width
        self._left_panel = panel_elements[0]
        self._left_panel.width = self._left_width
        self._left_panel.expand = False
        self.content = Row(
            [
                self._left_panel,
                ft.GestureDetector(
                    content=ft.VerticalDivider(),
                    mouse_cursor=ft.MouseCursor.RESIZE_LEFT_RIGHT,
                    drag_interval=10,
                    on_pan_update=self.move_vertical_divider,
                ),
                panel_elements[1],
            ],
            alignment=MainAxisAlignment.SPACE_AROUND,
            expand=True,
        )

    def move_vertical_divider(self, e: ft.DragUpdateEvent):
        next_width = self._left_width + e.local_delta.x
        next_width = max(self._min_left_width, min(next_width, self._max_left_width))

        if next_width != self._left_width:
            self._left_width = next_width
            self._left_panel.width = self._left_width
            self.update()
