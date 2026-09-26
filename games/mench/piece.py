"""
Piece (token) model for Mench (Ludo).

هر بازیکن ۴ مهره دارد.

مراحل مهره:
- yard: بیرون از زمین
- track: روی مسیر مشترک ۵۲ خانه‌ای
- home_column: داخل ستون رنگی خودش
- finished: رسیده به مرکز
"""

from __future__ import annotations


YARD_STEP = -1


class Piece:
    def __init__(self, piece_id: str, color: str):
        self.piece_id = piece_id
        self.color = color

        # yard / track / home_column / finished
        self.status: str = "yard"

        # موقعیت نسبی مهره نسبت به نقطه ورود رنگ خودش.
        #
        # -1       = yard
        # 0..51    = مسیر مشترک ۵۲ خانه‌ای
        # 52..56   = ستون خانه
        # 57       = مرکز و پایان
        self.relative_step: int = YARD_STEP

    # ========================================================
    # State helpers
    # ========================================================

    def is_in_yard(self) -> bool:
        return self.status == "yard"

    def is_on_track(self) -> bool:
        return self.status == "track"

    def is_in_home_column(self) -> bool:
        return self.status == "home_column"

    def is_finished(self) -> bool:
        return self.status == "finished"

    def is_on_board(self) -> bool:
        return self.status in {
            "track",
            "home_column",
        }

    # ========================================================
    # State changes
    # ========================================================

    def enter_board(self) -> None:
        """
        Move the piece from yard to its starting cell.
        """

        if not self.is_in_yard():
            raise ValueError(
                "Only a piece in the yard can enter the board."
            )

        self.status = "track"
        self.relative_step = 0

    def move_to_track(self, relative_step: int) -> None:
        """
        Move the piece to a shared-track position.
        """

        if not 0 <= relative_step <= 51:
            raise ValueError(
                "Track step must be between 0 and 51."
            )

        self.status = "track"
        self.relative_step = relative_step

    def move_to_home_column(self, relative_step: int) -> None:
        """
        Move the piece into its home column.

        Valid home-column steps are 52..56.
        """

        if not 52 <= relative_step <= 56:
            raise ValueError(
                "Home-column step must be between 52 and 56."
            )

        self.status = "home_column"
        self.relative_step = relative_step

    def finish(self) -> None:
        """
        Mark the piece as finished at the center.
        """

        self.status = "finished"
        self.relative_step = 57

    def send_home(self) -> None:
        """
        Send a captured piece back to its yard.
        """

        self.status = "yard"
        self.relative_step = YARD_STEP

    # ========================================================
    # Serialization
    # ========================================================

    def to_dict(self) -> dict:
        return {
            "piece_id": self.piece_id,
            "color": self.color,
            "status": self.status,
            "relative_step": self.relative_step,
        }
