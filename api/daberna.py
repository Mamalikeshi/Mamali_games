from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from games.daberna.room import Room, VALID_ROOM_SIZES
from games.daberna.game import DabernaGame

router = APIRouter(prefix="/api/daberna", tags=["Daberna"])

rooms: dict[str, Room] = {}
games: dict[str, DabernaGame] = {}


class CreateRoomRequest(BaseModel):
    user_id: int
    username: str
    max_players: int  # 10, 20, or 30


class JoinRoomRequest(BaseModel):
    user_id: int
    username: str


@router.post("/rooms")
def create_room(data: CreateRoomRequest):
    if data.max_players not in VALID_ROOM_SIZES:
        raise HTTPException(status_code=400, detail="max_players must be 10, 20, or 30")

    room_id = f"daberna-{len(rooms) + 1}"
    room = Room(room_id=room_id, max_players=data.max_players)
    player = room.add_player(user_id=data.user_id, username=data.username)
    if player is None:
        raise HTTPException(status_code=400, detail="Could not create room.")

    rooms[room_id] = room
    return {
        "success": True,
        "room_id": room_id,
        "max_players": room.max_players,
        "current_players": len(room.players),
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
        "current_players": len(room.players),
        "max_players": room.max_players,
        "is_full": room.is_full(),
    }


@router.post("/rooms/{room_id}/cards/{user_id}")
def add_card(room_id: str, user_id: int):
    room = rooms.get(room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found.")

    player = room.get_player(user_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found.")

    card = player.add_card()
    if card is None:
        raise HTTPException(status_code=400, detail="You already have the maximum of 2 cards.")

    return {
        "success": True,
        "card_id": card.card_id,
        "grid": card.grid,
        "card_count": len(player.cards),
    }


@router.post("/rooms/{room_id}/ready/{user_id}")
def ready_player(room_id: str, user_id: int):
    room = rooms.get(room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found.")

    player = room.get_player(user_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found.")

    if len(player.cards) == 0:
        raise HTTPException(status_code=400, detail="You must take at least one card first.")

    player.is_ready = True

    game_started = False
    if room.all_ready():
        game_started = room.start()
        if game_started:
            game = DabernaGame(room)
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


@router.get("/rooms/{room_id}/cards/{user_id}")
def get_player_cards(room_id: str, user_id: int):
    game = games.get(room_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found.")

    cards = game.get_player_cards(user_id)
    if cards is None:
        raise HTTPException(status_code=404, detail="Player not found.")

    return {
        "success": True,
        "room_id": room_id,
        "user_id": user_id,
        "cards": cards,
    }


@router.get("/rooms/{room_id}")
def get_room(room_id: str):
    room = rooms.get(room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found.")

    return room.to_dict()
