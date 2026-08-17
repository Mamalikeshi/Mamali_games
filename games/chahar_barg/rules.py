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

    برخلاف نسخه قبلی، فقط اولین ترکیب را برنمی‌گرداند.
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
    برای سازگاری با کدهای قدیمی.

    اگر فقط یک ترکیب وجود داشته باشد همان را برمی‌گرداند.
    اگر چند ترکیب وجود داشته باشد اولین ترکیب را برمی‌گرداند.

    در منطق جدید بازی، برای تصمیم‌گیری واقعی باید از
    _find_number_combos استفاده شود.
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
    حالتی که کارت بازی‌شده چیزی را جمع نمی‌کند.
    """

    return {
        "captured": [],
        "is_jack_sweep": False,
        "is_sour": False,
        "remaining_table": table_cards + [played_card],

        # برای منطق انتخاب بازیکن
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
    - کارت بازی‌شده
    - کارت‌های روی زمین
    - تعداد کارت‌ها
    - باقی‌مانده زمین
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

    خروجی شامل:
    - captured
    - is_jack_sweep
    - is_sour
    - remaining_table
    - requires_selection
    - capture_options

    اگر چند ترکیب مختلف برای جمع ۱۱ وجود داشته باشد،
    سیستم هیچ ترکیبی را به صورت خودکار انتخاب نمی‌کند.
    """

    # =========================================================
    # شاه
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
    # تمام کارت‌های روی زمین به جز شاه و بی‌بی را جمع می‌کند.
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
    # باید مجموع کارت‌های روی زمین با کارت بازی‌شده برابر ۱۱ شود.
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

    # ---------------------------------------------------------
    # هیچ ترکیبی برای ۱۱ وجود ندارد.
    # ---------------------------------------------------------

    if not combos:

        return _no_capture(
            played_card,
            table_cards,
        )

    # ---------------------------------------------------------
    # فقط یک ترکیب وجود دارد.
    #
    # در این حالت نیازی به انتخاب بازیکن نیست.
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # بیش از یک ترکیب وجود دارد.
    #
    # اینجا سیستم نباید خودش انتخاب کند.
    # ---------------------------------------------------------

    options = _build_capture_options(
        played_card,
        combos,
        table_cards,
    )

    return {
        "captured": [],
        "is_jack_sweep": False,
        "is_sour": False,

        # تا انتخاب بازیکن، زمین تغییر نمی‌کند.
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
    بعد از اینکه بازیکن یکی از گزینه‌های جمع ۱۱ را انتخاب کرد،
    این تابع همان گزینه را اعمال می‌کند.

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
    10 خشت = 3
    2 گشنیز = 2
    هر سرباز = 1
    هر آس = 1
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


def has_haft_khaj(
    captured_cards: list[Card],
) -> bool:
    """
    بررسی می‌کند آیا بازیکن 7 گشنیز را در کارت‌های
    جمع‌شده دارد یا خیر.
    """

    return any(
        card.suit == "clubs"
        and card.rank == "7"
        for card in captured_cards
    )
