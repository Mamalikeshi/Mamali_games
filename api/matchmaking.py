import uuid

from api.room import create_room, join_room


# کاربرهایی که منتظر پیدا شدن حریف تصادفی هستن
waiting_queue = []

# وقتی دو نفر جفت شدن، این دیکشنری کد اتاقشون رو نگه می‌داره
# تا نفری که منتظر بوده هم بتونه با پرسیدن پیدا کنه
matched_rooms = {}


def find_match(user_id: int, username: str):
    # اگه قبلاً جفت شده، فقط همون رو برگردون
    if user_id in matched_rooms:
        return {
            "matched": True,
            "room_id": matched_rooms.pop(user_id),
        }

    # اگه کسی توی صف منتظره، باهاش جفتش کن
    for waiting in waiting_queue:
        if waiting["user_id"] == user_id:
            continue

        waiting_queue.remove(waiting)

        room_id = "rand-" + uuid.uuid4().hex[:8]

        create_room(room_id)
        join_room(room_id, waiting["user_id"], waiting["username"])
        join_room(room_id, user_id, username)

        matched_rooms[waiting["user_id"]] = room_id

        return {
            "matched": True,
            "room_id": room_id,
        }

    # کسی توی صف نبود، خودش رو اضافه کن به صف و صبر کن
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
