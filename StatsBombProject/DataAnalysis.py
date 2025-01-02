# Soccer Data Analysis Pipeline
# Author: Nick Bochette
# Purpose: Analyze soccer match data from StatsBomb to generate player statistics and predictive models
# Last Updated: 2024

import pandas as pd
import os
import json
import orjson
from glob import glob
import numpy as np
import time
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# Track execution time for performance monitoring
start_time = time.time()

# -----------------
# Data Loading 
# -----------------

def load_competitions():
    """Load and filter competition (Bundesliga 2023/2024 Season)"""
    competitions_df = pd.read_json('/Users/nickbochette/Documents/GitHub/PortfolioProjects/StatsBombProject/data/competitions.json')
    
    # Only want German and Canadian male leagues for 2023/24 season
    return competitions_df[
        (competitions_df['country_name'].isin(['Germany', 'Canada'])) &
        (competitions_df['competition_international'] == False) &
        (competitions_df['competition_gender'] == 'male') & 
        (competitions_df['season_name'] == "2023/2024")
    ]

def load_match_data(relevant_competitions):
    """Load match data for selected competitions"""
    matches_dir = '/Users/nickbochette/Documents/GitHub/PortfolioProjects/StatsBombProject/data/matches'
    filtered_matches = []
    
    for competition_id, season_id in relevant_competitions[['competition_id', 'season_id']].values:
        match_file = os.path.join(matches_dir, f"{competition_id}/{season_id}.json")
        if os.path.exists(match_file):
            with open(match_file, 'r') as f:
                match_data = json.load(f)
                for match in match_data:
                    match['competition_id'] = competition_id
                    match['season_id'] = season_id
                filtered_matches.extend(match_data)
    
    return pd.DataFrame(filtered_matches)

# -----------------
# Event Processing
# -----------------

# Map event types to categories for analysis
event_type_mapping = {
    30: 'passes',
    16: 'shots',
    4: 'duels',
    14: 'dribbles',
    21: 'fouls_won',
    22: 'interceptions',
    42: 'ball_receipt',
    17: 'pressure',
    38: 'miscontrol',
    3: 'dispossessed',
    21: 'foul_won',
    22: 'foul_committed',
    37: 'error',
    33: '50_50',
    9: 'clearance',
    39: 'dribbled_passed',
    25: 'OG_for',
    20: 'OG_against'
}

# Map positions to general categories for player rating calculations
position_mapping = {
    1: 'Goalkeeper',
    2: 'Defender', 3: 'Defender', 4: 'Defender', 5: 'Defender', 
    6: 'Defender', 7: 'Defender', 8: 'Defender',
    9: 'Midfielder', 10: 'Midfielder', 11: 'Midfielder', 
    12: 'Midfielder', 13: 'Midfielder', 14: 'Midfielder',
    15: 'Midfielder', 16: 'Midfielder', 18: 'Midfielder',
    19: 'Midfielder', 20: 'Midfielder',
    17: 'Forward', 21: 'Forward', 22: 'Forward',
    23: 'Forward', 24: 'Forward', 25: 'Forward'
}

# -----------------
# Player Rating System
# -----------------

def calculate_player_rating(row):
    """
    Calculate player rating based on position and relevant stats
    Different weights applied to stats based on playing position
    """
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
    return 0



# -----------------
# Predictive Model Functions
# -----------------

def predict_player_rating(player_stats_dict, scaler, model):
    """Generate predicted rating for a player based on their stats"""
    player_df = pd.DataFrame([player_stats_dict])
    
    # Ensure alignment with training features
    for col in X.columns:
        if col not in player_df.columns:
            player_df[col] = 0
    
    player_scaled = scaler.transform(player_df[X.columns])
    return model.predict(player_scaled)[0]

# -----------------
# Main Execution
# -----------------

