#Imports
import pandas as pd
import seaborn as sns
import numpy as np
import calendar

import matplotlib
import matplotlib.pyplot as plt
plt.style.use('ggplot')
from matplotlib.pyplot import figure

%matplotlib inline
matplotlib.rcParams['figure.figsize'] = (12,8)


#Read in data
df = pd.read_csv(r'/Users/nickbochette/Downloads/ot_delaycause1_DL/Airline_Delay_Cause.csv')

#Check data types
df.dtypes


# -----Analyze Delay Patterns Across Airlines
# ---Objective: Identify which carriers experience the most delays and understand the contributing factors.




# --Group data by carrier or carrier_name and aggregate delay metrics (arr_del15, carrier_ct, weather_ct, etc.).
aggregated_df = df.groupby('carrier_name').agg({
    'arr_del15': 'sum',
    'arr_flights': 'sum',     
    'carrier_ct': 'sum',   
    'weather_ct': 'sum',     
    'nas_ct': 'sum', 
    'security_ct': 'sum',
    'late_aircraft_ct': 'sum' 
})

# -Resetting the index 
aggregated_df = aggregated_df.reset_index()
print(aggregated_df)


# --Calculate percentages of delay causes relative to total delays.
aggregated_df['carrier_ct_pct'] = (aggregated_df['carrier_ct'] / aggregated_df['arr_del15']) * 100
aggregated_df['weather_ct_pct'] = (aggregated_df['weather_ct'] / aggregated_df['arr_del15']) * 100
aggregated_df['nas_ct_pct'] = (aggregated_df['nas_ct'] / aggregated_df['arr_del15']) * 100
aggregated_df['security_ct_pct'] = (aggregated_df['security_ct'] / aggregated_df['arr_del15']) * 100
aggregated_df['late_aircraft_ct_pct'] = (aggregated_df['late_aircraft_ct'] / aggregated_df['arr_del15']) * 100

# -Display the updated DataFrame
print(aggregated_df)


# --Visualize carrier-specific delay patterns with bar charts or pie charts using libraries like Matplotlib or Seaborn.

# -Calculate the total delay percentage for each carrier
aggregated_df['total_delayed_pct'] = (aggregated_df['arr_del15'] / aggregated_df['arr_flights']) * 100

# -Sort by the highest total delay percentage and select the top N carriers
top_n = 10  # Number of top carriers to visualize
top_carriers_df = aggregated_df.nlargest(top_n, 'total_delayed_pct')


# -Melt the DataFrame for better handling in seaborn
melted_df = top_carriers_df.melt(
    id_vars='carrier_name', 
    value_vars=['carrier_ct_pct', 'weather_ct_pct', 'nas_ct_pct', 'security_ct_pct', 'late_aircraft_ct_pct'], 
    var_name='delay_type', 
    value_name='percentage'
)

# -Sort value_vars
melted_df = melted_df.sort_values(by=['carrier_name', 'percentage'], ascending=[True, False])

# --Create a grouped bar chart
plt.figure(figsize=(12, 6))
sns.barplot(data=melted_df, x='carrier_name', y='percentage', hue='delay_type', palette='viridis')

plt.title('Carrier Delay Patterns - 10 Most Delayed Airlines', fontsize=16)
plt.xlabel('Carrier Name', fontsize=12)
plt.ylabel('Percentage of Delays (%)', fontsize=12)
plt.xticks(rotation=45)
plt.legend(title='Delay Type', loc='upper right')
plt.tight_layout()
plt.show()


# -----Investigate Seasonal Trends in Delays
# ---Objective: Determine how delays vary by month or season.

# --Group data by month and calculate average delays (arr_delay) and delay counts (arr_del15).
byMonth_df = df.groupby('month').agg(
    average_arrival_delay=('arr_delay', 'mean'),   # Calculate average arrival delay
    delay_count=('arr_del15', 'sum')              # Count the number of delays
).reset_index()
print(byMonth_df)

# --Visualize delays over months with a line chart.
# -Plot the average arrival delay and delay count

