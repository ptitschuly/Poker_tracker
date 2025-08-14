import tkinter as tk
from tkinter import ttk, filedialog
import random
import itertools
import math
import os
import re
# --- NOUVEAUX IMPORTS ---
from deuces import Card as DeucesCard, Evaluator
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# --- IMPORTATIONS DIRECTES DEPUIS LES AUTRES FICHIERS ---
from recapitulatif_tournoi import traiter_resume as traiter_resume_tournoi
from Performance_cash_game import process_hand as process_cash_game_hand


# --- Poker Logic Classes and Functions (inchangé) ---

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

# Initialize the evaluator once to avoid repeated instantiation
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

def setup_scenario_from_gui(gui_elements):
    """Parses all GUI inputs and returns a configured scenario and key player details."""
    position_combobox = gui_elements['position_combobox']
    stacks_str = gui_elements['stacks_entry'].get()
    stack_strings = [s.strip() for s in stacks_str.split(',') if s.strip()]
    n_players = len(stack_strings)
    if n_players not in (2, 3):
        raise ValueError("Only 2 or 3 players supported.")

    if n_players == 2: positions = ['SB', 'BB']
    else: positions = ['BTN', 'SB', 'BB']
    position_combobox['values'] = positions
    selected_pos = position_combobox.get()
    if selected_pos not in positions:
        position_combobox.set(positions[0])
        selected_pos = positions[0]
    
    hero_pos_index = positions.index(selected_pos)
    player_stacks_raw = [float(s) for s in stack_strings]
    hero_stack = player_stacks_raw[hero_pos_index]
    opponent_stacks = [s for i, s in enumerate(player_stacks_raw) if i != hero_pos_index]
    player_stacks = [hero_stack] + opponent_stacks
    
    player_names = [f"Player {i+1}" for i in range(n_players)]
    player_name = player_names[0]
    players = [Player(name, stack) for name, stack in zip(player_names, player_stacks)]
    
    small_blind = float(gui_elements['sb_entry'].get() or '0')
    big_blind = float(gui_elements['bb_entry'].get() or '0')
    ante = float(gui_elements['ante_entry'].get() or '0')
    
    hole_cards_str = gui_elements['hole_cards_entry'].get().strip()
    player_hole_cards = parse_hand_string(hole_cards_str)
    players[0].hole_cards = player_hole_cards
    
    community_cards_str = gui_elements['community_cards_entry'].get().strip()
    community_cards = parse_community_cards_string(community_cards_str)
    if any(card in community_cards for card in player_hole_cards.cards):
        raise ValueError("Overlap between hole cards and community cards.")
        
    scenario = PokerScenario(players, small_blind, big_blind, ante)
    scenario.community_cards = community_cards
    
    opponent_range_string = gui_elements['opponent_range_entry'].get().strip()
    
    return scenario, player_name, opponent_range_string, selected_pos, big_blind, small_blind

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

def find_optimal_bet_from_gui(gui_elements):
    """
    Iterates through common bet sizes to find the action (fold, call, or raise)
    with the highest Expected Value.
    """
    ev_result_label = gui_elements['ev_result_label']
    ev_result_label.config(text="Optimizing bet size...", foreground="black")

    try:
        # 1. Setup the scenario using the new helper function
        scenario, player_name, opponent_range_string, selected_pos, big_blind, small_blind = setup_scenario_from_gui(gui_elements)

        # --- Corrected Optimization Logic ---
        
        # 2. Calculate EV of Folding
        ev_fold = 0.0

        # 3. Calculate EV of Calling
        # This logic assumes we are facing a single pre-flop bet of one big blind.
        amount_to_call = big_blind - (small_blind if selected_pos == 'SB' else 0)
        ev_call = calculate_chip_ev(scenario, player_name, opponent_range_string, 'call', amount_to_call)

        # 4. Calculate EV for a range of pre-flop Raise Sizes
        # Pre-flop raises are typically multiples of the big blind.
        raise_multipliers = [2.5, 3.0, 3.5, 4.0] 
        best_raise_ev = -float('inf')
        optimal_raise_size = 0

        effective_stack = min(scenario.players[0].stack, scenario.players[1].stack)

        for multiplier in raise_multipliers:
            # The total amount of the raise
            raise_amount = min(big_blind * multiplier, effective_stack)
            
            # A legal raise must be at least the size of the previous bet, and the raise amount
            # must be at least the size of the big blind.
            min_raise_to = big_blind * 2
            if raise_amount < min_raise_to: continue

            current_raise_ev = calculate_chip_ev(scenario, player_name, opponent_range_string, 'raise', raise_amount)
            
            if current_raise_ev > best_raise_ev:
                best_raise_ev = current_raise_ev
                optimal_raise_size = raise_amount

        # 5. Compare all options and find the best one
        best_action = "Fold"
        max_ev = ev_fold

        if ev_call > max_ev:
            best_action = f"Call {amount_to_call:.2f}"
            max_ev = ev_call
        
        if best_raise_ev > max_ev:
            best_action = f"Raise to {optimal_raise_size:.2f}"
            max_ev = best_raise_ev

        # 6. Display the result
        result_text = f"Optimal Action: {best_action} (EV: {max_ev:.2f})"
        ev_result_label.config(text=result_text, foreground="blue")

    except Exception as e:
        ev_result_label.config(text=f"Error: {e}", foreground="red")

