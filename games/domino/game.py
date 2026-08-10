"""
Main game engine for Domino (Double-Six set) - 2 player mode.
Fully independent from other games (per project rule).

قوانین کلی:
- هر بازیکن ۷ مهره می‌گیره (۱۴ مهره باقی‌مونده تو boneyard می‌مونه).
- دست اول: کسی که بالاترین دوبل رو داره شروع می‌کنه.
- از دست دوم به بعد، شروع‌کننده برعکس دست قبل می‌شه.
- اگه بازیکنی تو نوبتش مهره‌ی قابل بازی نداشته باشه، باید یکی‌یکی از
  boneyard بکشه تا مهره‌ی قابل بازی گیرش بیاد و بلافاصله بازیش کنه.
- اگه فقط یک مهره تو boneyard بمونه و بازیکن هنوز مهره‌ی قابل بازی نداشته
  باشه، اون یک مهره دست‌نخورده می‌مونه و نوبت به حریف می‌رسه.
- اگه هیچ‌کدوم از بازیکنان نتونن بازی کنن و boneyard هم دیگه قابل کشیدن
  نباشه، دست "بسته" می‌شه: کسی که مجموع نقطه‌های دستش کمتره برنده‌ی دسته
  و مجموع نقطه‌های دست حریف بهش تعلق می‌گیره.
- اولین بازیکنی که دستش خالی بشه، برنده‌ی دسته و مجموع نقطه‌های دست
  حریف بهش تعلق می‌گیره.
- بازی تا ۱۰۱ امتیاز ادامه داره.
"""

