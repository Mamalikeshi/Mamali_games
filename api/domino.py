from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from games.domino.player import Player
from games.domino.room import Room
from games.domino.game import DominoGame


router = APIRouter(
    prefix="/api/domino",
    tags=["Domino"],
)


# =========================================================
# حافظه موقت
# =========================================================

rooms: dict[str, Room] = {}
games: dict[str, DominoGame] = {}


# =========================================================
# Request Models
# =========================================================

class CreateRoomRequest(BaseModel):
    user_id: int
    username: str


class JoinRoomRequest(BaseModel):
    user_id: int
    username: str


class PlayTileRequest(BaseModel):
    user_id: int
    tile_index: int
    side: str | None = None


# =========================================================
# ساخت شناسه اتاق
# =========================================================

def _next_room_id() -> str:
    number = 1

    while f"domino-{number}" in rooms:
        number += 1

    return f"domino-{number}"


# =========================================================
# شروع واقعی بازی
# =========================================================

def _start_domino_game(room: Room) -> DominoGame:

    if len(room.players) != 2:
        raise HTTPException(
            status_code=400,
            detail="Exactly 2 players are required.",
        )

    existing_game = games.get(room.room_id)

    if existing_game is not None:
        return existing_game

    game = DominoGame(room)

    started = game.start_game()

    if not started:
        raise HTTPException(
            status_code=400,
            detail="Could not start Domino game.",
        )

    # اتاق را هم به حالت شروع‌شده می‌بریم
    room.start()

    games[room.room_id] = game

    return game


# =========================================================
# ساخت اتاق
# =========================================================

@router.post("/rooms")
def create_room(data: CreateRoomRequest):

    room_id = _next_room_id()

    room = Room(room_id=room_id)

    player = Player(
        user_id=data.user_id,
        username=data.username,
    )

    if not room.add_player(player):
        raise HTTPException(
            status_code=400,
            detail="Could not add player to room.",
        )

    rooms[room_id] = room

    return {
        "success": True,
        "room_id": room_id,
        "players": len(room.players),
        "is_full": room.is_full(),
        "is_started": room.is_started,
    }


# =========================================================
# ورود بازیکن دوم
# =========================================================

@router.post("/rooms/{room_id}/join")
def join_room(
    room_id: str,
    data: JoinRoomRequest,
):

    room = rooms.get(room_id)

    if room is None:
        raise HTTPException(
            status_code=404,
            detail="Room not found.",
        )

    if room.is_started:
        raise HTTPException(
            status_code=400,
            detail="Game has already started.",
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
        "is_started": room.is_started,
    }


# =========================================================
# آماده شدن بازیکن
# =========================================================

@router.post("/rooms/{room_id}/ready/{user_id}")
def ready_player(
    room_id: str,
    user_id: int,
):

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

    if room.is_started:
        return {
            "success": True,
            "room_id": room.room_id,
            "user_id": user_id,
            "is_ready": player.is_ready,
            "players_ready": sum(
                1
                for p in room.players
                if p.is_ready
            ),
            "game_started": True,
        }

    player.is_ready = True

    game_started = False
    game = None

    # وقتی هر دو آماده شدند،
    # همان لحظه بازی واقعی ساخته می‌شود.
    if room.both_ready():

        game = _start_domino_game(room)

        game_started = True

    return {
        "success": True,
        "room_id": room.room_id,
        "user_id": user_id,
        "is_ready": player.is_ready,
        "players_ready": sum(
            1
            for p in room.players
            if p.is_ready
        ),
        "game_started": game_started,
        "current_turn": (
            game.state.current_turn
            if game is not None and game.state is not None
            else None
        ),
    }


# =========================================================
# شروع دستی بازی
# =========================================================

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

    game = _start_domino_game(room)

    return {
        "success": True,
        "room_id": room.room_id,
        "game_started": True,
        "current_turn": (
            game.state.current_turn
            if game.state is not None
            else None
        ),
        "required_starting_tile": (
            game.first_round_required_tile.to_dict()
            if getattr(
                game,
                "first_round_required_tile",
                None,
            )
            else None
        ),
    }


