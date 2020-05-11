# Imports
from bs4 import BeautifulSoup
import requests

# Inputs
count = 0
team = input('Enter team name: ')
team_split = team.lower().split(' ')
team = '-'.join(team_split)

while True:
    no_of_players = input('Enter the length of the top scorer list to show: ')
    try:
        no_of_players = int(no_of_players)
        break
    except:
        print('Please enter a number only')

web_data = requests.get(f'https://www.bbc.co.uk/sport/football/teams/{team}/top-scorers').text
soup = BeautifulSoup(web_data,'html5lib')

# print(soup.prettify())

# Get relevant tags and class info by inspecting the relevant elements on the webpage within the browser.
for scorer_info in soup.find_all('div', class_= 'top-player-stats__body'):
    #print(scorer_info.prettify())
    if count >= no_of_players:
        break

    # Get name, goals, assists, % shots on target
    name = scorer_info.h2.text
    goals = scorer_info.find('span',class_='top-player-stats__goals-scored-number').text
    assists = scorer_info.find('span',class_='top-player-stats__assists-number gel-double-pica').text
    shots_on_target = scorer_info.find('span',class_='percentage-bar-chart__percentage gel-pica percentage-goals-on-target').text

    # The sep ='' argument sets the keyword argument seperator to have no space (default is one space between arguments in the print statement)
    print('Name = ', name,'\n','Goals = ', goals,'\n','Assists = ', assists,'\n','Shots on target = ', shots_on_target,'\n', sep ='')

    count += 1

#### START HERE: Update script to 1) Handle if a team name isn't found; 2) Correct names where funny characters are used (such as Sadio Mane); 3) save data to a SQlite database; and 4) visualise the data ####
