
import pandas as pd
import folium
from folium.features import CustomIcon
from folium.plugins import PolyLineTextPath
import numpy as np
import os

# Mapping of NBA team abbreviations to their respective cities
team_city_map = {
    'ATL': 'Atlanta, GA',
    'BOS': 'Boston, MA',
    'BKN': 'Brooklyn, NY',
    'CHA': 'Charlotte, NC',
    'CHI': 'Chicago, IL',
    'CLE': 'Cleveland, OH',
    'DAL': 'Dallas, TX',
    'DEN': 'Denver, CO',
    'DET': 'Detroit, MI',
    'GSW': 'San Francisco, CA',
    'HOU': 'Houston, TX',
    'IND': 'Indianapolis, IN',
    'LAC': 'Los Angeles, CA',
    'LAL': 'Los Angeles, CA',
    'MEM': 'Memphis, TN',
    'MIA': 'Miami, FL',
    'MIL': 'Milwaukee, WI',
    'MIN': 'Minneapolis, MN',
    'NOP': 'New Orleans, LA',
    'NYK': 'New York, NY',
    'OKC': 'Oklahoma City, OK',
    'ORL': 'Orlando, FL',
    'PHI': 'Philadelphia, PA',
    'PHX': 'Phoenix, AZ',
    'POR': 'Portland, OR',
    'SAC': 'Sacramento, CA',
    'SAS': 'San Antonio, TX',
    'TOR': 'Toronto, ON',
    'UTA': 'Salt Lake City, UT',
    'WAS': 'Washington, D.C.'
}
# Adding coordinates for Washington, D.C. to teams_coords
teams_coords = {
    'ATL': {'lat': 33.74735946504758, 'lon': -84.38854768473595},
    'BOS': {'lat': 42.35889807366554, 'lon': -71.04926109007948},
    'BKN': {'lat': 40.71317024948951, 'lon': -74.00027581460759},
    'CHA': {'lat': 35.22323775016379, 'lon': -80.85151605566169},
    'CHI': {'lat': 41.8760646493357, 'lon': -87.63241329906266},
    'CLE': {'lat': 41.50409978309838, 'lon': -81.69625992591952},
    'DAL': {'lat': 32.77380425465012, 'lon': -96.79473844766095},
    'DEN': {'lat': 39.74046675788151, 'lon': -104.98558743568462},
    'DET': {'lat': 42.33127691860287, 'lon': -83.03535981552895},
    'GSW': {'lat': 37.77341279262239, 'lon': -122.41048092955603},
    'HOU': {'lat': 29.75717646690923, 'lon': -95.37800555205185},
    'IND': {'lat': 39.7754462830884, 'lon': -86.15404934597622},
    'LAC': {'lat': 34.06328148623558, 'lon': -118.2524881009208},
    'LAL': {'lat': 33.56328148623558, 'lon': -118.2524881009208},
    'MEM': {'lat': 35.14816589941664, 'lon': -90.0408922968572},
    'MIA': {'lat': 25.76352490498945, 'lon': -80.1834570557793},
    'MIL': {'lat': 43.03669785829397, 'lon': -87.89335134479263},
    'MIN': {'lat': 44.97722503578261, 'lon': -93.26628811368671},
    'NOP': {'lat': 29.952609837351886, 'lon': -90.06179284932885},
    'NYK': {'lat': 40.710553418765095, 'lon': -74.00857253087082},
    'OKC': {'lat': 35.478844955079445, 'lon': -97.53693201972237},
    'ORL': {'lat': 28.531759394883284, 'lon': -81.37495267131123},
    'PHI': {'lat': 39.940995575125044, 'lon': -75.1744920480092},
    'PHX': {'lat': 33.44584636405516, 'lon': -112.07704345491207},
    'POR': {'lat': 45.51565795455857, 'lon': -122.66539963693144},
    'SAC': {'lat': 38.5761136616792, 'lon': -121.47586311167005},
    'SAS': {'lat': 29.421092659029753, 'lon': -98.46499823596957},
    'TOR': {'lat': 43.6580438148729, 'lon': -79.38493708454081},
    'UTA': {'lat': 40.76088977027471, 'lon': -111.87929946879744},
    'WAS': {'lat': 38.90708489692374, 'lon': -77.03380471557976}

}
team_colors = {
    'ATL': '#E03A3E',  # Atlanta Hawks
    'BOS': '#007A33',  # Boston Celtics
    'BKN': '#000000',  # Brooklyn Nets
    'CHA': '#1D1160',  # Charlotte Hornets
    'CHI': '#CE1141',  # Chicago Bulls
    'CLE': '#860038',  # Cleveland Cavaliers
    'DAL': '#00538C',  # Dallas Mavericks
    'DEN': '#0E2240',  # Denver Nuggets
    'DET': '#C8102E',  # Detroit Pistons
    'GSW': '#1D428A',  # Golden State Warriors
    'HOU': '#CE1141',  # Houston Rockets
    'IND': '#002D62',  # Indiana Pacers
    'LAC': '#C8102E',  # Los Angeles Clippers
    'LAL': '#552583',  # Los Angeles Lakers
    'MEM': '#5D76A9',  # Memphis Grizzlies
    'MIA': '#98002E',  # Miami Heat
    'MIL': '#00471B',  # Milwaukee Bucks
    'MIN': '#0C2340',  # Minnesota Timberwolves
    'NOP': '#0C2340',  # New Orleans Pelicans
    'NYK': '#006BB6',  # New York Knicks
    'OKC': '#007AC1',  # Oklahoma City Thunder
    'ORL': '#0077C0',  # Orlando Magic
    'PHI': '#006BB6',  # Philadelphia 76ers
    'PHX': '#1D1160',  # Phoenix Suns
    'POR': '#E03A3E',  # Portland Trail Blazers
    'SAC': '#5A2D81',  # Sacramento Kings
    'SAS': '#C4CED4',  # San Antonio Spurs
    'TOR': '#CE1141',  # Toronto Raptors
    'UTA': '#002B5C',  # Utah Jazz
    'WAS': '#002B5C',  # Washington Wizards
}
team_names = {
    'ATL': 'Atlanta Hawks',
    'BOS': 'Boston Celtics',
    'BKN': 'Brooklyn Nets',
    'CHA': 'Charlotte Hornets',
    'CHI': 'Chicago Bulls',
    'CLE': 'Cleveland Cavaliers',
    'DAL': 'Dallas Mavericks',
    'DEN': 'Denver Nuggets',
    'DET': 'Detroit Pistons',
    'GSW': 'Golden State Warriors',
    'HOU': 'Houston Rockets',
    'IND': 'Indiana Pacers',
    'LAC': 'LA Clippers',
    'LAL': 'Los Angeles Lakers',
    'MEM': 'Memphis Grizzlies',
    'MIA': 'Miami Heat',
    'MIL': 'Milwaukee Bucks',
    'MIN': 'Minnesota Timberwolves',
    'NOP': 'New Orleans Pelicans',
    'NYK': 'New York Knicks',
    'OKC': 'Oklahoma City Thunder',
    'ORL': 'Orlando Magic',
    'PHI': 'Philadelphia 76ers',
    'PHX': 'Phoenix Suns',
    'POR': 'Portland Trail Blazers',
    'SAC': 'Sacramento Kings',
    'SAS': 'San Antonio Spurs',
    'TOR': 'Toronto Raptors',
    'UTA': 'Utah Jazz',
    'WAS': 'Washington Wizards'
}

