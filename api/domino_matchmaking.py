"""
Domino matchmaking - پیدا کردن حریف تصادفی، بدون نیاز به ساخت اتاق و دادن کد.
دقیقاً هم‌الگو با api/chahar_barg_matchmaking.py
"""

import uuid

from games.domino.room import Room
from games.domino.player import Player

import api.domino as domino_api


# کاربرهایی که منتظر پیدا شدن حریف تصادفی هستن
waiting_queue = []

# وقتی دو نفر جفت شدن، این دیکشنری کد اتاقشون رو نگه می‌داره
matched_rooms = {}


def _create_and_join(room_id: str, first: dict, second: dict) -> Room:
    room = Room(room_id=room_id)
    room.add_player(Player(user_id=first["user_id"], username=first["username"]))
    room.add_player(Player(user_id=second["user_id"], username=second["username"]))

    domino_api.rooms[room_id] = room
    domino_api.active_room_by_user[first["user_id"]] = room_id
    domino_api.active_room_by_user[second["user_id"]] = room_id

    return room


def find_match(user_id: int, username: str):
    if user_id in matched_rooms:
        return {
            "matched": True,
            "room_id": matched_rooms.pop(user_id),
        }

    for waiting in waiting_queue:
        if waiting["user_id"] == user_id:
            continue

        waiting_queue.remove(waiting)

        room_id = "domino-" + uuid.uuid4().hex[:8]

        _create_and_join(
            room_id,
            waiting,
            {"user_id": user_id, "username": username},
        )

        matched_rooms[waiting["user_id"]] = room_id

        return {
            "matched": True,
            "room_id": room_id,
        }

    already_waiting = any(
        w["user_id"] == user_id for w in waiting_queue
    )

    if not already_waiting:
        waiting_queue.append({
            "user_id": user_id,
            "username": username,
        })

    return {
        "matched": False,
    }


def cancel_matchmaking(user_id: int):
    global waiting_queue
    waiting_queue = [
        w for w in waiting_queue if w["user_id"] != user_id
    ]
