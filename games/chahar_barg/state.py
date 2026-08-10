"""
Round state for Chahar Barg (Four Leaves / Yazdah) - 2 player mode.
Fully independent from other games (per project rule).

این فایل فقط وضعیت "یک دور" بازی رو نگه می‌داره (نه کل مسابقه).
اطلاعات کل مسابقه (امتیاز تجمعی، شماره دور و غیره) تو game.py نگه داشته می‌شه.
"""

from games.chahar_barg.card import Card


class ChaharBargState:
    def __init__(self):
        self.table_cards: list[Card] = []
        self.current_turn: int | None = None  # user_id بازیکنی که نوبتشه

        # امتیاز سورهایی که تو همین دور زده شده (کلید: user_id)
        self.sour_points: dict[int, int] = {}

        # آخرین بازیکنی که کارتی جمع کرده (برای دادن کارت‌های ته‌مونده‌ی زمین)
        self.last_capturer: int | None = None

        # وقتی deck خالی شده و این آخرین دست (۸ برگ پایانی) در حال بازی شدنه
        self.is_final_deal: bool = False

        self.round_over: bool = False

    def to_dict(self) -> dict:
        return {
            "table_cards": [card.to_dict() for card in self.table_cards],
            "current_turn": self.current_turn,
            "sour_points": self.sour_points,
            "last_capturer": self.last_capturer,
            "is_final_deal": self.is_final_deal,
            "round_over": self.round_over,
        }
