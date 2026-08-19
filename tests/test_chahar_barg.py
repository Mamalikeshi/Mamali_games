from games.chahar_barg.card import Card
from games.chahar_barg.room import Room
from games.chahar_barg.player import Player
from games.chahar_barg.game import ChaharBargGame


def test_chahar_barg_multiple_11_options_require_player_selection():

    room = Room(room_id="test-chahar-barg")

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

    # ---------------------------------------------------------
    # ساخت وضعیت کنترل‌شده برای تست
    # ---------------------------------------------------------

    game.state.table_cards = [
        Card("clubs", "2"),
        Card("hearts", "2"),
        Card("spades", "7"),
    ]

    player1.hand = [
        Card("diamonds", "9"),
    ]

    player2.hand = []

    game.state.current_turn = player1.user_id

    # ---------------------------------------------------------
    # بازیکن 9 را بازی می‌کند.
    #
    # دو حالت مختلف برای 11 وجود دارد:
    #
    # 9 + 2 گشنیز
    # 9 + 2 دل
    #
    # بنابراین سیستم نباید خودش انتخاب کند.
    # ---------------------------------------------------------

    assert game.play_card(
        player1.user_id,
        0,
    )

    # ---------------------------------------------------------
    # باید حرکت در حالت انتظار انتخاب باشد.
    # ---------------------------------------------------------

    assert game.has_pending_capture(
        player1.user_id
    )

    # ---------------------------------------------------------
    # کارت 9 هنوز باید در دست بازیکن باشد.
    # ---------------------------------------------------------

    assert len(player1.hand) == 1

    assert (
        player1.hand[0].rank
        == "9"
    )

    # ---------------------------------------------------------
    # زمین هم نباید هنوز تغییر کرده باشد.
    # ---------------------------------------------------------

    assert len(game.state.table_cards) == 3

    # ---------------------------------------------------------
    # باید دقیقاً دو گزینه داشته باشیم.
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # دیگر نباید حرکت در انتظار باشد.
    # ---------------------------------------------------------

    assert not game.has_pending_capture()

    # ---------------------------------------------------------
    # کارت 9 باید از دست بازیکن خارج شده باشد.
    # ---------------------------------------------------------

    assert len(player1.hand) == 0

    # ---------------------------------------------------------
    # باید 9 و یکی از دو کارت 2 جمع شده باشند.
    # ---------------------------------------------------------

    assert len(player1.captured) == 2

    captured_ranks = [
        card.rank
        for card in player1.captured
    ]

    assert "9" in captured_ranks

    assert "2" in captured_ranks

    # ---------------------------------------------------------
    # یک کارت 2 باید روی زمین باقی مانده باشد.
    # ---------------------------------------------------------

    assert len(game.state.table_cards) == 1

    assert (
        game.state.table_cards[0].rank
        == "2"
    )

    # ---------------------------------------------------------
    # بعد از انتخاب، نوبت باید به بازیکن دوم برسد.
    # ---------------------------------------------------------

    assert (
        game.state.current_turn
        == player2.user_id
    )
def test_jack_captures_everything_except_king_and_queen():

    room = Room(room_id="test-jack")

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

    # ---------------------------------------------------------
    # کارت‌های روی زمین
    # ---------------------------------------------------------

    game.state.table_cards = [
        Card("clubs", "2"),
        Card("hearts", "7"),
        Card("spades", "J"),
        Card("diamonds", "K"),
        Card("hearts", "Q"),
    ]

    player1.hand = [
        Card("clubs", "J"),
    ]

    player2.hand = []

    game.state.current_turn = player1.user_id

    # ---------------------------------------------------------
    # بازیکن سرباز بازی می‌کند.
    # ---------------------------------------------------------

    assert game.play_card(
        player1.user_id,
        0,
    )

    # ---------------------------------------------------------
    # سرباز باید این کارت‌ها را جمع کرده باشد:
    #
    # 2 گشنیز
    # 7 دل
    # J پیک
    # J بازی‌شده
    #
    # شاه و بی‌بی نباید جمع شده باشند.
    # ---------------------------------------------------------

    assert len(player1.captured) == 4

    captured = [
        (card.suit, card.rank)
        for card in player1.captured
    ]

    assert ("clubs", "2") in captured
    assert ("hearts", "7") in captured
    assert ("spades", "J") in captured
    assert ("clubs", "J") in captured

    # ---------------------------------------------------------
    # شاه و بی‌بی باید روی زمین باقی مانده باشند.
    # ---------------------------------------------------------

    assert len(game.state.table_cards) == 2

    remaining = [
        (card.suit, card.rank)
        for card in game.state.table_cards
    ]

    assert ("diamonds", "K") in remaining
    assert ("hearts", "Q") in remaining
def test_king_and_queen_only_capture_same_rank():

    room = Room(room_id="test-king-queen")

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

    # ---------------------------------------------------------
    # تست شاه
    # ---------------------------------------------------------

    game.state.table_cards = [
        Card("clubs", "K"),
        Card("hearts", "7"),
        Card("spades", "Q"),
    ]

    player1.hand = [
        Card("diamonds", "K"),
    ]

    player2.hand = []

    game.state.current_turn = player1.user_id

    assert game.play_card(
        player1.user_id,
        0,
    )

    # شاه باید فقط شاه را جمع کرده باشد.
    assert len(player1.captured) == 2

    captured = [
        (card.suit, card.rank)
        for card in player1.captured
    ]

    assert ("clubs", "K") in captured
    assert ("diamonds", "K") in captured

    # 7 و Q باید روی زمین بمانند.
    assert len(game.state.table_cards) == 2

    remaining = [
        (card.suit, card.rank)
        for card in game.state.table_cards
    ]

    assert ("hearts", "7") in remaining
    assert ("spades", "Q") in remaining

    # ---------------------------------------------------------
    # تست بی‌بی
    # ---------------------------------------------------------

    game.state.table_cards = [
        Card("clubs", "Q"),
        Card("hearts", "5"),
        Card("spades", "K"),
    ]

    player1.hand = [
        Card("diamonds", "Q"),
    ]

    game.state.current_turn = player1.user_id

    assert game.play_card(
        player1.user_id,
        0,
    )

    # بی‌بی باید فقط بی‌بی را جمع کرده باشد.
    assert len(player1.captured) == 4

    captured = [
        (card.suit, card.rank)
        for card in player1.captured
    ]

    assert ("clubs", "Q") in captured
    assert ("diamonds", "Q") in captured

    # 5 و K باید باقی مانده باشند.
    assert len(game.state.table_cards) == 2

    remaining = [
        (card.suit, card.rank)
        for card in game.state.table_cards
    ]

    assert ("hearts", "5") in remaining
    assert ("spades", "K") in remaining
def test_normal_sour_gives_5_points():

    room = Room(room_id="test-normal-sour")

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

    # تمام زمین را طوری می‌چینیم که 9 + 2 = 11 شود.
    game.state.table_cards = [
        Card("clubs", "2"),
    ]

    player1.hand = [
        Card("hearts", "9"),
    ]

    player2.hand = []

    game.state.current_turn = player1.user_id

    # این دور آخرین پخش نیست.
    game.state.is_final_deal = False

    assert game.play_card(
        player1.user_id,
        0,
    )

    # چون کل زمین با 9 جمع شده،
    # باید سور معمولی ثبت شده باشد.
    assert (
        game.state.sour_points[player1.user_id]
        == 5
    )
