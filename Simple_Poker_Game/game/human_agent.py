import numpy as np

class HumanAgent():
       
    def __init__(self):
       self.random = np.random
       
    def step(self,state):
        legal_actions = state['legal_actions']
        
        while True:
            print("Legal actions", str(legal_actions))
            action = input("Select one of the legal actions:")
            if action in legal_actions:
                return action
            else: print("Invalid Input!")

    def get_type(self):
        return "Human Agent"