# -Map month numbers to names
byMonth_df['month'] = byMonth_df['month'].apply(lambda x: calendar.month_abbr[x])
plt.figure(figsize=(10, 6))

# -Line for average arrival delay
plt.plot(byMonth_df['month'], byMonth_df['average_arrival_delay'], label='Average Arrival Delay', marker='o')

# -Line for delay count
plt.plot(byMonth_df['month'], byMonth_df['delay_count'], label='Delay Count', marker='s')

plt.title('Delays Over Months', fontsize=16)
plt.xlabel('Month', fontsize=12)
plt.ylabel('Value', fontsize=12)
plt.xticks(byMonth_df['month'])  # Ensure proper labeling of months
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# --Deeper dive into most delayed months, June and July
# -Filter the original dataframe (df) for June (6) and July (7)
filtered_df = df[df['month'].isin([6, 7])]

# -Group by airport_name and calculate the total and delayed flights
delay_stats = filtered_df.groupby('airport_name').agg(
    total_flights=('arr_flights', 'sum'),          # Total number of flights
    delayed_flights=('arr_del15', 'sum')          # Number of delayed flights
)

# -Calculate the percentage of delayed flights
delay_stats['percentage_delayed'] = (delay_stats['delayed_flights'] / delay_stats['total_flights']) * 100

# -Sort by percentage of delayed flights in descending order and get the top 10
top_airports_percentage = delay_stats.sort_values('percentage_delayed', ascending=False).head(10)

# -Display the top 10 airports by percentage of delayed flights
print(top_airports_percentage[['percentage_delayed']])



# -----Visualize Airport Performance
# ---Objective: Identify the airports with the most delays and the primary causes.

# Create a horizontal bar chart with Seaborn
plt.figure(figsize=(10, 6))
sns.barplot(
    x='percentage_delayed', 
    y=top_airports_percentage.index, 
    data=top_airports_percentage.reset_index(),
    palette='Blues_r'
)

plt.xlabel('Percentage of Delayed Flights', fontsize=12)
plt.ylabel('Airport Name', fontsize=12)
plt.title('Top 10 Airports by Percentage of Delayed Flights (June & July)', fontsize=14)
plt.tight_layout()
plt.show()

# ---Create heatmap of top 25 airports for all months
# --Group by airport_name and month to calculate delayed and total flights
delay_stats = df.groupby(['airport_name', 'month']).agg(
    total_flights=('arr_delay', 'count'),  # Total number of flights (count all rows)
    delayed_flights=('arr_del15', 'sum')  # Number of delayed flights (sum of arr_del15)
)

# -Calculate the percentage of delayed flights
delay_stats['percentage_delayed'] = (delay_stats['delayed_flights'] / delay_stats['total_flights']) * 100

# -Reshape the data to have months as columns
delay_heatmap_data = delay_stats['percentage_delayed'].unstack(fill_value=0)

# -Identify the top 25 airports by their overall percentage of delayed flights
top_25_airports = delay_heatmap_data.mean(axis=1).nlargest(25).index

# -Filter the data for the top 25 airports
filtered_heatmap_data = delay_heatmap_data.loc[top_25_airports]

# -Create the heatmap
plt.figure(figsize=(12, 8))
sns.heatmap(
    filtered_heatmap_data, 
    cmap='Reds', 
    annot=True, 
    fmt=".1f",  # Display percentage values with one decimal place
    linewidths=0.5, 
    cbar_kws={'label': 'Percentage of Delayed Flights'}
)

plt.title('Heatmap of Percentage of Delayed Flights for Top 25 Airports (All Months)', fontsize=16)
plt.xlabel('Month', fontsize=12)
plt.ylabel('Airport Name', fontsize=12)
plt.tight_layout()
plt.show()



# -----Assess Impact of Weather on Delays
# ---Objective: Quantify how much weather contributes to total delays and analyze trends.

# --Calculate the percentage of weather delays (weather_delay / arr_delay) across carriers, airports, and months.
# -Avoid division by zero by replacing NaN or infinite values with 0
df['weather_delay_percentage'] = (df['weather_delay'] / df['arr_delay']).fillna(0).replace([float('inf'), -float('inf')], 0) * 100

