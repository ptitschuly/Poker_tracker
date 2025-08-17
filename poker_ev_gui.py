import tkinter as tk
from tkinter import ttk, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
from focus_cash_game import show_double_entry_table

from recapitulatif_tournoi import analyser_resultats_tournois
from recapitulatif_expresso import analyser_resultats_expresso
from recapitulatif_cash_game import analyser_resultats_cash_game

from poker_logic import  RANKS, Player, PokerScenario, parse_hand_string, parse_community_cards_string
from poker_calculations import calculate_chip_ev


def setup_scenario_from_gui(gui_elements):
    """Parses all GUI inputs and returns a configured scenario and key player details."""
    position_combobox = gui_elements['position_combobox']
    stacks_str = gui_elements['stacks_entry'].get()
    stack_strings = [s.strip() for s in stacks_str.split(',') if s.strip()]
    n_players = len(stack_strings)
    if n_players not in (2, 3):
        raise ValueError("Only 2 or 3 players supported.")

    if n_players == 2:
        positions = ['SB', 'BB']
    else:
        positions = ['BTN', 'SB', 'BB']
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
    try:
        player_hole_cards = parse_hand_string(hole_cards_str)
    except ValueError as e:
        print(f"Error parsing hole cards: {e}")
        return None
    players[0].hole_cards = player_hole_cards
    
    community_cards_str = gui_elements['community_cards_entry'].get().strip()
    try: 
        community_cards = parse_community_cards_string(community_cards_str)
    except ValueError as e:
        print(f"Error parsing community cards: {e}")
        return None
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
        scenario, player_name, opponent_range_string, selected_pos, big_blind, small_blind = setup_scenario_from_gui(gui_elements)

        ev_fold = 0.0

        amount_to_call = big_blind - (small_blind if selected_pos == 'SB' else 0)
        ev_call = calculate_chip_ev(scenario, player_name, opponent_range_string, 'call', amount_to_call)

        raise_multipliers = [2.5, 3.0, 3.5, 4.0] 
        best_raise_ev = -float('inf')
        optimal_raise_size = 0

        effective_stack = min(scenario.players[0].stack, scenario.players[1].stack)

        for multiplier in raise_multipliers:
            raise_amount = min(big_blind * multiplier, effective_stack)
            min_raise_to = big_blind * 2
            if raise_amount < min_raise_to:
                continue

            current_raise_ev = calculate_chip_ev(scenario, player_name, opponent_range_string, 'raise', raise_amount)
            if current_raise_ev > best_raise_ev:
                best_raise_ev = current_raise_ev
                optimal_raise_size = raise_amount

        best_action = "Fold"
        max_ev = ev_fold

        if ev_call > max_ev:
            best_action = f"Call {amount_to_call:.2f}"
            max_ev = ev_call
        
        if best_raise_ev > max_ev:
            best_action = f"Raise to {optimal_raise_size:.2f}"
            max_ev = best_raise_ev

        result_text = f"Optimal Action: {best_action} (EV: {max_ev:.2f})"
        ev_result_label.config(text=result_text, foreground="blue")

    except Exception as e:
        ev_result_label.config(text=f"Error: {e}", foreground="red")

