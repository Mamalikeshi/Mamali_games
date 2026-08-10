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

    assert len(player1.hand) == 5
    assert len(player2.hand) == 5

    hokm_players = [
        player
        for player in room.players
        if player.is_hokm
    ]

    assert len(hokm_players) == 1

    hokm_player = hokm_players[0]

    other_player = next(
        player
        for player in room.players
        if player.user_id != hokm_player.user_id
    )

    assert game.state.current_turn == hokm_player.user_id

    assert game.choose_trump(
        other_player.user_id,
        "hearts",
    ) is False

    assert game.choose_trump(
        hokm_player.user_id,
        "hearts",
    )

    assert game.state.trump == "hearts"

    assert len(player1.hand) == 13
    assert len(player2.hand) == 13

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