from games.domino.deck import Deck
from games.domino.state import DominoState
from games.domino.rules import (
    find_highest_double,
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

        # وقتی بازیکنی مهره‌ای می‌کشه که قابل‌بازیه، باید بلافاصله بازیش کنه.
        # این متغیر نشون می‌ده کدوم مهره (اندیس تو دستش) رو تازه کشیده.
        self.pending_forced_tile_index: dict[int, int | None] = {}

    # ---------- شروع مسابقه و دست ----------

    def start_game(self) -> bool:
        if len(self.room.players) != 2:
            return False
        self._start_round(starter_user_id=None, is_first_round=True)
        return True

    def _start_round(self, starter_user_id: int | None, is_first_round: bool = False):
        self.round_number += 1

        self.deck = Deck()
        self.deck.shuffle()

        self.player_a.hand = []
        self.player_b.hand = []

        self.player_a.add_to_hand(self.deck.draw(TILES_PER_PLAYER))
        self.player_b.add_to_hand(self.deck.draw(TILES_PER_PLAYER))

        self.state = DominoState()
        self.pending_forced_tile_index = {
            self.player_a.user_id: None,
            self.player_b.user_id: None,
        }

        if is_first_round:
            hands = {
                self.player_a.user_id: self.player_a.hand,
                self.player_b.user_id: self.player_b.hand,
            }
            starter = find_highest_double(hands)
            if starter is None:
                starter = self.player_a.user_id
        else:
            starter = starter_user_id

        self.last_round_starter = starter
        self.state.current_turn = starter

    # ---------- کمکی ----------

    def get_player(self, user_id: int) -> Player | None:
        if self.player_a.user_id == user_id:
            return self.player_a
        if self.player_b.user_id == user_id:
            return self.player_b
        return None

    def _other_player(self, user_id: int) -> Player:
        if self.player_a.user_id == user_id:
            return self.player_b
        return self.player_a

    def _player_can_play(self, player: Player) -> bool:
        for tile in player.hand:
            if can_play_tile(tile, self.state.left_end, self.state.right_end):
                return True
        return False

    # ---------- کشیدن از boneyard وقتی مهره‌ی قابل‌بازی نیست ----------

    def draw_from_boneyard(self, user_id: int) -> dict:
        """
        بازیکن یه مهره از boneyard می‌کشه. اگه قابل‌بازی بود، باید بلافاصله
        بازیش کنه (از play_tile با همون اندیس استفاده می‌کنه).
        اگه فقط یک مهره تو boneyard بمونه و اون بازیکن هنوز نتونه بازی کنه،
        اون مهره دست‌نخورده می‌مونه و نوبت به حریف می‌رسه.
        """
        if self.match_finished or self.state.round_over:
            return {"success": False, "reason": "round_not_active"}
        if self.state.current_turn != user_id:
            return {"success": False, "reason": "not_your_turn"}

        player = self.get_player(user_id)
        if player is None:
            return {"success": False, "reason": "player_not_found"}
        if self._player_can_play(player):
            return {"success": False, "reason": "you_have_a_playable_tile"}

        # اگه فقط یک مهره باقی مونده، نمی‌کشیم؛ دست‌نخورده می‌مونه و نوبت عوض می‌شه
        if self.deck.remaining() <= 1:
            self._pass_turn_or_check_blocked(user_id)
            return {"success": True, "drew_tile": False, "playable": False}

        drawn = self.deck.draw_one()
        player.add_to_hand([drawn])

        if can_play_tile(drawn, self.state.left_end, self.state.right_end):
            new_index = len(player.hand) - 1
            self.pending_forced_tile_index[user_id] = new_index
            return {
                "success": True,
                "drew_tile": True,
                "playable": True,
                "forced_tile_index": new_index,
            }

        return {"success": True, "drew_tile": True, "playable": False}

    def _pass_turn_or_check_blocked(self, from_user_id: int):
        other = self._other_player(from_user_id)
        self.state.current_turn = other.user_id

        # اگه حریف هم نتونه بازی کنه و boneyard هم عملاً بن‌بسته، بازی بسته می‌شه
        if not self._player_can_play(other) and self.deck.remaining() <= 1:
            self._end_round_blocked()

    def _end_round_blocked(self):
        self.state.is_blocked = True
        self._finish_round_with_lowest_hand()

    def _finish_round_with_lowest_hand(self):
        sum_a = self.player_a.hand_pip_sum()
        sum_b = self.player_b.hand_pip_sum()

        if sum_a < sum_b:
            winner = self.player_a
            points = sum_b
        elif sum_b < sum_a:
            winner = self.player_b
            points = sum_a
        else:
            winner = None
            points = 0

        self._close_round(winner.user_id if winner else None, points)

    # ---------- بازی کردن یک مهره ----------

    def play_tile(self, user_id: int, tile_index: int, side: str) -> dict:
        if self.match_finished or self.state.round_over:
            return {"success": False, "reason": "round_not_active"}
        if self.state.current_turn != user_id:
            return {"success": False, "reason": "not_your_turn"}

        player = self.get_player(user_id)
        if player is None:
            return {"success": False, "reason": "player_not_found"}
        if tile_index < 0 or tile_index >= len(player.hand):
            return {"success": False, "reason": "invalid_tile_index"}

        # اگه بازیکن مهره‌ی قابل‌بازی داشت ولی این‌یکی که انتخاب کرده
        # قابل‌بازی نیست، رد می‌کنیم (باید یکی از مهره‌های قابل‌بازیش رو بزنه)
        tile = player.hand[tile_index]
        valid_sides = valid_sides_for_tile(tile, self.state.left_end, self.state.right_end)
        if side not in valid_sides:
            return {"success": False, "reason": "tile_not_playable_on_this_side"}

        result = place_tile(tile, side, self.state.left_end, self.state.right_end)
        player.remove_from_hand(tile)

        if side == "left" or (self.state.left_end is None and self.state.right_end is None):
            self.state.board.insert(0, tile)
        else:
            self.state.board.append(tile)

        self.state.left_end = result["new_left_end"]
        self.state.right_end = result["new_right_end"]

        self.pending_forced_tile_index[user_id] = None

        if len(player.hand) == 0:
            opponent = self._other_player(user_id)
            self._close_round(user_id, opponent.hand_pip_sum())
            return {"success": True, "round_over": True}

        self._pass_turn_or_check_blocked(user_id)
        return {"success": True, "round_over": False}

    # ---------- پایان دست و مسابقه ----------

    def _close_round(self, winner_user_id: int | None, points: int):
        if winner_user_id is not None:
            self.total_score[winner_user_id] += points

        self.player_a.score = self.total_score[self.player_a.user_id]
        self.player_b.score = self.total_score[self.player_b.user_id]

        self.last_round_summary = {
            "round_number": self.round_number,
            "winner_user_id": winner_user_id,
            "points_awarded": points,
            "was_blocked": self.state.is_blocked,
            "total_score": dict(self.total_score),
        }

        self.state.round_over = True

        if max(self.total_score.values()) >= MATCH_TARGET_SCORE:
            self.match_finished = True
            if self.total_score[self.player_a.user_id] == self.total_score[self.player_b.user_id]:
                self.match_winner = None
            else:
                self.match_winner = max(self.total_score, key=self.total_score.get)
        else:
            next_starter = self._other_player(self.last_round_starter).user_id
            self._start_round(starter_user_id=next_starter)

    # ---------- خروجی برای فرانت‌اند ----------

    def get_state(self) -> dict:
        return {
            "state": self.state.to_dict(),
            "player_a": self.player_a.to_dict(),
            "player_b": self.player_b.to_dict(),
            "boneyard_remaining": self.deck.remaining(),
            "round_number": self.round_number,
            "total_score": self.total_score,
            "match_finished": self.match_finished,
            "match_winner": self.match_winner,
            "last_round_summary": self.last_round_summary,
            "pending_forced_tile_index": self.pending_forced_tile_index,
        }

    def get_scores(self) -> dict:
        return dict(self.total_score)

    def get_winner(self) -> int | None:
        return self.match_winner

    def is_finished(self) -> bool:
        return self.match_finished
