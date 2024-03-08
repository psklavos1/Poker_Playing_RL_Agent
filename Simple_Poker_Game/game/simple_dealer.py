from utils import Card

class SimpleDealer():
    def __init__(self, np_random):
        self.np_random = np_random
        self.deck = self.init_deck()
        self.shuffle()
        self.pot = 0
        
    def init_deck(self):
        suit_list = ['S', 'H', 'D', 'C']
        rank_list = ['T', 'J', 'Q', 'K', 'A']
        res = [Card(suit, rank) for suit in suit_list for rank in rank_list]
        return res
    
    def get_deck(self):
        return self.deck
    
    def shuffle(self):
        self.np_random.shuffle(self.deck)

    def deal_card(self):
        """
        Deal one card from the deck

        Returns:
            (Card): The drawn card from the deck
        """
        return self.deck.pop()