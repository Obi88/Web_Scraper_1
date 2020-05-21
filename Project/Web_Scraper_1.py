# Imports
from bs4 import BeautifulSoup
import requests
import sqlite3

# Convert string %'s to decimals
def text_to_percentage(text):
    text_length = len(text)-1
    percentage = float(text[:text_length])/100
    return percentage

# Create database and initialise table
conn = sqlite3.connect('C:\\Users\go_ac\\Documents\\Files From Old Laptop\\Further learning\\IT\\General\\Code\\Projects\\Web_Scraper_1\Project\Database\\Football_Stats.sqlite')
cur = conn.cursor()

# Check if the tables in the database should be reset.
while True:
    reset = input('Reset Tables? (Enter "Y" or "N"): ')

    if reset == 'Y' or reset == 'y':
        cur.execute('DROP TABLE IF EXISTS Players')
        cur.execute('DROP TABLE IF EXISTS Top_Scorers')
        conn.commit()

        break
    elif reset == 'N' or reset == 'n':
        break
    else:
        print('Please enter "Y" or "N" on;y')

# Allow Foreign keys (as turned off by default in SQLite)
#cur.execute('PRAGMA foreign_keys = ON')

# Create database and initialise table
cur.execute('CREATE TABLE IF NOT EXISTS Players (Name TEXT NOT NULL, Team TEXT NOT NULL, CONSTRAINT Player_pk PRIMARY KEY (Name, Team))')
cur.execute('CREATE TABLE IF NOT EXISTS Top_Scorers (Name TEXT NOT NULL, Team TEXT NOT NULL, Goals INTEGER, Assists INTEGER, Shots_On_Target_Percentage DECIMAL(2,0), CONSTRAINT Player_pk PRIMARY KEY (Name, Team))')
conn.commit()

# Inputs
count = 0

while True:
    team = input('Enter team name: ')
    team_split = team.lower().split(' ')
    team_slug = '-'.join(team_split)

    # Use '.content' rather than '.text' here to avoid issues with dealing with improperly encoded text within the webpage.
    web_data = requests.get(f'https://www.bbc.co.uk/sport/football/teams/{team_slug}/top-scorers').content
    soup = BeautifulSoup(web_data,'html5lib')

    # print(soup.find('div', class_='error-message').h2.text)  #### ERROR CHECKING ####

    if soup.find('div', class_='error-message') == None:
        break
    else:
        print('Team not found. Please try another one.')

while True:
    no_of_players = input('Enter the length of the top scorer list to show: ')
    try:
        no_of_players = int(no_of_players)
        break
    except:
        print('Please enter a number only')

# Add an empty line for neatness.
print()

# print(soup.prettify())  #### ERROR CHECKING ####

# Get relevant tags and class info by inspecting the relevant elements on the webpage within the browser.
for scorer_info in soup.find_all('div', class_= 'top-player-stats__body'):
    #print(scorer_info.prettify())
    if count >= no_of_players:
        break

    # Get name, goals, assists, % shots on target
    name = scorer_info.h2.text

    goals = scorer_info.find('span',class_='top-player-stats__goals-scored-number').text
    goals = int(goals)

    assists = scorer_info.find('span',class_='top-player-stats__assists-number gel-double-pica').text
    assists = int(assists)

    shots_on_target = scorer_info.find('span',class_='percentage-bar-chart__percentage gel-pica percentage-goals-on-target').text
    shots_on_target = text_to_percentage(shots_on_target)

    # The sep ='' argument sets the keyword argument seperator to have no space (default is one space between arguments in the print statement)
    print('Name = ', name,'\n','Goals = ', goals,'\n','Assists = ', assists,'\n','Shots on target = ', shots_on_target,'\n', sep ='')

    # Insert informtion into SQL database
    cur.execute('INSERT OR IGNORE INTO Players (Name, Team) VALUES (?,?)',(name, team))
    cur.execute('INSERT OR IGNORE INTO Top_Scorers (Name, Team, Goals, Assists, Shots_On_Target_Percentage) VALUES (?,?,?,?,?)',(name, team, goals, assists, shots_on_target))

    # Update information in case the stats have changed
    cur.execute('UPDATE Top_Scorers SET Goals = ?, Assists = ?, Shots_On_Target_Percentage = ? WHERE (Name = ? AND Team = ?)',(goals, assists, shots_on_target, name, team))

    conn.commit()

    count += 1

#### START HERE: Update script to 1) visualise the data ####