def calculate_ev_from_gui(gui_elements):
    """
    Efficiently parses input values from the GUI dictionary, creates poker objects,
    calls the calculate_chip_ev function, and updates the GUI label.
    """
    ev_result_label = gui_elements['ev_result_label']
    ev_result_label.config(text="Calculating...", foreground="black")

    try:
        # 1. Setup the scenario using the new helper function
        scenario, player_name, opponent_range_string, _, _, _ = setup_scenario_from_gui(gui_elements)

        # 2. Get action details from GUI for single calculation
        bet_size = float(gui_elements['bet_size_entry'].get() or '0')
        player_action = gui_elements['action_combobox'].get().strip().lower()
        if player_action not in ('fold', 'call', 'raise'):
            raise ValueError("Invalid action.")
        if player_action == 'raise' and bet_size <= 0:
            raise ValueError("Raise amount must be positive.")

        # 3. Calculate EV
        calculated_ev = calculate_chip_ev(
            scenario=scenario,
            player_name=player_name,
            opponent_range_string=opponent_range_string,
            player_action=player_action,
            bet_size=bet_size
        )
        ev_result_label.config(text=f"{calculated_ev:.2f} Chips", foreground="green")

    except Exception as e:
        ev_result_label.config(text=f"Error: {e}", foreground="red")


# --- GUI Functions ---

def parse_hand_string(hand_string):
    """Parses a two-character hand string (e.g., 'AhKd') into a Hand object."""
    if len(hand_string) != 4:
        raise ValueError("Hole cards string must be exactly 4 characters (e.g., 'AhKd').")
    card1_str = hand_string[:2]
    card2_str = hand_string[2:]
    card1 = Card(card1_str[0].upper(), card1_str[1].lower())
    card2 = Card(card2_str[0].upper(), card2_str[1].lower())
    if card1 == card2:
        raise ValueError(f"Invalid hand string '{hand_string}': Cannot have duplicate cards.")
    return Hand(card1, card2)

def parse_community_cards_string(community_cards_string):
    """Parses a community cards string (e.g., 'AsKd7c') into a list of Card objects."""
    if len(community_cards_string) % 2 != 0:
        raise ValueError("Community cards string must have an even number of characters.")
    cards = []
    clean_string = community_cards_string.lower().replace(" ", "")
    for i in range(0, len(clean_string), 2):
        card_str = clean_string[i:i+2]
        card = Card(card_str[0].upper(), card_str[1])
        cards.append(card)
    if len(cards) != len(set(cards)):
        raise ValueError("Duplicate cards found in community cards.")
    return cards

def run_tournament_analysis_gui(gui_elements):
    """
    Lance l'analyse des tournois et met à jour l'interface graphique.
    """
    repertoire = filedialog.askdirectory(title="Sélectionnez le dossier d'historique des tournois")
    if not repertoire:
        return

    tree = gui_elements['results_tree']
    canvas_frame = gui_elements['canvas_frame']
    summary_label = gui_elements['summary_label']

    # Nettoyer les anciens résultats
    for item in tree.get_children():
        tree.delete(item)
    for widget in canvas_frame.winfo_children():
        widget.destroy()

    total_buy_ins = 0.0
    total_gains = 0.0
    fichiers_traites = 0
    gains_cumules = []
    resultat_net_courant = 0.0

    fichiers_summary = [f for f in os.listdir(repertoire) if f.endswith("summary.txt") and "Expresso" not in f]

    for nom_fichier in sorted(fichiers_summary):
        chemin_complet = os.path.join(repertoire, nom_fichier)
        try:
            with open(chemin_complet, 'r', encoding='utf-8') as f:
                contenu = f.read()
            
            buy_in, gains = traiter_resume_tournoi(contenu)
            
            if buy_in > 0:
                fichiers_traites += 1
                resultat_net = gains - buy_in
                
                # Insérer dans le tableau
                tree.insert("", "end", values=(nom_fichier, f"{buy_in:.2f}€", f"{gains:.2f}€", f"{resultat_net:+.2f}€"))
                
                total_buy_ins += buy_in
                total_gains += gains
                resultat_net_courant += resultat_net
                gains_cumules.append(resultat_net_courant)

        except Exception as e:
            print(f"Erreur lors du traitement du fichier {nom_fichier}: {e}")

    # Mettre à jour le résumé
    resultat_net_total = total_gains - total_buy_ins
    summary_text = (f"Tournois analysés : {fichiers_traites} | "
                    f"Total Buy-ins : {total_buy_ins:.2f}€ | "
                    f"Total Gains : {total_gains:.2f}€ | "
                    f"Résultat Net Global : {resultat_net_total:+.2f}€")
    summary_label.config(text=summary_text)

    # Créer le graphique
    if gains_cumules:
        fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
        ax.plot(gains_cumules, marker='o', linestyle='-', markersize=4)
        ax.axhline(0, color='grey', linewidth=0.8, linestyle='--')
        ax.set_title("Gains Cumulés des Tournois")
        ax.set_xlabel("Tournoi N°")
        ax.set_ylabel("Résultat Net Cumulé (€)")
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)


