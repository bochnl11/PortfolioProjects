

import pandas as pd
import os
import json
import orjson
from glob import glob
import numpy as np


import time
start_time = time.time()


competitions_df = pd.read_json('/Users/nickbochette/Documents/GitHub/PortfolioProjects/StatsBombProject/open-data/data/competitions.json')

# Filter competitions based on criteria
filtered_competitions = competitions_df[
    (competitions_df['country_name'].isin(['Germany', 'Canada'])) &
    (competitions_df['competition_international'] == False) &
    (competitions_df['competition_gender'] == 'male') & 
    (competitions_df['season_name'] == "2023/2024")
]

# Extract relevant competition and season IDs
relevant_competitions = filtered_competitions[['competition_id', 'season_id']]
print(relevant_competitions)

# Path to matches folder
matches_dir = '/Users/nickbochette/Documents/GitHub/PortfolioProjects/StatsBombProject/open-data/data/matches'
filtered_matches = []

# Iterate through all competition folders and season files
for competition_id, season_id in relevant_competitions.values:
    match_file = os.path.join(matches_dir, f"{competition_id}/{season_id}.json")
    if os.path.exists(match_file):
        with open(match_file, 'r') as f:
            match_data = json.load(f)
            # Add each match's competition_id and season_id for context
            for match in match_data:
                match['competition_id'] = competition_id
                match['season_id'] = season_id
            filtered_matches.extend(match_data)

# Convert to DataFrame
matches_df = pd.DataFrame(filtered_matches)

# Path to lineups and events folders
lineups_dir = '/Users/nickbochette/Documents/GitHub/PortfolioProjects/StatsBombProject/open-data/data/lineups'
events_dir = '/Users/nickbochette/Documents/GitHub/PortfolioProjects/StatsBombProject/open-data/data/events'

# Filter lineups and events based on match_id
lineups_data = []
events_data = []

for match_id in matches_df['match_id']:
    # Load lineups
    lineup_file = os.path.join(lineups_dir, f"{match_id}.json")
    if os.path.exists(lineup_file):
        with open(lineup_file, 'r') as f:
            lineup_data = json.load(f)
            lineup_df = pd.json_normalize(lineup_data)
            lineup_df['match_id'] = match_id  # Add match_id for merging
            lineups_data.append(lineup_df)
    
    # Load events
    event_file = os.path.join(events_dir, f"{match_id}.json")
    if os.path.exists(event_file):
        with open(event_file, 'r') as f:
            event_data = json.load(f)
            event_df = pd.json_normalize(event_data)
            event_df['match_id'] = match_id  # Add match_id for merging
            events_data.append(event_df)

# Combine all lineups and events into DataFrames
lineups_df = pd.concat(lineups_data, ignore_index=True)
events_df = pd.concat(events_data, ignore_index=True)



#Join competitions and matches:
matches_with_competitions = matches_df.merge(
    competitions_df,
    on=['competition_id', 'season_id'],
    how='left'
)

#Join matches_with_competitions with lineups:
matches_lineups = matches_with_competitions.merge(
    lineups_df,
    on='match_id',
    how='left'
)

#Join matches_with_competitions with events:
matches_events = matches_with_competitions.merge(
    events_df,
    on='match_id',
    how='left'
)



# # ---------------Match info CSV---------------
# Extract necessary fields
matches_df['home_team_name'] = matches_df['home_team'].apply(lambda x: x['home_team_name'])
matches_df['away_team_name'] = matches_df['away_team'].apply(lambda x: x['away_team_name'])
matches_df['stadium_name'] = matches_df['stadium'].apply(lambda x: x['name'])

# Create the match-level DataFrame
match_data = matches_df[[
    'match_id', 
    'home_team_name', 
    'away_team_name', 
    'stadium_name', 
    'home_score', 
    'away_score'
]]

# print(match_data.head())

match_data.to_csv('/Users/nickbochette/Documents/GitHub/PortfolioProjects/StatsBombProject/open-data/match_data.csv', index=False)




# -------------Aggregating features for player-level stats-------------------

# Define event types and their corresponding IDs
event_type_mapping = {
    30: 'passes',
    16: 'shots',
    11: 'duels',
    14: 'dribbles',
    21: 'fouls_won',
    22: 'interceptions',
    # Add more event types as needed
}

