"""
Piece (token) model for Manch (Ludo) - supports 2, 3, and 4 players.
Fully independent from other games (per project rule).

هر مهره یکی از این وضعیت‌ها رو داره:
- "yard": هنوز تو خونه‌ی شروع (بیرون از زمین بازی)
- "track": روی مسیر مشترک ۵۲خونه‌ای
- "home_column": تو ستون رنگی خودش (۶ خونه‌ی آخر)
- "finished": رسیده به خونه‌ی مرکزی (تمام شده)
"""


class Piece:
    def __init__(self, piece_id: str, color: str):
        self.piece_id = piece_id  # مثلا "red-0", "red-1", ...
        self.color = color
        self.status: str = "yard"

        # relative_step: تعداد گام‌هایی که از لحظه‌ی ورود به زمین برداشته.
        # 0 تا 50 => روی مسیر مشترکه (۵۱ خونه)
        # 51 تا 56 => تو ستون خونه‌ی رنگی خودشه (۶ خونه)
        # 56 => رسیده به مرکز (finished)
        self.relative_step: int = -1

    def is_in_yard(self) -> bool:
        return self.status == "yard"

    def is_finished(self) -> bool:
        return self.status == "finished"

    def to_dict(self) -> dict:
        return {
            "piece_id": self.piece_id,
            "color": self.color,
            "status": self.status,
            "relative_step": self.relative_step,
        }
