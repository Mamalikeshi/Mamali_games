"""
Domino API - 2 Player

Handles:
- Room creation
- Joining
- Ready
- Starting game
- Playing tiles
- Drawing tiles
- Passing
- Starting next round
- Game state
- Player hand
- Playable tiles
- Scores
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from games.domino.game import DominoGame
from games.domino.player import Player
from games.domino.room import Room


router = APIRouter(
    prefix="/api/domino",
    tags=["domino"],
)


# =========================================================
# In-memory storage
# =========================================================

rooms: dict[str, Room] = {}
games: dict[str, DominoGame] = {}


# =========================================================
# Request models
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
# Helpers
# =========================================================

def _next_room_id() -> str:

    number = 1

    while True:

        room_id = f"domino-{number}"

        if room_id not in rooms:
            return room_id

        number += 1


def _get_room(room_id: str) -> Room:

    room = rooms.get(room_id)

    if room is None:
        raise HTTPException(
            status_code=404,
            detail="Room not found.",
        )

    return room


def _get_game(room_id: str) -> DominoGame:

    game = games.get(room_id)

    if game is None:
        raise HTTPException(
            status_code=404,
            detail="Game not started.",
        )

    return game


def _start_domino_game(
    room: Room,
) -> DominoGame:

    if len(room.players) != 2:

        raise HTTPException(
            status_code=400,
            detail="Domino requires exactly 2 players.",
        )

    existing_game = games.get(
        room.room_id
    )

    if existing_game is not None:
        return existing_game

    game = DominoGame(room)

    started = game.start_game()

    if not started:

        raise HTTPException(
            status_code=400,
            detail="Unable to start domino game.",
        )

    room.start()

    games[room.room_id] = game

    return game


def _serialize_tile(tile):

    if tile is None:
        return None

    if hasattr(tile, "to_dict"):
        return tile.to_dict()

    if hasattr(tile, "left") and hasattr(tile, "right"):

        return {
            "left": tile.left,
            "right": tile.right,
        }

    return {
        "left": tile.a,
        "right": tile.b,
    }


# =========================================================
# Create room
# =========================================================

@router.post("/rooms")
def create_room(
    request: CreateRoomRequest,
):

    if request.user_id <= 0:

        raise HTTPException(
            status_code=400,
            detail="Invalid user_id.",
        )

    room_id = _next_room_id()

    room = Room(
        room_id=room_id
    )

    player = Player(
        user_id=request.user_id,
        username=request.username,
    )

    room.add_player(player)

    rooms[room_id] = room

    return {
        "room_id": room_id,
        "player_id": request.user_id,
        "message": "Room created.",
    }


# =========================================================
# Get room
# =========================================================

@router.get("/rooms/{room_id}")
def get_room(
    room_id: str,
):

    room = _get_room(room_id)

    players = []

    for player in room.players:

        players.append({
            "user_id": player.user_id,
            "username": player.username,
            "is_ready": getattr(
                player,
                "is_ready",
                False,
            ),
        })

    return {
        "room_id": room.room_id,
        "players": players,
        "player_count": len(
            room.players
        ),
        "is_started": room.is_started,
        "game_exists": (
            room.room_id in games
        ),
    }


# =========================================================
# Join room
# =========================================================

@router.post("/rooms/{room_id}/join")
def join_room(
    room_id: str,
    request: JoinRoomRequest,
):

    room = _get_room(room_id)

    if room.is_started:

        raise HTTPException(
            status_code=400,
            detail="Game already started.",
        )

    existing = room.get_player(
        request.user_id
    )

    if existing is not None:

        return {
            "room_id": room_id,
            "player_id": request.user_id,
            "message": "Player already in room.",
        }

    if len(room.players) >= 2:

        raise HTTPException(
            status_code=400,
            detail="Room is full.",
        )

    player = Player(
        user_id=request.user_id,
        username=request.username,
    )

    room.add_player(player)

    return {
        "room_id": room_id,
        "player_id": request.user_id,
        "message": "Player joined.",
    }


# =========================================================
# Ready
# =========================================================

@router.post(
    "/rooms/{room_id}/ready/{user_id}"
)
def ready_player(
    room_id: str,
    user_id: int,
):

    room = _get_room(room_id)

    player = room.get_player(
        user_id
    )

    if player is None:

        raise HTTPException(
            status_code=404,
            detail="Player not found in room.",
        )

    if not hasattr(
        player,
        "is_ready",
    ):

        player.is_ready = False

    player.is_ready = True

    game_started = False

    if (
        len(room.players) == 2
        and room.both_ready()
    ):

        _start_domino_game(room)

        game_started = True

    return {
        "room_id": room_id,
        "user_id": user_id,
        "is_ready": True,
        "game_started": game_started,
    }


# =========================================================
# Start game manually
# =========================================================

@router.post(
    "/rooms/{room_id}/start"
)
def start_game(
    room_id: str,
):

    room = _get_room(room_id)

    if room.room_id in games:

        game = games[room.room_id]

        return {
            "room_id": room_id,
            "started": True,
            "state": game.get_state(),
        }

    if len(room.players) != 2:

        raise HTTPException(
            status_code=400,
            detail="Domino requires exactly 2 players.",
        )

    game = _start_domino_game(room)

    return {
        "room_id": room_id,
        "started": True,
        "state": game.get_state(),
    }


# =========================================================
# Get game
# =========================================================

@router.get(
    "/rooms/{room_id}/game"
)
def get_game(
    room_id: str,
):

    game = _get_game(room_id)

    return {
        "room_id": room_id,
        "game": game.get_state(),
    }


# =========================================================
# Play tile
# =========================================================

@router.post(
    "/rooms/{room_id}/play"
)
def play_tile(
    room_id: str,
    request: PlayTileRequest,
):

    game = _get_game(room_id)

    success = game.play_tile(
        user_id=request.user_id,
        tile_index=request.tile_index,
        side=request.side,
    )

    if not success:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unable to play tile. "
                "Check turn, tile and side."
            ),
        )

    return {
        "success": True,
        "game": game.get_state(),
    }


# =========================================================
# Draw tile
# =========================================================

@router.post(
    "/rooms/{room_id}/draw/{user_id}"
)
def draw_tile(
    room_id: str,
    user_id: int,
):

    game = _get_game(room_id)

    tile = game.draw_tile(
        user_id
    )

    if tile is None:

        raise HTTPException(
            status_code=400,
            detail=(
                "Cannot draw a tile. "
                "You may have a playable tile, "
                "it may not be your turn, "
                "or the boneyard may be empty."
            ),
        )

    return {
        "success": True,
        "tile": _serialize_tile(tile),
        "game": game.get_state(),
    }


# =========================================================
# Pass
# =========================================================

@router.post(
    "/rooms/{room_id}/pass/{user_id}"
)
def pass_turn(
    room_id: str,
    user_id: int,
):

    game = _get_game(room_id)

    success = game.pass_turn(
        user_id
    )

    if not success:

        raise HTTPException(
            status_code=400,
            detail=(
                "Cannot pass. "
                "You may have a playable tile, "
                "the boneyard may not be empty, "
                "or it may not be your turn."
            ),
        )

    return {
        "success": True,
        "game": game.get_state(),
    }


# =========================================================
# Start next round
# =========================================================

@router.post(
    "/rooms/{room_id}/next-round"
)
def start_next_round(
    room_id: str,
):

    game = _get_game(room_id)

    if game.match_finished:

        raise HTTPException(
            status_code=400,
            detail="Match is already finished.",
        )

    if not game.round_finished:

        raise HTTPException(
            status_code=400,
            detail="Current round is not finished.",
        )

    started = game.start_next_round()

    if not started:

        raise HTTPException(
            status_code=400,
            detail="Unable to start next round.",
        )

    return {
        "success": True,
        "round_number":
            game.round_number,
        "game":
            game.get_state(),
    }


# =========================================================
# Player hand
# =========================================================

@router.get(
    "/rooms/{room_id}/hand/{user_id}"
)
def get_player_hand(
    room_id: str,
    user_id: int,
):

    game = _get_game(room_id)

    player = game.get_player(
        user_id
    )

    if player is None:

        raise HTTPException(
            status_code=404,
            detail="Player not found.",
        )

    return {
        "user_id": user_id,
        "hand": [
            _serialize_tile(tile)
            for tile in player.hand
        ],
    }


# =========================================================
# Playable tiles
# =========================================================

@router.get(
    "/rooms/{room_id}/playable/{user_id}"
)
def get_playable_tiles(
    room_id: str,
    user_id: int,
):

    game = _get_game(room_id)

    player = game.get_player(
        user_id
    )

    if player is None:

        raise HTTPException(
            status_code=404,
            detail="Player not found.",
        )

    playable = game.get_playable_tiles(
        user_id
    )

    indexes = []

    for index, tile in enumerate(
        player.hand
    ):

        if game.can_play_tile(tile):

            indexes.append(index)

    return {
        "user_id": user_id,
        "playable_indexes": indexes,
        "tiles": [
            _serialize_tile(tile)
            for tile in playable
        ],
    }


# =========================================================
# Score
# =========================================================

@router.get(
    "/rooms/{room_id}/score"
)
def get_score(
    room_id: str,
):

    game = _get_game(room_id)

    return {
        "room_id": room_id,
        "scores": game.get_scores(),
        "target": game.get_state()[
            "match_target_score"
        ],
        "round_number":
            game.round_number,
        "round_finished":
            game.round_finished,
        "round_winner":
            game.round_winner,
        "match_finished":
            game.match_finished,
        "match_winner":
            game.match_winner,
    }
