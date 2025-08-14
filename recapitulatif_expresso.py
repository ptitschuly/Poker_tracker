# filepath: c:\Users\schut\Documents\Projet_Winamax\Tracker_poker\recapitulatif_expresso.py
import os
import re


def analyser_resultats_expresso(repertoire):
    """
    Analyse les fichiers de résumé Expresso et retourne les données structurées,
    y compris les résultats cumulés pour le graphique.
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
            donnees_expressos.append({
                "fichier": nom_fichier,
                "buy_in": buy_in_fichier,
                "gains": gains_fichier,
                "net": resultat_net
            })
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
    try:
        resultats = analyser_resultats_expresso(chemin)
        print("\n--- RÉSUMÉ GLOBAL EXPRESSO ---")
        print(f"Nombre d'Expressos analysés : {resultats['nombre_traites']}")
        print(f"Total des Buy-ins : {resultats['total_buy_ins']:.2f}€")
        print(f"Total des Gains : {resultats['total_gains']:.2f}€")
        print(f"Résultat Net Global : {resultats['resultat_net_total']:+.2f}€")
    except FileNotFoundError as e:
        print(e)