# Add a column for event category using the mapping
# Step 1: Define event types and their corresponding IDs
event_type_mapping = {
    30: 'passes', #
    16: 'shots', #
    4: 'duels', #
    14: 'dribbles', #
    21: 'fouls_won', #
    22: 'interceptions', #
    42: 'ball_receipt', #
    17: 'pressure', #
    38: 'miscontrol', #
    3: 'dispossessed', #
    21: 'foul_won', #
    22: 'foul_committed', #
    37: 'error', #
    33: '50_50', #
    9: 'clearance', #
    39: 'dribbled_passed', #
    25: 'OG_for', #
    20: 'OG_against' #


    # Add more event types as needed
}

# Step 2: Add the event_category column, map event types to categories
events_df = events_df.copy()  # Avoid fragmentation warning
events_df['event_category'] = events_df['type.id'].map(event_type_mapping)

# Group and aggregate
player_stats = events_df.groupby(['player.id', 'match_id']).agg({
    # Player Information
    'player.name': 'first',  # Player name

    # Offensive Contributions
    'event_category': [
        lambda x: (x == 'passes').sum(),       
        lambda x: (x == 'shots').sum(),       
        lambda x: (x == 'dribbles').sum(),      
        lambda x: (x == 'interceptions').sum(),  
        lambda x: (x == 'duels').sum(),         
        lambda x: (x == 'foul_won').sum(),
        lambda x: (x == 'ball_receipt').sum(),  
        lambda x: (x == 'miscontrol').sum(), 
        lambda x: (x == 'dispossessed').sum(), 
        lambda x: (x == 'error').sum(), 
        lambda x: (x == 'pressure').sum(), 
        lambda x: (x == 'foul_committed').sum(), 
        lambda x: (x == '50_50').sum(), 
        lambda x: (x == 'clearance').sum(), 
        lambda x: (x == 'dribbled_passed').sum(), 
    ],
    'pass.outcome.name': [
        # Successful passes: Only for pass events and blank, NaN, or not 'Incomplete'/'Out'
        lambda x: ((events_df['event_category'] == 'passes') &
                   (x.isnull() | (x == "") | (~x.isin(["Incomplete", "Out"])))
                  ).sum(),
        # Unsuccessful passes: Only for pass events and 'Incomplete' or 'Out'
        lambda x: ((events_df['event_category'] == 'passes') & (x.isin(["Incomplete", "Out"]))).sum(),
    ],
    'dribble.outcome.name': [
        # Successful dribbles: Only for dribble events
        lambda x: ((events_df['event_category'] == 'dribbles') & (x == "Complete")).sum(),
        # Unsuccessful dribbles: Only for pass events and 'Incomplete'
        lambda x: ((events_df['event_category'] == 'dribbles') & (x == "Incomplete")).sum(),
    ],

    'pass.goal_assist': 'sum',                # Goal assists
    'pass.shot_assist': 'sum',                # Shot assists
    'shot.statsbomb_xg': 'sum',               # Total xG
    'shot.outcome.name': [
        lambda x: (x == "Goal").sum(),         # Goals scored
        lambda x: (x.isin(["Missed", "Blocked", "Off T"])).sum(),  # Missed/blocked/off-target shots
    ],

    # Defensive Contributions
    'duel.outcome.name': [
        lambda x: ((x == "Won") | (x == "Success In Play") | (x == "Success Out")).sum(),   # Duels won
        lambda x: ((x == "Lost In Play") | (x == "Lost Out")).sum(),          # Duels lost
    ],
    'clearance.body_part.name': 'count',       # Total clearances

    # Positional and Contextual Contributions
    'position.id': 'first',
    'position.name': 'first',                  # Player position
    'team.name': 'first',                      # Team name
    'location': 'count'                        # Total events involving the player
}).reset_index()


# Step 4: Rename columns for clarity
player_stats.columns = [
    'player_id', 'match_id', 'player_name',
    'total_passes', 'total_shots', 'total_dribbles',
    'total_interceptions', 'total_duels', 'total_fouls_won', 'total_ball_receipts',
    'total_miscontrols', 'total_dispossessions', 'total_errors', 
    'total_pressures', 'total_fouls_committed', 'total_50-50s', 
    'total_clearances', 'total_dribbled_past',
    'successful_passes', 'unsuccessful_passes',
    'successful_dribbles', 'unsuccessful_dribbles',
    'goal_assists', 'shot_assists', 'total_xg',
    'goals_scored', 'unsuccessful_shots',
    'duels_won', 'duels_lost',
    'clearances', 'position_code', 'position', 'team', 'event_count'
]

# Step 5: Fill NaN values with 0 for unattempted actions
player_stats.fillna(0, inplace=True)

# Display the aggregated stats
# print(player_stats.head())

