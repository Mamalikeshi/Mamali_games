"""
Rules for Chahar Barg (Four Leaves / Yazdah) - 2 player mode.
Fully independent from other games (per project rule).
"""

from itertools import combinations

from games.chahar_barg.card import Card


TARGET_SUM = 11

SOUR_NORMAL_POINTS = 5
SOUR_JACK_POINTS = 10

SOUR_DISABLE_THRESHOLD = 50
MATCH_TARGET_SCORE = 62


def _find_number_combos(
    target_value: int,
    cards: list[Card],
) -> list[list[Card]]:
    """
    تمام ترکیب‌های ممکن از کارت‌های عددی را پیدا می‌کند
    که مجموع ارزش آن‌ها برابر target_value باشد.

    اگر چند ترکیب مختلف برای جمع ۱۱ وجود داشته باشد،
    همه‌ی ترکیب‌ها برگردانده می‌شوند تا بازیکن خودش
    انتخاب کند کدام کارت‌ها را بردارد.
    """

    numbers = [
        card
        for card in cards
        if card.rank not in ("J", "Q", "K")
    ]

    combos: list[list[Card]] = []

    for size in range(1, len(numbers) + 1):
        for combo in combinations(numbers, size):

            if sum(card.value for card in combo) == target_value:
                combos.append(list(combo))

    return combos


def _find_number_combo(
    target_value: int,
    cards: list[Card],
) -> list[Card] | None:
    """
    سازگاری با کدهای قدیمی.

    اگر ترکیبی وجود داشته باشد، اولین ترکیب را برمی‌گرداند.

    در منطق جدید بازی، وقتی چند ترکیب وجود داشته باشد،
    resolve_move از _find_number_combos استفاده می‌کند
    و انتخاب را به بازیکن می‌سپارد.
    """

    combos = _find_number_combos(
        target_value,
        cards,
    )

    if not combos:
        return None

    return combos[0]


def _remove_cards(
    table_cards: list[Card],
    to_remove: list[Card],
) -> list[Card]:
    """
    کارت‌های انتخاب‌شده را از روی زمین حذف می‌کند.
    """

    remaining = list(table_cards)

    for card in to_remove:
        remaining.remove(card)

    return remaining


def _no_capture(
    played_card: Card,
    table_cards: list[Card],
) -> dict:
    """
    حالتی که کارت بازی‌شده هیچ کارتی را جمع نمی‌کند.
    """

    return {
        "captured": [],
        "is_jack_sweep": False,
        "is_sour": False,
        "remaining_table": table_cards + [played_card],
        "requires_selection": False,
        "capture_options": [],
    }


def _build_capture_options(
    played_card: Card,
    combos: list[list[Card]],
    table_cards: list[Card],
) -> list[dict]:
    """
    گزینه‌های قابل انتخاب برای بازیکن را می‌سازد.

    هر گزینه شامل:
    - شماره گزینه
    - کارت بازی‌شده
    - کارت‌های انتخاب‌شده از روی زمین
    - کارت‌های جمع‌شده
    - زمین باقی‌مانده
    - وضعیت سور
    """

    options = []

    for index, combo in enumerate(combos):

        remaining = _remove_cards(
            table_cards,
            combo,
        )

        captured = combo + [played_card]

        options.append(
            {
                "option_id": index,
                "table_cards": combo,
                "played_card": played_card,
                "captured": captured,
                "remaining_table": remaining,
                "is_sour": len(remaining) == 0,
                "is_jack_sweep": False,
            }
        )

    return options


