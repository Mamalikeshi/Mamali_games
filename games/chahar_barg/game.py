"""
Main game engine for Chahar Barg (Four Leaves / Yazdah) - 2 player mode.
Fully independent from other games (per project rule).

قوانین کلی مسابقه:
- هر دور تا تمام‌شدن کارت‌ها (کل دسته ۵۲تایی) ادامه دارد.
- شروع‌کننده‌ی دور اول تصادفی است.
- از دور دوم به بعد، شروع‌کننده برعکس دور قبل می‌شود.
- ۸ برگ آخر هر دور سور ندارد.
- اگر امتیاز کل یک بازیکن قبل از این دور به ۵۰ رسیده باشد،
  سور این دور برای او حساب نمی‌شود.
- بازی تا وقتی ادامه دارد که یکی از بازیکنان به ۶۲ امتیاز برسد.
"""

import random

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
        # وقتی چند ترکیب برای 11 وجود داشته باشد،
        # حرکت اینجا ذخیره می‌شود تا بازیکن انتخاب کند.
        #
        # ساختار:
        #
        # {
        #     "user_id": int,
        #     "card_index": int,
        #     "card": Card,
        #     "options": [...]
        # }
        # -----------------------------------------------------

        self.pending_capture: dict | None = None

    # =========================================================
    # شروع مسابقه
    # =========================================================

    def start_game(self) -> bool:

        if len(self.room.players) != 2:
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

    def _start_round(self, starter_user_id: int):

        self.round_number += 1

        self.last_round_starter = starter_user_id

        self.deck = Deck()
        self.deck.shuffle()

        self.player_a.hand = []
        self.player_a.captured = []

        self.player_b.hand = []
        self.player_b.captured = []

        self.state = ChaharBargState()

        self.pending_capture = None

        # چهار کارت اولیه روی زمین
        self.state.table_cards = self.deck.draw(4)

        # چهار کارت برای هر بازیکن
        self._deal_hands()

        # شروع نوبت
        self.state.current_turn = starter_user_id

    # =========================================================
    # پخش چهار کارت
    # =========================================================

    def _deal_hands(self):

        self.player_a.add_to_hand(
            self.deck.draw(4)
        )

        self.player_b.add_to_hand(
            self.deck.draw(4)
        )

        # اگر بعد از پخش این دست کارت دیگری
        # در دسته باقی نمانده باشد، این آخرین پخش است.
        if self.deck.is_empty():
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
    # بازی کردن یک کارت
    # =========================================================

    def play_card(
        self,
        user_id: int,
        card_index: int,
    ) -> bool:

        # -----------------------------------------------------
        # بازی تمام شده
        # -----------------------------------------------------

        if self.match_finished:
            return False

        # -----------------------------------------------------
        # اگر بازیکن هنوز در حال انتخاب ترکیب 11 است،
        # اجازه بازی کارت جدید ندارد.
        # -----------------------------------------------------

        if self.pending_capture is not None:
            return False

        # -----------------------------------------------------
        # بررسی نوبت
        # -----------------------------------------------------

        if self.state is None:
            return False

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
        # کارت را فعلاً از دست بازیکن حذف نمی‌کنیم.
        #
        # اگر چند حالت 11 وجود داشته باشد،
        # بازیکن باید ابتدا انتخاب کند.
        # -----------------------------------------------------

        card = player.hand[card_index]

        result = resolve_move(
            card,
            self.state.table_cards,
        )

        # =====================================================
        # چند حالت مختلف برای 11
        # =====================================================

        if result.get("requires_selection", False):

            self.pending_capture = {
                "user_id": user_id,
                "card_index": card_index,
                "card": card,
                "options": result["capture_options"],
            }

            # زمین و دست بازیکن هنوز تغییر نکرده‌اند.

            return True

        # =====================================================
        # حالت عادی
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
        # باید حرکتی در انتظار انتخاب باشد.
        # -----------------------------------------------------

        if self.pending_capture is None:
            return False

        # -----------------------------------------------------
        # فقط همان بازیکنی که کارت را بازی کرده
        # اجازه انتخاب دارد.
        # -----------------------------------------------------

        if self.pending_capture["user_id"] != user_id:
            return False

        # -----------------------------------------------------
        # اعتبار option_id
        # -----------------------------------------------------

        options = self.pending_capture["options"]

        if (
            option_id < 0
            or option_id >= len(options)
        ):
            return False

        if self.state is None:
            return False

        # -----------------------------------------------------
        # اطلاعات حرکت در انتظار
        # -----------------------------------------------------

        played_card = self.pending_capture["card"]

        # -----------------------------------------------------
        # اعمال انتخاب
        # -----------------------------------------------------

        result = apply_capture_option(
            played_card,
            self.state.table_cards,
            option_id,
        )

        if result is None:
            return False

        # -----------------------------------------------------
        # ابتدا حرکت در انتظار را پاک می‌کنیم.
        # -----------------------------------------------------

        self.pending_capture = None

        # -----------------------------------------------------
        # سپس حرکت را اعمال می‌کنیم.
        # -----------------------------------------------------

        self._apply_move(
            user_id,
            played_card,
            result,
        )

        return True

    # =========================================================
    # اعمال حرکت
    # =========================================================

    def _apply_move(
        self,
        user_id: int,
        card,
        result: dict,
    ):

        if self.state is None:
            return

        player = self.get_player(user_id)

        if player is None:
            return

        # -----------------------------------------------------
        # کارت بازی‌شده را از دست بازیکن حذف می‌کنیم.
        # -----------------------------------------------------

        player.remove_from_hand(card)

        # -----------------------------------------------------
        # اگر کارت چیزی را جمع کرده باشد
        # -----------------------------------------------------

        if result["captured"]:

            player.capture(
                result["captured"]
            )

            self.state.last_capturer = user_id

            # -------------------------------------------------
            # سور
            # -------------------------------------------------

            if (
                result["is_sour"]
                and not self.state.is_final_deal
            ):

                points = (
                    SOUR_JACK_POINTS
                    if result["is_jack_sweep"]
                    else SOUR_NORMAL_POINTS
                )

                self.state.sour_points[user_id] = (
                    self.state.sour_points.get(
                        user_id,
                        0,
                    )
                    + points
                )

        # -----------------------------------------------------
        # به‌روزرسانی زمین
        # -----------------------------------------------------

        self.state.table_cards = (
            result["remaining_table"]
        )

        # -----------------------------------------------------
        # اگر هر دو بازیکن دستشان خالی شده باشد
        # -----------------------------------------------------

        if (
            len(self.player_a.hand) == 0
            and len(self.player_b.hand) == 0
        ):

            # -------------------------------------------------
            # هنوز کارت در دسته وجود دارد
            # -------------------------------------------------

            if not self.deck.is_empty():

                self._deal_hands()

            # -------------------------------------------------
            # کل دسته تمام شده
            # -------------------------------------------------

            else:

                self._end_round()

        # -----------------------------------------------------
        # اگر دور تمام نشده، نوبت بازیکن مقابل است.
        # -----------------------------------------------------

        if (
            not self.match_finished
            and self.state is not None
            and not self.state.round_over
        ):

            self.state.current_turn = (
                self._other_player(user_id).user_id
            )

    # =========================================================
    # پایان دور
    # =========================================================

    def _end_round(self):

        if self.state is None:
            return

        # -----------------------------------------------------
        # کارت‌های باقی‌مانده روی زمین به آخرین جمع‌کننده
        # تعلق می‌گیرد.
        # -----------------------------------------------------

        if (
            self.state.table_cards
            and self.state.last_capturer is not None
        ):

            capturer = self.get_player(
                self.state.last_capturer
            )

            if capturer is not None:

                capturer.capture(
                    self.state.table_cards
                )

            self.state.table_cards = []

        # -----------------------------------------------------
        # امتیاز کارت‌ها
        # -----------------------------------------------------

        round_points = {
            self.player_a.user_id:
                tally_round_score(
                    self.player_a.captured
                ),

            self.player_b.user_id:
                tally_round_score(
                    self.player_b.captured
                ),
        }

                # -----------------------------------------------------
        # هفت خاج
        #
        # هر بازیکنی که بیشترین تعداد کارت گشنیز
        # را در پایان دور جمع کرده باشد،
        # ۷ امتیاز هفت خاج می‌گیرد.
        # -----------------------------------------------------

        player_a_clubs = count_clubs(
            self.player_a.captured
        )

        player_b_clubs = count_clubs(
            self.player_b.captured
        )

        if player_a_clubs > player_b_clubs:

            round_points[
                self.player_a.user_id
            ] += HAFT_KHAJ_POINTS

        elif player_b_clubs > player_a_clubs:

            round_points[
                self.player_b.user_id
            ] += HAFT_KHAJ_POINTS
        # -----------------------------------------------------
        # امتیاز سور
        # -----------------------------------------------------

        for user_id in (
            self.player_a.user_id,
            self.player_b.user_id,
        ):

            sour_earned = (
                self.state.sour_points.get(
                    user_id,
                    0,
                )
            )

            if (
                sour_earned
                and self.total_score[user_id]
                < SOUR_DISABLE_THRESHOLD
            ):

                round_points[user_id] += sour_earned

        # -----------------------------------------------------
        # اضافه کردن امتیاز دور به امتیاز کل
        # -----------------------------------------------------

        for user_id, points in round_points.items():

            self.total_score[user_id] += points

        self.player_a.score = (
            self.total_score[
                self.player_a.user_id
            ]
        )

        self.player_b.score = (
            self.total_score[
                self.player_b.user_id
            ]
        )

        # -----------------------------------------------------
        # خلاصه دور
        # -----------------------------------------------------

        self.last_round_summary = {
            "round_number": self.round_number,
            "round_points": dict(round_points),
            "total_score": dict(
                self.total_score
            ),
        }

        # -----------------------------------------------------
        # دور فعلی تمام شد.
        # -----------------------------------------------------

        self.state.round_over = True

        # -----------------------------------------------------
        # بررسی پایان کل مسابقه
        # -----------------------------------------------------

        if (
            max(self.total_score.values())
            >= MATCH_TARGET_SCORE
        ):

            self.match_finished = True

            self.match_winner = max(
                self.total_score,
                key=self.total_score.get,
            )

            # اگر مساوی شد، برنده نداریم.
            if (
                self.total_score[
                    self.player_a.user_id
                ]
                ==
                self.total_score[
                    self.player_b.user_id
                ]
            ):

                self.match_winner = None

        # -----------------------------------------------------
        # شروع دور بعد
        # -----------------------------------------------------

        else:

            next_starter = (
                self._other_player(
                    self.last_round_starter
                ).user_id
            )

            self._start_round(
                next_starter
            )

    # =========================================================
    # آیا بازیکن در حال انتخاب ترکیب 11 است؟
    # =========================================================

    def has_pending_capture(
        self,
        user_id: int | None = None,
    ) -> bool:

        if self.pending_capture is None:
            return False

        if user_id is None:
            return True

        return (
            self.pending_capture["user_id"]
            == user_id
        )

    # =========================================================
    # دریافت گزینه‌های انتخاب
    # =========================================================

    def get_capture_options(
        self,
        user_id: int,
    ) -> list[dict]:

        if self.pending_capture is None:
            return []

        if (
            self.pending_capture["user_id"]
            != user_id
        ):
            return []

        options = []

        for option in self.pending_capture["options"]:

            options.append(
                {
                    "option_id": option["option_id"],
                    "played_card": (
                        option["played_card"].to_dict()
                    ),
                    "table_cards": [
                        card.to_dict()
                        for card in option["table_cards"]
                    ],
                    "captured": [
                        card.to_dict()
                        for card in option["captured"]
                    ],
                    "remaining_table": [
                        card.to_dict()
                        for card in option["remaining_table"]
                    ],
                    "is_sour": option["is_sour"],
                    "is_jack_sweep": option[
                        "is_jack_sweep"
                    ],
                }
            )

        return options

    # =========================================================
    # خروجی وضعیت بازی
    # =========================================================

    def get_state(self) -> dict:

        pending_capture = None

        if self.pending_capture is not None:

            pending_capture = {
                "user_id": self.pending_capture[
                    "user_id"
                ],

                "card_index": self.pending_capture[
                    "card_index"
                ],

                "card": self.pending_capture[
                    "card"
                ].to_dict(),

                "options": self.get_capture_options(
                    self.pending_capture[
                        "user_id"
                    ]
                ),
            }

        return {
            "state": self.state.to_dict(),

            "player_a": self.player_a.to_dict(),

            "player_b": self.player_b.to_dict(),

            "deck_remaining": (
                self.deck.remaining()
            ),

            "round_number": self.round_number,

            "total_score": dict(
                self.total_score
            ),

            "match_finished": (
                self.match_finished
            ),

            "match_winner": (
                self.match_winner
            ),

            "last_round_summary": (
                self.last_round_summary
            ),

            # -------------------------------------------------
            # اطلاعات انتخاب ترکیب 11
            # -------------------------------------------------

            "pending_capture": pending_capture,
        }

    # =========================================================
    # امتیازات
    # =========================================================

    def get_scores(self) -> dict:

        return dict(
            self.total_score
        )

    # =========================================================
    # برنده
    # =========================================================

    def get_winner(self) -> int | None:

        return self.match_winner

    # =========================================================
    # پایان بازی
    # =========================================================

    def is_finished(self) -> bool:

        return self.match_finished
