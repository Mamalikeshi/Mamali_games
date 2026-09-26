"""
Tests for Domino game engine - 2 player mode.

Covers:
- Game start
- Two-player requirement
- Tile placement
- Drawing
- Passing
- Round scoring
- Block scoring
- Match scoring
- Next round
- Match winner
"""

from games.domino.game import DominoGame
from games.domino.player import Player
from games.domino.room import Room
from games.domino.tile import Tile


def make_tile(left: int, right: int) -> Tile:
    return Tile(left, right)


def make_game() -> DominoGame:

    player_a = Player(
        user_id=1,
        username="Player A",
    )

    player_b = Player(
        user_id=2,
        username="Player B",
    )

    room = Room(
        room_id="domino-test-room"
    )

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

    assert game.round_number == 1

    assert game.player_a.score == 0
    assert game.player_b.score == 0

    assert game.match_finished is False


# =========================================================
# فقط دو بازیکن
# =========================================================

def test_game_requires_two_players():

    player_a = Player(
        user_id=1,
        username="Player A",
    )

    room = Room(
        room_id="domino-one-player"
    )

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

    game.state.current_turn = (
        game.player_a.user_id
    )

    result = game.play_tile(
        game.player_a.user_id,
        0,
    )

    assert result is True

    assert len(game.player_a.hand) == 1

    assert len(game.state.board_tiles) == 1

    assert game.state.left_end == 6
    assert game.state.right_end == 6

    assert (
        game.state.current_turn
        == game.player_b.user_id
    )


# =========================================================
# بازی سمت چپ
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

    game.state.current_turn = (
        game.player_a.user_id
    )

    result = game.play_tile(
        game.player_a.user_id,
        0,
    )

    assert result is True

    assert len(game.state.board_tiles) == 2

    assert game.state.left_end == 2
    assert game.state.right_end == 4


# =========================================================
# بازی سمت راست
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

    game.state.current_turn = (
        game.player_a.user_id
    )

    result = game.play_tile(
        game.player_a.user_id,
        0,
    )

    assert result is True

    assert len(game.state.board_tiles) == 2

    assert game.state.left_end == 6
    assert game.state.right_end == 7


# =========================================================
# مهره نامعتبر
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

    game.state.current_turn = (
        game.player_a.user_id
    )

    result = game.play_tile(
        game.player_a.user_id,
        0,
    )

    assert result is False

    assert len(game.player_a.hand) == 1

    assert len(game.state.board_tiles) == 1


# =========================================================
# نوبت اشتباه
# =========================================================

def test_wrong_player_cannot_play():

    game = make_game()

    game.state.current_turn = (
        game.player_a.user_id
    )

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

    game.state.current_turn = (
        game.player_a.user_id
    )

    before = len(
        game.player_a.hand
    )

    drawn = game.draw_tile(
        game.player_a.user_id
    )

    assert drawn is not None

    assert len(
        game.player_a.hand
    ) == before + 1

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

    game.state.current_turn = (
        game.player_a.user_id
    )

    drawn = game.draw_tile(
        game.player_a.user_id
    )

    assert drawn is None

    assert len(
        game.player_a.hand
    ) == 1


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

    game.state.current_turn = (
        game.player_a.user_id
    )

    result = game.pass_turn(
        game.player_a.user_id
    )

    assert result is False


# =========================================================
# پایان دست با خالی شدن دست
# =========================================================

def test_round_scoring_when_player_has_no_tiles():

    game = make_game()

    game.player_a.hand = [
        make_tile(6, 5),
    ]

    game.player_b.hand = [
        make_tile(2, 3),
        make_tile(4, 5),
    ]

    game.state.board_tiles = [
        make_tile(6, 4)
    ]

    game.state.left_end = 6
    game.state.right_end = 4

    game.state.current_turn = (
        game.player_a.user_id
    )

    result = game.play_tile(
        game.player_a.user_id,
        0,
    )

    assert result is True

    assert game.round_finished is True

    assert game.round_winner == 1

    assert game.match_finished is False

    assert game.match_winner is None

    # 2+3 + 4+5 = 14
    assert game.player_a.score == 14
    assert game.player_b.score == 0

    assert game.last_round_summary is not None

    assert game.last_round_summary["points"] == 14

    assert game.last_round_summary["reason"] == "empty_hand"


