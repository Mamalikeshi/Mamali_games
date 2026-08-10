"""
Main game engine for Chahar Barg (Four Leaves / Yazdah) - 2 player mode.
Fully independent from other games (per project rule).
"""

from games.chahar_barg.deck import Deck
from games.chahar_barg.state import ChaharBargState
from games.chahar_barg.rules import resolve_move, calculate_final_scores
from games.chahar_barg.room import Room
from games.chahar_barg.player import Player


class ChaharBargGame:
    def __init__(self, room: Room):
        self.room = room
        self.deck = Deck()
        self.state = ChaharBargState()
        self.player_a: Player = room.players[0]
        self.player_b: Player = room.players[1]
        self.finished: bool = False

    def start_game(self) -> bool:
        if len(self.room.players) != 2:
            return False

        self.deck.shuffle()
        self.state.table_cards = self.deck.draw(4)
        self._deal_hands()
        self.state.current_turn = self.player_a.user_id
        self.state.sour_count[self.player_a.user_id] = 0
        self.state.sour_count[self.player_b.user_id] = 0
        return True

    def _deal_hands(self):
        self.player_a.add_to_hand(self.deck.draw(4))
        self.player_b.add_to_hand(self.deck.draw(4))

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

    def play_card(self, user_id: int, card_index: int) -> bool:
        if self.finished:
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
            if result["is_sour"]:
                self.state.sour_count[user_id] = (
                    self.state.sour_count.get(user_id, 0) + 1
                )

        self.state.table_cards = result["remaining_table"]

        if len(self.player_a.hand) == 0 and len(self.player_b.hand) == 0:
            if not self.deck.is_empty():
                self._deal_hands()
            else:
                self._end_round()

        if not self.finished:
            self.state.current_turn = self._other_player(user_id).user_id

        return True

    def _end_round(self):
        if self.state.table_cards and self.state.last_capturer is not None:
            capturer = self.get_player(self.state.last_capturer)
            capturer.capture(self.state.table_cards)
            self.state.table_cards = []

        scores = calculate_final_scores(
            self.player_a.captured,
            self.player_b.captured,
            self.state.sour_count.get(self.player_a.user_id, 0),
            self.state.sour_count.get(self.player_b.user_id, 0),
        )
        self.player_a.score = scores["player_a_score"]
        self.player_b.score = scores["player_b_score"]

        self.state.round_over = True
        self.state.game_over = True
        self.finished = True

    def get_state(self) -> dict:
        return {
            "state": self.state.to_dict(),
            "player_a": self.player_a.to_dict(),
            "player_b": self.player_b.to_dict(),
            "deck_remaining": self.deck.remaining(),
        }

    def get_scores(self) -> dict:
        return {
            self.player_a.user_id: self.player_a.score,
            self.player_b.user_id: self.player_b.score,
        }

    def get_winner(self) -> int | None:
        if not self.finished:
            return None
        if self.player_a.score > self.player_b.score:
            return self.player_a.user_id
        if self.player_b.score > self.player_a.score:
            return self.player_b.user_id
        return None

    def is_finished(self) -> bool:
        return self.finished
