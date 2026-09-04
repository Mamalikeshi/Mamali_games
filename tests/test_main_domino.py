from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_main_health():

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_domino_api_is_registered_in_main():

    response = client.post(
        "/api/domino/rooms",
        json={
            "user_id": 1001,
            "username": "main_player_1",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert "room_id" in data
    assert data["players"] == 1


def test_domino_join_through_main():

    create_response = client.post(
        "/api/domino/rooms",
        json={
            "user_id": 2001,
            "username": "player_1",
        },
    )

    assert create_response.status_code == 200

    room_id = create_response.json()["room_id"]

    join_response = client.post(
        f"/api/domino/rooms/{room_id}/join",
        json={
            "user_id": 2002,
            "username": "player_2",
        },
    )

    assert join_response.status_code == 200

    data = join_response.json()

    assert data["success"] is True
    assert data["players"] == 2
    assert data["is_full"] is True


def test_domino_ready_and_start_through_main():

    create_response = client.post(
        "/api/domino/rooms",
        json={
            "user_id": 3001,
            "username": "player_1",
        },
    )

    assert create_response.status_code == 200

    room_id = create_response.json()["room_id"]

    join_response = client.post(
        f"/api/domino/rooms/{room_id}/join",
        json={
            "user_id": 3002,
            "username": "player_2",
        },
    )

    assert join_response.status_code == 200

    ready_1 = client.post(
        f"/api/domino/rooms/{room_id}/ready/3001"
    )

    assert ready_1.status_code == 200
    assert ready_1.json()["game_started"] is False

    ready_2 = client.post(
        f"/api/domino/rooms/{room_id}/ready/3002"
    )

    assert ready_2.status_code == 200

    data = ready_2.json()

    assert data["success"] is True
    assert data["game_started"] is True


def test_domino_game_state_through_main():

    create_response = client.post(
        "/api/domino/rooms",
        json={
            "user_id": 4001,
            "username": "player_1",
        },
    )

    assert create_response.status_code == 200

    room_id = create_response.json()["room_id"]

    join_response = client.post(
        f"/api/domino/rooms/{room_id}/join",
        json={
            "user_id": 4002,
            "username": "player_2",
        },
    )

    assert join_response.status_code == 200

    client.post(
        f"/api/domino/rooms/{room_id}/ready/4001"
    )

    client.post(
        f"/api/domino/rooms/{room_id}/ready/4002"
    )

    response = client.get(
        f"/api/domino/rooms/{room_id}/game"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["room_id"] == room_id
    assert "game" in data
