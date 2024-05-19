import logging
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
import re
import pandas as pd
from urllib.parse import urlparse, parse_qs
import time
import random
import nba_api as nba
import os

base_url = 'https://www.basketball-reference.com/teams/'

def generate_team_url(team, year):
    return f"{base_url}{team}/{year}.html#all_roster"
def playerGamesStats(url, player_info):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Find all <tr> elements where id starts with 'pgl_basic'
    tr_tags = soup.find_all('tr', id=re.compile(r'^pgl_basic\.\d+$'))
    # Prepare to store the results
    all_stats = []
    season = extractSeason(soup)
    draft_info = extractPick(soup)
    for tr in tr_tags:
        # Extracting specific stats for each row
        stats = {
            "Game Score": tr.find('td', {"data-stat": "game_score"}).text,
            "Game Season": tr.find('td', {"data-stat": "game_season"}).text,
            "Points": tr.find('td', {"data-stat": "pts"}).text,
            "Assists": tr.find('td', {"data-stat": "ast"}).text,
            "Rebounds": tr.find('td', {"data-stat": "trb"}).text,
            "Steals": tr.find('td', {"data-stat": "stl"}).text,
            "Blocks": tr.find('td', {"data-stat": "blk"}).text,
            "Turnovers": tr.find('td', {"data-stat": "tov"}).text,
            "Personal Fouls": tr.find('td', {"data-stat": "pf"}).text,
            "Minutes Played": tr.find('td', {"data-stat": "mp"}).text,
            "Field Goals Made": tr.find('td', {"data-stat": "fg"}).text,
            "Field Goals Attempted": tr.find('td', {"data-stat": "fga"}).text,
            "Field Goals Percentage": tr.find('td', {"data-stat": "fg_pct"}).get_text(strip=True, separator=" "),
            "Three Points Made": tr.find('td', {"data-stat": "fg3"}).text,
            "Three Points Attempted": tr.find('td', {"data-stat": "fg3a"}).text,
            "Three Points Percentage": tr.find('td', {"data-stat": "fg3_pct"}).get_text(strip=True, separator=" "),
            "Free Throws Made": tr.find('td', {"data-stat": "ft"}).text,
            "Free Throws Attempted": tr.find('td', {"data-stat": "fta"}).text,
            "Free Throws Percentage": tr.find('td', {"data-stat": "ft_pct"}).get_text(strip=True, separator=" "),
            "Offensive Rebounds": tr.find('td', {"data-stat": "orb"}).text,
            "Defensive Rebounds": tr.find('td', {"data-stat": "drb"}).text,
            "Plus Minus": tr.find('td', {"data-stat": "plus_minus"}).text,
            "Opponent": tr.find('td', {"data-stat": "opp_id"}).text,
            "Location": 'A' if tr.find('td', {"data-stat": "game_location"}).text.strip() == '@' else 'H',
            "Game Date": tr.find('td', {"data-stat": "date_game"}).get_text(strip=True, separator=" "),
            "Age": tr.find('td', {"data-stat": "age"}).get_text(strip=True, separator=" "),
            "Team": tr.find('td', {"data-stat": "team_id"}).get_text(strip=True, separator=" "),
            "Game Result": tr.find('td', {"data-stat": "game_result"}).get_text(strip=True, separator=" "),
            "Starter": tr.find('td', {"data-stat": "gs"}).get_text(strip=True, separator=" "),
            "Season": season,
            "Draft Round": draft_info.get("Round", "N/A"),
            "Draft Pick in Round": draft_info.get("Pick in Round", "N/A"),
            "Draft Overall Pick": draft_info.get("Overall Pick", "N/A")

        }
        combined_stats = {**player_info, **stats}
        all_stats.append(combined_stats)
    return pd.DataFrame(all_stats)
