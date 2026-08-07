from dataclasses import dataclass, field

from .card import Card


@dataclass
class Player:
    user_id: int
    username: str

    hand: list[Card] = field(default_factory=list)

    tricks: int = 0

    is_ready: bool = False

    hokm: bool = False

    def receive_cards(self, cards: list[Card]):
        self.hand.extend(cards)

    def sort_hand(self):
        self.hand.sort(key=lambda c: (c.suit, c.rank))

    def play_card(self, index: int):
        if index < 0 or index >= len(self.hand):
            raise ValueError("Invalid card index")

        return self.hand.pop(index)

    def reset(self):
        self.hand.clear()
        self.tricks = 0
        self.is_ready = False
        self.hokm = False
