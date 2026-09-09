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

        if self.state is None:
            return False

        # -----------------------------------------------------
        # کارت بازی‌شده
        # -----------------------------------------------------

        played_card = self.pending_capture[
            "card"
        ]

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
        # حرکت دیگر در انتظار نیست.
        # -----------------------------------------------------

        self.pending_capture = None

        # -----------------------------------------------------
        # اعمال حرکت انتخاب‌شده
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
        card: Card,
        result: dict,
    ):

        if self.state is None:
            return

        self.state.cards_played_count += 1

        player = self.get_player(user_id)

        if player is None:
            return

        # -----------------------------------------------------
        # کارت بازی‌شده را از دست حذف می‌کنیم.
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

                # -----------------------------------------------
                # شکستن سور حریف:
                # اگه حریف تو همین دور سور داشته باشه، سور جدید ما
                # اول از امتیاز اون کم میشه. اگه امتیاز سور ما
                # بیشتر از سور حریف بود، مابه‌التفاوت برای خودمون
                # حساب میشه.
                # -----------------------------------------------

                opponent_id = self._other_player(
                    user_id
                ).user_id

                opponent_sour = (
                    self.state.sour_points.get(
                        opponent_id,
                        0,
                    )
                )

                if opponent_sour > 0:

                    if points <= opponent_sour:

                        self.state.sour_points[
                            opponent_id
                        ] = (
                            opponent_sour - points
                        )

                    else:

                        leftover = (
                            points - opponent_sour
                        )

                        self.state.sour_points[
                            opponent_id
                        ] = 0

                        self.state.sour_points[
                            user_id
                        ] = (
                            self.state.sour_points.get(
                                user_id,
                                0,
                            )
                            + leftover
                        )

                else:

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

            if (
                self.deck is not None
                and not self.deck.is_empty()
            ):

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

            self.state.set_turn(
                self._other_player(
                    user_id
                ).user_id
            )

    # =========================================================
    # پایان دور
    # =========================================================

    def _end_round(self):

        if self.state is None:
            return

        # -----------------------------------------------------
        # کارت‌های باقی‌مانده روی زمین به آخرین بازیکنی
        # که کارت جمع کرده تعلق می‌گیرد.
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
        # امتیاز عادی کارت‌ها
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

        # =====================================================
        # هفت‌خاج
        #
        # در کل دسته ۱۳ کارت گشنیز وجود دارد.
        #
        # هر بازیکنی که تعداد بیشتری گشنیز جمع کرده باشد
        # ۷ امتیاز می‌گیرد.
        #
        # خود ۷ گشنیز امتیاز جداگانه ندارد.
        # =====================================================

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

                round_points[user_id] += (
                    sour_earned
                )

        # -----------------------------------------------------
        # اضافه کردن امتیاز دور به امتیاز کل
        # -----------------------------------------------------

        for user_id, points in (
            round_points.items()
        ):

            self.total_score[user_id] += (
                points
            )

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

            "round_points": dict(
                round_points
            ),

            "total_score": dict(
                self.total_score
            ),

            "clubs": {
                self.player_a.user_id:
                    player_a_clubs,

                self.player_b.user_id:
                    player_b_clubs,
            },
        }

        # -----------------------------------------------------
        # دور فعلی تمام شد.
        # -----------------------------------------------------

        self.state.round_over = True

        # =====================================================
        # بررسی پایان کل مسابقه
        # =====================================================

        if (
            max(self.total_score.values())
            >= MATCH_TARGET_SCORE
        ):

            self.match_finished = True

            self.match_winner = max(
                self.total_score,
                key=self.total_score.get,
            )

            # -------------------------------------------------
            # اگر امتیاز مساوی شد، برنده نداریم.
            # -------------------------------------------------

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

        # =====================================================
        # شروع دور بعد
        # =====================================================

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
    # آیا انتخاب ترکیب 11 در انتظار است؟
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
    # دریافت گزینه‌های انتخاب 11
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

        for option in (
            self.pending_capture["options"]
        ):

            options.append(
                {
                    "option_id": option[
                        "option_id"
                    ],

                    "played_card": (
                        option[
                            "played_card"
                        ].to_dict()
                    ),

                    "table_cards": [
                        card.to_dict()
                        for card in option[
                            "table_cards"
                        ]
                    ],

                    "captured": [
                        card.to_dict()
                        for card in option[
                            "captured"
                        ]
                    ],

                    "remaining_table": [
                        card.to_dict()
                        for card in option[
                            "remaining_table"
                        ]
                    ],

                    "is_sour": option[
                        "is_sour"
                    ],

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
                "user_id":
                    self.pending_capture[
                        "user_id"
                    ],

                "card_index":
                    self.pending_capture[
                        "card_index"
                    ],

                "card":
                    self.pending_capture[
                        "card"
                    ].to_dict(),

                "options":
                    self.get_capture_options(
                        self.pending_capture[
                            "user_id"
                        ]
                    ),
            }

        return {
            "state": self.state.to_dict(),

            "player_a":
                self.player_a.to_dict(),

            "player_b":
                self.player_b.to_dict(),

            "deck_remaining":
                self.deck.remaining(),

            "round_number":
                self.round_number,

            "total_score":
                dict(
                    self.total_score
                ),

            "match_finished":
                self.match_finished,

            "match_winner":
                self.match_winner,

            "last_round_summary":
                self.last_round_summary,

            "pending_capture":
                pending_capture,
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

    # =========================================================
    # تایمر نوبت و تشخیص قطع ارتباط
    # =========================================================

    def check_timeouts(self):

        if self.match_finished:
            return

        if self.state is None:
            return

        # ۱. اگه بازیکنی بیشتر از ۶۰ ثانیه پیداش نبوده، ببازونش
        for player in self.room.players:

            last = self.state.last_seen.get(
                player.user_id
            )

            if last is None:
                continue

            if (
                time.time() - last
                > DISCONNECT_TIMEOUT_SECONDS
            ):

                opponent = self._other_player(
                    player.user_id
                )

                self.match_finished = True
                self.match_winner = opponent.user_id

                return

        # ۲. اگه نوبت کسی بیشتر از ۲۰ ثانیه طول کشیده، خودکار براش بازی کن
        if self.state.turn_started_at is None:
            return

        elapsed = (
            time.time()
            - self.state.turn_started_at
        )

        if elapsed <= TURN_TIMEOUT_SECONDS:
            return

        self._auto_play_for_current_turn()

    def _auto_play_for_current_turn(self):

        if self.state is None:
            return

        current_turn = self.state.current_turn

        if current_turn is None:
            return

        # اگه منتظر انتخاب ترکیب ۱۱ بود، خودکار اولین گزینه رو انتخاب کن
        if (
            self.pending_capture is not None
            and self.pending_capture["user_id"]
            == current_turn
        ):

            self.choose_capture_option(
                current_turn,
                0,
            )

            return

        player = self.get_player(current_turn)

        if player is None or not player.hand:
            return

        self.play_card(current_turn, 0)

    def forfeit(self, user_id: int):

        if self.match_finished:
            return False

        opponent = self._other_player(user_id)

        if opponent is None:
            return False

        self.match_finished = True
        self.match_winner = opponent.user_id

        return True