def resolve_move(
    played_card: Card,
    table_cards: list[Card],
) -> dict:
    """
    یک حرکت را پردازش می‌کند.

    اگر چند ترکیب مختلف برای جمع ۱۱ وجود داشته باشد،
    سیستم هیچ‌کدام را به صورت خودکار انتخاب نمی‌کند.

    در این حالت:
        requires_selection = True

    و گزینه‌های ممکن در:
        capture_options

    قرار می‌گیرند.
    """

    # =========================================================
    # شاه
    #
    # فقط با یک شاه دیگر جمع می‌شود.
    # =========================================================

    if played_card.rank == "K":

        for card in table_cards:

            if card.rank == "K":

                remaining = _remove_cards(
                    table_cards,
                    [card],
                )

                return {
                    "captured": [
                        card,
                        played_card,
                    ],
                    "is_jack_sweep": False,
                    "is_sour": len(remaining) == 0,
                    "remaining_table": remaining,
                    "requires_selection": False,
                    "capture_options": [],
                }

        return _no_capture(
            played_card,
            table_cards,
        )

    # =========================================================
    # بی‌بی
    #
    # فقط با یک بی‌بی دیگر جمع می‌شود.
    # =========================================================

    if played_card.rank == "Q":

        for card in table_cards:

            if card.rank == "Q":

                remaining = _remove_cards(
                    table_cards,
                    [card],
                )

                return {
                    "captured": [
                        card,
                        played_card,
                    ],
                    "is_jack_sweep": False,
                    "is_sour": len(remaining) == 0,
                    "remaining_table": remaining,
                    "requires_selection": False,
                    "capture_options": [],
                }

        return _no_capture(
            played_card,
            table_cards,
        )

    # =========================================================
    # سرباز
    #
    # تمام کارت‌های روی زمین به جز شاه و بی‌بی
    # را جمع می‌کند.
    # =========================================================

    if played_card.rank == "J":

        sweep_targets = [
            card
            for card in table_cards
            if card.rank not in ("Q", "K")
        ]

        if sweep_targets:

            remaining = _remove_cards(
                table_cards,
                sweep_targets,
            )

            return {
                "captured": sweep_targets + [played_card],
                "is_jack_sweep": True,
                "is_sour": len(remaining) == 0,
                "remaining_table": remaining,
                "requires_selection": False,
                "capture_options": [],
            }

        return _no_capture(
            played_card,
            table_cards,
        )

    # =========================================================
    # کارت عددی
    #
    # باید مجموع ارزش کارت‌های انتخاب‌شده روی زمین
    # به همراه کارت بازی‌شده برابر ۱۱ شود.
    # =========================================================

    needed = TARGET_SUM - played_card.value

    if needed <= 0:

        return _no_capture(
            played_card,
            table_cards,
        )

    combos = _find_number_combos(
        needed,
        table_cards,
    )

    # =========================================================
    # هیچ ترکیبی برای ۱۱ وجود ندارد.
    # =========================================================

    if not combos:

        return _no_capture(
            played_card,
            table_cards,
        )

    # =========================================================
    # فقط یک ترکیب وجود دارد.
    #
    # سیستم می‌تواند خودش همان ترکیب را بردارد.
    # =========================================================

    if len(combos) == 1:

        combo = combos[0]

        remaining = _remove_cards(
            table_cards,
            combo,
        )

        return {
            "captured": combo + [played_card],
            "is_jack_sweep": False,
            "is_sour": len(remaining) == 0,
            "remaining_table": remaining,
            "requires_selection": False,
            "capture_options": [],
        }

    # =========================================================
    # بیش از یک ترکیب برای ۱۱ وجود دارد.
    #
    # سیستم نباید خودش انتخاب کند.
    #
    # بازیکن باید انتخاب کند کدام ترکیب را می‌خواهد.
    # =========================================================

    options = _build_capture_options(
        played_card,
        combos,
        table_cards,
    )

    return {
        "captured": [],
        "is_jack_sweep": False,
        "is_sour": False,
        "remaining_table": list(table_cards),
        "requires_selection": True,
        "capture_options": options,
    }


def apply_capture_option(
    played_card: Card,
    table_cards: list[Card],
    option_id: int,
) -> dict | None:
    """
    بعد از انتخاب بازیکن، ترکیب انتخاب‌شده را اعمال می‌کند.

    اگر option_id نامعتبر باشد None برمی‌گرداند.
    """

    needed = TARGET_SUM - played_card.value

    if needed <= 0:
        return None

    combos = _find_number_combos(
        needed,
        table_cards,
    )

    if option_id < 0 or option_id >= len(combos):
        return None

    combo = combos[option_id]

    remaining = _remove_cards(
        table_cards,
        combo,
    )

    return {
        "captured": combo + [played_card],
        "is_jack_sweep": False,
        "is_sour": len(remaining) == 0,
        "remaining_table": remaining,
        "requires_selection": False,
        "capture_options": [],
    }


def tally_round_score(
    captured_cards: list[Card],
) -> int:
    """
    امتیاز کارت‌های جمع‌شده در یک دور.

    سور و هفت‌خاج در این تابع محاسبه نمی‌شوند.

    امتیازها:

    10 خشت = 3 امتیاز
    2 گشنیز = 2 امتیاز
    هر سرباز = 1 امتیاز
    هر آس = 1 امتیاز
    """

    score = 0

    for card in captured_cards:

        if (
            card.suit == "diamonds"
            and card.rank == "10"
        ):
            score += 3

        elif (
            card.suit == "clubs"
            and card.rank == "2"
        ):
            score += 2

        elif card.rank == "J":
            score += 1

        elif card.rank == "A":
            score += 1

    return score


def count_clubs(
    captured_cards: list[Card],
) -> int:
    """
    تعداد کارت‌های گشنیز جمع‌شده توسط بازیکن را
    محاسبه می‌کند.

    در کل دسته ۱۳ کارت گشنیز وجود دارد.

    هفت‌خاج بر اساس مقایسه تعداد گشنیزهای
    دو بازیکن در پایان دور محاسبه می‌شود.

    خود کارت ۷ گشنیز هیچ امتیاز ویژه‌ای ندارد.
    """

    return sum(
        1
        for card in captured_cards
        if card.suit == "clubs"
    )
