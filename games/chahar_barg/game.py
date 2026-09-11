"""
Main game engine for Chahar Barg (Four Leaves / Yazdah) - 2 player mode.
Fully independent from other games (per project rule).

قوانین کلی مسابقه:
- هر دور تا تمام‌شدن کارت‌های دسته ادامه دارد.
- شروع‌کننده‌ی دور اول تصادفی است.
- از دور دوم به بعد، شروع‌کننده برعکس دور قبل می‌شود.
- ۸ برگ آخر هر دور سور ندارد.
- اگر امتیاز کل بازیکن قبل از شروع دور به ۵۰ رسیده باشد،
  سور آن دور برای او حساب نمی‌شود.
- بازی تا وقتی ادامه دارد که یکی از بازیکنان به ۶۲ امتیاز برسد.
- هفت‌خاج:
  هر بازیکنی که در پایان دور تعداد بیشتری از ۱۳ کارت
  گشنیز را جمع کرده باشد، ۷ امتیاز می‌گیرد.
"""

import random
import time

from games.chahar_barg.card import Card
from games.chahar_barg.deck import Deck
from games.chahar_barg.state import ChaharBargState
from games.chahar_barg.rules import (
    resolve_move,
    apply_capture_option,
    tally_round_score,
    count_clubs,
    SOUR_NORMAL_POINTS,
    SOUR_JACK_POINTS,
    SOUR_DISABLE_THRESHOLD,
    MATCH_TARGET_SCORE,
)
from games.chahar_barg.room import Room
from games.chahar_barg.player import Player


HAFT_KHAJ_POINTS = 7
TURN_TIMEOUT_SECONDS = 20
DISCONNECT_TIMEOUT_SECONDS = 60


