import pytest

from games.mench.board import (
    TRACK_LENGTH,
    HOME_COLUMN_LENGTH,
    FINISH_STEP,
    TOTAL_STEPS,
    COLOR_ORDER,
    ENTRY_OFFSET,
    SAFE_TRACK_CELLS,
    MODE_COLORS,
    global_cell_for_step,
    is_on_track,
    is_home_column,
    is_finished_step,
    is_in_yard_step,
    is_safe_track_cell,
    is_safe_position,
    is_valid_relative_step,
    can_move_by_steps,
    next_relative_step,
    colors_for_mode,
    validate_color,
    validate_mode,
)


def test_board_constants():
    assert TRACK_LENGTH == 52
    assert HOME_COLUMN_LENGTH == 6

    # 52 track cells + 6 home cells
    # final step is 57
    assert FINISH_STEP == 57
    assert TOTAL_STEPS == 58


def test_color_order():
    assert COLOR_ORDER == [
        "red",
        "blue",
        "yellow",
        "green",
    ]


def test_entry_offsets():
    assert ENTRY_OFFSET["red"] == 0
    assert ENTRY_OFFSET["blue"] == 13
    assert ENTRY_OFFSET["yellow"] == 26
    assert ENTRY_OFFSET["green"] == 39


def test_safe_cells():
    assert SAFE_TRACK_CELLS == {
        0,
        13,
        26,
        39,
    }


def test_mode_colors():
    assert colors_for_mode(2) == [
        "red",
        "yellow",
    ]

    assert colors_for_mode(3) == [
        "red",
        "blue",
        "yellow",
    ]

    assert colors_for_mode(4) == [
        "red",
        "blue",
        "yellow",
        "green",
    ]


def test_invalid_mode():
    with pytest.raises(ValueError):
        validate_mode(1)

    with pytest.raises(ValueError):
        validate_mode(5)


def test_invalid_color():
    with pytest.raises(ValueError):
        validate_color("purple")


def test_red_track_mapping():
    assert global_cell_for_step("red", 0) == 0
    assert global_cell_for_step("red", 1) == 1
    assert global_cell_for_step("red", 51) == 51


def test_blue_track_mapping():
    assert global_cell_for_step("blue", 0) == 13
    assert global_cell_for_step("blue", 1) == 14
    assert global_cell_for_step("blue", 39) == 0


def test_yellow_track_mapping():
    assert global_cell_for_step("yellow", 0) == 26
    assert global_cell_for_step("yellow", 26) == 0


def test_green_track_mapping():
    assert global_cell_for_step("green", 0) == 39
    assert global_cell_for_step("green", 13) == 0


def test_track_mapping_returns_none_outside_track():
    assert global_cell_for_step("red", -1) is None
    assert global_cell_for_step("red", 52) is None
    assert global_cell_for_step("red", 57) is None


def test_track_detection():
    assert is_on_track(0)
    assert is_on_track(51)

    assert not is_on_track(-1)
    assert not is_on_track(52)
    assert not is_on_track(57)


def test_home_column_detection():
    assert is_home_column(52)
    assert is_home_column(53)
    assert is_home_column(56)
    assert is_home_column(57)

    assert not is_home_column(51)
    assert not is_home_column(58)


def test_finished_detection():
    assert is_finished_step(57)

    assert not is_finished_step(56)
    assert not is_finished_step(52)


def test_yard_detection():
    assert is_in_yard_step(-1)

    assert not is_in_yard_step(0)
    assert not is_in_yard_step(57)


def test_safe_track_cells():
    assert is_safe_track_cell(0)
    assert is_safe_track_cell(13)
    assert is_safe_track_cell(26)
    assert is_safe_track_cell(39)

    assert not is_safe_track_cell(1)
    assert not is_safe_track_cell(12)
    assert not is_safe_track_cell(14)


def test_safe_track_cell_invalid_values():
    assert not is_safe_track_cell(-1)
    assert not is_safe_track_cell(52)
    assert not is_safe_track_cell(100)


def test_safe_position_on_entry():
    assert is_safe_position("red", 0)
    assert is_safe_position("blue", 0)
    assert is_safe_position("yellow", 0)
    assert is_safe_position("green", 0)


def test_safe_position_after_entry():
    assert not is_safe_position("red", 1)
    assert not is_safe_position("blue", 1)
    assert not is_safe_position("yellow", 1)
    assert not is_safe_position("green", 1)


def test_home_column_is_safe():
    assert is_safe_position("red", 52)
    assert is_safe_position("red", 56)
    assert is_safe_position("red", 57)


def test_yard_is_safe():
    assert is_safe_position("red", -1)


def test_valid_relative_steps():
    assert is_valid_relative_step(-1)
    assert is_valid_relative_step(0)
    assert is_valid_relative_step(51)
    assert is_valid_relative_step(52)
    assert is_valid_relative_step(57)

    assert not is_valid_relative_step(-2)
    assert not is_valid_relative_step(58)


def test_can_move_on_track():
    assert can_move_by_steps(0, 1)
    assert can_move_by_steps(10, 6)
    assert can_move_by_steps(51, 6)


def test_can_move_into_home_column():
    assert can_move_by_steps(51, 1)
    assert can_move_by_steps(51, 6)

    assert can_move_by_steps(52, 5)


def test_cannot_pass_finish():
    assert not can_move_by_steps(53, 5)
    assert not can_move_by_steps(54, 4)
    assert not can_move_by_steps(56, 2)


def test_finished_piece_cannot_move():
    assert not can_move_by_steps(57, 1)
    assert not can_move_by_steps(57, 6)


def test_yard_piece_cannot_use_normal_movement():
    assert not can_move_by_steps(-1, 1)
    assert not can_move_by_steps(-1, 6)


def test_invalid_dice_values():
    assert not can_move_by_steps(0, 0)
    assert not can_move_by_steps(0, 7)
    assert not can_move_by_steps(0, -1)


def test_next_relative_step():
    assert next_relative_step(0, 1) == 1
    assert next_relative_step(10, 6) == 16
    assert next_relative_step(51, 6) == 57


def test_next_relative_step_invalid():
    with pytest.raises(ValueError):
        next_relative_step(57, 1)

    with pytest.raises(ValueError):
        next_relative_step(53, 5)

    with pytest.raises(ValueError):
        next_relative_step(-1, 6)
