
import numpy as np
import itertools
from utils import rank2int
from config import generate_state_space, generate_transition_model

class PolicyIterationAgent():
    
    def __init__(self,adversary):
        self.V = None
        self.prev_V = None
        self.Q = None
        self.new_pi = None
        self.pi = None
        self.policy = None
        
        self.random = np.random
        self.adversary_type = adversary
        
        self.cards = ['T', 'J', 'Q', 'K', 'A']
        
        # The actions are modeled through pick_action(), to take represent 2
        # different choices depending on the options available.
        # The choices could be one of the 2 groups [check, bet] and [fold, call.raise](mostly)
        # Below are the representations for each action
        # fold => bet/fold (bluff)
        # check => check/fold
        # bet => bet/call
        # call => check/call
        # raise => bet/raise
        self.actions = {0:'fold', 1:'check', 2:'bet', 3:'call', 4:'raise'}
        self.table_cards = list(itertools.combinations_with_replacement(self.cards, 2))
    
        self.state_space = generate_state_space()
        self.transition_model = generate_transition_model(self.adversary_type,self.state_space)
        # print(len(self.state_space))
        
        # print(len(self.transition_model))
        
    def get_type(self):
        return "Policy Iteration Agent"

    
    # policy iteration is simple, it will call alternatively policy evaluation then policy improvement, till the policy converges.
    def policy_iteration(self, P, gamma = 1, epsilon = 1e-10):
        t = 0
        random_actions = np.random.choice(tuple(P[0].keys()), len(P))     # start with random actions for each state  
        # print(random_actions)
        pi = lambda s: {s:a for s, a in enumerate(random_actions)}[s]     # and define your initial policy pi_0 based on these action (remember, we are passing policies around as python "functions", hence the need for this second line)
        
        # print("print\n",P[0][1])
        while True:
            old_pi = {s: pi(s) for s in range(len(P))}  #keep the old policy to compare with new
            V = self.policy_evaluation(pi,P,gamma,epsilon)   #evaluate latest policy --> you receive its converged value function
            pi = self.policy_improvement(V,P,gamma)          #get a better policy using the value function of the previous one just calculated 
            
            t += 1
            if old_pi == {s:pi(s) for s in range(len(P))}: # you have converged to the optimal policy if the "improved" policy is exactly the same as in the previous step
                break
        print('converged after %d iterations' %t) #keep track of the number of (outer) iterations to converge
        return V,pi
    
    def policy_evaluation(self,pi, P, gamma = 1.0, epsilon = 1e-10):  #inputs: (1) policy to be evaluated, (2) model of the environment (transition probabilities, etc., see previous cell), (3) discount factor (with default = 1), (4) convergence error (default = 10^{-10})
        t = 0   #there's more elegant ways to do this
        prev_V = np.zeros(len(P)) # use as "cost-to-go", i.e. for V(s')
        while True:
            V = np.zeros(len(P)) # current value function to be learnerd
            for s in range(len(P)):  # do for every state
                # calculate one Bellman step --> i.e., sum over all probabilities of transitions and reward for that state, the action suggested by the (fixed) policy, the reward earned (dictated by the model), and the cost-to-go from the next state (which is also decided by the model)
                
                for prob, next_state, reward, done in P[s][pi(s)]:  
                    V[s] += prob * (reward + gamma * prev_V[next_state] * (not done))
            if np.max(np.abs(prev_V - V)) < epsilon: #check if the new V estimate is close enough to the previous one; 
                break # if yes, finish loop
            prev_V = V.copy() #freeze the new values (to be used as the next V(s'))
            t += 1
        return V

    def policy_improvement(self, V, P, gamma=1):  # takes a value function (as the cost to go V(s')), a model, and a discount parameter
        Q = np.zeros((len(P), len(P[0])), dtype=np.float64) #create a Q value array
        for s in range(len(P)):        # for every state in the environment/model
            for a in range(len(P[s])):  # and for every action in that state
                for prob, next_state, reward, done in P[s][a]:  #evaluate the action value based on the model and Value function given (which corresponds to the previous policy that we are trying to improve) 
                    Q[s][a] += prob * (reward + gamma * V[next_state] * (not done))
        new_pi = lambda s: {s:a for s, a in enumerate(np.argmax(Q, axis=1))}[s]  # this basically creates the new (improved) policy by choosing at each state s the action a that has the highest Q value (based on the Q array we just calculated)
        # lambda is a "fancy" way of creating a function without formally defining it (e.g. simply to return, as here...or to use internally in another function)
        # you can implement this in a much simpler way, by using just a few more lines of code -- if this command is not clear, I suggest to try coding this yourself
        
        return new_pi

    def get_state(self,raw_state):
        public_cards = (raw_state['public_cards'][0][1], raw_state['public_cards'][1][1]) if raw_state['public_cards'] else None
        public_cards = sorted(public_cards, key=lambda x: rank2int(x), reverse=False) if public_cards else None
        state = (raw_state['hand'][0][1] , (public_cards[0],public_cards[1])) if public_cards else (state['hand'][0][1] , None)
        return state
    
    def step(self, state):
        if not self.policy:
            _,pi = self.policy_iteration(self.transition_model,gamma=.95)
            pi = {s: pi(s) for s in range(len(self.transition_model))}
            self.policy = pi
        
        public_cards = (state['public_cards'][0][1], state['public_cards'][1][1]) if state['public_cards'] else None
        public_cards = sorted(public_cards, key=lambda x: rank2int(x), reverse=False) if public_cards else None
        
        s = (state['hand'][0][1] , (public_cards[0],public_cards[1])) if public_cards else (state['hand'][0][1] , None)
        # print(state)
        # print(s)
        action_key = self.policy[self.state_space[s]]
        chosen_action = self.actions[action_key]
        # print("Initial decision:" + chosen_action)
        
        action  = self.pick_action(s, self.policy,state['legal_actions'])
        # print(f"Action Chosen By Policy Iteration Agent: {action}")
        return action
            
    def pick_action(self,state, policy , legal_actions):
        
        action_key = policy[self.state_space[state]]
        chosen_action = self.actions[action_key]
        # print(chosen_action)
        
        if len(legal_actions) == 1:
            return legal_actions[0]
        
        if chosen_action in legal_actions:
            return chosen_action
        else:
            if chosen_action == 'fold':
                return 'bet'
            elif chosen_action == 'check':
                return 'fold'
            elif chosen_action == 'bet': # bet call
                if 'raise' in legal_actions:
                   return 'call' #if rand<0.7 else 'raise'
                else: return 'call'
            elif chosen_action == 'call': # check call
                return 'check' #if rand<0.8 else 'bet'
            elif chosen_action == 'raise': # bet raise  
                return 'bet' if 'bet' in legal_actions else 'call'
            else: return 'check'
            
    
    
   