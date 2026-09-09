"""
Deck model for Chahar Barg (Four Leaves / Yazdah).
Fully independent from other games (per project rule).
"""

import random

from games.chahar_barg.card import Card, SUITS, RANKS


class Deck:
    def __init__(self):
        self.cards: list[Card] = []
        self.build()

    def build(self):
        self.cards = [
            Card(suit, rank)
            for suit in SUITS
            for rank in RANKS
        ]

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, count: int = 1) -> list[Card]:
        drawn = self.cards[:count]
        self.cards = self.cards[count:]
        return drawn

    def draw_no_jacks(self, count: int = 1) -> list[Card]:
        """
        مثل draw، ولی تضمین می‌کند هیچ‌کدام از کارت‌های کشیده‌شده
        سرباز نباشند (برای پخش اولیه‌ی چهار برگ وسط زمین).

        سرباز‌هایی که کنار گذاشته می‌شوند، به‌صورت تصادفی به بقیه‌ی
        دسته برگردانده می‌شوند تا ترتیب بازی به‌هم نخورد.
        """
        drawn: list[Card] = []
        set_aside: list[Card] = []

        while len(drawn) < count and self.cards:
            card = self.cards.pop(0)

            if card.is_jack():
                set_aside.append(card)
            else:
                drawn.append(card)

        for jack in set_aside:
            insert_pos = random.randint(0, len(self.cards))
            self.cards.insert(insert_pos, jack)

        return drawn

    def is_empty(self) -> bool:
        return len(self.cards) == 0

    def remaining(self) -> int:
        return len(self.cards)
