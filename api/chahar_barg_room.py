from games.chahar_barg.room import Room
from games.chahar_barg.player import Player


rooms = {}

# آخرین اتاقی که هر کاربر توش بوده، برای برگشتن به بازی بعد از خروج
active_room_by_user = {}


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

    if not room.add_player(player):
        return None

    active_room_by_user[user_id] = room_id

    return room


def get_room(room_id: str):
    return rooms.get(room_id)


def get_active_room_id(user_id: int):
    return active_room_by_user.get(user_id)


def clear_active_room(user_id: int):
    active_room_by_user.pop(user_id, None)


def mark_ready(room_id: str, user_id: int):
    room = rooms.get(room_id)

    if room is None:
        return False

    player = room.get_player(user_id)

    if player is None:
        return False

    player.is_ready = True

    return True
