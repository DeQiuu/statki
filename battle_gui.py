import PySimpleGUI as sg

from battleship_ai import choose_random_shot
from battleship_constants import (
    ACCENT_COLOR,
    APP_BACKGROUND,
    BUTTON_FONT,
    BUTTON_PRIMARY_COLOR,
    BUTTON_SECONDARY_COLOR,
    CARD_BACKGROUND,
    MODE_LABELS,
    SUBTITLE_FONT,
    TEXT_SECONDARY,
    TITLE_FONT,
    configure_theme,
)
from battleship_model import Board
from battleship_ui import BOARD_PREFIX, build_board_frame, cell_name, render_board

PLAYER_BOARD_PREFIX = "PLAYER_BOARD"


class BattleSession:
    def __init__(self, mode: str, player_board: Board, enemy_board: Board) -> None:
        if mode not in MODE_LABELS:
            raise ValueError(f"Unknown game mode: {mode}")

        self.mode = mode
        self.player_board = player_board
        self.enemy_board = enemy_board
        self.window: sg.Window | None = None
        self.current_player = 1
        self.game_over = False
        self.status_message = ""

    def _mode_title(self) -> str:
        return f"Tryb: {MODE_LABELS[self.mode]}"

    def _target_board_title(self) -> str:
        if self.mode == "singleplayer":
            return "Plansza ataku - komputer"
        return f"Plansza ataku - gracz {self._other_player(self.current_player)}"

    @staticmethod
    def _other_player(player: int) -> int:
        return 2 if player == 1 else 1

    def _board_panel(self, title: str, prefix: str) -> sg.Frame:
        return sg.Frame(
            "",
            [
                [
                    sg.Text(
                        title,
                        font=SUBTITLE_FONT,
                        text_color=ACCENT_COLOR,
                        background_color=CARD_BACKGROUND,
                        justification="center",
                        expand_x=True,
                    )
                ],
                [build_board_frame(prefix)],
            ],
            background_color=CARD_BACKGROUND,
            border_width=1,
            relief=sg.RELIEF_RIDGE,
            pad=(6, 0),
            element_justification="center",
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
                        key="-STATUS-",
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
            ],
            background_color=CARD_BACKGROUND,
            border_width=1,
            relief=sg.RELIEF_RIDGE,
            pad=(0, 12),
        )

        if self.mode == "singleplayer":
            board_row = [
                self._board_panel("Twoja flota", PLAYER_BOARD_PREFIX),
                self._board_panel(self._target_board_title(), BOARD_PREFIX),
            ]
        else:
            board_row = [self._board_panel(self._target_board_title(), BOARD_PREFIX)]

        layout = [
            [header_card],
            board_row,
            [
                sg.Frame(
                    "",
                    [
                        [
                            sg.Button(
                                "Nowa gra",
                                key="-NEW-",
                                size=(12, 1),
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
                    ],
                    background_color=CARD_BACKGROUND,
                    border_width=1,
                    relief=sg.RELIEF_RIDGE,
                    pad=(0, 0),
                    element_justification="center",
                )
            ],
        ]

        return sg.Window(
            "Statki - Bitwa",
            layout,
            finalize=True,
            element_justification="center",
            background_color=APP_BACKGROUND,
            margins=(24, 20),
        )

    def _set_header(self, status_text: str, detail_text: str) -> None:
        if self.window is None:
            return

        self.window["-MODE-"].update(self._mode_title())
        self.window["-STATUS-"].update(status_text)
        self.window["-DETAIL-"].update(detail_text)

    def _render(self) -> None:
        if self.window is None:
            return

        if self.mode == "singleplayer":
            render_board(
                self.window,
                self.player_board,
                PLAYER_BOARD_PREFIX,
                reveal_ships=True,
                interactive=False,
            )
            render_board(
                self.window,
                self.enemy_board,
                BOARD_PREFIX,
                reveal_ships=False,
                interactive=not self.game_over,
            )
            detail_text = "Twoja flota pozostaje widoczna po lewej stronie. Kliknij planszę ataku, aby oddać strzał."
        else:
            target_board = self._target_board()
            render_board(
                self.window,
                target_board,
                BOARD_PREFIX,
                reveal_ships=False,
                interactive=not self.game_over,
            )
            detail_text = "Kliknij pole na planszy ataku."

        self._set_header(
            self.status_message or f"Tura gracza {self.current_player}.",
            detail_text,
        )

    def _target_board(self) -> Board:
        if self.mode == "singleplayer":
            return self.enemy_board
        return self.enemy_board if self.current_player == 1 else self.player_board

    def _shot_result_text(self, result: str, row: int, col: int) -> str:
        location = cell_name(row, col)
        if result == "miss":
            return f"Strzał {location} -> pudło"
        if result == "hit":
            return f"Strzał {location} -> trafienie"
        if result == "sunk":
            return f"Strzał {location} -> zatopiony"
        return f"Strzał {location} -> powtórka"

    def _singleplayer_ai_turn(self) -> str:
        ai_row, ai_col = choose_random_shot(self.player_board)
        ai_result = self.player_board.receive_shot(ai_row, ai_col)
        return f"Komputer: {self._shot_result_text(ai_result, ai_row, ai_col)}"

    def _handle_battle_shot(self, row: int, col: int) -> None:
        target_board = self._target_board()
        result = target_board.receive_shot(row, col)

        if result == "repeat":
            self.status_message = f"Pole {cell_name(row, col)} zostało już użyte."
            self._render()
            return

        player_result = self._shot_result_text(result, row, col)

        if self.mode == "singleplayer":
            if target_board.all_ships_sunk():
                self.game_over = True
                self.status_message = f"{player_result}. Wygrywasz."
                self._render()
                return

            ai_result = self._singleplayer_ai_turn()
            if self.player_board.all_ships_sunk():
                self.game_over = True
                self.status_message = f"{player_result}. {ai_result}. Komputer wygrywa."
                self._render()
                return

            self.status_message = f"{player_result}. {ai_result}. Twoja tura."
            self._render()
            return

        if target_board.all_ships_sunk():
            self.game_over = True
            self.status_message = f"{player_result}. Gracz {self.current_player} wygrywa."
            self._render()
            return

        self.current_player = self._other_player(self.current_player)
        self.status_message = (
            f"{player_result}. Przekaż ekran graczowi {self.current_player}."
        )
        self._render()

    def run(self) -> str:
        self.window = self._build_window()
        self._render()

        try:
            while True:
                event, _values = self.window.read()

                if event in (sg.WINDOW_CLOSED, "-MENU-"):
                    return "menu"

                if event == "-NEW-":
                    return "restart"

                if isinstance(event, tuple) and len(event) == 3:
                    _prefix, row, col = event
                    if not self.game_over:
                        self._handle_battle_shot(row, col)

        finally:
            if self.window is not None:
                self.window.close()
            self.window = None
