#!/usr/bin/env python3
"""
Demonstration script for the new filtering functionality in Poker Tracker.

This script shows how to use the date and position filters programmatically.
"""

import sys
import os

# Add the current directory to the path to import the modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from recapitulatif_tournoi import analyser_resultats_tournois
from recapitulatif_cash_game import analyser_resultats_cash_game
from recapitulatif_expresso import analyser_resultats_expresso


def demonstrate_cash_game_filtering():
    """Demonstrate cash game filtering capabilities"""
    print("=== Cash Game Filtering Demo ===")
    
    # Example: Analyze only hands from a specific date range and positions
    directory = "/path/to/your/history/files"  # Replace with actual path
    username = "YourUsername"  # Replace with actual username
    
    # Date filter: only hands from January 2024
    date_filter = ("2024-01-01", "2024-01-31")
    
    # Position filter: only hands from button and cutoff positions
    position_filter = ["BTN", "CO"]
    
    try:
        print(f"Analyzing cash game hands for {username}")
        print(f"Date range: {date_filter[0]} to {date_filter[1]}")
        print(f"Positions: {', '.join(position_filter)}")
        
        results = analyser_resultats_cash_game(
            directory, 
            username, 
            date_filter=date_filter, 
            position_filter=position_filter
        )
        
        print(f"Found {results['total_hands']} hands matching criteria")
        print(f"Net result: {results['resultat_net_total']:+.2f}€")
        print(f"VPIP: {results['vpip_pct']:.1f}%")
        print(f"PFR: {results['pfr_pct']:.1f}%")
        
    except FileNotFoundError:
        print("Directory not found - this is just a demo")
    except Exception as e:
        print(f"Error: {e}")
    
    print()


def demonstrate_tournament_filtering():
    """Demonstrate tournament filtering capabilities"""
    print("=== Tournament Filtering Demo ===")
    
    directory = "/path/to/your/history/files"  # Replace with actual path
    
    # Date filter: only tournaments from December 2023
    date_filter = ("2023-12-01", "2023-12-31")
    
    try:
        print(f"Analyzing tournaments")
        print(f"Date range: {date_filter[0]} to {date_filter[1]}")
        
        results = analyser_resultats_tournois(directory, date_filter=date_filter)
        
        print(f"Found {results['nombre_tournois']} tournaments matching criteria")
        print(f"Total buy-ins: {results['total_buy_ins']:.2f}€")
        print(f"Total winnings: {results['total_gains']:.2f}€")
        print(f"Net result: {results['resultat_net_total']:+.2f}€")
        
    except FileNotFoundError:
        print("Directory not found - this is just a demo")
    except Exception as e:
        print(f"Error: {e}")
    
    print()


def demonstrate_expresso_filtering():
    """Demonstrate expresso filtering capabilities"""
    print("=== Expresso Filtering Demo ===")
    
    directory = "/path/to/your/history/files"  # Replace with actual path
    
    # Date filter: only expressos from last week
    date_filter = ("2024-01-08", "2024-01-14")
    
    try:
        print(f"Analyzing expresso tournaments")
        print(f"Date range: {date_filter[0]} to {date_filter[1]}")
        
        results = analyser_resultats_expresso(directory, date_filter=date_filter)
        
        print(f"Found {results['nombre_expressos']} expressos matching criteria")
        print(f"Total buy-ins: {results['total_buy_ins']:.2f}€")
        print(f"Total winnings: {results['total_gains']:.2f}€")
        print(f"Net result: {results['resultat_net_total']:+.2f}€")
        
    except FileNotFoundError:
        print("Directory not found - this is just a demo")
    except Exception as e:
        print(f"Error: {e}")
    
    print()


def show_filter_examples():
    """Show various filter combinations"""
    print("=== Filter Examples ===")
    
    print("Cash Game Filter Examples:")
    print("1. All hands from button position:")
    print('   position_filter = ["BTN"]')
    print()
    
    print("2. Hands from early positions:")
    print('   position_filter = ["UTG", "UTG+1", "MP"]')
    print()
    
    print("3. Hands from a specific month:")
    print('   date_filter = ("2024-01-01", "2024-01-31")')
    print()
    
    print("4. Hands from last week in late positions:")
    print('   date_filter = ("2024-01-08", "2024-01-14")')
    print('   position_filter = ["BTN", "CO", "HJ"]')
    print()
    
    print("Tournament/Expresso Filter Examples:")
    print("1. All games from a specific date:")
    print('   date_filter = ("2024-01-15", "2024-01-15")')
    print()
    
    print("2. Games from the last quarter:")
    print('   date_filter = ("2023-10-01", "2023-12-31")')
    print()
    
    print("3. No filter (all data):")
    print('   date_filter = None')
    print()


if __name__ == "__main__":
    print("Poker Tracker Filtering Demonstration")
    print("=====================================")
    print()
    
    # Show examples of how to use filters
    show_filter_examples()
    
    # Demonstrate each type of analysis
    demonstrate_cash_game_filtering()
    demonstrate_tournament_filtering()
    demonstrate_expresso_filtering()
    
    print("=== Summary ===")
    print("✅ All analysis functions now support filtering")
    print("✅ Cash games support both date and position filters")
    print("✅ Tournaments and expressos support date filters")
    print("✅ CLI interfaces have interactive filter prompts")
    print("✅ GUI has filter controls in all tabs")
    print("✅ All filters maintain backward compatibility")
    print()
    print("Use the CLI tools or GUI to apply filters to your actual data!")