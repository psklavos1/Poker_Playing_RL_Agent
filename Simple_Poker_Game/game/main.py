import numpy as np
import matplotlib.pyplot as plt


from utils import print_card
from simple_poker_game import SimplePokerGame
from random_agent import RandomAgent
from threshold_agent import ThresholdAgent
from policy_iteration import PolicyIterationAgent
from simple_player import PlayerStatus
from q_learning import QLearningAgent
from human_agent import HumanAgent

player_types = {0: "Random Agent", 1: "Threshold Loose Agent", 2: "Threshold Tight Agent", 3: "Policy Iteration Agent", 4: "Q-Learning Agent", 5: "Human Agent"}

cum_reward_list = []
avg_reward_list = []
players = []

# cummulative_rewards = np.zeros()

"""
    Run an experiment and print the results of each round.
    Args:
        agent: input 0, means Random Agent
               input 1, means Threshold Aggresive
               input 2, means Threshold Defensive
    """
def print_experiment():
    print("================= Simple Hold 'em Variation Example =================")
    
    #-------------------- Choose Opponents -------------------#
    print("Choose Player One:")
    players_ids = []
    while True:
        p1 = input("0: {:<20} | 1: {:<30} | 2: {:<30} | 3: {:<30}| 4: {:<30} | 5: {:<30}".format(player_types[0], player_types[1], player_types[2], player_types[3], player_types[4], player_types[5]))

        if p1 in ['0', '1', '2', '3', '4', '5']:
            p1 = int(p1)
            players_ids.append(p1)
            break
        else: print("Invalid Input!")
    
    print("Choose Player Two:")
    while True:
        p2 = input("0: {:<20} | 1: {:<30} | 2: {:<30} | 3: {:<30}| 4: {:<30} | 5: {:<30}".format(player_types[0], player_types[1], player_types[2], player_types[3], player_types[4], player_types[5]))
        if p2 in ['0', '1', '2', '3', '4', '5']:
            p2 = int(p2)
            players_ids.append(p2)
            break
        else: print("Invalid Input!")
    print(f"\n{player_types[p1]} VS {player_types[p2]}") 
    input("Press Enter to Start\n")   
    
    #-------------------- Initialize Opponents -------------------#
    for j,i in enumerate(players_ids):
        if i == 0:
            players.append(RandomAgent())
        elif i == 1:
            players.append(ThresholdAgent(aggro = True))
        elif i == 2:
            players.append(ThresholdAgent(aggro = False))
        elif i == 3:
            players.append(PolicyIterationAgent(adversary=players_ids[(j+1)%2]))
        elif i == 4:
            players.append(QLearningAgent(id=j))
        elif i == 5: 
            players.append(HumanAgent())

    
    if player_types[p1] != player_types[p2]:
        game = SimplePokerGame(p1_name = player_types[p1], p2_name = player_types[p2],stacks= 20)
    else:
        game = SimplePokerGame(p1_name = "" + player_types[p1] + "_1", p2_name = "" + player_types[p2] + "_2",stacks= 20)
         

    # If we have Q-Learning we specify opponent and train
    for i,p in enumerate(players):
        if p.get_type() == "Q-Learning Agent":
            print("Started Training Q-Learning Agent")
            p.train_agent(game,adversary=players[(i+1)%2])
            p.print_q_table()
            input("Training complete. Press Enter")
    
    
    #-------------------- Start Game Loop -------------------#
    num_hands_played = 0
    game_on = True
    while game_on: 
        # print("\n--------------------------------- Start a new Round ---------------------------------")
        num_hands_played +=1
        game = play_round(num_hands_played, game, players)
        
        payoffs = game.get_payoffs()
        
        # Careful problem is policy vs policy are chosen
        for id,p in enumerate(players):
            if p.get_type() == "Policy Iteration Agent" or p.get_type() == "Q-Learning Agent" :
                update_reward_list(payoffs[id])
        
        # If round over Print Showdown
        print_showdown(game,payoffs)
        
        # Check if game is over
        if game.is_over():
            game_on = False
            break
        # input('Press Enter to advance to new round!\n\n')
    # When The game is over print the final winner
    print_winner(game)
    plot_rewards()
    
def update_reward_list(reward):
    cum_reward_list.append(reward) if len(cum_reward_list)==0 else cum_reward_list.append(cum_reward_list[-1] + reward)
    avg_reward_list.append(cum_reward_list[-1]/len(cum_reward_list))
     
    
