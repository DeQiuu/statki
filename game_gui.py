from battleship_constants import MODE_MULTIPLAYER, MODE_SINGLEPLAYER, SHIP_SIZES
from battleship_model import Board
from battle_gui import BattleSession
from placement_gui import PlacementSession


def _run_singleplayer_setup() -> tuple[Board, Board] | None:
    player_board = Board()
    player_session = PlacementSession(
        player_board,
        mode=MODE_SINGLEPLAYER,
        title="Rozmieszczenie twojej floty",
        interactive=True,
    )
    if not player_session.run():
        return None

    ai_board = Board()
    ai_board.place_random_fleet(SHIP_SIZES)
    ai_session = PlacementSession(
        ai_board,
        mode=MODE_SINGLEPLAYER,
        title="Rozmieszczenie komputera",
        interactive=False,
        reveal_ships=False,
        continue_label="Rozpocznij bitwę",
    )
    if not ai_session.run():
        return None

    return player_board, ai_board


def _run_multiplayer_setup() -> tuple[Board, Board] | None:
    player_one_board = Board()
    player_one_session = PlacementSession(
        player_one_board,
        mode=MODE_MULTIPLAYER,
        title="Rozmieszczenie gracza 1",
        interactive=True,
    )
    if not player_one_session.run():
        return None

    player_two_board = Board()
    player_two_session = PlacementSession(
        player_two_board,
        mode=MODE_MULTIPLAYER,
        title="Rozmieszczenie gracza 2",
        interactive=True,
    )
    if not player_two_session.run():
        return None

    return player_one_board, player_two_board


def _run_match(mode: str, player_board: Board, enemy_board: Board) -> str:
    return BattleSession(mode, player_board, enemy_board).run()


def launch_game(mode: str) -> None:
    if mode not in (MODE_SINGLEPLAYER, MODE_MULTIPLAYER):
        raise ValueError(f"Unknown game mode: {mode}")

    while True:
        if mode == MODE_SINGLEPLAYER:
            boards = _run_singleplayer_setup()
            if boards is None:
                return
            player_board, enemy_board = boards
        else:
            boards = _run_multiplayer_setup()
            if boards is None:
                return
            player_board, enemy_board = boards

        action = _run_match(mode, player_board, enemy_board)
        if action != "restart":
            return


def main() -> None:
    launch_game(MODE_SINGLEPLAYER)


if __name__ == "__main__":
    main()
