"""
Tests for the main Domino game engine - 2 player mode.
"""

from games.domino.game import DominoGame
from games.domino.player import Player
from games.domino.room import Room
from games.domino.tile import Tile


def make_tile(left: int, right: int) -> Tile:
    """
    ساخت مهره دومینو.
    """
    return Tile(left, right)


def make_game() -> DominoGame:
    """
    ساخت یک بازی دومینوی دو نفره.
    """

    player_a = Player(user_id=1)
    player_b = Player(user_id=2)

    room = Room(room_id="domino-test-room")

    room.add_player(player_a)
    room.add_player(player_b)

    game = DominoGame(room)

    assert game.start_game() is True

    return game


# =========================================================
# شروع بازی
# =========================================================


def test_game_starts_with_two_players():

    game = make_game()

    assert game.state is not None

    assert len(game.player_a.hand) == 7

    assert len(game.player_b.hand) == 7

    assert game.deck is not None

    assert game.deck.remaining() == 14

    assert game.state.current_turn in (
        game.player_a.user_id,
        game.player_b.user_id,
    )


# =========================================================
# فقط دو بازیکن
# =========================================================


def test_game_requires_two_players():

    player_a = Player(user_id=1)

    room = Room(room_id="domino-one-player")

    room.add_player(player_a)

    try:
        DominoGame(room)
        assert False
    except ValueError:
        assert True


# =========================================================
# پیدا کردن بازیکن
# =========================================================


def test_get_player():

    game = make_game()

    assert game.get_player(1) is game.player_a

    assert game.get_player(2) is game.player_b

    assert game.get_player(999) is None


# =========================================================
# بزرگ‌ترین Double
# =========================================================


def test_highest_double():

    game = make_game()

    game.player_a.hand = [
        make_tile(2, 2),
        make_tile(6, 6),
        make_tile(4, 5),
    ]

    assert game._highest_double(
        game.player_a.hand
    ) == 6


def test_highest_double_returns_none_when_missing():

    game = make_game()

    game.player_a.hand = [
        make_tile(2, 3),
        make_tile(4, 5),
        make_tile(1, 6),
    ]

    assert game._highest_double(
        game.player_a.hand
    ) is None


# =========================================================
# تشخیص مهره قابل بازی
# =========================================================


def test_can_play_tile_on_empty_board():

    game = make_game()

    game.state.board_tiles = []

    assert game.can_play_tile(
        make_tile(3, 5)
    ) is True


def test_can_play_tile_matches_left_end():

    game = make_game()

    game.state.board_tiles = [
        make_tile(3, 5)
    ]

    game.state.left_end = 3
    game.state.right_end = 5

    assert game.can_play_tile(
        make_tile(3, 6)
    ) is True


def test_can_play_tile_matches_right_end():

    game = make_game()

    game.state.board_tiles = [
        make_tile(3, 5)
    ]

    game.state.left_end = 3
    game.state.right_end = 5

    assert game.can_play_tile(
        make_tile(6, 5)
    ) is True


def test_cannot_play_unmatched_tile():

    game = make_game()

    game.state.board_tiles = [
        make_tile(3, 5)
    ]

    game.state.left_end = 3
    game.state.right_end = 5

    assert game.can_play_tile(
        make_tile(1, 2)
    ) is False


# =========================================================
# مهره‌های قابل بازی
# =========================================================


def test_get_playable_tiles():

    game = make_game()

    game.player_a.hand = [
        make_tile(1, 2),
        make_tile(3, 6),
        make_tile(4, 5),
    ]

    game.state.board_tiles = [
        make_tile(3, 5)
    ]

    game.state.left_end = 3
    game.state.right_end = 5

    playable = game.get_playable_tiles(
        game.player_a.user_id
    )

    assert len(playable) == 2

    assert make_tile(3, 6) in playable

    assert make_tile(4, 5) in playable


# =========================================================
# بازی اولین مهره
# =========================================================


def test_play_first_tile():

    game = make_game()

    game.player_a.hand = [
        make_tile(6, 6),
        make_tile(1, 2),
    ]

    game.player_b.hand = [
        make_tile(3, 4),
    ]

    game.state.board_tiles = []

    game.state.current_turn = game.player_a.user_id

    result = game.play_tile(
        game.player_a.user_id,
        0,
    )

    assert result is True

    assert len(game.player_a.hand) == 1

    assert len(game.state.board_tiles) == 1

    assert game.state.left_end == 6

    assert game.state.right_end == 6

    assert game.state.current_turn == game.player_b.user_id


# =========================================================
# بازی مهره سمت چپ
# =========================================================


def test_play_tile_on_left():

    game = make_game()

    game.player_a.hand = [
        make_tile(2, 6),
    ]

    game.player_b.hand = [
        make_tile(1, 3),
    ]

    game.state.board_tiles = [
        make_tile(6, 4)
    ]

    game.state.left_end = 6
    game.state.right_end = 4

    game.state.current_turn = game.player_a.user_id

    result = game.play_tile(
        game.player_a.user_id,
        0,
    )

    assert result is True

    assert len(game.state.board_tiles) == 2

    assert game.state.left_end == 2

    assert game.state.right_end == 4


