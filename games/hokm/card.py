from dataclasses import dataclass


SUITS = ["hearts", "diamonds", "clubs", "spades"]

RANKS = [
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "J",
    "Q",
    "K",
    "A",
]


@dataclass(frozen=True)
class Card:
    suit: str
    rank: str

    def to_dict(self):
        return {
            "suit": self.suit,
            "rank": self.rank,
        }

    def __str__(self):
        return f"{self.rank} of {self.suit}"
