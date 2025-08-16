import os
import re

# Regex pour extraire la date des noms de fichiers
RE_DATE_FROM_FILENAME = re.compile(r'(\d{4}-\d{2}-\d{2})')

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

