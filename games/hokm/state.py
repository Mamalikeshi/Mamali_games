from dataclasses import dataclass, field
from typing import Optional

from .card import Card


@dataclass
class GameState:
    room_id: str

    current_turn: Optional[int] = None

    trump: Optional[str] = None

    trick_cards: list[tuple[int, Card]] = field(default_factory=list)

    completed_tricks: int = 0

    player_scores: dict[int, int] = field(default_factory=dict)

    round_number: int = 1

    game_over: bool = False

    winner_id: Optional[int] = None

    def set_turn(self, user_id: int):
        self.current_turn = user_id

    def set_trump(self, suit: str):
        self.trump = suit

    def add_card_to_trick(self, user_id: int, card: Card):
        self.trick_cards.append((user_id, card))

    def clear_trick(self):
        self.trick_cards.clear()

    def add_trick_win(self, user_id: int):
        self.player_scores[user_id] = (
            self.player_scores.get(user_id, 0) + 1
        )
        self.completed_tricks += 1

    def is_trick_complete(self) -> bool:
        return len(self.trick_cards) == 2

    def set_winner(self, user_id: int):
        self.winner_id = user_id
        self.game_over = True

    def reset_trick(self):
        self.clear_trick()
        self.completed_tricks = 0

    def to_dict(self):
        return {
            "room_id": self.room_id,
            "current_turn": self.current_turn,
            "trump": self.trump,
            "trick_cards": [
                {
                    "user_id": user_id,
                    "card": card.to_dict(),
                }
                for user_id, card in self.trick_cards
            ],
            "completed_tricks": self.completed_tricks,
            "player_scores": self.player_scores,
            "round_number": self.round_number,
            "game_over": self.game_over,
            "winner_id": self.winner_id,
        }
