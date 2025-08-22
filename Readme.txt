# Outils d'Analyse et de Calcul pour le Poker

Ce projet est une application de bureau développée en Python avec Tkinter, conçue pour aider les joueurs de poker à prendre de meilleures décisions et à analyser leurs performances.

## Fonctionnalités

L'application est divisée en plusieurs onglets, chacun avec un objectif précis :

### 1. Calculateur d'EV (Expected Value)

Cet onglet permet d'analyser une situation de jeu spécifique pour déterminer l'action la plus profitable.

*   **Configuration du Scénario** : Définissez les stacks des joueurs, les blinds, les antes et votre position.
*   **Détails de la Main** : Entrez vos cartes privatives et les cartes communes déjà sur le board.
*   **Analyse de l'Adversaire** : Spécifiez la range de mains probable de votre adversaire (ex: `JJ+, AQs+, AKo`).
*   **Calcul d'EV** : Calculez l'EV (en jetons) pour une action spécifique (Call, Raise d'un certain montant).
*   **Optimisation** : Trouvez automatiquement l'action optimale (Fold, Call, ou le meilleur montant de Raise) en comparant leurs EV respectives.

### 2. Analyse de Résultats (Tournois, Expresso, Cash Game)

Ces onglets permettent d'analyser vos historiques de mains pour suivre vos performances.

*   **Sélection de Dossier** : Choisissez le répertoire où vos historiques de mains (fichiers `.txt` de Winamax) sont sauvegardés.
*   **Analyse Automatique** : Le programme parcourt les fichiers, extrait les résultats de chaque partie (buy-in, gains, etc.).
*   **Tableau de Résultats** : Affiche un résumé détaillé de chaque session ou tournoi.
*   **Graphique de Gains** : Génère une courbe de vos gains cumulés pour visualiser votre progression.
*   **Résumé Statistique** : Calcule et affiche des indicateurs clés comme le total des buy-ins, les gains nets, et le retour sur investissement (ROI).

## Structure du Projet

Le code est organisé en plusieurs fichiers pour une meilleure lisibilité et maintenance (principe de séparation des préoccupations) :

*   `poker_ev_gui.py`: Fichier principal qui lance l'application. Il contient tout le code de l'interface graphique (GUI) et gère les interactions avec l'utilisateur.
*   `poker_logic.py`: Contient les classes et la logique fondamentales du poker (`Card`, `Hand`, `Player`, `PokerScenario`). C'est le "moteur" du jeu.
*   `poker_calculations.py`: Regroupe les fonctions de calcul complexes, comme l'évaluation de l'équité d'une main par simulation de Monte-Carlo et le calcul de l'EV.
*   `recapitulatif_tournoi.py`, `recapitulatif_expresso.py`, `recapitulatif_cash_game.py`: Modules spécialisés dans le parsing des fichiers d'historique pour chaque format de jeu.

## Prérequis et Installation

Pour faire fonctionner ce projet, vous avez besoin de Python 3 et de quelques bibliothèques externes.

1.  **Assurez-vous que Python 3 est installé.**

2.  **Installez les bibliothèques nécessaires via pip :**
    ```bash
    pip install matplotlib deuces
    ```

## Comment Lancer l'Application

Ouvrez un terminal, naviguez jusqu'au dossier du projet et exécutez la commande suivante :

```bash
python poker_ev_gui.py
```

La fenêtre de l'application devrait alors s'ouvrir.

## Testing et Validation

Ce projet inclut un agent de tests automatisé pour valider le bon fonctionnement de toutes les fonctionnalités.

### Lancer les tests

```bash
# Lancer tous les tests
python test_runner_agent.py

# Lancer les tests avec sortie détaillée
python test_runner_agent.py --verbose

# Lister tous les tests disponibles
python test_runner_agent.py --list
```

Pour plus d'informations sur les tests, consultez `TEST_RUNNER_DOCS.md`.


A venir : 
- Tournoi : 
- Cash game : WTSD% + Fold to 3-Bet  