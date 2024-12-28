import requests
from bs4 import BeautifulSoup

TOURNAMENTS_URL = "https://play.limitlesstcg.com/tournaments/completed?game=POCKET&format=all&platform=all&type=online&time=7days&show=499"
ENDPOINT = "https://play.limitlesstcg.com"
WINLOSS = 1

# Request for 
r = requests.get(TOURNAMENTS_URL)
tournaments_soup = BeautifulSoup(r.content, 'html5lib')
tournaments_rows = tournaments_soup.find_all('a', attrs = {'class':'date'}) 

# Getting tournament URLs
urls = []
for row in tournaments_rows:
    urls.append(row["href"])

# Getting player + decklist URLs
for url in urls:
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
    # If optimizations are needed, the decklist URL is just the win-loss URL with /decklist at the end
    standings_rows = standings_table.find_all('tr', attrs = {'data-placing':True})
    for row in standings_rows:
        print(row.find_all("td")[WINLOSS].a["href"])
        print(row.find_all("td")[decklist].a["href"])
