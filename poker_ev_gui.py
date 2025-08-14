import tkinter as tk
from tkinter import ttk, filedialog
import random
import os
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from recapitulatif_tournoi import analyser_resultats_tournois
from recapitulatif_expresso import analyser_resultats_expresso
from recapitulatif_cash_game import analyser_resultats_cash_game

from poker_logic import create_deck, Card, Hand, RANKS, SUITS, Player, PokerScenario, parse_hand_string, parse_community_cards_string
from poker_calculations import calculate_equity_fast, parse_range_string, calculate_chip_ev

# Initialize the evaluator once to avoid repeated instantiation

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
def run_analysis(analysis_function, widgets, graph_config):
    """
    Fonction générique pour lancer une analyse, traiter les résultats et mettre à jour l'UI.
    """
    repertoire = filedialog.askdirectory(title=f"Sélectionnez le dossier d'historique pour {graph_config['title']}")
    if not repertoire:
        return

    tree = widgets['tree']
    canvas_frame = widgets['canvas_frame']
    summary_label = widgets['summary_label']
    root = summary_label.winfo_toplevel() # Obtenir la fenêtre racine

    # Nettoyer les anciens résultats
    for item in tree.get_children():
        tree.delete(item)
    for widget in canvas_frame.winfo_children():
        widget.destroy()
    summary_label.config(text="Analyse en cours...")
    root.update_idletasks()

    try:
        # Appelle la fonction de traitement appropriée (tournoi, expresso, etc.)
        if analysis_function == analyser_resultats_cash_game:
            # TODO: Rendre le nom d'utilisateur configurable dans l'UI
            user_name = None
            if widgets['user_name_entry']:
                user_name = widgets['user_name_entry'].get()
                if not user_name:
                    raise ValueError("Veuillez entrer un nom d'utilisateur pour l'analyse cash game.")
                    return
            results = analysis_function(repertoire, user_name)
        else:
            results = analysis_function(repertoire)

        # Mise à jour du tableau (si des détails sont retournés)
        if "details" in results:
            for item in results["details"]:
                tree.insert("", "end", values=(item.get("fichier", "N/A"), f'{item.get("buy_in", 0):.2f}€', f'{item.get("gains", 0):.2f}€', f'{item.get("net", 0):+.2f}€'))

        # --- CORRECTION ---
        # On construit la chaîne de résumé ici, à partir des données reçues.
        # L'ancien code `summary_label.config(text=results["summary_text"])` est supprimé.
        
        summary_text = ""
        if analysis_function == analyser_resultats_cash_game:
            # Format spécifique pour le cash game
            total_hands = results.get("total_hands", 0)
            net_result = results.get("resultat_net_total", 0.0)
            summary_text = f"Mains jouées: {total_hands} | Résultat Net Global: {net_result:+.2f}€"
        else:
            # Format pour les tournois et expressos
            count = results.get("nombre_tournois") or results.get("nombre_expressos", 0)
            total_buy_ins = results.get("total_buy_ins", 0.0)
            total_gains = results.get("total_gains", 0.0)
            net_result = results.get("resultat_net_total", 0.0)
            item_name = "Tournois" if analysis_function == analyser_resultats_tournois else "Expressos"
            summary_text = (f"{item_name} analysés: {count} | "
                            f"Total Buy-ins: {total_buy_ins:.2f}€ | "
                            f"Total Gains: {total_gains:.2f}€ | "
                            f"Résultat Net Global: {net_result:+.2f}€")

        summary_label.config(text=summary_text)
        # --- FIN DE LA CORRECTION ---

        # Création du graphique
        if "cumulative_results" in results and results["cumulative_results"]:
            fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
            ax.plot(results["cumulative_results"], marker='o', linestyle='-', markersize=3, color=graph_config.get('color', 'blue'))
            ax.axhline(0, color='grey', linewidth=0.8, linestyle='--')
            ax.set_title(graph_config['title'])
            ax.set_xlabel(graph_config['xlabel'])
            ax.set_ylabel("Résultat Net Cumulé (€)")
            ax.grid(True, which='both', linestyle='--', linewidth=0.5)
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        else:
             for widget in canvas_frame.winfo_children():
                widget.destroy()


    except FileNotFoundError as e:
        summary_label.config(text=str(e))
    except Exception as e:
        summary_label.config(text=f"Une erreur est survenue: {e}")

