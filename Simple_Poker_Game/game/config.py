import itertools
from utils import rank2int

cards = ['T', 'J', 'Q', 'K', 'A']
actions = {0:'fold', 1:'check', 2:'bet', 3:'call', 4:'raise'}
table_cards = list(itertools.combinations_with_replacement(cards, 2))

def generate_state_space():
    state_space = {}
    id = 0
    for player_card in cards:
        state_space[(player_card, None)] = id  # Round 1 state with no table cards
        id+=1
        
        for table_card in table_cards:
            state_space[(player_card, table_card)] = id  # Round 2 state with table cards
            id+=1
                
    state_space[("Terminal", None)] = id # Terminal state where the showdown is happening
    
    # print("States:\n",state_space)
    # print("States:\n",len(state_space))
    return state_space

def generate_transition_model(adversary,state_space):
    transition_model = {}
    
    for id, state in enumerate(state_space):
        
        player_card, table_cards = state
        transition_model[id] = {}
    
        if table_cards is None:
            # First round transition model
            for action in actions:
                transition_model[id][action] = pre_flop_transition(state,action,adversary,state_space)
        else:
            # Second round transition model
            for action in actions:
                transition_model[id][action] = post_flop_transition(state,action,adversary,state_space)
        # print("State", state , " Transition: " ,transition_model[id], "\n\n")
    
    # print("Transitions:\n",transition_model[state_space[('T',None)]][1])
    # print(transition_model[state_space[('K', ('J', 'A'))]])
    
    return transition_model


def pre_flop_transition(state, action, adversary,state_space):
    if adversary == 0:
        return pre_flop_random(state, action,state_space)
    elif adversary == 1:
        return pre_flop_threshold_loose(state, action,state_space)
    else:
        return pre_flop_threshold_tight(state, action,state_space)

def post_flop_transition(state, action, adversary,state_space):
    if adversary == 0:
        return post_flop_random(state, action,state_space)
    elif adversary == 1:
        return post_flop_threshold_loose(state, action,state_space)
    else:
        return post_flop_threshold_tight(state, action,state_space)

    
def get_next_states_with_player_card(player_card,state_space):
    return [state for state in state_space if state[0] == player_card and state[1]]

def append_mult_states(transition,all_states,reward,terminal,state_space):
    for next_state in all_states:
        connections = 0
        my_card = next_state[0]
        table_cards = next_state[1]
        for table_card in table_cards:
            if my_card == table_card: connections +=1

        num_combs = 0
        if connections == 2:
            num_combs = 1 
            transition.append(((3/19)*(2/18)/num_combs, state_space[next_state], reward ,terminal))
        elif connections == 1:
            num_combs = 4
            transition.append(((3/19)+(3/19)-(3/19)*(2/18)/num_combs, state_space[next_state], reward ,terminal))
        else: 
            num_combs = 10
            transition.append(((1-(3/19)*(2/18)-(3/19)-(3/19)+(3/19)*(2/18))/num_combs, state_space[next_state], reward ,terminal))
            
    
###########################################################################
#                                                                         #
#                                                                         #
#--------------------- TRANSITION MODELS GENERATION ----------------------#
#                                                                         #
#                                                                         #
########################################################################### 
     
def pre_flop_random(state, action,state_space):
    player_card, _ = state

    transition = []
    if player_card == "Terminal":
        transition.append((1, state_space[("Terminal", None)], 0, True))
    else:
        post_flop_states = get_next_states_with_player_card(player_card,state_space)
        # [(probability, next_state, reward, terminal)]
        if action == 0: 
            transition.append((1, state_space[("Terminal", None)], 0, True))
        elif action == 1:
            append_mult_states(transition,post_flop_states,1,False,state_space)
        elif action == 2:
            append_mult_states(transition,post_flop_states,2,False,state_space)
        elif action == 3:
            append_mult_states(transition,post_flop_states,2,False,state_space)
        else: # raise
            append_mult_states(transition,post_flop_states,5,False,state_space)         
    return transition

