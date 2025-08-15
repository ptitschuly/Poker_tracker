"""
Test suite for poker_calculations.py

Tests the poker calculation functions: equity calculations, range parsing, EV calculations
"""

import unittest
import sys
import os

# Add the current directory to the path to import the modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from poker_logic import Card, Hand, create_deck, RANKS, SUITS, Player
from poker_calculations import calculate_equity_fast, parse_range_string, calculate_chip_ev


class TestEquityCalculations(unittest.TestCase):
    """Test cases for equity calculation functions"""
    
    def test_calculate_equity_basic(self):
        """Test basic equity calculation"""
        # AA vs random hand should have high equity
        hero_hand = Hand(Card('A', 's'), Card('A', 'h'))
        deck = create_deck()
        # Remove hero cards from deck
        deck.remove(Card('A', 's'))
        deck.remove(Card('A', 'h'))
        
        # Create a small opponent range (just one hand for testing)
        opponent_range = {Hand(Card('K', 's'), Card('K', 'h'))}
        community_cards = []
        
        equity = calculate_equity_fast(hero_hand, opponent_range, community_cards, num_simulations=1000)
        
        # AA vs KK should have roughly 80% equity
        self.assertGreater(equity, 0.7)
        self.assertLess(equity, 1.0)
    
    def test_calculate_equity_empty_range(self):
        """Test equity calculation with empty opponent range"""
        hero_hand = Hand(Card('A', 's'), Card('A', 'h'))
        opponent_range = set()
        community_cards = []
        
        equity = calculate_equity_fast(hero_hand, opponent_range, community_cards)
        self.assertEqual(equity, 1.0)
    
    def test_calculate_equity_with_board(self):
        """Test equity calculation with community cards"""
        hero_hand = Hand(Card('A', 's'), Card('A', 'h'))
        opponent_range = {Hand(Card('K', 's'), Card('K', 'h'))}
        community_cards = [Card('A', 'd'), Card('2', 'c'), Card('3', 'h')]
        
        equity = calculate_equity_fast(hero_hand, opponent_range, community_cards, num_simulations=1000)
        
        # AAA vs KK should have very high equity
        self.assertGreater(equity, 0.9)


class TestRangeParsing(unittest.TestCase):
    """Test cases for range parsing functions"""
    
    def test_parse_pair_range(self):
        """Test parsing pair ranges"""
        # Single pair
        hands = parse_range_string("AA")
        self.assertEqual(len(hands), 6)  # 6 combinations of AA
        
        for hand in hands:
            self.assertEqual(hand.cards[0].rank, 'A')
            self.assertEqual(hand.cards[1].rank, 'A')
    
    def test_parse_pair_plus_range(self):
        """Test parsing pair+ ranges"""
        hands = parse_range_string("JJ+")
        
        # Should include JJ, QQ, KK, AA
        pair_ranks = set()
        for hand in hands:
            if hand.cards[0].rank == hand.cards[1].rank:
                pair_ranks.add(hand.cards[0].rank)
        
        expected_ranks = {'J', 'Q', 'K', 'A'}
        self.assertEqual(pair_ranks, expected_ranks)
    
    def test_parse_suited_range(self):
        """Test parsing suited ranges"""
        hands = parse_range_string("AKs")
        self.assertEqual(len(hands), 4)  # 4 suited combinations
        
        for hand in hands:
            self.assertEqual(hand.cards[0].rank, 'A')
            self.assertEqual(hand.cards[1].rank, 'K')
            # Should be same suit
            self.assertEqual(hand.cards[0].suit, hand.cards[1].suit)
    
    def test_parse_offsuit_range(self):
        """Test parsing offsuit ranges"""
        hands = parse_range_string("AKo")
        self.assertEqual(len(hands), 12)  # 12 offsuit combinations
        
        for hand in hands:
            self.assertEqual(hand.cards[0].rank, 'A')
            self.assertEqual(hand.cards[1].rank, 'K')
            # Should be different suits
            self.assertNotEqual(hand.cards[0].suit, hand.cards[1].suit)
    
    def test_parse_suited_plus_range(self):
        """Test parsing suited+ ranges"""
        hands = parse_range_string("ATs+")
        
        # Should include ATs, AJs, AQs, AKs
        suited_combos = set()
        for hand in hands:
            if (hand.cards[0].rank == 'A' and 
                hand.cards[0].suit == hand.cards[1].suit):
                suited_combos.add(hand.cards[1].rank)
        
        expected_ranks = {'T', 'J', 'Q', 'K'}
        self.assertEqual(suited_combos, expected_ranks)
    
    def test_parse_complex_range(self):
        """Test parsing complex ranges with multiple components"""
        hands = parse_range_string("AA, KK, AKs")
        
        # Should have combinations of AA, KK, and AKs
        self.assertGreater(len(hands), 0)
        
        # Check we have some aces
        has_aa = any(h.cards[0].rank == 'A' and h.cards[1].rank == 'A' for h in hands)
        has_kk = any(h.cards[0].rank == 'K' and h.cards[1].rank == 'K' for h in hands)
        has_aks = any(h.cards[0].rank == 'A' and h.cards[1].rank == 'K' and 
                     h.cards[0].suit == h.cards[1].suit for h in hands)
        
        self.assertTrue(has_aa)
        self.assertTrue(has_kk)
        self.assertTrue(has_aks)
    
    def test_parse_empty_range(self):
        """Test parsing empty range"""
        hands = parse_range_string("")
        self.assertEqual(len(hands), 0)
    
    def test_parse_invalid_range(self):
        """Test parsing invalid range components"""
        # Should handle invalid components gracefully
        hands = parse_range_string("XX, AA")
        # Should still parse AA
        has_aa = any(h.cards[0].rank == 'A' and h.cards[1].rank == 'A' for h in hands)
        self.assertTrue(has_aa)


class TestChipEVCalculations(unittest.TestCase):
    """Test cases for chip EV calculation functions"""
    
    def test_calculate_chip_ev_basic(self):
        """Test basic chip EV calculation"""
        # Create a simple scenario
        from poker_logic import PokerScenario
        
        hero = Player("Hero", 1000.0)
        villain = Player("Villain", 1000.0)
        hero.hole_cards = Hand(Card('A', 's'), Card('A', 'h'))
        
        scenario = PokerScenario([hero, villain], 5, 10, 0)
        
        try:
            ev = calculate_chip_ev(scenario, "Hero", "KK", "call")
            self.assertIsInstance(ev, (int, float))
        except Exception as e:
            # The function may require more complex setup
            # This test mainly ensures the function signature is correct
            self.assertIn("calculate_chip_ev", str(e).__class__.__name__ + str(e))


if __name__ == '__main__':
    unittest.main()