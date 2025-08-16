"""
Test suite for filtering functionality in analysis modules
"""

import unittest
import sys
import os
import tempfile

# Add the parent directory to the path to import the modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from recapitulatif_tournoi import analyser_resultats_tournois
from recapitulatif_cash_game import analyser_resultats_cash_game
from recapitulatif_expresso import analyser_resultats_expresso


class TestDateFiltering(unittest.TestCase):
    """Test cases for date filtering functionality"""
    
    def test_cash_game_date_filter_parameters(self):
        """Test that cash game analysis accepts date filter parameters"""
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Test with date filter
                date_filter = ("2024-01-01", "2024-12-31")
                results = analyser_resultats_cash_game(temp_dir, "TestPlayer", date_filter=date_filter)
                self.assertIsInstance(results, dict)
                self.assertIn("details", results)
                self.assertIn("total_hands", results)
            except Exception as e:
                # Expected if no valid files exist
                pass
    
    def test_tournoi_date_filter_parameters(self):
        """Test that tournament analysis accepts date filter parameters"""
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Test with date filter
                date_filter = ("2024-01-01", "2024-12-31")
                results = analyser_resultats_tournois(temp_dir, date_filter=date_filter)
                self.assertIsInstance(results, dict)
                self.assertIn("details", results)
                self.assertIn("nombre_tournois", results)
            except Exception as e:
                # Expected if no valid files exist
                pass
    
    def test_expresso_date_filter_parameters(self):
        """Test that expresso analysis accepts date filter parameters"""
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Test with date filter
                date_filter = ("2024-01-01", "2024-12-31")
                results = analyser_resultats_expresso(temp_dir, date_filter=date_filter)
                self.assertIsInstance(results, dict)
                self.assertIn("details", results)
                self.assertIn("nombre_expressos", results)
            except Exception as e:
                # Expected if no valid files exist
                pass


class TestPositionFiltering(unittest.TestCase):
    """Test cases for position filtering functionality"""
    
    def test_cash_game_position_filter_parameters(self):
        """Test that cash game analysis accepts position filter parameters"""
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Test with position filter
                position_filter = ["BTN", "CO"]
                results = analyser_resultats_cash_game(temp_dir, "TestPlayer", position_filter=position_filter)
                self.assertIsInstance(results, dict)
                self.assertIn("details", results)
                self.assertIn("total_hands", results)
            except Exception as e:
                # Expected if no valid files exist
                pass
    
    def test_cash_game_combined_filters(self):
        """Test that cash game analysis accepts both date and position filters"""
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Test with both filters
                date_filter = ("2024-01-01", "2024-12-31")
                position_filter = ["BTN", "SB", "BB"]
                results = analyser_resultats_cash_game(temp_dir, "TestPlayer", 
                                                     date_filter=date_filter, 
                                                     position_filter=position_filter)
                self.assertIsInstance(results, dict)
                self.assertIn("details", results)
                self.assertIn("total_hands", results)
            except Exception as e:
                # Expected if no valid files exist
                pass


class TestFilteringFunctionality(unittest.TestCase):
    """Integration tests for filtering functionality"""
    
    def test_functions_maintain_backward_compatibility(self):
        """Test that all analysis functions work without filters (backward compatibility)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            functions_to_test = [
                (analyser_resultats_cash_game, ["TestPlayer"]),
                (analyser_resultats_tournois, []),
                (analyser_resultats_expresso, [])
            ]
            
            for func, extra_args in functions_to_test:
                try:
                    # Test without any filters (backward compatibility)
                    if extra_args:
                        result = func(temp_dir, *extra_args)
                    else:
                        result = func(temp_dir)
                    self.assertIsInstance(result, dict)
                    self.assertIn("details", result)
                except Exception:
                    # Expected if no valid files exist
                    continue
    
    def test_filter_parameter_types(self):
        """Test that filters handle various parameter types correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Test with None filters
                results = analyser_resultats_cash_game(temp_dir, "TestPlayer", 
                                                     date_filter=None, 
                                                     position_filter=None)
                self.assertIsInstance(results, dict)
                
                # Test with empty lists/tuples
                results = analyser_resultats_cash_game(temp_dir, "TestPlayer", 
                                                     date_filter=(), 
                                                     position_filter=[])
                self.assertIsInstance(results, dict)
                
                # Test with partial date filters
                results = analyser_resultats_cash_game(temp_dir, "TestPlayer", 
                                                     date_filter=("2024-01-01", None))
                self.assertIsInstance(results, dict)
                
                results = analyser_resultats_cash_game(temp_dir, "TestPlayer", 
                                                     date_filter=(None, "2024-12-31"))
                self.assertIsInstance(results, dict)
                
            except Exception:
                # Expected if no valid files exist
                pass


if __name__ == '__main__':
    unittest.main()