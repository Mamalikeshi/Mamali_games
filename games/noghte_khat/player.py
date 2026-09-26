"""
Player model for Noghte Khat (Dots and Boxes) - 2 player mode.
Fully independent from other games (per project rule).
"""


class Player:
    def __init__(self, user_id: int, username: str):
        self.user_id = user_id
        self.username = username
        self.is_ready: bool = False
        self.score: int = 0  # تعداد خونه‌هایی که گرفته

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "is_ready": self.is_ready,
            "score": self.score,
        }
