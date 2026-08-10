from api.room import create_room, join_room, get_room
from api.hokm import start_hokm, choose_trump, get_game_state


def test_room_and_hokm_api_flow():
    room_id = "api-test-room"

    room = create_room(room_id)

    assert room is not None
    assert room.room_id == room_id

    room = join_room(
        room_id,
        1,
        "player1",
    )

    assert room is not None

    room = join_room(
        room_id,
        2,
        "player2",
    )

    assert room is not None

    assert len(room.players) == 2

    room.players[0].is_ready = True
    room.players[1].is_ready = True

    game = start_hokm(room_id)

    assert game is not None

    state = get_game_state(room_id)

    assert state is not None
    assert state["trump"] is None

    hokm_player = next(
        player
        for player in room.players
        if player.is_hokm
    )

    assert choose_trump(
        room_id,
        hokm_player.user_id,
        "hearts",
    )

    state = get_game_state(room_id)

    assert state["trump"] == "hearts"
