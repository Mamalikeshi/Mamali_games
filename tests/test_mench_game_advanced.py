from games.mench.game import MenchGame
from games.mench.player import Player


def create_game(player_count=2):
    game = MenchGame("advanced-room")

    colors = ["red", "yellow", "blue", "green"]

    players = []

    for i in range(player_count):
        player = Player(
            user_id=i + 1,
            username=f"player{i + 1}",
            color=colors[i],
        )

        player.is_ready = True
        game.add_player(player)
        players.append(player)

    game.start()

    return game, players


# ============================================================
# Game start
# ============================================================

def test_game_starts_with_two_players():
    game, players = create_game(2)

    assert len(players) == 2
    assert game.current_player() == players[0]
    assert not game.is_finished()


def test_game_starts_with_three_players():
    game, players = create_game(3)

    assert len(players) == 3
    assert game.current_player() == players[0]


def test_game_starts_with_four_players():
    game, players = create_game(4)

    assert len(players) == 4
    assert game.current_player() == players[0]


# ============================================================
# Yard entry
# ============================================================

def test_six_allows_piece_to_leave_yard():
    game, players = create_game(2)

    player = players[0]
    piece = player.pieces[0]

    game.roll_dice(
        player.user_id,
        6,
    )

    result = game.move_piece(
        player.user_id,
        piece.piece_id,
    )

    assert piece.status == "track"
    assert piece.relative_step == 0
    assert result["finished"] is False


def test_non_six_does_not_allow_yard_entry():
    game, players = create_game(2)

    player = players[0]

    game.roll_dice(
        player.user_id,
        5,
    )

    assert game.get_movable_pieces(
        player.user_id,
        5,
    ) == []


# ============================================================
# Normal movement
# ============================================================

def test_piece_moves_forward_on_track():
    game, players = create_game(2)

    player = players[0]
    piece = player.pieces[0]

    piece.move_to_track(10)

    game.roll_dice(
        player.user_id,
        4,
    )

    result = game.move_piece(
        player.user_id,
        piece.piece_id,
    )

    assert piece.relative_step == 14
    assert piece.status == "track"
    assert result["new_relative_step"] == 14


# ============================================================
# Home column
# ============================================================

def test_piece_enters_home_column():
    game, players = create_game(2)

    player = players[0]
    piece = player.pieces[0]

    piece.move_to_track(50)

    game.roll_dice(
        player.user_id,
        2,
    )

    game.move_piece(
        player.user_id,
        piece.piece_id,
    )

    assert piece.relative_step == 52
    assert piece.status == "home_column"


def test_piece_moves_inside_home_column():
    game, players = create_game(2)

    player = players[0]
    piece = player.pieces[0]

    piece.move_to_home_column(52)

    game.roll_dice(
        player.user_id,
        2,
    )

    game.move_piece(
        player.user_id,
        piece.piece_id,
    )

    assert piece.relative_step == 54
    assert piece.status == "home_column"


# ============================================================
# Finish
# ============================================================

def test_piece_finishes_exactly():
    game, players = create_game(2)

    player = players[0]
    piece = player.pieces[0]

    piece.move_to_home_column(55)

    game.roll_dice(
        player.user_id,
        2,
    )

    game.move_piece(
        player.user_id,
        piece.piece_id,
    )

    assert piece.is_finished()
    assert piece.relative_step == 57


def test_piece_cannot_pass_finish():
    game, players = create_game(2)

    player = players[0]
    piece = player.pieces[0]

    piece.move_to_home_column(55)

    game.roll_dice(
        player.user_id,
        3,
    )

    assert piece not in game.get_movable_pieces(
        player.user_id,
        3,
    )


# ============================================================
# Turn handling
# ============================================================

def test_non_six_changes_turn():
    game, players = create_game(2)

    player1 = players[0]
    player2 = players[1]

    piece = player1.pieces[0]
    piece.move_to_track(10)

    game.roll_dice(
        player1.user_id,
        4,
    )

    game.move_piece(
        player1.user_id,
        piece.piece_id,
    )

    assert game.current_player() == player2


def test_six_gives_extra_turn():
    game, players = create_game(2)

    player1 = players[0]
    piece = player1.pieces[0]

    game.roll_dice(
        player1.user_id,
        6,
    )

    game.move_piece(
        player1.user_id,
        piece.piece_id,
    )

    assert game.current_player() == player1
    assert game.state.dice_rolled is False
    assert game.state.dice_value is None


# ============================================================
# Wrong turn protection
# ============================================================

def test_wrong_player_cannot_roll():
    game, players = create_game(2)

    player1 = players[0]
    player2 = players[1]

    try:
        game.roll_dice(
            player2.user_id,
            6,
        )
        assert False
    except ValueError:
        assert True


def test_wrong_player_cannot_move():
    game, players = create_game(2)

    player1 = players[0]
    player2 = players[1]

    piece = player1.pieces[0]

    game.roll_dice(
        player1.user_id,
        6,
    )

    try:
        game.move_piece(
            player2.user_id,
            piece.piece_id,
        )
        assert False
    except ValueError:
        assert True


# ============================================================
# Capture
# ============================================================

def test_piece_can_capture_opponent():
    game, players = create_game(2)

    attacker_player = players[0]
    victim_player = players[1]

    attacker = attacker_player.pieces[0]
    victim = victim_player.pieces[0]

    attacker.move_to_track(10)

    victim.move_to_track(49)

    game.roll_dice(
        attacker_player.user_id,
        4,
    )

    result = game.move_piece(
        attacker_player.user_id,
        attacker.piece_id,
    )

    assert attacker.relative_step == 14
    assert victim.is_in_yard() is False

    # Capture list must exist.
    assert isinstance(
        result["captured_pieces"],
        list,
    )


# ============================================================
# Safe cell
# ============================================================

def test_safe_cell_does_not_capture():
    game, players = create_game(2)

    attacker_player = players[0]
    victim_player = players[1]

    attacker = attacker_player.pieces[0]
    victim = victim_player.pieces[0]

    attacker.move_to_track(0)
    victim.move_to_track(0)

    game.roll_dice(
        attacker_player.user_id,
        1,
    )

    game.move_piece(
        attacker_player.user_id,
        attacker.piece_id,
    )

    assert victim.is_on_track()


# ============================================================
# Multiple pieces
# ============================================================

def test_multiple_pieces_can_move_with_six():
    game, players = create_game(2)

    player = players[0]

    game.roll_dice(
        player.user_id,
        6,
    )

    movable = game.get_movable_pieces(
        player.user_id,
        6,
    )

    assert len(movable) == 4


# ============================================================
# Serialization
# ============================================================

def test_game_serialization_contains_state():
    game, players = create_game(2)

    data = game.to_dict()

    assert isinstance(data, dict)
    assert "room_id" in data
    assert "players" in data
    assert "current_player_id" in data
    assert "dice_value" in data
