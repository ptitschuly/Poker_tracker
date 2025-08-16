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
RE_AMOUNT = re.compile(r'(\d+\.?\d*)€?')  # Support both with and without €
RE_RAKE = re.compile(r'Rake (\d+\.?\d*)€?')
RE_BUTTON = re.compile(r'Seat #(\d+) is the button')
RE_SEAT = re.compile(r'Seat (\d+): ([^(]+) \(')
RE_DATE = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')
RE_WON = re.compile(r'(\w+) won \((\d+\.?\d*)\)')  # Parse "Player won (amount)"
RE_COLLECTED = re.compile(r'(\w+) collected (\d+\.?\d*) from pot')  # Parse "Player collected amount from pot"


def get_hero_position(hand_text, user_name):
    """
    Détermine la position du héros relative au bouton.
    Retourne la position (BTN, SB, BB, UTG, CO, etc.) ou "Unknown" si non trouvée.
    """
    lines = hand_text.strip().split('\n')
    button_seat = None
    hero_seat = None
    seat_count = 0
    
    # Trouver le siège du bouton et le siège du héros
    for line in lines:
        button_match = RE_BUTTON.search(line)
        if button_match:
            button_seat = int(button_match.group(1))
        
        seat_match = RE_SEAT.search(line)
        if seat_match:
            seat_num = int(seat_match.group(1))
            player_name = seat_match.group(2).strip()
            seat_count = max(seat_count, seat_num)
            
            if player_name == user_name:
                hero_seat = seat_num
    
    if button_seat is None or hero_seat is None:
        return "Unknown"
    
    # Calculer la position relative
    # Distance du héros par rapport au bouton (dans le sens horaire)
    position_offset = (hero_seat - button_seat) % seat_count
    
    # Déterminer la position selon le nombre de sièges
    if seat_count == 2:
        positions = ["BTN", "BB"]  # En heads-up, BTN est aussi SB
    elif seat_count == 3:
        positions = ["BTN", "SB", "BB"]
    elif seat_count == 4:
        positions = ["BTN", "SB", "BB", "CO"]
    elif seat_count == 5:
        positions = ["BTN", "SB", "BB", "UTG", "CO"]
    elif seat_count == 6:
        positions = ["BTN", "SB", "BB", "UTG", "MP", "CO"]
    elif seat_count == 9:
        positions = ["BTN", "SB", "BB", "UTG", "UTG+1", "MP", "MP+1", "CO", "HJ"]
    else:
        return f"Seat{hero_seat}"  # Fallback pour tables non standards
    
    return positions[position_offset] if position_offset < len(positions) else "Unknown"

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
    y compris la main de départ du joueur, les cartes communautaires, la position et la date.
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
    # Nouveau: position et date
    position = get_hero_position(hand_text, user_name)
    date_str = None
    
    # Extraire la date depuis la première ligne
    if hand_lines:
        date_match = RE_DATE.search(hand_lines[0])
        if date_match:
            date_str = date_match.group(1)

    # --- AJOUT DES STATISTIQUES ---
    vpip = False
    pfr = False
    three_bet = False
    preflop_actions = []
    preflop = True

    # Extraire le nom de la table
    for line in hand_lines:
        match_table = RE_TABLE.search(line)
        if match_table:
            table_name = match_table.group(1)
            break

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

        # Check for winnings in different formats
        if user_name in line:
            # Check for "collected" format
            collected_match = RE_COLLECTED.search(line)
            if collected_match and collected_match.group(1) == user_name:
                try:
                    won_amount += float(collected_match.group(2))
                except (ValueError, IndexError):
                    pass
            
            # Bet amounts (not in summary)
            if not is_summary and ("bets" in line or "raises" in line or "calls" in line or "posts" in line):
                try:
                    amounts = RE_AMOUNT.findall(line)
                    if amounts:
                        bet_amount += float(amounts[-1])
                except (ValueError, IndexError):
                    pass

            # Summary winnings
            if is_summary and "won" in line:
                try:
                    match = RE_AMOUNT.search(line)
                    if match:
                        won_amount += float(match.group(1))
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
        "position": position,
        "date": date_str,

    }

def analyser_resultats_cash_game(repertoire, user_name, date_filter=None, position_filter=None):
    """
    Analyse les fichiers de cash game et retourne les détails de chaque main.
    
    Args:
        repertoire: Chemin vers le répertoire contenant les fichiers de historique
        user_name: Nom du joueur à analyser
        date_filter: Tuple (date_debut, date_fin) au format 'YYYY-MM-DD' ou None pour pas de filtre
        position_filter: Liste des positions à inclure (ex: ['BTN', 'CO']) ou None pour toutes
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
            
            # Application des filtres
            if date_filter:
                hand_date = hand_details.get("date")
                if hand_date:
                    # Extraire seulement la date (YYYY-MM-DD) de la chaîne complète
                    hand_date_only = hand_date.split(' ')[0]
                    if date_filter[0] and hand_date_only < date_filter[0]:
                        continue
                    if date_filter[1] and hand_date_only > date_filter[1]:
                        continue
                else:
                    # Si pas de date trouvée et qu'un filtre de date est appliqué, ignorer
                    continue
            
            if position_filter:
                hand_position = hand_details.get("position")
                if hand_position not in position_filter:
                    continue
            
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
    
    # Demander les filtres optionnels
    print("\n--- FILTRES OPTIONNELS ---")
    date_debut = input("Date de début (YYYY-MM-DD, optionnel) : ").strip()
    date_fin = input("Date de fin (YYYY-MM-DD, optionnel) : ").strip()
    
    print("Positions disponibles : BTN, SB, BB, UTG, CO, MP, HJ")
    positions_input = input("Positions à inclure (séparées par des virgules, optionnel) : ").strip()
    
    # Construire les filtres
    date_filter = None
    if date_debut or date_fin:
        date_filter = (date_debut or None, date_fin or None)
    
    position_filter = None
    if positions_input:
        positions = [pos.strip().upper() for pos in positions_input.split(',') if pos.strip()]
        if positions:
            position_filter = positions

    try:
        resultats = analyser_resultats_cash_game(chemin, pseudo, date_filter, position_filter)
        print("\n--- RÉSUMÉ GLOBAL CASH GAME ---")
        if date_filter:
            print(f"Filtres de date : {date_filter[0] or 'début'} - {date_filter[1] or 'fin'}")
        if position_filter:
            print(f"Positions filtrées : {', '.join(position_filter)}")
        print(f"Mains jouées : {resultats['total_hands']}")
        print(f"Total des mises : {resultats['total_mise']:.2f}€")
        print(f"Total des gains : {resultats['total_gains']:.2f}€")
        print(f"Résultat Net Global : {resultats['resultat_net_total']:+.2f}€")
        print(f"VPIP : {resultats['vpip_pct']:.1f}%")
        print(f"PFR : {resultats['pfr_pct']:.1f}%")
        print(f"3-bet : {resultats['three_bet_pct']:.1f}%")
    except FileNotFoundError as e:
        print(e)