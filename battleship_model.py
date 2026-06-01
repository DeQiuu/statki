import random
from dataclasses import dataclass, field

from battleship_constants import BOARD_SIZE


@dataclass
class Ship:
    cells: list[tuple[int, int]]
    hits: set[tuple[int, int]] = field(default_factory=set)

    @property
    def sunk(self) -> bool:
        return len(self.hits) == len(self.cells)


class Board:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.ship_map = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.shots = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.ships: list[Ship] = []

    @staticmethod
    def _neighbors(row: int, col: int) -> set[tuple[int, int]]:
        cells: set[tuple[int, int]] = set()
        for new_row in range(max(0, row - 1), min(BOARD_SIZE - 1, row + 1) + 1):
            for new_col in range(max(0, col - 1), min(BOARD_SIZE - 1, col + 1) + 1):
                cells.add((new_row, new_col))
        return cells

    def can_place(self, cells: list[tuple[int, int]]) -> bool:
        occupied = set(cells)
        for row, col in cells:
            if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
                return False
            if self.ship_map[row][col] is not None:
                return False
            for neighbor_row, neighbor_col in self._neighbors(row, col):
                if self.ship_map[neighbor_row][neighbor_col] is not None and (
                    neighbor_row,
                    neighbor_col,
                ) not in occupied:
                    return False
        return True

    def place_ship(self, cells: list[tuple[int, int]]) -> bool:
        if not self.can_place(cells):
            return False

        ship_id = len(self.ships) + 1
        for row, col in cells:
            self.ship_map[row][col] = ship_id
        self.ships.append(Ship(cells=list(cells)))
        return True

    def receive_shot(self, row: int, col: int) -> str:
        if self.shots[row][col] is not None:
            return "repeat"

        ship_id = self.ship_map[row][col]
        if ship_id is None:
            self.shots[row][col] = "miss"
            return "miss"

        self.shots[row][col] = "hit"
        ship = self.ships[ship_id - 1]
        ship.hits.add((row, col))
        if ship.sunk:
            return "sunk"
        return "hit"

    def all_ships_sunk(self) -> bool:
        return all(ship.sunk for ship in self.ships)

    def available_targets(self) -> list[tuple[int, int]]:
        return [
            (row, col)
            for row in range(BOARD_SIZE)
            for col in range(BOARD_SIZE)
            if self.shots[row][col] is None
        ]

    def place_random_fleet(self, ship_sizes: list[int]) -> None:
        self.reset()
        for size in ship_sizes:
            self._place_random_ship(size)

    def _place_random_ship(self, size: int) -> None:
        for _ in range(1000):
            vertical = random.choice((True, False))
            if vertical:
                start_row = random.randrange(BOARD_SIZE - size + 1)
                start_col = random.randrange(BOARD_SIZE)
                cells = [(start_row + offset, start_col) for offset in range(size)]
            else:
                start_row = random.randrange(BOARD_SIZE)
                start_col = random.randrange(BOARD_SIZE - size + 1)
                cells = [(start_row, start_col + offset) for offset in range(size)]

            if self.place_ship(cells):
                return

        raise RuntimeError("Unable to place a random ship")
