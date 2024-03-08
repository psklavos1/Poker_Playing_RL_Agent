from enum import Enum

class PlayerStatus(Enum):
    ALIVE = 0
    FOLDED = 1
    ALLIN = 2

class SimplePlayer:

    def __init__(self, player_id, np_random, stack=20, name="Bot"):
        """
        Initialize a player.
        Args:
            player_id (int): The id of the player
        """
        self.np_random = np_random
        self.player_id = player_id
        self.hand = []
        self.init_stack = stack
        self.stack = stack
        self.name = name
        self.status = PlayerStatus.ALIVE

        # The chips that this player has put in until now
        self.in_chips = 0
        
    def update_in_chips(self, chips_to_add):

        if self.stack - self.in_chips - chips_to_add > 0:
            self.in_chips += chips_to_add 
        else:
            # print("Player is now All-in") 
            self.in_chips += self.stack - self.in_chips
            self.status = PlayerStatus.ALLIN
    
    def round_reset(self):
        self.hand = []
        self.status = PlayerStatus.ALIVE
        self.in_chips = 0
    
    def stack_reset(self):
        self.stack = self.init_stack
    
    def get_state(self, legal_actions, chips, public_cards=None):
        """
        Encode the state for the player

        Args:
            public_cards (list): A list of public cards that seen by all the players
        Returns:
            (dict): The state of the player
        """
        dict = {
            'hand': [c.get_index() for c in self.hand],
            'stack': self.stack,
            'all_chips': chips,
            'my_chips': self.in_chips,
            'legal_actions': legal_actions,
        }
        if public_cards == None:
            dict.update({'public_cards': None}) 
        else:
            dict.update({'public_cards': [c.get_index() for c in public_cards]}) 
        return dict
    
    def get_player_id(self):
        return self.player_id

    def my_name(self):
        return self.name