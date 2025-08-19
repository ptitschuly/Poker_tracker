# filepath: c:\Users\schut\Documents\Projet_Winamax\Tracker_poker\recapitulatif_expresso.py
import os
import re

# Regex pour extraire la date des noms de fichiers
RE_DATE_FROM_FILENAME = re.compile(r'(\d{4}-\d{2}-\d{2})')

def extraire_details_expresso(fichier_path):
    """
    Extrait les détails complets d'un expresso depuis un fichier de résumé,
    incluant les mains jouées.
    
    Args:
        fichier_path: Chemin vers le fichier de résumé d'expresso
        
    Returns:
        dict: Détails de l'expresso avec buy-in, gains, mains, etc.
    """
    details = {
        "fichier": os.path.basename(fichier_path),
        "buy_in": 0.0,
        "gains": 0.0,
        "net": 0.0,
        "mains": [],
        "duree": "",
        "position_finale": "",
        "nombre_mains": 0
    }
    
    try:
        with open(fichier_path, 'r', encoding='utf-8') as f:
            contenu = f.read()
        
        # Extraire buy-in et gains
        buy_in_fichier = 0.0
        gains_fichier = 0.0
        
        for ligne in contenu.split('\n'):
            ligne = ligne.strip()
            if ligne.lower().startswith("buy-in"):
                montants = re.findall(r'(\d+\.\d{2})€', ligne)
                buy_in_fichier = sum(float(m) for m in montants)
            elif ligne.startswith("You won"):
                montants = re.findall(r'(\d+\.\d{2})€', ligne)
                gains_fichier = sum(float(m) for m in montants)
            elif ligne.startswith("Duration:"):
                details["duree"] = ligne.replace("Duration:", "").strip()
            elif ligne.startswith("Final Position:"):
                details["position_finale"] = ligne.replace("Final Position:", "").strip()
        
        details["buy_in"] = buy_in_fichier
        details["gains"] = gains_fichier
        details["net"] = gains_fichier - buy_in_fichier
        
        # Extraire les mains (même logique que pour les tournois)
        mains = extraire_mains_expresso(contenu)
        details["mains"] = mains
        details["nombre_mains"] = len(mains)
        
    except Exception as e:
        print(f"Erreur lors de l'extraction des détails de {fichier_path}: {e}")
    
    return details

def extraire_mains_expresso(contenu_texte):
    """
    Extrait les détails des mains d'un expresso.
    
    Args:
        contenu_texte: Contenu du fichier d'expresso
        
    Returns:
        list: Liste des mains avec leurs détails
    """
    mains = []
    
    # Diviser par "*** HAND" ou début de main
    parties = re.split(r'(?=Winamax Poker.*HandId:)', contenu_texte)
    
    for i, partie in enumerate(parties):
        if not partie.strip() or "HandId:" not in partie:
            continue
            
        main_details = {
            "numero": i,
            "hand_id": "",
            "niveau": "",
            "cartes_hero": "",
            "board": "",
            "action_hero": "",
            "resultat": 0.0,
            "pot_size": 0.0,
            "position": ""
        }
        
        # Extraire l'ID de la main
        hand_id_match = re.search(r'HandId: #([^-\s]+)', partie)
        if hand_id_match:
            main_details["hand_id"] = hand_id_match.group(1)
        
        # Extraire le niveau
        level_match = re.search(r'level: (\d+)', partie)
        if level_match:
            main_details["niveau"] = level_match.group(1)
        
        # Extraire les cartes du héros
        cartes_match = re.search(r'Hero: deals \[([^\]]+)\]', partie)
        if not cartes_match:
            cartes_match = re.search(r'Hero: shows \[([^\]]+)\]', partie)
        if cartes_match:
            main_details["cartes_hero"] = cartes_match.group(1)
        
        # Extraire le board
        flop_match = re.search(r'\*\*\* FLOP \*\*\* \[([^\]]+)\]', partie)
        turn_match = re.search(r'\*\*\* TURN \*\*\* \[([^\]]+)\]\[([^\]]+)\]', partie)
        river_match = re.search(r'\*\*\* RIVER \*\*\* \[([^\]]+)\]\[([^\]]+)\]', partie)
        
        board_cards = []
        if flop_match:
            board_cards.extend(flop_match.group(1).split(' '))
        if turn_match:
            board_cards.append(turn_match.group(2))
        if river_match:
            board_cards.append(river_match.group(2))
        
        main_details["board"] = " ".join(board_cards)
        
        # Extraire le résultat (pot gagné)
        collected_match = re.search(r'Hero collected (\d+(?:\.\d{2})?) from pot', partie)
        if collected_match:
            main_details["resultat"] = float(collected_match.group(1))
        
        wins_match = re.search(r'Hero wins (\d+(?:\.\d{2})?) with', partie)
        if wins_match:
            main_details["resultat"] = float(wins_match.group(1))
        
        # Déterminer l'action principale du héros
        if "fold" in partie and "Hero: folds" in partie:
            main_details["action_hero"] = "Fold"
        elif "calls" in partie and "Hero: calls" in partie:
            main_details["action_hero"] = "Call"
        elif "raises" in partie and "Hero: raises" in partie:
            main_details["action_hero"] = "Raise"
        elif "bets" in partie and "Hero: bets" in partie:
            main_details["action_hero"] = "Bet"
        elif "checks" in partie and "Hero: checks" in partie:
            main_details["action_hero"] = "Check"
        
        mains.append(main_details)
    
    return mains


