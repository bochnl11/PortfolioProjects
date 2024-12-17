
# !pip install pandas
# !pip install zipfile
# !pip install kaggle
# !pip install openpyxl



import pandas as pd
import zipfile
import kaggle


#import kaggle dataset
# !kaggle datasets download -d hmavrodiev/london-bike-sharing-dataset

#Unzip file & save in data frame
zipfile_name = 'london-bike-sharing-dataset.zip'
with zipfile.ZipFile(zipfile_name, 'r') as file: file.extractall()

bikes = pd.read_csv("london_merged.csv")

#Expore data
bikes.info()
bikes.shape
print(bikes.head())

#Count the unique weathercode & season values
bikes.weather_code.value_counts()
bikes.season.value_counts()

#Create subgroup & fieldnames to be used for analysis
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
bikes.rename(new_fields_dict, axis=1, inplace=True)

#Transform humidity values to decimal
bikes.humidity_percent = bikes.humidity_percent / 100

#Map season codes to an alphanumeric season
season_dict = {
    '0.0' : 'spring',
    '1.0' : 'summer',
    '2.0' : 'autumn',
    '3.0' : 'winter'
}
bikes.season = bikes.season.astype('str')
bikes.season = bikes.season.map(season_dict)

#Map weather codes to alphanumeric 
weather_dict = {
    '1.0' : 'Clear',
    '2.0' : 'Scattered Clouds',
    '3.0' : 'Mostly Cloudy',
    '4.0' : 'Cloudy',
    '7.0' : 'Rain',
    '10.0' : 'Thunderstorms',
    '26.0' : 'Snow/Frozen Precip'
}
bikes.weather = bikes.weather.astype('str')
bikes.weather = bikes.weather.map(weather_dict)
print(bikes.head())

#Write to an Excel file to use for visualizations
bikes.to_excel('london_bikes_data_final.xlsx', sheet_name='Bikes_Data')


