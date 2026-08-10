"""
Tile model for Domino (Double-Six set) - 2 player mode.
Fully independent from other games (per project rule).
"""

# رنگ هر عدد برای نمایش تو فرانت‌اند
PIP_COLORS = {
    0: None,
    1: "#7ec8e3",   # آبی کم‌رنگ
    2: "#4caf50",   # سبز
    3: "#e53935",   # قرمز
    4: "#757575",   # خاکستری
    5: "#1565c0",   # آبی پررنگ
    6: "#fbc02d",   # زرد
}


class Tile:
    def __init__(self, left: int, right: int):
        if not (0 <= left <= 6) or not (0 <= right <= 6):
            raise ValueError("Domino values must be between 0 and 6")
        self.left = left
        self.right = right

    @property
    def is_double(self) -> bool:
        return self.left == self.right

    @property
    def pip_sum(self) -> int:
        return self.left + self.right

    def has_value(self, value: int) -> bool:
        return self.left == value or self.right == value

    def other_end(self, known_value: int) -> int:
        """اگه یه سر مهره رو بدونیم، سر دیگه‌ش رو برمی‌گردونه."""
        if self.left == known_value:
            return self.right
        return self.left

    def to_dict(self) -> dict:
        return {
            "left": self.left,
            "right": self.right,
            "is_double": self.is_double,
        }

    def __repr__(self) -> str:
        return f"[{self.left}|{self.right}]"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Tile):
            return False
        return (
            (self.left == other.left and self.right == other.right)
            or (self.left == other.right and self.right == other.left)
        )
