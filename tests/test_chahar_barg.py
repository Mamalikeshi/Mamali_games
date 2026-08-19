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