player_stats.to_csv('/Users/nickbochette/Documents/GitHub/PortfolioProjects/StatsBombProject/open-data/player_level_data.csv', index=False)



# Map position.id to generalized position categories
position_mapping = {
    1: 'Goalkeeper',
    2: 'Defender', 3: 'Defender', 4: 'Defender', 5: 'Defender', 6: 'Defender',
    7: 'Defender', 8: 'Defender',
    9: 'Midfielder', 10: 'Midfielder', 11: 'Midfielder', 
    12: 'Midfielder', 13: 'Midfielder', 14: 'Midfielder', 15: 'Midfielder', 
    16: 'Midfielder', 18: 'Midfielder', 19: 'Midfielder', 20: 'Midfielder',
    17: 'Forward', 21: 'Forward', 22: 'Forward', 23: 'Forward', 24: 'Forward', 25: 'Forward'
}

# Map position.id to a new column in player_stats
player_stats['position_category'] = player_stats['position_code'].map(position_mapping)



def calculate_player_rating(row):
    if row['position_category'] == 'Forward':
        return (
            row['goals_scored'] * 4.0 +
            row['total_xg'] * 5.0 +
            row['goal_assists'] * 3.0 +
            row['total_shots'] * 1.5 +
            row['successful_passes'] * 0.8 +
            row['successful_dribbles'] * 1.2 +
            row['shot_assists'] * 1.5 +
            row['total_ball_receipts'] * 1.0 +
            row['total_interceptions'] * 0.3 +
            row['total_pressures'] * 0.5 +
            row['total_fouls_won'] * 2.0 +
            row['total_errors'] * -1.0
        )
    elif row['position_category'] == 'Midfielder':
        return (
            row['successful_passes'] * 1.5 +
            row['goal_assists'] * 2.0 +
            row['shot_assists'] * 1.5 +
            row['successful_dribbles'] * 1.0 +
            row['total_interceptions'] * 2.0 +
            row['duels_won'] * 2.0 +
            row['total_pressures'] * 1.8 +
            row['total_ball_receipts'] * 0.75 +
            row['goals_scored'] * 3.0 +
            row['total_xg'] * 4.0 +
            row['total_clearances'] * 0.2 +
            row['total_dribbled_past'] * -2.0 +
            row['total_fouls_committed'] * -1.0 +
            row['total_errors'] * -2.5
        )
    elif row['position_category'] == 'Defender':
        return (
            row['total_interceptions'] * 2.0 +
            row['duels_won'] * 2.0 +
            row['total_clearances'] * 1.5 +
            row['successful_passes'] * 1.5 +
            row['total_pressures'] * 1.0 +
            row['goals_scored'] * 1.0 +
            row['total_xg'] * 2.0 +
            row['successful_dribbles'] * 0.5 +
            row['total_dribbled_past'] * -2.0 +
            row['total_fouls_committed'] * -1.0 +
            row['total_errors'] * -4.0
        )
    elif row['position_category'] == 'Goalkeeper':
        return (
            row['total_interceptions'] * 2.0 +
            row['total_clearances'] * 2.0 +
            row['successful_passes'] * 1.5 +
            row['total_errors'] * -5.0
        )
    else:
        return 0

# Apply the rating calculation
player_stats['player_rating'] = player_stats.apply(calculate_player_rating, axis=1)

from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler(feature_range=(0, 10))
player_stats['normalized_rating'] = scaler.fit_transform(player_stats[['player_rating']])

# print(player_stats[['player_name', 'match_id', 'position_category', 'player_rating', 'normalized_rating']].head(50))
sorted_player_stats = player_stats.sort_values(by=['match_id', 'normalized_rating'], ascending=False)
# print(sorted_player_stats[['match_id', 'team', 'player_name', 'position_category', 'player_rating', 'normalized_rating']].head(50))

sorted_player_stats.to_csv('/Users/nickbochette/Documents/GitHub/PortfolioProjects/StatsBombProject/open-data/player_rankings_data.csv', index=False)


