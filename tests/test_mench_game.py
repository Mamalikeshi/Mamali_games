"""
Tests for the Mench game engine.
"""

import pytest

from games.mench.game import MenchGame
from games.mench.player import Player


# ============================================================
# Helpers
# ============================================================

def create_player(
    user_id: int,
    username: str,
    color: str,
) -> Player:
    return Player(
        user_id=user_id,
        username=username,
        color=color,
    )


def create_started_game() -> MenchGame:
    game = MenchGame(room_id="test-room")

    player1 = create_player(1, "player1", "red")
    player2 = create_player(2, "player2", "yellow")

    player1.is_ready = True
    player2.is_ready = True

    game.add_player(player1)
    game.add_player(player2)

    game.start()

    return game


# ============================================================
# Initialization
# ============================================================

def test_game_initialization():
    game = MenchGame(room_id="room-1")

    assert game.room_id == "room-1"
    assert game.state.room_id == "room-1"
    assert game.state.players == []
    assert game.state.current_player_id is None
    assert game.state.game_finished is False


# ============================================================
# Player management
# ============================================================

def test_add_player():
    game = MenchGame(room_id="room-1")

    player = create_player(
        1,
        "player1",
        "red",
    )

    game.add_player(player)

    assert game.state.player_count() == 1
    assert game.get_player(1) is player
    assert game.state.current_player_id == 1


def test_duplicate_player_is_rejected():
    game = MenchGame(room_id="room-1")

    player = create_player(
        1,
        "player1",
        "red",
    )

    game.add_player(player)

    with pytest.raises(ValueError):
        game.add_player(
            create_player(
                1,
                "another",
                "yellow",
            )
        )


def test_maximum_four_players():
    game = MenchGame(room_id="room-1")

    colors = [
        "red",
        "blue",
        "yellow",
        "green",
    ]

    for user_id, color in enumerate(colors, start=1):
        game.add_player(
            create_player(
                user_id,
                f"player{user_id}",
                color,
            )
        )

    with pytest.raises(ValueError):
        game.add_player(
            create_player(
                5,
                "player5",
                "red",
            )
        )


# ============================================================
# Game start
# ============================================================

def test_game_requires_two_players():
    game = MenchGame(room_id="room-1")

    player = create_player(
        1,
        "player1",
        "red",
    )

    player.is_ready = True

    game.add_player(player)

    with pytest.raises(ValueError):
        game.start()


def test_game_requires_all_players_ready():
    game = MenchGame(room_id="room-1")

    player1 = create_player(
        1,
        "player1",
        "red",
    )

    player2 = create_player(
        2,
        "player2",
        "yellow",
    )

    player1.is_ready = True
    player2.is_ready = False

    game.add_player(player1)
    game.add_player(player2)

    with pytest.raises(ValueError):
        game.start()


def test_game_starts_with_two_ready_players():
    game = create_started_game()

    assert game.state.current_player_id == 1
    assert game.state.dice_value is None
    assert game.state.dice_rolled is False
    assert game.state.waiting_for_piece is False
    assert game.state.game_finished is False


def test_game_supports_three_players():
    game = MenchGame(room_id="room-1")

    players = [
        create_player(1, "p1", "red"),
        create_player(2, "p2", "blue"),
        create_player(3, "p3", "yellow"),
    ]

    for player in players:
        player.is_ready = True
        game.add_player(player)

    game.start()

    assert game.state.player_count() == 3
    assert game.state.current_player_id == 1


def test_game_supports_four_players():
    game = MenchGame(room_id="room-1")

    players = [
        create_player(1, "p1", "red"),
        create_player(2, "p2", "blue"),
        create_player(3, "p3", "yellow"),
        create_player(4, "p4", "green"),
    ]

    for player in players:
        player.is_ready = True
        game.add_player(player)

    game.start()

    assert game.state.player_count() == 4
    assert game.state.current_player_id == 1


# ============================================================
# Turn management
# ============================================================

def test_is_player_turn():
    game = create_started_game()

    assert game.is_player_turn(1) is True
    assert game.is_player_turn(2) is False


def test_advance_turn():
    game = create_started_game()

    game.advance_turn()

    assert game.state.current_player_id == 2


def test_turn_wraps_back_to_first_player():
    game = create_started_game()

    game.advance_turn()
    game.advance_turn()

    assert game.state.current_player_id == 1


# ============================================================
# Dice
# ============================================================

