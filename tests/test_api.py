from api.room import create_room, join_room
from api.hokm import start_hokm, choose_trump, get_game_state


def test_full_hokm_api_flow():
    room_id = "full-api-test"

    # Create room
    room = create_room(room_id)

    assert room is not None
    assert room.room_id == room_id

    # Player 1 joins
    room = join_room(
        room_id,
        1,
        "player1",
    )

    assert room is not None
    assert len(room.players) == 1

    # Player 2 joins
    room = join_room(
        room_id,
        2,
        "player2",
    )

    assert room is not None
    assert len(room.players) == 2

    # Both players are ready
    room.players[0].is_ready = True
    room.players[1].is_ready = True

    # Start Hokm
    game = start_hokm(room_id)

    assert game is not None
    assert room.is_started

    # Each player initially has 5 cards
    assert len(room.players[0].hand) == 5
    assert len(room.players[1].hand) == 5

    # Find Hokm player
    hokm_player = next(
        player
        for player in room.players
        if player.is_hokm
    )

    # Hokm player chooses trump
    assert choose_trump(
        room_id,
        hokm_player.user_id,
        "hearts",
    )

    # Both players should now have 13 cards
    assert len(room.players[0].hand) == 13
    assert len(room.players[1].hand) == 13

    # Game state should contain trump
    state = get_game_state(room_id)

    assert state is not None
    assert state["trump"] == "hearts"

    # Hokm player should have the first turn
    assert state["current_turn"] == hokm_player.user_id