# =========================================================
# بازی مهره سمت راست
# =========================================================


def test_play_tile_on_right():

    game = make_game()

    game.player_a.hand = [
        make_tile(4, 7),
    ]

    game.player_b.hand = [
        make_tile(1, 3),
    ]

    game.state.board_tiles = [
        make_tile(6, 4)
    ]

    game.state.left_end = 6
    game.state.right_end = 4

    game.state.current_turn = game.player_a.user_id

    result = game.play_tile(
        game.player_a.user_id,
        0,
    )

    assert result is True

    assert len(game.state.board_tiles) == 2

    assert game.state.left_end == 6

    assert game.state.right_end == 7


# =========================================================
# مهره نامعتبر نباید بازی شود
# =========================================================


def test_unmatched_tile_is_rejected():

    game = make_game()

    game.player_a.hand = [
        make_tile(1, 2),
    ]

    game.player_b.hand = [
        make_tile(3, 4),
    ]

    game.state.board_tiles = [
        make_tile(6, 5)
    ]

    game.state.left_end = 6
    game.state.right_end = 5

    game.state.current_turn = game.player_a.user_id

    result = game.play_tile(
        game.player_a.user_id,
        0,
    )

    assert result is False

    assert len(game.player_a.hand) == 1

    assert len(game.state.board_tiles) == 1


# =========================================================
# نوبت بازیکن اشتباه
# =========================================================


def test_wrong_player_cannot_play():

    game = make_game()

    game.state.current_turn = game.player_a.user_id

    result = game.play_tile(
        game.player_b.user_id,
        0,
    )

    assert result is False


# =========================================================
# خرید مهره
# =========================================================


def test_draw_tile_when_no_move_exists():

    game = make_game()

    game.player_a.hand = [
        make_tile(1, 1),
    ]

    game.player_b.hand = [
        make_tile(2, 2),
    ]

    game.state.board_tiles = [
        make_tile(6, 5)
    ]

    game.state.left_end = 6
    game.state.right_end = 5

    game.state.current_turn = game.player_a.user_id

    before = len(game.player_a.hand)

    drawn = game.draw_tile(
        game.player_a.user_id
    )

    assert drawn is not None

    assert len(game.player_a.hand) == before + 1

    assert game.deck.remaining() == 13


def test_cannot_draw_when_playable_tile_exists():

    game = make_game()

    game.player_a.hand = [
        make_tile(5, 2),
    ]

    game.state.board_tiles = [
        make_tile(6, 5)
    ]

    game.state.left_end = 6
    game.state.right_end = 5

    game.state.current_turn = game.player_a.user_id

    drawn = game.draw_tile(
        game.player_a.user_id
    )

    assert drawn is None

    assert len(game.player_a.hand) == 1


# =========================================================
# Pass
# =========================================================


def test_pass_not_allowed_when_boneyard_has_tiles():

    game = make_game()

    game.player_a.hand = [
        make_tile(1, 1),
    ]

    game.state.board_tiles = [
        make_tile(6, 5)
    ]

    game.state.left_end = 6
    game.state.right_end = 5

    game.state.current_turn = game.player_a.user_id

    result = game.pass_turn(
        game.player_a.user_id
    )

    assert result is False


# =========================================================
# پایان دور با خالی شدن دست
# =========================================================


def test_round_ends_when_player_has_no_tiles():

    game = make_game()

    game.player_a.hand = [
        make_tile(6, 5),
    ]

    game.player_b.hand = [
        make_tile(2, 3),
    ]

    game.state.board_tiles = [
        make_tile(6, 4)
    ]

    game.state.left_end = 6
    game.state.right_end = 4

    game.state.current_turn = game.player_a.user_id

    result = game.play_tile(
        game.player_a.user_id,
        0,
    )

    assert result is True

    assert game.round_finished is True

    assert game.match_finished is True

    assert game.match_winner == game.player_a.user_id

    assert game.get_winner() == game.player_a.user_id


# =========================================================
# وضعیت بازی
# =========================================================


def test_get_state():

    game = make_game()

    state = game.get_state()

    assert "state" in state

    assert "player_a" in state

    assert "player_b" in state

    assert "boneyard_remaining" in state

    assert "round_finished" in state

    assert "round_winner" in state

    assert "match_finished" in state

    assert "match_winner" in state

    assert "last_round_summary" in state


# =========================================================
# وضعیت اولیه امتیازات
# =========================================================


def test_initial_scores():

    game = make_game()

    scores = game.get_scores()

    assert scores == {
        game.player_a.user_id: 0,
        game.player_b.user_id: 0,
    }


# =========================================================
# بازی تمام نشده در شروع
# =========================================================


def test_game_is_not_finished_after_start():

    game = make_game()

    assert game.is_finished() is False

    assert game.get_winner() is None
