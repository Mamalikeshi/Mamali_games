import random

from .card import Card, SUITS, RANKS


class Deck:
    def __init__(self):
        self.cards = [
            Card(suit, rank)
            for suit in SUITS
            for rank in RANKS
        ]

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, players=2, cards_per_player=13):
        if len(self.cards) < players * cards_per_player:
            raise ValueError("Not enough cards.")

        hands = []

        for _ in range(players):
            hand = []
            for _ in range(cards_per_player):
                hand.append(self.cards.pop())
            hands.append(hand)

        return hands

    def remaining(self):
        return len(self.cards)