#---------------Predictive Model --------------------------------
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# Aggregate player statistics across matches to get season averages
player_season_stats = player_stats.groupby('player_id').agg({
    'player_name': 'first',
    'position_category': 'first',
    'team': 'first',
    'total_passes': 'mean',
    'total_shots': 'mean',
    'total_dribbles': 'mean',
    'total_interceptions': 'mean',
    'total_duels': 'mean',
    'total_fouls_won': 'mean',
    'total_ball_receipts': 'mean',
    'total_miscontrols': 'mean',
    'total_dispossessions': 'mean',
    'total_errors': 'mean',
    'total_pressures': 'mean',
    'total_fouls_committed': 'mean',
    'total_50-50s': 'mean',
    'total_clearances': 'mean',
    'total_dribbled_past': 'mean',
    'successful_passes': 'mean',
    'unsuccessful_passes': 'mean',
    'successful_dribbles': 'mean',
    'unsuccessful_dribbles': 'mean',
    'goal_assists': 'mean',
    'shot_assists': 'mean',
    'total_xg': 'mean',
    'goals_scored': 'mean',
    'unsuccessful_shots': 'mean',
    'duels_won': 'mean',
    'duels_lost': 'mean',
    'normalized_rating': 'mean'
}).reset_index()

# Create position dummy variables
position_dummies = pd.get_dummies(player_season_stats['position_category'], prefix='position')
player_season_stats = pd.concat([player_season_stats, position_dummies], axis=1)


# Select features for the model
feature_columns = [col for col in player_season_stats.columns if col not in 
                  ['player_id', 'player_name', 'position_category', 'team', 'normalized_rating']]

X = player_season_stats[feature_columns]
y = player_season_stats['normalized_rating']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train the model
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train_scaled, y_train)

# Function to predict rating for a new player
def predict_player_rating(player_stats_dict, scaler=scaler, model=rf_model):
    # Convert single player stats to DataFrame
    player_df = pd.DataFrame([player_stats_dict])
    
    # Ensure all feature columns are present
    for col in X.columns:
        if col not in player_df.columns:
            player_df[col] = 0
    
    # Scale features
    player_scaled = scaler.transform(player_df[X.columns])
    
    # Make prediction
    predicted_rating = model.predict(player_scaled)[0]
    
    return predicted_rating

# Evaluate model
train_score = rf_model.score(X_train_scaled, y_train)
test_score = rf_model.score(X_test_scaled, y_test)

print(f"Training R² Score: {train_score:.3f}")
print(f"Testing R² Score: {test_score:.3f}")

# Get feature importance
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

print("\nTop 10 Most Important Features:")
print(feature_importance.head(10))



#----------------Bundesliga Player Predicted Ratings---------------------


# Aggregate stats per player
player_averages = player_stats.groupby(['player_id', 'player_name', 'team', 'position_category']).agg({
    'total_passes': 'mean',
    'total_shots': 'mean',
    'total_dribbles': 'mean',
    'total_interceptions': 'mean',
    'total_duels': 'mean',
    'total_fouls_won': 'mean',
    'total_ball_receipts': 'mean',
    'total_miscontrols': 'mean',
    'total_dispossessions': 'mean',
    'total_errors': 'mean',
    'total_pressures': 'mean',
    'total_fouls_committed': 'mean',
    'total_50-50s': 'mean',
    'total_clearances': 'mean',
    'total_dribbled_past': 'mean',
    'successful_passes': 'mean',
    'unsuccessful_passes': 'mean',
    'successful_dribbles': 'mean',
    'unsuccessful_dribbles': 'mean',
    'goal_assists': 'mean',
    'shot_assists': 'mean',
    'total_xg': 'mean',
    'goals_scored': 'mean',
    'unsuccessful_shots': 'mean',
    'duels_won': 'mean',
    'duels_lost': 'mean',
    'normalized_rating': 'mean'
}).reset_index()

# Create position dummies for each player
position_dummies = pd.get_dummies(player_averages['position_category'], prefix='position')
player_averages = pd.concat([player_averages, position_dummies], axis=1)

# Prepare data for predictions
predictions = []
for _, player in player_averages.iterrows():
    player_dict = player.drop(['player_id', 'player_name', 'team', 'position_category', 'normalized_rating']).to_dict()
    predicted_rating = predict_player_rating(player_dict)
    
    predictions.append({
        'player_name': player['player_name'],
        'team': player['team'],
        'position': player['position_category'],
        'actual_rating': player['normalized_rating'],
        'predicted_rating': predicted_rating,
        'rating_difference': predicted_rating - player['normalized_rating']
    })

player_predicted_ratings = pd.DataFrame(predictions)
player_predicted_ratings = player_predicted_ratings.sort_values('predicted_rating', ascending=False)

print(player_predicted_ratings.head(10))
player_predicted_ratings.to_csv('/Users/nickbochette/Documents/GitHub/PortfolioProjects/StatsBombProject/open-data/player_predicted_ratings.csv', index=False)





# End the timer and calculate elapsed time
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Total runtime: {elapsed_time:.2f} seconds")
print("Complete")