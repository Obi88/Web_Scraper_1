###### Setup ######

# Imports
from bs4 import BeautifulSoup
import requests
import sqlite3
import pprint   # Module to do pretty printing.

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

        if print_info == "Yes" or print_info == "yes" or print_info == "Y" or print_info == "y":
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


###### Results functions ######

# Summary of the teams, goals, assists and number of scorers in the database.
def summary(connection, cursor_object):
    cursor_object.execute("SELECT Team, SUM(Goals), SUM(Assists), COUNT(Name) FROM Top_Scorers GROUP BY Team")

    summary_list = []
    headings = ["team", "goals", "assists", "no_of_players"]

    for row in cursor_object:
        team_dict = {}

        team_dict = dict(zip(headings,row)) # Note that you can zip any 2 sequences together, they don't have to be the same data type (here I'm zipping the list "headings" with the tuple "row")
        summary_list.append(team_dict)

    pprint.pprint(summary_list)
    print()

# The top scorer(s)/assisters in the database.
def top_scorers(connection, cursor_object):
    no_of_scorers = input("Enter the maximum number of top scorers you want to see: ")
    try:
        int(no_of_scorers)
    except:
        print("Please enter a numerical value only.")
        return

    cursor_object.execute("SELECT Name, Team, Goals FROM Top_Scorers ORDER BY Goals DESC LIMIT ?", (no_of_scorers,))

    for row in cursor_object:
        print(row)
    print()

def top_assisters(connection, cursor_object):
    no_of_assisters = input("Enter the maximum number of top assisters you want to see: ")
    try:
        int(no_of_assisters)
    except:
        print("Please enter a numerical value only.")
        return

    cursor_object.execute("SELECT Name, Team, Assists FROM Top_Scorers ORDER BY Assists DESC LIMIT ?", (no_of_assisters,))

    for row in cursor_object:
        print(row)
    print()

# Average goals/assists per person for each team in the database.
def averages(connection, cursor_object):
    cursor_object.execute("SELECT Team, ROUND(AVG(Goals),2), ROUND(AVG(Assists),2), COUNT(Name) FROM Top_Scorers GROUP BY Team")

    summary_list = []
    headings = ["team", "average_goals", "average_assists", "no_of_players"]

    for row in cursor_object:
        team_dict = {}

        team_dict = dict(zip(headings,row)) # Note that you can zip any 2 sequences together, they don't have to be the same data type (here I'm zipping the list "headings" with the tuple "row")
        summary_list.append(team_dict)

    summary_list.sort(key=sort_averages_goals, reverse=True)
    pprint.pprint(summary_list)
    print()

def sort_averages_goals(dict):  # Allows sorting of the list of dictionaries of averages for each team by average goals.
    return(dict["average_goals"])

# A weighted score for each team (ranked and sorted).
def team_score(connection, cursor_object):
    goals_score = input("Enter the number of points to award per goal: ")
    assist_score = input("Enter the number of points to award per assist: ")
    try:
        goals_score = float(goals_score)
        assist_score = float(assist_score)
    except:
        print("Please enter numerical values only.")
        return

    cursor_object.execute("SELECT Team, SUM(Goals), SUM(Assists), ROUND(((?*SUM(Goals))+(?*SUM(Assists)))/COUNT(Name),2) AS Team_Score FROM Top_Scorers GROUP BY Team ORDER BY Team_Score DESC", (goals_score, assist_score)) # Need to multiply by "3.0" rather than by "3" or else it just return an integer score number (I want to include decimals).

    for row in cursor_object:
        print(row)
    print()


###### START HERE: 1) Visualise the data using these output functions and TKinter. Assign actions (such as reseting the database) to buttons. ######


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

    # Update the database?
    while True:
        update = input('Update Tables? (Enter "Y" or "N"): ')

        if update == 'Y' or update == 'y':
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
            print_info = input("Print the player information to the Terminal? (Enter 'Yes' or 'Y' if required): ")

            # Add an empty line for neatness.
            print()

            # Run the main program.
            for team, no_of_players in search_list:
                team_data(team, no_of_players, conn, cur, print_info)

            break

        elif update == 'N' or update == 'n':
            break
        else:
            print('Please enter "Y" or "N" only')

    # Show results summaries?
    while True:
        results = input('Show results summaries? (Enter "Y" or "N"): ')

        if results == 'Y' or results == 'y':
            summary(conn, cur)
            top_scorers(conn, cur)
            top_assisters(conn, cur)
            averages(conn, cur)
            team_score(conn, cur)
            break
        elif reset == 'N' or reset == 'n':
            break
        else:
            print('Please enter "Y" or "N" only')
