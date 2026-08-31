"""
Main game engine for Domino - 2 player mode.
Standard Double-Six Domino.

Rules:
- 2 players only.
- 28 tiles in the full set.
- Each player receives 7 tiles.
- Remaining tiles form the boneyard.
- A tile can be played when one side matches
  one of the two open ends of the board.
- If the player has no legal move, they draw
  from the boneyard until they can play or
  the boneyard becomes empty.
- If no legal move exists after the boneyard
  is empty, the player passes.
- A round ends when:
    1. A player has no tiles left, or
    2. Both players are blocked.
"""

from games.domino.deck import Deck
from games.domino.player import Player
from games.domino.room import Room
from games.domino.state import DominoState
from games.domino.tile import Tile


class DominoGame:

    def __init__(self, room: Room):

        self.room = room

        if len(room.players) != 2:
            raise ValueError(
                "Domino requires exactly 2 players."
            )

        self.player_a: Player = room.players[0]
        self.player_b: Player = room.players[1]

        self.deck: Deck | None = None
        self.state: DominoState | None = None

        self.match_finished: bool = False
        self.match_winner: int | None = None

        self.round_finished: bool = False
        self.round_winner: int | None = None

        self.last_round_summary: dict | None = None

    # =========================================================
    # شروع بازی
    # =========================================================

    def start_game(self) -> bool:

        if len(self.room.players) != 2:
            return False

        self.deck = Deck()
        self.deck.shuffle()

        self.state = DominoState()

        self.match_finished = False
        self.match_winner = None

        self.round_finished = False
        self.round_winner = None

        self.last_round_summary = None

        self.player_a.hand = []
        self.player_b.hand = []

        self._deal_initial_tiles()

        starter = self._choose_starter()

        self.state.current_turn = starter

        return True

    # =========================================================
    # پخش ۷ مهره برای هر بازیکن
    # =========================================================

    def _deal_initial_tiles(self):

        if self.deck is None:
            return

        self.player_a.add_to_hand(
            self.deck.draw(7)
        )

        self.player_b.add_to_hand(
            self.deck.draw(7)
        )

    # =========================================================
    # انتخاب شروع‌کننده
    #
    # بازیکنی که بزرگ‌ترین Double را دارد شروع می‌کند.
    # =========================================================

    def _choose_starter(self) -> int:

        player_a_double = self._highest_double(
            self.player_a.hand
        )

        player_b_double = self._highest_double(
            self.player_b.hand
        )

        if player_a_double is not None and player_b_double is None:
            return self.player_a.user_id

        if player_b_double is not None and player_a_double is None:
            return self.player_b.user_id

        if (
            player_a_double is not None
            and player_b_double is not None
        ):

            if player_a_double > player_b_double:
                return self.player_a.user_id

            if player_b_double > player_a_double:
                return self.player_b.user_id

        # اگر هیچ‌کدام Double نداشتند،
        # بازیکنی که مجموع بزرگ‌تری دارد شروع می‌کند.

        player_a_total = sum(
            self._tile_value(tile)
            for tile in self.player_a.hand
        )

        player_b_total = sum(
            self._tile_value(tile)
            for tile in self.player_b.hand
        )

        if player_a_total > player_b_total:
            return self.player_a.user_id

        if player_b_total > player_a_total:
            return self.player_b.user_id

        # حالت بسیار نادر مساوی:
        # بازیکن A شروع می‌کند.

        return self.player_a.user_id

    # =========================================================
    # پیدا کردن بزرگ‌ترین Double
    # =========================================================

    def _highest_double(
        self,
        hand: list[Tile],
    ) -> int | None:

        doubles = []

        for tile in hand:

            left, right = self._tile_sides(tile)

            if left == right:
                doubles.append(left)

        if not doubles:
            return None

        return max(doubles)

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
    # مقدار دو طرف مهره
    #
    # برای سازگاری با Tile های مختلف،
    # چند نام متداول را پشتیبانی می‌کنیم.
    # =========================================================

    def _tile_sides(
        self,
        tile: Tile,
    ) -> tuple[int, int]:

        if hasattr(tile, "left") and hasattr(tile, "right"):
            return tile.left, tile.right

        if hasattr(tile, "a") and hasattr(tile, "b"):
            return tile.a, tile.b

        if hasattr(tile, "value_a") and hasattr(tile, "value_b"):
            return tile.value_a, tile.value_b

        if hasattr(tile, "values"):
            values = tile.values

            return values[0], values[1]

        raise AttributeError(
            "Tile must have left/right, a/b, "
            "value_a/value_b, or values."
        )

    # =========================================================
    # مجموع ارزش مهره
    # =========================================================

    def _tile_value(
        self,
        tile: Tile,
    ) -> int:

        left, right = self._tile_sides(tile)

        return left + right

    # =========================================================
    # آیا مهره قابل بازی است؟
    # =========================================================

    def can_play_tile(
        self,
        tile: Tile,
    ) -> bool:

        if self.state is None:
            return False

        # اولین مهره بازی
        if not self.state.board_tiles:
            return True

        left, right = self._tile_sides(tile)

        return (
            left == self.state.left_end
            or right == self.state.left_end
            or left == self.state.right_end
            or right == self.state.right_end
        )

    # =========================================================
    # مهره‌های قابل بازی یک بازیکن
    # =========================================================

    def get_playable_tiles(
        self,
        user_id: int,
    ) -> list[Tile]:

        player = self.get_player(user_id)

        if player is None:
            return []

        return [
            tile
            for tile in player.hand
            if self.can_play_tile(tile)
        ]

    # =========================================================
    # بازی کردن مهره
    # =========================================================

    def play_tile(
        self,
        user_id: int,
        tile_index: int,
        side: str | None = None,
    ) -> bool:

        if self.match_finished:
            return False

        if self.round_finished:
            return False

        if self.state is None:
            return False

        if self.state.current_turn != user_id:
            return False

        player = self.get_player(user_id)

        if player is None:
            return False

        if (
            tile_index < 0
            or tile_index >= len(player.hand)
        ):
            return False

        tile = player.hand[tile_index]

        if not self.can_play_tile(tile):
            return False

        # اولین مهره روی زمین
        if not self.state.board_tiles:

            player.remove_from_hand(tile)

            self.state.board_tiles.append(tile)

            left, right = self._tile_sides(tile)

            self.state.left_end = left
            self.state.right_end = right

            self.state.last_player = user_id

            self._after_play(user_id)

            return True

        # بازی روی زمین
        success = self._place_tile(
            player,
            tile,
            side,
        )

        if not success:
            return False

        self.state.last_player = user_id

        self._after_play(user_id)

        return True

    # =========================================================
    # قرار دادن مهره روی زمین
    # =========================================================

    def _place_tile(
        self,
        player: Player,
        tile: Tile,
        side: str | None,
    ) -> bool:

        left, right = self._tile_sides(tile)

        left_end = self.state.left_end
        right_end = self.state.right_end

        can_left = (
            left == left_end
            or right == left_end
        )

        can_right = (
            left == right_end
            or right == right_end
        )

        # اگر فقط یک طرف ممکن باشد،
        # همان طرف انتخاب می‌شود.

        if can_left and not can_right:
            side = "left"

        elif can_right and not can_left:
            side = "right"

        # اگر هر دو طرف ممکن باشند،
        # بازیکن باید طرف را مشخص کند.

        elif can_left and can_right:

            if side not in ("left", "right"):
                return False

        else:
            return False

        player.remove_from_hand(tile)

        if side == "left":

            self.state.board_tiles.insert(
                0,
                tile,
            )

            if left == left_end:
                self.state.left_end = right
            else:
                self.state.left_end = left

            return True

        if side == "right":

            self.state.board_tiles.append(tile)

            if left == right_end:
                self.state.right_end = right
            else:
                self.state.right_end = left

            return True

        return False

    # =========================================================
    # خرید مهره از Boneyard
    # =========================================================

    def draw_tile(
        self,
        user_id: int,
    ) -> Tile | None:

        if self.match_finished:
            return None

        if self.round_finished:
            return None

        if self.state is None:
            return None

        if self.state.current_turn != user_id:
            return None

        player = self.get_player(user_id)

        if player is None:
            return None

        if self.deck is None:
            return None

        # اگر مهره قابل بازی دارد،
        # نباید مجبور به خرید باشد.

        if self.get_playable_tiles(user_id):
            return None

        if self.deck.is_empty():
            return None

        drawn = self.deck.draw(1)

        if not drawn:
            return None

        tile = drawn[0]

        player.add_to_hand([tile])

        return tile

    # =========================================================
    # پاس دادن
    # =========================================================

    def pass_turn(
        self,
        user_id: int,
    ) -> bool:

        if self.match_finished:
            return False

        if self.round_finished:
            return False

        if self.state is None:
            return False

        if self.state.current_turn != user_id:
            return False

        # بازیکن فقط زمانی می‌تواند Pass کند
        # که هیچ مهره قابل بازی نداشته باشد
        # و Boneyard هم خالی باشد.

        if self.get_playable_tiles(user_id):
            return False

        if self.deck is not None and not self.deck.is_empty():
            return False

        self.state.pass_count += 1

        # اگر هر دو بازیکن پشت سر هم Pass کنند،
        # بازی Block شده است.

        if self.state.pass_count >= 2:
            self._end_round_blocked()
            return True

        self.state.current_turn = (
            self._other_player(user_id).user_id
        )

        return True

    # =========================================================
    # بعد از بازی مهره
    # =========================================================

    def _after_play(
        self,
        user_id: int,
    ):

        if self.state is None:
            return

        # چون بازیکن دیگر Pass قبلی را با یک حرکت
        # شکسته است، شمارنده Pass صفر می‌شود.

        self.state.pass_count = 0

        # بازیکن تمام مهره‌هایش را بازی کرده است.

        player = self.get_player(user_id)

        if player is not None and not player.hand:

            self._end_round_winner(
                user_id
            )

            return

        # نوبت بازیکن مقابل

        self.state.current_turn = (
            self._other_player(user_id).user_id
        )

    # =========================================================
    # پایان دور به دلیل تمام شدن مهره‌ها
    # =========================================================

    def _end_round_winner(
        self,
        user_id: int,
    ):

        if self.state is None:
            return

        self.round_finished = True
        self.round_winner = user_id

        winner = self.get_player(user_id)

        loser = self._other_player(user_id)

        winner_points = sum(
            self._tile_value(tile)
            for tile in loser.hand
        )

        self.last_round_summary = {
            "winner": user_id,
            "reason": "empty_hand",
            "points": winner_points,
            "remaining_tiles": {
                winner.user_id: len(winner.hand),
                loser.user_id: len(loser.hand),
            },
        }

        self.state.round_over = True

        self.match_finished = True
        self.match_winner = user_id

    # =========================================================
    # پایان دور به دلیل Block شدن
    # =========================================================

    def _end_round_blocked(self):

        if self.state is None:
            return

        self.round_finished = True

        a_points = sum(
            self._tile_value(tile)
            for tile in self.player_a.hand
        )

        b_points = sum(
            self._tile_value(tile)
            for tile in self.player_b.hand
        )

        if a_points < b_points:
            winner_id = self.player_a.user_id

        elif b_points < a_points:
            winner_id = self.player_b.user_id

        else:
            winner_id = None

        self.round_winner = winner_id

        self.last_round_summary = {
            "winner": winner_id,
            "reason": "blocked",
            "points": {
                self.player_a.user_id: a_points,
                self.player_b.user_id: b_points,
            },
            "remaining_tiles": {
                self.player_a.user_id:
                    len(self.player_a.hand),
                self.player_b.user_id:
                    len(self.player_b.hand),
            },
        }

        self.state.round_over = True

        self.match_finished = True
        self.match_winner = winner_id

    # =========================================================
    # وضعیت بازی
    # =========================================================

    def get_state(self) -> dict:

        if self.state is None:
            return {
                "state": None,
                "player_a": self.player_a.to_dict(),
                "player_b": self.player_b.to_dict(),
                "boneyard_remaining": 0,
                "round_finished": False,
                "round_winner": None,
                "match_finished": False,
                "match_winner": None,
                "last_round_summary": None,
            }

        return {
            "state": self.state.to_dict(),

            "player_a":
                self.player_a.to_dict(),

            "player_b":
                self.player_b.to_dict(),

            "boneyard_remaining":
                self.deck.remaining()
                if self.deck is not None
                else 0,

            "round_finished":
                self.round_finished,

            "round_winner":
                self.round_winner,

            "match_finished":
                self.match_finished,

            "match_winner":
                self.match_winner,

            "last_round_summary":
                self.last_round_summary,
        }

    # =========================================================
    # امتیازات
    # =========================================================

    def get_scores(self) -> dict:

        scores = {
            self.player_a.user_id: 0,
            self.player_b.user_id: 0,
        }

        if self.last_round_summary is not None:

            winner = self.last_round_summary.get(
                "winner"
            )

            if winner is not None:

                points = self.last_round_summary.get(
                    "points",
                    0,
                )

                if isinstance(points, int):
                    scores[winner] = points

        return scores

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
