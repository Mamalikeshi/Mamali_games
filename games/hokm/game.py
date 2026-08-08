from .deck import Deck
from .player import Player
from .room import Room
from .state import GameState
from .rules import (
    can_play_card,
    determine_trick_winner,
    validate_trump,
)


class HokmGame:
    def __init__(self, room: Room):
        self.room = room
        self.state = GameState(room_id=room.room_id)
        self.deck = Deck()

    def start_game(self) -> bool:
        if len(self.room.players) != 2:
            return False

        if not self.room.both_ready():
            return False

        self.deck = Deck()
        self.deck.shuffle()

        hands = self.deck.deal(
            players=2,
            cards_per_player=13,
        )

        for player, hand in zip(self.room.players, hands):
            player.hand = hand
            player.sort_hand()

        self.room.is_started = True

        first_player = self.room.players[0]
        self.state.set_turn(first_player.user_id)

        return True

    def choose_trump(self, user_id: int, suit: str) -> bool:
        if not self.room.is_started:
            return False

        if not validate_trump(suit):
            return False

        player = self.room.get_player(user_id)

        if player is None:
            return False

        # فعلاً فقط بازیکنی که نوبتش است
        # می‌تواند حکم را انتخاب کند.
        if self.state.current_turn != user_id:
            return False

        self.state.set_trump(suit)
        player.hokm = True

        return True

    def play_card(self, user_id: int, card_index: int) -> bool:
        if not self.room.is_started:
            return False

        if self.state.trump is None:
            return False

        if self.state.current_turn != user_id:
            return False

        player = self.room.get_player(user_id)

        if player is None:
            return False

        if card_index < 0 or card_index >= len(player.hand):
            return False

        card = player.hand[card_index]

        if not can_play_card(
            card,
            player.hand,
            self.state.trick_cards,
        ):
            return False

        played_card = player.play_card(card_index)

        self.state.add_card_to_trick(
            user_id,
            played_card,
        )

        if self.state.is_trick_complete():
            self._finish_trick()
        else:
            self._switch_turn()

        return True

    def _switch_turn(self):
        for player in self.room.players:
            if player.user_id != self.state.current_turn:
                self.state.set_turn(player.user_id)
                return

    def _finish_trick(self):
        winner_id = determine_trick_winner(
            self.state.trick_cards,
            self.state.trump,
        )

        winner = self.room.get_player(winner_id)

        if winner is not None:
            winner.tricks += 1

        self.state.add_trick_win(winner_id)

        self.state.clear_trick()

        # برنده Trick بعدی را شروع می‌کند.
        self.state.set_turn(winner_id)

        # در حکم دو نفره هر بازیکن 13 کارت دارد.
        # بنابراین بعد از 13 Trick، دست تمام می‌شود.
        if self.state.completed_tricks >= 13:
            self._finish_round()

    def _finish_round(self):
        player_one = self.room.players[0]
        player_two = self.room.players[1]

        if player_one.tricks > player_two.tricks:
            winner_id = player_one.user_id
        elif player_two.tricks > player_one.tricks:
            winner_id = player_two.user_id
        else:
            winner_id = None

        if winner_id is not None:
            self.state.set_winner(winner_id)

       def get_scores(self):
        return {
            str(player.user_id): player.tricks
            for player in self.room.players
        }

    def get_winner(self):
        return self.state.winner

    def is_finished(self):
        return self.state.winner is not None
    def get_player(self, user_id: int) -> Player | None:
        return self.room.get_player(user_id)

    def get_state(self):
        return self.state.to_dict()
