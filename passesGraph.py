import time
import pandas as pd
from nba_api.stats.endpoints import playerdashptpass
from nba_api.stats.static import players, teams
import networkx as nx

player_data = pd.read_csv('final_data.csv')
player_data = player_data[['Player', 'Season', 'Team']]
def get_player_id(name):
    # Find players by name
    player_dict = players.find_players_by_full_name(name)
    if player_dict:
        # Assuming you want the first match
        return player_dict[0]['id']
    else:
        return "Player not found"
def get_team_id(abbreviation):
    # Find teams by abbreviation
    team_dict = teams.find_team_by_abbreviation(abbreviation)
    if team_dict:
        return team_dict['id']
    else:
        return "Team not found"


def fetch_passing_stats(player_id, team_id, season):
    attempt = 0
    max_attempts = 2
    empty_df = pd.DataFrame()  # Predefined empty DataFrame for failure cases
    while attempt < max_attempts:
        try:
            # Fetch passing stats from NBA API
            pass_stats = playerdashptpass.PlayerDashPtPass(team_id=team_id, player_id=player_id, season=season,
                                                           per_mode_simple='Totals')
            made = pass_stats.get_data_frames()[0]  # Assuming the first DataFrame contains the relevant data
            received = pass_stats.get_data_frames()[1]

            # Check if the necessary columns exist
            if 'PASS_TEAMMATE_PLAYER_ID' in made.columns and 'PASS' in made.columns:
                # Return filtered DataFrames
                return (
                    made[['PLAYER_NAME_LAST_FIRST', 'PASS_TO', 'PASS', 'TEAM_ABBREVIATION']],
                    received[['PLAYER_NAME_LAST_FIRST', 'PASS_FROM', 'PASS', 'TEAM_ABBREVIATION']]
                )
            else:
                print(
                    f"Columns not found in DataFrame for Player ID: {player_id}, Team ID: {team_id}, Season: {season}")
                return empty_df, empty_df  # Return empty DataFrames to maintain output consistency
        except Exception as e:
            print(
                f"Attempt {attempt + 1}: Failed to fetch data for Player ID: {player_id}, Team ID: {team_id}, Season: {season}")
            print(f"Error: {e}")
            time.sleep(2 ** attempt)  # Exponential back-off
            attempt += 1

    return empty_df, empty_df

def add_data(player_data):
    passing_data = pd.DataFrame()
    for index, row in player_data.iterrows():
        df_made,df_received = fetch_passing_stats(player_id=get_player_id(row['Player']), season=row['Season'], team_id=get_team_id(row['Team']))
        df_made.rename(columns={'PASS_TO': 'PARTNER', 'PASS': 'PASSES_MADE'}, inplace=True)
        df_received.rename(columns={'PASS_FROM': 'PARTNER', 'PASS': 'PASSES_RECEIVED'}, inplace=True)

        # Merge the DataFrames on PARTNER and TEAM_ABBREVIATION
        print(df_made.columns,df_received.columns)
        if not df_received.empty or not df_made.empty :
         total_passes = pd.merge(df_made, df_received, on=['PLAYER_NAME_LAST_FIRST', 'PARTNER', 'TEAM_ABBREVIATION'],
                                how='outer')

         total_passes.fillna(0, inplace=True)

            # Calculate the total passes exchanged
         total_passes['TOTAL_PASSES'] = total_passes['PASSES_MADE'] + total_passes['PASSES_RECEIVED']
        passing_data = pd.concat([passing_data,total_passes], ignore_index=True)
    return passing_data

# passes_graph_data = add_data(player_data)
# passes_graph_data.to_csv('passes_graph.csv',index = False)

nodes = pd.read_csv('passes_graph.csv')
nodes = nodes.drop_duplicates()

# # Create an empty undirected graph
# G = nx.Graph()
# # Add edges with attributes
# for _, row in nodes.iterrows():
#     G.add_edge(row['PLAYER_NAME_LAST_FIRST'], row['PARTNER'], total_passes=row['TOTAL_PASSES'], team=row['TEAM_ABBREVIATION'])
# print(G['Player A']['Player B'])  # Output the attributes of the edge between 'Player A' and 'Player B'
#
# nx.write_graphml(G, "network_data.graphml")