#############################################################################################
def pre_flop_threshold_loose(state, action,state_space):
    player_card, _ = state

    transition = []
    if player_card == "Terminal":
        transition.append((1, state_space[("Terminal", None)], 0, True))
    else:
        post_flop_states = get_next_states_with_player_card(player_card,state_space)
        if(player_card == 'A'):
            # [(probability, next_state, reward, terminal)]
            if action == 0: 
                transition.append((1, state_space[("Terminal", None)], -3, True))
            elif action == 1:
                append_mult_states(transition,post_flop_states,1,False,state_space)
            elif action == 2:
                append_mult_states(transition,post_flop_states,3,False,state_space)
            elif action == 3:
                append_mult_states(transition,post_flop_states,2,False,state_space)
            else: # raise
                append_mult_states(transition,post_flop_states,5,False,state_space)         
                
        elif(player_card == 'K'):
            # [(probability, next_state, reward, terminal)]
            if action == 0:
                transition.append((1, state_space[("Terminal", None)], -3, True))
            elif action == 1:
                append_mult_states(transition,post_flop_states,-2,False,state_space)
            elif action == 2:
                append_mult_states(transition,post_flop_states,5,False,state_space)
            elif action == 3:
                append_mult_states(transition,post_flop_states, 4,False,state_space)
            else: # raise
                append_mult_states(transition,post_flop_states, 2,False,state_space)
                
        elif(player_card == 'Q'):
            # [(probability, next_state, reward, terminal)]
            if action == 0:
                transition.append((1, state_space[("Terminal", None)],-2 , True))
            elif action == 1:
                append_mult_states(transition,post_flop_states, 2,False,state_space)
            elif action == 2:
                append_mult_states(transition,post_flop_states, 2,False,state_space)
            elif action == 3:
                append_mult_states(transition,post_flop_states, 4,False,state_space)
            else: # raise
                append_mult_states(transition,post_flop_states,-3,False,state_space)
        elif(player_card == 'J'):
            # [(probability, next_state, reward, terminal)]
            if action == 0:
                transition.append((1, state_space[("Terminal", None)], 3, True))
            elif action == 1:
                append_mult_states(transition,post_flop_states,5,False,state_space)
            elif action == 2:
                append_mult_states(transition,post_flop_states,-3,False,state_space)
            elif action == 3:
                append_mult_states(transition,post_flop_states,-4,False,state_space)
            else: # raise
                append_mult_states(transition,post_flop_states,-5,False,state_space)
        else: #(player_card == 'T'):
            # [(probability, next_state, reward, terminal)]
            if action == 0:
                transition.append((1, state_space[("Terminal", None)], 3, True))
            elif action == 1:
                append_mult_states(transition,post_flop_states,5,False,state_space)
            elif action == 2:
                append_mult_states(transition,post_flop_states,-4,False,state_space)
            elif action == 3:
                append_mult_states(transition,post_flop_states,-5,False,state_space)
            else: # raise
                append_mult_states(transition,post_flop_states,-5,False,state_space)
    return transition

