import PySimpleGUI as sg

from battleship_constants import (
    APP_BACKGROUND,
    BUTTON_DANGER_COLOR,
    BUTTON_FONT,
    BUTTON_PRIMARY_COLOR,
    BUTTON_SECONDARY_COLOR,
    CARD_BACKGROUND,
    ACCENT_COLOR,
    MODE_MULTIPLAYER,
    MODE_SINGLEPLAYER,
    SUBTITLE_FONT,
    TITLE_FONT,
    TEXT_SECONDARY,
    configure_theme,
)


def build_menu_window() -> sg.Window:
    configure_theme()

    layout = [
        [
            sg.Text(
                "Statki",
                font=TITLE_FONT,
                text_color=ACCENT_COLOR,
                background_color=APP_BACKGROUND,
                justification="center",
                expand_x=True,
            )
        ],
        [
            sg.Text(
                "Wybierz tryb gry",
                font=SUBTITLE_FONT,
                text_color=TEXT_SECONDARY,
                background_color=APP_BACKGROUND,
                justification="center",
                expand_x=True,
            )
        ],
        [
            sg.Frame(
                "",
                [
                    [
                        sg.Button(
                            "Jednoosobowa",
                            key="-SINGLE-",
                            size=(16, 1),
                            font=BUTTON_FONT,
                            button_color=BUTTON_PRIMARY_COLOR,
                            pad=(8, 8),
                        ),
                        sg.Button(
                            "Dwuosobowa",
                            key="-MULTI-",
                            size=(16, 1),
                            font=BUTTON_FONT,
                            button_color=BUTTON_SECONDARY_COLOR,
                            pad=(8, 8),
                        ),
                    ]
                ],
                background_color=CARD_BACKGROUND,
                border_width=1,
                relief=sg.RELIEF_RIDGE,
                pad=(0, 10),
                element_justification="center",
            )
        ],
        [
            sg.Button(
                "Wyjdź",
                key="-EXIT-",
                size=(16, 1),
                font=BUTTON_FONT,
                button_color=BUTTON_DANGER_COLOR,
                pad=(0, 8),
            )
        ],
    ]
    return sg.Window(
        "Statki",
        layout,
        element_justification="center",
        finalize=True,
        background_color=APP_BACKGROUND,
        margins=(32, 28),
        resizable=False,
    )


def main() -> None:
    window = build_menu_window()

    try:
        while True:
            event, _values = window.read()
            if event in (sg.WINDOW_CLOSED, "-EXIT-"):
                break

            if event in ("-SINGLE-", "-MULTI-"):
                from game_gui import launch_game

                mode = MODE_SINGLEPLAYER if event == "-SINGLE-" else MODE_MULTIPLAYER
                window.hide()
                try:
                    launch_game(mode)
                finally:
                    window.un_hide()
    finally:
        window.close()


if __name__ == "__main__":
    main()