def test_roll_dice_with_fixed_value():
    game = create_started_game()

    result = game.roll_dice(
        user_id=1,
        dice_value=4,
    )

    assert result == 4
    assert game.state.dice_value == 4
    assert game.state.dice_rolled is True


def test_roll_dice_rejects_invalid_value():
    game = create_started_game()

    with pytest.raises(ValueError):
        game.roll_dice(
            user_id=1,
            dice_value=7,
        )


def test_roll_dice_rejects_zero():
    game = create_started_game()

    with pytest.raises(ValueError):
        game.roll_dice(
            user_id=1,
            dice_value=0,
        )


def test_player_cannot_roll_out_of_turn():
    game = create_started_game()

    with pytest.raises(ValueError):
        game.roll_dice(
            user_id=2,
            dice_value=4,
        )


def test_player_cannot_roll_twice():
    game = create_started_game()

    game.roll_dice(
        user_id=1,
        dice_value=4,
    )

    with pytest.raises(ValueError):
        game.roll_dice(
            user_id=1,
            dice_value=3,
        )


# ============================================================
# Yard movement
# ============================================================

def test_six_allows_piece_to_leave_yard():
    game = create_started_game()

    game.roll_dice(
        user_id=1,
        dice_value=6,
    )

    movable = game.get_movable_pieces(1)

    assert len(movable) == 4

    piece = movable[0]

    result = game.move_piece(
        user_id=1,
        piece_id=piece.piece_id,
    )

    assert piece.status == "track"
    assert piece.relative_step == 0
    assert result["old_status"] == "yard"
    assert result["new_status"] == "track"


def test_non_six_does_not_allow_yard_piece_to_leave():
    game = create_started_game()

    game.roll_dice(
        user_id=1,
        dice_value=5,
    )

    movable = game.get_movable_pieces(1)

    assert movable == []


# ============================================================
# Normal movement
# ============================================================

def test_piece_moves_on_track():
    game = create_started_game()

    player = game.get_player(1)
    piece = player.pieces[0]

    piece.status = "track"
    piece.relative_step = 0

    game.roll_dice(
        user_id=1,
        dice_value=4,
    )

    result = game.move_piece(
        user_id=1,
        piece_id=piece.piece_id,
    )

    assert piece.relative_step == 4
    assert piece.status == "track"

    assert result["dice_value"] == 4
    assert result["old_relative_step"] == 0
    assert result["new_relative_step"] == 4


def test_piece_enters_home_column():
    game = create_started_game()

    player = game.get_player(1)
    piece = player.pieces[0]

    piece.status = "track"
    piece.relative_step = 51

    game.roll_dice(
        user_id=1,
        dice_value=1,
    )

    game.move_piece(
        user_id=1,
        piece_id=piece.piece_id,
    )

    assert piece.relative_step == 52
    assert piece.status == "home_column"


def test_piece_reaches_finish():
    game = create_started_game()

    player = game.get_player(1)
    piece = player.pieces[0]

    piece.status = "home_column"
    piece.relative_step = 56

    game.roll_dice(
        user_id=1,
        dice_value=1,
    )

    result = game.move_piece(
        user_id=1,
        piece_id=piece.piece_id,
    )

    assert piece.relative_step == 57
    assert piece.status == "finished"
    assert result["finished"] is True


def test_piece_cannot_move_beyond_finish():
    game = create_started_game()

    player = game.get_player(1)
    piece = player.pieces[0]

    piece.status = "home_column"
    piece.relative_step = 56

    game.roll_dice(
        user_id=1,
        dice_value=2,
    )

    with pytest.raises(ValueError):
        game.move_piece(
            user_id=1,
            piece_id=piece.piece_id,
        )


# ============================================================
# Piece selection
# ============================================================

def test_cannot_move_piece_before_dice_roll():
    game = create_started_game()

    piece = game.get_player(1).pieces[0]

    with pytest.raises(ValueError):
        game.move_piece(
            user_id=1,
            piece_id=piece.piece_id,
        )


def test_cannot_move_another_players_piece():
    game = create_started_game()

    game.roll_dice(
        user_id=1,
        dice_value=6,
    )

    opponent_piece = game.get_player(2).pieces[0]

    with pytest.raises(ValueError):
        game.move_piece(
            user_id=1,
            piece_id=opponent_piece.piece_id,
        )


# ============================================================
# Extra turn after six
# ============================================================

