import numpy as np
from utils import rank2int


class ThresholdAgent():
    def __init__(self, aggro = True):
       self.random = np.random
       self.aggro = aggro
    
    def loose_play(self,state):
        # Case we have only one choice
        if len(state['legal_actions']) == 1:
            return state['legal_actions'][0]
        rand = np.random.random()
        # Preflop strategy
        if state['round'] == 0:        
            if state['hand'][0][1] == 'A' or state['hand'][0][1] == 'K' or state['hand'][0][1] == 'Q':
                return state['legal_actions'][-1]

            else:
                if 'check' in state['legal_actions']:
                    return 'check'
                else: return 'call' 
                    
        else: # Post Flop
            num_of_connections = 0
            # check if he has connection to board
            for i in range(len(state['public_cards'])):
                if state['hand'][0][1] == state['public_cards'][i][1]: 
                    num_of_connections += 1
            # with connection bet (play most aggresive option)
            if num_of_connections > 0:
                return state['legal_actions'][-1]
            else: 
                # else if he has nothing leave
                return state['legal_actions'][-1] if rand<0.1 else state['legal_actions'][0]
                
                    
    def tight_play(self,state):
        # Case we have only one choice
        if len(state['legal_actions']) == 1:
            return state['legal_actions'][0]
        rand = np.random.random()
        # Preflop strategy
        if state['round'] == 0:        
            if state['hand'][0][1] == 'A':
                if 'bet' in state['legal_actions']:
                    return 'bet'
                else:
                    return 'raise' if 'raise' in state['legal_actions'] else 'call'
            elif state['hand'][0][1] == 'K':
                return 'bet' if 'bet' in state['legal_actions'] else 'call'
            elif state['hand'][0][1] == 'Q':
                return 'check' if 'check' in state['legal_actions'] else 'call'
            else:
                return 'check' if 'check' in state['legal_actions'] else 'fold'
                    
        else: # Post Flop
            public_ranks = (state['public_cards'][0][1], state['public_cards'][1][1])
            sorted_table_cards = sorted(public_ranks, key=lambda x: rank2int(x), reverse=True)
            connections = [1 if state['hand'][0][1] == sorted_table_cards[i] else 0 for i in range(len(sorted_table_cards)) ]
            # with connection
            if sum(connections) > 0:
                if sum(connections) > 0:
                    return 'bet' if 'bet' in state['legal_actions'] else 'call'
                else:
                    # return 'check' if 'check' in state['legal_actions'] else 'call'
                    return state['legal_actions'][0]
            else: 
                # else if he has nothing leave
                return state['legal_actions'][0]
           
                
    def step(self,state):
        if self.aggro:
            return self.loose_play(state)
        else: 
            return self.tight_play(state)
    
    def get_type(self):
        return "Threshold Loose Agent" if self.aggro else "Threshold Tight Agent"