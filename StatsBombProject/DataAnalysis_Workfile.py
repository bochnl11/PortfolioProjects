


#---------------------------------------------------------------------------------------
# #--Read in matches files
# matches_dir = '/Users/nickbochette/Documents/GitHub/PortfolioProjects/StatsBombProject/open-data/data/matches'
# matches_data = []

# # Iterate through all competition folders
# for competition_folder in glob(os.path.join(matches_dir, '*')):
#     if os.path.isdir(competition_folder):  # Ensure it's a directory
#         competition_id = os.path.basename(competition_folder)  # Extract competition_id

#         for season_file in glob(os.path.join(competition_folder, '*.json')):
#             with open(season_file, 'r') as f:
#                 data = json.load(f)
#                 df = pd.json_normalize(data, sep='_')
#                 # Add competition and season context
#                 season_id = os.path.splitext(os.path.basename(season_file))[0]  # Extract season_id from file name
#                 df['competition_id'] = competition_id
#                 df['season_id'] = season_id
#                 matches_data.append(df)

# matches_df = pd.concat(matches_data, ignore_index=True)
# # print(matches_df.head())


# #--Read in lineups files
# lineups_dir = '/Users/nickbochette/Documents/GitHub/PortfolioProjects/StatsBombProject/open-data/data/lineups'
# lineups_data = [] # Create an empty list to store DataFrames

# # Iterate through all .json files in the directory
# for file_path in glob(os.path.join(lineups_dir, '*.json')):
#     with open(file_path, 'r') as f:
#         data = json.load(f)
#         df = pd.json_normalize(data, sep='_')
#         file_name = os.path.splitext(os.path.basename(file_path))[0]
#         df['match_id'] = file_name # Add a column for the file name (without the path)
#         lineups_data.append(df)

# # Combine all DataFrames into one
# lineups_df = pd.concat(lineups_data, ignore_index=True)
# # print(lineups_df.head())


# #--Read in events files

# events_dir = '/Users/nickbochette/Documents/GitHub/PortfolioProjects/StatsBombProject/open-data/data/events'
# events_data = [] # Create an empty list to store DataFrames

# # for file_path in glob(os.path.join(events_dir, '*.json')):
# #     with open(file_path, 'rb') as f:
# #         data = orjson.loads(f.read())
# #         df = pd.json_normalize(data)
# #         df['source_file'] = os.path.basename(file_path) # Add a column for the file name (without the path)
# #         events_data.append(df)

# # Reading in a subset of the events files - important for speed of testing 
# for file_path in glob(os.path.join(events_dir, '*.json')):
#     # Extract the file name without extension
#     file_name = os.path.splitext(os.path.basename(file_path))[0]
#     if file_name.startswith("15"):      # Check if the name starts with "15"
#         with open(file_path, 'r') as f:
#             data = json.load(f)
#             df = pd.json_normalize(data, sep='_')
#             df['match_id'] = file_name
#             events_data.append(df)

# # # Combine all DataFrames into one
# # events_df.to_csv('/Users/nickbochette/Documents/GitHub/PortfolioProjects/StatsBombProject/open-data/events_data.csv', index=False)
# events_df = pd.concat(events_data, ignore_index=True)

# events_df = pd.read_csv('/Users/nickbochette/Documents/GitHub/PortfolioProjects/StatsBombProject/open-data/events_data.csv', low_memory=False)
# print(events_df.head())









# matches_df['competition_id'] = matches_df['competition_id'].astype(int)
# matches_df['season_id'] = matches_df['season_id'].astype(int)
# events_df['match_id'] = events_df['match_id'].astype(int)
# lineups_df['match_id'] = lineups_df['match_id'].astype(int)

# # Extract datatype information for each DataFrame
# events_dtypes = events_df.dtypes.reset_index()
# events_dtypes.columns = ['Column Name', 'Data Type']

# matches_dtypes = matches_df.dtypes.reset_index()
# matches_dtypes.columns = ['Column Name', 'Data Type']

# lineups_dtypes = lineups_df.dtypes.reset_index()
# lineups_dtypes.columns = ['Column Name', 'Data Type']

# competitions_dtypes = competitions_df.dtypes.reset_index()
# competitions_dtypes.columns = ['Column Name', 'Data Type']

# # Create an Excel writer to save all DataFrames into one file
# with pd.ExcelWriter('/Users/nickbochette/Documents/GitHub/PortfolioProjects/StatsBombProject/open-data/dataframes_dtypes.xlsx', engine='openpyxl') as writer:
#     events_dtypes.to_excel(writer, sheet_name='events_df', index=False)
#     matches_dtypes.to_excel(writer, sheet_name='matches_df', index=False)
#     lineups_dtypes.to_excel(writer, sheet_name='lineups_df', index=False)
#     competitions_dtypes.to_excel(writer, sheet_name='competitions_df', index=False)
# print("Data types exported successfully!")