import random

from battleship_model import Board


def choose_random_shot(board: Board) -> tuple[int, int]:
    targets = board.available_targets()
    if not targets:
        raise RuntimeError("No remaining targets")
    return random.choice(targets)
