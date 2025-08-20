#!/usr/bin/env python3
"""
Script de test pour la fonctionnalité de focus sur les tournois.
Ce script teste les nouvelles fonctions sans interface graphique.
"""

import sys
import os
import tempfile

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from recapitulatif_tournoi import extraire_details_tournoi, analyser_resultats_tournois
from Tracker_poker.recapitulatif_tournament import extraire_details_expresso, analyser_resultats_expresso

def test_tournament_details():
    """Test la fonctionnalité d'extraction des détails de tournoi"""
    print("=== Test des détails de tournoi ===")
    
    # Créer un fichier de test temporaire
    sample_content = """Winamax Poker - Tournament "Test Tournament" buyIn: 5.00€ + 0.50€ level: 0 - HandId: #123456789-123-1234567890 - Holdem no limit (50/100) - 2024/01/15 20:00:00 UTC
Table: 'Tournament Table' 2-max (real money) Seat #1 is the button
Seat 1: Hero (1500)
Seat 2: Villain (1500)

*** ANTE/BLINDS ***
Hero posts small blind 50
Villain posts big blind 100

*** PRE-FLOP ***
Hero: deals [Ah Kh]
Hero: raises 100 to 200
Villain: calls 100

*** FLOP *** [As 7h 2c]
Villain: checks
Hero: bets 150
Villain: calls 150

*** TURN *** [As 7h 2c][Tc]
Villain: checks 
Hero: bets 300
Villain: folds
Hero: doesn't show hand
Hero collected 800 from pot

*** SUMMARY ***
Buy-in: 5.50€
You won: 10.00€
Result: +4.50€
Duration: 8 minutes
Final Position: 1st"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='_summary.txt', delete=False) as f:
        f.write(sample_content)
        temp_file = f.name
    
    try:
        # Test extraction des détails
        details = extraire_details_tournoi(temp_file)
        
        print(f"✓ Fichier: {details['fichier']}")
        print(f"✓ Buy-in: {details['buy_in']:.2f}€")
        print(f"✓ Gains: {details['gains']:.2f}€")
        print(f"✓ Net: {details['net']:+.2f}€")
        print(f"✓ Durée: {details['duree']}")
        print(f"✓ Position: {details['position_finale']}")
        print(f"✓ Nombre de mains: {details['nombre_mains']}")
        
        for i, main in enumerate(details['mains']):
            print(f"  Main {i+1}: {main['cartes_hero']} -> {main['action_hero']} -> {main['resultat']:.0f}")
        
        print("✓ Test des détails de tournoi réussi!\n")
        return True
        
    except Exception as e:
        print(f"✗ Erreur dans le test des détails de tournoi: {e}")
        return False
    finally:
        os.unlink(temp_file)

def test_expresso_details():
    """Test la fonctionnalité d'extraction des détails d'expresso"""
    print("=== Test des détails d'expresso ===")
    
    sample_content = """Winamax Poker - Tournament "Expresso No Limit Hold'em" buyIn: 2.00€ + 0.20€ level: 0 - HandId: #987654321-456-9876543210 - Holdem no limit (10/20) - 2024/01/15 21:00:00 UTC
Table: 'Expresso Table' 3-max (real money) Seat #1 is the button
Seat 1: Hero (1000)
Seat 2: Player2 (1000)
Seat 3: Player3 (1000)

*** ANTE/BLINDS ***
Player2 posts small blind 10
Player3 posts big blind 20

*** PRE-FLOP ***
Hero: shows [Ac As]
Hero: raises 980 to 1000 and is all-in
Player2: calls 990 and is all-in
Player3: folds
Hero: shows [Ac As]
Player2: shows [Kd Kh]

*** FLOP *** [4h 7s 9c]
*** TURN *** [4h 7s 9c][Ad]
*** RIVER *** [4h 7s 9c Ad][2h]

Hero wins 2020 with three of a kind, Aces

*** SUMMARY ***
Buy-in: 2.20€
You won: 6.00€
Result: +3.80€
Duration: 4 minutes
Final Position: 1st"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='_Expresso_summary.txt', delete=False) as f:
        f.write(sample_content)
        temp_file = f.name
    
    try:
        # Test extraction des détails
        details = extraire_details_expresso(temp_file)
        
        print(f"✓ Fichier: {details['fichier']}")
        print(f"✓ Buy-in: {details['buy_in']:.2f}€")
        print(f"✓ Gains: {details['gains']:.2f}€")
        print(f"✓ Net: {details['net']:+.2f}€")
        print(f"✓ Durée: {details['duree']}")
        print(f"✓ Position: {details['position_finale']}")
        print(f"✓ Nombre de mains: {details['nombre_mains']}")
        
        for i, main in enumerate(details['mains']):
            print(f"  Main {i+1}: {main['cartes_hero']} -> {main['action_hero']} -> {main['resultat']:.0f}")
        
        print("✓ Test des détails d'expresso réussi!\n")
        return True
        
    except Exception as e:
        print(f"✗ Erreur dans le test des détails d'expresso: {e}")
        return False
    finally:
        os.unlink(temp_file)

def test_integration():
    """Test d'intégration avec analyse complète"""
    print("=== Test d'intégration ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Créer quelques fichiers de test
        tournament_content = """Winamax Poker - Tournament "Test" buyIn: 5.00€ + 0.50€
*** SUMMARY ***
Buy-in: 5.50€
You won: 10.00€"""
        
        expresso_content = """Winamax Poker - Tournament "Expresso Test" buyIn: 2.00€ + 0.20€  
*** SUMMARY ***
Buy-in: 2.20€
You won: 6.00€"""
        
        # Écrire les fichiers
        with open(os.path.join(temp_dir, "2024-01-15_Tournament_123_summary.txt"), 'w') as f:
            f.write(tournament_content)
        
        with open(os.path.join(temp_dir, "2024-01-15_Expresso_456_summary.txt"), 'w') as f:
            f.write(expresso_content)
        
        try:
            # Test analyse tournois
            results_tournois = analyser_resultats_tournois(temp_dir)
            print(f"✓ Analyse tournois: {results_tournois['nombre_tournois']} tournoi(s) trouvé(s)")
            
            # Test analyse expressos
            results_expressos = analyser_resultats_expresso(temp_dir)  
            print(f"✓ Analyse expressos: {results_expressos['nombre_expressos']} expresso(s) trouvé(s)")
            
            print("✓ Test d'intégration réussi!\n")
            return True
            
        except Exception as e:
            print(f"✗ Erreur dans le test d'intégration: {e}")
            return False

if __name__ == "__main__":
    print("Lancement des tests pour la fonctionnalité de focus sur les tournois...\n")
    
    tests = [
        test_tournament_details,
        test_expresso_details,
        test_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"=== Résultats des tests ===")
    print(f"Tests réussis: {passed}/{total}")
    
    if passed == total:
        print("🎉 Tous les tests sont passés!")
        sys.exit(0)
    else:
        print("❌ Certains tests ont échoué")
        sys.exit(1)