def create_analysis_tab(notebook, tab_name, analysis_function, graph_config):
    """
    Crée un onglet d'analyse complet et générique.
    """
    tab = ttk.Frame(notebook, padding="10")
    notebook.add(tab, text=tab_name)
    tab.columnconfigure(0, weight=1)
    tab.rowconfigure(1, weight=2)  # Poids pour le tableau
    tab.rowconfigure(2, weight=3)  # Poids pour le graphique

    # --- Widgets ---
    controls_frame = ttk.Frame(tab)
    analyze_button = ttk.Button(controls_frame, text=f"Lancer l'analyse {tab_name}")
    
    # --- AJOUT D'UN CHAMP POUR LE PSEUDO ---
    user_name_label = None
    user_name_entry = None
    if analysis_function == analyser_resultats_cash_game:
        user_name_label = ttk.Label(controls_frame, text="Votre Pseudo:")
        user_name_label.pack(side=tk.LEFT, padx=(0, 5))
        user_name_entry = ttk.Entry(controls_frame)
        user_name_entry.insert(0, "PogShellCie") # Default value
        user_name_entry.pack(side=tk.LEFT, padx=5)
    
    analyze_button.pack(side=tk.LEFT, padx=5)
    # ...

    results_frame = ttk.LabelFrame(tab, text=f"Résultats détaillés ({tab_name})")
    columns = ('filename', 'buyin', 'winnings', 'net')
    tree = ttk.Treeview(results_frame, columns=columns, show='headings')
    scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=tree.yview)
    
    canvas_frame = ttk.LabelFrame(tab, text="Graphique des gains cumulés")
    summary_label = ttk.Label(tab, text="Prêt à analyser.", anchor="w", font=('TkDefaultFont', 9, 'bold'))

    # --- Configuration du tableau ---
    tree.heading('filename', text='Fichier / Session')
    tree.heading('buyin', text='Buy-in')
    tree.heading('winnings', text='Gains')
    tree.heading('net', text='Net')
    tree.column('filename', width=300)
    tree.column('buyin', width=80, anchor='e')
    tree.column('winnings', width=80, anchor='e')
    tree.column('net', width=80, anchor='e')
    tree.configure(yscroll=scrollbar.set)

    # --- Placement des widgets ---
    controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
    analyze_button.pack()
    results_frame.grid(row=1, column=0, sticky="nsew", pady=5)
    results_frame.columnconfigure(0, weight=1)
    results_frame.rowconfigure(0, weight=1)
    tree.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")
    canvas_frame.grid(row=2, column=0, sticky="nsew", pady=5)
    summary_label.grid(row=3, column=0, sticky="ew", pady=(10, 0))

    # --- Lier la commande ---
    widgets = {'tree': tree, 'canvas_frame': canvas_frame, 'summary_label': summary_label, 'user_name_entry': user_name_entry}
    analyze_button.config(command=lambda: run_analysis(analysis_function, widgets, graph_config))

    return tab

def create_gui():
    """Creates the main GUI window for the poker EV calculator with improved layout."""
    global root # Rendre root accessible globalement pour la fonction d'analyse
    root = tk.Tk()
    root.title("Poker Tools")
    root.geometry("900x800") # Taille par défaut

    # This ensures the script exits when the window is closed.
    root.protocol("WM_DELETE_WINDOW", root.destroy)

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
    }

    # --- Lier les commandes des boutons ---
    calculate_button.config(command=lambda: calculate_ev_from_gui(gui_elements))
    optimize_button.config(command=lambda: find_optimal_bet_from_gui(gui_elements))

    # --- Onglets d'Analyse (maintenant génériques) ---
    create_analysis_tab(
        notebook,
        tab_name="Tournois",
        analysis_function=analyser_resultats_tournois,
        graph_config={'title': 'Performance en Tournois', 'xlabel': 'Tournoi N°', 'color': 'blue'}
    )
    
    create_analysis_tab(
        notebook,
        tab_name="Expresso",
        analysis_function=analyser_resultats_expresso,
        graph_config={'title': 'Performance en Expresso', 'xlabel': 'Expresso N°', 'color': 'red'}
    )

    create_analysis_tab(
        notebook,
        tab_name="Cash Game",
        analysis_function=analyser_resultats_cash_game,
        graph_config={'title': 'Performance en Cash Game', 'xlabel': 'Main N°', 'color': 'green'}
    )

    return root

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
    main_window = create_gui()
    main_window.mainloop()
