import random
import time

from games.hokm.state import GameState
from games.hokm.deck import Deck
from games.hokm.card import Card
from games.hokm.player import Player


TURN_TIMEOUT_SECONDS = 20
DISCONNECT_TIMEOUT_SECONDS = 60
TRICK_HOLD_SECONDS = 2


class HokmGame:
    def __init__(self, room):
        self.room = room
        self.state = GameState(room.room_id)
        self.deck = None

    def get_player(self, user_id: int):
        for player in self.room.players:
            if player.user_id == user_id:
                return player

        return None

    def start_game(self):
        if len(self.room.players) != 2:
            return False

        if not self.room.both_ready():
            return False

        self.room.start()

        hokm_player = random.choice(self.room.players)

        self._deal_new_hand(hokm_player.user_id)

        return True

    def choose_trump(self, user_id: int, suit: str):
        if self.state.trick_completed_at is not None:
            return False

        if self.state.trump is not None:
            return False

        player = self.get_player(user_id)

        if player is None:
            return False

        if not player.is_hokm:
            return False

        if user_id != self.state.current_turn:
            return False

        valid_suits = {
            "hearts",
            "diamonds",
            "clubs",
            "spades",
        }

        if suit not in valid_suits:
            return False

        self.state.set_trump(suit)

        self.deck.deal_additional(
            self.room.players,
            8,
        )

        return True

    def play_card(self, user_id: int, card_index: int):
        # تا وقتی داریم دستِ قبلی رو (که کامل شده) نشون می‌دیم، هیچ حرکتی قبول نیست
        if self.state.trick_completed_at is not None:
            return False

        if self.state.trump is None:
            return False

        if user_id != self.state.current_turn:
            return False

        player = self.get_player(user_id)

        if player is None:
            return False

        if card_index < 0 or card_index >= len(player.hand):
            return False

        card = player.hand[card_index]

        if self.state.trick_cards:
            _, first_card = self.state.trick_cards[0]

            has_lead_suit = any(
                hand_card.suit == first_card.suit
                for hand_card in player.hand
            )

            if has_lead_suit and card.suit != first_card.suit:
                return False

        player.hand.pop(card_index)

        self.state.add_card_to_trick(
            user_id,
            card,
        )

        if self.state.is_trick_complete():
            winner = self._determine_trick_winner()

            if winner is None:
                return False

            self.state.add_trick_win(winner)

            # اینجا عمداً دست رو پاک نمی‌کنیم و نوبت رو هم عوض نمی‌کنیم؛
            # چند ثانیه صبر می‌کنیم (توی check_timeouts) تا هر دو بازیکن
            # فرصت ببینن هر دو برگ روی زمین چی بودن
            self.state.mark_trick_completed(winner)

        else:
            for next_player in self.room.players:
                if next_player.user_id != user_id:
                    self.state.set_turn(next_player.user_id)
                    break

        return True

    def _determine_trick_winner(self):
        if len(self.state.trick_cards) != 2:
            return None

        first_user, first_card = self.state.trick_cards[0]
        second_user, second_card = self.state.trick_cards[1]

        if second_card.suit == self.state.trump:
            if first_card.suit != self.state.trump:
                return second_user

        if first_card.suit == self.state.trump:
            if second_card.suit != self.state.trump:
                return first_user

        if second_card.suit == first_card.suit:
            if second_card.rank_value > first_card.rank_value:
                return second_user

        return first_user

    def _check_hand_finished(self):
        for user_id, wins in self.state.trick_wins.items():
            if wins >= 7:
                return True

        return False

    def _finish_hand(self, hand_winner: int):
        opponent = next(
            (
                p for p in self.room.players
                if p.user_id != hand_winner
            ),
            None,
        )

        opponent_tricks = (
            self.state.trick_wins.get(opponent.user_id, 0)
            if opponent is not None else 0
        )

        hokm_player = next(
            (p for p in self.room.players if p.is_hokm),
            None,
        )

        winner_is_hokm = (
            hokm_player is not None
            and hokm_player.user_id == hand_winner
        )

        # قانون کُت: اگه یه طرف تمام برگ‌های اون دست رو ببره و حریف
        # حتی یه برگ هم نگیره، امتیاز بیشتری می‌گیره
        if opponent_tricks == 0:
            points = 2 if winner_is_hokm else 3
        else:
            points = 1

        self.state.hand_wins[hand_winner] = (
            self.state.hand_wins.get(hand_winner, 0) + points
        )

        if self.state.hand_wins[hand_winner] >= 7:
            self.state.set_winner(hand_winner)
            self.state.set_turn(hand_winner)
        else:
            self._deal_new_hand(hand_winner)

    def _deal_new_hand(self, hokm_user_id: int):
        for player in self.room.players:
            player.is_hokm = False
            player.hand = []

        self.state.start_new_hand()

        self.deck = Deck()
        self.deck.shuffle()

        self.deck.deal(self.room.players, 5)

        hokm_player = self.get_player(hokm_user_id)
        hokm_player.is_hokm = True

        self.state.set_turn(hokm_user_id)

    def get_scores(self):
        return self.state.hand_wins

    def get_winner(self):
        return self.state.winner

    def is_finished(self):
        return self.state.winner is not None

    def get_state(self):
        return self.state.to_dict()

    def check_timeouts(self):
        if self.state.winner is not None:
            return

        # ۰. اگه یه دست (trick) کامل شده، صبر می‌کنیم تا هر دو نفر ببیننش
        if self.state.trick_completed_at is not None:
            if time.time() - self.state.trick_completed_at >= TRICK_HOLD_SECONDS:
                winner = self.state.pending_trick_winner

                self.state.clear_trick()
                self.state.trick_completed_at = None
                self.state.pending_trick_winner = None

                if self._check_hand_finished():
                    self._finish_hand(winner)
                else:
                    self.state.set_turn(winner)

            return

        # ۱. اگه بازیکنی بیشتر از ۶۰ ثانیه پیداش نبوده (پول نزده)، ببازونش
        for player in self.room.players:
            last = self.state.last_seen.get(player.user_id)

            if last is None:
                continue

            if time.time() - last > DISCONNECT_TIMEOUT_SECONDS:
                opponent = next(
                    (
                        p for p in self.room.players
                        if p.user_id != player.user_id
                    ),
                    None,
                )

                if opponent is not None:
                    self.state.set_winner(opponent.user_id)

                return

        # ۲. اگه نوبت کسی بیشتر از ۲۰ ثانیه طول کشیده، خودکار براش بازی کن
        if self.state.turn_started_at is None:
            return

        elapsed = time.time() - self.state.turn_started_at

        if elapsed <= TURN_TIMEOUT_SECONDS:
            return

        self._auto_play_for_current_turn()

    def _auto_play_for_current_turn(self):
        player = self.get_player(self.state.current_turn)

        if player is None:
            return

        if self.state.trump is None:
            if player.is_hokm:
                suit = random.choice(list(Card.SUITS))
                self.choose_trump(player.user_id, suit)
            return

        if not player.hand:
            return

        valid_index = 0

        if self.state.trick_cards:
            _, first_card = self.state.trick_cards[0]

            for index, hand_card in enumerate(player.hand):
                if hand_card.suit == first_card.suit:
                    valid_index = index
                    break

        self.play_card(player.user_id, valid_index)

    def forfeit(self, user_id: int):
        if self.state.winner is not None:
            return False

        opponent = next(
            (
                p for p in self.room.players
                if p.user_id != user_id
            ),
            None,
        )

        if opponent is None:
            return False

        self.state.set_winner(opponent.user_id)

        return True
