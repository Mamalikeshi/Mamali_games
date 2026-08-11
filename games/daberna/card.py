"""
Card (ticket) model for Daberna (Iranian 90-ball Bingo).
Fully independent from other games (per project rule).

هر کارت ۳ ردیف در ۹ ستونه. هر ردیف دقیقاً ۵ خونه‌ی پر (عدد) و ۴ خونه‌ی
خالی داره. هر ستون بازه‌ی عددی مخصوص به خودش رو داره:
ستون ۱: ۱-۹ , ستون ۲: ۱۰-۱۹ , ... , ستون ۹: ۸۰-۹۰
اعداد داخل هر ستون از بالا به پایین صعودی چیده می‌شن.
"""

import random

COLUMN_RANGES = [
    (1, 9), (10, 19), (20, 29), (30, 39), (40, 49),
    (50, 59), (60, 69), (70, 79), (80, 90),
]

ROWS = 3
COLUMNS = 9
NUMBERS_PER_CARD = 15


def _generate_column_counts() -> list[int]:
    """هر ستون بین ۱ تا ۳ عدد داره، جمعاً ۱۵ عدد."""
    counts = [1] * COLUMNS
    remaining = NUMBERS_PER_CARD - COLUMNS
    while remaining > 0:
        idx = random.randrange(COLUMNS)
        if counts[idx] < 3:
            counts[idx] += 1
            remaining -= 1
    return counts


def _generate_row_assignment(column_counts: list[int]) -> list[list[int]] | None:
    """
    برای هر ستون، مشخص می‌کنه تو کدوم ردیف(ها) عدد داره، طوری‌که هر
    ردیف دقیقاً ۵ عدد داشته باشه.
    """
    for _ in range(500):
        assignment = []
        row_sums = [0, 0, 0]
        for count in column_counts:
            rows_chosen = random.sample(range(ROWS), count)
            assignment.append(rows_chosen)
            for r in rows_chosen:
                row_sums[r] += 1
        if row_sums == [NUMBERS_PER_CARD // ROWS] * ROWS:
            return assignment
    return None


class Card:
    def __init__(self, card_id: str):
        self.card_id = card_id
        self.grid: list[list[int | None]] = [[None] * COLUMNS for _ in range(ROWS)]
        self.all_numbers: set[int] = set()
        self._generate()

    def _generate(self):
        column_counts = _generate_column_counts()
        assignment = _generate_row_assignment(column_counts)
        if assignment is None:
            # fallback خیلی نادر: از اول با کانت‌های جدید تلاش کن
            self._generate()
            return

        for col_idx, rows_chosen in enumerate(assignment):
            low, high = COLUMN_RANGES[col_idx]
            count = len(rows_chosen)
            numbers = sorted(random.sample(range(low, high + 1), count))
            for i, r in enumerate(sorted(rows_chosen)):
                self.grid[r][col_idx] = numbers[i]
                self.all_numbers.add(numbers[i])

    def missing_numbers(self, drawn_numbers: set[int]) -> list[int]:
        return sorted(self.all_numbers - drawn_numbers)

    def remaining_count(self, drawn_numbers: set[int]) -> int:
        return len(self.all_numbers - drawn_numbers)

    def is_complete(self, drawn_numbers: set[int]) -> bool:
        return self.all_numbers.issubset(drawn_numbers)

    def completion_draw_index(self, draw_order: list[int]) -> int:
        """
        بزرگ‌ترین ایندکس (تو ترتیب اعلام‌شدن اعداد) که برای کامل‌شدن این
        کارت لازمه. یعنی آخرین عددی که این کارت بهش نیاز داره، کِی اعلام
        می‌شه.
        """
        return max(draw_order.index(n) for n in self.all_numbers)

    def to_dict(self, drawn_numbers: set[int]) -> dict:
        return {
            "card_id": self.card_id,
            "grid": self.grid,
            "drawn_numbers": sorted(self.all_numbers & drawn_numbers),
            "remaining_count": self.remaining_count(drawn_numbers),
        }
