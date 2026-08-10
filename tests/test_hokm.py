from games.hokm.room import Room
from games.hokm.player import Player
from games.hokm.game import HokmGame


def test_hokm_game_flow():
    room = Room(room_id="test-room")

    player1 = Player(
        user_id=1,
        username="player1",
    )

    player2 = Player(
        user_id=2,
        username="player2",
    )

    assert room.add_player(player1)
    assert room.add_player(player2)

    player1.is_ready = True
    player2.is_ready = True

    assert room.both_ready()

    game = HokmGame(room)

    # Start game: each player receives 5 cards.
    assert game.start_game()

    assert room.is_started

    assert len(player1.hand) == 5
    assert len(player2.hand) == 5

    # The first player is the Hokm player.
    hokm_player = room.players[0]
    other_player = room.players[1]

    assert hokm_player.is_hokm
    assert not other_player.is_hokm

    # Only the Hokm player can choose the trump.
    assert game.choose_trump(
        other_player.user_id,
        "hearts",
    ) is False

    assert game.choose_trump(
        hokm_player.user_id,
        "hearts",
    )

    assert game.state.trump == "hearts"

    # After choosing trump, both players receive
    # the remaining 8 cards.
    assert len(player1.hand) == 13
    assert len(player2.hand) == 13

    # The Hokm player starts the first trick.
    assert game.state.current_turn == hokm_player.user_id

    assert game.play_card(
        hokm_player.user_id,
        0,
    )

    assert game.state.current_turn == other_player.user_id

    assert game.play_card(
        other_player.user_id,
        0,
    )

    assert game.state.completed_tricks == 1
