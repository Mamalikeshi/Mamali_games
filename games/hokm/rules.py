class HokmRules:

    SUITS = {
        "hearts",
        "diamonds",
        "clubs",
        "spades",
    }

    @staticmethod
    def valid_trump(suit: str) -> bool:
        return suit in HokmRules.SUITS

    @staticmethod
    def can_play_card(
        card,
        hand,
        trick_cards,
        trump,
    ):
        if card not in hand:
            return False

        if not trick_cards:
            return True

        first_card = trick_cards[0][1]
        lead_suit = first_card.suit

        # اگر بازیکن کارت از رنگ شروع Trick دارد،
        # باید همان رنگ را بازی کند.
        if any(
            c.suit == lead_suit
            for c in hand
        ):
            return card.suit == lead_suit

        # اگر از رنگ شروع ندارد، می‌تواند
        # کارت دیگری از جمله حکم بازی کند.
        return True

    @staticmethod
    def card_power(card, lead_suit, trump):
        if card.suit == trump:
            return 100 + card.rank_value

        if card.suit == lead_suit:
            return 50 + card.rank_value

        return card.rank_value

    @staticmethod
    def determine_trick_winner(
        trick_cards,
        trump,
    ):
        if len(trick_cards) != 2:
            return None

        first_user, first_card = trick_cards[0]
        second_user, second_card = trick_cards[1]

        lead_suit = first_card.suit

        first_power = HokmRules.card_power(
            first_card,
            lead_suit,
            trump,
        )

        second_power = HokmRules.card_power(
            second_card,
            lead_suit,
            trump,
        )

        if second_power > first_power:
            return second_user

        return first_user
