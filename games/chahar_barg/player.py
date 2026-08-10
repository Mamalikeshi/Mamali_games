"""
Player model for Chahar Barg (Four Leaves / Yazdah).
Fully independent from other games (per project rule).
"""

from games.chahar_barg.card import Card


class Player:
    def __init__(self, user_id: int, username: str):
        self.user_id = user_id
        self.username = username
        self.is_ready: bool = False

        self.hand: list[Card] = []
        self.captured: list[Card] = []  # کارت‌هایی که جمع کرده (سور)
        self.score: int = 0
        self.team: int | None = None  # فقط تو حالت چهارنفره پر می‌شه (0 یا 1)

    def add_to_hand(self, cards: list[Card]):
        self.hand.extend(cards)

    def remove_from_hand(self, card: Card) -> bool:
        for existing in self.hand:
            if existing == card:
                self.hand.remove(existing)
                return True
        return False

    def capture(self, cards: list[Card]):
        self.captured.extend(cards)

    def hand_to_dict(self) -> list[dict]:
        return [card.to_dict() for card in self.hand]

    def captured_to_dict(self) -> list[dict]:
        return [card.to_dict() for card in self.captured]

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "is_ready": self.is_ready,
            "team": self.team,
            "score": self.score,
            "hand_count": len(self.hand),
            "captured_count": len(self.captured),
        }
