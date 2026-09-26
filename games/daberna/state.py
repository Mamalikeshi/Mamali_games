"""
Round state for Daberna (Iranian 90-ball Bingo).
Fully independent from other games (per project rule).
"""

import time


class DabernaState:
    def __init__(self):
        self.start_time: float = time.time()
        self.drawn_numbers: list[int] = []
        self.is_finished: bool = False
        self.winners: list[dict] = []  # [{ "user_id":..., "username":..., "card_id":... }]

    @property
    def current_number(self) -> int | None:
        if not self.drawn_numbers:
            return None
        return self.drawn_numbers[-1]

    @property
    def drawn_set(self) -> set:
        return set(self.drawn_numbers)

    def to_dict(self) -> dict:
        return {
            "drawn_numbers": self.drawn_numbers,
            "current_number": self.current_number,
            "total_drawn": len(self.drawn_numbers),
            "is_finished": self.is_finished,
            "winners": self.winners,
        }