def run_analysis(analysis_function, widgets, graph_config):
    """
    Fonction générique pour lancer une analyse, traiter les résultats et mettre à jour l'UI.
    """
    global selected_history_directory
    # Utilise le répertoire global, ne demande plus à chaque fois
    repertoire = selected_history_directory
    if not repertoire:
        widgets['summary_label'].config(text="Aucun dossier d'historique sélectionné.")
        return

    tree = widgets['tree']
    canvas_frame = widgets['canvas_frame']
    summary_label = widgets['summary_label']
    root = summary_label.winfo_toplevel()

    for item in tree.get_children():
        tree.delete(item)
    for widget in canvas_frame.winfo_children():
        widget.destroy()
    summary_label.config(text="Analyse en cours...")
    root.update_idletasks()

    try:
        if analysis_function == analyser_resultats_cash_game:
            user_name = None
            if widgets['user_name_entry']:
                user_name = widgets['user_name_entry'].get()
                if not user_name:
                    raise ValueError("Veuillez entrer un nom d'utilisateur pour l'analyse cash game.")
                    return
            
            # Construire les filtres
            date_filter = None
            if widgets.get('date_start_entry') and widgets.get('date_end_entry'):
                date_start = widgets['date_start_entry'].get().strip()
                date_end = widgets['date_end_entry'].get().strip()
                if date_start or date_end:
                    date_filter = (date_start or None, date_end or None)
            
            position_filter = None
            if widgets.get('position_checks'):
                selected_positions = [pos for pos, var in widgets['position_checks'].items() if var.get()]
                if selected_positions and len(selected_positions) < len(widgets['position_checks']):
                    # Seulement filtrer si toutes les positions ne sont pas sélectionnées
                    position_filter = selected_positions
            
            results = analysis_function(repertoire, user_name, date_filter, position_filter)
        elif analysis_function in [analyser_resultats_tournois, analyser_resultats_expresso]:
            # Pour les tournois et expresso, seul le filtre de date est applicable
            date_filter = None
            if widgets.get('date_start_entry') and widgets.get('date_end_entry'):
                date_start = widgets['date_start_entry'].get().strip()
                date_end = widgets['date_end_entry'].get().strip()
                if date_start or date_end:
                    date_filter = (date_start or None, date_end or None)
            
            results = analysis_function(repertoire, date_filter)
        else:
            results = analysis_function(repertoire)

        if "details" in results:
            if analysis_function == analyser_resultats_cash_game:
                tree.heading('filename', text='Main')
                tree.heading('buyin', text='Mise')
                tree.heading('winnings', text='Gains')
                tree.heading('net', text='Net')
                tree.heading('community', text='Community Cards')
                for item in results["details"]:
                    tree.insert("", "end", values=(item.get("hand", "N/A"), f'{item.get("bet_amount", 0):.2f}€', f'{item.get("gains", 0):.2f}€', f'{item.get("net", 0):+.2f}€', item.get("community_cards", "N/A")))
            else:
                tree.heading('filename', text='Fichier / Session')
                tree.heading('buyin', text='Buy-in')
                tree.heading('winnings', text='Gains')
                tree.heading('net', text='Net')
                for item in results["details"]:
                    tree.insert("", "end", values=(item.get("fichier", "N/A"), f'{item.get("buy_in", 0):.2f}€', f'{item.get("gains", 0):.2f}€', f'{item.get("net", 0):+.2f}€'))

        summary_text = ""
        if analysis_function == analyser_resultats_cash_game:
            total_hands = results.get("total_hands", 0)
            total_mise = results.get("total_mise", 0.0)
            total_gains = results.get("total_gains", 0.0)
            net_result = results.get("resultat_net_total", 0.0)
            total_rake = results.get("total_rake", 0.0)
            vpip_pct = results.get("vpip_pct", 0.0)
            pfr_pct = results.get("pfr_pct", 0.0)
            three_bet_pct = results.get("three_bet_pct", 0.0)
            summary_text = (
                f"Mains: {total_hands} | Total misé: {total_mise:.2f}€ | "
                f"Total gagné: {total_gains:.2f}€ | Rake payé: {total_rake:.2f}€ | "
                f"Résultat Net Global: {net_result:+.2f}€\n"
                f"VPIP: {vpip_pct:.1f}% | PFR: {pfr_pct:.1f}% | 3-bet: {three_bet_pct:.1f}%"
            )
        else:
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

        if analysis_function == analyser_resultats_cash_game and "hand_type_results" in results:
            if 'hand_type_btn' in widgets:
                widgets['hand_type_btn'].config(state='normal')
                widgets['hand_type_btn'].results = results

        if "cumulative_results" in results and results["cumulative_results"]:
            fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
            ax.plot(results["cumulative_results"], marker='o', linestyle='-', markersize=2, color=graph_config.get('color', 'blue'), label="Gains Nets")
            if analysis_function == analyser_resultats_cash_game and "cumulative_non_showdown_results" in results:
                ax.plot(results["cumulative_non_showdown_results"], linestyle='-', color='red', label="Gains sans Showdown")
            ax.axhline(0, color='grey', linewidth=0.8, linestyle='--')
            ax.set_title(graph_config['title'])
            ax.set_xlabel(graph_config['xlabel'])
            ax.set_ylabel("Résultat Net Cumulé (€)")
            ax.grid(True, which='both', linestyle='--', linewidth=0.5)
            ax.legend()
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

def show_hand_type_results_popup(results_dict):
    """
    Affiche la matrice en appelant la fonction réutilisable show_double_entry_table.
    """
    if not results_dict:
        return
    values = results_dict.get("hand_type_results", {}) or {}
    counts = results_dict.get("hand_type_counts", {}) or {}
    root = None
    try:
        root = tk._default_root
    except Exception:
        root = None
    show_double_entry_table(RANKS, values, counts=counts, title="Résultats par main (matrice)", parent=root)

