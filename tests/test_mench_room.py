"""
Tests for the Mench room.
"""

from games.mench.room import Room


# ============================================================
# Initialization
# ============================================================

def test_room_initialization():
    room = Room(
        room_id="room-1",
        max_players=2,
    )

    assert room.room_id == "room-1"
    assert room.max_players == 2
    assert room.players == []
    assert room.is_started is False
    assert room.game is None


def test_room_supports_two_players():
    room = Room(
        room_id="room-1",
        max_players=2,
    )

    assert room.max_players == 2


def test_room_supports_three_players():
    room = Room(
        room_id="room-1",
        max_players=3,
    )

    assert room.max_players == 3


def test_room_supports_four_players():
    room = Room(
        room_id="room-1",
        max_players=4,
    )

    assert room.max_players == 4


def test_invalid_player_count():
    try:
        Room(
            room_id="room-1",
            max_players=5,
        )
        assert False
    except ValueError:
        assert True


# ============================================================
# Player management
# ============================================================

def test_add_player():
    room = Room(
        room_id="room-1",
        max_players=2,
    )

    player = room.add_player(
        user_id=1,
        username="player1",
    )

    assert player is not None
    assert player.user_id == 1
    assert player.username == "player1"
    assert player.color == "red"
    assert len(room.players) == 1


def test_second_player_gets_second_color():
    room = Room(
        room_id="room-1",
        max_players=2,
    )

    player1 = room.add_player(
        user_id=1,
        username="player1",
    )

    player2 = room.add_player(
        user_id=2,
        username="player2",
    )

    assert player1.color == "red"
    assert player2.color == "yellow"


def test_duplicate_player_is_rejected():
    room = Room(
        room_id="room-1",
        max_players=2,
    )

    first = room.add_player(
        user_id=1,
        username="player1",
    )

    second = room.add_player(
        user_id=1,
        username="player1-again",
    )

    assert first is not None
    assert second is None
    assert len(room.players) == 1


def test_room_rejects_player_when_full():
    room = Room(
        room_id="room-1",
        max_players=2,
    )

    room.add_player(
        user_id=1,
        username="player1",
    )

    room.add_player(
        user_id=2,
        username="player2",
    )

    player3 = room.add_player(
        user_id=3,
        username="player3",
    )

    assert player3 is None
    assert len(room.players) == 2


def test_get_player():
    room = Room(
        room_id="room-1",
        max_players=2,
    )

    player = room.add_player(
        user_id=10,
        username="player10",
    )

    assert room.get_player(10) is player
    assert room.get_player(999) is None


def test_is_full():
    room = Room(
        room_id="room-1",
        max_players=2,
    )

    assert room.is_full() is False

    room.add_player(
        user_id=1,
        username="player1",
    )

    assert room.is_full() is False

    room.add_player(
        user_id=2,
        username="player2",
    )

    assert room.is_full() is True


# ============================================================
# Readiness
# ============================================================

def test_room_is_not_ready_when_not_full():
    room = Room(
        room_id="room-1",
        max_players=2,
    )

    player = room.add_player(
        user_id=1,
        username="player1",
    )

    player.is_ready = True

    assert room.all_ready() is False


def test_room_is_not_ready_when_player_not_ready():
    room = Room(
        room_id="room-1",
        max_players=2,
    )

    player1 = room.add_player(
        user_id=1,
        username="player1",
    )

    player2 = room.add_player(
        user_id=2,
        username="player2",
    )

    player1.is_ready = True
    player2.is_ready = False

    assert room.all_ready() is False


def test_room_is_ready_when_all_players_are_ready():
    room = Room(
        room_id="room-1",
        max_players=2,
    )

    player1 = room.add_player(
        user_id=1,
        username="player1",
    )

    player2 = room.add_player(
        user_id=2,
        username="player2",
    )

    player1.is_ready = True
    player2.is_ready = True

    assert room.all_ready() is True


# ============================================================
# Starting the game
# ============================================================

def test_room_cannot_start_when_not_full():
    room = Room(
        room_id="room-1",
        max_players=2,
    )

    player = room.add_player(
        user_id=1,
        username="player1",
    )

    player.is_ready = True

    assert room.start() is False
    assert room.is_started is False
    assert room.game is None


def test_room_cannot_start_when_not_all_ready():
    room = Room(
        room_id="room-1",
        max_players=2,
    )

    player1 = room.add_player(
        user_id=1,
        username="player1",
    )

    room.add_player(
        user_id=2,
        username="player2",
    )

    player1.is_ready = True

    assert room.start() is False
    assert room.is_started is False
    assert room.game is None


def test_room_starts_game_when_all_ready():
    room = Room(
        room_id="room-1",
        max_players=2,
    )

    player1 = room.add_player(
        user_id=1,
        username="player1",
    )

    player2 = room.add_player(
        user_id=2,
        username="player2",
    )

    player1.is_ready = True
    player2.is_ready = True

    assert room.start() is True

    assert room.is_started is True
    assert room.game is not None

    assert room.game.room_id == "room-1"
    assert room.game.state.player_count() == 2
    assert room.game.state.current_player_id == 1


def test_room_game_uses_same_player_objects():
    room = Room(
        room_id="room-1",
        max_players=2,
    )

    player1 = room.add_player(
        user_id=1,
        username="player1",
    )

    player2 = room.add_player(
        user_id=2,
        username="player2",
    )

    player1.is_ready = True
    player2.is_ready = True

    room.start()

    game_player1 = room.game.get_player(1)
    game_player2 = room.game.get_player(2)

    assert game_player1 is player1
    assert game_player2 is player2


def test_started_room_cannot_start_again():
    room = Room(
        room_id="room-1",
        max_players=2,
    )

    player1 = room.add_player(
        user_id=1,
        username="player1",
    )

    player2 = room.add_player(
        user_id=2,
        username="player2",
    )

    player1.is_ready = True
    player2.is_ready = True

    assert room.start() is True

    old_game = room.game

    assert room.start() is False
    assert room.game is old_game


def test_started_room_cannot_accept_new_player():
    room = Room(
        room_id="room-1",
        max_players=2,
    )

    player1 = room.add_player(
        user_id=1,
        username="player1",
    )

    player2 = room.add_player(
        user_id=2,
        username="player2",
    )

    player1.is_ready = True
    player2.is_ready = True

    room.start()

    player3 = room.add_player(
        user_id=3,
        username="player3",
    )

    assert player3 is None


# ============================================================
# Serialization
# ============================================================

def test_room_to_dict_before_start():
    room = Room(
        room_id="room-1",
        max_players=2,
    )

    data = room.to_dict()

    assert data["room_id"] == "room-1"
    assert data["max_players"] == 2
    assert data["is_full"] is False
    assert data["is_started"] is False
    assert data["game"] is None


def test_room_to_dict_after_start():
    room = Room(
        room_id="room-1",
        max_players=2,
    )

    player1 = room.add_player(
        user_id=1,
        username="player1",
    )

    player2 = room.add_player(
        user_id=2,
        username="player2",
    )

    player1.is_ready = True
    player2.is_ready = True

    room.start()

    data = room.to_dict()

    assert data["is_started"] is True
    assert data["game"] is not None
    assert data["game"]["room_id"] == "room-1"
    assert len(data["game"]["players"]) == 2
