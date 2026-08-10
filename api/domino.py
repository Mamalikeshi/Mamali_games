from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from games.domino.player import Player
from games.domino.room import Room
from games.domino.game import DominoGame

router = APIRouter(prefix="/api/domino", tags=["Domino"])

rooms: dict[str, Room] = {}
games: dict[str, DominoGame] = {}


class CreateRoomRequest(BaseModel):
    user_id: int
    username: str


class JoinRoomRequest(BaseModel):
    user_id: int
    username: str


@router.post("/rooms")
def create_room(data: CreateRoomRequest):
    room_id = f"domino-{len(rooms) + 1}"
    room = Room(room_id=room_id)
    player = Player(user_id=data.user_id, username=data.username)
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
        raise HTTPException(status_code=404, detail="Room not found.")

    player = Player(user_id=data.user_id, username=data.username)
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
        raise HTTPException(status_code=404, detail="Room not found.")

    player = room.get_player(user_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found.")

    player.is_ready = True

    game_started = False
    if room.both_ready():
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

    if len(room.players) != 2:
        raise HTTPException(
            status_code=400,
            detail="Exactly 2 players are required.",
        )

    if not room.both_ready():
        raise HTTPException(
            status_code=400,
            detail="Both players must be ready.",
        )

    game = DominoGame(room)
    started = game.start_game()
    if not started:
        raise HTTPException(
            status_code=400,
            detail="Could not start Domino game.",
        )

    games[room_id] = game

    return {
        "success": True,
        "room_id": room.room_id,
        "game_started": True,
        "current_turn": game.state.current_turn,
        "required_starting_tile": (
            game.first_round_required_tile.to_dict()
            if game.first_round_required_tile
            else None
        ),
    }


class PlayTileRequest(BaseModel):
    user_id: int
    tile_index: int
    side: str


@router.post("/rooms/{room_id}/play")
def play_tile(room_id: str, data: PlayTileRequest):
    game = games.get(room_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found.")

    result = game.play_tile(data.user_id, data.tile_index, data.side)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("reason", "invalid_move"))

    return {
        "success": True,
        "room_id": room_id,
        "result": result,
        "state": game.get_state(),
    }


@router.post("/rooms/{room_id}/draw/{user_id}")
def draw_tile(room_id: str, user_id: int):
    game = games.get(room_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found.")

    result = game.draw_from_boneyard(user_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("reason", "cannot_draw"))

    return {
        "success": True,
        "room_id": room_id,
        "result": result,
        "state": game.get_state(),
    }


@router.get("/rooms/{room_id}/hand/{user_id}")
def get_player_hand(room_id: str, user_id: int):
    game = games.get(room_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found.")

    player = game.get_player(user_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found.")

    return {
        "success": True,
        "room_id": room_id,
        "user_id": user_id,
        "hand": player.hand_to_dict(),
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


@router.get("/rooms/{room_id}/score")
def get_score(room_id: str):
    game = games.get(room_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found.")

    return {
        "success": True,
        "room_id": room_id,
        "scores": game.get_scores(),
        "winner": game.get_winner(),
        "game_finished": game.is_finished(),
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
