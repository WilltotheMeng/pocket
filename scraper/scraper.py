import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import json
import copy

TOURNAMENTS_URL = "https://play.limitlesstcg.com/tournaments/completed?game=POCKET&format=all&platform=all&type=online&time=1days&show=499"
ENDPOINT = "https://play.limitlesstcg.com"
WINLOSS = 1
DECKLIST_SUFFIX = "/decklist"


# Request for overall list of tournaments
r = requests.get(TOURNAMENTS_URL)
tournaments_soup = BeautifulSoup(r.content, 'html5lib')
tournaments_rows = tournaments_soup.find_all('a', attrs = {'class':'date'}) 

# Getting tournament URLs
tournaments_urls = []
for row in tournaments_rows:
    tournaments_urls.append(row["href"])
print("Finished finding tournaments")

# Getting player + decklist URLs
player_urls = []
for url in tournaments_urls:
    r = requests.get(ENDPOINT+ url)
    standings_soup = BeautifulSoup(r.content, 'html5lib')
    standings_table = standings_soup.find("table", attrs = {'class':'striped'})

    # Determine which column the decklist is in
    decklist = -1
    for index, p_tag in enumerate(standings_table.find_all('th')):
        if p_tag.text == "List":
            decklist = index
            break
    # If decklists don't exist, we can't do anything with the tournament data
    if (decklist == -1):
        continue
    
    # Gather links for the player's win-loss and the decklist
    # The decklist URL is just the win-loss URL with /decklist at the end
    standings_rows = standings_table.find_all('tr', attrs = {'data-placing':True})
    for row in standings_rows:
        player_urls.append(row.find_all("td")[WINLOSS].a["href"])
print("Finished finding matchups and decklists")

# Gather matchup info
matchups = []
for url in player_urls:
    r = requests.get(ENDPOINT + url)
    matchups_soup = BeautifulSoup(r.content, 'html5lib')
    matchups_table = matchups_soup.find("div", attrs = {'class':'history'})
    wins_rows = matchups_soup.find_all("td", attrs = {'class':'winner'}, string="WIN")

    for row in wins_rows:
        loser = row.parent.find("a")
        # Byes don't have a link
        if loser is None:
            continue
        matchups.append([url, loser["href"]])
matchup_data = pd.DataFrame(matchups, columns=['WINNER', 'LOSER'])
matchup_data.to_csv("matchups.csv")
print("Finished getting matchups")

# Gather decklist info 
deck_dictionary = {}
for url in player_urls:
    r = requests.get(ENDPOINT + url + DECKLIST_SUFFIX)
    decklist_soup = BeautifulSoup(r.content, 'html5lib')
    deck_type = decklist_soup.find("div", attrs = {'class':'deck'})["data-tooltip"]
    cards_soup = decklist_soup.find("div", attrs = {'class':'decklist'})

    player_dict = {}
    cards = []
    # Limitless splits out Pokemon and Trainer cards so we need to look at all objects
    for card in cards_soup.find_all("p"):
        cards.append(card.a.text)
    
    player_dict["deck_type"] = deck_type
    player_dict["cards"] = copy.deepcopy(cards)
    deck_dictionary[url] = copy.deepcopy(player_dict)
print("Finished getting decklists")

with open("decks.json", "w") as f:
    json.dump(deck_dictionary, f)

    