#############################################################################################
def pre_flop_threshold_tight(state, action,state_space):
    player_card, _ = state

    transition = []
    if player_card == "Terminal":
        transition.append((1, state_space[("Terminal", None)], 0, True))
    else:
        post_flop_states = get_next_states_with_player_card(player_card,state_space)
        if(player_card == 'A'):
            # [(probability, next_state, reward, terminal)]
            if action == 0: 
                transition.append((1,state_space[("Terminal", None)], -5, True))
            elif action == 1:
                append_mult_states(transition,post_flop_states,-3,False,state_space)
            elif action == 2:
                append_mult_states(transition,post_flop_states,4,False,state_space)
            elif action == 3:
                append_mult_states(transition,post_flop_states,3,False,state_space)
            else: # raise
                append_mult_states(transition,post_flop_states,5,False,state_space)         
                
        elif(player_card == 'K'):
            # [(probability, next_state, reward, terminal)]
            if action == 0:
                transition.append((1, state_space[("Terminal", None)], -4, True))
            elif action == 1:
                append_mult_states(transition,post_flop_states,-2,False,state_space)
            elif action == 2:
                append_mult_states(transition,post_flop_states,4,False,state_space)
            elif action == 3:
                append_mult_states(transition,post_flop_states,1,False,state_space)
            else: # raise
                append_mult_states(transition,post_flop_states,2,False,state_space)
                
        elif(player_card == 'Q'):
            # [(probability, next_state, reward, terminal)]
            if action == 0:
                transition.append((1, state_space[("Terminal", None)], -2, True))
            elif action == 1:
                append_mult_states(transition,post_flop_states,0,False,state_space)
            elif action == 2:
                append_mult_states(transition,post_flop_states,4,False,state_space)
            elif action == 3:
                append_mult_states(transition,post_flop_states,3,False,state_space)
            else: # raise
                append_mult_states(transition,post_flop_states,-4,False,state_space)
        elif(player_card == 'J'):
            # [(probability, next_state, reward, terminal)]
            if action == 0:
                transition.append((1, state_space[("Terminal", None)], 1, True))
            elif action == 1:
                append_mult_states(transition,post_flop_states,3,False,state_space)
            elif action == 2:
                append_mult_states(transition,post_flop_states,-5,False,state_space)
            elif action == 3:
                append_mult_states(transition,post_flop_states,4,False,state_space)
            else: # raise
                append_mult_states(transition,post_flop_states,-5,False,state_space)
        else: #(player_card == 'T'):
            # [(probability, next_state, reward, terminal)]
            if action == 0:
                transition.append((1, state_space[("Terminal", None)], 1, True))
            elif action == 1:
                append_mult_states(transition,post_flop_states,3,False,state_space)
            elif action == 2:
                append_mult_states(transition,post_flop_states,-5,False,state_space)
            elif action == 3:
                append_mult_states(transition,post_flop_states,1,False,state_space)
            else: # raise
                append_mult_states(transition,post_flop_states,-5,False,state_space)
    return transition

####################################### POST FLOP #############################################
def post_flop_random(state, action,state_space):
    player_card, table_cards = state
    transition = []
    
    if player_card == "Terminal":
        transition.append((1, state_space[("Terminal", None)], 0, True))
    
    terminal_state = len(state_space)-1
    
    if action == 0:
        transition.append((1, state_space[("Terminal", None)], -5, True))
    elif action == 1:
        transition.append((1,terminal_state,-5,True))
    elif action == 2:
        transition.append((1,terminal_state,-5,True))
    elif action == 3:
        transition.append((1,terminal_state,-5,True))
    else: # raise
        transition.append((1,terminal_state,5,True))          
    return transition  

