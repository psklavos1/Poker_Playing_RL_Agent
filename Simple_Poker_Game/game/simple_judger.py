from utils import rank2int
from simple_player import PlayerStatus
from simple_player import PlayerStatus

class SimpleJudger():
    
    def __init__(self, np_random):
        self.np_random = np_random
        
    def judge_game(self, players, public_cards):
        ''' Judge the winner of the game.

        Args:
            players (list): The list of players who play the game
            public_card (object): The public card that seen by all the players

        Returns:
            (list): Each entry of the list corresponds to one entry of the
        '''
        # Judge who are the winners
        winners = [0] * len(players)
        self.num_players = len(players)
        fold_count = 0
        ranks = []
        
        # If every player folds except one, the alive player is the winner
        for idx, player in enumerate(players):
            ranks.append(rank2int(player.hand[0].rank))
            if player.status == PlayerStatus.FOLDED:
                fold_count += 1
            else:
                alive_idx = idx
        if fold_count == (self.num_players - 1):
            winners[alive_idx] = 1
        
        # If not all folded then
        # Check who has the most connections to the board and highest pair
        if sum(winners) < 1:
            num_pairs = [0] * self.num_players
            for idx, player in enumerate(players):
                # get the number of connections to the board
                for i in range(len(public_cards)):
                    if player.hand[0].rank == public_cards[i].rank:
                        num_pairs[idx] += 1
            
            # if there is at least one connection to the board
            if sum(num_pairs)>0:
                max_pair_ids = []            
                # check who has most pairs
                for idx, player in enumerate(players):
                    if num_pairs[idx] == max(num_pairs):
                        max_pair_ids.append(idx)
                        
                # if there is someone with more pairs then he is the winner.
                if len(max_pair_ids) == 1: 
                    winners[max_pair_ids[0]] = 1
                else: # else winner is one with greatest rank from those with max pair
                    for i in range(len(ranks)):
                        if i not in max_pair_ids:
                            ranks[i] = ''
                    winners = self.get_winners_by_rank(ranks)
                    
        # If non of the above conditions, the winner player is the one with the highest card rank
        if sum(winners) < 1:
            winners = self.get_winners_by_rank(ranks)

        # Compute the total chips
        total = 0
        for p in players:
            total += p.in_chips

        each_win = float(total) / sum(winners)

        payoffs = []
        for i, _ in enumerate(players):
            if winners[i] == 1:
                payoffs.append(each_win - players[i].in_chips)
            else:
                payoffs.append(float(-players[i].in_chips))
        return payoffs
    
    def get_winners_by_rank(self, ranks):
        winners = [0] * self.num_players
        max_rank = max(ranks)
        max_index = [i for i, j in enumerate(ranks) if j == max_rank]
        for idx in max_index:
            winners[idx] = 1
        return winners
    
    