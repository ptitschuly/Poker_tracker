#!/usr/bin/env python3
"""
Démonstration de la nouvelle fonctionnalité de focus sur les tournois.
Ce script montre comment utiliser les nouvelles fonctions pour analyser 
les détails complets d'un tournoi ou expresso.
"""

import sys
import os
import json

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from recapitulatif_tournoi import analyser_resultats_tournois, extraire_details_tournoi
from recapitulatif_expresso import analyser_resultats_expresso, extraire_details_expresso

def demo_functionality():
    """Démonstration complète de la nouvelle fonctionnalité"""
    
    print("=" * 70)
    print("   DÉMONSTRATION - FOCUS SUR LES TOURNOIS")
    print("=" * 70)
    print()
    
    # Utiliser les fichiers de test que nous avons créés
    test_dir = "/tmp/sample_poker_data"
    
    if not os.path.exists(test_dir):
        print("⚠️  Répertoire de test non trouvé. Création des données de test...")
        return
    
    print("🔍 ÉTAPE 1: Analyse globale des tournois")
    print("-" * 50)
    
    try:
        # Analyse globale des tournois
        results_tournois = analyser_resultats_tournois(test_dir)
        
        print(f"📊 Résultats globaux:")
        print(f"   • Nombre de tournois: {results_tournois['nombre_tournois']}")
        print(f"   • Total Buy-ins: {results_tournois['total_buy_ins']:.2f}€")
        print(f"   • Total Gains: {results_tournois['total_gains']:.2f}€")
        print(f"   • Résultat Net: {results_tournois['resultat_net_total']:+.2f}€")
        print()
        
        print("📋 Liste des tournois:")
        for i, tournoi in enumerate(results_tournois['details'], 1):
            print(f"   {i}. {tournoi['fichier']}")
            print(f"      Buy-in: {tournoi['buy_in']:.2f}€ | Gains: {tournoi['gains']:.2f}€ | Net: {tournoi['net']:+.2f}€")
        print()
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse des tournois: {e}")
        return
    
    print("🔍 ÉTAPE 2: Focus sur un tournoi spécifique")
    print("-" * 50)
    
    # Prendre le premier tournoi pour la démonstration
    if results_tournois['details']:
        premier_tournoi = results_tournois['details'][0]
        fichier_path = os.path.join(test_dir, premier_tournoi['fichier'])
        
        print(f"🎯 Focus sur: {premier_tournoi['fichier']}")
        print()
        
        try:
            # Extraire les détails complets
            details = extraire_details_tournoi(fichier_path)
            
            print("📈 Informations détaillées:")
            print(f"   • Fichier: {details['fichier']}")
            print(f"   • Buy-in: {details['buy_in']:.2f}€")
            print(f"   • Gains: {details['gains']:.2f}€")
            print(f"   • Résultat Net: {details['net']:+.2f}€")
            print(f"   • Position finale: {details['position_finale']}")
            print(f"   • Durée: {details['duree']}")
            print(f"   • Nombre de mains: {details['nombre_mains']}")
            print()
            
            if details['mains']:
                print("🃏 Détail des mains jouées:")
                print("   " + "─" * 60)
                print("   Main | Niveau | Cartes   | Board           | Action | Résultat")
                print("   " + "─" * 60)
                
                for main in details['mains']:
                    cartes = main['cartes_hero'] or '-'
                    board = main['board'] or '-'
                    action = main['action_hero'] or '-'
                    resultat = f"{main['resultat']:.0f}" if main['resultat'] > 0 else "-"
                    
                    print(f"   {main['numero']:4} | {main['niveau']:6} | {cartes:8} | {board:15} | {action:6} | {resultat:>7}")
                
                print("   " + "─" * 60)
            print()
            
        except Exception as e:
            print(f"❌ Erreur lors de l'extraction des détails: {e}")
    
    print("🔍 ÉTAPE 3: Analyse des expressos")
    print("-" * 50)
    
    try:
        # Analyse globale des expressos
        results_expressos = analyser_resultats_expresso(test_dir)
        
        print(f"📊 Résultats globaux expressos:")
        print(f"   • Nombre d'expressos: {results_expressos['nombre_expressos']}")
        print(f"   • Total Buy-ins: {results_expressos['total_buy_ins']:.2f}€")
        print(f"   • Total Gains: {results_expressos['total_gains']:.2f}€")
        print(f"   • Résultat Net: {results_expressos['resultat_net_total']:+.2f}€")
        print()
        
        if results_expressos['details']:
            print("📋 Liste des expressos:")
            for i, expresso in enumerate(results_expressos['details'], 1):
                print(f"   {i}. {expresso['fichier']}")
                print(f"      Buy-in: {expresso['buy_in']:.2f}€ | Gains: {expresso['gains']:.2f}€ | Net: {expresso['net']:+.2f}€")
            print()
            
            # Focus sur le premier expresso
            premier_expresso = results_expressos['details'][0]
            fichier_path = os.path.join(test_dir, premier_expresso['fichier'])
            
            print(f"🎯 Focus sur: {premier_expresso['fichier']}")
            
            details_expresso = extraire_details_expresso(fichier_path)
            print(f"   • Nombre de mains: {details_expresso['nombre_mains']}")
            print(f"   • Durée: {details_expresso['duree']}")
            print(f"   • Position finale: {details_expresso['position_finale']}")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse des expressos: {e}")
    
    print()
    print("✨ FONCTIONNALITÉS IMPLÉMENTÉES:")
    print("-" * 50)
    print("✅ Double-clic sur un tournoi dans l'interface pour voir les détails")
    print("✅ Fenêtre popup avec toutes les informations du tournoi")
    print("✅ Liste détaillée de toutes les mains jouées")
    print("✅ Statistiques spécifiques au tournoi")
    print("✅ Graphiques des actions du joueur")
    print("✅ Navigation facile pour retourner à la liste globale")
    print("✅ Support pour les tournois ET les expressos")
    print("✅ Interface intuitive avec info-bulle")
    print()
    
    print("🎮 UTILISATION:")
    print("-" * 50)
    print("1. Lancez l'application: python3 poker_ev_gui.py")
    print("2. Sélectionnez votre dossier d'historiques")
    print("3. Allez dans l'onglet 'Tournois' ou 'Expresso'")
    print("4. Cliquez sur 'Lancer l'analyse'")
    print("5. Double-cliquez sur n'importe quel tournoi dans la liste")
    print("6. Explorez les détails dans la fenêtre qui s'ouvre")
    print("7. Fermez la fenêtre pour revenir à la liste")
    print()
    
    print("=" * 70)
    print("   DÉMONSTRATION TERMINÉE")
    print("=" * 70)

if __name__ == "__main__":
    demo_functionality()