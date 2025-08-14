import pandas as pd
import matplotlib.pyplot as plt
import re
import os

def process_hand(hand_text, user_name):
    """Processes a single hand of poker and returns the net result for the user."""
    hand_lines = hand_text.strip().split('\n')
    bet_amount = 0.0
    won_amount = 0.0
    is_summary = False

    # Find all lines related to the user's actions and summary
    for line in hand_lines:
        if "*** SUMMARY ***" in line:
            is_summary = True
        
        if user_name in line:
            # Extract bets made by the user (pre-flop, flop, turn, river)
            if not is_summary and ("bets" in line or "raises" in line or "calls" in line or "posts" in line):
                try:
                    # The amount the user put in the pot in this action
                    match = re.search(r'(\d+\.?\d*)€', line)
                    if match:
                        bet_amount += float(match.group(1))
                except (ValueError, IndexError):
                    print(f"Could not parse bet amount from line: {line}")

            # Extract winnings from the summary section
            if is_summary and "won" in line:
                try:
                    match = re.search(r'won (\d+\.?\d*)€', line)
                    if match:
                        won_amount = float(match.group(1))
                except (ValueError, IndexError):
                    print(f"Could not parse won amount from line: {line}")

    return won_amount - bet_amount

def run_test():
    """Runs a test case with a sample hand to verify the logic."""
    print("--- Running Test Case ---")
    user_name = "PogShellCie"
    # A sample hand history text
    test_hand = """
Winamax Poker - HandId: #12345 - Holdem no limit (0.05€/0.10€) - 2025/08/14 20:00:00 UTC
Table: 'Nice 5-max'
Seat 1: PlayerA (5.00€)
Seat 2: PogShellCie (10.00€) (big blind)
Seat 3: PlayerC (4.50€) (button)
Seat 4: PlayerD (11.20€)
Seat 5: PlayerE (9.80€) (small blind)
PlayerE posts small blind 0.05€
PogShellCie posts big blind 0.10€
*** HOLE CARDS ***
Dealt to PogShellCie [Ah Kh]
PlayerD raises 0.20€ to 0.30€
PlayerE folds
PogShellCie calls 0.20€
PlayerC folds
*** FLOP *** [As 5c 6h]
PogShellCie checks
PlayerD bets 0.45€
PogShellCie calls 0.45€
*** TURN *** [As 5c 6h][Kd]
PogShellCie checks
PlayerD bets 1.10€
PogShellCie raises 2.50€ to 3.60€
PlayerD calls 2.50€
*** RIVER *** [As 5c 6h Kd][2s]
PogShellCie bets 5.65€ and is all-in
PlayerD calls 5.65€
*** SHOW DOWN ***
PogShellCie shows [Ah Kh] (two pair, Aces and Kings)
PlayerD shows [6d 6s] (three of a kind, Sixes)
PlayerD collected 19.80€ from pot
*** SUMMARY ***
Total pot 20.80€ | Rake 1.00€
Board: [As 5c 6h Kd 2s]
Seat 2: PogShellCie (big blind) lost with two pair, Aces and Kings
Seat 4: PlayerD won 19.80€ with three of a kind, Sixes
    """
    
    # Expected results for this hand:
    # Blinds: 0.10€
    # Call pre-flop: 0.20€
    # Call flop: 0.45€
    # Raise turn: 3.60€
    # Bet river: 5.65€
    # Total bet: 0.10 + 0.20 + 0.45 + 3.60 + 5.65 = 10.00€
    # Won: 0€
    # Net result: -10.00€
    expected_net = -10.00
    
    actual_net = process_hand(test_hand, user_name)
    
    print(f"User: {user_name}")
    print(f"Expected Net Result: {expected_net:.2f}€")
    print(f"Actual Net Result:   {actual_net:.2f}€")
    
    if abs(expected_net - actual_net) < 0.01:
        print("Test PASSED!")
    else:
        print("Test FAILED!")
    print("--- End of Test Case ---\n")


def main():
    user_name = "PogShellCie"
    try:
        folder_path = input("Entrez le chemin complet du dossier d'historique de Winamax (ex: C:\\Users\\schut\\AppData\\Roaming\\winamax\\documents) : ")
        if not os.path.isdir(folder_path):
            print("Error: The provided path is not a valid directory.")
            return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    net_result = 0.0
    hand_results = []

    excluded_keywords = ["Freeroll", "Expresso", "Kill The Fish"]

    all_items = os.listdir(folder_path)
    hand_history_files = [
        os.path.join(folder_path, item) 
        for item in all_items 
        if item.endswith('.txt') and not any(keyword in item for keyword in excluded_keywords)
    ]

    print(f"Found {len(hand_history_files)} relevant files:")

    for file_path in hand_history_files:
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()

        hand_list = file_content.split('Winamax Poker -')
        
        for hand_text in hand_list:
            if not hand_text.strip():
                continue
            
            hand_net = process_hand(hand_text, user_name)
            net_result += hand_net
            hand_results.append(net_result)

    print(f"\nOverall net result for {user_name}: {net_result:.2f}€")

    if hand_results:
        plt.figure(figsize=(12, 6))
        plt.plot(hand_results)
        plt.xlabel("Hand Number")
        plt.ylabel("Net Result (€)")
        plt.title(f"Cumulative Net Result per Hand for {user_name}")
        plt.grid(True)
        plt.show()
    else:
        print("No hand data to plot.")

# To run the test, call run_test(). To run the main script, call main().
if __name__ == '__main__':
    #run_test()
    main() # You can comment out run_test() and uncomment main() to run the full script