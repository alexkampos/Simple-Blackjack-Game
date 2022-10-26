import abc
import random

# SUIT,RANK,VALUE
suits = ('Hearts', 'Diamonds', 'Spades', 'Clubs')
ranks = ('Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King', 'Ace')
values = {
    'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5, 'Six': 6, 'Seven': 7, 'Eight': 8,
    'Nine': 9, 'Ten': 10, 'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': (1, 11)
}
used_cards = []


# CARD
class Card:

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.value = values[rank]

    def __str__(self):
        return self.rank + " of " + self.suit


# DECK
class Deck:

    def __init__(self):
        self.all_cards = []

        for suit in suits:
            for rank in ranks:
                # Create the Card Object
                created_card = Card(suit, rank)

                self.all_cards.append(created_card)

    def shuffle(self):
        random.shuffle(self.all_cards)

    def deal_one(self):
        last_card = self.all_cards.pop(-1)
        if not self.all_cards:
            for item in used_cards:
                self.all_cards.append(item)
            used_cards.clear()
            self.shuffle()
        return last_card


# PLAYER
class Player:
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.cards_dealt = []
        self.cards_sum = 0

    def remove_all_cards_dealt(self):
        self.cards_dealt = []

    def add_cards(self, new_cards):
        if type(new_cards) == type([]):
            # List of multiple Card objects
            self.cards_dealt.extend(new_cards)
        else:
            # For a single Card object
            self.cards_dealt.append(new_cards)

    def move_cards_dealt_to_used(self, used_cards):
        for item in self.cards_dealt:
            used_cards.append(item)
        self.cards_dealt.clear()

    def compute_sum(self):
        aces_count = 0
        cards_sum = 0
        for card in self.cards_dealt:
            if card.rank == 'Ace':
                aces_count += 1
            else:
                cards_sum += card.value

        # check player's difference from getting busted
        dif_to_bust = 22 - cards_sum
        cards_sum_with_aces_count = cards_sum + aces_count

        # if giving to player's aces value one still gets the player busted
        # then we are returning the sum + aces values as one since the player loses either way
        if aces_count >= dif_to_bust:
            return cards_sum_with_aces_count
        # else is checked if one of the aces could take value of eleven
        else:
            if cards_sum_with_aces_count + 10 <= 21:
                return cards_sum_with_aces_count + 10
            else:
                return cards_sum_with_aces_count

    @abc.abstractmethod
    def decide_next_step(self, *args):
        """Function deciding what should the next step be on the game based on player's cards"""
        return


# PLAYER
class Human(Player):

    def __init__(self):
        self.bank = 200
        self.bet = 0
        Player.__init__(self)

    def __str__(self):
        return f"Player's sum is {self.cards_sum}"

    def decide_next_step(self, new_deck):
        end_game = False
        first_iteration = True
        while True:
            self.cards_sum = self.compute_sum()
            if self.cards_sum > 21:
                print(f'You got busted! Sum: {self.cards_sum} \nDealer Wins!')
                self.bank -= self.bet
                end_game = True
                return end_game
            elif self.cards_sum == 21:
                if first_iteration:
                    print(f'You got a Blackjack!!! Sum: {self.cards_sum}')
                else:
                    print(f'Nice! Sum: {self.cards_sum}')
                return end_game
            else:
                first_iteration = False
                hit_or_hold_value = hit_or_hold()
                if hit_or_hold_value == 'HOLD':
                    return end_game
                else:
                    self.add_cards(new_deck.deal_one())
                    print(f"Player's cards are: {', '.join(card.__str__() for card in self.cards_dealt)}")


# DEALER
class Dealer(Player):

    def __init__(self):
        Player.__init__(self)

    def __str__(self):
        return f"Dealer's sum is {self.cards_sum}"

    def decide_next_step(self, new_deck, human_player):
        end_game = False
        while True:
            self.cards_sum = self.compute_sum()
            print(f"Dealer's cards are: {', '.join(card.__str__() for card in self.cards_dealt)}")
            if self.cards_sum > 21:
                print(f"Dealer got busted! Sum: {self.cards_sum} \nPlayer Wins!")
                human_player.bank += human_player.bet
                end_game = True
                return end_game
            elif self.cards_sum < 17:
                print('Dealer draws')
                self.add_cards(new_deck.deal_one())
            #   Dealer stops drawing if his sum is equal or bigger to 17
            else:
                print('Dealer holds')
                return end_game


def deal_new_hand():
    deal_hand = input("Should I deal you a hand? (Y/N) ")
    while deal_hand != 'Y' and deal_hand != 'N':
        deal_hand = input("Please answer with a Y for yes or an N for no. \nShould I deal you a hand? (Y/N) ")

    return deal_hand


def get_players_bet(bank):
    players_bet = input(f"Budget: {bank}. Please make a bet: ")
    while True:
        try:
            players_bet_int = int(players_bet)
        except ValueError:
            players_bet = input("Bet should be an integer.\nPlease make a valid bet: ")
        else:
            if players_bet_int > bank:
                players_bet = input("Bet shouldn't be bigger than your bank.\nPlease make a valid bet: ")
            else:
                return players_bet_int


def hit_or_hold():
    should_hit_or_hold = input("Would you like another card? (Y/N) ")
    while True:
        if should_hit_or_hold == 'Y':
            return 'HIT'
        elif should_hit_or_hold == 'N':
            return 'HOLD'
        else:
            should_hit_or_hold = input("Please answer with a Y for yes or an N for no. \n"
                                       "Would you like another card? (Y/N) ")


def check_winner(player, dealer):
    print(f"Player's sum: {player.cards_sum} \nDealer's sum: {dealer.cards_sum}")
    if player.cards_sum > dealer.cards_sum:
        print('Player wins!')
        player.bank += player.bet
    else:
        print("Dealer wins!")
        player.bank -= player.bet


# GAME SETUP
def game_setup():
    player = Human()
    dealer = Dealer()
    new_deck = Deck()
    new_deck.shuffle()

    while True:
        player.move_cards_dealt_to_used(used_cards)
        dealer.move_cards_dealt_to_used(used_cards)
        if player.bank > 0 and deal_new_hand() == 'Y':
                player.bet = get_players_bet(player.bank)

                # Deal 2 cards to player, both up
                player.add_cards([new_deck.deal_one(), new_deck.deal_one()])
                print(f"Player's cards are: {', '.join(card.__str__() for card in player.cards_dealt)}")

                # Deal 2 cards to dealer, one up one down
                dealer.add_cards([new_deck.deal_one(), new_deck.deal_one()])
                print(f"Dealer's cards are: HIDDEN CARD,"
                      f" {', '.join(card.__str__() for card in dealer.cards_dealt[1:])}")

                end_game = player.decide_next_step(new_deck)

                if end_game:
                    continue

                end_game = dealer.decide_next_step(new_deck, player)

                if end_game:
                    continue

                check_winner(player, dealer)
        else:
            break

    print("Thank you for playing. See you again soon!")


if __name__ == '__main__':
    game_setup()
