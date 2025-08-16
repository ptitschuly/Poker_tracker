# filepath: c:\Users\schut\Documents\Projet_Winamax\Tracker_poker\recapitulatif_cash_game.py
import os
import re
from poker_logic import RANKS

# --- Constants for Hand History Parsing ---
MARKER_DEALT_TO = "Dealt to "
MARKER_FLOP = "*** FLOP ***"
MARKER_TURN = "*** TURN ***"
MARKER_RIVER = "*** RIVER ***"
MARKER_SHOWDOWN = "*** SHOW DOWN ***"
MARKER_SUMMARY = "*** SUMMARY ***"

# --- Pre-compiled Regular Expressions for Efficiency ---
RE_TABLE = re.compile(r"Table: '(.+?)'")
RE_HAND = re.compile(r'\[(.+?)\]')
RE_BOARD = re.compile(r'\[(.*?)\]')
RE_AMOUNT = re.compile(r'(\d+\.?\d*)€')
RE_RAKE = re.compile(r'Rake (\d+\.?\d*)€')

def normalize_hand(hand_str):
	"""
	Convertit une main 'AsKd' -> 'AKs' ou 'AKo' / '77' pour paire.
	Utilise l'ordre canonique CANONICAL_RANKS pour décider de la carte la plus forte.
	"""
	if not isinstance(hand_str, str) or len(hand_str) != 4:
		return hand_str
	try:
		r1, s1, r2, s2 = hand_str[0], hand_str[1], hand_str[2], hand_str[3]
	except Exception:
		return hand_str

	# paire
	if r1 == r2:
		return f"{r1}{r1}"

	# mettre la carte la plus forte en premier selon CANONICAL_RANKS
	try:
		i1 = RANKS[::-1].index(r1)
		i2 = RANKS[::-1].index(r2)
	except ValueError:
		# fallback : garder l'ordre d'origine si rang inconnu
		i1, i2 = 0, 1

	if i1 > i2:
		# r2 est plus fort, on swap
		r1, s1, r2, s2 = r2, s2, r1, s1

	# suited / offsuit
	if s1 == s2:
		return f"{r1}{r2}s"
	else:
		return f"{r1}{r2}o"

def process_hand(hand_text, user_name):
    """
    Traite une seule main de poker et retourne un dictionnaire avec les détails de la main,
    y compris la main de départ du joueur et les cartes communautaires.
    """
    hand_lines = hand_text.strip().split('\n')
    bet_amount, won_amount = 0.0, 0.0
    is_summary = False
    hero_hand = "N/A"
    table_name = "N/A"
    community_cards = "" # Initialisé à une chaîne vide
    is_showdown = MARKER_SHOWDOWN in hand_text
    rake = 0.0
    normalized_hand = None
    position = None  # <-- Ajout pour la position

    # --- AJOUT DES STATISTIQUES ---
    vpip = False
    pfr = False
    three_bet = False
    preflop_actions = []
    preflop = True

    # Extraire le nom de la table
    if hand_lines:
        match_table = RE_TABLE.search(hand_lines[0])
        if match_table:
            table_name = match_table.group(1)

    for line in hand_lines:
        # Extraire la main du joueur
        if line.startswith(f"{MARKER_DEALT_TO}{user_name}"):
            match_hand = RE_HAND.search(line)
            if match_hand:
                hero_hand = match_hand.group(1).replace(" ", "")
                normalized_hand = normalize_hand(hero_hand)
                # --- Détection de la position ---
                # Exemple Winamax : "Dealt to PogShellCie [As Kd] (BTN)"
                pos_match = re.search(r"\((\w+)\)", line)
                if pos_match:
                    position = pos_match.group(1)
        
        # Extraire les cartes communautaires (flop, turn, river)
        if MARKER_FLOP in line:
            match_board = RE_BOARD.search(line)
            if match_board:
                community_cards = match_board.group(1).replace(" ", "")
        elif MARKER_TURN in line or MARKER_RIVER in line:
            match_board = RE_BOARD.search(line)
            if match_board:
                # La ligne contient toutes les cartes jusqu'à ce stade
                community_cards = match_board.group(1).replace(" ", "")

        if MARKER_SUMMARY in line:
            is_summary = True
        
        if is_summary and "Rake" in line:
            match_rake = RE_RAKE.search(line)
            if match_rake:
                rake = float(match_rake.group(1))

        if user_name in line:
            if not is_summary and ("bets" in line or "raises" in line or "calls" in line or "posts" in line):
                try:
                    amounts = RE_AMOUNT.findall(line)
                    if amounts:
                        bet_amount += float(amounts[-1])
                except (ValueError, IndexError):
                    pass

            if is_summary and "won" in line:
                try:
                    match = RE_AMOUNT.search(line)
                    if match:
                        won_amount = float(match.group(1))
                except (ValueError, IndexError):
                    pass
                    
        # Detect preflop actions for VPIP/PFR/3bet
        if preflop:
            if line.startswith('*** FLOP ***'):
                preflop = False
            elif user_name in line:
                # Exclude posts (blinds/antes)
                if any(word in line for word in ['calls', 'raises', 'bets']):
                    if 'posts' not in line:
                        vpip = True
                if 'raises' in line and 'posts' not in line:
                    pfr = True
                    preflop_actions.append('raise')
                elif 'calls' in line and 'posts' not in line:
                    preflop_actions.append('call')
                elif 'bets' in line and 'posts' not in line:
                    preflop_actions.append('bet')

    # Detect 3-bet: If hero raises and there was already a raise before
    # (i.e., hero's first preflop action is a raise and there was a previous raise)
    # We'll check if there is more than one 'raise' in preflop actions
    if preflop_actions.count('raise') >= 1:
        # If hero's first preflop action is a raise and there was a previous raise
        # (i.e., hero's raise is not the first raise in the hand)
        # We'll check if there is a raise before hero's raise
        # For simplicity, if hero's first action is a raise and it's not the first raise in the hand
        # We'll look for 'raises' in preflop lines before hero's first raise
        hero_acted = False
        for line in hand_lines:
            if line.startswith('*** FLOP ***'):
                break
            if user_name in line and 'raises' in line and 'posts' not in line:
                hero_acted = True
                break
            if 'raises' in line and user_name not in line and 'posts' not in line and not hero_acted:
                three_bet = True
                break

    # --- FIN AJOUT STATISTIQUES ---
    net = won_amount - bet_amount
    net_non_showdown = 0
    if not is_showdown:
        net_non_showdown = net

    # Only count rake if the user won the hand
    if won_amount == 0:
        rake = 0.0

    return {
        "hand": hero_hand,
        "table": table_name,
        "bet_amount": bet_amount,
        "gains": won_amount,
        "net": net,
        "community_cards": community_cards if community_cards else "N/A",
        "net_non_showdown": net_non_showdown,
        "rake": rake,
        "vpip": vpip,
        "pfr": pfr,
        "three_bet": three_bet,
        "normalized_hand": normalized_hand,
        "position": position,  # <-- Ajouté ici
    }

