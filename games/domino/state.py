"""
Round state for Domino (Double-Six set) - 2 player mode.
Fully independent from other games (per project rule).
"""

from games.domino.tile import Tile


class DominoState:
    def __init__(self):
        # مهره‌های چیده‌شده رو زمین، به ترتیب از چپ به راست
        self.board: list[Tile] = []

        self.left_end: int | None = None
        self.right_end: int | None = None

        self.current_turn: int | None = None  # user_id بازیکنی که نوبتشه

        # اگه بازی به بن‌بست خورده (هیچ‌کس نمی‌تونه بازی کنه و boneyard هم خالیه)
        self.is_blocked: bool = False

        self.round_over: bool = False

    def to_dict(self) -> dict:
        return {
            "board": [tile.to_dict() for tile in self.board],
            "left_end": self.left_end,
            "right_end": self.right_end,
            "current_turn": self.current_turn,
            "is_blocked": self.is_blocked,
            "round_over": self.round_over,
        }