# -Group by carrier, airport, and month
weather_delay_stats = df.groupby(['carrier_name', 'airport_name', 'month'])['weather_delay_percentage'].mean().reset_index()

# -Rename for clarity
weather_delay_stats.rename(columns={'weather_delay_percentage': 'avg_weather_delay_percentage'}, inplace=True)

# -Create the heatmap for carriers and months
plt.figure(figsize=(12, 8))
sns.heatmap(
    #carrier_month_pivot, 
    cmap='YlGnBu', 
    annot=True, 
    fmt=".1f",  # Show percentages with one decimal place
    linewidths=0.5, 
    cbar_kws={'label': 'Avg Weather Delay Percentage'}
)

plt.title('Weather Delay Percentage by Carrier and Month', fontsize=16)
plt.xlabel('Month', fontsize=12)
plt.ylabel('Carrier Name', fontsize=12)
plt.tight_layout()
plt.show()

# --Airport vs. Month Heatmap
# -Create the heatmap for airports and months
plt.figure(figsize=(12, 12))
sns.heatmap(
    #airport_month_pivot, 
    cmap='RdYlBu', 
    annot=True, 
    fmt=".1f", 
    linewidths=0.5, 
    cbar_kws={'label': 'Avg Weather Delay Percentage'}
)

plt.title('Weather Delay Percentage by Airport and Month', fontsize=16)
plt.xlabel('Month', fontsize=12)
plt.ylabel('Airport Name', fontsize=12)
plt.tight_layout()
plt.show()

# --Select top 5 carriers with the highest overall average weather delay percentage
top_5_carriers = weather_delay_stats.groupby('carrier_name')['avg_weather_delay_percentage'].mean().nlargest(5).index
filtered_data = weather_delay_stats[weather_delay_stats['carrier_name'].isin(top_5_carriers)]

# -Create a line chart
plt.figure(figsize=(10, 6))
sns.lineplot(
    data=filtered_data, 
    x='month', 
    y='avg_weather_delay_percentage', 
    hue='carrier_name', 
    marker='o'
)

