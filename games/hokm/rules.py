from .card import Card


CARD_VALUES = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 14,
}


def can_play_card(
    card: Card,
    hand: list[Card],
    trick_cards: list[tuple[int, Card]],
) -> bool:
    """
    بررسی می‌کند که آیا بازیکن اجازه دارد این کارت را بازی کند.

    قانون:
    اگر بازیکن کارت هم‌خال با کارت اول دست داشته باشد،
    باید همان خال را بازی کند.
    """

    if not trick_cards:
        return True

    lead_suit = trick_cards[0][1].suit

    has_lead_suit = any(
        hand_card.suit == lead_suit
        for hand_card in hand
    )

    if has_lead_suit:
        return card.suit == lead_suit

    return True


def card_strength(card: Card) -> int:
    return CARD_VALUES[card.rank]


def determine_trick_winner(
    trick_cards: list[tuple[int, Card]],
    trump: str,
) -> int:
    """
    مشخص می‌کند چه کسی برنده این Trick شده است.
    """

    if len(trick_cards) != 2:
        raise ValueError("A two-player trick must contain exactly two cards.")

    lead_suit = trick_cards[0][1].suit

    winner_user_id, winner_card = trick_cards[0]

    for user_id, card in trick_cards[1:]:
        current_wins = False

        # حکم از هر خالی به جز حکم قوی‌تر است.
        if card.suit == trump and winner_card.suit != trump:
            current_wins = True

        # اگر هر دو حکم باشند، رتبه کارت تعیین‌کننده است.
        elif card.suit == trump and winner_card.suit == trump:
            current_wins = (
                card_strength(card)
                > card_strength(winner_card)
            )

        # اگر کارت جدید حکم نیست ولی کارت فعلی هم حکم نیست،
        # فقط کارت هم‌خال با خال شروع می‌تواند برنده شود.
        elif (
            card.suit == lead_suit
            and winner_card.suit != trump
        ):
            if winner_card.suit != lead_suit:
                current_wins = True
            else:
                current_wins = (
                    card_strength(card)
                    > card_strength(winner_card)
                )

        if current_wins:
            winner_user_id = user_id
            winner_card = card

    return winner_user_id


def validate_trump(suit: str) -> bool:
    return suit in {
        "hearts",
        "diamonds",
        "clubs",
        "spades",
    }