def analyser_resultats_expresso(repertoire, date_filter=None):
    """
    Analyse les fichiers de résumé Expresso et retourne les données structurées,
    y compris les résultats cumulés pour le graphique.
    
    Args:
        repertoire: Chemin vers le répertoire contenant les fichiers
        date_filter: Tuple (date_debut, date_fin) au format 'YYYY-MM-DD' ou None pour pas de filtre
    """
    if not os.path.isdir(repertoire):
        raise FileNotFoundError(f"Le répertoire '{repertoire}' n'existe pas.")

    donnees_expressos = []
    total_buy_ins = 0.0
    total_gains = 0.0

    # Variables pour le graphique
    gains_cumules = []
    resultat_net_courant = 0.0

    fichiers_a_traiter = [f for f in os.listdir(repertoire) if f.endswith("summary.txt") and "Expresso" in f]

    for nom_fichier in sorted(fichiers_a_traiter):
        # Extraction de la date depuis le nom du fichier
        date_match = RE_DATE_FROM_FILENAME.search(nom_fichier)
        file_date = None
        if date_match:
            file_date = date_match.group(1)
        
        # Application du filtre de date
        if date_filter and file_date:
            if date_filter[0] and file_date < date_filter[0]:
                continue
            if date_filter[1] and file_date > date_filter[1]:
                continue
        elif date_filter and not file_date:
            # Si un filtre de date est demandé mais pas de date trouvée, ignorer
            continue
        
        chemin_complet = os.path.join(repertoire, nom_fichier)
        buy_in_fichier = 0.0
        gains_fichier = 0.0
        with open(chemin_complet, 'r', encoding='utf-8') as f:
            contenu_texte = f.read()
            for ligne in contenu_texte.split('\n'):
                l = ligne.strip()
                if l.lower().startswith("buy-in"):
                    montants = amount_regex.findall(l)
                    if montants:
                        buy_in_fichier = sum(float(m.replace(',', '.')) for m in montants)
                    else:
                        # ligne buy-in présente mais sans montant explicite -> considérer 0.0
                        buy_in_fichier = 0.0
                elif l.startswith("You won"):
                    montants = amount_regex.findall(l)
                    if montants:
                        gains_fichier = sum(float(m.replace(',', '.')) for m in montants)
                    else:
                        gains_fichier = 0.0
        
        if buy_in_fichier > 0:
            resultat_net = gains_fichier - buy_in_fichier
            expresso_data = {
                "fichier": nom_fichier,
                "buy_in": buy_in_fichier,
                "gains": gains_fichier,
                "net": resultat_net
            }
            
            # Ajouter la date si trouvée
            if file_date:
                expresso_data["date"] = file_date
                
            donnees_expressos.append(expresso_data)
            total_buy_ins += buy_in_fichier
            total_gains += gains_fichier

            # Mettre à jour les données pour le graphique
            resultat_net_courant += resultat_net
            gains_cumules.append(resultat_net_courant)

    return {
        "details": donnees_expressos,
        "total_buy_ins": total_buy_ins,
        "total_gains": total_gains,
        "resultat_net_total": total_gains - total_buy_ins,
        "nombre_expressos": len(donnees_expressos),
        "cumulative_results": gains_cumules # Clé ajoutée pour le graphique
    }

if __name__ == "__main__":
    chemin = input("Entrez le chemin du dossier d'historique : ")
    
    # Demander les filtres optionnels
    print("\n--- FILTRES OPTIONNELS ---")
    date_debut = input("Date de début (YYYY-MM-DD, optionnel) : ").strip()
    date_fin = input("Date de fin (YYYY-MM-DD, optionnel) : ").strip()
    
    # Construire le filtre de date
    date_filter = None
    if date_debut or date_fin:
        date_filter = (date_debut or None, date_fin or None)
    
    try:
        resultats = analyser_resultats_expresso(chemin, date_filter)
        print("\n--- RÉSUMÉ GLOBAL EXPRESSO ---")
        if date_filter:
            print(f"Filtre de date : {date_filter[0] or 'début'} - {date_filter[1] or 'fin'}")
        print(f"Nombre d'Expressos analysés : {resultats['nombre_expressos']}")
        print(f"Total des Buy-ins : {resultats['total_buy_ins']:.2f}€")
        print(f"Total des Gains : {resultats['total_gains']:.2f}€")
        print(f"Résultat Net Global : {resultats['resultat_net_total']:+.2f}€")
    except FileNotFoundError as e:
        print(e)