# Base path to your logos folder
base_path = '/Users/ohadkiperman/PycharmProjects/pythonProject/nbaTransfers/nba_logos'
team_logos = {
    'ATL': os.path.join(base_path, 'atlanta-hawks-logo.png'),
    'BOS': os.path.join(base_path, 'boston-celtics-logo.png'),
    'BKN': os.path.join(base_path, 'brooklyn-nets-logo.png'),
    'CHA': os.path.join(base_path, 'charlotte-hornets-logo.png'),
    'CHI': os.path.join(base_path, 'chicago-bulls-logo.png'),
    'CLE': os.path.join(base_path, 'cleveland-cavaliers-logo.png'),
    'DAL': os.path.join(base_path, 'dallas-mavericks-logo.png'),
    'DEN': os.path.join(base_path, 'denver-nuggets-logo.png'),
    'DET': os.path.join(base_path, 'detroit-pistons-logo.png'),
    'GSW': os.path.join(base_path, 'golden-state-warriors-logo.png'),
    'HOU': os.path.join(base_path, 'houston-rockets-logo.png'),
    'IND': os.path.join(base_path, 'indiana-pacers-logo.png'),
    'LAC': os.path.join(base_path, 'los-angeles-clippers-logo.png'),
    'LAL': os.path.join(base_path, 'los-angeles-lakers-logo.png'),
    'MEM': os.path.join(base_path, 'memphis-grizzlies-logo.png'),
    'MIA': os.path.join(base_path, 'miami-heat-logo.png'),
    'MIL': os.path.join(base_path, 'milwaukee-bucks-logo.png'),
    'MIN': os.path.join(base_path, 'minnesota-timberwolves-logo.png'),
    'NOP': os.path.join(base_path, 'new-orleans-pelicans-logo.png'),
    'NYK': os.path.join(base_path, 'new-york-knicks-logo.png'),
    'OKC': os.path.join(base_path, 'oklahoma-city-thunder-logo.png'),
    'ORL': os.path.join(base_path, 'orlando-magic-logo.png'),
    'PHI': os.path.join(base_path, 'philadelphia-76ers-logo.png'),
    'PHX': os.path.join(base_path, 'phoenix-suns-logo.png'),
    'POR': os.path.join(base_path, 'portland-trail-blazers-logo.png'),
    'SAC': os.path.join(base_path, 'sacramento-kings-logo.png'),
    'SAS': os.path.join(base_path, 'san-antonio-spurs-logo.png'),
    'TOR': os.path.join(base_path, 'toronto-raptors-logo.png'),
    'UTA': os.path.join(base_path, 'utah-jazz-logo.png'),
    'WAS': os.path.join(base_path, 'washington-wizards-logo.png')
}


