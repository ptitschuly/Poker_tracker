# filepath: c:\Users\schut\Documents\Projet_Winamax\Tracker_poker\recapitulatif_cash_game.py
import os
import re

def process_hand(hand_text, user_name):
    """
    Traite une seule main de poker et retourne un dictionnaire avec les détails de la main,
    y compris la main de départ du joueur.
    """
    hand_lines = hand_text.strip().split('\n')
    bet_amount = 0.0
    won_amount = 0.0
    is_summary = False
    hero_hand = "N/A" # Remplacera hand_id
    table_name = "N/A"

    # Extraire le nom de la table
    if hand_lines:
        match_table = re.search(r"Table: '(.+?)'", hand_lines[0])
        if match_table:
            table_name = match_table.group(1)

    for line in hand_lines:
        # --- NOUVELLE LOGIQUE POUR TROUVER LA MAIN ---
        if line.startswith(f"Dealt to {user_name}"):
            match_hand = re.search(r'\[(.+?)\]', line)
            if match_hand:
                # Nettoie la main (ex: "7s 2h" -> "7s2h")
                hero_hand = match_hand.group(1).replace(" ", "")
        # --- FIN DE LA NOUVELLE LOGIQUE ---

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
        "hero_hand": hero_hand, # Clé modifiée
        "table": table_name,
        "net": won_amount - bet_amount
    }

def analyser_resultats_cash_game(repertoire, user_name):
    """
    Analyse les fichiers de cash game et retourne les détails de chaque main.
    """
    if not os.path.isdir(repertoire):
        raise FileNotFoundError(f"Le répertoire '{repertoire}' n'existe pas.")

    net_result = 0.0
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
            
    return {
        "details": all_hands_details,
        "resultat_net_total": net_result,
        "total_hands": len(all_hands_details),
        "cumulative_results": hand_results_cumulative
    }

if __name__ == '__main__':
    chemin = input("Entrez le chemin du dossier d'historique : ")
    pseudo = input("Entrez votre pseudo Winamax : ")
    try:
        resultats = analyser_resultats_cash_game(chemin, pseudo)
        print("\n--- RÉSUMÉ GLOBAL CASH GAME ---")
        print(f"Fichiers analysés : {resultats['files_analyzed']}")
        print(f"Mains jouées : {resultats['total_hands']}")
        print(f"Résultat Net Global : {resultats['net_result']:+.2f}€")
    except FileNotFoundError as e:
        print(e)