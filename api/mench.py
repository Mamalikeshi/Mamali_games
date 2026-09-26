from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from games.mench.room import Room
from games.mench.game import MenchGame

router = APIRouter(prefix="/api/mench", tags=["Mench"])

rooms: dict[str, Room] = {}
games: dict[str, MenchGame] = {}


class CreateRoomRequest(BaseModel):
    user_id: int
    username: str
    max_players: int  # 2, 3, or 4


class JoinRoomRequest(BaseModel):
    user_id: int
    username: str


@router.post("/rooms")
def create_room(data: CreateRoomRequest):
    if data.max_players not in (2, 3, 4):
        raise HTTPException(status_code=400, detail="max_players must be 2, 3, or 4")

    room_id = f"mench-{len(rooms) + 1}"
    room = Room(room_id=room_id, max_players=data.max_players)
    player = room.add_player(user_id=data.user_id, username=data.username)
    if player is None:
        raise HTTPException(status_code=400, detail="Could not create room.")

    rooms[room_id] = room
    return {
        "success": True,
        "room_id": room_id,
        "your_color": player.color,
        "players": len(room.players),
        "max_players": room.max_players,
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
        "your_color": player.color,
        "players": len(room.players),
        "max_players": room.max_players,
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
    if room.all_ready():
        game_started = room.start()

    return {
        "success": True,
        "room_id": room.room_id,
        "user_id": user_id,
        "is_ready": player.is_ready,
        "players_ready": sum(1 for p in room.players if p.is_ready),
        "game_started": game_started,
    }


@router.post("/rooms/{room_id}/start")
def start_game(room_id: str):
    room = rooms.get(room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found.")

    if not room.all_ready():
        raise HTTPException(status_code=400, detail="All players must be ready.")

    game = MenchGame(room)
    started = game.start_game()
    if not started:
        raise HTTPException(status_code=400, detail="Could not start Mench game.")

    games[room_id] = game

    return {
        "success": True,
        "room_id": room.room_id,
        "game_started": True,
        "current_turn": game.state.current_turn,
    }


class RollDiceRequest(BaseModel):
    user_id: int


@router.post("/rooms/{room_id}/roll")
def roll_dice(room_id: str, data: RollDiceRequest):
    game = games.get(room_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found.")

    result = game.roll_dice(data.user_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("reason", "invalid_roll"))

    return {
        "success": True,
        "room_id": room_id,
        "result": result,
        "state": game.get_state(),
    }


class MovePieceRequest(BaseModel):
    user_id: int
    piece_id: str


@router.post("/rooms/{room_id}/move")
def move_piece(room_id: str, data: MovePieceRequest):
    game = games.get(room_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found.")

    result = game.move_piece(data.user_id, data.piece_id)
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
        "max_players": room.max_players,
        "players": [
            {
                "user_id": player.user_id,
                "username": player.username,
                "color": player.color,
                "is_ready": player.is_ready,
            }
            for player in room.players
        ],
        "is_full": room.is_full(),
        "is_started": room.is_started,
    }
