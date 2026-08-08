import random

from games.hokm.card import Card


class Deck:
    def __init__(self):
        self.cards = []

        for suit in Card.SUITS:
            for rank in Card.RANKS:
                self.cards.append(
                    Card(suit, rank)
                )

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, players, cards_each=13):
        if len(players) != 2:
            raise ValueError(
                "Hokm requires exactly 2 players."
            )

        required_cards = len(players) * cards_each

        if len(self.cards) < required_cards:
            raise ValueError(
                "Not enough cards in deck."
            )

        for player in players:
            player.hand = []

        for _ in range(cards_each):
            for player in players:
                player.hand.append(
                    self.cards.pop()
                )

        for player in players:
            player.sort_hand()
