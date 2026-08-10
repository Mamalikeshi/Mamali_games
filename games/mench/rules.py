"""
Rules for Mench (Ludo) - supports 2, 3, and 4 players.
Fully independent from other games (per project rule).
"""

from games.mench.piece import Piece
from games.mench.board import (
    global_cell_for_step,
    is_home_column,
    is_finished_step,
    SAFE_TRACK_CELLS,
    TOTAL_STEPS,
)

ENTRY_ROLL = 6


def can_leave_yard(dice_value: int) -> bool:
    return dice_value == ENTRY_ROLL


def compute_new_step(piece: Piece, dice_value: int) -> int | None:
    """
    قدم جدید مهره رو بعد از حرکت با این تاس محاسبه می‌کنه.
    اگه حرکت غیرمجاز باشه (مثلاً بیش‌ازحد میره جلوتر از خونه‌ی آخر)، None برمی‌گردونه.
    """
    if piece.is_in_yard():
        if not can_leave_yard(dice_value):
            return None
        return 0  # وارد اولین خونه‌ی مسیر مشترک می‌شه

    if piece.is_finished():
        return None

    new_step = piece.relative_step + dice_value

    # برای رسیدن به خونه‌ی آخر (finished) باید عدد دقیق بیاد
    if new_step > TOTAL_STEPS - 1:
        return None

    return new_step


def find_collisions(
    mover_color: str,
    new_relative_step: int,
    all_players_pieces: dict[str, list[Piece]],
) -> dict:
    """
    بررسی می‌کنه که آیا مهره‌ای که تازه حرکت کرده، با مهره‌ی دیگه‌ای هم‌خونه شده یا نه.

    خروجی:
        {
            "burned_opponent_pieces": [...],  # مهره‌های حریف که باید بسوزن
            "burned_own_piece": Piece | None,  # اگه خودش رو مهره‌ی خودی نشسته و باید بسوزه
        }
    """
    result = {"burned_opponent_pieces": [], "burned_own_piece": None}

    if is_home_column(new_relative_step):
        # تو ستون رنگی خودشه؛ هیچ رنگ دیگه‌ای اونجا نمیاد، پس برخوردی نیست
        return result

    target_cell = global_cell_for_step(mover_color, new_relative_step)
    is_safe = target_cell in SAFE_TRACK_CELLS

    for color, pieces in all_players_pieces.items():
        for other_piece in pieces:
            if other_piece.is_in_yard() or other_piece.is_finished():
                continue
            if is_home_column(other_piece.relative_step):
                continue

            other_cell = global_cell_for_step(color, other_piece.relative_step)
            if other_cell != target_cell:
                continue

            if color == mover_color:
                # مهره‌ی خودی رو خونه‌ی مشترک: طبق قانون، مهره‌ای که روش
                # قرار می‌گیریم می‌سوزه (چه خونه امن باشه چه نباشه، چون
                # خود صاحب مهره داره روی مهره‌ی خودش می‌شینه)
                result["burned_own_piece"] = other_piece
            else:
                if not is_safe:
                    result["burned_opponent_pieces"].append(other_piece)

    return result


def apply_move(piece: Piece, new_relative_step: int):
    piece.relative_step = new_relative_step
    if is_finished_step(new_relative_step):
        piece.status = "finished"
    elif is_home_column(new_relative_step):
        piece.status = "home_column"
    else:
        piece.status = "track"


def send_to_yard(piece: Piece):
    piece.status = "yard"
    piece.relative_step = -1


def has_any_legal_move(player_pieces: list[Piece], dice_value: int) -> bool:
    for piece in player_pieces:
        if compute_new_step(piece, dice_value) is not None:
            return True
    return False
