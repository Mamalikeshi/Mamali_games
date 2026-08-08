from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from games.hokm.player import Player
from games.hokm.room import Room
from games.hokm.game import HokmGame

router = APIRouter(prefix="/api/hokm", tags=["Hokm"])

rooms: dict[str, Room] = {}
games: dict[str, HokmGame] = {}

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

@router.post("/rooms/{room_id}/start")
def start_game(room_id: str):
    room = rooms.get(room_id)

    if room is None:
        raise HTTPException(
            status_code=404,
            detail="Room not found.",
        )

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

    if room.is_started:
        return {
            "success": True,
            "message": "Game already started.",
            "room_id": room.room_id,
        game = HokmGame(room)

started = game.start_game()

if not started:
    raise HTTPException(
        status_code=400,
        detail="Could not start Hokm game.",
    )

games[room_id] = game

return {
    "success": True,
    "room_id": room.room_id,
    "game_started": True,
    "current_turn": game.state.current_turn,
}
class TrumpRequest(BaseModel):
    user_id: int
    suit: str


class PlayCardRequest(BaseModel):
    user_id: int
    card_index: int


@router.post("/rooms/{room_id}/trump")
def choose_trump(room_id: str, data: TrumpRequest):
    game = games.get(room_id)

    if game is None:
        raise HTTPException(
            status_code=404,
            detail="Game not found.",
        )

    success = game.choose_trump(
        data.user_id,
        data.suit,
    )

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Cannot choose this trump.",
        )

    return {
        "success": True,
        "room_id": room_id,
        "trump": data.suit,
    }


@router.post("/rooms/{room_id}/play")
def play_card(
    room_id: str,
    data: PlayCardRequest,
):
    game = games.get(room_id)

    if game is None:
        raise HTTPException(
            status_code=404,
            detail="Game not found.",
        )

    success = game.play_card(
        data.user_id,
        data.card_index,
    )

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Cannot play this card.",
        )

    return {
        "success": True,
        "room_id": room_id,
        "state": game.get_state(),
    }
@router.get("/rooms/{room_id}/hand/{user_id}")
def get_player_hand(room_id: str, user_id: int):
    game = games.get(room_id)

    if game is None:
        raise HTTPException(
            status_code=404,
            detail="Game not found.",
        )

    player = game.get_player(user_id)

    if player is None:
        raise HTTPException(
            status_code=404,
            detail="Player not found.",
        )

    return {
        "success": True,
        "room_id": room_id,
        "user_id": user_id,
        "hand": [
            card.to_dict()
            for card in player.hand
        ],
    }
@router.get("/rooms/{room_id}/game")
def get_game_state(room_id: str):
    game = games.get(room_id)

    if game is None:
        raise HTTPException(
            status_code=404,
            detail="Game not found.",
        )

    state = game.get_state()

    return {
        "success": True,
        "room_id": room_id,
        "game": state,
    }
@router.get("/rooms/{room_id}/turn")
def get_turn(room_id: str):
    game = games.get(room_id)

    if game is None:
        raise HTTPException(
            status_code=404,
            detail="Game not found.",
        )

    return {
        "success": True,
        "room_id": room_id,
        "current_turn": game.state.current_turn,
        "trump": game.state.trump,
        "trick_cards": [
            {
                "user_id": user_id,
                "card": card.to_dict(),
            }
            for user_id, card in game.state.trick_cards
        ],
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
