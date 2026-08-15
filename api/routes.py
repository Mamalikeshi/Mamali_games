from fastapi import APIRouter
from pydantic import BaseModel

from api.room import create_room, join_room, get_room, mark_ready
from api.hokm import (
    start_hokm,
    choose_trump,
    play_card,
    get_game_state,
)
from api.profile import register_or_get_user, get_profile
from api.matchmaking import find_match, cancel_matchmaking


router = APIRouter()


class CreateRoomRequest(BaseModel):
    room_id: str


class ReadyRequest(BaseModel):
    room_id: str
    user_id: int


class MatchmakingRequest(BaseModel):
    user_id: int
    username: str


class RegisterUserRequest(BaseModel):
    telegram_id: int
    first_name: str = ""
    username: str = ""


class JoinRoomRequest(BaseModel):
    room_id: str
    user_id: int
    username: str


class StartGameRequest(BaseModel):
    room_id: str


class ChooseTrumpRequest(BaseModel):
    room_id: str
    user_id: int
    suit: str


class PlayCardRequest(BaseModel):
    room_id: str
    user_id: int
    card_index: int


@router.get("/api/status")
async def status():
    return {
        "project": "Mamali Games",
        "status": "online",
        "version": "0.1",
    }


@router.post("/api/room/create")
async def create_room_api(
    request: CreateRoomRequest,
):
    room = create_room(request.room_id)

    if room is None:
        return {
            "success": False,
            "error": "Room already exists",
        }

    return {
        "success": True,
        "room": room.to_dict(),
    }


@router.post("/api/room/join")
async def join_room_api(
    request: JoinRoomRequest,
):
    room = join_room(
        request.room_id,
        request.user_id,
        request.username,
    )

    if room is None:
        return {
            "success": False,
            "error": "Cannot join room",
        }

    return {
        "success": True,
        "room": room.to_dict(),
    }


@router.get("/api/room/{room_id}")
async def get_room_api(room_id: str):
    room = get_room(room_id)

    if room is None:
        return {
            "success": False,
            "error": "Room not found",
        }

    return {
        "success": True,
        "room": room.to_dict(),
    }


@router.post("/api/room/ready")
async def mark_ready_api(request: ReadyRequest):
    success = mark_ready(
        request.room_id,
        request.user_id,
    )

    if not success:
        return {
            "success": False,
            "error": "Cannot mark ready",
        }

    return {
        "success": True,
    }


@router.post("/api/game/start")
async def start_game_api(
    request: StartGameRequest,
):
    game = start_hokm(request.room_id)

    if game is None:
        return {
            "success": False,
            "error": "Cannot start game",
        }

    return {
        "success": True,
        "state": game.get_state(),
    }


@router.post("/api/game/trump")
async def choose_trump_api(
    request: ChooseTrumpRequest,
):
    success = choose_trump(
        request.room_id,
        request.user_id,
        request.suit,
    )

    if not success:
        return {
            "success": False,
            "error": "Cannot choose trump",
        }

    return {
        "success": True,
        "state": get_game_state(
            request.room_id,
            request.user_id,
        ),
    }


@router.post("/api/game/play")
async def play_card_api(
    request: PlayCardRequest,
):
    success = play_card(
        request.room_id,
        request.user_id,
        request.card_index,
    )

    if not success:
        return {
            "success": False,
            "error": "Invalid card move",
        }

    return {
        "success": True,
        "state": get_game_state(
            request.room_id,
            request.user_id,
        ),
    }


@router.get("/api/game/{room_id}")
async def get_game_api(room_id: str, user_id: int = None):
    state = get_game_state(room_id, user_id)

    if state is None:
        return {
            "success": False,
            "error": "Game not found",
        }

    return {
        "success": True,
        "state": state,
    }


@router.post("/api/profile/register")
async def register_user_api(request: RegisterUserRequest):
    user = await register_or_get_user(
        request.telegram_id,
        request.first_name,
        request.username,
    )

    return {
        "success": True,
        "profile": user,
    }


@router.get("/api/profile/{telegram_id}")
async def get_profile_api(telegram_id: int):
    profile = await get_profile(telegram_id)

    if profile is None:
        return {
            "success": False,
            "error": "User not found",
        }

    return {
        "success": True,
        "profile": profile,
    }


@router.post("/api/matchmaking/find")
async def matchmaking_find_api(request: MatchmakingRequest):
    result = find_match(
        request.user_id,
        request.username,
    )

    return {
        "success": True,
        **result,
    }


@router.post("/api/matchmaking/cancel")
async def matchmaking_cancel_api(request: MatchmakingRequest):
    cancel_matchmaking(request.user_id)

    return {
        "success": True,
    }
