"""
Main game engine for Chahar Barg (Four Leaves / Yazdah) - 2 player mode.
Fully independent from other games (per project rule).

قوانین کلی مسابقه:
- هر دور تا تمام‌شدن کارت‌ها (کل دسته ۵۲تایی) ادامه داره.
- شروع‌کننده‌ی دور اول تصادفیه. از دور دوم به بعد، شروع‌کننده برعکس دور قبل می‌شه.
- ۸ برگ آخر هر دور (آخرین باری که کارت پخش می‌شه) سور نداره.
- اگه امتیاز کل یک بازیکن (قبل از این دور) به ۵۰ برسه، سور این دور براش حساب نمی‌شه.
- بازی تا وقتی ادامه داره که یکی از بازیکنان به ۶۲ امتیاز برسه.
"""

import random

from games.chahar_barg.deck import Deck
from games.chahar_barg.state import ChaharBargState
from games.chahar_barg.rules import (
    resolve_move,
    tally_round_score,
    has_haft_khaj,
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

    # ---------- شروع مسابقه و دور ----------

    def start_game(self) -> bool:
        if len(self.room.players) != 2:
            return False
        starter = random.choice([self.player_a.user_id, self.player_b.user_id])
        self._start_round(starter)
        return True

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
        self.state.table_cards = self.deck.draw(4)
        self._deal_hands()
        self.state.current_turn = starter_user_id

    def _deal_hands(self):
        self.player_a.add_to_hand(self.deck.draw(4))
        self.player_b.add_to_hand(self.deck.draw(4))
        if self.deck.is_empty():
            self.state.is_final_deal = True

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

    # ---------- بازی کردن یک کارت ----------

    def play_card(self, user_id: int, card_index: int) -> bool:
        if self.match_finished:
            return False
        if self.state.current_turn != user_id:
            return False

        player = self.get_player(user_id)
        if player is None:
            return False
        if card_index < 0 or card_index >= len(player.hand):
            return False

        card = player.hand[card_index]
        result = resolve_move(card, self.state.table_cards)
        player.remove_from_hand(card)

        if result["captured"]:
            player.capture(result["captured"])
            self.state.last_capturer = user_id

            if result["is_sour"] and not self.state.is_final_deal:
                points = SOUR_JACK_POINTS if result["is_jack_sweep"] else SOUR_NORMAL_POINTS
                self.state.sour_points[user_id] = (
                    self.state.sour_points.get(user_id, 0) + points
                )

        self.state.table_cards = result["remaining_table"]

        if len(self.player_a.hand) == 0 and len(self.player_b.hand) == 0:
            if not self.deck.is_empty():
                self._deal_hands()
            else:
                self._end_round()

        if not self.match_finished and self.state is not None and not self.state.round_over:
            self.state.current_turn = self._other_player(user_id).user_id

        return True

    # ---------- پایان دور ----------

    def _end_round(self):
        if self.state.table_cards and self.state.last_capturer is not None:
            capturer = self.get_player(self.state.last_capturer)
            capturer.capture(self.state.table_cards)
            self.state.table_cards = []

        round_points = {
            self.player_a.user_id: tally_round_score(self.player_a.captured),
            self.player_b.user_id: tally_round_score(self.player_b.captured),
        }

        if has_haft_khaj(self.player_a.captured):
            round_points[self.player_a.user_id] += HAFT_KHAJ_POINTS
        elif has_haft_khaj(self.player_b.captured):
            round_points[self.player_b.user_id] += HAFT_KHAJ_POINTS

        for user_id in (self.player_a.user_id, self.player_b.user_id):
            sour_earned = self.state.sour_points.get(user_id, 0)
            if sour_earned and self.total_score[user_id] < SOUR_DISABLE_THRESHOLD:
                round_points[user_id] += sour_earned

        for user_id, points in round_points.items():
            self.total_score[user_id] += points

        self.player_a.score = self.total_score[self.player_a.user_id]
        self.player_b.score = self.total_score[self.player_b.user_id]

        self.last_round_summary = {
            "round_number": self.round_number,
            "round_points": round_points,
            "total_score": dict(self.total_score),
        }

        self.state.round_over = True

        if max(self.total_score.values()) >= MATCH_TARGET_SCORE:
            self.match_finished = True
            self.match_winner = max(self.total_score, key=self.total_score.get)
            if self.total_score[self.player_a.user_id] == self.total_score[self.player_b.user_id]:
                self.match_winner = None
        else:
            next_starter = self._other_player(self.last_round_starter).user_id
            self._start_round(next_starter)

    # ---------- خروجی برای فرانت‌اند ----------

    def get_state(self) -> dict:
        return {
            "state": self.state.to_dict(),
            "player_a": self.player_a.to_dict(),
            "player_b": self.player_b.to_dict(),
            "deck_remaining": self.deck.remaining(),
            "round_number": self.round_number,
            "total_score": self.total_score,
            "match_finished": self.match_finished,
            "match_winner": self.match_winner,
            "last_round_summary": self.last_round_summary,
        }

    def get_scores(self) -> dict:
        return dict(self.total_score)

    def get_winner(self) -> int | None:
        return self.match_winner

    def is_finished(self) -> bool:
        return self.match_finished
