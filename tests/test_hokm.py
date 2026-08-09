from games.hokm.card import Card
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

    assert game.start_game()

    assert room.is_started

    assert len(player1.hand) == 13
    assert len(player2.hand) == 13

    first_player = room.players[0]

    assert game.choose_trump(
        first_player.user_id,
        "hearts",
    )

    assert game.state.trump == "hearts"

    first_card = first_player.hand[0]

    assert game.play_card(
        first_player.user_id,
        0,
    )

    second_player = room.players[1]

    assert game.state.current_turn == second_player.user_id

    second_card = second_player.hand[0]

    assert game.play_card(
        second_player.user_id,
        0,
    )

    assert game.state.completed_tricks == 1