def create_analysis_tab(notebook, tab_name, analysis_function, graph_config):
    """
    Crée un onglet d'analyse complet et générique.
    """
    tab = ttk.Frame(notebook, padding="10")
    notebook.add(tab, text=tab_name)
    tab.columnconfigure(0, weight=1)
    tab.rowconfigure(1, weight=2)
    tab.rowconfigure(2, weight=3)

    controls_frame = ttk.Frame(tab)
    analyze_button = ttk.Button(controls_frame, text=f"Lancer l'analyse {tab_name}")
    user_name_label = None
    user_name_entry = None
    date_start_label = None
    date_start_entry = None
    date_end_label = None
    date_end_entry = None
    position_label = None
    position_checks = {}
    
    if analysis_function == analyser_resultats_cash_game:
        # Frame pour les contrôles de filtre
        filter_frame = ttk.LabelFrame(controls_frame, text="Filtres")
        filter_frame.pack(side=tk.LEFT, padx=(0, 10), fill="y")
        
        # Pseudo
        user_name_label = ttk.Label(filter_frame, text="Votre Pseudo:")
        user_name_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        user_name_entry = ttk.Entry(filter_frame)
        user_name_entry.insert(0, "PogShellCie") # Default value
        user_name_entry.grid(row=0, column=1, padx=5, pady=2)
        
        # Filtres de date
        date_start_label = ttk.Label(filter_frame, text="Date début (YYYY-MM-DD):")
        date_start_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        date_start_entry = ttk.Entry(filter_frame, width=12)
        date_start_entry.grid(row=1, column=1, padx=5, pady=2)
        
        date_end_label = ttk.Label(filter_frame, text="Date fin (YYYY-MM-DD):")
        date_end_label.grid(row=2, column=0, sticky="w", padx=5, pady=2)
        date_end_entry = ttk.Entry(filter_frame, width=12)
        date_end_entry.grid(row=2, column=1, padx=5, pady=2)
        
        # Filtres de position
        position_label = ttk.Label(filter_frame, text="Positions:")
        position_label.grid(row=3, column=0, sticky="nw", padx=5, pady=2)
        
        positions_frame = ttk.Frame(filter_frame)
        positions_frame.grid(row=3, column=1, padx=5, pady=2, sticky="w")
        
        positions = ["BTN", "SB", "BB", "UTG", "CO", "MP", "HJ"]
        for i, pos in enumerate(positions):
            var = tk.BooleanVar(value=True)  # Toutes cochées par défaut
            position_checks[pos] = var
            check = ttk.Checkbutton(positions_frame, text=pos, variable=var)
            check.grid(row=i//4, column=i%4, sticky="w", padx=2)
    elif analysis_function in [analyser_resultats_tournois, analyser_resultats_expresso]:
        # Pour les tournois et expresso, seulement filtres de date
        filter_frame = ttk.LabelFrame(controls_frame, text="Filtres")
        filter_frame.pack(side=tk.LEFT, padx=(0, 10), fill="y")
        
        # Filtres de date
        date_start_label = ttk.Label(filter_frame, text="Date début (YYYY-MM-DD):")
        date_start_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        date_start_entry = ttk.Entry(filter_frame, width=12)
        date_start_entry.grid(row=0, column=1, padx=5, pady=2)
        
        date_end_label = ttk.Label(filter_frame, text="Date fin (YYYY-MM-DD):")
        date_end_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        date_end_entry = ttk.Entry(filter_frame, width=12)
        date_end_entry.grid(row=1, column=1, padx=5, pady=2)
    
    analyze_button.pack(side=tk.LEFT, padx=5)

    results_frame = ttk.LabelFrame(tab, text=f"Résultats détaillés ({tab_name})")
    columns = ('filename', 'buyin', 'winnings', 'net')
    if analysis_function == analyser_resultats_cash_game:
        columns = ('filename', 'buyin', 'winnings', 'net', 'community')
    tree = ttk.Treeview(results_frame, columns=columns, show='headings')
    scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=tree.yview)
    canvas_frame = ttk.LabelFrame(tab, text="Graphique des gains cumulés")
    summary_label = ttk.Label(tab, text="Prêt à analyser.", anchor="w", font=('TkDefaultFont', 9, 'bold'))

    tree.heading('filename', text='Fichier / Session')
    tree.heading('buyin', text='Buy-in')
    tree.heading('winnings', text='Gains')
    tree.heading('net', text='Net')
    tree.column('filename', width=300)
    tree.column('buyin', width=80, anchor='e')
    tree.column('winnings', width=80, anchor='e')
    tree.column('net', width=80, anchor='e')
    if analysis_function == analyser_resultats_cash_game:
        tree.column('community', width=120, anchor='w')
    tree.configure(yscroll=scrollbar.set)

    controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
    analyze_button.pack()
    results_frame.grid(row=1, column=0, sticky="nsew", pady=5)
    results_frame.columnconfigure(0, weight=1)
    results_frame.rowconfigure(0, weight=1)
    tree.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")
    canvas_frame.grid(row=2, column=0, sticky="nsew", pady=5)
    summary_label.grid(row=3, column=0, sticky="ew", pady=(10, 0))

    hand_type_btn = None
    if analysis_function == analyser_resultats_cash_game:
        def open_hand_type_results():
            if hasattr(hand_type_btn, 'results'):
                show_hand_type_results_popup(hand_type_btn.results)
        hand_type_btn = ttk.Button(tab, text="Voir résultats par main", command=open_hand_type_results, state='disabled')
        hand_type_btn.grid(row=4, column=0, sticky="ew", pady=(5, 0))

    widgets = {
        'tree': tree,
        'canvas_frame': canvas_frame,
        'summary_label': summary_label,
        'user_name_entry': user_name_entry,
        'date_start_entry': date_start_entry,
        'date_end_entry': date_end_entry,
        'position_checks': position_checks,
    }
    if hand_type_btn:
        widgets['hand_type_btn'] = hand_type_btn

    analyze_button.config(command=lambda: run_analysis(analysis_function, widgets, graph_config))

    return tab

