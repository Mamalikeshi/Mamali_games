"""
Card model for Chahar Barg (Four Leaves / Yazdah).
Fully independent from other games (per project rule).
"""

SUITS = ["hearts", "diamonds", "clubs", "spades"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

# مقدار عددی هر کارت برای جمع کردن (سور)
# A = 1 , 2-10 = همون عدد , J/Q/K = 0 (فقط برای جفت شدن با هم استفاده میشن)
RANK_VALUES = {
    "A": 1, "2": 2, "3": 3, "4": 4, "5": 5,
    "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
    "J": 0, "Q": 0, "K": 0,
}


class Card:
    def __init__(self, suit: str, rank: str):
        if suit not in SUITS:
            raise ValueError(f"Invalid suit: {suit}")
        if rank not in RANKS:
            raise ValueError(f"Invalid rank: {rank}")
        self.suit = suit
        self.rank = rank

    @property
    def value(self) -> int:
        return RANK_VALUES[self.rank]

    def matches(self, other: "Card") -> bool:
        """
        دو کارت وقتی جفت میشن (قابل جمع کردن هستن) که رنک یکسان داشته باشن.
        """
        return self.rank == other.rank

    def is_jack(self) -> bool:
        return self.rank == "J"

    def to_dict(self) -> dict:
        return {
            "suit": self.suit,
            "rank": self.rank,
            "value": self.value,
        }

    def __repr__(self) -> str:
        return f"{self.rank}-{self.suit}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.rank == other.rank
