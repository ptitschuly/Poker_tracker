from poker_logic import create_deck, Card, Hand, RANKS, SUITS
import random
from deuces import Card as DeucesCard, Evaluator


evaluator = Evaluator() # Créez une instance de l'évaluateur une seule fois

def calculate_equity_fast(hero_hand, opponent_range, community_cards, num_simulations=10000):
    """
    Calculates equity using the ultra-fast 'deuces' library.
    """
    if not opponent_range: return 1.0

    # Convertir les cartes communautaires au format deuces
    deuces_community = [DeucesCard.new(c.rank + c.suit) for c in community_cards]
    
    # Convertir la main du héros au format deuces
    deuces_hero_hand = [DeucesCard.new(c.rank + c.suit) for c in hero_hand.cards]

    deck = create_deck()
    known_cards = set(hero_hand.cards) | set(community_cards)
    deck -= known_cards

    valid_opponent_range = {
        opp_hand for opp_hand in opponent_range 
        if not known_cards.intersection(set(opp_hand.cards))
    }

    if not valid_opponent_range: return 1.0

    wins, ties, total_simulations = 0, 0, 0
    num_cards_to_draw = 5 - len(community_cards)
    sims_per_hand = max(1, num_simulations // len(valid_opponent_range))

    for opp_hand in valid_opponent_range:
        deuces_opp_hand = [DeucesCard.new(c.rank + c.suit) for c in opp_hand.cards]
        matchup_deck = list(deck - set(opp_hand.cards))
        
        if len(matchup_deck) < num_cards_to_draw: continue

        for _ in range(sims_per_hand):
            total_simulations += 1
            runout = random.sample(matchup_deck, num_cards_to_draw)
            deuces_runout = [DeucesCard.new(c.rank + c.suit) for c in runout]
            
            board = deuces_community + deuces_runout
            
            # Évaluation ultra-rapide
            hero_score = evaluator.evaluate(board, deuces_hero_hand)
            opp_score = evaluator.evaluate(board, deuces_opp_hand)

            if hero_score < opp_score: # Note : pour deuces, un score plus bas est meilleur
                wins += 1
            elif hero_score == opp_score:
                ties += 1
    
    if total_simulations == 0: return 1.0
    return (wins + 0.5 * ties) / total_simulations

def parse_range_string(range_string):
    """
    Parses a standard poker range string (e.g., "JJ+, AKs, 76s, T9o, QQ")
    into a set of Hand objects.
    """
    hands = set()
    # Normalize and split the input string
    range_parts = [part.strip() for part in range_string.replace(' ', '').split(',') if part]

    for part in range_parts:
        if len(part) < 2:
            continue

        # Handle pairs (e.g., QQ, JJ+)
        if part[0] == part[1]:
            rank1 = part[0].upper()
            if rank1 not in RANKS: continue

            # Handle pair+ (e.g., JJ+)
            if len(part) == 3 and part[2] == '+':
                start_index = RANKS.index(rank1)
                for r_idx in range(start_index, len(RANKS)):
                    rank = RANKS[r_idx]
                    # Add all 6 combinations for this pair
                    for i, s1 in enumerate(SUITS):
                        for j, s2 in enumerate(SUITS):
                            if i < j:
                                hands.add(Hand(Card(rank, s1), Card(rank, s2)))
            # Handle specific pair (e.g., QQ)
            elif len(part) == 2:
                # Add all 6 combinations for this pair
                for i, s1 in enumerate(SUITS):
                    for j, s2 in enumerate(SUITS):
                        if i < j:
                            hands.add(Hand(Card(part[0], s1), Card(part[0], s2)))

        # Handle non-pairs (e.g., AKs, T9o, QJs+)
        elif len(part) >= 3:
            rank1, rank2 = part[0].upper(), part[1].upper()
            suit_info = part[2].lower()

            if rank1 not in RANKS or rank2 not in RANKS: continue
            
            # Ensure rank1 is the higher rank for consistency
            if RANKS.index(rank1) < RANKS.index(rank2):
                rank1, rank2 = rank2, rank1

            # Handle suited 's' or off-suit 'o'
            if suit_info in ['s', 'o']:
                is_suited = (suit_info == 's')
                
                # Handle plus notation for non-pairs (e.g., AJs+, KTs+)
                if len(part) == 4 and part[3] == '+':
                    start_rank2_idx = RANKS.index(rank2)
                    for r2_idx in range(start_rank2_idx, RANKS.index(rank1)):
                        current_rank2 = RANKS[r2_idx]
                        if is_suited: # 4 suited combos
                            for suit in SUITS:
                                hands.add(Hand(Card(rank1, suit), Card(current_rank2, suit)))
                        else: # 12 off-suit combos
                            for s1 in SUITS:
                                for s2 in SUITS:
                                    if s1 != s2:
                                        hands.add(Hand(Card(rank1, s1), Card(current_rank2, s2)))
                # Handle specific hand (e.g., AKs, T9o)
                else:
                    if is_suited: # 4 suited combos
                        for suit in SUITS:
                            hands.add(Hand(Card(rank1, suit), Card(rank2, suit)))
                    else: # 12 off-suit combos
                        for s1 in SUITS:
                            for s2 in SUITS:
                                if s1 != s2:
                                    hands.add(Hand(Card(rank1, s1), Card(rank2, s2)))
    return hands

def calculate_chip_ev(scenario, player_name, opponent_range_string, player_action, bet_size=0.0, use_icm=False, payout_structure=None):
    """
    Calculates the expected value (EV) of a poker action in chips.
    This implementation assumes a 1-vs-1 scenario for the EV calculation.
    """
    hero = next((p for p in scenario.players if p.name == player_name), None)
    if not hero or not hero.hole_cards:
        raise ValueError("Hero or hero's hole cards not found.")

    # For simplicity, this assumes one opponent.
    opponent = next((p for p in scenario.players if p.name != player_name), None)
    if not opponent:
        raise ValueError("Opponent not found.")

    # The EV of folding is the baseline, which is 0. We don't lose any more chips.
    if player_action == 'fold':
        return 0.0

    # Parse the opponent's range from the string
    opponent_range = parse_range_string(opponent_range_string)
    
    # Calculate equity against the opponent's range
    equity = calculate_equity_fast(hero.hole_cards, opponent_range, scenario.community_cards)

    # Corrected EV Calculation:
    # EV = (Equity * Reward) - ((1 - Equity) * Risk)
    # Reward = The total pot size if you win (current pot + opponent's call)
    # Risk = The amount you are putting into the pot for this action.

    if player_action == 'call':
        # Your risk is the size of the call.
        risk = bet_size
        # The reward is the pot before you call, plus the opponent's bet you are calling.
        # This is equivalent to the current pot size.
        reward = scenario.pot
        ev = (equity * reward) - ((1 - equity) * risk)
        return ev
    
    elif player_action == 'raise':
        # Simplified model: Assumes opponent always calls the raise.
        # Your risk is the total size of your raise.
        risk = bet_size
        # The reward is the pot before you raise, plus the opponent's implied call amount.
        # The opponent must call your 'bet_size' to continue.
        reward = scenario.pot + bet_size
        ev = (equity * reward) - ((1 - equity) * risk)
        return ev

    return 0.0 # Should not be reached

