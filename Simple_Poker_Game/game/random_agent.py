import numpy as np

class RandomAgent():
    def __init__(self):
       self.random = np.random
       
    def step(self,state):
        legal_actions = state['legal_actions']
        return self.random.choice(legal_actions)

    def get_type(self):
        return "Random Agent"