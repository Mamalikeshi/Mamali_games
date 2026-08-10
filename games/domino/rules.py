"""
Rules for Domino (Double-Six set) - 2 player mode.
Fully independent from other games (per project rule).
"""

from games.domino.tile import Tile

TILES_PER_PLAYER = 7
MATCH_TARGET_SCORE = 101


def hand_has_double(hand: list[Tile]) -> bool:
    return any(tile.is_double for tile in hand)


def find_highest_double(hands: dict[int, list[Tile]]) -> int | None:
    """
    بین دست همه‌ی بازیکنان، صاحب بالاترین دوبل (جفت) رو پیدا می‌کنه.
    خروجی: user_id همون بازیکن، یا None اگه هیچ‌کس دوبل نداشت.
    """
    best_user_id = None
    best_value = -1
    for user_id, hand in hands.items():
        for tile in hand:
            if tile.is_double and tile.left > best_value:
                best_value = tile.left
                best_user_id = user_id
    return best_user_id


def can_play_tile(tile: Tile, left_end: int | None, right_end: int | None) -> bool:
    if left_end is None and right_end is None:
        return True  # اولین مهره‌ی بازی
    return tile.has_value(left_end) or tile.has_value(right_end)


def valid_sides_for_tile(tile: Tile, left_end: int | None, right_end: int | None) -> list[str]:
    """
    مهره رو می‌شه از کدوم سمت(ها) گذاشت: 'left', 'right', یا هردو.
    """
    if left_end is None and right_end is None:
        return ["left"]

    sides = []
    if tile.has_value(left_end):
        sides.append("left")
    if tile.has_value(right_end):
        sides.append("right")
    return sides


def place_tile(
    tile: Tile,
    side: str,
    left_end: int | None,
    right_end: int | None,
) -> dict:
    """
    مهره رو از سمت مشخص‌شده روی زمین می‌ذاره و سرِ جدید اون طرف رو برمی‌گردونه.
    """
    if left_end is None and right_end is None:
        return {"new_left_end": tile.left, "new_right_end": tile.right}

    if side == "left":
        new_value = tile.other_end(left_end)
        return {"new_left_end": new_value, "new_right_end": right_end}

    if side == "right":
        new_value = tile.other_end(right_end)
        return {"new_left_end": left_end, "new_right_end": new_value}

    raise ValueError("side must be 'left' or 'right'")
