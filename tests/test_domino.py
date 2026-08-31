"""
Tests for Domino - 2 player mode.
Fully independent from other games.
"""

from games.domino.card import DominoTile
from games.domino.player import DominoPlayer
from games.domino.deck import DominoDeck
from games.domino.state import DominoState
from games.domino.game import DominoGame
from games.domino.room import DominoRoom


def test_domino_tile_creation():
    tile = DominoTile(3, 5)

    assert tile.left == 3
    assert tile.right == 5


def test_domino_tile_value():
    tile = DominoTile(3, 5)

    assert tile.value == 8


def test_domino_tile_matches():
    tile = DominoTile(3, 5)

    assert tile.matches(3)
    assert tile.matches(5)

    assert not tile.matches(2)


def test_domino_tile_is_double():
    double_tile = DominoTile(6, 6)
    normal_tile = DominoTile(3, 5)

    assert double_tile.is_double()
    assert not normal_tile.is_double()


def test_domino_tile_flip():
    tile = DominoTile(2, 6)

    flipped = tile.flip()

    assert flipped.left == 6
    assert flipped.right == 2


def test_domino_deck_has_28_tiles():
    deck = DominoDeck()

    assert len(deck.tiles) == 28


def test_domino_deck_has_no_duplicate_tiles():
    deck = DominoDeck()

    values = [
        (tile.left, tile.right)
        for tile in deck.tiles
    ]

    assert len(values) == len(set(values))


def test_domino_player_creation():
    player = DominoPlayer(user_id=100)

    assert player.user_id == 100
    assert player.hand == []


def test_domino_player_add_tile():
    player = DominoPlayer(user_id=100)
    tile = DominoTile(2, 4)

    player.add_tile(tile)

    assert len(player.hand) == 1
    assert player.hand[0] == tile


def test_domino_player_remove_tile():
    player = DominoPlayer(user_id=100)
    tile = DominoTile(2, 4)

    player.add_tile(tile)
    player.remove_tile(tile)

    assert tile not in player.hand


def test_domino_state_creation():
    state = DominoState()

    assert state.table == []
    assert state.current_turn is None
    assert state.round_over is False


def test_domino_state_set_turn():
    state = DominoState()

    state.set_turn(100)

    assert state.current_turn == 100


def test_domino_room_accepts_two_players():
    room = DominoRoom(room_id="test-room")

    player_a = DominoPlayer(user_id=100)
    player_b = DominoPlayer(user_id=200)

    assert room.add_player(player_a)
    assert room.add_player(player_b)

    assert len(room.players) == 2


def test_domino_room_rejects_third_player():
    room = DominoRoom(room_id="test-room")

    player_a = DominoPlayer(user_id=100)
    player_b = DominoPlayer(user_id=200)
    player_c = DominoPlayer(user_id=300)

    assert room.add_player(player_a)
    assert room.add_player(player_b)

    assert not room.add_player(player_c)

    assert len(room.players) == 2


def test_domino_game_requires_two_players():
    room = DominoRoom(room_id="test-room")

    player = DominoPlayer(user_id=100)

    assert room.add_player(player)

    game = DominoGame(room)

    assert not game.start_game()


def test_domino_game_starts_with_two_players():
    room = DominoRoom(room_id="test-room")

    player_a = DominoPlayer(user_id=100)
    player_b = DominoPlayer(user_id=200)

    room.add_player(player_a)
    room.add_player(player_b)

    game = DominoGame(room)

    assert game.start_game()


def test_domino_game_deals_tiles_to_two_players():
    room = DominoRoom(room_id="test-room")

    player_a = DominoPlayer(user_id=100)
    player_b = DominoPlayer(user_id=200)

    room.add_player(player_a)
    room.add_player(player_b)

    game = DominoGame(room)

    assert game.start_game()

    assert len(player_a.hand) > 0
    assert len(player_b.hand) > 0


def test_domino_game_has_current_turn():
    room = DominoRoom(room_id="test-room")

    player_a = DominoPlayer(user_id=100)
    player_b = DominoPlayer(user_id=200)

    room.add_player(player_a)
    room.add_player(player_b)

    game = DominoGame(room)

    assert game.start_game()

    assert game.state.current_turn in [100, 200]


def test_domino_game_get_player():
    room = DominoRoom(room_id="test-room")

    player_a = DominoPlayer(user_id=100)
    player_b = DominoPlayer(user_id=200)

    room.add_player(player_a)
    room.add_player(player_b)

    game = DominoGame(room)

    assert game.get_player(100) == player_a
    assert game.get_player(200) == player_b
    assert game.get_player(999) is None