def test_six_gives_extra_turn():
    game = create_started_game()

    piece = game.get_player(1).pieces[0]

    game.roll_dice(
        user_id=1,
        dice_value=6,
    )

    result = game.move_piece(
        user_id=1,
        piece_id=piece.piece_id,
    )

    assert result["extra_turn"] is True
    assert result["next_player_id"] == 1

    assert game.state.current_player_id == 1
    assert game.state.dice_rolled is False
    assert game.state.dice_value is None


def test_non_six_moves_turn_to_next_player():
    game = create_started_game()

    player = game.get_player(1)
    piece = player.pieces[0]

    piece.status = "track"
    piece.relative_step = 0

    game.roll_dice(
        user_id=1,
        dice_value=4,
    )

    result = game.move_piece(
        user_id=1,
        piece_id=piece.piece_id,
    )

    assert result["extra_turn"] is False
    assert result["next_player_id"] == 2
    assert game.state.current_player_id == 2


# ============================================================
# No legal move
# ============================================================

def test_no_legal_move_with_non_six():
    game = create_started_game()

    game.roll_dice(
        user_id=1,
        dice_value=5,
    )

    assert game.has_legal_move(1) is False

    result = game.finish_roll_without_move(
        user_id=1,
    )

    assert result["moved"] is False
    assert result["extra_turn"] is False
    assert result["next_player_id"] == 2
    assert game.state.current_player_id == 2


def test_no_legal_move_with_six_gives_extra_roll():
    game = create_started_game()

    # All pieces are deliberately made unable to move.
    # We do this by putting them at the finish.
    player = game.get_player(1)

    for piece in player.pieces:
        piece.status = "finished"
        piece.relative_step = 57

    game.roll_dice(
        user_id=1,
        dice_value=6,
    )

    assert game.has_legal_move(1) is False

    result = game.finish_roll_without_move(
        user_id=1,
    )

    assert result["moved"] is False
    assert result["extra_turn"] is True
    assert result["next_player_id"] == 1
    assert game.state.current_player_id == 1
    assert game.state.dice_rolled is False


# ============================================================
# Capturing
# ============================================================

def test_piece_can_capture_opponent():
    game = create_started_game()

    attacker = game.get_player(1).pieces[0]
    victim = game.get_player(2).pieces[0]

    attacker.status = "track"
    attacker.relative_step = 5

    victim.status = "track"
    victim.relative_step = 5

    game.roll_dice(
        user_id=1,
        dice_value=2,
    )

    # Move attacker to the same global cell as victim.
    # For this test we choose positions with matching global
    # destination after the move.
    victim.relative_step = 7

    result = game.move_piece(
        user_id=1,
        piece_id=attacker.piece_id,
    )

    assert attacker.relative_step == 7
    assert victim.status == "yard"
    assert victim.relative_step == -1
    assert victim.piece_id in result["captured_pieces"]


# ============================================================
# Player completion
# ============================================================

def test_player_finishes_when_all_pieces_finish():
    game = create_started_game()

    player = game.get_player(1)

    for piece in player.pieces[:3]:
        piece.status = "finished"
        piece.relative_step = 57

    last_piece = player.pieces[3]

    last_piece.status = "home_column"
    last_piece.relative_step = 56

    game.roll_dice(
        user_id=1,
        dice_value=1,
    )

    result = game.move_piece(
        user_id=1,
        piece_id=last_piece.piece_id,
    )

    assert result["player_finished"] is True
    assert 1 in game.state.winner_order


# ============================================================
# Game completion
# ============================================================

def test_two_player_game_finishes_when_first_player_finishes():
    game = create_started_game()

    player1 = game.get_player(1)

    for piece in player1.pieces[:3]:
        piece.status = "finished"
        piece.relative_step = 57

    last_piece = player1.pieces[3]

    last_piece.status = "home_column"
    last_piece.relative_step = 56

    game.roll_dice(
        user_id=1,
        dice_value=1,
    )

    game.move_piece(
        user_id=1,
        piece_id=last_piece.piece_id,
    )

    assert game.is_finished() is True
    assert game.winner() is player1


# ============================================================
# State serialization
# ============================================================

def test_game_to_dict():
    game = create_started_game()

    data = game.to_dict()

    assert data["room_id"] == "test-room"
    assert data["current_player_id"] == 1
    assert len(data["players"]) == 2
    assert data["game_finished"] is False
