import requests
from flask import Flask, render_template
from flask_socketio import SocketIO
import time
import pandas as pd

player_ids_df = pd.read_csv('player_ids.csv',header=None)
player_ids = {player_ids_df.iloc[i][0]:player_ids_df.iloc[i][1] for i in range(len(player_ids_df))}

app = Flask(__name__)
socketio = SocketIO(app)

PLAYER_ID = 237
season_year = 2022
start_date = '2023-04-10'


@app.template_filter()
def length(obj):
    return len(obj)

app.jinja_env.filters['length'] = length

# def get_player_stats():
#     response = requests.get(f"https://www.balldontlie.io/api/v1/stats?player_ids[]={PLAYER_ID}&postseason=True")
#     data = response.json()["data"]
#     stats = []
#     for game in data:
#         game_stats = {}
#         game_stats["game_date"] = game["game"]["date"]
#         game_stats["points"] = game["pts"]
#         stats.append(game_stats)
#     return stats


def get_player_stats(names):
    player_stats = []
    for player_name in names:
        print(player_name)
        # Search for the player by name
        # response = requests.get(f"https://www.balldontlie.io/api/v1/players?search={player_name}")
        # print("RESPONSE",response.status_code)
        # if response.status_code != 200:
        #     print(f"Error searching for player {player_name}: {response.json()}")
        #     continue
        #
        # # Get the player ID from the search results
        # search_results = response.json()["data"]
        # if len(search_results) == 0:
        #     print(f"No results found for player {player_name}")
        #     continue
        # player_id = search_results[0]["id"]

        # Get the player's stats
        response = requests.get(f"https://www.balldontlie.io/api/v1/stats?seasons[]={season_year}&start_date[]={start_date}&player_ids[]={player_ids[player_name]}&postseason=true")
        if response.status_code != 200:
            print(f"Error getting stats for player {player_name}: {response.json()}")
            continue

        # Add the player's stats to the list
        player_stats += response.json()["data"]

    return player_stats

def get_all_player_stats():
    response = requests.get(f"https://www.balldontlie.io/api/v1/stats?seasons[]={season_year}&postseason=True")
    data = response.json()["data"]
    print(data)
    stats = []
    for game in data:
        game_stats = {}
        game_stats["game_date"] = game["game"]["date"]
        game_stats["points"] = game["pts"]
        stats.append(game_stats)
    return stats
# player_stats = []
# for player_name in names:
#     # Search for the player by name
#     response = requests.get(f"https://www.balldontlie.io/api/v1/players?search={player_name}")
#     if response.status_code != 200:
#         print(f"Error searching for player {player_name}: {response.json()}")
#         continue
#
#     # Get the player ID from the search results
#     search_results = response.json()["data"]
#     if len(search_results) == 0:
#         print(f"No results found for player {player_name}")
#         continue
#     player_id = search_results[0]["id"]
#
#     # Get the player's stats
#     response = requests.get(f"https://www.balldontlie.io/api/v1/stats?seasons[]={season_year}&start_date[]={start_date}&player_ids[]={player_id}&postseason=true")
#     if response.status_code != 200:
#         print(f"Error getting stats for player {player_name}: {response.json()}")
#         continue
#
#     # Add the player's stats to the list
#     player_stats += response.json()["data"]
#
# return player_stats

# @app.route('/')
# def home():
#     stats = get_player_stats()
#     cumulative_points = 0
#     for game in stats:
#         cumulative_points += game["points"]
#         game["cumulative_points"] = cumulative_points
#     return render_template('index.html', stats=stats)

# @app.route('/')
# def home():
#     stats = get_player_stats()
#     cumulative_points = 0
#     for game in stats:
#         cumulative_points += game["points"]
#         game["cumulative_points"] = cumulative_points
#     player_stats = [{"name": "Player Name", "cumulative_points": cumulative_points}]
#     return render_template('index.html', players=player_stats)


import csv


@app.route('/')
def home():
    owner_names = []
    player_names = []
    play_in_points = []

    teams = {}

    # Read the CSV file containing player names
    with open('2023_minigame.csv') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
           if "*" in row[0]:
               owner_names.append(row[0])
               owner_name = row[0]
               teams[owner_name] = []
           else:
               player_names.append(row[0])
               play_in_points.append(row[1])
               teams[owner_name].append(row[0])
        # owner_names = [row[0] for row in reader if "*" in row[0]]
        # player_names = [row[0] for row in reader if "*" not in row[0]]
        # play_in_points = [row[1] for row in reader]

        print(owner_names)
        print(len(player_names))
        print(play_in_points)
        print(teams)

    # get_all_player_stats()
    # print("################################################################################")
    # Get the player stats from the API
    stats = get_player_stats(player_names)

    # Initialize a dictionary to store the cumulative points for each player
    # player_cumulative_points = {name: 0 for name in player_names}
    player_cumulative_points = {}
    for n in range(len(player_names)):
        player_cumulative_points[player_names[n]] = int(play_in_points[n])

    # Calculate the cumulative points for each player
    for game in stats:
        # print(game)
        # print(game.keys())
        player_name = game["player"]["first_name"]+" "+game["player"]["last_name"]

        if player_name in player_cumulative_points:
            player_cumulative_points[player_name] += game["pts"]

    # Create a list of dictionaries containing the player name and cumulative points
    player_stats = [{"name": name, "pts": player_cumulative_points[name]} for name in player_names]
    print(teams)
    print(player_stats)

    final_teams = {}

    for t in teams:
        final_teams[t] = {}
        team_total = 0
        for player in teams[t]:
            final_teams[t][player] = player_cumulative_points[player]
            team_total += player_cumulative_points[player]

        final_teams[t]['team_total'] = team_total

    print(final_teams)


    # Render the HTML template with the player stats
    return render_template('index.html', players=final_teams)


if __name__ == '__main__':
    socketio.run(app, debug=True)
