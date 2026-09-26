"""
Player model for Daberna (Iranian 90-ball Bingo).
Fully independent from other games (per project rule).
"""

from games.daberna.card import Card

MAX_CARDS_PER_PLAYER = 2


class Player:
    def __init__(self, user_id: int, username: str):
        self.user_id = user_id
        self.username = username
        self.is_ready: bool = False
        self.cards: list[Card] = []

    def add_card(self) -> Card | None:
        if len(self.cards) >= MAX_CARDS_PER_PLAYER:
            return None
        card = Card(card_id=f"{self.user_id}-{len(self.cards) + 1}")
        self.cards.append(card)
        return card

    def best_remaining_count(self, drawn_numbers: set[int]) -> int | None:
        if not self.cards:
            return None
        return min(card.remaining_count(drawn_numbers) for card in self.cards)

    def has_winning_card(self, drawn_numbers: set[int]) -> Card | None:
        for card in self.cards:
            if card.is_complete(drawn_numbers):
                return card
        return None

    def to_dict(self, drawn_numbers: set[int]) -> dict:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "is_ready": self.is_ready,
            "card_count": len(self.cards),
            "best_remaining_count": self.best_remaining_count(drawn_numbers),
        }
