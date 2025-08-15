"""
Test suite for poker_logic.py

Tests the core poker classes: Card, Hand, Player, PokerScenario
"""

import unittest
import sys
import os

# Add the current directory to the path to import the modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from poker_logic import Card, Hand, Player, PokerScenario, RANKS, SUITS, create_deck, parse_hand_string, parse_community_cards_string


class TestCard(unittest.TestCase):
    """Test cases for the Card class"""
    
    def test_valid_card_creation(self):
        """Test creating valid cards"""
        card = Card('A', 's')
        self.assertEqual(card.rank, 'A')
        self.assertEqual(card.suit, 's')
        
        # Test case insensitive
        card2 = Card('k', 'H')
        self.assertEqual(card2.rank, 'K')
        self.assertEqual(card2.suit, 'h')
    
    def test_invalid_rank(self):
        """Test creating card with invalid rank"""
        with self.assertRaises(ValueError):
            Card('X', 's')
    
    def test_invalid_suit(self):
        """Test creating card with invalid suit"""
        with self.assertRaises(ValueError):
            Card('A', 'x')
    
    def test_rank_value(self):
        """Test get_rank_value method"""
        self.assertEqual(Card('2', 's').get_rank_value(), 0)
        self.assertEqual(Card('A', 's').get_rank_value(), 12)
        self.assertEqual(Card('K', 's').get_rank_value(), 11)
    
    def test_card_equality(self):
        """Test card equality comparison"""
        card1 = Card('A', 's')
        card2 = Card('A', 's')
        card3 = Card('A', 'h')
        
        self.assertEqual(card1, card2)
        self.assertNotEqual(card1, card3)
    
    def test_card_string_representation(self):
        """Test card string representation"""
        card = Card('A', 's')
        self.assertEqual(str(card), 'As')
        self.assertEqual(repr(card), "Card('A', 's')")


class TestHand(unittest.TestCase):
    """Test cases for the Hand class"""
    
    def test_valid_hand_creation(self):
        """Test creating valid hands"""
        card1 = Card('A', 's')
        card2 = Card('K', 'h')
        hand = Hand(card1, card2)
        
        # Should be sorted by rank (highest first)
        self.assertEqual(hand.cards[0], card1)  # Ace
        self.assertEqual(hand.cards[1], card2)  # King
    
    def test_hand_sorting(self):
        """Test that hand cards are sorted correctly"""
        card1 = Card('2', 's')
        card2 = Card('A', 'h')
        hand = Hand(card1, card2)
        
        # Ace should come first
        self.assertEqual(hand.cards[0], card2)  # Ace
        self.assertEqual(hand.cards[1], card1)  # Two
    
    def test_duplicate_cards(self):
        """Test that duplicate cards are not allowed"""
        card1 = Card('A', 's')
        card2 = Card('A', 's')
        
        with self.assertRaises(ValueError):
            Hand(card1, card2)
    
    def test_invalid_hand_creation(self):
        """Test creating hand with non-Card objects"""
        with self.assertRaises(ValueError):
            Hand("As", "Kh")
    
    def test_hand_equality(self):
        """Test hand equality comparison"""
        hand1 = Hand(Card('A', 's'), Card('K', 'h'))
        hand2 = Hand(Card('K', 'h'), Card('A', 's'))  # Different order
        hand3 = Hand(Card('A', 'h'), Card('K', 's'))
        
        self.assertEqual(hand1, hand2)  # Same cards, different order
        self.assertNotEqual(hand1, hand3)  # Different suits
    
    def test_hand_string_representation(self):
        """Test hand string representation"""
        hand = Hand(Card('A', 's'), Card('K', 'h'))
        self.assertEqual(str(hand), 'AsKh')


class TestPokerHelperFunctions(unittest.TestCase):
    """Test cases for poker helper functions"""
    
    def test_create_deck(self):
        """Test deck creation"""
        deck = create_deck()
        self.assertEqual(len(deck), 52)
        
        # Check all ranks and suits are present
        ranks_found = set()
        suits_found = set()
        for card in deck:
            ranks_found.add(card.rank)
            suits_found.add(card.suit)
        
        self.assertEqual(len(ranks_found), 13)
        self.assertEqual(len(suits_found), 4)
    
    def test_parse_hand_string(self):
        """Test parsing hand string"""
        hand = parse_hand_string("AsKh")
        self.assertEqual(len(hand.cards), 2)
        self.assertEqual(hand.cards[0].rank, 'A')
        self.assertEqual(hand.cards[0].suit, 's')
        self.assertEqual(hand.cards[1].rank, 'K')
        self.assertEqual(hand.cards[1].suit, 'h')
    
    def test_parse_hand_string_invalid(self):
        """Test parsing invalid hand string"""
        with self.assertRaises(ValueError):
            parse_hand_string("AsKhQd")  # Too many cards
        
        with self.assertRaises(ValueError):
            parse_hand_string("As")  # Too few cards
    
    def test_parse_community_cards_string(self):
        """Test parsing community cards string"""
        # Empty string
        cards = parse_community_cards_string("")
        self.assertEqual(len(cards), 0)
        
        # Flop
        cards = parse_community_cards_string("AsKhQd")
        self.assertEqual(len(cards), 3)
        
        # Full board
        cards = parse_community_cards_string("AsKhQdJcTh")
        self.assertEqual(len(cards), 5)


class TestPlayer(unittest.TestCase):
    """Test cases for the Player class"""
    
    def test_player_creation(self):
        """Test creating a player"""
        player = Player("Hero", 1000.0)
        self.assertEqual(player.name, "Hero")
        self.assertEqual(player.stack, 1000.0)
        self.assertEqual(player.hole_cards, None)
    
    def test_player_with_cards(self):
        """Test creating a player with cards"""
        hand = Hand(Card('A', 's'), Card('K', 'h'))
        player = Player("Hero", 1000.0)
        player.hole_cards = hand
        self.assertEqual(player.hole_cards, hand)


if __name__ == '__main__':
    unittest.main()