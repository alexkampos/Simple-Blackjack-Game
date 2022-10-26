import unittest
from unittest.mock import patch
from blackjack import Player, Card, Deck, Human, Dealer, suits, ranks, \
    deal_new_hand, get_players_bet, hit_or_hold, check_winner, game_setup


class TestDeck(unittest.TestCase):

    def test_deal_one(self):
        new_deck = Deck()
        last_deck_element = new_deck.all_cards[-1]
        self.assertTrue(new_deck.all_cards.count(last_deck_element))

        last_deck_element_popped = new_deck.deal_one()
        self.assertEqual(last_deck_element, last_deck_element_popped)
        self.assertFalse(new_deck.all_cards.count(last_deck_element))


class TestPlayer(unittest.TestCase):

    def test_add_cards(self):
        player = Human()
        # assert list is empty
        assert not player.cards_dealt

        card_one = Card(suits[0], ranks[0])
        card_two = Card(suits[1], ranks[1])
        card_three = Card(suits[2], ranks[2])
        player.add_cards(card_one)
        player.add_cards([card_two, card_three])

        self.assertTrue({card_one, card_two, card_three}.issubset(player.cards_dealt))

    def test_compute_sum_with_no_aces(self):
        player = Human()
        card_one = Card('Hearts', 'Queen')
        card_two = Card('Spades', 'King')
        player.add_cards([card_one, card_two])

        self.assertEqual(20, player.compute_sum())

    def test_compute_sum_for_one_ace_as_eleven(self):
        player = Human()
        card_one = Card('Hearts', 'Ace')
        card_two = Card('Spades', 'Five')
        player.add_cards([card_one, card_two])

        self.assertEqual(16, player.compute_sum())

    def test_compute_sum_for_one_ace_as_one(self):
        player = Human()
        card_one = Card('Hearts', 'Ace')
        card_two = Card('Spades', 'Six')
        card_three = Card('Hearts', 'King')
        player.add_cards([card_one, card_two, card_three])

        self.assertEqual(17, player.compute_sum())

    def test_compute_sum_for_two_aces_as_eleven_and_one(self):
        player = Human()
        card_one = Card('Hearts', 'Ace')
        card_two = Card('Spades', 'Ace')
        card_three = Card('Spades', 'Nine')
        player.add_cards([card_one, card_two, card_three])

        self.assertEqual(21, player.compute_sum())

    def test_compute_sum_for_two_aces_as_one_and_one(self):
        player = Human()
        card_one = Card('Hearts', 'Ace')
        card_two = Card('Spades', 'Ace')
        card_three = Card('Spades', 'King')
        card_four = Card('Spades', 'Nine')
        player.add_cards([card_one, card_two, card_three, card_four])

        self.assertEqual(21, player.compute_sum())

    def test_compute_sum_for_three_aces_as_eleven_one_and_one(self):
        player = Human()
        card_one = Card('Hearts', 'Ace')
        card_two = Card('Spades', 'Ace')
        card_three = Card('Diamonds', 'Ace')
        card_four = Card('Spades', 'Five')
        player.add_cards([card_one, card_two, card_three, card_four])

        self.assertEqual(18, player.compute_sum())

    def test_compute_sum_for_three_aces_as_one_one_and_one(self):
        player = Human()
        card_one = Card('Hearts', 'Ace')
        card_two = Card('Spades', 'Ace')
        card_three = Card('Diamonds', 'Ace')
        card_four = Card('Spades', 'King')
        card_five = Card('Diamonds', 'Seven')
        player.add_cards([card_one, card_two, card_three, card_four, card_five])

        self.assertEqual(20, player.compute_sum())

    def test_compute_sum_for_four_aces_as_eleven_one_one_and_one(self):
        player = Human()
        card_one = Card('Hearts', 'Ace')
        card_two = Card('Spades', 'Ace')
        card_three = Card('Diamonds', 'Ace')
        card_four = Card('Clubs', 'Ace')
        card_five = Card('Diamonds', 'Six')
        player.add_cards([card_one, card_two, card_three, card_four, card_five])

        self.assertEqual(20, player.compute_sum())

    def test_compute_sum_for_four_aces_as_one_one_one_and_one(self):
        player = Human()
        card_one = Card('Hearts', 'Ace')
        card_two = Card('Spades', 'Ace')
        card_three = Card('Diamonds', 'Ace')
        card_four = Card('Clubs', 'Ace')
        card_five = Card('Diamonds', 'Six')
        card_six = Card('Diamonds', 'King')
        player.add_cards([card_one, card_two, card_three, card_four, card_five, card_six])

        self.assertEqual(20, player.compute_sum())

    def test_move_cards_dealt_to_used(self):
        used_cards = []
        player = Human()
        card_one = Card('Hearts', 'Ace')
        card_two = Card('Spades', 'Ace')
        player.add_cards([card_one, card_two])
        player.move_cards_dealt_to_used(used_cards)
        self.assertTrue(card_one in used_cards)
        self.assertTrue(card_two in used_cards)
        assert not player.cards_dealt


