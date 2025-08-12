import tkinter as tk
from tkinter import ttk
import random
import itertools
import math

# Assume the Card, Hand, Player, and PokerScenario classes,
# as well as the RANKS, SUITS, parse_range_string,
# evaluate_seven_card_hand, create_deck, calculate_equity,
# calculate_icm, and chip_to_real_value functions
# are defined in the previous cells and available in the environment.

# If running this code block independently, you would need to include
# the definitions of Card, Hand, RANKS, SUITS, evaluate_seven_card_hand,
# create_deck, calculate_equity, calculate_icm, chip_to_real_value,
# Player, and PokerScenario here.

# For completeness and to make this block runnable locally,
# I'm including minimal definitions or placeholders for assumed existing code.
# In a real scenario where the previous cells have been run,
# these re-definitions might cause issues or be redundant.

# --- Assumed Existing Poker Logic Classes and Functions (Placeholders) ---
# You would replace these with the actual code from previous cells.

# Example Card Class (replace with your actual Card class definition)
class Card:
    RANKS = '23456789TJQKA'
    SUITS = 'cdhs' # clubs, diamonds, hearts, spades

    def __init__(self, rank, suit):
        if rank.upper() not in self.RANKS:
            raise ValueError(f"Invalid rank: {rank}")
        if suit.lower() not in self.SUITS:
            raise ValueError(f"Invalid suit: {suit}")
        self.rank = rank.upper()
        self.suit = suit.lower()

    def __str__(self):
        return f"{self.rank}{self.suit}"

    def __repr__(self):
        return f"Card('{self.rank}', '{self.suit}')"

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.rank == other.rank and self.suit == other.suit
        return False

    def __hash__(self):
        return hash((self.rank, self.suit))

    def get_rank_value(self):
        return self.RANKS.index(self.rank) + 2 # 2 has value 2, A has value 14


# Example Hand Class (replace with your actual Hand class definition)
class Hand:
    def __init__(self, card1, card2):
        if not isinstance(card1, Card) or not isinstance(card2, Card):
            raise ValueError("Hand must be created with two Card objects.")
        if card1 == card2:
             raise ValueError("A hand cannot contain duplicate cards.")
        self.cards = tuple(sorted([card1, card2], key=lambda c: c.get_rank_value(), reverse=True)) # Store cards sorted by rank

    def __str__(self):
        return f"{self.cards[0]}{self.cards[1]}"

    def __repr__(self):
        return f"Hand({repr(self.cards[0])}, {repr(self.cards[1])})"

    def __eq__(self, other):
        if isinstance(other, Hand):
            # Hands are equal if they contain the same two cards (order doesn't matter due to sorting)
            return set(self.cards) == set(other.cards)
        return False

    def __hash__(self):
        # Use a frozenset for hashing to handle order irrelevance
        return hash(frozenset(self.cards))


# Example Player Class (replace with your actual Player class definition)
class Player:
    def __init__(self, name, stack):
        if not isinstance(name, str) or not name:
            raise ValueError("Player name must be a non-empty string.")
        if not isinstance(stack, (int, float)) or stack < 0:
            raise ValueError("Player stack must be a non-negative number.")
        self.name = name
        self.stack = stack
        self.hole_cards = None # Will be a Hand object or None

    def __str__(self):
        return f"{self.name} ({self.stack}€)"

    def __repr__(self):
        return f"Player('{self.name}', {self.stack})"


