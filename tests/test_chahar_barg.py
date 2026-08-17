from games.chahar_barg.card import Card
from games.chahar_barg.room import Room
from games.chahar_barg.player import Player
from games.chahar_barg.game import ChaharBargGame


def make_card(suit: str, rank: str) -> Card:
    return Card(suit, rank)


def test_multiple_11_combinations_require_player_selection():
    room = Room(room_id="test-multiple-11")

    player1 = Player(
        user_id=1,
        username="player1",
    )

    player2 = Player(
        user_id=2,
        username="player2",
    )

    assert room.add_player(player1)
    assert room.add_player(player2)

    game = ChaharBargGame(room)

    # بازی را بدون وابستگی به کارت‌های تصادفی شروع می‌کنیم.
    assert game.start_game()

    # زمین را دستی تنظیم می‌کنیم:
    # 2 گشنیز + 2 دل
    game.state.table_cards = [
        make_card("clubs", "2"),
        make_card("hearts", "2"),
    ]

    # دست بازیکن اول را دستی تنظیم می‌کنیم:
    # 9 + چند کارت دیگر
    player1.hand = [
        make_card("spades", "9"),
        make_card("diamonds", "5"),
        make_card("clubs", "7"),
        make_card("hearts", "A"),
    ]

    # برای اینکه نوبت بازیکن اول باشد.
    game.state.current_turn = player1.user_id

    # بازیکن 9 را بازی می‌کند.
    assert game.play_card(
        player1.user_id,
        0,
    )

    # چون دو حالت مختلف برای 11 وجود دارد،
    # سیستم نباید خودش یکی را انتخاب کند.
    assert game.has_pending_capture(
        player1.user_id
    )

    # کارت 9 هنوز نباید از دست بازیکن حذف شده باشد.
    assert len(player1.hand) == 4

    # زمین هم هنوز نباید تغییر کرده باشد.
    assert len(game.state.table_cards) == 2

    # باید دقیقاً دو گزینه وجود داشته باشد:
    #
    # 9 + 2 گشنیز
    # 9 + 2 دل
    options = game.get_capture_options(
        player1.user_id
    )

    assert len(options) == 2

    # ---------------------------------------------------------
    # بازیکن گزینه اول را انتخاب می‌کند.
    # ---------------------------------------------------------

    assert game.choose_capture_option(
        player1.user_id,
        0,
    )

    # دیگر نباید انتخابی در انتظار باشد.
    assert not game.has_pending_capture()

    # کارت 9 باید از دست بازیکن خارج شده باشد.
    assert len(player1.hand) == 3

    # باید 9 و یکی از دو کارت 2 جمع شده باشند.
    assert len(player1.captured) == 2

    captured_ranks = {
        card.rank
        for card in player1.captured
    }

    assert "9" in captured_ranks
    assert "2" in captured_ranks

    # فقط یک کارت 2 روی زمین باقی مانده باشد.
    assert len(game.state.table_cards) == 1

    remaining_card = game.state.table_cards[0]

    assert remaining_card.rank == "2"


def test_single_11_combination_is_automatic():
    room = Room(room_id="test-single-11")

    player1 = Player(
        user_id=1,
        username="player1",
    )

    player2 = Player(
        user_id=2,
        username="player2",
    )

    assert room.add_player(player1)
    assert room.add_player(player2)

    game = ChaharBargGame(room)

    assert game.start_game()

    # فقط یک حالت برای 11 وجود دارد:
    #
    # 9 + 2 = 11
    game.state.table_cards = [
        make_card("clubs", "2"),
        make_card("hearts", "5"),
        make_card("spades", "7"),
    ]

    player1.hand = [
        make_card("diamonds", "9"),
    ]

    game.state.current_turn = player1.user_id

    assert game.play_card(
        player1.user_id,
        0,
    )

    # چون فقط یک حالت وجود دارد،
    # نباید منتظر انتخاب بازیکن بمانیم.
    assert not game.has_pending_capture()

    # 9 و 2 باید جمع شده باشند.
    assert len(player1.captured) == 2

    # 5 و 7 باید روی زمین باقی مانده باشند.
    assert len(game.state.table_cards) == 2

    assert all(
        card.rank in {"5", "7"}
        for card in game.state.table_cards
    )