# Assuming 'data' is your DataFrame
data = pd.read_csv("final_data.csv")
data.sort_values(by=['Player', 'Season'], inplace=True)
data['From_Team'] = data.groupby('Player')['Team'].shift(1)
data.dropna(subset=['From_Team'], inplace=True)

def great_circle_points(start, end, num_points=100):

    lat1, lon1 = np.radians(start)
    lat2, lon2 = np.radians(end)

    fraction = np.linspace(0, 1, num_points)

    delta = np.arccos(np.sin(lat1) * np.sin(lat2) + np.cos(lat1) * np.cos(lat2) * np.cos(lon2 - lon1))
    if isinstance(delta, np.float64) and delta == 0:
        return [start] * num_points  # Avoid division by zero if start and end are the same

    a = np.sin((1 - fraction) * delta) / np.sin(delta)
    b = np.sin(fraction * delta) / np.sin(delta)
    x = a * np.cos(lat1) * np.cos(lon1) + b * np.cos(lat2) * np.cos(lon2)
    y = a * np.cos(lat1) * np.sin(lon1) + b * np.cos(lat2) * np.sin(lon2)
    z = a * np.sin(lat1) + b * np.sin(lat2)

    lat_points = np.arctan2(z, np.sqrt(x ** 2 + y ** 2))
    lon_points = np.arctan2(y, x)

    lat_points = np.degrees(lat_points)
    lon_points = np.degrees(lon_points)

    return list(zip(lat_points, lon_points))

# Create a map centered on the geographic center of the continental USA
m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)

# Add markers with custom logos for each team location
for team, coords in teams_coords.items():
    if team in team_logos:
        icon = CustomIcon(
            icon_image=team_logos[team],
            icon_size=(32, 32),
            icon_anchor=(16, 16)
        )
        folium.Marker(
            location=[coords['lat'], coords['lon']],
            icon=icon,
            popup=team_names.get(team, team)  # Show the full team name in the popup
        ).add_to(m)

# Process and display player transfers
for index, row in data.iterrows():
    from_team = row['From_Team']
    to_team = row['Team']
    player = row['Player']
    season = row['Season']

    if from_team in teams_coords and to_team in teams_coords:
        origin = teams_coords[from_team]
        destination = teams_coords[to_team]
        curve_points = great_circle_points((origin['lat'], origin['lon']), (destination['lat'], destination['lon']))
        line = folium.PolyLine(locations=curve_points, color=team_colors[from_team], weight=2.5, opacity=0.75).add_to(m)
        folium.Popup(f"Transfer of {player} from {from_team} to {to_team} during {season} season").add_to(line)
        PolyLineTextPath(line, '\u25BA', repeat=False, offset=-10,
                         attributes={'fill': team_colors[from_team], 'font-weight': 'bold', 'font-size': '18'}).add_to(m)

# Save or display the map
m.save('nba_transfers_map.html')