def run_cash_game_analysis_gui(gui_elements):
    """
    Lance l'analyse des mains de cash game et met à jour l'interface graphique.
    """
    folder_path = filedialog.askdirectory(title="Sélectionnez le dossier d'historique Winamax")
    if not folder_path:
        return

    # TODO: Rendre le nom d'utilisateur configurable dans l'UI
    user_name = "PogShellCie" 
    
    canvas_frame = gui_elements['cg_canvas_frame']
    summary_label = gui_elements['cg_summary_label']

    # Nettoyer les anciens résultats
    for widget in canvas_frame.winfo_children():
        widget.destroy()
    summary_label.config(text="Analyse en cours...")
    root.update_idletasks() # Forcer la mise à jour de l'UI

    net_result = 0.0
    hand_results = []
    total_hands = 0
    excluded_keywords = ["Freeroll", "Expresso", "Kill The Fish", "summary"]
    
    try:
        all_items = os.listdir(folder_path)
        hand_history_files = [
            os.path.join(folder_path, item) 
            for item in all_items 
            if item.endswith('.txt') and not any(keyword in item for keyword in excluded_keywords)
        ]

        if not hand_history_files:
            summary_label.config(text="Aucun fichier de cash game valide trouvé.")
            return

        for file_path in hand_history_files:
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()

            # Chaque main commence par "Winamax Poker -"
            hand_list = file_content.split('Winamax Poker -')
            
            for hand_text in hand_list:
                if not hand_text.strip() or "HandId" not in hand_text:
                    continue
                
                # On rajoute le séparateur pour que la fonction de traitement fonctionne correctement
                full_hand_text = 'Winamax Poker -' + hand_text
                hand_net = process_cash_game_hand(full_hand_text, user_name)
                net_result += hand_net
                hand_results.append(net_result)
                total_hands += 1
        
        # Mettre à jour le résumé
        summary_text = f"Fichiers analysés: {len(hand_history_files)} | Mains jouées: {total_hands} | Résultat Net Global: {net_result:+.2f}€"
        summary_label.config(text=summary_text)

        # Créer le graphique
        if hand_results:
            fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
            ax.plot(hand_results)
            ax.axhline(0, color='grey', linewidth=0.8, linestyle='--')
            ax.set_title(f"Performance en Cash Game pour {user_name}")
            ax.set_xlabel("Nombre de mains")
            ax.set_ylabel("Résultat Net Cumulé (€)")
            ax.grid(True)
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        else:
            summary_label.config(text="Aucune main valide trouvée dans les fichiers.")

    except Exception as e:
        summary_label.config(text=f"Erreur lors de l'analyse: {e}")


