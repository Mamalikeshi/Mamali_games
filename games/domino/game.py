"""
Main game engine for Domino - 2 player mode.

Standard Double-Six Domino:
- 28 tiles
- 2 players
- 7 tiles for each player
- 14 tiles in boneyard
- Match target: 101 points

Round:
- A player wins by emptying their hand.
- If the game is blocked, the player with fewer pips wins.
- Winner receives the opponent's remaining pips.
- If the round is blocked, the winner receives the opponent's
  remaining pip total.
- If both players have the same pip total, the round gives 0 points.

Match:
- Scores accumulate between rounds.
- A player reaching MATCH_TARGET_SCORE wins the match.
"""

from games.domino.deck import Deck
from games.domino.player import Player
from games.domino.room import Room
from games.domino.state import DominoState
from games.domino.tile import Tile
from games.domino.rules import (
    MATCH_TARGET_SCORE,
    TILES_PER_PLAYER,
)


class DominoGame:

    def __init__(self, room: Room):

        if len(room.players) != 2:
            raise ValueError(
                "Domino requires exactly 2 players."
            )

        self.room = room

        self.player_a: Player = room.players[0]
        self.player_b: Player = room.players[1]

        self.deck: Deck | None = None
        self.state: DominoState | None = None

        # Match
        self.match_finished: bool = False
        self.match_winner: int | None = None

        # Round
        self.round_finished: bool = False
        self.round_winner: int | None = None

        self.round_number: int = 0

        self.last_round_summary: dict | None = None

        # امتیاز کل Match
        self.player_a.score = 0
        self.player_b.score = 0

    # =========================================================
    # شروع Match
    # =========================================================

    def start_game(self) -> bool:

        if len(self.room.players) != 2:
            return False

        self.match_finished = False
        self.match_winner = None

        self.round_number = 0

        self.player_a.score = 0
        self.player_b.score = 0

        self.last_round_summary = None

        return self._start_round()

    # =========================================================
    # شروع یک دست
    # =========================================================

    def _start_round(self) -> bool:

        if self.match_finished:
            return False

        self.deck = Deck()
        self.deck.shuffle()

        self.state = DominoState()

        self.round_finished = False
        self.round_winner = None

        self.player_a.hand = []
        self.player_b.hand = []

        self._deal_initial_tiles()

        self.round_number += 1

        starter = self._choose_starter()

        self.state.current_turn = starter

        return True

    # =========================================================
    # شروع دست بعدی
    # =========================================================

    def start_next_round(self) -> bool:

        if self.match_finished:
            return False

        if not self.round_finished:
            return False

        return self._start_round()

    # =========================================================
    # پخش ۷ مهره برای هر بازیکن
    # =========================================================

    def _deal_initial_tiles(self):

        if self.deck is None:
            return

        self.player_a.add_to_hand(
            self.deck.draw(TILES_PER_PLAYER)
        )

        self.player_b.add_to_hand(
            self.deck.draw(TILES_PER_PLAYER)
        )

    # =========================================================
    # انتخاب شروع‌کننده
    # =========================================================

    def _choose_starter(self) -> int:

        player_a_double = self._highest_double(
            self.player_a.hand
        )

        player_b_double = self._highest_double(
            self.player_b.hand
        )

        if (
            player_a_double is not None
            and player_b_double is None
        ):
            return self.player_a.user_id

        if (
            player_b_double is not None
            and player_a_double is None
        ):
            return self.player_b.user_id

        if (
            player_a_double is not None
            and player_b_double is not None
        ):

            if player_a_double > player_b_double:
                return self.player_a.user_id

            if player_b_double > player_a_double:
                return self.player_b.user_id

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

        return self.player_a.user_id

    # =========================================================
    # بزرگ‌ترین Double
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
    # گرفتن دو طرف مهره
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
    # مجموع پیپ‌های دست
    # =========================================================

    def _hand_pip_sum(
        self,
        player: Player,
    ) -> int:

        return sum(
            self._tile_value(tile)
            for tile in player.hand
        )

    # =========================================================
    # آیا مهره قابل بازی است؟
    # =========================================================

    def can_play_tile(
        self,
        tile: Tile,
    ) -> bool:

        if self.state is None:
            return False

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
    # مهره‌های قابل بازی
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

        # اولین مهره
        if not self.state.board_tiles:

            player.remove_from_hand(tile)

            self.state.board_tiles.append(tile)

            left, right = self._tile_sides(tile)

            self.state.left_end = left
            self.state.right_end = right

            self.state.last_player = user_id

            self._after_play(user_id)

            return True

        # مهره روی زمین
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
    # قرار دادن مهره
    # =========================================================

    def _place_tile(
        self,
        player: Player,
        tile: Tile,
        side: str | None,
    ) -> bool:

        if self.state is None:
            return False

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

        if can_left and not can_right:
            side = "left"

        elif can_right and not can_left:
            side = "right"

        elif can_left and can_right:

            if side not in ("left", "right"):
                return False

        else:
            return False

        # سمت چپ
        if side == "left":

            player.remove_from_hand(tile)

            self.state.board_tiles.insert(
                0,
                tile,
            )

            if left == left_end:
                self.state.left_end = right
            else:
                self.state.left_end = left

            return True

        # سمت راست
        if side == "right":

            player.remove_from_hand(tile)

            self.state.board_tiles.append(tile)

            if left == right_end:
                self.state.right_end = right
            else:
                self.state.right_end = left

            return True

        return False

    # =========================================================
    # خرید مهره
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

        # اگر مهره قابل بازی دارد، خرید ممنوع
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
    # پاس
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

        # مهره قابل بازی دارد → پاس ممنوع
        if self.get_playable_tiles(user_id):
            return False

        # هنوز مهره در Boneyard هست → باید خرید کند
        if (
            self.deck is not None
            and not self.deck.is_empty()
        ):
            return False

        self.state.pass_count += 1

        # دو پاس → Block
        if self.state.pass_count >= 2:

            self._end_round_blocked()

            return True

        self.state.current_turn = (
            self._other_player(user_id).user_id
        )

        return True

    # =========================================================
    # بعد از بازی موفق
    # =========================================================

    def _after_play(
        self,
        user_id: int,
    ):

        if self.state is None:
            return

        self.state.pass_count = 0

        player = self.get_player(user_id)

        if player is not None and not player.hand:

            self._end_round_winner(user_id)

            return

        self.state.current_turn = (
            self._other_player(user_id).user_id
        )

    # =========================================================
    # پایان دست با خالی شدن دست
    # =========================================================

    def _end_round_winner(
        self,
        user_id: int,
    ):

        if self.state is None:
            return

        if self.round_finished:
            return

        self.round_finished = True
        self.round_winner = user_id

        winner = self.get_player(user_id)

        if winner is None:
            return

        loser = self._other_player(user_id)

        points = self._hand_pip_sum(loser)

        winner.score += points

        self.last_round_summary = {
            "round_number": self.round_number,
            "winner": user_id,
            "reason": "empty_hand",
            "points": points,
            "scores": {
                self.player_a.user_id:
                    self.player_a.score,
                self.player_b.user_id:
                    self.player_b.score,
            },
            "remaining_tiles": {
                self.player_a.user_id:
                    len(self.player_a.hand),
                self.player_b.user_id:
                    len(self.player_b.hand),
            },
        }

        self.state.round_over = True

        self._check_match_finished()

    # =========================================================
    # پایان دست به دلیل Block
    # =========================================================

    def _end_round_blocked(self):

        if self.state is None:
            return

        if self.round_finished:
            return

        self.round_finished = True

        a_points = self._hand_pip_sum(
            self.player_a
        )

        b_points = self._hand_pip_sum(
            self.player_b
        )

        if a_points < b_points:

            winner_id = self.player_a.user_id
            points = b_points

        elif b_points < a_points:

            winner_id = self.player_b.user_id
            points = a_points

        else:

            winner_id = None
            points = 0

        self.round_winner = winner_id

        if winner_id is not None:

            winner = self.get_player(
                winner_id
            )

            if winner is not None:
                winner.score += points

        self.last_round_summary = {
            "round_number": self.round_number,
            "winner": winner_id,
            "reason": "blocked",
            "points": points,
            "pip_totals": {
                self.player_a.user_id:
                    a_points,
                self.player_b.user_id:
                    b_points,
            },
            "scores": {
                self.player_a.user_id:
                    self.player_a.score,
                self.player_b.user_id:
                    self.player_b.score,
            },
            "remaining_tiles": {
                self.player_a.user_id:
                    len(self.player_a.hand),
                self.player_b.user_id:
                    len(self.player_b.hand),
            },
        }

        self.state.is_blocked = True
        self.state.round_over = True

        self._check_match_finished()

    # =========================================================
    # بررسی پایان Match
    # =========================================================

    def _check_match_finished(self):

        if (
            self.player_a.score >=
            MATCH_TARGET_SCORE
        ):

            self.match_finished = True

            self.match_winner = (
                self.player_a.user_id
            )

            return

        if (
            self.player_b.score >=
            MATCH_TARGET_SCORE
        ):

            self.match_finished = True

            self.match_winner = (
                self.player_b.user_id
            )

    # =========================================================
    # امتیازات Match
    # =========================================================

    def get_scores(self) -> dict:

        return {
            self.player_a.user_id:
                self.player_a.score,

            self.player_b.user_id:
                self.player_b.score,
        }

    # =========================================================
    # وضعیت کامل بازی
    # =========================================================

    def get_state(self) -> dict:

        if self.state is None:

            return {
                "state": None,

                "player_a":
                    self.player_a.to_dict(),

                "player_b":
                    self.player_b.to_dict(),

                "boneyard_remaining": 0,

                "round_number":
                    self.round_number,

                "round_finished":
                    self.round_finished,

                "round_winner":
                    self.round_winner,

                "match_finished":
                    self.match_finished,

                "match_winner":
                    self.match_winner,

                "match_target_score":
                    MATCH_TARGET_SCORE,

                "scores":
                    self.get_scores(),

                "last_round_summary":
                    self.last_round_summary,
            }

        return {
            "state":
                self.state.to_dict(),

            "player_a":
                self.player_a.to_dict(),

            "player_b":
                self.player_b.to_dict(),

            "boneyard_remaining":
                (
                    self.deck.remaining()
                    if self.deck is not None
                    else 0
                ),

            "round_number":
                self.round_number,

            "round_finished":
                self.round_finished,

            "round_winner":
                self.round_winner,

            "match_finished":
                self.match_finished,

            "match_winner":
                self.match_winner,

            "match_target_score":
                MATCH_TARGET_SCORE,

            "scores":
                self.get_scores(),

            "last_round_summary":
                self.last_round_summary,
        }

    # =========================================================
    # برنده Match
    # =========================================================

    def get_winner(self) -> int | None:

        return self.match_winner

    # =========================================================
    # پایان Match
    # =========================================================

    def is_finished(self) -> bool:

        return self.match_finished
