"""
Main game engine for Domino (Double-Six set) - 2 player mode.
Fully independent from other games (per project rule).

قوانین کلی:
- هر بازیکن ۷ مهره می‌گیرد.
- دست اول: پخش تکرار می‌شود تا حداقل یکی از دو بازیکن یک مهره جفت داشته باشد.
- صاحب بالاترین جفت شروع‌کننده است و باید همان جفت را اولین حرکت بازی کند.
- از حرکت دوم به بعد، هر مهره قابل‌بازی آزادانه قابل انداختن است.
- از دست دوم به بعد، شروع‌کننده برعکس دست قبل می‌شود.
- اگر بازیکنی مهره قابل‌بازی نداشته باشد، باید از Boneyard بکشد.
- اگر مهره کشیده‌شده قابل‌بازی باشد، بازیکن باید همان مهره را بلافاصله بازی کند.
- اگر فقط یک مهره در Boneyard باقی مانده باشد، آن مهره کشیده نمی‌شود.
- اگر هیچ‌کدام از بازیکنان نتوانند بازی کنند، دست بسته می‌شود.
- در دست بسته، بازیکنی که مجموع امتیاز مهره‌های دستش کمتر است برنده می‌شود.
- اولین بازیکنی که دستش تمام شود، برنده دست است.
- امتیاز مهره‌های دست حریف به برنده تعلق می‌گیرد.
- بازی تا ۱۰۱ امتیاز ادامه دارد.
"""

from games.domino.deck import Deck
from games.domino.state import DominoState
from games.domino.rules import (
    find_highest_double,
    hand_has_double,
    can_play_tile,
    valid_sides_for_tile,
    place_tile,
    TILES_PER_PLAYER,
    MATCH_TARGET_SCORE,
)
from games.domino.room import Room
from games.domino.player import Player
from games.domino.tile import Tile


