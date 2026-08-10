from games.hokm.game import HokmGame
from api.room import rooms, get_room


games = {}


def start_hokm(room_id: str):
    room = get_room(room_id)

    if room is None:
        return None

    if room_id in games:
        return games[room_id]

    game = HokmGame(room)

    if not game.start_game():
        return None

    games[room_id] = game

    return game


def choose_trump(room_id: str, user_id: int, suit: str):
    game = games.get(room_id)

    if game is None:
        return False

    return game.choose_trump(
        user_id,
        suit,
    )


def play_card(
    room_id: str,
    user_id: int,
    card_index: int,
):
    game = games.get(room_id)

    if game is None:
        return False

    return game.play_card(
        user_id,
        card_index,
    )


def get_game_state(room_id: str):
    game = games.get(room_id)

    if game is None:
        return None

    return game.get_state()