def analyser_resultats_cash_game(repertoire, user_name):
    """
    Analyse les fichiers de cash game et retourne les détails de chaque main.
    """
    if not os.path.isdir(repertoire):
        raise FileNotFoundError(f"Le répertoire '{repertoire}' n'existe pas.")

    net_result, total_gains, total_mise, total_rake = 0.0, 0.0, 0.0, 0.0
    net_non_showdown_cumulative = 0.0
    hand_results_cumulative = []
    non_showdown_results_cumulative = []
    all_hands_details = []
    
    excluded_keywords = ["Freeroll", "Expresso", "Kill The Fish", "summary"]
    
    all_items = os.listdir(repertoire)
    hand_history_files = [
        os.path.join(repertoire, item) 
        for item in sorted(all_items)
        if item.endswith('.txt') and not any(keyword in item for keyword in excluded_keywords)
    ]

    vpip_count = 0
    pfr_count = 0
    three_bet_count = 0
    total_hands = 0
    hand_type_results = {}
    hand_type_counts = {}

    for file_path in hand_history_files:
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()

        hand_list = file_content.split('Winamax Poker -')
        
        for hand_text in hand_list:
            if not hand_text.strip() or "HandId" not in hand_text:
                continue
            
            full_hand_text = 'Winamax Poker -' + hand_text
            hand_details = process_hand(full_hand_text, user_name)
            
            all_hands_details.append(hand_details)
            
            net_result += hand_details["net"]
            hand_results_cumulative.append(net_result)

            net_non_showdown_cumulative += hand_details["net_non_showdown"]
            non_showdown_results_cumulative.append(net_non_showdown_cumulative)

            total_mise += hand_details["bet_amount"]
            total_gains += hand_details["gains"]
            total_rake += hand_details["rake"]
            total_hands += 1
            if hand_details.get("vpip"):
                vpip_count += 1
            if hand_details.get("pfr"):
                pfr_count += 1
            if hand_details.get("three_bet"):
                three_bet_count += 1
            nh = hand_details.get("normalized_hand")
            if nh:
                hand_type_results.setdefault(nh, 0.0)
                hand_type_results[nh] += hand_details["net"]
                hand_type_counts.setdefault(nh, 0)
                hand_type_counts[nh] += 1

    vpip_pct = (vpip_count / total_hands * 100) if total_hands else 0
    pfr_pct = (pfr_count / total_hands * 100) if total_hands else 0
    three_bet_pct = (three_bet_count / total_hands * 100) if total_hands else 0

    # ensure counts dict exists
    if 'hand_type_counts' not in locals():
        hand_type_counts = {}

    return {
        "details": all_hands_details,
        "resultat_net_total": net_result,
        "total_hands": len(all_hands_details),
        "cumulative_results": hand_results_cumulative,
        "cumulative_non_showdown_results": non_showdown_results_cumulative,
        "total_mise": total_mise,
        "total_gains": total_gains,
        "total_rake": total_rake,
        "vpip_pct": vpip_pct,
        "pfr_pct": pfr_pct,
        "three_bet_pct": three_bet_pct,
        "hand_type_results": hand_type_results,
        "hand_type_counts": hand_type_counts,
    }

if __name__ == '__main__':
    chemin = input("Entrez le chemin du dossier d'historique : ")
    pseudo = input("Entrez votre pseudo Winamax : ")

    try:
        resultats = analyser_resultats_cash_game(chemin, pseudo)
        print("\n--- RÉSUMÉ GLOBAL CASH GAME ---")        
        print(f"Mains jouées : {resultats['total_hands']}")
        print(f"Total des mises : {resultats['total_mise']:.2f}€")
        print(f"Total des gains : {resultats['total_gains']:.2f}€")
        print(f"Résultat Net Global : {resultats['resultat_net_total']:+.2f}€")
    except FileNotFoundError as e:
        print(e)