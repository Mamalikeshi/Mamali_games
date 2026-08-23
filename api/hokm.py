from games.hokm.game import HokmGame
from api.room import rooms, get_room, clear_active_room


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


def get_game_state(room_id: str, user_id: int = None):
    game = games.get(room_id)

    if game is None:
        return None

    if user_id is not None:
        game.state.touch(user_id)

    game.check_timeouts()

    state = game.get_state()

    if state.get("winner") is not None:
        for player in game.room.players:
            clear_active_room(player.user_id)

    if user_id is not None:
        player = game.get_player(user_id)

        if player is not None:
            state["my_hand"] = [
                card.to_dict() for card in player.hand
            ]
            state["my_is_hokm"] = player.is_hokm

    return state


def forfeit_game(room_id: str, user_id: int):
    game = games.get(room_id)

    if game is None:
        return False

    success = game.forfeit(user_id)

    if success:
        for player in game.room.players:
            clear_active_room(player.user_id)

    return success
