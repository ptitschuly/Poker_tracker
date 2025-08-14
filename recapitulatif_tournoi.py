import os
import re

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

def analyser_resultats_tournois(repertoire):
    """
    Analyse les fichiers de résumé de tournoi et retourne les données structurées,
    y compris les résultats cumulés pour le graphique.
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
        chemin_complet = os.path.join(repertoire, nom_fichier)
        with open(chemin_complet, 'r', encoding='utf-8') as f:
            contenu = f.read()
        
        buy_in, gains = traiter_resume(contenu)
        
        if buy_in > 0:
            resultat_net = gains - buy_in
            donnees_tournois.append({
                "fichier": nom_fichier,
                "buy_in": buy_in,
                "gains": gains,
                "net": resultat_net
            })
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
    try:
        resultats = analyser_resultats_tournois(chemin)
        print("\n--- RÉSUMÉ GLOBAL TOURNOIS ---")
        print(f"Nombre de tournois analysés : {resultats['nombre_tournois']}")
        print(f"Total des Buy-ins : {resultats['total_buy_ins']:.2f}€")
        print(f"Total des Gains : {resultats['total_gains']:.2f}€")
        print(f"Résultat Net Global : {resultats['resultat_net_total']:+.2f}€")
    except FileNotFoundError as e:
        print(e)

