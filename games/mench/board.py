"""
Board layout for Mench (Ludo) - supports 2, 3, and 4 players.
Fully independent from other games (per project rule).

طراحی صفحه:
- مسیر مشترک دور صفحه شامل ۵۲ خونه‌ست (relative_step های 0 تا 50، یعنی ۵۱ قدم
  رو مسیر مشترک، قبل از ورود به ستون خونه‌ی رنگی خودش).
- هر رنگ یه نقطه‌ی ورود (entry) روی این مسیر مشترک داره.
- بعد از ۵۱ قدم، مهره وارد ستون رنگی خودش می‌شه (۶ خونه، relative_step
  های 51 تا 56). خونه‌ی 56 یعنی مهره کامل رسیده (finished).
- ترتیب رنگ‌ها دور صفحه (در جهت عقربه‌های ساعت): قرمز، آبی، زرد، سبز.
- خونه‌های امن: فقط همون ۴ خونه‌ی رنگی شروع (entry) هر بازیکن. هیچ مهره‌ای
  اونجا سوزونده نمی‌شه مگراینکه صاحب همون رنگ، خودش تاسی بیاره و روی
  مهره‌ی خودش بشینه.
"""

TRACK_LENGTH = 52
HOME_COLUMN_LENGTH = 6
TOTAL_STEPS = TRACK_LENGTH - 1 + HOME_COLUMN_LENGTH  # 0..56 => 57 خونه

COLOR_ORDER = ["red", "blue", "yellow", "green"]

# نقطه‌ی ورود هر رنگ به مسیر مشترک (۵۲ خونه، هر رنگ ۱۳تا فاصله از قبلی)
ENTRY_OFFSET = {
    "red": 0,
    "blue": 13,
    "yellow": 26,
    "green": 39,
}

# خونه‌های امن روی مسیر مشترک: همون خونه‌های ورود چهار رنگ (همیشه ثابته،
# حتی تو بازی دو یا سه‌نفره هم این ۴ تا خونه رو صفحه هستن و امنن)
SAFE_TRACK_CELLS = set(ENTRY_OFFSET.values())

# حالت‌های مختلف بازی و اینکه کدوم رنگ‌ها توشون بازی می‌کنن
MODE_COLORS = {
    2: ["red", "yellow"],       # روبه‌روی هم
    3: ["red", "blue", "yellow"],
    4: ["red", "blue", "yellow", "green"],
}


def global_cell_for_step(color: str, relative_step: int) -> int | None:
    """
    relative_step (0 تا 50) رو به خونه‌ی مطلق روی مسیر مشترک (0 تا 51) تبدیل می‌کنه.
    برای relative_step >= 51 (یعنی تو ستون خونه‌ست)، None برمی‌گردونه چون
    دیگه رو مسیر مشترک نیست.
    """
    if relative_step < 0 or relative_step > 50:
        return None
    return (ENTRY_OFFSET[color] + relative_step) % TRACK_LENGTH


def is_home_column(relative_step: int) -> bool:
    return 51 <= relative_step <= 56


def is_finished_step(relative_step: int) -> bool:
    return relative_step == 56
