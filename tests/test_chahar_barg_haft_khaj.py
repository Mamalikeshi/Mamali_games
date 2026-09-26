from games.chahar_barg.card import Card
from games.chahar_barg.rules import count_clubs


def test_haft_khaj_player_with_more_clubs():
    player_a_cards = [
        Card(suit="clubs", rank="A"),
        Card(suit="clubs", rank="2"),
        Card(suit="clubs", rank="3"),
        Card(suit="clubs", rank="4"),
        Card(suit="clubs", rank="5"),
        Card(suit="clubs", rank="6"),
        Card(suit="clubs", rank="7"),
    ]

    player_b_cards = [
        Card(suit="clubs", rank="8"),
        Card(suit="clubs", rank="9"),
        Card(suit="clubs", rank="10"),
        Card(suit="clubs", rank="J"),
        Card(suit="clubs", rank="Q"),
        Card(suit="clubs", rank="K"),
    ]

    assert count_clubs(player_a_cards) == 7
    assert count_clubs(player_b_cards) == 6

    assert count_clubs(player_a_cards) > count_clubs(
        player_b_cards
    )


def test_haft_khaj_player_b_with_more_clubs():
    player_a_cards = [
        Card(suit="clubs", rank="A"),
        Card(suit="clubs", rank="2"),
        Card(suit="clubs", rank="3"),
        Card(suit="clubs", rank="4"),
        Card(suit="clubs", rank="5"),
    ]

    player_b_cards = [
        Card(suit="clubs", rank="6"),
        Card(suit="clubs", rank="7"),
        Card(suit="clubs", rank="8"),
        Card(suit="clubs", rank="9"),
        Card(suit="clubs", rank="10"),
        Card(suit="clubs", rank="J"),
        Card(suit="clubs", rank="Q"),
        Card(suit="clubs", rank="K"),
    ]

    assert count_clubs(player_a_cards) == 5
    assert count_clubs(player_b_cards) == 8

    assert count_clubs(player_b_cards) > count_clubs(
        player_a_cards
    )


def test_all_13_clubs_are_accounted_for():
    player_a_cards = [
        Card(suit="clubs", rank="A"),
        Card(suit="clubs", rank="2"),
        Card(suit="clubs", rank="3"),
        Card(suit="clubs", rank="4"),
        Card(suit="clubs", rank="5"),
        Card(suit="clubs", rank="6"),
        Card(suit="clubs", rank="7"),
    ]

    player_b_cards = [
        Card(suit="clubs", rank="8"),
        Card(suit="clubs", rank="9"),
        Card(suit="clubs", rank="10"),
        Card(suit="clubs", rank="J"),
        Card(suit="clubs", rank="Q"),
        Card(suit="clubs", rank="K"),
    ]

    total_clubs = (
        count_clubs(player_a_cards)
        + count_clubs(player_b_cards)
    )

    assert total_clubs == 13