# Example PokerScenario Class (replace with your actual PokerScenario class definition)
class PokerScenario:
    def __init__(self, players, small_blind, big_blind, ante=0):
        if not isinstance(players, list) or len(players) < 2 or not all(isinstance(p, Player) for p in players):
            raise ValueError("Players must be a list of at least two Player objects.")
        if not isinstance(small_blind, (int, float)) or small_blind <= 0:
             raise ValueError("Small blind must be a positive number.")
        if not isinstance(big_blind, (int, float)) or big_blind <= 0:
             raise ValueError("Big blind must be a positive number.")
        if not isinstance(ante, (int, float)) or ante < 0:
             raise ValueError("Ante must be a non-negative number.")


        self.players = players
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.ante = ante
        self.pot = 0.0
        self.community_cards = [] # List of Card objects
        self.street = "pre-flop" # Can be "pre-flop", "flop", "turn", "river"
        self.current_player_index = 0 # Index in the self.players list

        # Add blinds and antes to the pot initially (simplification for EV calculation context)
        self.pot += small_blind + big_blind + (len(players) * ante)


    def __str__(self):
        player_info = ", ".join([str(p) for p in self.players])
        community_info = ", ".join([str(c) for c in self.community_cards]) if self.community_cards else "None"
        return (
            f"Street: {self.street}\n"
            f"Players: {player_info}\n"
            f"Blinds/Ante: {self.small_blind}/{self.big_blind}/{self.ante}\n"
            f"Pot: {self.pot}€\n"
            f"Community Cards: {community_info}\n"
            f"Current Player to Act: {self.players[self.current_player_index].name}"
        )

    def add_community_cards(self, cards):
        # Simplified for EV calculation context - just adds cards without street logic
        self.community_cards.extend(cards)
        # In a full simulation, you'd update street here

    def next_street(self):
         # Placeholder for full simulation logic
         pass

    def next_player(self):
         # Placeholder for full simulation logic
         pass


# Example Poker Hand Evaluation and Deck Functions (replace with your actual implementations)
# These are complex and assumed to be in previous cells.
# For this combined block to run, you'd need the actual code for:
# RANKS, SUITS, create_deck, evaluate_seven_card_hand, parse_range_string, calculate_equity,
# _calculate_icm_recursive_correct, calculate_icm, chip_to_real_value, calculate_chip_ev.

# Minimal placeholders to avoid NameErrors if running this block alone:
RANKS = '23456789TJQKA'
SUITS = 'cdhs'

def create_deck():
    return [Card(r, s) for r in RANKS for s in SUITS]

def evaluate_seven_card_hand(cards):
    # This is a complex function. Placeholder: return a dummy rank based on pair count.
    # You need the actual implementation from previous cells.
    rank_counts = {}
    for card in cards:
        rank_counts[card.rank] = rank_counts.get(card.rank, 0) + 1
    pairs = sum(1 for count in rank_counts.values() if count >= 2)
    if pairs >= 2: return 100 # Dummy rank for two pair or better
    if pairs == 1: return 50 # Dummy rank for one pair
    return 10 # Dummy rank for high card

def parse_range_string(range_string):
     # Placeholder: return a list of dummy hands
     # You need the actual implementation from previous cells.
     print("Warning: Using placeholder parse_range_string.")
     return [Hand(Card('A','s'), Card('K','s'))] # Example dummy hand

def calculate_equity(player_hand, opponent_range, community_cards=None, num_simulations=10000):
    # Placeholder: return fixed equity
    # You need the actual implementation from previous cells.
    print("Warning: Using placeholder calculate_equity.")
    return {"win": 0.5, "loss": 0.5, "tie": 0.0}

def _calculate_icm_recursive_correct(current_stacks, current_payouts, original_player_indices):
    # Placeholder
    print("Warning: Using placeholder _calculate_icm_recursive_correct.")
    return {i: stack for i, stack in zip(original_player_indices, current_stacks)} # Dummy ICM

def calculate_icm(player_stacks, payout_structure):
    # Placeholder
    print("Warning: Using placeholder calculate_icm.")
    return player_stacks # Dummy ICM

def chip_to_real_value(total_chips_in_play, payout_structure, player_stacks_before_action, player_index, chip_change):
    # Placeholder
    print("Warning: Using placeholder chip_to_real_value.")
    return chip_change # Dummy real value change

