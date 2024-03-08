import numpy as np
from copy import deepcopy, copy

from simple_judger import SimpleJudger as Judger
from simple_dealer import SimpleDealer as Dealer
from simple_player import SimplePlayer as Player,PlayerStatus
from simple_round import SimpleRound as Round

# Define the simplified poker game
class SimplePokerGame():
    
    def __init__(self, allow_step_back=False, num_players=2, p1_name="Player_1",p2_name="Player_2",stacks= 20):
        
        self.allow_step_back = allow_step_back
        self.np_random = np.random.RandomState()
        
        self.dealer = Dealer(self.np_random)
        self.num_rounds = 2  # Number of betting rounds
        self.num_private_cards = 1
        self.num_public_cards = 2
        self.num_players = num_players
        self.game_counter = 0
        # Initialize two players to play the game
        self.players = [Player(0, self.np_random, name=p1_name, stack=stacks),Player(1, self.np_random, name=p2_name,stack=stacks)]
        
        # Initialize a judger class which will decide who wins in the end
        self.judger = Judger(self.np_random)
        self.first_player = None
        # With caution
        self.small_blind = 0
        self.big_blind = 0
        self.ante = 0.5
        # self.ante = 0
        
        # Raise amount and allowed times
        self.allowed_raise_num = 2        
        self.raise_amount = 1
        
        # Save betting history
        self.history_raise_nums = [0 for _ in range(self.allowed_raise_num)]

    def init_game(self):
        self.game_counter += 1
        for player in self.players:
            player.round_reset()
       # Initialize a dealer that can deal cards
        self.dealer = Dealer(self.np_random)
        # Deal cards to each  player to prepare for the first round
        
        for i in range(self.num_private_cards * self.num_players):
            self.players[i % self.num_players].hand.append(self.dealer.deal_card())

        # Initialize public cards
        self.public_cards = []
        
        # Randomly choose a small blind and a big blind(just to keep track of who is playing)
        self.player_small = self.np_random.randint(0, self.num_players) if self.game_counter == 1 else (self.player_small + 1) % self.num_players
        self.player_big = (self.player_small + 1) % self.num_players
        # The player next to the big blind plays the first
        self.first_player = self.game_pointer = (self.player_big + 1) % self.num_players
        
        # Both players lose ante
        for i in range(self.num_players):
            self.players[i].update_in_chips(self.ante)
            self.dealer.pot = self.ante
        
        # Initialize a bidding round, in the first round, the big blind and the small blind needs to
        # be passed to the round for processing.
        self.round = Round(raise_amount=self.raise_amount,
                           allowed_raise_num=self.allowed_raise_num,
                           num_players=self.num_players,
                           np_random=self.np_random)

        self.round.start_new_round(game_pointer=self.game_pointer, raised=[p.in_chips for p in self.players])
        # Count the round. There are 2 rounds in each game.
        self.round_counter = 0
        # Save the history for stepping back to the last state.
        self.history = []
        state = self.get_state(self.game_pointer)
        # Save betting history
        self.history_raise_nums = [0 for _ in range(self.allowed_raise_num)]
        return state, self.game_pointer
    
    def step(self, action):
        """
        Get the next state

        Args:
            action (str): a specific action. (call, raise, fold, or check)

        Returns:
            (tuple): Tuple containing:

                (dict): next player's state
                (int): next player id
        """
        if self.allow_step_back:
            # First snapshot the current state
            r = deepcopy(self.round)
            b = self.game_pointer
            r_c = self.round_counter
            d = deepcopy(self.dealer)
            p = deepcopy(self.public_cards)
            ps = deepcopy(self.players)
            rn = copy(self.history_raise_nums)
            self.history.append((r, b, r_c, d, p, ps, rn))

        # Then we proceed to the next round
        self.game_pointer = self.round.proceed_round(self.players, action)
        
        # Save the current raise num to history
        self.history_raise_nums[self.round_counter] = self.round.have_raised

        
        bet_round_over = False
        # If a round is over, we deal more public cards
        if self.round.is_over():
            # For the first round, we deal 2 cards
            if self.round_counter == 0:
                self.public_cards.append(self.dealer.deal_card())
                self.public_cards.append(self.dealer.deal_card())
                bet_round_over = True
            
            self.round_counter += 1
            self.game_pointer = self.first_player
            self.round.start_new_round(self.game_pointer)

        state = self.get_state(self.game_pointer)
        

        return state, self.game_pointer , bet_round_over
    
    def step_back(self):
        """
        Return to the previous state of the game

        Returns:
            (bool): True if the game steps back successfully
        """
        if len(self.history) > 0:
            self.round, self.game_pointer, self.round_counter, self.dealer, self.public_cards, \
                self.players, self.history_raises_nums = self.history.pop()
            return True
        return False
    
    
    def get_legal_actions(self):
        """
        Return the legal actions for current player

        Returns:
            (list): A list of legal actions
        """
        # pass the player that is to play first
        return self.round.get_legal_actions(self.players)

    def get_state(self, player):
        """
        Return player's state

        Args:
            player (int): player id

        Returns:
            (dict): The state of the player
        """
        self.dealer.pot = np.sum([player.in_chips for player in self.players])
        
        chips = [self.players[i].in_chips for i in range(self.num_players)]
        legal_actions = self.get_legal_actions()
        state = self.players[player].get_state(legal_actions, chips, self.public_cards)
        state['first_player'] = self.first_player
        state['round'] = self.round_counter
        state['raise_nums'] = self.history_raise_nums
        state['pot'] = self.dealer.pot
        return state

    def get_player_id(self):
        """
        Return the current player's id

        Returns:
            (int): current player's id
        """
        return self.game_pointer
    
    
    def get_payoffs(self):
        ''' Return the payoffs of the game
        Returns:
            (list): Each entry corresponds to the payoff of one player
        '''
        chips_payoffs = self.judger.judge_game(self.players, self.public_cards)
        # was big blind but we have set to 0 in case it is used somewhere else
        payoffs = np.array(chips_payoffs) / (self.raise_amount)
        return payoffs
    
    def update_stack(self,payoffs):
        for id ,player in enumerate(self.players):
            new_stack = player.stack + payoffs[id]
            if new_stack >0:
                player.stack += payoffs[id]
            else: player.stack = 0
            
            
    def is_over(self):
        """
        Check if the game is over

        Returns:
            (boolean): True if the game is over
        """ 
        lost_players = [1 if p.stack == 0 else 0 for p in self.players]
        # If only one player is alive, the game is over.
        if sum(lost_players) > 0:
            return True
        return False
    
    def round_over(self):
        """
        Check if the game round is over

        Returns:
            (boolean): True if the round is over
        """ 
        alive_players = [1 if p.status in (PlayerStatus.ALIVE, PlayerStatus.ALLIN) else 0 for p in self.players]
        # If only one player is alive, the game is over.
        # If all rounds are finished
        if self.round_counter >= 2 or sum(alive_players) == 1:
            self.update_stack(self.get_payoffs())
            return True
        return False
    
    
    
    
    
    