def create_gui():
    """Creates the main GUI window for the poker EV calculator and other tabs"""
    global root
    global selected_history_directory
    root = tk.Tk()
    root.title("Poker Tools")
    root.geometry("900x800")
    root.protocol("WM_DELETE_WINDOW", root.quit)

    # Demande le dossier d'historique une seule fois au lancement
    selected_history_directory = filedialog.askdirectory(title="Sélectionnez le dossier d'historique à analyser")
    if not selected_history_directory:
        tk.messagebox.showerror("Erreur", "Aucun dossier sélectionné. L'application va se fermer.")
        root.destroy()
        sys.exit(0)

    notebook = ttk.Notebook(root)
    notebook.pack(pady=10, padx=10, fill="both", expand=True)

    ev_tab = ttk.Frame(notebook, padding="10")
    notebook.add(ev_tab, text="Calculateur d'EV")

    scenario_frame = ttk.LabelFrame(ev_tab, text="Scenario Details")
    scenario_frame.grid(row=0, column=0, padx=15, pady=10, sticky="ew")
    ev_tab.columnconfigure(0, weight=1)
    scenario_frame.columnconfigure(1, weight=1)
    scenario_frame.columnconfigure(3, weight=1)

    ttk.Label(scenario_frame, text="Player Stacks (comma-separated):").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    stacks_entry = ttk.Entry(scenario_frame, width=40)
    stacks_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
    stacks_entry.insert(0, "1000, 1500")

    ttk.Label(scenario_frame, text="Your Position:").grid(row=0, column=2, sticky="w", padx=(15, 5))
    position_options = ['SB', 'BB']
    position_combobox = ttk.Combobox(scenario_frame, values=position_options, state="readonly", width=10)
    position_combobox.grid(row=0, column=3, sticky="ew", padx=5)
    position_combobox.set('SB')

    blind_ante_frame = ttk.Frame(scenario_frame)
    blind_ante_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
    blind_ante_frame.columnconfigure(1, weight=1)
    blind_ante_frame.columnconfigure(3, weight=1)

    ttk.Label(blind_ante_frame, text="Small Blind:").grid(row=0, column=0, sticky="w", padx=(0, 5))
    sb_entry = ttk.Entry(blind_ante_frame, width=8)
    sb_entry.grid(row=0, column=1, sticky="ew", padx=5)
    sb_entry.insert(0, "10")

    ttk.Label(blind_ante_frame, text="Big Blind:").grid(row=0, column=2, sticky="w", padx=5)
    bb_entry = ttk.Entry(blind_ante_frame, width=8)
    bb_entry.grid(row=0, column=3, sticky="ew", padx=5)
    bb_entry.insert(0, "20")

    ttk.Label(blind_ante_frame, text="Ante:").grid(row=0, column=4, sticky="w", padx=5)
    ante_entry = ttk.Entry(blind_ante_frame, width=8)
    ante_entry.grid(row=0, column=5, sticky="ew", padx=(5, 0))
    ante_entry.insert(0, "0")

    hand_frame = ttk.LabelFrame(ev_tab, text="Player and Hand Details")
    hand_frame.grid(row=1, column=0, padx=15, pady=10, sticky="ew")
    hand_frame.columnconfigure(1, weight=1)

    ttk.Label(hand_frame, text="Your Hole Cards (e.g., AhKd):").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    hole_cards_entry = ttk.Entry(hand_frame, width=20)
    hole_cards_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
    hole_cards_entry.insert(0, "AsKd")

    ttk.Label(hand_frame, text="Community Cards (e.g., AsKd7c or leave empty):").grid(row=1, column=0, sticky="w", padx=10, pady=5)
    community_cards_entry = ttk.Entry(hand_frame, width=20)
    community_cards_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
    community_cards_entry.insert(0, "Th9d2c")

    action_frame = ttk.LabelFrame(ev_tab, text="Opponent and Action Details")
    action_frame.grid(row=2, column=0, padx=15, pady=10, sticky="ew")
    action_frame.columnconfigure(1, weight=1)

    ttk.Label(action_frame, text="Opponent Range (e.g., JJ+, AKs, AKo):").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    opponent_range_entry = ttk.Entry(action_frame, width=40)
    opponent_range_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
    opponent_range_entry.insert(0, "JJ+, AKs, AKo")

    action_bet_frame = ttk.Frame(action_frame)
    action_bet_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
    action_bet_frame.columnconfigure(1, weight=1)
    action_bet_frame.columnconfigure(3, weight=1)

    ttk.Label(action_bet_frame, text="Your Action:").grid(row=0, column=0, sticky="w", padx=(0, 5))
    action_options = ['Fold', 'Call', 'Raise']
    action_combobox = ttk.Combobox(action_bet_frame, values=action_options, state="readonly", width=12)
    action_combobox.grid(row=0, column=1, sticky="ew", padx=5)
    action_combobox.set('Call')

    ttk.Label(action_bet_frame, text="Bet/Call Size:").grid(row=0, column=2, sticky="w", padx=5)
    bet_size_entry = ttk.Entry(action_bet_frame, width=8)
    bet_size_entry.grid(row=0, column=3, sticky="ew", padx=(5, 0))
    bet_size_entry.insert(0, "50")

    output_frame = ttk.LabelFrame(ev_tab, text="Result")
    output_frame.grid(row=3, column=0, padx=15, pady=10, sticky="ew")
    output_frame.columnconfigure(1, weight=1)

    ttk.Label(output_frame, text="Calculated EV:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    ev_result_label = ttk.Label(output_frame, text="Enter details and click Calculate", font=('TkDefaultFont', 12, 'bold'), anchor='w')
    ev_result_label.grid(row=0, column=1, sticky="ew", padx=10, pady=5)

    buttons_frame = ttk.Frame(ev_tab)
    buttons_frame.grid(row=4, column=0, padx=15, pady=15)
    buttons_frame.columnconfigure(0, weight=1)
    buttons_frame.columnconfigure(1, weight=1)

    calculate_button = ttk.Button(buttons_frame, text="Calculate EV for Given Size")
    calculate_button.grid(row=0, column=0, padx=5, sticky="ew")

    optimize_button = ttk.Button(buttons_frame, text="Find Optimal Bet")
    optimize_button.grid(row=0, column=1, padx=5, sticky="ew")

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

    calculate_button.config(command=lambda: calculate_ev_from_gui(gui_elements))
    optimize_button.config(command=lambda: find_optimal_bet_from_gui(gui_elements))

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
        scenario, player_name, opponent_range_string, _, _, _ = setup_scenario_from_gui(gui_elements)
        bet_size = float(gui_elements['bet_size_entry'].get() or '0')
        player_action = gui_elements['action_combobox'].get().strip().lower()
        if player_action not in ('fold', 'call', 'raise'):
            raise ValueError("Invalid action.")
        if player_action == 'raise' and bet_size <= 0:
            raise ValueError("Raise amount must be positive.")

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

if __name__ == "__main__":
    main_window = create_gui()
    try:
        main_window.mainloop()
    finally:
        sys.exit(0)
    ev_result_label.grid(row=0, column=1, sticky="ew", padx=10, pady=5) # Sticky ew
