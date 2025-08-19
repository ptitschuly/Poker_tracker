import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from recapitulatif_tournoi import extraire_details_tournoi
from recapitulatif_expresso import extraire_details_expresso

def show_tournament_details(fichier_path, parent=None):
    """
    Affiche une fenêtre avec les détails complets d'un tournoi ou expresso.
    
    Args:
        fichier_path: Chemin vers le fichier de tournoi/expresso
        parent: Fenêtre parent (optionnel)
    """
    # Déterminer le type (tournoi ou expresso) et extraire les détails
    fichier_path_detail = fichier_path.replace("_summary","")
    if "Expresso" in fichier_path:
        details = extraire_details_expresso(fichier_path_detail)
        title_prefix = "Détails Expresso"
    else:
        details = extraire_details_tournoi(fichier_path_detail)
        title_prefix = "Détails Tournoi"
    
    # Créer la fenêtre popup
    root = parent if parent is not None else tk._default_root
    popup = tk.Toplevel(root)
    popup.title(f"{title_prefix} - {details['fichier']}")
    popup.geometry("1000x700")
    popup.grab_set()  # Modal window
    
    # Frame principal avec padding
    main_frame = ttk.Frame(popup, padding=10)
    main_frame.pack(fill="both", expand=True)
    
    # Titre et informations générales
    header_frame = ttk.Frame(main_frame)
    header_frame.pack(fill="x", pady=(0, 10))
    
    title_label = ttk.Label(header_frame, text=f"{title_prefix}", 
                           font=('TkDefaultFont', 14, 'bold'))
    title_label.pack(side="left")
    
    # Informations du tournoi en colonne droite
    info_frame = ttk.LabelFrame(header_frame, text="Résumé")
    info_frame.pack(side="right", padx=(10, 0))
    
    info_text = (f"Buy-in: {details['buy_in']:.2f}€\n"
                f"Gains: {details['gains']:.2f}€\n"
                f"Résultat Net: {details['net']:+.2f}€\n"
                f"Position: {details['position_finale']}\n"
                f"Durée: {details['duree']}\n"
                f"Mains jouées: {details['nombre_mains']}")
    
    ttk.Label(info_frame, text=info_text, justify="left").pack(padx=5, pady=5)
    
    # Notebook pour organiser les informations
    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill="both", expand=True, pady=(10, 0))
    
    # Onglet 1: Liste des mains
    hands_frame = ttk.Frame(notebook)
    notebook.add(hands_frame, text="Mains jouées")
    
    # Créer le Treeview pour les mains
    hands_tree_frame = ttk.Frame(hands_frame)
    hands_tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    columns = ('hand_num', 'level', 'cards', 'board', 'action', 'result')
    hands_tree = ttk.Treeview(hands_tree_frame, columns=columns, show='headings')
    
    # Configurer les colonnes
    hands_tree.heading('hand_num', text='Main #')
    hands_tree.heading('level', text='Niveau')
    hands_tree.heading('cards', text='Cartes')
    hands_tree.heading('board', text='Board')
    hands_tree.heading('action', text='Action')
    hands_tree.heading('result', text='Résultat')
    
    hands_tree.column('hand_num', width=60, anchor='center')
    hands_tree.column('level', width=60, anchor='center')
    hands_tree.column('cards', width=100, anchor='center')
    hands_tree.column('board', width=200, anchor='center')
    hands_tree.column('action', width=100, anchor='center')
    hands_tree.column('result', width=100, anchor='e')
    
    # Scrollbar pour le Treeview
    scrollbar_hands = ttk.Scrollbar(hands_tree_frame, orient=tk.VERTICAL, command=hands_tree.yview)
    hands_tree.configure(yscrollcommand=scrollbar_hands.set)
    
    # Remplir le Treeview avec les mains
    for main in details['mains']:
        result_text = f"{main['resultat']:.0f}" if main['resultat'] > 0 else "-"
        hands_tree.insert("", "end", values=(
            main['numero'],
            main['niveau'],
            main['cartes_hero'] or '-',
            main['board'] or '-',
            main['action_hero'] or '-',
            result_text
        ))
    
    hands_tree.pack(side="left", fill="both", expand=True)
    scrollbar_hands.pack(side="right", fill="y")
    
    # Onglet 2: Statistiques
    stats_frame = ttk.Frame(notebook)
    notebook.add(stats_frame, text="Statistiques")
    
    # Calculer quelques statistiques simples
    total_mains = len(details['mains'])
    mains_gagnees = sum(1 for m in details['mains'] if m['resultat'] > 0)
    mains_perdues = sum(1 for m in details['mains'] if m['resultat'] == 0 and m['action_hero'] not in ['Check', ''])
    
    actions_count = {}
    for main in details['mains']:
        action = main['action_hero']
        if action:
            actions_count[action] = actions_count.get(action, 0) + 1
    
    # Afficher les statistiques
    stats_text_frame = ttk.LabelFrame(stats_frame, text="Statistiques générales")
    stats_text_frame.pack(fill="x", padx=10, pady=10)
    
    stats_content = (f"Total mains: {total_mains}\n"
                    f"Mains gagnées: {mains_gagnees}\n"
                    f"Mains perdues/foldées: {mains_perdues}\n"
                    f"Taux de réussite: {(mains_gagnees/total_mains*100):.1f}%" if total_mains > 0 else "")
    
    ttk.Label(stats_text_frame, text=stats_content, justify="left").pack(padx=10, pady=10)
    
    # Graphique des actions
    if actions_count:
        chart_frame = ttk.LabelFrame(stats_frame, text="Répartition des actions")
        chart_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        fig, ax = plt.subplots(figsize=(6, 4), dpi=80)
        actions = list(actions_count.keys())
        counts = list(actions_count.values())
        
        ax.pie(counts, labels=actions, autopct='%1.1f%%', startangle=90)
        ax.set_title("Actions du joueur")
        
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
    
    # Boutons de contrôle
    buttons_frame = ttk.Frame(main_frame)
    buttons_frame.pack(fill="x", pady=(10, 0))
    
    def close_window():
        popup.destroy()
    
    ttk.Button(buttons_frame, text="Fermer", command=close_window).pack(side="right", padx=5)
    
    # Centrer la fenêtre
    popup.update_idletasks()
    x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
    y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
    popup.geometry(f"+{x}+{y}")
    
    return popup

# Test de la fonction
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Cacher la fenêtre principale
    
    # Test avec le fichier de tournoi sample
    show_tournament_details('/tmp/sample_poker_data/2024-01-15_Tournament_123456_summary.txt')
    
    root.mainloop()