"""
Round state for Domino - 2 player mode.
Standard Double-Six Domino.
"""

import time

from games.domino.tile import Tile


class DominoState:

    def __init__(self):

        # =====================================================
        # صفحه بازی
        # =====================================================

        self.board_tiles: list[Tile] = []

        # برای سازگاری با کدهای قدیمی
        self.board = self.board_tiles

        # =====================================================
        # دو سر باز
        # =====================================================

        self.left_end: int | None = None
        self.right_end: int | None = None

        # =====================================================
        # نوبت
        # =====================================================

        self.current_turn: int | None = None

        # زمان شروع نوبتِ فعلی (برای تایمر ۲۰ ثانیه‌ای)
        self.turn_started_at: float = time.time()

        # اگر بازیکن نه مهره‌ی قابل‌بازی دارد و نه امکان کشیدن،
        # این زمانِ شروعِ شمارش معکوسِ پاسِ خودکار (۲ ثانیه) است
        self.pending_pass_at: float | None = None

        # =====================================================
        # اطلاعات حرکت
        # =====================================================

        self.last_player: int | None = None

        # تعداد پاس‌های متوالی
        self.pass_count: int = 0

        # =====================================================
        # وضعیت پایان
        # =====================================================

        self.is_blocked: bool = False

        self.round_over: bool = False

    # =========================================================
    # تبدیل وضعیت به Dictionary
    # =========================================================

    def to_dict(self) -> dict:

        return {
            "board": [
                tile.to_dict()
                for tile in self.board_tiles
            ],

            "board_tiles": [
                tile.to_dict()
                for tile in self.board_tiles
            ],

            "left_end": self.left_end,
            "right_end": self.right_end,

            "current_turn": self.current_turn,

            "turn_started_at": self.turn_started_at,

            "pending_pass_at": self.pending_pass_at,

            "last_player": self.last_player,

            "pass_count": self.pass_count,

            "is_blocked": self.is_blocked,

            "round_over": self.round_over,
        }
