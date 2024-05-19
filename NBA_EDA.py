import pandas as pd
import numpy as np
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import playerdashptpass
import random
import time

def mean_round(series, decimals=2):
    return np.round(series.mean(), decimals)
def calculate_data(data):
    # Group by 'Player', 'Season', and 'Team'
    grouped = data.groupby(['Player', 'Season', 'Team'])

    aggregated_data = grouped.agg({
        'Game Score': lambda x: mean_round(x),
        'Points': lambda x: mean_round(x),
        'Assists': lambda x: mean_round(x),
        'Rebounds': lambda x: mean_round(x),
        'Steals': lambda x: mean_round(x),
        'Blocks': lambda x: mean_round(x),
        'Turnovers': lambda x: mean_round(x),
        'Personal Fouls': lambda x: mean_round(x),
        'Minutes Played': lambda x: mean_round(x),
        'Field Goals Made': lambda x: mean_round(x),
        'Field Goals Attempted': lambda x: mean_round(x),
        'Field Goals Percentage': lambda x: mean_round(x),
        'Three Points Made': lambda x: mean_round(x),
        'Three Points Attempted': lambda x: mean_round(x),
        'Three Points Percentage': lambda x: mean_round(x),
        'Free Throws Made': lambda x: mean_round(x),
        'Free Throws Attempted': lambda x: mean_round(x),
        'Free Throws Percentage': lambda x: mean_round(x),
        'Offensive Rebounds': lambda x: mean_round(x),
        'Defensive Rebounds': lambda x: mean_round(x),
        'Plus Minus': lambda x: mean_round(x),
        'Starter': lambda x: np.round(np.mean(x) * 100, 2)
    })
    # Add non-aggregatable data by taking the first occurrence
    non_agg_data = grouped[['Number', 'Position', 'Height', 'Weight', 'Birth Date', 'Country', 'Years Experience', 'College', 'Player URL', 'Draft Round', 'Draft Pick in Round', 'Draft Overall Pick']].first()
    # Combine the aggregated data and the non-aggregatable data
    final_df = pd.concat([aggregated_data, non_agg_data], axis=1)
    # Reset index to make 'Player', 'Season', and 'Team' columns again
    final_df.reset_index(inplace=True)
    return final_df
def convert_minutes(time_str):
    if ':' in time_str:
        minutes, seconds = time_str.split(':')
        return round(int(minutes) + int(seconds) / 60,2)
    return 0.0  # Return 0 if no ':' found (or handle other cases as needed)
def data_cleaning(data):
    # Fill 'College' with 'None' for missing values
    data['College'].fillna('None', inplace=True)
    # Calculate percentages where missing, or fill with 0 where appropriate
    data['Field Goals Percentage'] = data.apply(lambda x: round(x['Field Goals Made'] / x['Field Goals Attempted'], 3) if x['Field Goals Attempted'] > 0 else 0, axis=1)
    data['Three Points Percentage'] = data.apply(lambda x: round(x['Three Points Made'] / x['Three Points Attempted'], 3) if x['Three Points Attempted'] > 0 else 0, axis=1)
    data['Free Throws Percentage'] = data.apply(lambda x: round(x['Free Throws Made'] / x['Free Throws Attempted'], 3) if x['Free Throws Attempted'] > 0 else 0,axis=1)
    # Draft information handling
    data['Draft Round'].fillna(0, inplace=True)
    data['Draft Pick in Round'].fillna(0, inplace=True)
    data['Draft Overall Pick'].fillna(0, inplace=True)
    # Handle 'Plus Minus'
    data['Plus Minus'].fillna(0, inplace=True)

    return data
def calculate_wins_losses(data):
    # Define a custom function to process the Game Result and count wins/losses
    def process_game_result(x):
        wins = sum(1 for result in x if 'W' in result)
        losses = sum(1 for result in x if 'L' in result)
        return pd.Series({'Total Wins': wins, 'Total Losses': losses})

    # Group by Player, Season, and Team to calculate wins and losses
    grouped = data.groupby(['Player', 'Season', 'Team'])
    win_loss_data = grouped['Game Result'].apply(process_game_result).reset_index()
    return win_loss_data
def add_win_loss(data):
    calc_data = calculate_wins_losses(data)
    data = calculate_data(data)
    wins_losses_pivot = calc_data.pivot_table(index=['Player', 'Season', 'Team'],
                                                       columns='level_3',
                                                       values='Game Result',
                                                       fill_value=0).reset_index()

    # Rename the columns for clarity
    wins_losses_pivot.columns = ['Player', 'Season', 'Team', 'Total Losses', 'Total Wins']
    # Merge the pivoted DataFrame with your main data
    final_data = pd.merge(data, wins_losses_pivot, on=['Player', 'Season', 'Team'], how='left')

    # Optionally, fill NaN values if any
    final_data['Total Wins'] = final_data['Total Wins'].fillna(0)
    final_data['Total Losses'] = final_data['Total Losses'].fillna(0)
    return final_data


data = pd.read_csv('transfers.csv')
data.drop_duplicates(subset=['Player', 'Season', 'Team', 'Game Date'], keep='first', inplace=True)
data.to_csv('cleaned_data.csv', index=False)
data['Minutes Played'] = data['Minutes Played'].apply(convert_minutes)
data_clean = data_cleaning(data)
data_clean = add_win_loss(data)

def preprocess_full_data(full_data):
    # Convert game date to datetime and sort
    full_data['Game Date'] = pd.to_datetime(full_data['Game Date'])
    full_data.sort_values(['Player', 'Season', 'Team', 'Game Date'], inplace=True)
    return full_data
