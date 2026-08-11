"""
Round state for Noghte Khat (Dots and Boxes) - 2 player mode.
Fully independent from other games (per project rule).
"""

from games.noghte_khat.board import all_line_ids, all_box_coords


class NoghteKhatState:
    def __init__(self):
        # کدوم خط‌ها کشیده شدن و توسط کدوم user_id
        self.drawn_lines: dict[str, int] = {}

        # هر خونه که گرفته شده، مال کدوم user_id هست
        self.owned_boxes: dict[str, int] = {}  # key: "row-col"

        self.current_turn: int | None = None
        self.game_over: bool = False
        self.winner_user_id: int | None = None  # None هم یعنی مساوی/بدون‌برنده

    def remaining_lines(self) -> list[str]:
        return [line for line in all_line_ids() if line not in self.drawn_lines]

    def total_boxes(self) -> int:
        return len(all_box_coords())

    def to_dict(self) -> dict:
        return {
            "drawn_lines": self.drawn_lines,
            "owned_boxes": self.owned_boxes,
            "current_turn": self.current_turn,
            "game_over": self.game_over,
            "winner_user_id": self.winner_user_id,
            "total_boxes": self.total_boxes(),
        }