# Actual calculate_chip_ev function from previous cell
def calculate_chip_ev(scenario, player_name, opponent_range_string, player_action, bet_size=0.0, use_icm=False, payout_structure=None):
    """
    Calculates the Chip EV or Real Money EV for a given player's decision.
    Assumes a heads-up scenario for equity calculation, but ICM can handle multiple players.

    Args:
        scenario: The current PokerScenario object.
        player_name: The name of the player whose EV is being calculated.
        opponent_range_string: A string representing the opponent's range.
        player_action: The action taken by the player ('fold', 'call', 'raise').
        bet_size: The total amount the player is putting into the pot
                  for 'call' or 'raise' actions.
        use_icm: Boolean, if True, calculates Real Money EV using ICM.
        payout_structure: Required if use_icm is True. A list of monetary payouts.

    Returns:
        The calculated EV (in chips if use_icm is False, in currency if use_icm is True).
    """
    player = None
    player_index = -1
    opponent = None
    # opponent_index = -1 # Not used in this simplified heads-up equity model

    # Find the player and determine their index
    for i, p in enumerate(scenario.players):
        if p.name == player_name:
            player = p
            player_index = i
            break # Found the player

    if player is None:
        raise ValueError(f"Player with name '{player_name}' not found in the scenario.")

    # Find the opponent for heads-up equity calculation if applicable
    # This assumes there is exactly one other player besides the current player for equity.
    if len(scenario.players) == 2:
        for p in scenario.players:
            if p.name != player_name:
                 opponent = p
                 break
    elif len(scenario.players) > 2:
         # In a multi-way pot, calculating equity against a single opponent range is a simplification.
         # A more complex model would need multi-way equity.
         # For this function, we'll proceed with the heads-up equity calculation logic,
         # meaning the 'opponent_range_string' represents the combined range of all opponents who continue.
         pass # opponent remains None, which is handled in equity calculation


    if use_icm:
        if payout_structure is None or not isinstance(payout_structure, list) or not payout_structure:
            raise ValueError("payout_structure must be provided and be a non-empty list when use_icm is True.")
        # Ensure payout structure length is <= number of players
        if len(payout_structure) > len(scenario.players):
             print("Warning: Payout structure longer than number of players. Truncating payout structure for ICM.")
             payout_structure = payout_structure[:len(scenario.players)]

    # Handle fold action first, as it doesn't require equity calculation
    if player_action.lower() == 'fold':
        # If folding, the player's chip change is 0.
        # Chip EV of folding is 0.
        # Real Money EV of folding is 0 (relative to the current real value).
        # This represents the *change* in value compared to staying pat (folding).
        return 0.0

    # For 'call' or 'raise', equity calculation is needed
    elif player_action.lower() == 'call' or player_action.lower() == 'raise':
        if bet_size < 0:
             raise ValueError("Bet size cannot be negative.")
        if player_action.lower() == 'raise' and bet_size <= 0:
             raise ValueError("Raise amount must be positive.")

        # Amount the player adds to the pot in this action
        player_contribution_this_action = bet_size
        current_pot = scenario.pot

        # Assumed opponent action: call the player's bet/raise
        # This is a simplification. Opponent might fold or re-raise.
        # For this model, we assume the opponent *calls* with their specified range.
        opponent_contribution_this_action = bet_size # Simplified: Opponent calls the player's bet_size

        # Pot size after both players have acted in this round (assuming opponent calls)
        final_pot_at_showdown = current_pot + player_contribution_this_action + opponent_contribution_this_action

        # Calculate equity assuming the hand goes to showdown after this action
        opponent_range = parse_range_string(opponent_range_string)

        # If the opponent range is empty, it means the opponent always folds to this action.
        # In this case, the player wins the current pot uncontested.
        # Chip change = current pot - player_contribution_this_action
        if not opponent_range:
             chip_change_uncontested = current_pot - player_contribution_this_action # Net chip change

             if use_icm:
                  # Calculate Real Money EV if opponent folds
                  player_stacks_before_action = [p.stack for p in scenario.players]
                  real_value_before_action = calculate_icm(player_stacks_before_action, payout_structure)[player_index]

                  # Stack after winning uncontested
                  stacks_after_uncontested_win = list(player_stacks_before_action)
                  stacks_after_uncontested_win[player_index] += chip_change_uncontested
                  # Ensure stacks remain non-negative
                  if stacks_after_uncontested_win[player_index] < 0:
                     stacks_after_uncontested_win[player_index] = 0.0

                  real_value_after_uncontested_win = calculate_icm(stacks_after_uncontested_win, payout_structure)[player_index]

                  real_money_ev_uncontested = real_value_after_uncontested_win - real_value_before_action
                  return real_money_ev_uncontested
             else:
                  return chip_change_uncontested # Chip EV if opponent folds


        # Calculate equity against the opponent's calling range
        # This still assumes a heads-up confrontation for the equity calculation itself.
        if opponent is None and len(scenario.players) > 2:
             # If multi-way, the equity calculation against a single range is a simplification.
             # We'll use the first other player found in the list as the "opponent" for the equity call,
             # but this is not strictly correct for multi-way pots.
             # A proper multi-way equity calculation would be needed.
             temp_opponent = None
             for p in scenario.players:
                 if p.name != player_name:
                      temp_opponent = p # Just pick one as a placeholder for the equity call
                      break
             if temp_opponent:
                  equity_results = calculate_equity(player.hole_cards, opponent_range, scenario.community_cards)
             else:
                 # Should not happen if len(players) > 1 and player is found.
                 print("Error: Could not find an opponent for equity calculation.")
                 return 0.0 # Cannot calculate EV
        elif opponent:
             equity_results = calculate_equity(player.hole_cards, opponent_range, scenario.community_cards)
        else: # Should not happen if len(players) == 2 and player is found.
             print("Error: Could not find an opponent for heads-up equity calculation.")
             return 0.0 # Cannot calculate EV


        prob_win = equity_results['win']
        prob_loss = equity_results['loss']
        prob_tie = equity_results['tie']

        if use_icm:
            # Calculate Real Money EV using ICM
            player_stacks_before_action = [p.stack for p in scenario.players]
            # Total chips is sum of stacks before action
            total_chips_before_action = sum(player_stacks_before_action)


            # Calculate Real Value before the action
            icm_values_before = calculate_icm(player_stacks_before_action, payout_structure)
            real_value_before = icm_values_before[player_index]

            # Calculate expected real value after the action
            expected_real_value_after = 0.0

            # Scenario 1: Player Wins (against the opponent's calling range)
            # Player's stack changes by (final_pot_at_showdown - player_contribution_this_action)
            # Note: This is simplified - in a multi-way pot, player might win against one opponent but lose to another.
            # Assuming a simplified heads-up outcome for equity vs the range.
            chip_change_win = final_pot_at_showdown - player_contribution_this_action
            # Calculate ICM value of the stack after winning
            stacks_after_win = list(player_stacks_before_action)
            stacks_after_win[player_index] += chip_change_win
            # Ensure stacks are non-negative
            if stacks_after_win[player_index] < 0:
                 stacks_after_win[player_index] = 0.0
            icm_values_after_win = calculate_icm(stacks_after_win, payout_structure)
            expected_real_value_after += prob_win * icm_values_after_win[player_index]

            # Scenario 2: Player Loses (against the opponent's calling range)
            # Player's stack decreases by player_contribution_this_action
            chip_change_loss = -player_contribution_this_action
            # Calculate ICM value of the stack after losing
            stacks_after_loss = list(player_stacks_before_action)
            stacks_after_loss[player_index] += chip_change_loss
             # Ensure stacks are non-negative
            if stacks_after_loss[player_index] < 0:
                 stacks_after_loss[player_index] = 0.0
            icm_values_after_loss = calculate_icm(stacks_after_loss, payout_structure)
            expected_real_value_after += prob_loss * icm_values_after_loss[player_index]

            # Scenario 3: Player Ties (against the opponent's calling range)
            # Player's stack changes by ((final_pot_at_showdown / 2.0) - player_contribution_this_action)
            chip_change_tie = (final_pot_at_showdown / 2.0) - player_contribution_this_action
            # Calculate ICM value of the stack after tying
            stacks_after_tie = list(player_stacks_before_action)
            stacks_after_tie[player_index] += chip_change_tie
             # Ensure stacks are non-negative
            if stacks_after_tie[player_index] < 0:
                 stacks_after_tie[player_index] = 0.0
            icm_values_after_tie = calculate_icm(stacks_after_tie, payout_structure)
            expected_real_value_after += prob_tie * icm_values_after_tie[player_index]

            # Real Money EV of the action is the expected value after minus the value before
            real_money_ev = expected_real_value_after - real_value_before

            return real_money_ev

        else: # Calculate Chip EV
            # Calculate chip change for each outcome
            # Win: Player wins the final pot. Chip change = Final Pot - amount player put in this action
            chip_change_win = final_pot_at_showdown - player_contribution_this_action

            # Loss: Player loses the amount they put in this action
            chip_change_loss = -player_contribution_this_action

            # Tie: The final pot is split. Player receives half. Chip change = (final_pot_at_showdown / 2.0) - player_contribution_this_action
            chip_change_tie = (final_pot_at_showdown / 2.0) - player_contribution_this_action

            # Calculate Chip EV
            chip_ev = (prob_win * chip_change_win) + (prob_loss * chip_change_loss) + (prob_tie * chip_change_tie)

            return chip_ev

    else:
        raise ValueError(f"Invalid player action: {player_action}. Must be 'fold', 'call', or 'raise'.")



