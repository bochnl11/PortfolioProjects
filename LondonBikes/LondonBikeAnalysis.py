import pandas as pd
import zipfile
import kaggle

# Data Acquisition
# Download London bike sharing dataset from Kaggle
# Note: Requires kaggle API credentials to be configured
# !kaggle datasets download -d hmavrodiev/london-bike-sharing-dataset

# Extract Dataset
# Unzip the downloaded dataset and load into pandas DataFrame
zipfile_name = 'london-bike-sharing-dataset.zip'
with zipfile.ZipFile(zipfile_name, 'r') as file: file.extractall()

# Load the extracted CSV into a pandas DataFrame
bikes = pd.read_csv("london_merged.csv")

# Initial Data Exploration
# Display DataFrame information including data types and non-null counts
bikes.info()
# Get dimensions of the DataFrame (rows, columns)
bikes.shape
# Display first 5 rows of the dataset for initial inspection
print(bikes.head())

# Categorical Data Analysis
# Analyze distribution of weather conditions and seasonal patterns
bikes.weather_code.value_counts()
bikes.season.value_counts()

# Field Renaming
# Create a dictionary to map original column names to more descriptive names
# This improves readability and maintainability of the code
new_fields_dict = {
    'timestamp' : 'time',
    'cnt' : 'count',
    't1' : 'temp_real_C',
    't2' : 'temp_feels_like_C',
    'hum' : 'humidity_percent',
    'wind_speed' : 'wind_speed_kph',
    'weather_code' : 'weather',
    'is_holiday' : 'is_holiday',
    'is_weekend' : 'is_weekend',
    'season' : 'season'
}
# Apply the renaming to the DataFrame
bikes.rename(new_fields_dict, axis=1, inplace=True)

# Data Normalization
# Convert humidity from percentage to decimal format
bikes.humidity_percent = bikes.humidity_percent / 100

# Season Code Mapping
# Convert numerical season codes to descriptive text values
# 0: spring, 1: summer, 2: autumn, 3: winter
season_dict = {
    '0.0' : 'spring',
    '1.0' : 'summer',
    '2.0' : 'autumn',
    '3.0' : 'winter'
}
# Convert season column to string type for mapping
bikes.season = bikes.season.astype('str')
# Apply season mapping
bikes.season = bikes.season.map(season_dict)

# Weather Code Mapping
# Convert numerical weather codes to descriptive text values
weather_dict = {
    '1.0' : 'Clear',
    '2.0' : 'Scattered Clouds',
    '3.0' : 'Mostly Cloudy',
    '4.0' : 'Cloudy',
    '7.0' : 'Rain',
    '10.0' : 'Thunderstorms',
    '26.0' : 'Snow/Frozen Precip'
}
# Convert weather column to string type for mapping
bikes.weather = bikes.weather.astype('str')
# Apply weather mapping
bikes.weather = bikes.weather.map(weather_dict)
# Display transformed data
print(bikes.head())

# Data Export
# Export processed DataFrame to Excel for visualization purposes
bikes.to_excel('london_bikes_data_final.xlsx', sheet_name='Bikes_Data')
