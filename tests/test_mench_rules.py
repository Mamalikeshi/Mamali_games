import pytest

from games.mench.player import Player
from games.mench.piece import Piece

from games.mench.rules import (
    DICE_MIN,
    DICE_MAX,
    ENTER_ROLL,
    is_valid_dice_value,
    validate_dice_value,
    can_enter_from_yard,
    calculate_destination,
    can_piece_move,
    movable_pieces,
    destination_global_cell,
    is_destination_safe,
    can_capture,
    pieces_to_capture,
    capture_piece,
    movement_result,
    player_can_move,
    player_has_finished,
)


# ============================================================
# Helpers
# ============================================================


def make_player(
    user_id: int,
    username: str,
    color: str,
) -> Player:
    return Player(
        user_id=user_id,
        username=username,
        color=color,
    )


# ============================================================
# Dice
# ============================================================


def test_valid_dice_values():
    assert is_valid_dice_value(1)
    assert is_valid_dice_value(2)
    assert is_valid_dice_value(3)
    assert is_valid_dice_value(4)
    assert is_valid_dice_value(5)
    assert is_valid_dice_value(6)


def test_invalid_dice_values():
    assert not is_valid_dice_value(0)
    assert not is_valid_dice_value(7)
    assert not is_valid_dice_value(-1)


def test_validate_dice_value():
    for value in range(1, 7):
        validate_dice_value(value)


def test_validate_dice_value_raises():
    with pytest.raises(ValueError):
        validate_dice_value(0)

    with pytest.raises(ValueError):
        validate_dice_value(7)


# ============================================================
# Yard / entering board
# ============================================================


def test_yard_piece_enters_with_six():
    piece = Piece("red-0", "red")

    assert can_enter_from_yard(
        piece,
        ENTER_ROLL,
    )

    assert calculate_destination(
        piece,
        6,
    ) == 0


def test_yard_piece_cannot_enter_without_six():
    piece = Piece("red-0", "red")

    for dice in range(1, 6):
        assert not can_enter_from_yard(
            piece,
            dice,
        )

        assert calculate_destination(
            piece,
            dice,
        ) is None


def test_yard_piece_can_move_with_six():
    piece = Piece("red-0", "red")

    assert can_piece_move(
        piece,
        6,
    )


def test_yard_piece_cannot_move_without_six():
    piece = Piece("red-0", "red")

    assert not can_piece_move(
        piece,
        5,
    )


# ============================================================
# Normal movement
# ============================================================


def test_piece_moves_on_track():
    piece = Piece("red-0", "red")

    piece.relative_step = 10
    piece.status = "track"

    assert calculate_destination(
        piece,
        4,
    ) == 14


def test_piece_moves_six_steps():
    piece = Piece("red-0", "red")

    piece.relative_step = 10
    piece.status = "track"

    assert calculate_destination(
        piece,
        6,
    ) == 16


def test_piece_can_move_on_track():
    piece = Piece("red-0", "red")

    piece.relative_step = 10
    piece.status = "track"

    assert can_piece_move(
        piece,
        1,
    )


def test_finished_piece_cannot_move():
    piece = Piece("red-0", "red")

    piece.relative_step = 57
    piece.status = "finished"

    assert not can_piece_move(
        piece,
        1,
    )

    assert not can_piece_move(
        piece,
        6,
    )


# ============================================================
# Exact finish
# ============================================================


def test_piece_can_finish_with_exact_roll():
    piece = Piece("red-0", "red")

    piece.relative_step = 51
    piece.status = "track"

    assert calculate_destination(
        piece,
        6,
    ) == 57


def test_piece_cannot_pass_finish():
    piece = Piece("red-0", "red")

    piece.relative_step = 52
    piece.status = "home_column"

    assert calculate_destination(
        piece,
        6,
    ) is None


def test_piece_near_finish_needs_exact_value():
    piece = Piece("red-0", "red")

    piece.relative_step = 54
    piece.status = "home_column"

    assert calculate_destination(
        piece,
        3,
    ) == 57

    assert calculate_destination(
        piece,
        4,
    ) is None


# ============================================================
# Movable pieces
# ============================================================


def test_movable_pieces_with_six():
    player = make_player(
        1,
        "red_player",
        "red",
    )

    pieces = movable_pieces(
        player,
        6,
    )

    assert len(pieces) == 4


def test_movable_pieces_without_six():
    player = make_player(
        1,
        "red_player",
        "red",
    )

    pieces = movable_pieces(
        player,
        5,
    )

    assert len(pieces) == 0


def test_movable_pieces_mixed_state():
    player = make_player(
        1,
        "red_player",
        "red",
    )

    player.pieces[0].relative_step = 10
    player.pieces[0].status = "track"

    player.pieces[1].relative_step = 20
    player.pieces[1].status = "track"

    player.pieces[2].relative_step = 57
    player.pieces[2].status = "finished"

    player.pieces[3].relative_step = -1
    player.pieces[3].status = "yard"

    movable = movable_pieces(
        player,
        3,
    )

    assert len(movable) == 2


# ============================================================
# Global destination
# ============================================================


def test_red_destination_global_cell():
    piece = Piece("red-0", "red")

    piece.relative_step = 10
    piece.status = "track"

    assert destination_global_cell(
        piece,
        3,
    ) == 13


def test_blue_destination_global_cell():
    piece = Piece("blue-0", "blue")

    piece.relative_step = 10
    piece.status = "track"

    assert destination_global_cell(
        piece,
        3,
    ) == 26


