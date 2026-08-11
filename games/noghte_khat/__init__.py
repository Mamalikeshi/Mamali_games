from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from games.noghte_khat.room import Room
from games.noghte_khat.game import NoghteKhatGame

router = APIRouter(prefix="/api/noghte_khat", tags=["NoghteKhat"])

rooms: dict[str, Room] = {}
games: dict[str, NoghteKhatGame] = {}


class CreateRoomRequest(BaseModel):
    user_id: int
    username: str


class JoinRoomRequest(BaseModel):
    user_id: int
    username: str


@router.post("/rooms")
def create_room(data: CreateRoomRequest):
    room_id = f"noghte-khat-{len(rooms) + 1}"
    room = Room(room_id=room_id)
    room.add_player(user_id=data.user_id, username=data.username)
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
        raise HTTPException(status_code=404, detail="Room not found.")

    player = room.add_player(user_id=data.user_id, username=data.username)
    if player is None:
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
        raise HTTPException(status_code=404, detail="Room not found.")

    player = room.get_player(user_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found.")

    player.is_ready = True

    game_started = False
    if room.both_ready():
        game_started = room.start()
        if game_started:
            game = NoghteKhatGame(room)
            game.start_game()
            games[room_id] = game

    return {
        "success": True,
        "room_id": room.room_id,
        "user_id": user_id,
        "is_ready": player.is_ready,
        "players_ready": sum(1 for p in room.players if p.is_ready),
        "game_started": game_started,
    }


class DrawLineRequest(BaseModel):
    user_id: int
    line_id: str


@router.post("/rooms/{room_id}/draw")
def draw_line(room_id: str, data: DrawLineRequest):
    game = games.get(room_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found.")

    result = game.draw_line(data.user_id, data.line_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("reason", "invalid_move"))

    return {
        "success": True,
        "room_id": room_id,
        "result": result,
        "state": game.get_state(),
    }


@router.get("/rooms/{room_id}/game")
def get_game_state(room_id: str):
    game = games.get(room_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found.")

    return {
        "success": True,
        "room_id": room_id,
        "game": game.get_state(),
    }


@router.get("/rooms/{room_id}")
def get_room(room_id: str):
    room = rooms.get(room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found.")

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
