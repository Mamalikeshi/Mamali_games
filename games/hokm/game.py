from games.hokm.state import GameState
from games.hokm.deck import Deck
from games.hokm.player import Player


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

        self.deck = Deck()
        self.deck.shuffle()

        self.deck.deal(self.room.players, 5)

        hokm_player = self.room.players[0]
        hokm_player.is_hokm = True

        self.state.set_turn(hokm_player.user_id)

        return True

    def choose_trump(self, user_id: int, suit: str):
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

            self.state.clear_trick()

            if self._check_game_finished():
                self.state.set_winner(winner)
            else:
                self.state.set_turn(winner)

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

    def _check_game_finished(self):
        for user_id, wins in self.state.trick_wins.items():
            if wins >= 7:
                return True

        return False

    def get_scores(self):
        return self.state.trick_wins

    def get_winner(self):
        return self.state.winner

    def is_finished(self):
        return self.state.winner is not None

    def get_state(self):
        return self.state.to_dict()
