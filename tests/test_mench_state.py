import pytest

from games.mench.player import Player
from games.mench.state import MenchState


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


def test_initial_state():
    state = MenchState("test-room")

    assert state.room_id == "test-room"
    assert state.players == []
    assert state.current_player_index == 0
    assert state.current_player_id is None
    assert state.dice_value is None
    assert not state.dice_rolled
    assert not state.waiting_for_piece
    assert state.turn_number == 0
    assert state.last_move is None
    assert state.last_captured_pieces == []
    assert not state.game_finished
    assert state.winner_id is None


def test_add_player():
    state = MenchState("test-room")

    player = make_player(
        1,
        "red_player",
        "red",
    )

    state.add_player(player)

    assert len(state.players) == 1
    assert state.get_player(1) is player
    assert state.current_player_id == 1


def test_add_multiple_players():
    state = MenchState("test-room")

    red = make_player(1, "red", "red")
    blue = make_player(2, "blue", "blue")

    state.add_player(red)
    state.add_player(blue)

    assert len(state.players) == 2
    assert state.get_player(1) is red
    assert state.get_player(2) is blue


def test_duplicate_player_rejected():
    state = MenchState("test-room")

    player = make_player(
        1,
        "red",
        "red",
    )

    state.add_player(player)

    with pytest.raises(ValueError):
        state.add_player(player)


def test_get_missing_player():
    state = MenchState("test-room")

    assert state.get_player(999) is None


def test_current_player():
    state = MenchState("test-room")

    red = make_player(1, "red", "red")
    blue = make_player(2, "blue", "blue")

    state.add_player(red)
    state.add_player(blue)

    assert state.current_player() is red


def test_set_current_player():
    state = MenchState("test-room")

    red = make_player(1, "red", "red")
    blue = make_player(2, "blue", "blue")

    state.add_player(red)
    state.add_player(blue)

    state.set_current_player(2)

    assert state.current_player_id == 2
    assert state.current_player_index == 1
    assert state.current_player() is blue


def test_set_missing_current_player():
    state = MenchState("test-room")

    state.add_player(
        make_player(1, "red", "red")
    )

    with pytest.raises(ValueError):
        state.set_current_player(999)


def test_advance_turn():
    state = MenchState("test-room")

    red = make_player(1, "red", "red")
    blue = make_player(2, "blue", "blue")

    state.add_player(red)
    state.add_player(blue)

    state.advance_turn()

    assert state.current_player_id == 2
    assert state.current_player_index == 1
    assert state.turn_number == 1


def test_advance_turn_wraps():
    state = MenchState("test-room")

    red = make_player(1, "red", "red")
    blue = make_player(2, "blue", "blue")

    state.add_player(red)
    state.add_player(blue)

    state.advance_turn()
    state.advance_turn()

    assert state.current_player_id == 1
    assert state.current_player_index == 0
    assert state.turn_number == 2


def test_set_dice():
    state = MenchState("test-room")

    state.set_dice(6)

    assert state.dice_value == 6
    assert state.dice_rolled
    assert not state.waiting_for_piece


def test_invalid_dice():
    state = MenchState("test-room")

    with pytest.raises(ValueError):
        state.set_dice(0)

    with pytest.raises(ValueError):
        state.set_dice(7)


def test_require_piece_selection():
    state = MenchState("test-room")

    state.set_dice(4)
    state.require_piece_selection()

    assert state.dice_value == 4
    assert state.dice_rolled
    assert state.waiting_for_piece


def test_require_piece_selection_without_dice():
    state = MenchState("test-room")

    with pytest.raises(ValueError):
        state.require_piece_selection()


def test_reset_dice_state():
    state = MenchState("test-room")

    state.set_dice(6)
    state.require_piece_selection()

    state.reset_dice_state()

    assert state.dice_value is None
    assert not state.dice_rolled
    assert not state.waiting_for_piece