class ChaharBargGame:

    def __init__(self, room: Room):

        self.room = room

        self.player_a: Player = room.players[0]
        self.player_b: Player = room.players[1]

        self.deck: Deck | None = None
        self.state: ChaharBargState | None = None

        self.total_score: dict[int, int] = {
            self.player_a.user_id: 0,
            self.player_b.user_id: 0,
        }

        self.round_number: int = 0

        self.last_round_starter: int | None = None

        self.match_finished: bool = False
        self.match_winner: int | None = None

        self.last_round_summary: dict | None = None

        # -----------------------------------------------------
        # وقتی چند ترکیب مختلف برای جمع 11 وجود داشته باشد،
        # حرکت تا انتخاب بازیکن در اینجا نگه داشته می‌شود.
        # -----------------------------------------------------

        self.pending_capture: dict | None = None

    # =========================================================
    # شروع مسابقه
    # =========================================================

    def start_game(self) -> bool:

        if len(self.room.players) != 2:
            return False

        if not self.room.start():
            return False

        starter = random.choice(
            [
                self.player_a.user_id,
                self.player_b.user_id,
            ]
        )

        self._start_round(starter)

        return True

    # =========================================================
    # شروع یک دور
    # =========================================================

    def _start_round(
        self,
        starter_user_id: int,
    ):

        self.round_number += 1

        self.last_round_starter = starter_user_id

        self.deck = Deck()
        self.deck.shuffle()

        # -----------------------------------------------------
        # پاک کردن دست و کارت‌های جمع‌شده دور قبلی
        # -----------------------------------------------------

        self.player_a.hand = []
        self.player_a.captured = []

        self.player_b.hand = []
        self.player_b.captured = []

        # -----------------------------------------------------
        # ساخت وضعیت جدید دور
        # -----------------------------------------------------

        self.state = ChaharBargState()

        self.pending_capture = None

        # -----------------------------------------------------
        # چهار کارت اولیه روی زمین
        # -----------------------------------------------------

        self.state.table_cards = self.deck.draw_no_jacks(4)

        # -----------------------------------------------------
        # چهار کارت برای هر بازیکن
        # -----------------------------------------------------

        self._deal_hands()

        # -----------------------------------------------------
        # تعیین شروع‌کننده
        # -----------------------------------------------------

        self.state.set_turn(starter_user_id)

    # =========================================================
    # پخش چهار کارت
    # =========================================================

    def _deal_hands(self):

        if self.deck is None:
            return

        self.player_a.add_to_hand(
            self.deck.draw(4)
        )

        self.player_b.add_to_hand(
            self.deck.draw(4)
        )

        # -----------------------------------------------------
        # اگر بعد از پخش این دست کارت دیگری در دسته نمانده
        # باشد، این آخرین دست ۸ کارتی است.
        # -----------------------------------------------------

        if self.deck.is_empty():

            if self.state is not None:
                self.state.is_final_deal = True

    # =========================================================
    # پیدا کردن بازیکن
    # =========================================================

    def get_player(
        self,
        user_id: int,
    ) -> Player | None:

        if self.player_a.user_id == user_id:
            return self.player_a

        if self.player_b.user_id == user_id:
            return self.player_b

        return None

    # =========================================================
    # بازیکن مقابل
    # =========================================================

    def _other_player(
        self,
        user_id: int,
    ) -> Player:

        if self.player_a.user_id == user_id:
            return self.player_b

        return self.player_a

    # =========================================================
    # بازی کردن کارت
    # =========================================================

    def play_card(
        self,
        user_id: int,
        card_index: int,
    ) -> bool:

        # -----------------------------------------------------
        # اگر کل مسابقه تمام شده باشد
        # -----------------------------------------------------

        if self.match_finished:
            return False

        # -----------------------------------------------------
        # اگر بازیکن هنوز در حال انتخاب ترکیب 11 باشد
        # اجازه بازی کارت جدید ندارد.
        # -----------------------------------------------------

        if self.pending_capture is not None:
            return False

        # -----------------------------------------------------
        # وضعیت بازی باید موجود باشد.
        # -----------------------------------------------------

        if self.state is None:
            return False

        # -----------------------------------------------------
        # بررسی نوبت
        # -----------------------------------------------------

        if self.state.current_turn != user_id:
            return False

        # -----------------------------------------------------
        # پیدا کردن بازیکن
        # -----------------------------------------------------

        player = self.get_player(user_id)

        if player is None:
            return False

        # -----------------------------------------------------
        # بررسی شماره کارت
        # -----------------------------------------------------

        if (
            card_index < 0
            or card_index >= len(player.hand)
        ):
            return False

        # -----------------------------------------------------
        # کارت را فعلاً از دست حذف نمی‌کنیم.
        #
        # اگر چند ترکیب برای 11 وجود داشته باشد،
        # ابتدا بازیکن باید انتخاب کند.
        # -----------------------------------------------------

        card = player.hand[card_index]

        result = resolve_move(
            card,
            self.state.table_cards,
        )

        # =====================================================
        # چند ترکیب برای 11
        # =====================================================

        if result.get(
            "requires_selection",
            False,
        ):

            self.pending_capture = {
                "user_id": user_id,
                "card_index": card_index,
                "card": card,
                "options": result[
                    "capture_options"
                ],
            }

            # -------------------------------------------------
            # زمین و دست بازیکن هنوز تغییر نکرده‌اند.
            # -------------------------------------------------

            return True

        # =====================================================
        # حرکت عادی
        # =====================================================

        self._apply_move(
            user_id,
            card,
            result,
        )

        return True

    # =========================================================
    # انتخاب ترکیب 11
    # =========================================================

    def choose_capture_option(
        self,
        user_id: int,
        option_id: int,
    ) -> bool:

        # -----------------------------------------------------
        # باید حرکت در انتظار انتخاب وجود داشته باشد.
        # -----------------------------------------------------

        if self.pending_capture is None:
            return False

        # -----------------------------------------------------
        # فقط همان بازیکن اجازه انتخاب دارد.
        # -----------------------------------------------------

        if (
            self.pending_capture["user_id"]
            != user_id
        ):
            return False

        # -----------------------------------------------------
        # بررسی option_id
        # -----------------------------------------------------

        options = self.pending_capture[
            "options"
        ]

        if (
            option_id < 0
            or option_id >= len(options)
        ):
            return False

        # -----------------------------------------------------
        # وضعیت بازی
        # -----------------------------------------------------