# --- GUI Functions ---

def parse_hand_string(hand_string):
    """Parses a two-character hand string (e.g., 'AhKd') into a Hand object."""
    if len(hand_string) != 4:
        raise ValueError("Hole cards string must be exactly 4 characters (e.g., 'AhKd').")
    card1_str = hand_string[:2]
    card2_str = hand_string[2:]
    card1 = Card(card1_str[0].upper(), card1_str[1].lower())
    card2 = Card(card2_str[0].upper(), card2_str[1].lower())

    # Check for duplicate cards within the hand itself
    if card1 == card2:
        raise ValueError(f"Invalid hand string '{hand_string}': Cannot have duplicate cards in a hand.")

    return Hand(card1, card2)


def parse_community_cards_string(community_cards_string):
    """Parses a community cards string (e.g., 'AsKd7c') into a list of Card objects."""
    if len(community_cards_string) % 2 != 0:
        raise ValueError("Community cards string must have an even number of characters (each card is 2 chars).")
    cards = []
    # Convert to lowercase and remove spaces for parsing
    clean_string = community_cards_string.lower().replace(" ", "")
    for i in range(0, len(clean_string), 2):
        card_str = clean_string[i:i+2]
        if len(card_str) == 2:
             card = Card(card_str[0].upper(), card_str[1]) # Suit is already lower
             cards.append(card)
        else:
             raise ValueError(f"Could not parse card starting at position {i}: '{community_cards_string[i:]}'")


    # Check for duplicate cards within the community cards
    if len(cards) != len(set(cards)):
         seen = set()
         # Find duplicates for better error message
         duplicates = [x for x in cards if x in seen or seen.add(x)]
         # Format duplicates nicely, e.g., [Card('A', 's'), Card('A', 's')] -> "As, As"
         duplicate_strs = [str(card) for card in duplicates]
         raise ValueError(f"Duplicate cards found in community cards: {', '.join(duplicate_strs)}")


    return cards