plt.title('Weather Delay Trends for Top 5 Carriers', fontsize=16)
plt.xlabel('Month', fontsize=12)
plt.ylabel('Avg Weather Delay Percentage', fontsize=12)
plt.legend(title='Carrier', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# --Investigate correlations between month and weather delay.
# -Calculate the average weather delay percentage for each month
monthly_weather_delays = df.groupby('month')['weather_delay_percentage'].mean().reset_index()

plt.figure(figsize=(10, 6))
sns.barplot(data=monthly_weather_delays, x='month', y='weather_delay_percentage', palette='cool')

plt.title('Average Weather Delay Percentage by Month', fontsize=16)
plt.xlabel('Month', fontsize=12)
plt.ylabel('Avg Weather Delay Percentage', fontsize=12)
plt.xticks(ticks=range(12), labels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
plt.tight_layout()
plt.show()


# -----Analyze Trends in Cancelled and Diverted Flights
# ---Objective: Understand when and where cancellations and diversions are most common.

# --Calculate cancellation and diversion rates:
df['cancellation_rate'] = df['arr_cancelled'] / df['arr_flights']
df['diversion_rate'] = df['arr_diverted'] / df['arr_flights']

# -To avoid division by zero, ensure any infinite or NaN values are handled:
df['cancellation_rate'] = df['cancellation_rate'].fillna(0).replace([float('inf'), -float('inf')], 0)
df['diversion_rate'] = df['diversion_rate'].fillna(0).replace([float('inf'), -float('inf')], 0)

# --Group data by month, carrier, or airport to see variations in rates.
# -Group by month and calculate the average cancellation and diversion rates
monthly_rates = df.groupby('month')[['cancellation_rate', 'diversion_rate']].mean().reset_index()
print(monthly_rates)

# -Group by carrier and calculate the average cancellation and diversion rates
carrier_rates = df.groupby('carrier_name')[['cancellation_rate', 'diversion_rate']].mean().reset_index()
print(carrier_rates)

# -Group by airport and calculate the average cancellation and diversion rates
airport_rates = df.groupby('airport_name')[['cancellation_rate', 'diversion_rate']].mean().reset_index()
print(airport_rates)

# --Visualize trends of top 5 airports for diversion or cancellation
# -Group by airport and calculate the average cancellation and diversion rates
airport_rates = df.groupby('airport_name')[['cancellation_rate', 'diversion_rate']].mean().reset_index()

# -Sort the data to get the top 5 airports for cancellation rate
top_airports_cancelled = airport_rates.sort_values(by='cancellation_rate', ascending=False).head(5)

# -Sort the data to get the top 5 airports for diversion rate
top_airports_diverted = airport_rates.sort_values(by='diversion_rate', ascending=False).head(5)

# -Horizontal bar plot for top 5 airports by cancellation rate
plt.figure(figsize=(10, 6))
sns.barplot(data=top_airports_cancelled, y='airport_name', x='cancellation_rate', palette='cool')

plt.title('Top 5 Airports by Cancellation Rate', fontsize=16)
plt.xlabel('Cancellation Rate', fontsize=12)
plt.ylabel('Airport Name', fontsize=12)

# Add the value labels on the bars
for p in plt.gca().patches:
    plt.gca().text(p.get_width() + 0.01, p.get_y() + p.get_height() / 2, f'{p.get_width():.2f}', ha='left', va='center', fontsize=10)
plt.tight_layout()
plt.show()














#---------------TABLEAU-------------

# 1. Monthly Trends in Delays

# 	•	Visualization Type: Line Chart
# 	•	Insights Provided:
# 	•	Displays seasonal trends in total delays (arr_delay) or the percentage of delayed flights (arr_del15 / arr_flights).
# 	•	Highlights peaks in delay causes such as weather or carrier issues.
# 	•	Implementation Steps:
# 	1.	Aggregate delay metrics by month.
# 	2.	Use a dual-axis chart to compare total delays and delay percentages over time.

# 2. Delay Contribution by Cause

# 	•	Visualization Type: Stacked Bar Chart or Tree Map
# 	•	Insights Provided:
# 	•	Breaks down delays (carrier_ct, weather_ct, nas_ct, etc.) by airline or airport to show contributing factors.
# 	•	Quickly identifies the primary causes of delays for different carriers or airports.
# 	•	Implementation Steps:
# 	1.	Group data by carrier or airport.
# 	2.	Create a stacked bar chart to display the proportion of each delay cause relative to the total.

# 3. Airport Performance Heatmap

# 	•	Visualization Type: Heatmap
# 	•	Insights Provided:
# 	•	Visualizes the delay percentage (arr_del15 / arr_flights) or average delay time (arr_delay) across all airports.
# 	•	Quickly identifies airports with consistently high delays.
# 	•	Implementation Steps:
# 	1.	Group data by airport.
# 	2.	Map metrics like average delay time to color intensity in a heatmap.

# 4. Impact of Weather Delays

# 	•	Visualization Type: Scatter Plot with Trend Line
# 	•	Insights Provided:
# 	•	Examines the relationship between weather-related delay counts (weather_ct) and delay durations (weather_delay).
# 	•	Identifies patterns or outliers where weather delays are unusually high or low compared to counts.
# 	•	Implementation Steps:
# 	1.	Use weather_ct on the X-axis and weather_delay on the Y-axis.
# 	2.	Add a trend line to show overall correlation.

# 5. Cancellations and Diversions Over Time

# 	•	Visualization Type: Area Chart or Bar Chart
# 	•	Insights Provided:
# 	•	Tracks changes in flight cancellation and diversion rates across months or years.
# 	•	Highlights spikes during specific months (e.g., winter storms).
# 	•	Implementation Steps:
# 	1.	Calculate cancellation_rate (arr_cancelled / arr_flights) and diversion_rate (arr_diverted / arr_flights).
# 	2.	Use time (year/month) on the X-axis and rates on the Y-axis.