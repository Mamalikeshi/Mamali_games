"""
Board model for Noghte Khat (Dots and Boxes) - 2 player mode, 5x5 boxes.
Fully independent from other games (per project rule).

طراحی صفحه:
- ۵ در ۵ خونه => یه شبکه‌ی ۶ در ۶ نقطه.
- خط‌های افقی: بین دو نقطه‌ی هم‌ردیف و همسایه. تعداد: 6 ردیف * 5 خط = 30 خط
- خط‌های عمودی: بین دو نقطه‌ی هم‌ستون و همسایه. تعداد: 5 ردیف * 6 خط = 30 خط
- هر خونه با مختصات (row, col) از ۰ تا ۴ مشخص می‌شه و ۴ ضلع داره:
  top, bottom, left, right که هرکدوم به یه خط افقی یا عمودی مشخص اشاره می‌کنن.
"""

GRID_SIZE = 5  # تعداد خونه در هر ردیف/ستون
DOTS = GRID_SIZE + 1  # تعداد نقطه در هر ردیف/ستون


def horizontal_line_id(row: int, col: int) -> str:
    """خط افقی بین نقطه‌ی (row, col) و (row, col+1)."""
    return f"h-{row}-{col}"


def vertical_line_id(row: int, col: int) -> str:
    """خط عمودی بین نقطه‌ی (row, col) و (row+1, col)."""
    return f"v-{row}-{col}"


def all_line_ids() -> list[str]:
    lines = []
    for row in range(DOTS):
        for col in range(GRID_SIZE):
            lines.append(horizontal_line_id(row, col))
    for row in range(GRID_SIZE):
        for col in range(DOTS):
            lines.append(vertical_line_id(row, col))
    return lines


def box_sides(row: int, col: int) -> list[str]:
    """۴ ضلع خونه‌ی (row, col)."""
    return [
        horizontal_line_id(row, col),        # بالا
        horizontal_line_id(row + 1, col),    # پایین
        vertical_line_id(row, col),          # چپ
        vertical_line_id(row, col + 1),      # راست
    ]


def all_box_coords() -> list[tuple[int, int]]:
    return [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)]


def is_valid_line_id(line_id: str) -> bool:
    return line_id in all_line_ids()
