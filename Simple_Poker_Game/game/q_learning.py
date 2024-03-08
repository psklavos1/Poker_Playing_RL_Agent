import itertools
import numpy as np
import matplotlib.pyplot as plt
import time




from utils import rank2int
from config import generate_state_space

class QLearningAgent:
    def __init__(self, id, learning_rate= .1, discount_factor=.95):
        self.actions = ['fold', 'check', 'bet', 'call', 'raise']
        self.num_actions = len(self.actions)
        self.cards = ['T', 'J', 'Q', 'K', 'A']
        self.table_cards = list(itertools.combinations_with_replacement(self.cards, 2))
        self.my_id = id
        self.state_space = generate_state_space()
        self.num_states = len(self.state_space)
        
        # Define a list to store the rewards for each episode
        self.cumulative_rewards = []
        self.avg_reward = []
        
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = 1
        
        self.q_table = np.zeros((self.num_states, self.num_actions))

    def get_type(self):
        return "Q-Learning Agent"

    
    def pick_action(self, state, legal_actions, epsilon):
        action_values = self.q_table[self.state_space[state]]  # Get the Q-values for the current state
        legal_action_values = [action_values[action] for action in range(len(legal_actions))]  # Filter Q-values for legal actions
        
        if np.random.uniform(0, 1) < epsilon:
            # Explore by choosing a random action
            action_index = np.random.choice(len(legal_action_values),1)[0]
            action = legal_actions[action_index]  # Get the corresponding legal action
        else:
            # Exploit by choosing the action with maximum Q-value
            action_index = np.argmax(legal_action_values)  # Get the index of the action with the maximum Q-value
            action = legal_actions[action_index]  # Get the corresponding legal action
            
        return action


    def update_q_table(self, state, action, reward, next_state):
        action_index = self.actions.index(action)
        current_q = self.q_table[self.state_space[state], action_index] 
        max_q = np.max(self.q_table[self.state_space[next_state]])
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_q - current_q)
        
        self.q_table[self.state_space[state], action_index] = new_q
        
    def get_state(self,raw_state):
        public_cards = (raw_state['public_cards'][0][1], raw_state['public_cards'][1][1]) if raw_state['public_cards'] else None
        public_cards = sorted(public_cards, key=lambda x: rank2int(x), reverse=False) if public_cards else None
        state = (raw_state['hand'][0][1] , (public_cards[0],public_cards[1])) if public_cards else (raw_state['hand'][0][1] , None)
        return state
    
    def train_agent(self,game, adversary, num_episodes = 1_000_000,  threshold = 0.0001):
        # Record the starting time
        start_time = time.time()

        for episode in range(num_episodes):
            raw_state,_ = game.init_game()  # Reset the environment to start a new episode
            for player in game.players:
                player.stack_reset()
            
            done = False
            self.epsilon = (episode+1)**(-1/4)
            
            state_to_update = ()
            action_to_update = ""
            to_update = False
            prev_q_table = self.q_table.copy()
            episode_reward = 0.0
            
            while not done:
                # Print the legal actions

                my_player = True if game.get_player_id() == self.my_id else False
                
                if my_player:   
                    action = self.pick_action(self.get_state(raw_state), raw_state['legal_actions'], self.epsilon)
                    state_to_update = self.get_state(raw_state)
                    action_to_update = action
                else:
                    action = adversary.step(raw_state)
                    
                raw_next_state, _,bet_round_over = game.step(action)
                done = game.round_over()
                
                reward = self.get_reward(game)
                episode_reward += reward
                
                if my_player: 
                    to_update = True if bet_round_over or done else False
                else:
                    to_update = not to_update
                
                # update Q tabke==le
                if len(state_to_update) != 0 and to_update:
                    my_card = state_to_update[0]
                    public_cards = (self.get_state(raw_next_state)[1][0], self.get_state(raw_next_state)[1][1]) if self.get_state(raw_next_state)[1] else None 
                    next_state = (my_card,public_cards) 
                    self.update_q_table(state_to_update, action_to_update, reward, next_state)
                
                raw_state = raw_next_state
                
            self.cumulative_rewards.append(episode_reward) if len(self.cumulative_rewards)==0 else self.cumulative_rewards.append(self.cumulative_rewards[-1] + episode_reward)            
            self.avg_reward.append(self.cumulative_rewards[-1]/len(self.cumulative_rewards))
            # Check convergence
            max_q_change = np.max(np.abs(self.q_table - prev_q_table))
            # To prevent early stage stop due to insufficient information
            if max_q_change < threshold and episode >10000:
                print(f"Q-learning converged in {episode+1} episodes")
                break
        
        # Record the ending time
        end_time = time.time()
        
        # Calculate the elapsed time
        elapsed_time = end_time - start_time

        # Print the elapsed time in seconds
        print("Elapsed time In Training: {} seconds".format(elapsed_time))
        
        # Plot the learning curve
        plt.plot(range(1, len(self.cumulative_rewards)+1), self.cumulative_rewards)
        plt.xlabel("Episode")
        plt.ylabel("Cumulative Reward Until Convergence")
        plt.title("Learning Curve")
        plt.show()
        plt.legend()
        
        plt.plot(range(1, len(self.avg_reward)+1), self.avg_reward)
        plt.xlabel("Episode")
        plt.ylabel("Average Reward Until Convergence")
        plt.title("Average Learning Curve")
        plt.show()
        plt.legend()
        
        
            
    
    def print_q_table(self):
        print("State                | Action               | Q-Value")
        print("-----------------------------------------------------")
        i = 0
        for state in self.state_space:
            s = self.state_space[state]
            for a, action in enumerate(self.actions):
                # print(state[1])
                tmp = str(state)
                # if state[0] != "Terminal":
                i+=1
                print("{:<20} | {:<20} | {:.2f}".format(tmp, action, self.q_table[s][a]),flush=True)
        # length = len(self.state_space)
        # print(f"Printed: {i}\nStates: {length} ")
        
        
    def step(self, raw_state):
        state = self.get_state(raw_state)
        action = self.pick_action(state,raw_state['legal_actions'], epsilon=0)
        
        return action
    
    def get_reward(self, game):
        # Check if it's the final state
        if game.round_over():
            payoffs = game.get_payoffs()
            return payoffs[self.my_id]
        
        # Intermediate states or initial states
        else:
            return 0