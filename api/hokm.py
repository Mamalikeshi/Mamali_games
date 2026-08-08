from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from games.hokm.player import Player
from games.hokm.room import Room


router = APIRouter(prefix="/api/hokm", tags=["Hokm"])

rooms: dict[str, Room] = {}


class CreateRoomRequest(BaseModel):
    user_id: int
    username: str


class JoinRoomRequest(BaseModel):
    user_id: int
    username: str


@router.post("/rooms")
def create_room(data: CreateRoomRequest):
    room_id = f"hokm-{len(rooms) + 1}"

    room = Room(room_id=room_id)

    player = Player(
        user_id=data.user_id,
        username=data.username,
    )

    room.add_player(player)
    rooms[room_id] = room

    return {
        "success": True,
        "room_id": room_id,
        "players": len(room.players),
    }


@router.post("/rooms/{room_id}/join")
def join_room(room_id: str, data: JoinRoomRequest):
    room = rooms.get(room_id)

    if room is None:
        raise HTTPException(
            status_code=404,
            detail="Room not found.",
        )

    player = Player(
        user_id=data.user_id,
        username=data.username,
    )

    if not room.add_player(player):
        raise HTTPException(
            status_code=400,
            detail="Room is full or player already joined.",
        )

    return {
        "success": True,
        "room_id": room.room_id,
        "players": len(room.players),
        "is_full": room.is_full(),
    }


@router.post("/rooms/{room_id}/ready/{user_id}")
def ready_player(room_id: str, user_id: int):
    room = rooms.get(room_id)

    if room is None:
        raise HTTPException(
            status_code=404,
            detail="Room not found.",
        )

    player = room.get_player(user_id)

    if player is None:
        raise HTTPException(
            status_code=404,
            detail="Player not found.",
        )

    player.is_ready = True

    game_started = False

    if room.both_ready():
        game_started = room.start()

    return {
        "success": True,
        "room_id": room.room_id,
        "user_id": user_id,
        "is_ready": player.is_ready,
        "players_ready": sum(
            1 for p in room.players if p.is_ready
        ),
        "game_started": game_started,
    }


@router.get("/rooms/{room_id}")
def get_room(room_id: str):
    room = rooms.get(room_id)

    if room is None:
        raise HTTPException(
            status_code=404,
            detail="Room not found.",
        )

    return {
        "room_id": room.room_id,
        "players": [
            {
                "user_id": player.user_id,
                "username": player.username,
                "is_ready": player.is_ready,
            }
            for player in room.players
        ],
        "is_full": room.is_full(),
        "is_started": room.is_started,
    }
