from games.chahar_barg.game import ChaharBargGame
from api.chahar_barg_room import get_room, clear_active_room


games = {}


def start_chahar_barg(room_id: str):
    room = get_room(room_id)

    if room is None:
        return None

    if room_id in games:
        return games[room_id]

    game = ChaharBargGame(room)

    if not game.start_game():
        return None

    games[room_id] = game

    return game


def play_card(room_id: str, user_id: int, card_index: int):
    game = games.get(room_id)

    if game is None:
        return False

    return game.play_card(
        user_id,
        card_index,
    )


def choose_capture_option(room_id: str, user_id: int, option_id: int):
    game = games.get(room_id)

    if game is None:
        return False

    return game.choose_capture_option(
        user_id,
        option_id,
    )


def get_game_state(room_id: str, user_id: int = None):
    game = games.get(room_id)

    if game is None:
        return None

    if user_id is not None:
        game.state.touch(user_id)

    game.check_timeouts()

    state = game.get_state()

    if state.get("match_finished"):
        for player in game.room.players:
            clear_active_room(player.user_id)

    if user_id is not None:
        player = game.get_player(user_id)

        if player is not None:
            state["my_hand"] = player.hand_to_dict()

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