# =========================================================
# شروع دست بعد
# =========================================================

def test_start_next_round():

    game = make_game()

    game.round_finished = True

    old_round = game.round_number

    result = game.start_next_round()

    assert result is True

    assert game.round_number == old_round + 1

    assert game.round_finished is False

    assert game.match_finished is False

    assert len(game.player_a.hand) == 7

    assert len(game.player_b.hand) == 7

    assert game.deck is not None

    assert game.deck.remaining() == 14


def test_cannot_start_next_round_before_round_finishes():

    game = make_game()

    assert game.round_finished is False

    assert game.start_next_round() is False


# =========================================================
# Block
# =========================================================

def test_block_round_scoring():

    game = make_game()

    game.player_a.hand = [
        make_tile(1, 1),
    ]

    game.player_b.hand = [
        make_tile(6, 6),
    ]

    game.state.board_tiles = [
        make_tile(4, 5)
    ]

    game.state.left_end = 4
    game.state.right_end = 5

    game.state.current_turn = (
        game.player_a.user_id
    )

    game.deck.tiles = []

    assert game.pass_turn(
        game.player_a.user_id
    ) is True

    assert game.pass_turn(
        game.player_b.user_id
    ) is True

    assert game.round_finished is True

    assert game.round_winner == (
        game.player_a.user_id
    )

    # حریف 12 پیپ دارد
    assert game.player_a.score == 12

    assert game.player_b.score == 0

    assert game.match_finished is False


def test_block_tie_gives_zero_points():

    game = make_game()

    game.player_a.hand = [
        make_tile(2, 2),
    ]

    game.player_b.hand = [
        make_tile(1, 3),
    ]

    game.state.board_tiles = [
        make_tile(5, 6)
    ]

    game.state.left_end = 5
    game.state.right_end = 6

    game.state.current_turn = (
        game.player_a.user_id
    )

    game.deck.tiles = []

    assert game.pass_turn(
        game.player_a.user_id
    ) is True

    assert game.pass_turn(
        game.player_b.user_id
    ) is True

    assert game.round_finished is True

    assert game.round_winner is None

    assert game.player_a.score == 0
    assert game.player_b.score == 0


# =========================================================
# رسیدن به 101
# =========================================================

def test_match_finishes_at_101():

    game = make_game()

    game.player_a.score = 95
    game.player_b.score = 20

    game.player_a.hand = [
        make_tile(6, 5),
    ]

    game.player_b.hand = [
        make_tile(3, 3),
    ]

    game.state.board_tiles = [
        make_tile(6, 4)
    ]

    game.state.left_end = 6
    game.state.right_end = 4

    game.state.current_turn = (
        game.player_a.user_id
    )

    result = game.play_tile(
        game.player_a.user_id,
        0,
    )

    assert result is True

    assert game.player_a.score == 101

    assert game.match_finished is True

    assert game.match_winner == (
        game.player_a.user_id
    )

    assert game.is_finished() is True

    assert game.get_winner() == (
        game.player_a.user_id
    )


def test_cannot_start_next_round_after_match_finishes():

    game = make_game()

    game.player_a.score = 101
    game.match_finished = True
    game.match_winner = game.player_a.user_id
    game.round_finished = True

    assert game.start_next_round() is False


# =========================================================
# امتیازات
# =========================================================

def test_get_scores():

    game = make_game()

    assert game.get_scores() == {
        1: 0,
        2: 0,
    }

    game.player_a.score = 30
    game.player_b.score = 15

    assert game.get_scores() == {
        1: 30,
        2: 15,
    }


# =========================================================
# وضعیت بازی
# =========================================================

def test_get_state_contains_match_information():

    game = make_game()

    state = game.get_state()

    assert "state" in state
    assert "player_a" in state
    assert "player_b" in state

    assert "boneyard_remaining" in state

    assert "round_number" in state
    assert "round_finished" in state
    assert "round_winner" in state

    assert "match_finished" in state
    assert "match_winner" in state

    assert "match_target_score" in state
    assert "scores" in state

    assert "last_round_summary" in state

    assert state["match_target_score"] == 101


# =========================================================
# بازی تازه شروع شده
# =========================================================

def test_game_is_not_finished_after_start():

    game = make_game()

    assert game.is_finished() is False

    assert game.get_winner() is None