def calculate_wins_losses_first_games(full_data):
    # Check if each game is a win or a loss
    full_data['Win'] = full_data['Game Result'].apply(lambda x: 1 if 'W' in x else 0)
    full_data['Loss'] = full_data['Game Result'].apply(lambda x: 1 if 'L' in x else 0)

    # Group by player, season, team, and calculate wins and losses for the first 5, 10, 15 games
    grouped = full_data.groupby(['Player', 'Season', 'Team'])
    full_data['Wfirst5'] = grouped['Win'].transform(lambda x: x.head(5).sum())
    full_data['Wfirst10'] = grouped['Win'].transform(lambda x: x.head(10).sum())
    full_data['Wfirst15'] = grouped['Win'].transform(lambda x: x.head(15).sum())
    full_data['Lfirst5'] = grouped['Loss'].transform(lambda x: x.head(5).sum())
    full_data['Lfirst10'] = grouped['Loss'].transform(lambda x: x.head(10).sum())
    full_data['Lfirst15'] = grouped['Loss'].transform(lambda x: x.head(15).sum())

    # Select relevant columns and drop duplicates to ensure each player-season-team combination is unique
    return full_data[['Player', 'Season', 'Team', 'Wfirst5', 'Lfirst5', 'Wfirst10', 'Lfirst10', 'Wfirst15',
                      'Lfirst15']].drop_duplicates()
def add_wins_losses_to_aggregated_data(aggregated_data, wins_losses_first_games):
    # Merge the wins and losses data with the aggregated stats
    final_data = pd.merge(aggregated_data, wins_losses_first_games, on=['Player', 'Season', 'Team'], how='left')
    return final_data



full_data = preprocess_full_data(data)
wins_losses_first_games = calculate_wins_losses_first_games(data)
final_aggregated_data = add_wins_losses_to_aggregated_data(data_clean, wins_losses_first_games)




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
    max_attempts = 5
    while attempt < max_attempts:
        try:
            pass_stats = playerdashptpass.PlayerDashPtPass(team_id=team_id, player_id=player_id, season=season, per_mode_simple='PerGame')
            return pass_stats.get_data_frames()[0]  # Assuming this is the correct DataFrame
        except Exception as e:
            print(f"Attempt {attempt + 1}: Failed to fetch data for Player ID: {player_id}, Team ID: {team_id}, Season: {season}")
            print(f"Error: {e}")
            time.sleep(2 ** attempt)  # Exponential back-off
            attempt += 1
    return pd.DataFrame()  # Return empty DataFrame after all retries fail
def process_passing_stats(data):
    # Create a DataFrame to hold all the passing data
    all_passing_data = pd.DataFrame()
    for index, row in data.iterrows():
        player_name = row['Player']
        team_abbreviation = row['Team']
        season = row['Season']

        player_id = get_player_id(player_name)
        team_id = get_team_id(team_abbreviation)
        print(player_id,team_id , season)
        # Fetch passing data for each row
        time.sleep(random.randint(1, 3))
        passing_data = fetch_passing_stats(player_id, team_id, season)
        if not passing_data.empty:
            passing_data['Player'] = player_name  # Add player name to the DataFrame
            passing_data['Season'] = season       # Add season to the DataFrame
            passing_data['Team'] = team_abbreviation  # Add team to the DataFrame
            # Append the results to the all_passing_data DataFrame
            all_passing_data = pd.concat([all_passing_data, passing_data], ignore_index=True)

    return all_passing_data
# def reshape_passing_data(data):
#     # Create a new column for the 'made_pass' and 'made_freq' identifiers for each teammate
#     data['made_pass_col'] = 'made_pass_' + data['PASS_TO'].str.replace(' ', '_')
#     data['made_freq_col'] = 'made_freq_' + data['PASS_TO'].str.replace(' ', '_')
#
#     # Pivot the table to have dynamic columns based on the 'PASS_TO' field
#     pass_pivot = data.pivot_table(index=['PLAYER_NAME_LAST_FIRST', 'Season', 'Team'],
#                                   columns='made_pass_col',
#                                   values='PASS',
#                                   aggfunc='sum',
#                                   fill_value=0)
#
#     freq_pivot = data.pivot_table(index=['PLAYER_NAME_LAST_FIRST', 'Season', 'Team'],
#                                   columns='made_freq_col',
#                                   values='FREQUENCY',
#                                   aggfunc='mean',
#                                   fill_value=0)
#
#     # Merge the pivoted data frames on the index
#     combined_pivot = pd.concat([pass_pivot, freq_pivot], axis=1).reset_index()
#
#     # Renaming columns for clarity
#     combined_pivot.columns = [col.replace(' ', '_') for col in combined_pivot.columns]
#
#     return combined_pivot


def reshape_passing_data(data):
    # Define a function to calculate average passes
    def average_total_passes(group):
        total_passes = group['PASS'].sum()
        number_of_entries = len(group)
        return total_passes / number_of_entries if number_of_entries > 0 else 0

    # Group by Player, Season, and Team and apply the function
    avg_passes_data = data.groupby(['Player', 'Season', 'Team']).apply(average_total_passes).reset_index()
    avg_passes_data.columns = ['Player', 'Season', 'Team', 'Avg_Total_Passes']

    return avg_passes_data

df1 = pd.read_csv('pass1.csv')

# passing_stats = process_passing_stats(final_aggregated_data)
# test = reshape_passing_data(passing_stats)
# test.to_csv('pass1.csv',index = False)


def add_passes(final_data,passes):
    passes['Avg_Total_Passes'] = passes['Avg_Total_Passes'].round(2)
    combined_df = pd.merge(final_data, passes, on=['Player', 'Season', 'Team'], how='left')
    combined_df.fillna(value=0, inplace=True)
    return combined_df



final_aggregated_data = add_passes(final_aggregated_data,df1)
final_aggregated_data.to_csv('final_data.csv', index=False)

print(final_aggregated_data.columns)