def test_advance_turn_resets_dice():
    state = MenchState("test-room")

    red = make_player(1, "red", "red")
    blue = make_player(2, "blue", "blue")

    state.add_player(red)
    state.add_player(blue)

    state.set_dice(6)
    state.require_piece_selection()

    state.advance_turn()

    assert state.current_player_id == 2
    assert state.dice_value is None
    assert not state.dice_rolled
    assert not state.waiting_for_piece


def test_last_move():
    state = MenchState("test-room")

    move = {
        "piece_id": "red-0",
        "from_step": -1,
        "to_step": 0,
    }

    state.set_last_move(move)

    assert state.last_move == move


def test_captured_pieces():
    state = MenchState("test-room")

    state.set_captured_pieces(
        ["blue-0", "blue-1"]
    )

    assert state.last_captured_pieces == [
        "blue-0",
        "blue-1",
    ]


def test_clear_move_result():
    state = MenchState("test-room")

    state.set_last_move(
        {"piece_id": "red-0"}
    )

    state.set_captured_pieces(
        ["blue-0"]
    )

    state.clear_move_result()

    assert state.last_move is None
    assert state.last_captured_pieces == []


def test_set_winner():
    state = MenchState("test-room")

    red = make_player(1, "red", "red")
    blue = make_player(2, "blue", "blue")

    state.add_player(red)
    state.add_player(blue)

    state.set_winner(1)

    assert state.game_finished
    assert state.winner_id == 1
    assert not state.waiting_for_piece


def test_invalid_winner():
    state = MenchState("test-room")

    state.add_player(
        make_player(1, "red", "red")
    )

    with pytest.raises(ValueError):
        state.set_winner(999)


def test_player_count():
    state = MenchState("test-room")

    assert state.player_count() == 0

    state.add_player(
        make_player(1, "red", "red")
    )

    assert state.player_count() == 1


def test_ready_to_start_requires_two_players():
    state = MenchState("test-room")

    red = make_player(1, "red", "red")
    red.is_ready = True

    state.add_player(red)

    assert not state.is_ready_to_start()


def test_ready_to_start_when_two_players_ready():
    state = MenchState("test-room")

    red = make_player(1, "red", "red")
    blue = make_player(2, "blue", "blue")

    red.is_ready = True
    blue.is_ready = True

    state.add_player(red)
    state.add_player(blue)

    assert state.is_ready_to_start()


def test_not_ready_when_one_player_not_ready():
    state = MenchState("test-room")

    red = make_player(1, "red", "red")
    blue = make_player(2, "blue", "blue")

    red.is_ready = True
    blue.is_ready = False

    state.add_player(red)
    state.add_player(blue)

    assert not state.is_ready_to_start()


def test_three_players_can_start():
    state = MenchState("test-room")

    for user_id, color in [
        (1, "red"),
        (2, "blue"),
        (3, "yellow"),
    ]:
        player = make_player(
            user_id,
            color,
            color,
        )
        player.is_ready = True
        state.add_player(player)

    assert state.is_ready_to_start()


def test_four_players_can_start():
    state = MenchState("test-room")

    for user_id, color in [
        (1, "red"),
        (2, "blue"),
        (3, "yellow"),
        (4, "green"),
    ]:
        player = make_player(
            user_id,
            color,
            color,
        )
        player.is_ready = True
        state.add_player(player)

    assert state.is_ready_to_start()


def test_to_dict():
    state = MenchState("test-room")

    red = make_player(1, "red", "red")
    blue = make_player(2, "blue", "blue")

    state.add_player(red)
    state.add_player(blue)

    state.set_dice(6)
    state.require_piece_selection()

    data = state.to_dict()

    assert data["room_id"] == "test-room"
    assert len(data["players"]) == 2
    assert data["current_player_id"] == 1
    assert data["dice_value"] == 6
    assert data["dice_rolled"]
    assert data["waiting_for_piece"]
    assert data["game_finished"] is False
    assert data["winner_id"] is None
