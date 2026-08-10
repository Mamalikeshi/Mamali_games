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

    def is_empty(self) -> bool:
        return len(self.cards) == 0

    def remaining(self) -> int:
        return len(self.cards)