#############################################################################################
def post_flop_threshold_loose(state, action,state_space):
    
    player_card, table_cards = state
    transition = []
    
    if player_card == "Terminal":
        transition.append((1, state_space[("Terminal", None)], 0, True))
    
    terminal_state = len(state_space)-1
    sorted_table_cards = sorted(table_cards, key=lambda x: rank2int(x), reverse=True)
    connections = [1 if player_card == sorted_table_cards[i] else 0 for i in range(len(table_cards)) ]
    # If there is a triplet
    if sum(connections) == 2:
        if action == 0:
            transition.append((1,state_space[("Terminal", None)], -5, True))
        elif action == 1:
            transition.append((1,terminal_state,-5,True))
        elif action == 2:
            transition.append((1,terminal_state,3,True))
        elif action == 3:
            transition.append((1,terminal_state,2,True))
        else: # raise
            transition.append((1,terminal_state,5,True))          
    
    # 1 pair
    elif sum(connections) == 1:
        # top pair
        if connections[0] == 1:
            if action == 0:
                transition.append((1, state_space[("Terminal", None)], -5, True))
            elif action == 1:
                transition.append((1,terminal_state,-5,True))
            elif action == 2:
                transition.append((1,terminal_state,3,True))
            elif action == 3:
                transition.append((1,terminal_state,2,True))
            else: # raise
                transition.append((1,terminal_state,5,True))
        # second pair
        else:
            if action == 0:
                transition.append((1,state_space[("Terminal", None)], -4, True))
            elif action == 1:
                transition.append((1,terminal_state,-3,True))
            elif action == 2:
                transition.append((1,terminal_state,5,True))
            elif action == 3:
                transition.append((1,terminal_state,2,True))
            else: # raise
                transition.append((1,terminal_state,2,True))
    # High card
    else:
        if action == 0:
            transition.append((1,state_space[("Terminal", None)], 3 , True))
        elif action == 1:
            transition.append((1,terminal_state,1,True))
        elif action == 2:
            transition.append((1,terminal_state, -2 ,True))
        elif action == 3:
            transition.append((1,terminal_state,-5,True))
        else: # raise
            transition.append((1,terminal_state,-5,True))
        # if player_card == 'A':
        #     if action == 0:
        #         transition.append((1,state_space[(player_card, None)], -3 , True))
        #     elif action == 1:
        #         transition.append((1,terminal_state,1,True))
        #     elif action == 2:
        #         transition.append((1,terminal_state, 2 ,True))
        #     elif action == 3:
        #         transition.append((1,terminal_state,5,True))
        #     else: # raise
        #         transition.append((1,terminal_state,-5,True))
        # elif player_card == 'K':
        #     if action == 0:
        #         transition.append((1, state_space[(player_card, None)], -1, True))
        #     elif action == 1:
        #         transition.append((1,terminal_state,-1,True))
        #     elif action == 2:
        #         transition.append((1,terminal_state,1,True))
        #     elif action == 3:
        #         transition.append((1,terminal_state,5,True))
        #     else: # raise
        #         transition.append((1,terminal_state,-5,True))
        # else: # for Q,J ,T, very difficult to win
        #     if action == 0:
        #         transition.append((1,state_space[(player_card, None)], 5, True))
        #     elif action == 1:
        #         transition.append((1,terminal_state,5,True))
        #     elif action == 2:
        #         transition.append((1,terminal_state,-4,True))
        #     elif action == 3:
        #         transition.append((1,terminal_state,-5,True))
        #     else: # raise
        #         transition.append((1,terminal_state,-5,True))
    return transition  
#############################################################################################
def post_flop_threshold_tight(state, action,state_space):

    player_card, table_cards = state
    transition = []
    
    if player_card == "Terminal":
        transition.append((1, state_space[("Terminal", None)], 0, True))
    
    terminal_state = len(state_space)-1
    sorted_table_cards = sorted(table_cards, key=lambda x: rank2int(x), reverse=True)
    connections = [1 if player_card == sorted_table_cards[i] else 0 for i in range(len(table_cards)) ]
    
    # For this speciic opponent the fold action will be modeled as 
    # fold if fold available else bluff  
    
    # If there is a triplet
    if sum(connections) == 2:
        if action == 0:
            transition.append((1, terminal_state, -3, True))
        elif action == 1:
            transition.append((1,terminal_state,-5,True))
        elif action == 2:
            transition.append((1,terminal_state,3,True))
        elif action == 3:
            transition.append((1,terminal_state,2,True))
        else: # raise
            transition.append((1,terminal_state,5,True))          
    
    # 1 pair
    elif sum(connections) == 1:
        # top pair
        if connections[0] == 1:
            if action == 0:
                transition.append((1,terminal_state, -3, True))
            elif action == 1:
                transition.append((1,terminal_state,-5,True))
            elif action == 2:
                transition.append((1,terminal_state,3,True))
            elif action == 3:
                transition.append((1,terminal_state,2,True))
            else: # raise
                transition.append((1,terminal_state,5,True))
        # second pair raises only with top so we take advantage with bluff
        else:
            if action == 0:
                transition.append((1, terminal_state, 5, True))
            elif action == 1:
                transition.append((1,terminal_state,2,True))
            elif action == 2:
                transition.append((1,terminal_state,-3,True))
            elif action == 3:
                transition.append((1,terminal_state,-4,True))
            else: # raise
                transition.append((1,terminal_state,-5,True))
    # High card
    else:
        if player_card == 'A':
            if action == 0:
                transition.append((1,terminal_state, 5,True))
            elif action == 1:
                transition.append((1,terminal_state,3,True))
            elif action == 2:
                transition.append((1,terminal_state,-5,True))
            elif action == 3:
                transition.append((1,terminal_state,-5,True))
            else: # raise
                transition.append((1,terminal_state,-5,True))
        elif player_card == 'K':
            if action == 0:
                transition.append((1,terminal_state, 4,True))
            elif action == 1:
                transition.append((1,terminal_state,3,True))
            elif action == 2:
                transition.append((1,terminal_state,-5,True))
            elif action == 3:
                transition.append((1,terminal_state,-5,True))
            else: # raise
                transition.append((1,terminal_state,-5,True))
        else: # for Q,J ,T, very difficult to win
            if action == 0:
                transition.append((1,terminal_state, 3, True))
            elif action == 1:
                transition.append((1,terminal_state,5,True))
            elif action == 2:
                transition.append((1,terminal_state,-4,True))
            elif action == 3:
                transition.append((1,terminal_state,-5,True))
            else: # raise
                transition.append((1,terminal_state,-5,True))
    return transition  


