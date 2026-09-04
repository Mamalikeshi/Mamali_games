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

Those responsibilities belong to other modules.
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


# ============================================================
# Dice validation
# ============================================================


def is_valid_dice_value(dice_value: int) -> bool:
    """Return True when the dice value is between 1 and 6."""
    return DICE_MIN <= dice_value <= DICE_MAX


def validate_dice_value(dice_value: int) -> None:
    """Raise ValueError when the dice value is invalid."""
    if not is_valid_dice_value(dice_value):
        raise ValueError(
            "Dice value must be between 1 and 6."
        )


# ============================================================
# Piece state helpers
# ============================================================


def can_enter_from_yard(
    piece: Piece,
    dice_value: int,
) -> bool:
    """
    Check whether a yard piece can enter the board.

    A piece can leave the yard only when the player rolls 6.
    """

    validate_dice_value(dice_value)

    return (
        piece.is_in_yard()
        and dice_value == ENTER_ROLL
    )


def is_piece_finished(piece: Piece) -> bool:
    """Return True when the piece has reached the center."""
    return piece.is_finished()


def is_piece_on_board(piece: Piece) -> bool:
    """
    Return True when the piece is on the shared track
    or inside its home column.
    """

    return (
        piece.status in {
            "track",
            "home_column",
        }
        and not piece.is_finished()
    )


# ============================================================
# Destination calculation
# ============================================================


def calculate_destination(
    piece: Piece,
    dice_value: int,
) -> int | None:
    """
    Calculate the destination relative_step.

    Returns:
        None -> piece cannot move
        int  -> destination step

    Rules:
    - yard piece requires a 6 and enters at step 0
    - board piece advances by dice value
    - finished piece cannot move
    - destination cannot pass FINISH_STEP
    """

    validate_dice_value(dice_value)

    # Finished pieces cannot move.
    if piece.is_finished():
        return None

    # Yard -> entry.
    if piece.is_in_yard():
        if dice_value == ENTER_ROLL:
            return 0

        return None

    # Normal board movement.
    destination = (
        piece.relative_step + dice_value
    )

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
    """
    Return True when the piece has a legal move.
    """

    return calculate_destination(
        piece,
        dice_value,
    ) is not None


def movable_pieces(
    player: Player,
    dice_value: int,
) -> list[Piece]:
    """
    Return all pieces belonging to the player that can move
    with the current dice value.
    """

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
    Return the global track cell of the destination.

    Returns None when:
    - the piece enters home column
    - the piece finishes
    - the piece cannot move
    """

    destination = calculate_destination(
        piece,
        dice_value,
    )

    if destination is None:
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
    Return True when the destination is a safe position.

    Home-column and finished positions are safe by definition.
    """

    destination = calculate_destination(
        piece,
        dice_value,
    )

    if destination is None:
        return False

    global_cell = global_cell_for_step(
        piece.color,
        destination,
    )

    if global_cell is None:
        # Home column / finished.
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

    Capture is possible when:
    - attacker and victim have different colors
    - both are on the shared track
    - they occupy the same global cell
    - the destination cell is not safe
    """

    if attacker.color == victim.color:
        return False

    if not is_on_track(attacker.relative_step):
        return False

    if not is_on_track(victim.relative_step):
        return False

    attacker_cell = global_cell_for_step(
        attacker.color,
        attacker.relative_step,
    )

    victim_cell = global_cell_for_step(
        victim.color,
        victim.relative_step,
    )

    if attacker_cell is None or victim_cell is None:
        return False

    if attacker_cell != destination_global_cell:
        return False

    if victim_cell != destination_global_cell:
        return False

    if is_safe_track_cell(destination_global_cell):
        return False

    return True


def pieces_to_capture(
    attacker: Piece,
    opponents: list[Player],
    dice_value: int,
) -> list[Piece]:
    """
    Return all opponent pieces that would be captured if the
    attacker moves using the given dice value.
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
    Send a captured piece back to its yard.
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

    global_cell = global_cell_for_step(
        piece.color,
        destination,
    )

    return {
        "can_move": True,
        "piece_id": piece.piece_id,
        "from_step": piece.relative_step,
        "to_step": destination,
        "global_cell": global_cell,
        "enters_board": (
            piece.is_in_yard()
            and destination == 0
        ),
        "enters_home_column": (
            destination > 0
            and destination > 51
        ),
        "finishes": (
            destination == FINISH_STEP
        ),
        "safe": (
            True
            if global_cell is None
            else is_safe_track_cell(global_cell)
        ),
    }


# ============================================================
# Player-level helpers
# ============================================================


def player_can_move(
    player: Player,
    dice_value: int,
) -> bool:
    """
    Return True when at least one piece can move.
    """

    return bool(
        movable_pieces(
            player,
            dice_value,
        )
    )


def player_has_finished(
    player: Player,
) -> bool:
    """Return True when all four pieces are finished."""
    return player.all_finished()
