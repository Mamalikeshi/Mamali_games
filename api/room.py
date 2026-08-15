from games.hokm.room import Room
from games.hokm.player import Player


rooms = {}


def create_room(room_id: str):
    if room_id in rooms:
        return None

    room = Room(room_id=room_id)
    rooms[room_id] = room

    return room


def join_room(room_id: str, user_id: int, username: str):
    room = rooms.get(room_id)

    if room is None:
        return None

    player = Player(
        user_id=user_id,
        username=username,
    )
    player.is_ready = True

    if not room.add_player(player):
        return None

    return room


def get_room(room_id: str):
    return rooms.get(room_id)