###########################################################################
#                                                                         #
#                                                                         #
#--------------------- Q-Learning Rewards Generation ---------------------#
#                                                                         #
#                                                                         #
########################################################################### 

    
    # Intermediate states or initial states
   
        # player_card, table_cards = state
        # # pre-flop.
        # if not table_cards:
        #     if player_card == 'A':
        #         if action == 0:
        #             return -5
        #         elif action == 1:
        #             return -3
        #         elif action == 2:
        #             return 4
        #         elif action == 3:
        #             return 2
        #         else:
        #             return 5
        #     elif player_card == 'K':
        #         if action == 0:
        #             return -4
        #         elif action == 1:
        #             return -2
        #         elif action == 2:
        #             return 3
        #         elif action == 3:
        #             return 3
        #         else:
        #             return 3
        #     elif player_card == 'Q':
        #         if action == 0:
        #             return -1
        #         elif action == 1:
        #             return 0
        #         elif action == 2:
        #             return -1
        #         elif action == 3:
        #             return 1
        #         else:
        #             return -4
        #     else: 
        #         if action == 0:
        #             return 3
        #         elif action == 1:
        #             return 4
        #         elif action == 2:
        #             return -3
        #         elif action == 3:
        #             return -2
        #         else:
        #             return -5
        # # post flop
        # else:
        #     sorted_table_cards = sorted(table_cards, key=lambda x: rank2int(x), reverse=True)
        #     connections = [1 if player_card == sorted_table_cards[i] else 0 for i in range(len(table_cards)) ]
        #     # If there is a triplet or top pair
        #     if sum(connections) == 2 or sum(connections) == 1 and connections[0] == 1:
        #         if action == 0:
        #             return -5
        #         elif action == 1:
        #             return -4
        #         elif action == 2:
        #             return 4
        #         elif action == 3:
        #             return 2
        #         else: # raise
        #             return 5          
            
        #     # bottom pair
        #     elif connections[1] == 1:
        #         if action == 0:
        #             return -4
        #         elif action == 1:
        #             return -2
        #         elif action == 2:
        #             return 3
        #         elif action == 3:
        #             return 4
        #         else: # raise
        #             return 2
        #     # High card
        #     else:
        #         if player_card == 'A':
        #             if action == 0:
        #                 return -2
        #             elif action == 1:
        #                 return 1
        #             elif action == 2:
        #                 return -1
        #             elif action == 3:
        #                 return 3
        #             else: # raise
        #                 return -5
        #         elif player_card == 'K':
        #             if action == 0:
        #                 return -1
        #             elif action == 1:
        #                 return 2
        #             elif action == 2:
        #                 return -2
        #             elif action == 3:
        #                 return 1
        #             else: # raise
        #                 return -5
        #         else: # for Q,J,T, very difficult to win
        #             if action == 0:
        #                 return -1
        #             elif action == 1:
        #                 return -1
        #             elif action == 2:
        #                 return -3
        #             elif action == 3:
        #                 return -4
        #             else: # raise
        #                 return -5
                            
            