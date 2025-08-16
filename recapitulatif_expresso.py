# filepath: c:\Users\schut\Documents\Projet_Winamax\Tracker_poker\recapitulatif_expresso.py
import os
import re

# Regex pour extraire la date des noms de fichiers
RE_DATE_FROM_FILENAME = re.compile(r'(\d{4}-\d{2}-\d{2})')


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
            for ligne in f:
                if ligne.strip().lower().startswith("buy-in"):
                    montants = re.findall(r'(\d+\.\d{2})€', ligne)
                    buy_in_fichier = sum(float(m) for m in montants)
                elif ligne.strip().startswith("You won"):
                    montants = re.findall(r'(\d+\.\d{2})€', ligne)
                    gains_fichier = sum(float(m) for m in montants)
        
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