def allPlayersStats(url,year):
    response = requests.get(url)
    if response.status_code != 200:
        logging.error(f"Failed to load URL {url} with status code {response.status_code}")
        return pd.DataFrame()
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'roster'})
    if table is None:
        logging.error(f"No table found in URL {url}")
        return pd.DataFrame()
    # Extract rows
    rows = table.find_all('tr')
    data = []

    # Base URL for constructing full player URLs
    base_url = 'https://www.basketball-reference.com'

    # Extract data from each row
    for row in rows:
        cols = row.find_all(['th', 'td'])
        player_url = cols[1].find('a')['href'] if cols[1].find('a') else None
        full_url = base_url + player_url.replace('.html', f'/gamelog/{year}') if player_url else None
        data.append({
            'Number': cols[0].text.strip(),
            'Player': cols[1].text.strip(),
            'Position': cols[2].text.strip(),
            'Height': cols[3].text.strip(),
            'Weight': cols[4].text.strip(),
            'Birth Date': cols[5].text.strip(),
            'Country': cols[6].find('span').get('class')[1][2:] if cols[6].find('span') else '',
            'Years Experience': cols[7].text.strip(),
            'College': cols[8].text.strip() if cols[8].find('a') else 'None',
            'Player URL': full_url,
        })

    # Convert to DataFrame
    df = pd.DataFrame(data)
    return df
def extractSeason(soup):
    title_tag = soup.find('title')
    if title_tag:
        title_text = title_tag.text
        # Pattern to find the season format "YYYY-YY"
        match = re.search(r'\b(\d{4}-\d{2})\b', title_text)
        if match:
            return match.group(1)  # This will return the season "2022-23"
    return None  # Return None if no season is found
def extractAllTeams(teams, years):
        all_player_game_stats = []
        for year in tqdm(years, desc="Processing Years", leave=True):
            for team in tqdm(teams, desc=f"Teams in {year}", leave=False):
                url = generate_team_url(team, year)
                # Wait before fetching team data
                roster_df = allPlayersStats(url, year)
                time.sleep(random.randint(5, 10))  # Sleeping before making the request
                if roster_df.empty:
                    print(f"No players found for team {team} in year {year}")
                    continue
                for index, player_info in roster_df.iterrows():
                    if player_info['Player URL']:
                        # Wait before fetching each player's game stats
                        time.sleep(random.randint(2, 5))  # Sleeping before fetching player stats
                        player_game_stats_df = playerGamesStats(player_info['Player URL'], player_info)
                        all_player_game_stats.append(player_game_stats_df)
                print(f"finish season:{year}")
        if not all_player_game_stats:
            return pd.DataFrame()  # Return empty DataFrame if no data collected
        return pd.concat(all_player_game_stats, ignore_index=True)
def extractPick(soup):
    draft_element = soup.find('strong', string=lambda text: text and 'Draft:' in text)
    if draft_element:
        a_tag = draft_element.find_next('a')
        if a_tag:
            draft_info = a_tag.next_sibling.strip()
            match = re.search(r'(\d+)\w+ round \((\d+)\w+ pick, (\d+)\w+ overall\)', draft_info)
            if match:
                return {
                    "Round": match.group(1),
                    "Pick in Round": match.group(2),
                    "Overall Pick": match.group(3)
                }
            else:
                return {"error": "Draft information could not be parsed correctly."}
        else:
            return {"error": "No <a> tag found after the draft indicator."}
    else:
        return {"error": "Draft element not found."}
def doubleTeam(df):
    team_changes = df.groupby(['Player', 'Season'])['Team'].nunique()

    # Convert the GroupBy object to a DataFrame
    team_changes = team_changes.reset_index()
    team_changes.rename(columns={'Team': 'num_teams'}, inplace=True)

    # Create a new column 'moved' that indicates if a player has moved (num_teams > 1)
    team_changes['moved'] = team_changes['num_teams'] > 1

    # Merge this information back to the original DataFrame
    df = pd.merge(df, team_changes[['Player', 'Season', 'moved']], on=['Player', 'Season'], how='left')
    return df

def concatenate_csv_files(directory):
    # List to hold dataframes
    dfs = []

    # Iterate over each file in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):  # Check if the file is a CSV
            file_path = os.path.join(directory, filename)
            df = pd.read_csv(file_path)
            dfs.append(df)  # Append the dataframe to the list

    # Concatenate all dataframes in the list
    combined_df = pd.concat(dfs, ignore_index=True)

    # Save the combined dataframe to a new CSV file
    combined_df.to_csv(os.path.join(directory, 'combined_csv_files.csv'), index=False)

# Usage
directory_path = '/Users/ohadkiperman/PycharmProjects/pythonProject/nbaTransfers/'  # Update this to the path of your CSV files
concatenate_csv_files(directory_path)