def plot_rewards():
    for p,player in enumerate(players):
        if player.get_type() == "Policy Iteration Agent":
            plt.xlabel("Round") 
            plt.ylabel("Cumulative Reward") 
            plt.title(f"Cumulative Reward for Policy Iteration Agent") 
            plt.plot(np.arange(1, len(cum_reward_list)+1), cum_reward_list, label = 'Policy Cumulative Reward')
            plt.legend() 
            plt.show()
            
            plt.xlabel("Round") 
            plt.ylabel("Average Reward per Round") 
            plt.title(f"Average Reward for Policy Iteration Agent") 
            plt.plot(np.arange(1, len(avg_reward_list)+1), avg_reward_list, label = 'Policy Average Reward')
            plt.legend() 
            plt.show()
            
            

def play_round(round,game,players):
    print(f"\n\n============================= Round {round} =============================")
    print("\n================= Public Cards =================")
    print_card([None, None])
    
    # Round starts
    state, _ = game.init_game()
    print("Pot: ", state['pot'],"\n")
    
    public_printed = False
    while not game.round_over():
        
        # If not First Round print once the public cards
        if state['round']>0 and not public_printed:
            print("\n================= Public Cards =================")
            print_card(state['public_cards'])
            print("Pot: ", state['pot'],"\n")
            public_printed = True    
            
        # Print the current player's hand
        print("\n========= Player: ", game.players[game.game_pointer].my_name(), " =========")
        # We see only cards of player 0: To simulate being in his side in the table 
        print("Card: ")
        print_card(state['hand'] if game.game_pointer == 0 else None)
        print("Stack at Start: ", state['stack'])
        print("In Chips: ", state['my_chips'])
        
        if len(state['legal_actions']) > 1: # If Someone not All-In. Action 
            # input("Press enter for adversary to move")
            print("Legal actions:", state['legal_actions'])
            action = players[game.get_player_id()].step(state)
            print("Action chosen:", action)
        else: # Else. Go on untill round finishes
            action = state['legal_actions'][0]
            print("Simulate to end as player is all in")
        # Proced in game
        state, _, _ = game.step(action)
    return game

def print_winner(game):
    bankrupt_p = 0
    for id, p in enumerate(game.players): 
        if p.stack == 0:
            bankrupt_p = id
    print("\n\nThe Player ", game.players[bankrupt_p].my_name() ," Is Bankrupt!\nTherefore The Winner Is ", game.players[(bankrupt_p+1)%2].my_name())
    for p, player in enumerate(players):
        if player.get_type() =="Policy Iteration Agent" or player.get_type() =="Q-Learning Agent":
            print("Average reward at the end of the game for Agent: {:.2f}".format(avg_reward_list[-1]))
        
    
    # print(f"Average Cumulative Reward of player: {game.players[0].my_name()} => {res[0]}\nAverage Cumulative Reward of player: {game.players[1].my_name()} => {res[1]}\n")
   
        
def print_showdown(game,payoffs):
    ''' Get the perfect information of the current state

    Returns:
        (dict): A dictionary of all the perfect information of the current state
    '''
    
    print("\n\n==================== Showdown =================")
    state = game.get_state(game.get_player_id())
    print("\nPublic Cards:")
    if state['public_cards']:
        print_card(state['public_cards'])
    else: print_card([None ,None])
    
    folded_players = [1 if p.status == PlayerStatus.FOLDED else 0 for p in game.players]
    if sum(folded_players) >0:
        print("Winner due to fold")
        
    print("Player ", game.players[0].my_name()," Hand: ")
    hand = [c.get_index() for c in game.players[0].hand]
    print_card(hand)
    
    print("Player ", game.players[1].my_name()," Hand: ")
    hand = [c.get_index() for c in game.players[1].hand]
    print_card(hand)
    
    
    if np.amax(payoffs) != 0:
        max_index = np.argmax(payoffs)  # Find the maximum value
        print("Player ", game.players[max_index].my_name(), " wins: ", state['all_chips'][(max_index+1)%2])
    else: 
        print("Players Split The Pot: To Each Are Returned: ", state['pot']/2)
        
    
def main():
    # Set the number of players
    print_experiment()

if __name__ == "__main__":
    main()