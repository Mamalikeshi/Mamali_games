"""
Player model for Domino (Double-Six set) - 2 player mode.
Fully independent from other games (per project rule).
"""

from games.domino.tile import Tile


class Player:
    def __init__(self, user_id: int, username: str):
        self.user_id = user_id
        self.username = username
        self.is_ready: bool = False

        self.hand: list[Tile] = []
        self.score: int = 0

    def add_to_hand(self, tiles: list[Tile]):
        self.hand.extend(tiles)

    def remove_from_hand(self, tile: Tile) -> bool:
        for existing in self.hand:
            if existing == tile:
                self.hand.remove(existing)
                return True
        return False

    def hand_pip_sum(self) -> int:
        return sum(t.pip_sum for t in self.hand)

    def has_playable_tile(self, left_end: int | None, right_end: int | None) -> bool:
        if left_end is None and right_end is None:
            return len(self.hand) > 0
        for tile in self.hand:
            if tile.has_value(left_end) or tile.has_value(right_end):
                return True
        return False

    def hand_to_dict(self) -> list[dict]:
        return [tile.to_dict() for tile in self.hand]

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "is_ready": self.is_ready,
            "score": self.score,
            "hand_count": len(self.hand),
        }
