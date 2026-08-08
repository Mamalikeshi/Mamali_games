class Card:
    SUITS = {
        "hearts",
        "diamonds",
        "clubs",
        "spades",
    }

    RANKS = {
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "6": 6,
        "7": 7,
        "8": 8,
        "9": 9,
        "10": 10,
        "J": 11,
        "Q": 12,
        "K": 13,
        "A": 14,
    }

    def __init__(self, suit: str, rank: str):
        if suit not in self.SUITS:
            raise ValueError("Invalid suit.")

        if rank not in self.RANKS:
            raise ValueError("Invalid rank.")

        self.suit = suit
        self.rank = rank
        self.rank_value = self.RANKS[rank]

    def to_dict(self):
        return {
            "suit": self.suit,
            "rank": self.rank,
            "rank_value": self.rank_value,
        }

    def __repr__(self):
        return f"{self.rank} of {self.suit}"