def create_gui():
    """Creates the main GUI window for the poker EV calculator with improved layout."""
    root = tk.Tk()
    root.title("Poker EV Calculator (Chip EV)") # Clarify it's Chip EV

    # Configure the root grid to expand with the window
    root.columnconfigure(0, weight=1)

    # Frame for scenario details
    scenario_frame = ttk.LabelFrame(root, text="Scenario Details")
    scenario_frame.grid(row=0, column=0, padx=15, pady=10, sticky="ew") # Increased padding

    # Configure scenario_frame grid
    scenario_frame.columnconfigure(1, weight=1)
    scenario_frame.columnconfigure(2, weight=1)


    # Player Stacks
    ttk.Label(scenario_frame, text="Player Stacks (comma-separated):").grid(row=0, column=0, sticky="w", padx=10, pady=5) # Increased padding
    stacks_entry = ttk.Entry(scenario_frame, width=40)
    stacks_entry.grid(row=0, column=1, columnspan=2, sticky="ew", padx=10, pady=5) # Span across 2 columns, sticky ew
    stacks_entry.insert(0, "1000, 1500") # Default value example

    # Blinds and Ante (arranged side-by-side)
    blind_ante_frame = ttk.Frame(scenario_frame) # Use a sub-frame for better alignment
    blind_ante_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=5) # Span and sticky

    blind_ante_frame.columnconfigure(1, weight=1) # Give SB entry space
    blind_ante_frame.columnconfigure(3, weight=1) # Give BB entry space
    # Ante entry will take minimal space

    ttk.Label(blind_ante_frame, text="Small Blind:").grid(row=0, column=0, sticky="w", padx=(0, 5))
    sb_entry = ttk.Entry(blind_ante_frame, width=8)
    sb_entry.grid(row=0, column=1, sticky="ew", padx=5) # Sticky ew within sub-frame
    sb_entry.insert(0, "10") # Default value example

    ttk.Label(blind_ante_frame, text="Big Blind:").grid(row=0, column=2, sticky="w", padx=5)
    bb_entry = ttk.Entry(blind_ante_frame, width=8)
    bb_entry.grid(row=0, column=3, sticky="ew", padx=5) # Sticky ew within sub-frame
    bb_entry.insert(0, "20") # Default value example

    ttk.Label(blind_ante_frame, text="Ante:").grid(row=0, column=4, sticky="w", padx=5)
    ante_entry = ttk.Entry(blind_ante_frame, width=8)
    ante_entry.grid(row=0, column=5, sticky="ew", padx=(5, 0)) # Sticky ew within sub-frame
    ante_entry.insert(0, "0") # Default value example


    # Frame for player and hand details
    hand_frame = ttk.LabelFrame(root, text="Player and Hand Details")
    hand_frame.grid(row=1, column=0, padx=15, pady=10, sticky="ew") # Increased padding

    # Configure hand_frame grid
    hand_frame.columnconfigure(1, weight=1)

    # Player Hole Cards
    ttk.Label(hand_frame, text="Your Hole Cards (e.g., AhKd):").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    hole_cards_entry = ttk.Entry(hand_frame, width=20)
    hole_cards_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=5) # Sticky ew
    hole_cards_entry.insert(0, "AsKd") # Default value example

    # Community Cards
    ttk.Label(hand_frame, text="Community Cards (e.g., AsKd7c or leave empty):").grid(row=1, column=0, sticky="w", padx=10, pady=5)
    community_cards_entry = ttk.Entry(hand_frame, width=20)
    community_cards_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=5) # Sticky ew
    community_cards_entry.insert(0, "Th9d2c") # Default value example


    # Frame for opponent and action details
    action_frame = ttk.LabelFrame(root, text="Opponent and Action Details")
    action_frame.grid(row=2, column=0, padx=15, pady=10, sticky="ew") # Increased padding

    # Configure action_frame grid
    action_frame.columnconfigure(1, weight=1)

    # Opponent Range
    ttk.Label(action_frame, text="Opponent Range (e.g., JJ+, AKs, AKo):").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    opponent_range_entry = ttk.Entry(action_frame, width=40)
    opponent_range_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=5) # Sticky ew
    opponent_range_entry.insert(0, "JJ+, AKs, AKo") # Default value example
    # Consider adding a tooltip later for the range format


    # Player Action and Bet Size (arranged side-by-side)
    action_bet_frame = ttk.Frame(action_frame) # Use a sub-frame
    action_bet_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

    action_bet_frame.columnconfigure(1, weight=1) # Give Action Combobox space
    action_bet_frame.columnconfigure(3, weight=1) # Give Bet Size entry space


    # Player Action (using Combobox for dropdown)
    ttk.Label(action_bet_frame, text="Your Action:").grid(row=0, column=0, sticky="w", padx=(0, 5))
    action_options = ['Fold', 'Call', 'Raise']
    action_combobox = ttk.Combobox(action_bet_frame, values=action_options, state="readonly", width=12) # Adjusted width
    action_combobox.grid(row=0, column=1, sticky="ew", padx=5) # Sticky ew within sub-frame
    action_combobox.set('Call') # Set default value


    # Bet Size
    ttk.Label(action_bet_frame, text="Bet/Call Size:").grid(row=0, column=2, sticky="w", padx=5)
    bet_size_entry = ttk.Entry(action_bet_frame, width=8) # Adjusted width
    bet_size_entry.grid(row=0, column=3, sticky="ew", padx=(5, 0)) # Sticky ew within sub-frame
    bet_size_entry.insert(0, "50") # Default value example


    # Output Area
    output_frame = ttk.LabelFrame(root, text="Result")
    output_frame.grid(row=3, column=0, padx=15, pady=10, sticky="ew") # Increased padding

    # Configure output_frame grid
    output_frame.columnconfigure(1, weight=1)

    ttk.Label(output_frame, text="Calculated EV:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    ev_result_label = ttk.Label(output_frame, text="Enter details and click Calculate", font=('TkDefaultFont', 12, 'bold'), anchor='w') # Set initial text, sticky w
    ev_result_label.grid(row=0, column=1, sticky="ew", padx=10, pady=5) # Sticky ew

    # Add a button to trigger calculation
    calculate_button = ttk.Button(root, text="Calculate EV")
    calculate_button.grid(row=4, column=0, padx=15, pady=15) # Increased padding


    # Store entry widgets for later access (e.g., in the calculation function)
    gui_elements = {
        'stacks_entry': stacks_entry,
        'sb_entry': sb_entry,
        'bb_entry': bb_entry,
        'ante_entry': ante_entry,
        'hole_cards_entry': hole_cards_entry,
        'community_cards_entry': community_cards_entry,
        'opponent_range_entry': opponent_range_entry,
        'action_combobox': action_combobox,
        'bet_size_entry': bet_size_entry,
        'ev_result_label': ev_result_label,
        'calculate_button': calculate_button
    }

    return root, gui_elements # Return the root window and elements


def calculate_ev_from_gui(gui_elements):
    """
    Efficiently parses input values from the GUI dictionary, creates poker objects,
    calls the calculate_chip_ev function, and updates the GUI label.
    """
    ev_result_label = gui_elements['ev_result_label']
    ev_result_label.config(text="Calculating...", foreground="black")

    try:
        # Parse and validate player stacks
        stacks_str = gui_elements['stacks_entry'].get()
        stack_strings = [s.strip() for s in stacks_str.split(',') if s.strip()]
        n_players = len(stack_strings)
        if n_players not in (2, 3):
            raise ValueError("Only 2 or 3 players supported.")

        player_stacks = []
        for i, s in enumerate(stack_strings):
            stack = float(s)
            if stack < 0:
                raise ValueError(f"Player {i+1} stack cannot be negative.")
            player_stacks.append(stack)

        player_names = [f"Player {i+1}" for i in range(n_players)]
        player_name = player_names[0]
        players = [Player(name, stack) for name, stack in zip(player_names, player_stacks)]

        # Parse blinds, ante, bet size
        small_blind = float(gui_elements['sb_entry'].get() or '0')
        big_blind = float(gui_elements['bb_entry'].get() or '0')
        ante = float(gui_elements['ante_entry'].get() or '0')
        bet_size = float(gui_elements['bet_size_entry'].get() or '0')
        if small_blind < 0 or big_blind < 0 or ante < 0 or bet_size < 0:
            raise ValueError("Blinds, ante, and bet/call size must be non-negative.")

        # Parse hole cards
        hole_cards_str = gui_elements['hole_cards_entry'].get().strip()
        player_hole_cards = parse_hand_string(hole_cards_str)
        players[0].hole_cards = player_hole_cards

        # Parse community cards
        community_cards_str = gui_elements['community_cards_entry'].get().strip()
        community_cards = parse_community_cards_string(community_cards_str)
        if any(card in community_cards for card in player_hole_cards.cards):
            raise ValueError("Overlap between hole cards and community cards.")

        num_community = len(community_cards)
        if num_community not in (0, 3, 4, 5):
            raise ValueError("Community cards must be 0, 3, 4, or 5.")

        scenario = PokerScenario(players, small_blind, big_blind, ante)
        if num_community:
            scenario.community_cards = community_cards
            scenario.street = ["pre-flop", "flop", "turn", "river"][num_community // 2]

        # Opponent range and action
        opponent_range_string = gui_elements['opponent_range_entry'].get().strip()
        player_action = gui_elements['action_combobox'].get().strip().lower()
        if player_action not in ('fold', 'call', 'raise'):
            raise ValueError("Invalid action.")

        if player_action == 'raise' and bet_size <= 0:
            raise ValueError("Raise amount must be positive.")

        # Calculate EV
        calculated_ev = calculate_chip_ev(
            scenario=scenario,
            player_name=player_name,
            opponent_range_string=opponent_range_string,
            player_action=player_action,
            bet_size=bet_size,
            use_icm=False
        )
        ev_result_label.config(text=f"{calculated_ev:.2f} Chips", foreground="green")

    except Exception as e:
        ev_result_label.config(text=f"Error: {e}", foreground="red")


# --- GUI Creation and Mainloop (Commented out for Colab) ---
root, gui_elements = create_gui()
calculate_button = gui_elements.get('calculate_button')
if calculate_button:
    calculate_button.config(command=lambda: calculate_ev_from_gui(gui_elements))
root.mainloop()