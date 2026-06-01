import PySimpleGUI as sg

from battleship_constants import (
    BOARD_BUTTON_PAD,
    BOARD_CELL_SIZE,
    BOARD_FONT,
    BOARD_FRAME_PAD,
    BOARD_SIZE,
    COLUMN_LABELS,
    EMPTY_TEXT_COLOR,
    HIT_COLOR,
    HIT_TEXT_COLOR,
    MISS_COLOR,
    MISS_TEXT_COLOR,
    PREVIEW_COLOR,
    PREVIEW_INVALID_COLOR,
    ROW_LABELS,
    SEA_COLOR,
    SHIP_COLOR,
    PANEL_BACKGROUND,
    TEXT_SECONDARY,
)
from battleship_model import Board

BOARD_PREFIX = "BOARD"


def board_key(prefix: str, row: int, col: int) -> tuple[str, int, int]:
    return (prefix, row, col)


def cell_name(row: int, col: int) -> str:
    return f"{ROW_LABELS[row]}{COLUMN_LABELS[col]}"


def build_board_frame(prefix: str) -> sg.Frame:
    layout: list[list[sg.Element]] = []

    header_row: list[sg.Element] = [
        sg.Text(
            " ",
            size=BOARD_CELL_SIZE,
            background_color=PANEL_BACKGROUND,
        )
    ]
    for column_label in COLUMN_LABELS:
        header_row.append(
            sg.Text(
                column_label,
                size=BOARD_CELL_SIZE,
                justification="center",
                font=BOARD_FONT,
                text_color=TEXT_SECONDARY,
                background_color=PANEL_BACKGROUND,
            )
        )
    layout.append(header_row)

    for row_index, row_label in enumerate(ROW_LABELS):
        row_layout: list[sg.Element] = [
            sg.Text(
                row_label,
                size=BOARD_CELL_SIZE,
                justification="center",
                font=BOARD_FONT,
                text_color=TEXT_SECONDARY,
                background_color=PANEL_BACKGROUND,
            )
        ]
        for col_index in range(BOARD_SIZE):
            row_layout.append(
                sg.Button(
                    "",
                    key=board_key(prefix, row_index, col_index),
                    size=BOARD_CELL_SIZE,
                    pad=BOARD_BUTTON_PAD,
                    border_width=1,
                    font=BOARD_FONT,
                    button_color=(EMPTY_TEXT_COLOR, SEA_COLOR),
                )
            )
        layout.append(row_layout)

    return sg.Frame(
        "",
        layout,
        pad=BOARD_FRAME_PAD,
        background_color=PANEL_BACKGROUND,
        border_width=1,
        relief=sg.RELIEF_RIDGE,
    )


def ship_cells(
    row: int,
    col: int,
    size: int,
    orientation: str,
) -> list[tuple[int, int]]:
    if orientation == "horizontal":
        return [(row, col + offset) for offset in range(size)]
    return [(row + offset, col) for offset in range(size)]


def bind_board_hover(window: sg.Window, prefix: str) -> None:
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            element = window[board_key(prefix, row, col)]
            element.bind("<Enter>", "ENTER")
            element.bind("<Leave>", "LEAVE")


def render_board(
    window: sg.Window,
    board: Board,
    prefix: str,
    *,
    reveal_ships: bool,
    interactive: bool,
    preview_cells: set[tuple[int, int]] | None = None,
    preview_valid: bool = True,
) -> None:
    preview_lookup = preview_cells or set()
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            shot_state = board.shots[row][col]
            ship_present = board.ship_map[row][col] is not None
            is_preview = (row, col) in preview_lookup

            if is_preview:
                text = ""
                colors = (
                    EMPTY_TEXT_COLOR,
                    PREVIEW_COLOR if preview_valid else PREVIEW_INVALID_COLOR,
                )
            elif shot_state == "hit":
                text = "X"
                colors = (HIT_TEXT_COLOR, HIT_COLOR)
            elif shot_state == "miss":
                text = "o"
                colors = (MISS_TEXT_COLOR, MISS_COLOR)
            elif reveal_ships and ship_present:
                text = "S"
                colors = (EMPTY_TEXT_COLOR, SHIP_COLOR)
            else:
                text = ""
                colors = (EMPTY_TEXT_COLOR, SEA_COLOR)

            disabled = not interactive or (not reveal_ships and shot_state is not None)
            window[board_key(prefix, row, col)].update(
                text=text,
                button_color=colors,
                disabled=disabled,
            )