if __name__ == "__main__":
    # Load and process competition data
    filtered_competitions = load_competitions()
    matches_df = load_match_data(filtered_competitions)

    # Load lineups and events
    lineups_dir = '/Users/nickbochette/Documents/GitHub/PortfolioProjects/StatsBombProject/data/lineups'
    events_dir = '/Users/nickbochette/Documents/GitHub/PortfolioProjects/StatsBombProject/data/events'
    
    # Process match-specific data
    lineups_data = []
    events_data = []
    for match_id in matches_df['match_id']:
        # Load lineups
        lineup_file = os.path.join(lineups_dir, f"{match_id}.json")
        if os.path.exists(lineup_file):
            with open(lineup_file, 'r') as f:
                lineup_data = json.load(f)
                lineup_df = pd.json_normalize(lineup_data)
                lineup_df['match_id'] = match_id
                lineups_data.append(lineup_df)
        
        # Load events
        event_file = os.path.join(events_dir, f"{match_id}.json")
        if os.path.exists(event_file):
            with open(event_file, 'r') as f:
                event_data = json.load(f)
                event_df = pd.json_normalize(event_data)
                event_df['match_id'] = match_id
                events_data.append(event_df)

    # Combine data
    lineups_df = pd.concat(lineups_data, ignore_index=True)
    events_data_with_category = []
    for match_id in matches_df['match_id']:
        event_file = os.path.join(events_dir, f"{match_id}.json")
        if os.path.exists(event_file):
            with open(event_file, 'r') as f:
                event_data = json.load(f)
                event_df = pd.json_normalize(event_data)
                event_df['match_id'] = match_id
                # Add event_category during initial DataFrame creation
                event_df['event_category'] = event_df['type.id'].map(event_type_mapping)
                events_data_with_category.append(event_df)

    events_df = pd.concat(events_data_with_category, ignore_index=True)

    # Create match summary data
    matches_df['home_team_name'] = matches_df['home_team'].apply(lambda x: x['home_team_name'])
    matches_df['away_team_name'] = matches_df['away_team'].apply(lambda x: x['away_team_name'])
    matches_df['stadium_name'] = matches_df['stadium'].apply(lambda x: x['name'])
    match_data = matches_df[['match_id', 'home_team_name', 'away_team_name', 'stadium_name', 'home_score', 'away_score']]
    match_data.to_csv('/Users/nickbochette/Documents/GitHub/PortfolioProjects/StatsBombProject/match_data.csv', index=False)

    # Calculate player statistics
    player_stats = events_df.groupby(['player.id', 'match_id']).agg({
        'player.name': 'first',
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
            lambda x: ((events_df['event_category'] == 'passes') &
                      (x.isnull() | (x == "") | (~x.isin(["Incomplete", "Out"])))).sum(),
            lambda x: ((events_df['event_category'] == 'passes') & 
                      (x.isin(["Incomplete", "Out"]))).sum(),
        ],
        'dribble.outcome.name': [
            lambda x: ((events_df['event_category'] == 'dribbles') & 
                      (x == "Complete")).sum(),
            lambda x: ((events_df['event_category'] == 'dribbles') & 
                      (x == "Incomplete")).sum(),
        ],
        'pass.goal_assist': 'sum',
        'pass.shot_assist': 'sum',
        'shot.statsbomb_xg': 'sum',
        'shot.outcome.name': [
            lambda x: (x == "Goal").sum(),
            lambda x: (x.isin(["Missed", "Blocked", "Off T"])).sum(),
        ],
        'duel.outcome.name': [
            lambda x: ((x == "Won") | (x == "Success In Play") | 
                      (x == "Success Out")).sum(),
            lambda x: ((x == "Lost In Play") | (x == "Lost Out")).sum(),
        ],
        'clearance.body_part.name': 'count',
        'position.id': 'first',
        'position.name': 'first',
        'team.name': 'first',
        'location': 'count'
    }).reset_index()

    # Rename columns for clarity
    player_stats.columns = [
        'player_id', 'match_id', 'player_name',
        'total_passes', 'total_shots', 'total_dribbles',
        'total_interceptions', 'total_duels', 'total_fouls_won',
        'total_ball_receipts', 'total_miscontrols', 'total_dispossessions',
        'total_errors', 'total_pressures', 'total_fouls_committed',
        'total_50-50s', 'total_clearances', 'total_dribbled_past',
        'successful_passes', 'unsuccessful_passes',
        'successful_dribbles', 'unsuccessful_dribbles',
        'goal_assists', 'shot_assists', 'total_xg',
        'goals_scored', 'unsuccessful_shots',
        'duels_won', 'duels_lost',
        'clearances', 'position_code', 'position', 'team', 'event_count'
    ]

    # Fill missing values and add position categories
    player_stats.fillna(0, inplace=True)
    player_stats['position_category'] = player_stats['position_code'].map(position_mapping)
    
    # Calculate player ratings
    player_stats['player_rating'] = player_stats.apply(calculate_player_rating, axis=1)
    
    # Normalize ratings to 0-10 scale
    scaler = MinMaxScaler(feature_range=(0, 10))
    player_stats['normalized_rating'] = scaler.fit_transform(player_stats[['player_rating']])

    # Sort players by match and rating & Export
    sorted_player_stats = player_stats.sort_values(by=['match_id', 'normalized_rating'], ascending=False)
    sorted_player_stats.to_csv('/Users/nickbochette/Documents/GitHub/PortfolioProjects/StatsBombProject/player_rankings_data.csv', index=False)
    
    # Prepare season-level statistics for modeling
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
    
    # Create position dummy variables for modeling
    position_dummies = pd.get_dummies(player_season_stats['position_category'], prefix='position')
    player_season_stats = pd.concat([player_season_stats, position_dummies], axis=1)
    
    # Prepare features for modeling
    feature_columns = [col for col in player_season_stats.columns 
                      if col not in ['player_id', 'player_name', 'position_category', 
                                   'team', 'normalized_rating']]
    
    X = player_season_stats[feature_columns]
    y = player_season_stats['normalized_rating']
    
    # Split data and train model
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_train_scaled, y_train)
    
    # Generate predictions for all players
    predictions = []
    for _, player in player_season_stats.iterrows():
        player_dict = player.drop(['player_id', 'player_name', 'team', 
                                 'position_category', 'normalized_rating']).to_dict()
        predicted_rating = predict_player_rating(player_dict, scaler, rf_model)
        
        predictions.append({
            'player_name': player['player_name'],
            'team': player['team'],
            'position': player['position_category'],
            'actual_rating': player['normalized_rating'],
            'predicted_rating': predicted_rating,
            'rating_difference': predicted_rating - player['normalized_rating']
        })
    
    # Save final results
    player_predicted_ratings = pd.DataFrame(predictions)
    player_predicted_ratings = player_predicted_ratings.sort_values('predicted_rating', ascending=False)
    player_predicted_ratings.to_csv('/Users/nickbochette/Documents/GitHub/PortfolioProjects/StatsBombProject/player_predicted_ratings.csv', index=False)
    
    # Print execution summary
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Total runtime: {elapsed_time:.2f} seconds")
    print("Processing complete")