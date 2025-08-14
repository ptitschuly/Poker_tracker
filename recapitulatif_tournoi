import os
import re

def traiter_resume(contenu_texte):
    """
    Extrait le buy-in et les gains d'un contenu textuel de résumé de tournoi.

    Args:
        contenu_texte (str): Le contenu complet du fichier de résumé.

    Returns:
        tuple: Un tuple contenant (buy_in, gains).
    """
    buy_in = 0.0
    gains = 0.0
    lignes = contenu_texte.split('\n')
    for ligne in lignes:
        # Extraire la somme des buy-ins (part principale + rebuys + bounty)
        if ligne.startswith("Buy-in:") or ligne.startswith("Buy-In :"):
            montants = re.findall(r'(\d+\.\d{2})€', ligne)
            buy_in = sum(float(m) for m in montants)

        # Extraire la somme des gains (prix + bounties)
        elif ligne.startswith("You won"):
            montants = re.findall(r'(\d+\.\d{2})€', ligne)
            gains = sum(float(m) for m in montants)
    return buy_in, gains

def run_test():
    """Exécute un cas de test avec un exemple de résumé de tournoi."""
    print("--- Lancement du Test ---")
    exemple_resume = """
Winamax Poker - Tournament summary : Kill The Fish(952211455)
Player : PogShellCie
Buy-In : 0.11€ + 0.11€ + 0.03€
Registered players : 402
Mode : tt
Type : knockout
Speed : semiturbo
Flight ID : 0
Levels : Levels : [100-200:25:1500:holdem-no-limit,125-250:30:300:holdem-no-limit]
Prizepool : 56.98€
Tournament started 2025/07/13 09:30:00 UTC
You played 2h 58min 25s 
You finished in 14th place
You won 0.63€ + Bounty 0.93€
"""
    # Résultats attendus
    buy_in_attendu = 0.11 + 0.11 + 0.03  # 0.25€
    gains_attendus = 0.63 + 0.93         # 1.56€
    resultat_net_attendu = gains_attendus - buy_in_attendu

    # Traitement de l'exemple
    buy_in_calcule, gains_calcules = traiter_resume(exemple_resume)
    resultat_net_calcule = gains_calcules - buy_in_calcule

    print(f"Buy-in attendu : {buy_in_attendu:.2f}€ | Calculé : {buy_in_calcule:.2f}€")
    print(f"Gains attendus  : {gains_attendus:.2f}€ | Calculés : {gains_calcules:.2f}€")
    print(f"Résultat net attendu : {resultat_net_attendu:+.2f}€ | Calculé : {resultat_net_calcule:+.2f}€")

    # Vérification
    if abs(buy_in_attendu - buy_in_calcule) < 0.01 and abs(gains_attendus - gains_calcules) < 0.01:
        print("\n>>> Test RÉUSSI !")
    else:
        print("\n>>> Test ÉCHOUÉ !")
    print("--- Fin du Test ---\n")

def analyser_resultats_tournois(repertoire):
    """
    Analyse les fichiers de résumé de tournois dans un répertoire donné pour calculer le résultat net.

    Args:
        repertoire (str): Le chemin vers le dossier contenant les fichiers de résumé.
    """
    if not os.path.isdir(repertoire):
        print(f"Erreur : Le répertoire '{repertoire}' n'existe pas.")
        return

    total_buy_ins = 0.0
    total_gains = 0.0
    fichiers_traites = 0

    print(f"Analyse du répertoire : {repertoire}\n")

    # Parcourir tous les fichiers dans le répertoire
    for nom_fichier in os.listdir(repertoire):
        # Filtrer les fichiers : doit finir par "summary.txt" et ne pas contenir "Expresso"
        if nom_fichier.endswith("summary.txt") and "Expresso" not in nom_fichier:
            chemin_complet = os.path.join(repertoire, nom_fichier)
            
            try:
                with open(chemin_complet, 'r', encoding='utf-8') as f:
                    contenu = f.read()
                
                buy_in_fichier, gains_fichier = traiter_resume(contenu)
                
                # Ne traiter que les fichiers où un buy-in a été trouvé
                if buy_in_fichier > 0:
                    fichiers_traites += 1
                    resultat_net_fichier = gains_fichier - buy_in_fichier

                    # Mettre à jour les totaux globaux
                    total_buy_ins += buy_in_fichier
                    total_gains += gains_fichier

            except Exception as e:
                print(f"Erreur lors du traitement du fichier {nom_fichier}: {e}")

    # Calcul et affichage du résumé global
    resultat_net_total = total_gains - total_buy_ins
    
    print("\n--- RÉSUMÉ GLOBAL ---")
    if fichiers_traites > 0:
        print(f"Nombre de tournois analysés : {fichiers_traites}")
        print(f"Total des Buy-ins : {total_buy_ins:.2f}€")
        print(f"Total des Gains : {total_gains:.2f}€")
        print(f"Résultat Net Global : {resultat_net_total:+.2f}€")
    else:
        print("Aucun fichier de résumé de tournoi correspondant n'a été trouvé.")

if __name__ == "__main__":
    # Lancer le test en premier
    # run_test()

    # Demander à l'utilisateur de fournir le chemin du dossier pour l'analyse complète
    # Exemple de chemin : C:\Users\VotreNom\AppData\Roaming\winamax\documents\VotrePseudo\history
    chemin_dossier = input("Entrez le chemin complet du dossier d'historique de Winamax (ou appuyez sur Entrée pour quitter) : ")
    if chemin_dossier:
        analyser_resultats_tournois(chemin_dossier)

