# --- Poker Logic Classes and Functions  ---

RANKS = '23456789TJQKA'
SUITS = 'cdhs'

class Card:
    def __init__(self, rank, suit):
        # Reference the module-level constants
        if rank.upper() not in RANKS:
            raise ValueError(f"Invalid rank: {rank}")
        if suit.lower() not in SUITS:
            raise ValueError(f"Invalid suit: {suit}")
        self.rank = rank.upper()
        self.suit = suit.lower()

    def get_rank_value(self):
        # Reference the module-level constant
        return RANKS.index(self.rank)

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

class Hand:
    # ... (code complet de la classe Hand) ...
    def __init__(self, card1, card2):
        if not isinstance(card1, Card) or not isinstance(card2, Card):
            raise ValueError("Hand must be created with two Card objects.")
        if card1 == card2:
             raise ValueError("A hand cannot contain duplicate cards.")
        self.cards = tuple(sorted([card1, card2], key=lambda c: c.get_rank_value(), reverse=True))

    def __str__(self):
        return f"{self.cards[0]}{self.cards[1]}"

    def __repr__(self):
        return f"Hand({repr(self.cards[0])}, {repr(self.cards[1])})"

    def __eq__(self, other):
        if isinstance(other, Hand):
            return set(self.cards) == set(other.cards)
        return False

    def __hash__(self):
        return hash(frozenset(self.cards))

class Player:
    # ... (code complet de la classe Player) ...
    def __init__(self, name, stack):
        if not isinstance(name, str) or not name:
            raise ValueError("Player name must be a non-empty string.")
        if not isinstance(stack, (int, float)) or stack < 0:
            raise ValueError("Player stack must be a non-negative number.")
        self.name = name
        self.stack = stack
        self.hole_cards = None

    def __str__(self):
        return f"{self.name} ({self.stack}€)"

    def __repr__(self):
        return f"Player('{self.name}', {self.stack})"

class PokerScenario:
    # ... (code complet de la classe PokerScenario) ...
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
        self.pot = small_blind + big_blind + (len(players) * ante)
        self.community_cards = []
        self.street = "pre-flop"
        self.current_player_index = 0

def create_deck():
    """Creates a standard 52-card deck."""
    return {Card(rank, suit) for rank in RANKS for suit in SUITS}

def parse_hand_string(hand_string):
    """Parses a two-character hand string (e.g., 'AhKd') into a Hand object."""
    if len(hand_string) != 4:
        raise ValueError("Hole cards string must be exactly 4 characters (e.g., 'AhKd').")
    card1_str = hand_string[:2]
    card2_str = hand_string[2:]
    card1 = Card(card1_str[0], card1_str[1])
    card2 = Card(card2_str[0], card2_str[1])
    if card1 == card2:
        raise ValueError(f"Invalid hand string '{hand_string}': Cannot have duplicate cards.")
    return Hand(card1, card2)

def parse_community_cards_string(community_cards_string):
    """Parses a community cards string (e.g., 'AsKd7c') into a list of Card objects."""
    if len(community_cards_string) % 2 != 0:
        raise ValueError("Community cards string must have an even number of characters.")
    cards = []
    clean_string = community_cards_string.replace(" ", "") # Keep lower() for consistency if you wish, but Card handles it.
    for i in range(0, len(clean_string), 2):
        card_str = clean_string[i:i+2]
        card = Card(card_str[0], card_str[1])
        cards.append(card)
    if len(cards) != len(set(cards)):
        raise ValueError("Duplicate cards found in community cards.")
    return cards


