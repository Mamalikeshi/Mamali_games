"""
Rules for Chahar Barg (Four Leaves / Yazdah) - 2 player mode.
Fully independent from other games (per project rule).
"""

from itertools import combinations

from games.chahar_barg.card import Card

TARGET_SUM = 11

SOUR_NORMAL_POINTS = 5
SOUR_JACK_POINTS = 10
SOUR_DISABLE_THRESHOLD = 50   # اگه امتیاز کل بازیکن >= این عدد باشه، سور حساب نمیشه
MATCH_TARGET_SCORE = 62       # امتیاز نهایی برای برنده شدن در کل بازی


def _find_number_combo(target_value: int, cards: list[Card]) -> list[Card] | None:
    numbers = [c for c in cards if c.rank not in ("J", "Q", "K")]
    for size in range(1, len(numbers) + 1):
        for combo in combinations(numbers, size):
            if sum(c.value for c in combo) == target_value:
                return list(combo)
    return None


def _remove_cards(table_cards: list[Card], to_remove: list[Card]) -> list[Card]:
    remaining = list(table_cards)
    for card in to_remove:
        remaining.remove(card)
    return remaining


def _no_capture(played_card: Card, table_cards: list[Card]) -> dict:
    return {
        "captured": [],
        "is_jack_sweep": False,
        "is_sour": False,
        "remaining_table": table_cards + [played_card],
    }


def resolve_move(played_card: Card, table_cards: list[Card]) -> dict:
    """
    یک حرکت رو پردازش می‌کنه.
    خروجی شامل: captured, is_jack_sweep, is_sour, remaining_table
    """
    # شاه: فقط با یک شاه دیگه
    if played_card.rank == "K":
        for card in table_cards:
            if card.rank == "K":
                remaining = _remove_cards(table_cards, [card])
                return {
                    "captured": [card, played_card],
                    "is_jack_sweep": False,
                    "is_sour": len(remaining) == 0,
                    "remaining_table": remaining,
                }
        return _no_capture(played_card, table_cards)

    # بی‌بی: فقط با یک بی‌بی دیگه
    if played_card.rank == "Q":
        for card in table_cards:
            if card.rank == "Q":
                remaining = _remove_cards(table_cards, [card])
                return {
                    "captured": [card, played_card],
                    "is_jack_sweep": False,
                    "is_sour": len(remaining) == 0,
                    "remaining_table": remaining,
                }
        return _no_capture(played_card, table_cards)

    # سرباز: جارو کردن همه‌چیز به‌جز شاه و بی‌بی
    if played_card.rank == "J":
        sweep_targets = [c for c in table_cards if c.rank not in ("Q", "K")]
        if sweep_targets:
            remaining = _remove_cards(table_cards, sweep_targets)
            return {
                "captured": sweep_targets + [played_card],
                "is_jack_sweep": True,
                "is_sour": len(remaining) == 0,
                "remaining_table": remaining,
            }
        return _no_capture(played_card, table_cards)

    # کارت عددی: جمع یازده
    needed = TARGET_SUM - played_card.value
    combo = _find_number_combo(needed, table_cards) if needed > 0 else None
    if combo:
        remaining = _remove_cards(table_cards, combo)
        return {
            "captured": combo + [played_card],
            "is_jack_sweep": False,
            "is_sour": len(remaining) == 0,
            "remaining_table": remaining,
        }

    return _no_capture(played_card, table_cards)


def tally_round_score(captured_cards: list[Card]) -> int:
    """
    امتیاز کارت‌های جمع‌شده در یک دور (بدون سور و بدون هفت‌خاج).
    جمع کل این امتیازات بین دو بازیکن باید ۲۰ باشه.
    """
    score = 0
    for card in captured_cards:
        if card.suit == "diamonds" and card.rank == "10":
            score += 3
        elif card.suit == "clubs" and card.rank == "2":
            score += 2
        elif card.rank == "J":
            score += 1
        elif card.rank == "A":
            score += 1
    return score


def has_haft_khaj(captured_cards: list[Card]) -> bool:
    return any(card.suit == "clubs" and card.rank == "7" for card in captured_cards)
