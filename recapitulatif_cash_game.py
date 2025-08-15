# filepath: c:\Users\schut\Documents\Projet_Winamax\Tracker_poker\recapitulatif_cash_game.py
import os
import re

def process_hand(hand_text, user_name):
    """
    Traite une seule main de poker et retourne un dictionnaire avec les détails de la main,
    y compris la main de départ du joueur et les cartes communautaires.
    """
    hand_lines = hand_text.strip().split('\n')
    bet_amount = 0.0
    won_amount = 0.0
    is_summary = False
    hero_hand = "N/A"
    table_name = "N/A"
    community_cards = "" # Initialisé à une chaîne vide

    # Extraire le nom de la table
    if hand_lines:
        match_table = re.search(r"Table: '(.+?)'", hand_lines[0])
        if match_table:
            table_name = match_table.group(1)

    for line in hand_lines:
        # Extraire la main du joueur
        if line.startswith(f"Dealt to {user_name}"):
            match_hand = re.search(r'\[(.+?)\]', line)
            if match_hand:
                hero_hand = match_hand.group(1).replace(" ", "")
        
        # Extraire les cartes communautaires (flop, turn, river)
        if "*** FLOP ***" in line:
            match_board = re.search(r'\[(.*?)\]', line)
            if match_board:
                community_cards = match_board.group(1).replace(" ", "")
        elif "*** TURN ***" in line or "*** RIVER ***" in line:
            match_board = re.search(r'\[(.*?)\]', line)
            if match_board:
                # La ligne contient toutes les cartes jusqu'à ce stade
                community_cards = match_board.group(1).replace(" ", "")

        if "*** SUMMARY ***" in line:
            is_summary = True
        
        if user_name in line:
            if not is_summary and ("bets" in line or "raises" in line or "calls" in line or "posts" in line):
                try:
                    amounts = re.findall(r'(\d+\.?\d*)€', line)
                    if amounts:
                        bet_amount += float(amounts[-1])
                except (ValueError, IndexError):
                    pass

            if is_summary and "won" in line:
                try:
                    match = re.search(r'(\d+\.?\d*)€', line)
                    if match:
                        won_amount = float(match.group(1))
                except (ValueError, IndexError):
                    pass
                    
    return {
        "hand": hero_hand, # Renommé pour la cohérence
        "table": table_name,
        "bet_amount": bet_amount,
        "gains": won_amount,
        "net": won_amount - bet_amount,
        "community_cards": community_cards if community_cards else "N/A"
    }

def analyser_resultats_cash_game(repertoire, user_name):
    """
    Analyse les fichiers de cash game et retourne les détails de chaque main.
    """
    if not os.path.isdir(repertoire):
        raise FileNotFoundError(f"Le répertoire '{repertoire}' n'existe pas.")

    net_result, total_gains, total_mise = 0.0, 0.0, 0.0
    hand_results_cumulative = []
    all_hands_details = []
    
    excluded_keywords = ["Freeroll", "Expresso", "Kill The Fish", "summary"]
    
    all_items = os.listdir(repertoire)
    hand_history_files = [
        os.path.join(repertoire, item) 
        for item in sorted(all_items)
        if item.endswith('.txt') and not any(keyword in item for keyword in excluded_keywords)
    ]

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
            total_mise += hand_details["bet_amount"]
            total_gains += hand_details["gains"]
    return {
        "details": all_hands_details,
        "resultat_net_total": net_result,
        "total_hands": len(all_hands_details),
        "cumulative_results": hand_results_cumulative,
        "total_mise": total_mise,
        "total_gains": total_gains
    }

if __name__ == '__main__':
    chemin = input("Entrez le chemin du dossier d'historique : ")
    pseudo = input("Entrez votre pseudo Winamax : ")
    #resultats = analyser_resultats_cash_game(chemin, pseudo)
    #print(resultats)
    
    try:
        resultats = analyser_resultats_cash_game(chemin, pseudo)
        print("\n--- RÉSUMÉ GLOBAL CASH GAME ---")        
        print(f"Mains jouées : {resultats['total_hands']}")
        print(f"Total des mises : {resultats['total_mise']:.2f}€")
        print(f"Total des gains : {resultats['total_gains']:.2f}€")
        print(f"Résultat Net Global : {resultats['resultat_net_total']:+.2f}€")
    except FileNotFoundError as e:
        print(e)