class TestHuman(unittest.TestCase):

    @patch.object(Player, 'compute_sum', lambda *args: 25)
    def test_decide_next_step_when_sum_over_21(self):
        new_deck = Deck()
        player = Human()
        player.bet = 20
        end_game = player.decide_next_step(new_deck)

        self.assertEqual(player.bank, 180)
        self.assertTrue(end_game)

    @patch.object(Player, 'compute_sum', lambda *args: 21)
    def test_decide_next_step_when_blackjack(self):
        new_deck = Deck()
        player = Human()
        end_game = player.decide_next_step(new_deck)

        self.assertFalse(end_game)

    @patch.object(Player, 'compute_sum', lambda *args: 17)
    @patch('blackjack.hit_or_hold', lambda *args: 'HOLD')
    def test_decide_next_step(self):
        new_deck = Deck()
        player = Human()
        end_game = player.decide_next_step(new_deck)

        self.assertFalse(end_game)


class TestDealer(unittest.TestCase):

    @patch.object(Player, 'compute_sum', lambda *args: 25)
    def test_decide_next_step_when_sum_over_21(self):
        new_deck = Deck()
        player = Human()
        dealer = Dealer()
        player.bet = 20
        end_game = dealer.decide_next_step(new_deck, player)

        self.assertEqual(player.bank, 220)
        self.assertTrue(end_game)

    @patch.object(Player, 'compute_sum', lambda *args: 18)
    def test_decide_next_step_when_over_17(self):
        new_deck = Deck()
        player = Human()
        dealer = Dealer()
        end_game = dealer.decide_next_step(new_deck, player)

        self.assertFalse(end_game)


class TestBlackjack(unittest.TestCase):

    @patch('builtins.input', lambda *args: 'Y')
    def test_deal_new_hand_for_yes(self):
        result = deal_new_hand()
        self.assertEqual('Y', result)

    @patch('builtins.input', lambda *args: 'N')
    def test_deal_new_hand_for_no(self):
        result = deal_new_hand()
        self.assertEqual('N', result)

    @patch('builtins.input', lambda *args: '20')
    def test_get_players_bet(self):
        result = get_players_bet(200)
        self.assertEqual(20, result)

    @patch('builtins.input', lambda *args: 'Y')
    def test_hit_or_hold_for_yes(self):
        result = hit_or_hold()
        self.assertEqual('HIT', result)

    @patch('builtins.input', lambda *args: 'N')
    def test_hit_or_hold_for_no(self):
        result = hit_or_hold()
        self.assertEqual('HOLD', result)

    def test_check_winner_when_player_wins(self):
        player = Human()
        dealer = Dealer()
        player.cards_sum = 20
        dealer.cards_sum = 18
        player.bet = 20
        check_winner(player, dealer)

        self.assertEqual(player.bank, 220)

    def test_check_winner_when_dealer_wins(self):
        player = Human()
        dealer = Dealer()
        player.cards_sum = 17
        dealer.cards_sum = 19
        player.bet = 20
        check_winner(player, dealer)

        self.assertEqual(player.bank, 180)


if __name__ == '__main__':
    unittest.main()