class DominoGame:

    def __init__(self, room: Room):

        self.room = room

        self.player_a: Player = room.players[0]
        self.player_b: Player = room.players[1]

        self.deck: Deck | None = None
        self.state: DominoState | None = None

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
        # اگر بازیکن مهره‌ای از Boneyard بکشد که قابل بازی باشد،
        # باید همان مهره را بلافاصله بازی کند.
        #
        # مقدار:
        # user_id -> index of forced tile
        # -----------------------------------------------------

        self.pending_forced_tile_index: dict[
            int,
            int | None,
        ] = {}

        # -----------------------------------------------------
        # فقط برای اولین حرکت اولین دست.
        #
        # بالاترین جفتی که باعث شروع بازیکن شده،
        # باید اولین مهره‌ای باشد که بازی می‌کند.
        # -----------------------------------------------------

        self.first_round_required_tile: Tile | None = None

    # =========================================================
    # شروع مسابقه
    # =========================================================

    def start_game(self) -> bool:

        if len(self.room.players) != 2:
            return False

        self._start_round(
            starter_user_id=None,
            is_first_round=True,
        )

        return True

    # =========================================================
    # شروع یک دست
    # =========================================================

    def _start_round(
        self,
        starter_user_id: int | None,
        is_first_round: bool = False,
    ):

        self.round_number += 1

        self.first_round_required_tile = None

        # -----------------------------------------------------
        # پاک کردن دست قبلی
        # -----------------------------------------------------

        self.player_a.hand = []
        self.player_b.hand = []

        # =====================================================
        # دست اول
        #
        # تا وقتی حداقل یکی از بازیکنان جفت نداشته باشد،
        # دوباره پخش می‌کنیم.
        # =====================================================

        if is_first_round:

            while True:

                self.deck = Deck()
                self.deck.shuffle()

                dealt_a = self.deck.draw(
                    TILES_PER_PLAYER
                )

                dealt_b = self.deck.draw(
                    TILES_PER_PLAYER
                )

                if (
                    hand_has_double(dealt_a)
                    or hand_has_double(dealt_b)
                ):
                    self.player_a.add_to_hand(
                        dealt_a
                    )

                    self.player_b.add_to_hand(
                        dealt_b
                    )

                    break

        # =====================================================
        # دست‌های بعدی
        # =====================================================

        else:

            self.deck = Deck()
            self.deck.shuffle()

            self.player_a.add_to_hand(
                self.deck.draw(
                    TILES_PER_PLAYER
                )
            )

            self.player_b.add_to_hand(
                self.deck.draw(
                    TILES_PER_PLAYER
                )
            )

        # -----------------------------------------------------
        # ساخت state جدید
        # -----------------------------------------------------

        self.state = DominoState()

        self.pending_forced_tile_index = {
            self.player_a.user_id: None,
            self.player_b.user_id: None,
        }

        # =====================================================
        # تعیین شروع‌کننده
        # =====================================================

        if is_first_round:

            hands = {
                self.player_a.user_id:
                    self.player_a.hand,

                self.player_b.user_id:
                    self.player_b.hand,
            }

            starter = find_highest_double(
                hands
            )

            starter_hand = hands[starter]

            highest_double_value = max(
                tile.left
                for tile in starter_hand
                if tile.is_double
            )

            self.first_round_required_tile = Tile(
                highest_double_value,
                highest_double_value,
            )

        else:

            starter = starter_user_id

        self.last_round_starter = starter

        self.state.current_turn = starter

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
    # آیا بازیکن حداقل یک مهره قابل بازی دارد؟
    # =========================================================

    def _player_can_play(
        self,
        player: Player,
    ) -> bool:

        if self.state is None:
            return False

        for tile in player.hand:

            if can_play_tile(
                tile,
                self.state.left_end,
                self.state.right_end,
            ):
                return True

        return False

    # =========================================================
    # کشیدن مهره از Boneyard
    # =========================================================

    def draw_from_boneyard(
        self,
        user_id: int,
    ) -> dict:

        if self.state is None:
            return {
                "success": False,
                "reason": "round_not_active",
            }

        if (
            self.match_finished
            or self.state.round_over
        ):
            return {
                "success": False,
                "reason": "round_not_active",
            }

        if (
            self.state.current_turn
            != user_id
        ):
            return {
                "success": False,
                "reason": "not_your_turn",
            }

        player = self.get_player(user_id)

        if player is None:
            return {
                "success": False,
                "reason": "player_not_found",
            }

        # -----------------------------------------------------
        # اگر مهره قابل بازی دارد،
        # نباید از Boneyard بکشد.
        # -----------------------------------------------------

        if self._player_can_play(player):

            return {
                "success": False,
                "reason": "you_have_a_playable_tile",
            }

        # -----------------------------------------------------
        # اگر فقط یک مهره باقی مانده،
        # آن را نمی‌کشیم.
        # -----------------------------------------------------

        if self.deck.remaining() <= 1:

            self._pass_turn_or_check_blocked(
                user_id
            )

            return {
                "success": True,
                "drew_tile": False,
                "playable": False,
            }

        # -----------------------------------------------------
        # کشیدن یک مهره
        # -----------------------------------------------------

        drawn = self.deck.draw_one()

        player.add_to_hand(
            [drawn]
        )

        # -----------------------------------------------------
        # اگر مهره قابل بازی بود،
        # همان مهره اجباری می‌شود.
        # -----------------------------------------------------

        if can_play_tile(
            drawn,
            self.state.left_end,
            self.state.right_end,
        ):

            new_index = len(player.hand) - 1

            self.pending_forced_tile_index[
                user_id
            ] = new_index

            return {
                "success": True,
                "drew_tile": True,
                "playable": True,
                "forced_tile_index": new_index,
            }

        # -----------------------------------------------------
        # مهره قابل بازی نیست.
        #
        # بازیکن باید دوباره بکشد.
        # -----------------------------------------------------

        return {
            "success": True,
            "drew_tile": True,
            "playable": False,
        }

    # =========================================================
    # رد شدن نوبت / بررسی بسته شدن بازی
    # =========================================================

    def _pass_turn_or_check_blocked(
        self,
        from_user_id: int,
    ):

        other = self._other_player(
            from_user_id
        )

        self.state.current_turn = (
            other.user_id
        )

        # -----------------------------------------------------
        # اگر حریف هم مهره قابل بازی ندارد
        # و Boneyard دیگر قابل کشیدن نیست،
        # بازی بسته شده است.
        # -----------------------------------------------------

        if (
            not self._player_can_play(other)
            and self.deck.remaining() <= 1
        ):

            self._end_round_blocked()

    # =========================================================
    # پایان دست بسته
    # =========================================================

    def _end_round_blocked(self):

        self.state.is_blocked = True

        self._finish_round_with_lowest_hand()

    # =========================================================
    # انتخاب برنده دست بسته
    # =========================================================

    def _finish_round_with_lowest_hand(self):

        sum_a = (
            self.player_a.hand_pip_sum()
        )

        sum_b = (
            self.player_b.hand_pip_sum()
        )

        if sum_a < sum_b:

            winner = self.player_a
            points = sum_b

        elif sum_b < sum_a:

            winner = self.player_b
            points = sum_a

        else:

            winner = None
            points = 0

        self._close_round(
            winner.user_id
            if winner is not None
            else None,
            points,
        )

    # =========================================================
    # بازی کردن مهره
    # =========================================================

    def play_tile(
        self,
        user_id: int,
        tile_index: int,
        side: str,
    ) -> dict:

        if self.state is None:

            return {
                "success": False,
                "reason": "round_not_active",
            }

        if (
            self.match_finished
            or self.state.round_over
        ):

            return {
                "success": False,
                "reason": "round_not_active",
            }

        # -----------------------------------------------------
        # بررسی نوبت
        # -----------------------------------------------------

        if (
            self.state.current_turn
            != user_id
        ):

            return {
                "success": False,
                "reason": "not_your_turn",
            }

        player = self.get_player(
            user_id
        )

        if player is None:

            return {
                "success": False,
                "reason": "player_not_found",
            }

        # -----------------------------------------------------
        # بررسی index
        # -----------------------------------------------------

        if (
            tile_index < 0
            or tile_index >= len(player.hand)
        ):

            return {
                "success": False,
                "reason": "invalid_tile_index",
            }

        tile = player.hand[tile_index]

        # =====================================================
        # مهره اجباری کشیده‌شده
        # =====================================================

        forced_index = (
            self.pending_forced_tile_index.get(
                user_id
            )
        )

        if (
            forced_index is not None
            and tile_index != forced_index
        ):

            return {
                "success": False,
                "reason": "must_play_drawn_tile",
            }

        # =====================================================
        # اولین حرکت اولین دست
        #
        # حتماً باید بالاترین جفت بازی شود.
        # =====================================================

        if (
            self.round_number == 1
            and len(self.state.board) == 0
            and self.first_round_required_tile
            is not None
        ):

            if (
                tile
                != self.first_round_required_tile
            ):

                return {
                    "success": False,
                    "reason":
                        "must_play_starting_double",
                }

        # =====================================================
        # بررسی قابل بازی بودن روی سمت انتخاب‌شده
        # =====================================================

        valid_sides = valid_sides_for_tile(
            tile,
            self.state.left_end,
            self.state.right_end,
        )

        if side not in valid_sides:

            return {
                "success": False,
                "reason":
                    "tile_not_playable_on_this_side",
            }

        # =====================================================
        # قرار دادن مهره
        # =====================================================

        result = place_tile(
            tile,
            side,
            self.state.left_end,
            self.state.right_end,
        )

        player.remove_from_hand(
            tile
        )

        # -----------------------------------------------------
        # اضافه کردن به board
        # -----------------------------------------------------

        if (
            side == "left"
            or (
                self.state.left_end is None
                and self.state.right_end is None
            )
        ):

            self.state.board.insert(
                0,
                tile,
            )

        else:

            self.state.board.append(
                tile
            )

        # -----------------------------------------------------
        # به‌روزرسانی دو سر بازی
        # -----------------------------------------------------

        self.state.left_end = (
            result["new_left_end"]
        )

        self.state.right_end = (
            result["new_right_end"]
        )

        # -----------------------------------------------------
        # مهره اجباری دیگر اجباری نیست.
        # -----------------------------------------------------

        self.pending_forced_tile_index[
            user_id
        ] = None

        # =====================================================
        # آیا دست بازیکن خالی شده؟
        # =====================================================

        if len(player.hand) == 0:

            opponent = self._other_player(
                user_id
            )

            self._close_round(
                user_id,
                opponent.hand_pip_sum(),
            )

            return {
                "success": True,
                "round_over": True,
            }

        # =====================================================
        # ادامه بازی
        # =====================================================

        self._pass_turn_or_check_blocked(
            user_id
        )

        return {
            "success": True,
            "round_over": False,
        }

    # =========================================================
    # پایان دست و مسابقه
    # =========================================================

    def _close_round(
        self,
        winner_user_id: int | None,
        points: int,
    ):

        if winner_user_id is not None:

            self.total_score[
                winner_user_id
            ] += points

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

        self.last_round_summary = {

            "round_number":
                self.round_number,

            "winner_user_id":
                winner_user_id,

            "points_awarded":
                points,

            "was_blocked":
                self.state.is_blocked,

            "total_score":
                dict(self.total_score),
        }

        self.state.round_over = True

        # =====================================================
        # بررسی پایان کل مسابقه
        # =====================================================

        if (
            max(self.total_score.values())
            >= MATCH_TARGET_SCORE
        ):

            self.match_finished = True

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

            else:

                self.match_winner = max(
                    self.total_score,
                    key=self.total_score.get,
                )

        # =====================================================
        # شروع دست بعد
        # =====================================================

        else:

            next_starter = (
                self._other_player(
                    self.last_round_starter
                ).user_id
            )

            self._start_round(
                starter_user_id=next_starter
            )

    # =========================================================
    # خروجی وضعیت بازی برای فرانت‌اند
    # =========================================================

    def get_state(self) -> dict:

        return {

            "state":
                self.state.to_dict(),

            "player_a":
                self.player_a.to_dict(),

            "player_b":
                self.player_b.to_dict(),

            "boneyard_remaining":
                self.deck.remaining(),

            "round_number":
                self.round_number,

            "total_score":
                self.total_score,

            "match_finished":
                self.match_finished,

            "match_winner":
                self.match_winner,

            "last_round_summary":
                self.last_round_summary,

            "pending_forced_tile_index":
                self.pending_forced_tile_index,
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

    def get_winner(
        self,
    ) -> int | None:

        return self.match_winner

    # =========================================================
    # پایان بازی
    # =========================================================

    def is_finished(
        self,
    ) -> bool:

        return self.match_finished
