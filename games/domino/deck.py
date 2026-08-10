"""
Deck (boneyard) for Domino (Double-Six set) - 2 player mode.
Fully independent from other games (per project rule).
"""

import random

from games.domino.tile import Tile


class Deck:
    def __init__(self):
        self.tiles: list[Tile] = []
        self.build()

    def build(self):
        self.tiles = [
            Tile(left, right)
            for left in range(0, 7)
            for right in range(left, 7)
        ]

    def shuffle(self):
        random.shuffle(self.tiles)

    def draw(self, count: int = 1) -> list[Tile]:
        drawn = self.tiles[:count]
        self.tiles = self.tiles[count:]
        return drawn

    def draw_one(self) -> Tile | None:
        if self.is_empty():
            return None
        return self.tiles.pop(0)

    def is_empty(self) -> bool:
        return len(self.tiles) == 0

    def remaining(self) -> int:
        return len(self.tiles)
