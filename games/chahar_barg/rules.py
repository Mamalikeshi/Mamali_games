"""
Rules for Chahar Barg (Four Leaves / Yazdah) - 2 player mode.
Fully independent from other games (per project rule).

منطق بازی:
- هر بازیکن ۴ کارت دستشه.
- روی زمین چند کارت باز چیده شده.
- بازیکن یه کارت از دستش بازی می‌کنه:
    - اگه رنکش با یکی از کارت‌های زمین یکی بود، اون کارت(ها) رو جمع می‌کنه (سور جزئی).
    - اگه با هیچ کارت زمین جفت نشد، کارت خودش هم میره رو زمین.
- سرباز (J) کل زمین رو جارو می‌کنه (همه‌ی کارت‌های زمین رو با خودش جمع می‌کنه).
- اگه بازیکنی با کارتش کل زمین رو خالی کنه (نه با سرباز)، بهش "سور" میگن و
  ۵ امتیاز اضافه جایزه می‌گیره.
- هفت خاج (7 clubs) در پایان دور به صاحبش ۷ امتیاز میده و طرف مقابل هیچی نمی‌گیره.
"""

from games.chahar_barg.card import Card

SOUR_BONUS = 5
HAFT_KHAJ_BONUS = 7


def find_matches(played_card: Card, table_cards: list[Card]) -> list[Card]:
    """کارت‌های روی زمین که با کارت بازی‌شده جفت میشن رو برمی‌گردونه."""
    return [card for card in table_cards if card.matches(played_card)]


def resolve_move(played_card: Card, table_cards: list[Card]) -> dict:
    """
    یک حرکت رو پردازش می‌کنه و نتیجه رو برمی‌گردونه.

    خروجی:
        {
            "captured": [...],   # کارت‌هایی که جمع شدن (شامل خود کارت بازیکن)
            "is_jack_sweep": bool,
            "is_sour": bool,     # اگه زمین کاملاً خالی شد
            "remaining_table": [...]  # کارت‌های باقی‌مونده روی زمین
        }
    """
    # سرباز: کل زمین رو جارو می‌کنه
    if played_card.is_jack() and len(table_cards) > 0:
        return {
            "captured": table_cards + [played_card],
            "is_jack_sweep": True,
            "is_sour": True,
            "remaining_table": [],
        }

    matches = find_matches(played_card, table_cards)

    if not matches:
        # جفت نشد، کارت میره رو زمین
        new_table = table_cards + [played_card]
        return {
            "captured": [],
            "is_jack_sweep": False,
            "is_sour": False,
            "remaining_table": new_table,
        }

    # جفت شد، کارت‌های جفت‌شده به‌علاوه کارت خودش جمع میشه
    remaining = [card for card in table_cards if card not in matches]
    is_sour = len(remaining) == 0

    return {
        "captured": matches + [played_card],
        "is_jack_sweep": False,
        "is_sour": is_sour,
        "remaining_table": remaining,
    }


def calculate_final_scores(
    player_a_captured: list[Card],
    player_b_captured: list[Card],
    player_a_sour_count: int,
    player_b_sour_count: int,
) -> dict:
    """
    بعد از تموم شدن کارت‌های دست بازیکن‌ها (پایان دور)، امتیاز نهایی حساب می‌شه.
    """
    score_a = 0
    score_b = 0

    # تعداد کل کارت‌های جمع‌شده (هر کی بیشتر جمع کرده باشه امتیاز می‌گیره)
    if len(player_a_captured) > len(player_b_captured):
        score_a += 1
    elif len(player_b_captured) > len(player_a_captured):
        score_b += 1

    # هفت خاج
    haft_khaj = Card("clubs", "7")
    if haft_khaj in player_a_captured:
        score_a += HAFT_KHAJ_BONUS
    elif haft_khaj in player_b_captured:
        score_b += HAFT_KHAJ_BONUS

    # جایزه سور
    score_a += player_a_sour_count * SOUR_BONUS
    score_b += player_b_sour_count * SOUR_BONUS

    return {
        "player_a_score": score_a,
        "player_b_score": score_b,
    }
