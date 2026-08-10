"""
Game state for Chahar Barg (Four Leaves / Yazdah) - 2 player mode.
Fully independent from other games (per project rule).
"""

from games.chahar_barg.card import Card


class ChaharBargState:
    def __init__(self):
        self.table_cards: list[Card] = []
        self.current_turn: int | None = None  # user_id بازیکنی که نوبتشه

        # چند بار هر بازیکن سور زده (برای امتیاز پایان دور)
        self.sour_count: dict[int, int] = {}

        # آخرین بازیکنی که کارتی جمع کرده (برای وقتی دست بازیکن‌ها تموم شد
        # و کارت‌های باقی‌مونده روی زمین باید به یکی داده بشه)
        self.last_capturer: int | None = None

        self.round_over: bool = False
        self.game_over: bool = False

    def to_dict(self) -> dict:
        return {
            "table_cards": [card.to_dict() for card in self.table_cards],
            "current_turn": self.current_turn,
            "sour_count": self.sour_count,
            "last_capturer": self.last_capturer,
            "round_over": self.round_over,
            "game_over": self.game_over,
        }
