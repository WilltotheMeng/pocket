import numpy as np
import pandas as pd
import json
import copy

comparison = ["Dragonite Frosmoth","Misty"]

ONE_CARD = "1 "
TWO_CARD = "2 "

# Parse scraped data
decks = {}
with open('decks.json') as json_file:
    decks = json.load(json_file)
matchups = pd.read_csv('matchups.csv')

# Determine win percents
deck_stats = pd.DataFrame(columns=["WINS","LOSSES","TOTAL_GAMES","WINRATE","WIN_DECK_KEYS","LOSS_DECK_KEYS"])
win_counts = {}
loss_counts = {}
all_deck_types = {}
for _, rows in matchups.iterrows():
    winning_deck = decks[rows["WINNER"]]["deck_type"]
    losing_deck = decks[rows["LOSER"]]["deck_type"]

    # Toss dittos
    if winning_deck == losing_deck:
        continue

    # Easy mode
    if winning_deck in win_counts:
        win_counts[winning_deck] += 1
    else: 
        win_counts[winning_deck] = 1
    if losing_deck in loss_counts:
        loss_counts[losing_deck] += 1
    else: 
        loss_counts[losing_deck] = 1
    
    all_deck_types[winning_deck] = 1
    all_deck_types[losing_deck] = 1

    # Hard mode
    if winning_deck not in deck_stats.index:
        deck_stats.loc[winning_deck] = [0, 0, 0, 0.0, [], []]
    if losing_deck not in deck_stats.index:
        deck_stats.loc[losing_deck] = [0, 0, 0, 0.0, [], []]
    
    deck_stats.at[winning_deck, "WINS"] += 1
    deck_stats.at[winning_deck, "WIN_DECK_KEYS"].append(rows["WINNER"])
    deck_stats.at[losing_deck, "LOSSES"] += 1
    deck_stats.at[losing_deck, "LOSS_DECK_KEYS"].append(rows["LOSER"])

# Post-processing
for deck in deck_stats.index:
    total_games = deck_stats.at[deck, "WINS"] + deck_stats.at[deck, "LOSSES"]
    deck_stats.at[deck, "TOTAL_GAMES"] = total_games
    deck_stats.at[deck, "WINRATE"] = deck_stats.at[deck, "WINS"] / total_games

deck_stats.sort_values(by="TOTAL_GAMES", ascending=False, inplace=True)

for deck in deck_stats.index:

    #print(deck + " win rate: " + format(deck_stats.at[deck, "WINRATE"], ".0%") + " (n=" + str(deck_stats.at[deck, "TOTAL_GAMES"]) + ")")
    break


zero_stats = [0, 0, 0]
one_stats = [0, 0, 0]
two_stats = [0, 0, 0]

for winning_deck in deck_stats.at[comparison[0], "WIN_DECK_KEYS"]:
    if (ONE_CARD + comparison[1]) in decks[winning_deck]["cards"]:
        one_stats[0] += 1
    elif (TWO_CARD + comparison[1]) in decks[winning_deck]["cards"]:
        two_stats[0] += 1
    else:
        zero_stats[0] += 1

for losing_deck in deck_stats.at[comparison[0], "LOSS_DECK_KEYS"]:
    if (ONE_CARD + comparison[1]) in decks[losing_deck]["cards"]:
        one_stats[1] += 1
    elif (TWO_CARD + comparison[1]) in decks[losing_deck]["cards"]:
        two_stats[1] += 1
    else:
        zero_stats[1] += 1

zero_stats[2] = zero_stats[0] + zero_stats[1]
one_stats[2] = one_stats[0] + one_stats[1]
two_stats[2] = two_stats[0] + two_stats[1]
zero_winrate = "N/A" if zero_stats[2] == 0 else format(zero_stats[0] / zero_stats[2], ".0%")
one_winrate = "N/A" if one_stats[2] == 0 else format(one_stats[0] / one_stats[2], ".0%")
two_winrate = "N/A" if two_stats[2] == 0 else format(two_stats[0] / two_stats[2], ".0%")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("Winrate Analysis of " + comparison[1] + " in " + comparison[0])
print("    Zero copies: " + zero_winrate + " (n=" + str(zero_stats[2]) + ")")
print("       One copy: " + one_winrate + " (n=" + str(one_stats[2]) + ")")
print("     Two copies: " + two_winrate + " (n=" + str(two_stats[2]) + ")")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

deck_stats.to_csv("deckstats.csv")