
# !pip install pandas
# !pip install zipfile
# !pip install kaggle



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

#Map weather codes to alphanumeric 
weather_dict = {
    '1.0' = 'Clear',
    '2.0' = 'Scattered Clouds',
    '3.0' = 'Mostly Cloudy',
    '4.0' = 'Cloudy',
    '7.0' = 'Rain',
    '10.0' = 'Thunderstorms',
    '26.0' = 'Snow/Frozen Precip'
}