def create_gui():
    """Creates the main GUI window for the poker EV calculator with improved layout."""
    root = tk.Tk()
    root.title("Poker Tools")
    root.geometry("850x750") # Taille par défaut

    # --- Création du Notebook (onglets) ---
    notebook = ttk.Notebook(root)
    notebook.pack(pady=10, padx=10, fill="both", expand=True)

    # --- Onglet 1: Calculateur d'EV ---
    ev_tab = ttk.Frame(notebook, padding="10")
    notebook.add(ev_tab, text="Calculateur d'EV")

    # Frame for scenario details
    scenario_frame = ttk.LabelFrame(ev_tab, text="Scenario Details")
    scenario_frame.grid(row=0, column=0, padx=15, pady=10, sticky="ew") # Increased padding
    ev_tab.columnconfigure(0, weight=1)

    # Configure scenario_frame grid
    scenario_frame.columnconfigure(1, weight=1)
    scenario_frame.columnconfigure(3, weight=1) # Add weight for the new combobox column


    # Player Stacks
    ttk.Label(scenario_frame, text="Player Stacks (comma-separated):").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    stacks_entry = ttk.Entry(scenario_frame, width=40)
    stacks_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
    stacks_entry.insert(0, "1000, 1500") # Default value example

    # Your Position
    ttk.Label(scenario_frame, text="Your Position:").grid(row=0, column=2, sticky="w", padx=(15, 5))
    position_options = ['SB', 'BB'] # Default for 2 players
    position_combobox = ttk.Combobox(scenario_frame, values=position_options, state="readonly", width=10)
    position_combobox.grid(row=0, column=3, sticky="ew", padx=5)
    position_combobox.set('SB') # Default selection


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
    hand_frame = ttk.LabelFrame(ev_tab, text="Player and Hand Details")
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
    action_frame = ttk.LabelFrame(ev_tab, text="Opponent and Action Details")
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
    output_frame = ttk.LabelFrame(ev_tab, text="Result")
    output_frame.grid(row=3, column=0, padx=15, pady=10, sticky="ew") # Increased padding

    # Configure output_frame grid
    output_frame.columnconfigure(1, weight=1)

    ttk.Label(output_frame, text="Calculated EV:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    ev_result_label = ttk.Label(output_frame, text="Enter details and click Calculate", font=('TkDefaultFont', 12, 'bold'), anchor='w') # Set initial text, sticky w
    ev_result_label.grid(row=0, column=1, sticky="ew", padx=10, pady=5) # Sticky ew

    # --- Buttons Frame ---
    buttons_frame = ttk.Frame(ev_tab)
    buttons_frame.grid(row=4, column=0, padx=15, pady=15)
    buttons_frame.columnconfigure(0, weight=1)
    buttons_frame.columnconfigure(1, weight=1)

    # Add a button to trigger single calculation
    calculate_button = ttk.Button(buttons_frame, text="Calculate EV for Given Size")
    calculate_button.grid(row=0, column=0, padx=5, sticky="ew")

    # Add a new button to trigger optimization
    optimize_button = ttk.Button(buttons_frame, text="Find Optimal Bet")
    optimize_button.grid(row=0, column=1, padx=5, sticky="ew")


    # Store entry widgets for later access (e.g., in the calculation function)
    gui_elements = {
        'stacks_entry': stacks_entry,
        'position_combobox': position_combobox,
        'sb_entry': sb_entry,
        'bb_entry': bb_entry,
        'ante_entry': ante_entry,
        'hole_cards_entry': hole_cards_entry,
        'community_cards_entry': community_cards_entry,
        'opponent_range_entry': opponent_range_entry,
        'action_combobox': action_combobox,
        'bet_size_entry': bet_size_entry,
        'ev_result_label': ev_result_label,
        'calculate_button': calculate_button,
        'optimize_button': optimize_button
    }

    # --- Onglet 2: Analyse de Tournois ---
    tournament_tab = ttk.Frame(notebook, padding="10")
    notebook.add(tournament_tab, text="Analyse Tournois")
    tournament_tab.columnconfigure(0, weight=1)
    tournament_tab.rowconfigure(1, weight=1) # Permet au tableau de s'étendre
    tournament_tab.rowconfigure(2, weight=2) # Permet au graphique de s'étendre

    # Frame pour les contrôles
    controls_frame = ttk.Frame(tournament_tab)
    controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
    analyze_button = ttk.Button(controls_frame, text="Lancer l'analyse des tournois")
    analyze_button.pack()

    # Frame pour les résultats (tableau)
    results_frame = ttk.LabelFrame(tournament_tab, text="Résultats par tournoi")
    results_frame.grid(row=1, column=0, sticky="nsew", pady=5)
    results_frame.columnconfigure(0, weight=1)
    results_frame.rowconfigure(0, weight=1)

    # Tableau (Treeview)
    columns = ('filename', 'buyin', 'winnings', 'net')
    results_tree = ttk.Treeview(results_frame, columns=columns, show='headings')
    results_tree.heading('filename', text='Fichier')
    results_tree.heading('buyin', text='Buy-in')
    results_tree.heading('winnings', text='Gains')
    results_tree.heading('net', text='Net')
    results_tree.column('filename', width=300)
    results_tree.column('buyin', width=80, anchor='e')
    results_tree.column('winnings', width=80, anchor='e')
    results_tree.column('net', width=80, anchor='e')
    
    # Scrollbar pour le tableau
    scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=results_tree.yview)
    results_tree.configure(yscroll=scrollbar.set)
    results_tree.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    # Frame pour le graphique
    canvas_frame = ttk.LabelFrame(tournament_tab, text="Graphique des gains cumulés")
    canvas_frame.grid(row=2, column=0, sticky="nsew", pady=5)
    canvas_frame.columnconfigure(0, weight=1)
    canvas_frame.rowconfigure(0, weight=1)

    # Label pour le résumé global
    summary_label = ttk.Label(tournament_tab, text="Prêt à analyser.", anchor="w", font=('TkDefaultFont', 9, 'bold'))
    summary_label.grid(row=3, column=0, sticky="ew", pady=(10, 0))

    # Ajouter les nouveaux éléments au dictionnaire
    gui_elements['results_tree'] = results_tree
    gui_elements['canvas_frame'] = canvas_frame
    gui_elements['summary_label'] = summary_label
    gui_elements['analyze_button'] = analyze_button

    # Lier la fonction au bouton d'analyse
    analyze_button.config(command=lambda: run_tournament_analysis_gui(gui_elements))


    # --- Onglet 3: Analyse de Cash Game ---
    cash_game_tab = ttk.Frame(notebook, padding="10")
    notebook.add(cash_game_tab, text="Analyse Cash Game")
    cash_game_tab.columnconfigure(0, weight=1)
    cash_game_tab.rowconfigure(1, weight=1) # Permet au graphique de s'étendre

    # Frame pour les contrôles
    cg_controls_frame = ttk.Frame(cash_game_tab)
    cg_controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
    cg_analyze_button = ttk.Button(cg_controls_frame, text="Lancer l'analyse Cash Game")
    cg_analyze_button.pack()

    # Frame pour le graphique
    cg_canvas_frame = ttk.LabelFrame(cash_game_tab, text="Graphique des gains cumulés (Cash Game)")
    cg_canvas_frame.grid(row=1, column=0, sticky="nsew", pady=5)
    cg_canvas_frame.columnconfigure(0, weight=1)
    cg_canvas_frame.rowconfigure(0, weight=1)

    # Label pour le résumé global
    cg_summary_label = ttk.Label(cash_game_tab, text="Prêt à analyser.", anchor="w", font=('TkDefaultFont', 9, 'bold'))
    cg_summary_label.grid(row=2, column=0, sticky="ew", pady=(10, 0))

    # Ajouter les nouveaux éléments au dictionnaire
    gui_elements['cg_canvas_frame'] = cg_canvas_frame
    gui_elements['cg_summary_label'] = cg_summary_label
    gui_elements['cg_analyze_button'] = cg_analyze_button

    # Lier la fonction au bouton d'analyse
    cg_analyze_button.config(command=lambda: run_cash_game_analysis_gui(gui_elements))


    return root, gui_elements

