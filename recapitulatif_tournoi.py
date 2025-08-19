import os
import re

# Regex pour extraire la date des noms de fichiers
RE_DATE_FROM_FILENAME = re.compile(r'(\d{4}-\d{2}-\d{2})')

def extraire_details_tournoi(fichier_path):
    """
    Extrait les détails complets d'un tournoi depuis un fichier de résumé,
    incluant les mains jouées.
    
    Args:
        fichier_path: Chemin vers le fichier de résumé de tournoi
        
    Returns:
        dict: Détails du tournoi avec buy-in, gains, mains, etc.
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
        
        # Extraire buy-in et gains du résumé
        buy_in, gains = traiter_resume(contenu)
        details["buy_in"] = buy_in
        details["gains"] = gains
        details["net"] = gains - buy_in
        
        # Extraire informations additionnelles du résumé
        lignes = contenu.split('\n')
        for ligne in lignes:
            ligne = ligne.strip()
            if ligne.startswith("Duration:"):
                details["duree"] = ligne.replace("Duration:", "").strip()
            elif ligne.startswith("Final Position:"):
                details["position_finale"] = ligne.replace("Final Position:", "").strip()
        
        # Extraire les mains
        mains = extraire_mains_tournoi(contenu)
        details["mains"] = mains
        details["nombre_mains"] = len(mains)
        
    except Exception as e:
        print(f"Erreur lors de l'extraction des détails de {fichier_path}: {e}")
    
    return details

def extraire_mains_tournoi(contenu_texte):
    """
    Extrait les détails des mains d'un tournoi.
    
    Args:
        contenu_texte: Contenu du fichier de tournoi
        
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

def traiter_resume(contenu_texte):
    """
    Extrait le buy-in et les gains d'un contenu textuel de résumé de tournoi.
    """
    buy_in = 0.0
    gains = 0.0
    for ligne in contenu_texte.split('\n'):
        if ligne.strip().lower().startswith("buy-in"):
            montants = re.findall(r'(\d+\.\d{2})€', ligne)
            buy_in = sum(float(m) for m in montants)
        elif ligne.strip().startswith("You won"):
            montants = re.findall(r'(\d+\.\d{2})€', ligne)
            gains = sum(float(m) for m in montants)
    return buy_in, gains

def analyser_resultats_tournois(repertoire, date_filter=None):
    """
    Analyse les fichiers de résumé de tournoi et retourne les données structurées,
    y compris les résultats cumulés pour le graphique.
    
    Args:
        repertoire: Chemin vers le répertoire contenant les fichiers
        date_filter: Tuple (date_debut, date_fin) au format 'YYYY-MM-DD' ou None pour pas de filtre
    """
    if not os.path.isdir(repertoire):
        raise FileNotFoundError(f"Le répertoire '{repertoire}' n'existe pas.")

    donnees_tournois = []
    total_buy_ins = 0.0
    total_gains = 0.0
    
    # Variables pour le graphique
    gains_cumules = []
    resultat_net_courant = 0.0

    fichiers_a_traiter = [f for f in os.listdir(repertoire) if f.endswith("summary.txt") and "Expresso" not in f]

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
        with open(chemin_complet, 'r', encoding='utf-8') as f:
            contenu = f.read()
        
        buy_in, gains = traiter_resume(contenu)
        
        if buy_in > 0:
            resultat_net = gains - buy_in
            tournoi_data = {
                "fichier": nom_fichier,
                "buy_in": buy_in,
                "gains": gains,
                "net": resultat_net
            }
            
            # Ajouter la date si trouvée
            if file_date:
                tournoi_data["date"] = file_date
                
            donnees_tournois.append(tournoi_data)
            total_buy_ins += buy_in
            total_gains += gains

            # Mettre à jour les données pour le graphique
            resultat_net_courant += resultat_net
            gains_cumules.append(resultat_net_courant)

    return {
        "details": donnees_tournois,
        "total_buy_ins": total_buy_ins,
        "total_gains": total_gains,
        "resultat_net_total": total_gains - total_buy_ins,
        "nombre_tournois": len(donnees_tournois),
        "cumulative_results": gains_cumules  # Clé ajoutée pour le graphique
    }

if __name__ == "__main__":
    # Cette partie sert uniquement à l'exécution directe du script pour le test
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
        resultats = analyser_resultats_tournois(chemin, date_filter)
        print("\n--- RÉSUMÉ GLOBAL TOURNOIS ---")
        if date_filter:
            print(f"Filtre de date : {date_filter[0] or 'début'} - {date_filter[1] or 'fin'}")
        print(f"Nombre de tournois analysés : {resultats['nombre_tournois']}")
        print(f"Total des Buy-ins : {resultats['total_buy_ins']:.2f}€")
        print(f"Total des Gains : {resultats['total_gains']:.2f}€")
        print(f"Résultat Net Global : {resultats['resultat_net_total']:+.2f}€")
    except FileNotFoundError as e:
        print(e)

