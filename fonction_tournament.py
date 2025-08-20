import re
import os

# Regex partagées
RE_DATE_FROM_FILENAME = re.compile(r'(\d{4}-\d{2}-\d{2})|(\d{8})')
amount_regex = re.compile(r'(\d+(?:[.,]\d{2})?)€')

def extraire_date_fichier(nom_fichier):
    """
    Extrait la date d'un nom de fichier au format YYYY-MM-DD ou YYYYMMDD.
    Retourne la date normalisée 'YYYY-MM-DD' ou None.
    """
    match = RE_DATE_FROM_FILENAME.search(nom_fichier)
    if match:
        if match.group(1):
            return match.group(1)
        elif match.group(2):
            g2 = match.group(2)
            return f"{g2[0:4]}-{g2[4:6]}-{g2[6:8]}"
    return None

def extraire_montants_ligne(ligne):
    """
    Extrait tous les montants d'une ligne sous forme de float.
    """
    return [float(m.replace(',', '.')) for m in amount_regex.findall(ligne)]

def traiter_resume(contenu_texte):
    """
    Extrait le buy-in et les gains d'un contenu textuel de résumé de tournoi.
    Utilise la fonction utilitaire extraire_montants_ligne.
    """
    buy_in = None
    gains = 0.0
    for ligne in contenu_texte.split('\n'):
        l = ligne.strip()
        if l.lower().startswith("buy-in"):
            buy_in = sum(extraire_montants_ligne(l))
            if buy_in is None:
                buy_in = 0.0
        elif l.startswith("You won"):
            gains = sum(extraire_montants_ligne(l))
            if gains is None:
                gains = 0.0
    return buy_in, gains

def extraire_details_tournoi_expresso(fichier_path):
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
        "hero_username": "",
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

        # Extraire le joueur : 
        hero_username = re.search(r'Player: ([^\s]+)', contenu)
        if hero_username:
            details["hero_username"] = hero_username.group(1)  
                  
        # Extraire buy-in et gains du résumé
        buy_in, gains = traiter_resume(contenu)
        details["buy_in"] = buy_in
        details["gains"] = gains
        details["net"] = gains - buy_in
        
        # Extraire informations additionnelles du résumé
        lignes = contenu.split('\n')
        for ligne in lignes:
            ligne = ligne.strip()
            if ligne.startswith("You played"):
                details["duree"] = ligne.replace("You played", "").strip()
            elif ligne.startswith("You finished"):
                details["position_finale"] = ligne.replace("You finished", "").strip()

        fichier_path_detail = fichier_path.replace("_summary","")
        with open(fichier_path_detail, 'r', encoding='utf-8') as file:
            contenu_detail = file.read()
        # Extraire les mains
        mains = extraire_mains_tournoi_expresso(contenu_detail)
        details["mains"] = mains
        details["nombre_mains"] = len(mains)
        
    except Exception as e:
        print(f"Erreur lors de l'extraction des détails de {fichier_path}: {e}")
    
    return details

def extraire_mains_tournoi_expresso(contenu_texte):
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
            "hero": "",
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

        # Extraire le joueur : 
        hero_username = re.search(r'Player: ([^\s]+)', partie)
        if hero_username:
            main_details["hero"] = hero_username.group(1)

        # Extraire l'ID de la main
        hand_id_match = re.search(r'HandId: #([^-\s]+)', partie)
        if hand_id_match:
            main_details["hand_id"] = hand_id_match.group(1)
        
        # Extraire le niveau
        level_match = re.search(r'level: (\d+)', partie)
        if level_match:
            main_details["niveau"] = level_match.group(1)
        
        # Extraire les cartes du héros
        cartes_match = re.search(rf'Dealt to {re.escape(hero_username)} \[([^\]]+)\]', partie)
        if not cartes_match:
            cartes_match = re.search(r'shows \[([^\]]+)\]', partie)
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
        wins_match = re.search(rf'{re.escape(main_details["hero"])} wins (\d+(?:\.\d{2})?) with', partie)
        if wins_match:
            main_details["resultat"] = float(wins_match.group(1))
        
        # Déterminer l'action principale du héros
        if "fold" in partie and f"{main_details['hero']} folds" in partie:
            main_details["action_hero"] = "Fold"
        elif "calls" in partie and f"{main_details['hero']} calls" in partie:
            main_details["action_hero"] = "Call"
        elif "raises" in partie and f"{main_details['hero']} raises" in partie:
            main_details["action_hero"] = "Raise"
        elif "bets" in partie and f"{main_details['hero']} bets" in partie:
            main_details["action_hero"] = "Bet"
        elif "checks" in partie and f"{main_details['hero']} checks" in partie:
            main_details["action_hero"] = "Check"
        
        mains.append(main_details)
    
    return mains

def analyser_resultats_générique(repertoire, 
                                 date_filter=None,
                                 file_filter=lambda f:True,
                                 count_key="nombre_tournois"):
    """
    Analyse les fichiers de résumé Expresso et retourne les données structurées,
    y compris les résultats cumulés pour le graphique.
    
    Args:
        repertoire: Chemin vers le répertoire contenant les fichiers
        date_filter: Tuple (date_debut, date_fin) au format 'YYYY-MM-DD' ou None pour pas de filtre
    """
    if not os.path.isdir(repertoire):
        raise FileNotFoundError(f"Le répertoire '{repertoire}' n'existe pas.")

    donnees = []
    total_buy_ins = 0.0
    total_gains = 0.0

    # Variables pour le graphique
    gains_cumules = []
    resultat_net_courant = 0.0

    fichiers_a_traiter = [f for f in os.listdir(repertoire) if f.endswith("summary.txt") and file_filter(f)]
    for nom_fichier in sorted(fichiers_a_traiter):
        # Extraction de la date depuis le nom du fichier (utilitaire)
        file_date = extraire_date_fichier(nom_fichier)
        
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
        
        # Inclure si une ligne buy-in a été trouvée (même si le montant est 0.0)
        if buy_in is not None:
            resultat_net = gains - buy_in
            data = {
                "fichier": nom_fichier,
                "buy_in": buy_in,
                "gains": gains,
                "net": resultat_net
            }

            # Ajouter la date si trouvée
            if file_date:
                data["date"] = file_date

            donnees.append(data)
            total_buy_ins += buy_in
            total_gains += gains

            # Mettre à jour les données pour le graphique
            resultat_net_courant += resultat_net
            gains_cumules.append(resultat_net_courant)

    return {
        "details": donnees,
        "total_buy_ins": total_buy_ins,
        "total_gains": total_gains,
        "resultat_net_total": total_gains - total_buy_ins,
        "nombre_expressos": len(donnees),
        "cumulative_results": gains_cumules # Clé ajoutée pour le graphique
    }
