"""
Rules engine for Mench (Ludo).

This module contains only game rules.

It does NOT manage:
- turns
- rooms
- players joining
- dice rolling state
- API
- frontend
"""

from __future__ import annotations

from games.mench.board import (
    FINISH_STEP,
    global_cell_for_step,
    is_on_track,
    is_safe_track_cell,
)
from games.mench.piece import Piece
from games.mench.player import Player


# ============================================================
# Constants
# ============================================================

DICE_MIN = 1
DICE_MAX = 6

ENTER_ROLL = 6
YARD_STEP = -1

TRACK_FIRST_STEP = 0
TRACK_LAST_STEP = 51

HOME_FIRST_STEP = 52
HOME_LAST_STEP = 56


# ============================================================
# Dice validation
# ============================================================

def is_valid_dice_value(dice_value: int) -> bool:
    return (
        isinstance(dice_value, int)
        and DICE_MIN <= dice_value <= DICE_MAX
    )


def validate_dice_value(dice_value: int) -> None:
    if not is_valid_dice_value(dice_value):
        raise ValueError(
            "Dice value must be an integer between 1 and 6."
        )


# ============================================================
# Piece state helpers
# ============================================================

def can_enter_from_yard(
    piece: Piece,
    dice_value: int,
) -> bool:
    """
    A yard piece can enter only with a 6.
    """

    validate_dice_value(dice_value)

    return (
        piece.is_in_yard()
        and dice_value == ENTER_ROLL
    )


def is_piece_finished(piece: Piece) -> bool:
    return piece.is_finished()


def is_piece_on_board(piece: Piece) -> bool:
    return piece.is_on_board()


# ============================================================
# Destination calculation
# ============================================================

def calculate_destination(
    piece: Piece,
    dice_value: int,
) -> int | None:
    """
    Calculate the destination relative_step.

    Rules:
    - yard + 6 -> step 0
    - yard + anything else -> illegal
    - board piece -> current step + dice
    - finished -> cannot move
    - cannot pass FINISH_STEP
    """

    validate_dice_value(dice_value)

    # Finished piece cannot move.
    if piece.is_finished():
        return None

    # Yard -> starting cell.
    if piece.is_in_yard():
        if dice_value == ENTER_ROLL:
            return TRACK_FIRST_STEP

        return None

    # Safety check for corrupted/invalid state.
    if piece.relative_step < TRACK_FIRST_STEP:
        return None

    destination = piece.relative_step + dice_value

    # Cannot pass the center.
    if destination > FINISH_STEP:
        return None

    return destination


# ============================================================
# Movement validation
# ============================================================

def can_piece_move(
    piece: Piece,
    dice_value: int,
) -> bool:
    return (
        calculate_destination(
            piece,
            dice_value,
        )
        is not None
    )


def movable_pieces(
    player: Player,
    dice_value: int,
) -> list[Piece]:
    validate_dice_value(dice_value)

    return [
        piece
        for piece in player.pieces
        if can_piece_move(piece, dice_value)
    ]


# ============================================================
# Position helpers
# ============================================================

def destination_global_cell(
    piece: Piece,
    dice_value: int,
) -> int | None:
    """
    Return the global track cell of destination.

    Returns None for:
    - home column
    - finished
    - illegal move
    """

    destination = calculate_destination(
        piece,
        dice_value,
    )

    if destination is None:
        return None

    if not is_on_track(destination):
        return None

    return global_cell_for_step(
        piece.color,
        destination,
    )


def is_destination_safe(
    piece: Piece,
    dice_value: int,
) -> bool:
    """
    Determine whether destination is safe.

    Safe:
    - home column
    - finished
    - designated safe track cells
    """

    destination = calculate_destination(
        piece,
        dice_value,
    )

    if destination is None:
        return False

    # Home column / finish.
    if not is_on_track(destination):
        return True

    global_cell = global_cell_for_step(
        piece.color,
        destination,
    )

    if global_cell is None:
        return True

    return is_safe_track_cell(global_cell)


# ============================================================
# Capture rules
# ============================================================

def can_capture(
    attacker: Piece,
    victim: Piece,
    destination_global_cell: int,
) -> bool:
    """
    Determine whether attacker can capture victim.

    Capture requires:
    - different colors
    - both pieces on shared track
    - both occupy the same global cell
    - destination is not safe
    """

    # Same color cannot capture itself.
    if attacker.color == victim.color:
        return False

    # Attacker must be on shared track.
    if not attacker.is_on_track():
        return False

    # Victim must be on shared track.
    if not victim.is_on_track():
        return False

    # Destination must be a valid shared-track cell.
    if not 0 <= destination_global_cell < 52:
        return False

    attacker_cell = global_cell_for_step(
        attacker.color,
        attacker.relative_step,
    )

    victim_cell = global_cell_for_step(
        victim.color,
        victim.relative_step,
    )

    if attacker_cell is None:
        return False

    if victim_cell is None:
        return False

    # Attacker must actually land on this cell.
    if attacker_cell != destination_global_cell:
        return False

    # Victim must occupy the same cell.
    if victim_cell != destination_global_cell:
        return False

    # Safe cells cannot be captured.
    if is_safe_track_cell(destination_global_cell):
        return False

    return True


def pieces_to_capture(
    attacker: Piece,
    opponents: list[Player],
    dice_value: int,
) -> list[Piece]:
    """
    Return every opponent piece that would be captured
    by the attacker's move.
    """

    destination = destination_global_cell(
        attacker,
        dice_value,
    )

    if destination is None:
        return []

    if is_safe_track_cell(destination):
        return []

    captured: list[Piece] = []

    for player in opponents:
        for victim in player.pieces:
            if can_capture(
                attacker,
                victim,
                destination,
            ):
                captured.append(victim)

    return captured


# ============================================================
# Applying capture
# ============================================================

def capture_piece(piece: Piece) -> None:
    """
    Send a captured piece back to the yard.
    """

    piece.send_home()


# ============================================================
# Movement result
# ============================================================

def movement_result(
    piece: Piece,
    dice_value: int,
) -> dict:
    """
    Return a complete description of a possible movement.

    This function does not mutate the piece.
    """

    validate_dice_value(dice_value)

    destination = calculate_destination(
        piece,
        dice_value,
    )

    if destination is None:
        return {
            "can_move": False,
            "piece_id": piece.piece_id,
            "from_step": piece.relative_step,
            "to_step": None,
            "global_cell": None,
            "enters_board": False,
            "enters_home_column": False,
            "finishes": False,
            "safe": False,
        }

    global_cell = None

    if is_on_track(destination):
        global_cell = global_cell_for_step(
            piece.color,
            destination,
        )

    enters_board = (
        piece.is_in_yard()
        and destination == TRACK_FIRST_STEP
    )

    enters_home_column = (
        HOME_FIRST_STEP <= destination <= HOME_LAST_STEP
    )

    finishes = destination == FINISH_STEP

    safe = (
        True
        if global_cell is None
        else is_safe_track_cell(global_cell)
    )

    return {
        "can_move": True,
        "piece_id": piece.piece_id,
        "from_step": piece.relative_step,
        "to_step": destination,
        "global_cell": global_cell,
        "enters_board": enters_board,
        "enters_home_column": enters_home_column,
        "finishes": finishes,
        "safe": safe,
    }


# ============================================================
# Player-level helpers
# ============================================================

def player_can_move(
    player: Player,
    dice_value: int,
) -> bool:
    return bool(
        movable_pieces(
            player,
            dice_value,
        )
    )


def player_has_finished(
    player: Player,
) -> bool:
    return player.all_finished()
