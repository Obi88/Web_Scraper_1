###### Setup ######

# Imports
from bs4 import BeautifulSoup
import requests
import sqlite3

# Create database and initialise tables
conn = sqlite3.connect('C:\\Users\go_ac\\Documents\\Files From Old Laptop\\Further learning\\IT\\General\\Code\\Projects\\Web_Scraper_1\Project\Database\\Football_Stats.sqlite')
cur = conn.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS Players (Name TEXT NOT NULL, Team TEXT NOT NULL, CONSTRAINT Player_pk PRIMARY KEY (Name, Team))')
cur.execute('CREATE TABLE IF NOT EXISTS Top_Scorers (Name TEXT NOT NULL, Team TEXT NOT NULL, Goals INTEGER, Assists INTEGER, Shots_On_Target_Percentage DECIMAL(2,0), CONSTRAINT Player_pk PRIMARY KEY (Name, Team))')
conn.commit()


###### Define helper functions ######

# Check if the tables in the database should be reset.
def database_reset_check(connection, cursor_object):
    cursor_object.execute('DROP TABLE IF EXISTS Players')
    cursor_object.execute('DROP TABLE IF EXISTS Top_Scorers')
    connection.commit()
    print("The database has been refreshed.")

def parse_data(soup_object, team_name, no_of_players, connection, cursor_object):
    count = 0

    # Get relevant tags and class info by inspecting the relevant elements on the webpage within the browser.
    for scorer_info in soup_object.find_all('div', class_= 'top-player-stats__body'):

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

        if print_info == "Yes":
            # The sep ='' argument sets the keyword argument seperator to have no space (default is one space between arguments in the print statement)
            print('Name = ', name,'\n', 'Team = ', team_name,'\n','Goals = ', goals,'\n','Assists = ', assists,'\n','Shots on target = ', shots_on_target,'\n', sep ='')

        # Insert informtion into SQL database
        update_database(connection, cursor_object, name, team_name, goals, assists, shots_on_target)

        count += 1

# Update the database with new informtion.
def update_database(connection, cursor_object, name, team, goals, assists, shots_on_target):
    # Insert informtion into SQL database
    cursor_object.execute('INSERT OR IGNORE INTO Players (Name, Team) VALUES (?,?)',(name, team))
    cursor_object.execute('INSERT OR IGNORE INTO Top_Scorers (Name, Team, Goals, Assists, Shots_On_Target_Percentage) VALUES (?,?,?,?,?)',(name, team, goals, assists, shots_on_target))

    # Update information in case the stats have changed
    cursor_object.execute('UPDATE Top_Scorers SET Goals = ?, Assists = ?, Shots_On_Target_Percentage = ? WHERE (Name = ? AND Team = ?)',(goals, assists, shots_on_target, name, team))

    connection.commit()

# Convert string %'s to decimals
def text_to_percentage(text):
    text_length = len(text)-1
    percentage = float(text[:text_length])/100
    return percentage

# Select the team who's top scorers you want to record.
def sluggify_team_name(team_name):
    team_split = team_name.lower().split(' ')
    team_slug = '-'.join(team_split)
    return team_slug


###### Main program ######

def team_data(team_name, no_of_players, connection, cursor_object, print_info = "No",):

    try:
        no_of_players = int(no_of_players)
    except:
        print("The numbers of players to search for must be provided as an integer")
        return

    team_slug = sluggify_team_name(team_name)

    # Get data from BBC Football website.
    # Use '.content' rather than '.text' here to avoid issues with dealing with improperly encoded text within the webpage.
    web_data = requests.get(f'https://www.bbc.co.uk/sport/football/teams/{team_slug}/top-scorers').content
    soup = BeautifulSoup(web_data,'html5lib')

    if soup.find('div', class_='error-message') == None:
        pass
    else:
        print('Team not found. Please try another one.')
        return

    parse_data(soup, team_name, no_of_players, connection, cursor_object)


###### START HERE: Update script to 1) Add output functions (SQL queries); 2) Visualise the data using these output functions and TKinter. Assign actions (such as reseting the database) to buttons. ######
# For step 1, print the results into the section run as main below.



###### Output functions ######

# Summary of the teams, goals, assists and number of scorers in the database.

# The top scorer(s)/assisters in the database.

# Average goals/assists per person for each team in the database.

# A weighted score for each team (ranked and sorted).



#### STEPS OF GUI: 1) Add a reset database button. ####
#### 2) text entry boxes promption the team name and the number of scorers to add to the database (write a 'update database' function and a submit button to initiate it. ####
#### 3) Print the added entries within a textbox with a 'clear_textbox' function timed to automatically clear the box after say 10 seconds. ####
#### 4) Create another window where can retrieve interesting information from the top scorers database [such as: 1) a summary of the teams, goals, assists and number of scorers in the database, 2) The top scorer(s)/assisters in the database, 3) average goals/assists per person for each team in the database, 4) A weighted score for each team (ranked and sorted)].  ####
#### 5) Create a button to run each of the 4 stats (and put their code inside functions and call when the button is clicked). Print detailed results to a textbox, with a label used to show the top ranked one (include a picture with a gold trophy beside it.)  ####
#### 6) Include a button to switch between the 2 views (database addition and printed stats)  ####


###### ++++++ This section is executed only if the module is being ran directly (as opposed to functions being imported for use in another program) ++++++ ######

if __name__ == '__main__':

    # Reset the database?
    while True:
        reset = input('Reset Tables? (Enter "Y" or "N"): ')

        if reset == 'Y' or reset == 'y':
            database_reset_check(conn, cur)
            break
        elif reset == 'N' or reset == 'n':
            break
        else:
            print('Please enter "Y" or "N" only')

    # Inputs.
    teams_to_check = []
    no_of_players_per_team = []

    done = "Y"

    while done !="N" and done !="n":
        team = input('Enter team name: ')
        no_of_players = input('Enter the length of the top scorer list to show: ')

        teams_to_check.append(team)
        no_of_players_per_team.append(no_of_players)

        while True:
            done = input('Any more teams to check? (Enter "Y" or "N"): ')
            if done == "Y" or done == "N" or done =="y" or done == "n":
                pass
            else:
                print('Please enter "Y" or "N" only')
                continue
            break

    search_list = zip(teams_to_check, no_of_players_per_team)

    # Check if scraped web information should be printed to the terminal.
    print_info = input("Print the player information to the Terminal? (Enter 'Yes' if required): ")

    # Add an empty line for neatness.
    print()

    # Run the main program.
    for team, no_of_players in search_list:
        team_data(team, no_of_players, conn, cur, print_info)
