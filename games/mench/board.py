"""
Board engine for Mench (Ludo).

Supports:
- 2 players
- 3 players
- 4 players

The board uses:
- 52 shared track cells: global cells 0..51
- 6 home-column cells for each color
- relative_step 0..51 -> shared track
- relative_step 52..57 -> player's home column
- relative_step 57 -> finished / center

This module is completely independent from other games.
"""

from __future__ import annotations


# ============================================================
# Board constants
# ============================================================

TRACK_LENGTH = 52
HOME_COLUMN_LENGTH = 6

# A piece starts at relative_step 0.
# 0..51 = 52 shared track positions
# 52..57 = 6 home-column positions
# 57 = final center position
FINISH_STEP = TRACK_LENGTH + HOME_COLUMN_LENGTH - 1

TOTAL_STEPS = FINISH_STEP + 1


# ============================================================
# Colors
# ============================================================

COLOR_ORDER = [
    "red",
    "blue",
    "yellow",
    "green",
]


# ============================================================
# Player modes
# ============================================================

MODE_COLORS = {
    2: ["red", "yellow"],
    3: ["red", "blue", "yellow"],
    4: ["red", "blue", "yellow", "green"],
}


# ============================================================
# Entry cells
# ============================================================

# Each color enters the shared 52-cell track at a different cell.
#
# Clockwise order:
# red -> blue -> yellow -> green
#
# Each entry is 13 cells apart.
ENTRY_OFFSET = {
    "red": 0,
    "blue": 13,
    "yellow": 26,
    "green": 39,
}


# ============================================================
# Safe cells
# ============================================================

# The four color entry cells are safe.
#
# IMPORTANT:
# Safe cells are GLOBAL track cells.
# Therefore they remain present even when the game has only
# 2 or 3 players.
SAFE_TRACK_CELLS = frozenset(
    ENTRY_OFFSET[color]
    for color in COLOR_ORDER
)


# ============================================================
# Validation helpers
# ============================================================


def validate_color(color: str) -> None:
    """Raise ValueError if the color is not a valid Mench color."""
    if color not in COLOR_ORDER:
        raise ValueError(f"Invalid Mench color: {color}")


def validate_mode(player_count: int) -> None:
    """Raise ValueError if the player count is not supported."""
    if player_count not in MODE_COLORS:
        raise ValueError(
            "Mench supports only 2, 3, or 4 players."
        )


def colors_for_mode(player_count: int) -> list[str]:
    """Return the colors used by the requested player count."""
    validate_mode(player_count)
    return MODE_COLORS[player_count].copy()


# ============================================================
# Track conversion
# ============================================================


def global_cell_for_step(
    color: str,
    relative_step: int,
) -> int | None:
    """
    Convert a player's relative step to a global track cell.

    Returns:
        0..51 -> global shared-track cell
        None  -> piece is not on the shared track

    Examples:

        red, 0  -> 0
        red, 1  -> 1

        blue, 0 -> 13
        blue, 1 -> 14

        yellow, 0 -> 26

        green, 0 -> 39
    """

    validate_color(color)

    if not 0 <= relative_step < TRACK_LENGTH:
        return None

    return (
        ENTRY_OFFSET[color] + relative_step
    ) % TRACK_LENGTH


# ============================================================
# Position classification
# ============================================================


def is_on_track(relative_step: int) -> bool:
    """
    Return True when the piece is on the shared 52-cell track.
    """
    return 0 <= relative_step < TRACK_LENGTH


def is_home_column(relative_step: int) -> bool:
    """
    Return True when the piece is inside its 6-cell home column.

    Steps:
        52..57
    """
    return TRACK_LENGTH <= relative_step <= FINISH_STEP


def is_finished_step(relative_step: int) -> bool:
    """
    Return True when the piece has reached the center.
    """
    return relative_step == FINISH_STEP


def is_in_yard_step(relative_step: int) -> bool:
    """
    Return True when the piece is still in the yard.

    -1 represents the yard.
    """
    return relative_step == -1


# ============================================================
# Safe-cell logic
# ============================================================


def is_safe_track_cell(global_cell: int) -> bool:
    """
    Return True if a global track cell is a safe cell.
    """
    if not 0 <= global_cell < TRACK_LENGTH:
        return False

    return global_cell in SAFE_TRACK_CELLS


def is_safe_position(
    color: str,
    relative_step: int,
) -> bool:
    """
    Determine whether a piece is currently on a safe position.

    Home-column cells are inherently safe because opponents
    cannot occupy them.

    Yard is also considered safe because it is outside the
    shared board.

    On the shared track, only the four color-entry cells
    are safe.
    """

    validate_color(color)

    if is_in_yard_step(relative_step):
        return True

    if is_home_column(relative_step):
        return True

    if not is_on_track(relative_step):
        return False

    global_cell = global_cell_for_step(
        color,
        relative_step,
    )

    if global_cell is None:
        return False

    return is_safe_track_cell(global_cell)


# ============================================================
# Movement validation
# ============================================================


def is_valid_relative_step(relative_step: int) -> bool:
    """
    Return True if the relative step is a valid piece position.

    Valid positions:
        -1  -> yard
        0..57 -> board/home/finish
    """
    return -1 <= relative_step <= FINISH_STEP


def can_move_by_steps(
    current_step: int,
    dice_value: int,
) -> bool:
    """
    Check whether a piece can physically advance by the given
    dice value without passing the finish.

    This function does NOT check:
    - whether the piece is in the yard
    - whether a 6 is required for entering
    - blocking rules
    - captures
    - turn ownership

    Those belong in rules.py.
    """

    if not is_valid_relative_step(current_step):
        return False

    if not 1 <= dice_value <= 6:
        return False

    if current_step == -1:
        return False

    if is_finished_step(current_step):
        return False

    return current_step + dice_value <= FINISH_STEP


def next_relative_step(
    current_step: int,
    dice_value: int,
) -> int:
    """
    Calculate the next relative step.

    Raises ValueError if the movement is invalid.
    """

    if not can_move_by_steps(
        current_step,
        dice_value,
    ):
        raise ValueError(
            "Invalid Mench movement."
        )

    return current_step + dice_value
