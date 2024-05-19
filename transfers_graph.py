import pandas as pd
import networkx as nx

# Load your data
data = pd.read_csv("final_data.csv")

# Prepare the data by creating a 'From_Team' column
data['From_Team'] = data.groupby('Player')['Team'].shift(1)
print(data.head(10))  # Print first 10 rows to verify the data looks correct
data.dropna(subset=['From_Team'], inplace=True)  # Remove entries without a valid 'From_Team'

# Initialize the directed graph
G = nx.MultiDiGraph()  # Using a MultiDiGraph to allow multiple edges between nodes

# Add edges to the graph, each transfer is unique and gets its own edge
for index, row in data.iterrows():
    # Create a unique key for each transfer combining player, season, and team transition
    edge_key = f"{row['Player']}-{row['Season']}-{row['From_Team']}-{row['Team']}"

    # Add an edge with this unique key
    G.add_edge(row['From_Team'], row['Team'], key=edge_key,
               player=row['Player'], season=row['Season'], position=row.get('Position', 'N/A'))

# Export the graph to a GraphML file
nx.write_graphml(G, "nba_transfers.graphml")