def calculate_ev_from_gui(gui_elements):
    """
    Efficiently parses input values from the GUI dictionary, creates poker objects,
    calls the calculate_chip_ev function, and updates the GUI label.
    """
    ev_result_label = gui_elements['ev_result_label']
    ev_result_label.config(text="Calculating...", foreground="black")

    try:
        # 1. Setup the scenario using the new helper function
        scenario, player_name, opponent_range_string, _, _, _ = setup_scenario_from_gui(gui_elements)

        # 2. Get action details from GUI for single calculation
        bet_size = float(gui_elements['bet_size_entry'].get() or '0')
        player_action = gui_elements['action_combobox'].get().strip().lower()
        if player_action not in ('fold', 'call', 'raise'):
            raise ValueError("Invalid action.")
        if player_action == 'raise' and bet_size <= 0:
            raise ValueError("Raise amount must be positive.")

        # 3. Calculate EV
        calculated_ev = calculate_chip_ev(
            scenario=scenario,
            player_name=player_name,
            opponent_range_string=opponent_range_string,
            player_action=player_action,
            bet_size=bet_size
        )
        ev_result_label.config(text=f"{calculated_ev:.2f} Chips", foreground="green")

    except Exception as e:
        ev_result_label.config(text=f"Error: {e}", foreground="red")


# --- GUI Creation and Mainloop ---
if __name__ == "__main__":
    root, gui_elements = create_gui()
    
    calculate_button = gui_elements.get('calculate_button')
    if calculate_button:
        calculate_button.config(command=lambda: calculate_ev_from_gui(gui_elements))

    optimize_button = gui_elements.get('optimize_button')
    if optimize_button:
        optimize_button.config(command=lambda: find_optimal_bet_from_gui(gui_elements))

    root.mainloop()