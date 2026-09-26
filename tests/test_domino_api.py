from fastapi.testclient import TestClient

from api.domino import router


class TestApp:
    def __init__(self):
        from fastapi import FastAPI

        self.app = FastAPI()
        self.app.include_router(router)


client = TestClient(TestApp().app)


def reset_game_data():
    from api import domino

    domino.rooms.clear()
    domino.games.clear()


# =========================================================
# ساخت اتاق
# =========================================================

def test_create_domino_room():

    reset_game_data()

    response = client.post(
        "/api/domino/rooms",
        json={
            "user_id": 1,
            "username": "player1",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["room_id"] == "domino-1"
    assert data["players"] == 1
    assert data["is_full"] is False
    assert data["is_started"] is False


# =========================================================
# ورود بازیکن دوم
# =========================================================

def test_join_domino_room():

    reset_game_data()

    create = client.post(
        "/api/domino/rooms",
        json={
            "user_id": 1,
            "username": "player1",
        },
    )

    room_id = create.json()["room_id"]

    response = client.post(
        f"/api/domino/rooms/{room_id}/join",
        json={
            "user_id": 2,
            "username": "player2",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["players"] == 2
    assert data["is_full"] is True


# =========================================================
# اتاق بیشتر از دو بازیکن را قبول نکند
# =========================================================

def test_domino_room_rejects_third_player():

    reset_game_data()

    create = client.post(
        "/api/domino/rooms",
        json={
            "user_id": 1,
            "username": "player1",
        },
    )

    room_id = create.json()["room_id"]

    response = client.post(
        f"/api/domino/rooms/{room_id}/join",
        json={
            "user_id": 2,
            "username": "player2",
        },
    )

    assert response.status_code == 200

    response = client.post(
        f"/api/domino/rooms/{room_id}/join",
        json={
            "user_id": 3,
            "username": "player3",
        },
    )

    assert response.status_code == 400


# =========================================================
# آماده شدن بازیکن
# =========================================================

def test_domino_player_ready():

    reset_game_data()

    create = client.post(
        "/api/domino/rooms",
        json={
            "user_id": 1,
            "username": "player1",
        },
    )

    room_id = create.json()["room_id"]

    client.post(
        f"/api/domino/rooms/{room_id}/join",
        json={
            "user_id": 2,
            "username": "player2",
        },
    )

    response = client.post(
        f"/api/domino/rooms/{room_id}/ready/1"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["is_ready"] is True
    assert data["players_ready"] == 1
    assert data["game_started"] is False


# =========================================================
# شروع بازی بعد از آماده شدن هر دو نفر
# =========================================================

def test_domino_game_starts_when_both_players_ready():

    reset_game_data()

    create = client.post(
        "/api/domino/rooms",
        json={
            "user_id": 1,
            "username": "player1",
        },
    )

    room_id = create.json()["room_id"]

    client.post(
        f"/api/domino/rooms/{room_id}/join",
        json={
            "user_id": 2,
            "username": "player2",
        },
    )

    first_ready = client.post(
        f"/api/domino/rooms/{room_id}/ready/1"
    )

    assert first_ready.status_code == 200
    assert first_ready.json()["game_started"] is False

    second_ready = client.post(
        f"/api/domino/rooms/{room_id}/ready/2"
    )

    assert second_ready.status_code == 200

    data = second_ready.json()

    assert data["success"] is True
    assert data["game_started"] is True


# =========================================================
# دریافت اطلاعات اتاق
# =========================================================

def test_get_domino_room():

    reset_game_data()

    create = client.post(
        "/api/domino/rooms",
        json={
            "user_id": 1,
            "username": "player1",
        },
    )

    room_id = create.json()["room_id"]

    response = client.get(
        f"/api/domino/rooms/{room_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["room_id"] == room_id
    assert len(data["players"]) == 1
    assert data["players"][0]["user_id"] == 1
    assert data["game_exists"] is False


# =========================================================
# دریافت دست بازیکن
# =========================================================

def test_get_domino_player_hand():

    reset_game_data()

    create = client.post(
        "/api/domino/rooms",
        json={
            "user_id": 1,
            "username": "player1",
        },
    )

    room_id = create.json()["room_id"]

    client.post(
        f"/api/domino/rooms/{room_id}/join",
        json={
            "user_id": 2,
            "username": "player2",
        },
    )

    client.post(
        f"/api/domino/rooms/{room_id}/ready/1"
    )

    client.post(
        f"/api/domino/rooms/{room_id}/ready/2"
    )

    response = client.get(
        f"/api/domino/rooms/{room_id}/hand/1"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["user_id"] == 1
    assert len(data["hand"]) == 7


# =========================================================
# دریافت وضعیت بازی
# =========================================================

def test_get_domino_game_state():

    reset_game_data()

    create = client.post(
        "/api/domino/rooms",
        json={
            "user_id": 1,
            "username": "player1",
        },
    )

    room_id = create.json()["room_id"]

    client.post(
        f"/api/domino/rooms/{room_id}/join",
        json={
            "user_id": 2,
            "username": "player2",
        },
    )

    client.post(
        f"/api/domino/rooms/{room_id}/ready/1"
    )

    client.post(
        f"/api/domino/rooms/{room_id}/ready/2"
    )

    response = client.get(
        f"/api/domino/rooms/{room_id}/game"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["room_id"] == room_id
    assert "game" in data


# =========================================================
# دریافت مهره‌های قابل بازی
# =========================================================

def test_get_playable_domino_tiles():

    reset_game_data()

    create = client.post(
        "/api/domino/rooms",
        json={
            "user_id": 1,
            "username": "player1",
        },
    )

    room_id = create.json()["room_id"]

    client.post(
        f"/api/domino/rooms/{room_id}/join",
        json={
            "user_id": 2,
            "username": "player2",
        },
    )

    client.post(
        f"/api/domino/rooms/{room_id}/ready/1"
    )

    client.post(
        f"/api/domino/rooms/{room_id}/ready/2"
    )

    response = client.get(
        f"/api/domino/rooms/{room_id}/playable/1"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert "playable_indexes" in data
    assert "playable_tiles" in data


# =========================================================
# امتیاز بازی
# =========================================================

def test_get_domino_score():

    reset_game_data()

    create = client.post(
        "/api/domino/rooms",
        json={
            "user_id": 1,
            "username": "player1",
        },
    )

    room_id = create.json()["room_id"]

    client.post(
        f"/api/domino/rooms/{room_id}/join",
        json={
            "user_id": 2,
            "username": "player2",
        },
    )

    client.post(
        f"/api/domino/rooms/{room_id}/ready/1"
    )

    client.post(
        f"/api/domino/rooms/{room_id}/ready/2"
    )

    response = client.get(
        f"/api/domino/rooms/{room_id}/score"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert "scores" in data
    assert "game_finished" in data


# =========================================================
# اتاق وجود نداشته باشد
# =========================================================

def test_domino_room_not_found():

    reset_game_data()

    response = client.get(
        "/api/domino/rooms/not-existing"
    )

    assert response.status_code == 404


# =========================================================
# بازی وجود نداشته باشد
# =========================================================

def test_domino_game_not_found():

    reset_game_data()

    response = client.get(
        "/api/domino/rooms/not-existing/game"
    )

    assert response.status_code == 404


# =========================================================
# بازیکن وجود نداشته باشد
# =========================================================

def test_domino_hand_player_not_found():

    reset_game_data()

    create = client.post(
        "/api/domino/rooms",
        json={
            "user_id": 1,
            "username": "player1",
        },
    )

    room_id = create.json()["room_id"]

    response = client.get(
        f"/api/domino/rooms/{room_id}/hand/999"
    )

    assert response.status_code == 404
