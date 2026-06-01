import PySimpleGUI as sg

from battleship_constants import (
    APP_BACKGROUND,
    ACCENT_COLOR,
    BOARD_SIZE,
    BUTTON_DANGER_COLOR,
    BUTTON_FONT,
    BUTTON_PRIMARY_COLOR,
    BUTTON_SECONDARY_COLOR,
    CARD_BACKGROUND,
    MODE_LABELS,
    SHIP_SIZES,
    SUBTITLE_FONT,
    TEXT_SECONDARY,
    TITLE_FONT,
    configure_theme,
)
from battleship_model import Board
from battleship_ui import (
    BOARD_PREFIX,
    bind_board_hover,
    build_board_frame,
    cell_name,
    render_board,
    ship_cells,
)


HOVER_ENTER = "ENTER"
HOVER_LEAVE = "LEAVE"


class PlacementSession:
    def __init__(
        self,
        board: Board,
        *,
        mode: str,
        title: str,
        interactive: bool,
        reveal_ships: bool = True,
        continue_label: str = "Kontynuuj",
    ) -> None:
        if mode not in MODE_LABELS:
            raise ValueError(f"Unknown game mode: {mode}")

        self.board = board
        self.mode = mode
        self.title = title
        self.interactive = interactive
        self.reveal_ships = reveal_ships
        self.continue_label = continue_label
        self.window: sg.Window | None = None
        self.orientation = "horizontal"
        self.next_ship_index = 0
        self.preview_cells: set[tuple[int, int]] = set()
        self.preview_valid = True
        self.status_message = ""

    def _current_ship_size(self) -> int:
        return SHIP_SIZES[self.next_ship_index]

    def _orientation_label(self) -> str:
        return "pozioma" if self.orientation == "horizontal" else "pionowa"

    def _board_title(self) -> str:
        return self.title

    def _mode_title(self) -> str:
        return f"Tryb: {MODE_LABELS[self.mode]}"

    def _detail_text(self) -> str:
        if not self.interactive:
            return self.status_message or "Flota gotowa. Kontynuuj do okna bitwy."
        if self.next_ship_index >= len(SHIP_SIZES):
            return self.status_message or "Flota gotowa."
        if self.status_message:
            return self.status_message
        return (
            f"Następny statek: {self._current_ship_size()} | "
            f"orientacja: {self._orientation_label()} | "
            "Kliknij pole startowe na swojej planszy."
        )

    def _build_window(self) -> sg.Window:
        configure_theme()

        header_card = sg.Frame(
            "",
            [
                [
                    sg.Text(
                        "Statki",
                        font=TITLE_FONT,
                        text_color=ACCENT_COLOR,
                        background_color=CARD_BACKGROUND,
                        justification="center",
                        expand_x=True,
                    )
                ],
                [
                    sg.Text(
                        "",
                        key="-MODE-",
                        size=(90, 1),
                        font=SUBTITLE_FONT,
                        text_color=TEXT_SECONDARY,
                        background_color=CARD_BACKGROUND,
                        justification="center",
                        expand_x=True,
                    )
                ],
                [
                    sg.Text(
                        "",
                        key="-DETAIL-",
                        size=(90, 1),
                        font=SUBTITLE_FONT,
                        text_color=TEXT_SECONDARY,
                        background_color=CARD_BACKGROUND,
                        justification="center",
                        expand_x=True,
                    )
                ],
                [
                sg.Text(
                    self._board_title(),
                    key="-BOARD-TITLE-",
                    font=SUBTITLE_FONT,
                    text_color=ACCENT_COLOR,
                        background_color=CARD_BACKGROUND,
                        justification="center",
                        expand_x=True,
                    )
                ],
            ],
            background_color=CARD_BACKGROUND,
            border_width=1,
            relief=sg.RELIEF_RIDGE,
            pad=(0, 12),
        )

        layout = [
            [header_card],
            [build_board_frame(BOARD_PREFIX)],
            [
                sg.Frame(
                    "",
                    [self._controls_row()],
                    background_color=CARD_BACKGROUND,
                    border_width=1,
                    relief=sg.RELIEF_RIDGE,
                    pad=(0, 0),
                    element_justification="center",
                )
            ],
        ]

        return sg.Window(
            f"Statki - {self.title}",
            layout,
            finalize=True,
            element_justification="center",
            background_color=APP_BACKGROUND,
            margins=(24, 20),
        )

    def _controls_row(self) -> list[sg.Element]:
        if self.interactive:
            return [
            sg.Button(
                "Obróć",
                key="-ROTATE-",
                size=(12, 1),
                font=BUTTON_FONT,
                button_color=BUTTON_PRIMARY_COLOR,
                pad=(6, 8),
            ),
            sg.Button(
                "Resetuj",
                key="-RESET-",
                size=(12, 1),
                font=BUTTON_FONT,
                button_color=BUTTON_DANGER_COLOR,
                pad=(6, 8),
            ),
            sg.Button(
                "Menu główne",
                    key="-MENU-",
                    size=(12, 1),
                    font=BUTTON_FONT,
                    button_color=BUTTON_SECONDARY_COLOR,
                    pad=(6, 8),
                ),
            ]

        return [
            sg.Button(
                self.continue_label,
                key="-CONTINUE-",
                size=(14, 1),
                font=BUTTON_FONT,
                button_color=BUTTON_PRIMARY_COLOR,
                pad=(6, 8),
            ),
            sg.Button(
                "Menu główne",
                key="-MENU-",
                size=(12, 1),
                font=BUTTON_FONT,
                button_color=BUTTON_SECONDARY_COLOR,
                pad=(6, 8),
            ),
        ]

    def _set_status(self) -> None:
        if self.window is None:
            return

        self.window["-MODE-"].update(self._mode_title())
        self.window["-DETAIL-"].update(self._detail_text())
        self.window["-BOARD-TITLE-"].update(self._board_title())

    def _render(self) -> None:
        if self.window is None:
            return

        self._set_status()
        render_board(
            self.window,
            self.board,
            BOARD_PREFIX,
            reveal_ships=self.reveal_ships,
            interactive=self.interactive,
            preview_cells=self.preview_cells if self.interactive else None,
            preview_valid=self.preview_valid,
        )

    def _bind_hover(self) -> None:
        if self.window is None or not self.interactive:
            return

        bind_board_hover(self.window, BOARD_PREFIX)

    def _clear_preview(self) -> None:
        self.preview_cells.clear()
        self.preview_valid = True
        self._render()

    def _set_preview(self, row: int, col: int) -> None:
        candidate_cells = ship_cells(
            row,
            col,
            self._current_ship_size(),
            self.orientation,
        )
        self.preview_cells = {
            (preview_row, preview_col)
            for preview_row, preview_col in candidate_cells
            if 0 <= preview_row < BOARD_SIZE and 0 <= preview_col < BOARD_SIZE
        }
        self.preview_valid = self.board.can_place(candidate_cells)
        self._render()

    def _place_ship_at(self, row: int, col: int) -> None:
        candidate_cells = ship_cells(
            row,
            col,
            self._current_ship_size(),
            self.orientation,
        )

        if not self.board.place_ship(candidate_cells):
            self.status_message = f"Nie można umieścić statku na polu {cell_name(row, col)}."
            self._clear_preview()
            return

        self.status_message = ""
        self.preview_cells.clear()
        self.preview_valid = True
        self.next_ship_index += 1
        if self.next_ship_index >= len(SHIP_SIZES):
            self.status_message = "Flota gotowa."
            raise StopIteration

        self._render()

    def run(self) -> bool:
        self.window = self._build_window()
        self._bind_hover()
        self._render()

        try:
            while True:
                event, _values = self.window.read()

                if event in (sg.WINDOW_CLOSED, "-MENU-"):
                    return False

                if not self.interactive:
                    if event == "-CONTINUE-":
                        return True
                    continue

                if event == "-ROTATE-":
                    self.orientation = (
                        "vertical" if self.orientation == "horizontal" else "horizontal"
                    )
                    self._clear_preview()
                    continue

                if event == "-RESET-":
                    self.board.reset()
                    self.orientation = "horizontal"
                    self.next_ship_index = 0
                    self.status_message = ""
                    self._clear_preview()
                    continue

                if isinstance(event, tuple) and len(event) == 2:
                    key, action = event
                    if action == HOVER_ENTER and isinstance(key, tuple) and len(key) == 3:
                        _prefix, row, col = key
                        self._set_preview(row, col)
                        continue
                    if action == HOVER_LEAVE:
                        self._clear_preview()
                        continue

                if isinstance(event, tuple) and len(event) == 3:
                    _prefix, row, col = event
                    try:
                        self._place_ship_at(row, col)
                    except StopIteration:
                        return True

        finally:
            if self.window is not None:
                self.window.close()
            self.window = None