# =========================================================
# بازی کردن مهره
# =========================================================

@router.post("/rooms/{room_id}/play")
def play_tile(
    room_id: str,
    data: PlayTileRequest,
):

    game = games.get(room_id)

    if game is None:
        raise HTTPException(
            status_code=404,
            detail="Game not found.",
        )

    success = game.play_tile(
        user_id=data.user_id,
        tile_index=data.tile_index,
        side=data.side,
    )

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Invalid domino move.",
        )

    return {
        "success": True,
        "room_id": room_id,
        "action": "play",
        "state": game.get_state(),
    }


# =========================================================
# خرید یک مهره
# =========================================================

@router.post("/rooms/{room_id}/draw/{user_id}")
def draw_tile(
    room_id: str,
    user_id: int,
):

    game = games.get(room_id)

    if game is None:
        raise HTTPException(
            status_code=404,
            detail="Game not found.",
        )

    tile = game.draw_tile(user_id)

    if tile is None:
        raise HTTPException(
            status_code=400,
            detail="Cannot draw a tile.",
        )

    return {
        "success": True,
        "room_id": room_id,
        "action": "draw",
        "tile": tile.to_dict(),
        "state": game.get_state(),
    }


# =========================================================
# پاس
# =========================================================

@router.post("/rooms/{room_id}/pass/{user_id}")
def pass_turn(
    room_id: str,
    user_id: int,
):

    game = games.get(room_id)

    if game is None:
        raise HTTPException(
            status_code=404,
            detail="Game not found.",
        )

    success = game.pass_turn(user_id)

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Cannot pass.",
        )

    return {
        "success": True,
        "room_id": room_id,
        "action": "pass",
        "state": game.get_state(),
    }


# =========================================================
# دست بازیکن
# =========================================================

@router.get("/rooms/{room_id}/hand/{user_id}")
def get_player_hand(
    room_id: str,
    user_id: int,
):

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
        "hand": player.hand_to_dict(),
    }


# =========================================================
# مهره‌های قابل بازی
# =========================================================

@router.get("/rooms/{room_id}/playable/{user_id}")
def get_playable_tiles(
    room_id: str,
    user_id: int,
):

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

    playable = game.get_playable_tiles(user_id)

    playable_indexes = []

    for index, tile in enumerate(player.hand):

        if tile in playable:
            playable_indexes.append(index)

    return {
        "success": True,
        "room_id": room_id,
        "user_id": user_id,
        "playable_indexes": playable_indexes,
        "playable_tiles": [
            tile.to_dict()
            for tile in playable
        ],
    }


# =========================================================
# وضعیت کامل بازی
# =========================================================

@router.get("/rooms/{room_id}/game")
def get_game_state(room_id: str):

    game = games.get(room_id)

    if game is None:
        raise HTTPException(
            status_code=404,
            detail="Game not found.",
        )

    return {
        "success": True,
        "room_id": room_id,
        "game": game.get_state(),
    }


# =========================================================
# امتیاز
# =========================================================

@router.get("/rooms/{room_id}/score")
def get_score(room_id: str):

    game = games.get(room_id)

    if game is None:
        raise HTTPException(
            status_code=404,
            detail="Game not found.",
        )

    return {
        "success": True,
        "room_id": room_id,
        "scores": game.get_scores(),
        "winner": game.get_winner(),
        "game_finished": game.is_finished(),
    }


# =========================================================
# اطلاعات اتاق
# =========================================================

@router.get("/rooms/{room_id}")
def get_room(room_id: str):

    room = rooms.get(room_id)

    if room is None:
        raise HTTPException(
            status_code=404,
            detail="Room not found.",
        )

    return {
        "success": True,
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
        "game_exists": room_id in games,
    }