def test_home_column_has_no_global_track_cell():
    piece = Piece("red-0", "red")

    piece.relative_step = 52
    piece.status = "home_column"

    assert destination_global_cell(
        piece,
        1,
    ) is None


# ============================================================
# Safe destinations
# ============================================================


def test_red_entry_is_safe():
    piece = Piece("red-0", "red")

    piece.relative_step = 50
    piece.status = "track"

    # 50 + 2 = 52, which is home column.
    assert is_destination_safe(
        piece,
        2,
    )


def test_home_column_destination_is_safe():
    piece = Piece("red-0", "red")

    piece.relative_step = 52
    piece.status = "home_column"

    assert is_destination_safe(
        piece,
        1,
    )


# ============================================================
# Capture
# ============================================================


def test_capture_opponent_on_same_non_safe_cell():
    attacker = Piece(
        "red-0",
        "red",
    )

    victim = Piece(
        "blue-0",
        "blue",
    )

    attacker.relative_step = 5
    attacker.status = "track"

    victim.relative_step = 44
    victim.status = "track"

    # Red step 5 -> global 5
    # Blue step 44 -> global 5
    destination = 5

    assert can_capture(
        attacker,
        victim,
        destination,
    )


def test_cannot_capture_on_safe_cell():
    attacker = Piece(
        "red-0",
        "red",
    )

    victim = Piece(
        "blue-0",
        "blue",
    )

    attacker.relative_step = 12
    attacker.status = "track"

    victim.relative_step = 1
    victim.status = "track"

    # Red 12 -> global 12
    # Blue 51 -> would be global 12
    #
    # We explicitly test safe cell 13 instead.
    destination = 13

    assert not can_capture(
        attacker,
        victim,
        destination,
    )


def test_cannot_capture_same_color():
    attacker = Piece(
        "red-0",
        "red",
    )

    victim = Piece(
        "red-1",
        "red",
    )

    attacker.relative_step = 5
    attacker.status = "track"

    victim.relative_step = 5
    victim.status = "track"

    assert not can_capture(
        attacker,
        victim,
        5,
    )


def test_capture_piece_sends_piece_home():
    piece = Piece(
        "blue-0",
        "blue",
    )

    piece.relative_step = 20
    piece.status = "track"

    capture_piece(piece)

    assert piece.relative_step == -1
    assert piece.status == "yard"


# ============================================================
# Pieces to capture
# ============================================================


def test_pieces_to_capture():
    attacker_player = make_player(
        1,
        "red_player",
        "red",
    )

    opponent_player = make_player(
        2,
        "blue_player",
        "blue",
    )

    attacker = attacker_player.pieces[0]

    attacker.relative_step = 5
    attacker.status = "track"

    victim = opponent_player.pieces[0]

    victim.relative_step = 44
    victim.status = "track"

    captured = pieces_to_capture(
        attacker,
        [opponent_player],
        1,
    )

    assert victim in captured


def test_no_capture_on_safe_cell():
    attacker_player = make_player(
        1,
        "red_player",
        "red",
    )

    opponent_player = make_player(
        2,
        "blue_player",
        "blue",
    )

    attacker = attacker_player.pieces[0]

    attacker.relative_step = 12
    attacker.status = "track"

    victim = opponent_player.pieces[0]

    victim.relative_step = 0
    victim.status = "track"

    captured = pieces_to_capture(
        attacker,
        [opponent_player],
        1,
    )

    assert captured == []


# ============================================================
# Movement result
# ============================================================


def test_movement_result_from_yard_with_six():
    piece = Piece(
        "red-0",
        "red",
    )

    result = movement_result(
        piece,
        6,
    )

    assert result["can_move"]
    assert result["from_step"] == -1
    assert result["to_step"] == 0
    assert result["enters_board"]


def test_movement_result_invalid_yard_move():
    piece = Piece(
        "red-0",
        "red",
    )

    result = movement_result(
        piece,
        5,
    )

    assert not result["can_move"]
    assert result["to_step"] is None


def test_movement_result_normal_move():
    piece = Piece(
        "red-0",
        "red",
    )

    piece.relative_step = 10
    piece.status = "track"

    result = movement_result(
        piece,
        4,
    )

    assert result["can_move"]
    assert result["from_step"] == 10
    assert result["to_step"] == 14
    assert result["global_cell"] == 14


def test_movement_result_finish():
    piece = Piece(
        "red-0",
        "red",
    )

    piece.relative_step = 51
    piece.status = "track"

    result = movement_result(
        piece,
        6,
    )

    assert result["can_move"]
    assert result["to_step"] == 57
    assert result["finishes"]


# ============================================================
# Player helpers
# ============================================================


def test_player_can_move():
    player = make_player(
        1,
        "red_player",
        "red",
    )

    player.pieces[0].relative_step = 10
    player.pieces[0].status = "track"

    assert player_can_move(
        player,
        3,
    )


def test_player_cannot_move():
    player = make_player(
        1,
        "red_player",
        "red",
    )

    assert not player_can_move(
        player,
        3,
    )


def test_player_has_finished():
    player = make_player(
        1,
        "red_player",
        "red",
    )

    for piece in player.pieces:
        piece.relative_step = 57
        piece.status = "finished"

    assert player_has_finished(player)


def test_player_has_not_finished():
    player = make_player(
        1,
        "red_player",
        "red",
    )

    assert not player_has_finished(player)
