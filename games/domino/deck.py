"""
Deck (boneyard) for Domino (Double-Six set) - 2 player mode.
Fully independent from other games (per project rule).

طبق قانون رسمی دومینوی دو نفره: همیشه آخرین مهره‌ی باقیمانده
در بازار به‌صورت رو به پایین باقی می‌ماند و هیچ بازیکنی
اجازه‌ی برداشتن آن را ندارد.
"""

import random

from games.domino.tile import Tile

# تعداد مهره‌ای که همیشه باید دست‌نخورده در بازار بماند
RESERVED_TILES = 1


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

        # هرگز اجازه نده مهره‌ی رزرو شده کشیده شود
        available = max(
            0,
            len(self.tiles) - RESERVED_TILES,
        )

        count = min(count, available)

        drawn = self.tiles[:count]
        self.tiles = self.tiles[count:]
        return drawn

    def draw_one(self) -> Tile | None:
        drawn = self.draw(1)
        if not drawn:
            return None
        return drawn[0]

    def is_empty(self) -> bool:
        # وقتی فقط مهره‌ی رزرو شده باقی مانده، بازار از نظر
        # قابلیت کشیدن خالی محسوب می‌شود
        return len(self.tiles) <= RESERVED_TILES

    def remaining(self) -> int:
        return len(self.tiles)
