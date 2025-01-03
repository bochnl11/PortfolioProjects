"""
Airline Delay Analysis Script
Author: Nick Bochette
Purpose: Analyze 2023 airline delay patterns, seasonal trends, and contributing factors
"""

# Import required libraries
import pandas as pd
import seaborn as sns
import numpy as np
import calendar
import matplotlib
import matplotlib.pyplot as plt

# Configure matplotlib settings
plt.style.use('ggplot')
matplotlib.rcParams['figure.figsize'] = (12,8)

# Load and prepare data
def load_data():
    """Load airline delay data and verify data types"""
    df = pd.read_csv(r'/Users/nickbochette/Documents/GitHub/PortfolioProjects/Airline_Delay_Cause.csv')
    df.dtypes  # Validate data types
    return df

def analyze_carrier_delays(df):
    """
    Analyze delay patterns across airlines by calculating delay metrics and percentages
    Returns aggregated dataframe with carrier-specific delay statistics
    """
    # Aggregate delay metrics by carrier
    aggregated_df = df.groupby('carrier_name').agg({
        'arr_del15': 'sum',
        'arr_flights': 'sum',     
        'carrier_ct': 'sum',   
        'weather_ct': 'sum',     
        'nas_ct': 'sum', 
        'security_ct': 'sum',
        'late_aircraft_ct': 'sum' 
    }).reset_index()
    
    # Calculate percentage contribution of each delay type
    delay_types = ['carrier_ct', 'weather_ct', 'nas_ct', 'security_ct', 'late_aircraft_ct']
    for delay_type in delay_types:
        aggregated_df[f'{delay_type}_pct'] = (aggregated_df[delay_type] / aggregated_df['arr_del15']) * 100
    
    # Calculate total delay percentage
    aggregated_df['total_delayed_pct'] = (aggregated_df['arr_del15'] / aggregated_df['arr_flights']) * 100
    
    return aggregated_df

def visualize_carrier_delays(aggregated_df, top_n=10):
    """Generate visualization of delay patterns for top N most delayed airlines"""
    # Select top carriers by delay percentage
    top_carriers_df = aggregated_df.nlargest(top_n, 'total_delayed_pct')
    
    # Prepare data for visualization
    melted_df = top_carriers_df.melt(
        id_vars='carrier_name', 
        value_vars=[col for col in top_carriers_df.columns if col.endswith('_pct') and col != 'total_delayed_pct'],
        var_name='delay_type', 
        value_name='percentage'
    ).sort_values(by=['carrier_name', 'percentage'], ascending=[True, False])
    
    # Create grouped bar chart
    plt.figure(figsize=(12, 6))
    sns.barplot(data=melted_df, x='carrier_name', y='percentage', hue='delay_type', palette='viridis')
    plt.title('Carrier Delay Patterns - 10 Most Delayed Airlines', fontsize=16)
    plt.xlabel('Carrier Name', fontsize=12)
    plt.ylabel('Percentage of Delays (%)', fontsize=12)
    plt.xticks(rotation=45)
    plt.legend(title='Delay Type', loc='upper right')
    plt.tight_layout()
    plt.show()

def analyze_seasonal_trends(df):
    """Analyze and visualize monthly delay patterns"""
    # Aggregate delays by month
    byMonth_df = df.groupby('month').agg(
        average_arrival_delay=('arr_delay', 'mean'),
        delay_count=('arr_del15', 'sum')
    ).reset_index()
    
    # Convert month numbers to abbreviations
    byMonth_df['month'] = byMonth_df['month'].apply(lambda x: calendar.month_abbr[x])
    
    # Create dual-line plot
    plt.figure(figsize=(10, 6))
    plt.plot(byMonth_df['month'], byMonth_df['average_arrival_delay'], label='Average Arrival Delay', marker='o')
    plt.plot(byMonth_df['month'], byMonth_df['delay_count'], label='Delay Count', marker='s')
    plt.title('Delays Over Months', fontsize=16)
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Value', fontsize=12)
    plt.xticks(byMonth_df['month'])
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def analyze_peak_months(df):
    """Analyze delays during peak months (June and July)"""
    # Filter and aggregate data for peak months
    peak_months_df = df[df['month'].isin([6, 7])]
    delay_stats = peak_months_df.groupby('airport_name').agg(
        total_flights=('arr_flights', 'sum'),
        delayed_flights=('arr_del15', 'sum')
    )
    
    # Calculate and sort delay percentages
    delay_stats['percentage_delayed'] = (delay_stats['delayed_flights'] / delay_stats['total_flights']) * 100
    return delay_stats.sort_values('percentage_delayed', ascending=False).head(10)

def visualize_airport_performance(df):
    """Generate heatmap of delay percentages for top 25 airports across all months"""
    # Calculate delay statistics
    delay_stats = df.groupby(['airport_name', 'month']).agg(
        total_flights=('arr_delay', 'count'),
        delayed_flights=('arr_del15', 'sum')
    )
    delay_stats['percentage_delayed'] = (delay_stats['delayed_flights'] / delay_stats['total_flights']) * 100
    
    # Prepare heatmap data
    delay_heatmap = delay_stats['percentage_delayed'].unstack(fill_value=0)
    top_25_airports = delay_heatmap.mean(axis=1).nlargest(25).index
    
    # Create heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(
        delay_heatmap.loc[top_25_airports],
        cmap='Reds',
        annot=True,
        fmt=".1f",
        linewidths=0.5,
        cbar_kws={'label': 'Percentage of Delayed Flights'}
    )
    plt.title('Heatmap of Percentage of Delayed Flights for Top 25 Airports (All Months)', fontsize=16)
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Airport Name', fontsize=12)
    plt.tight_layout()
    plt.show()

def analyze_weather_impact(df):
    """Analyze and visualize weather's impact on delays"""
    # Calculate weather delay percentages
    df['weather_delay_percentage'] = (df['weather_delay'] / df['arr_delay']).fillna(0).replace([float('inf'), -float('inf')], 0) * 100
    weather_stats = df.groupby(['carrier_name', 'airport_name', 'month'])['weather_delay_percentage'].mean().reset_index()
    
    # Create monthly weather delay visualization
    monthly_weather = df.groupby('month')['weather_delay_percentage'].mean().reset_index()
    plt.figure(figsize=(10, 6))
    sns.barplot(data=monthly_weather, x='month', y='weather_delay_percentage', palette='cool')
    plt.title('Average Weather Delay Percentage by Month', fontsize=16)
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Avg Weather Delay Percentage', fontsize=12)
    plt.xticks(ticks=range(12), labels=[calendar.month_abbr[i] for i in range(1, 13)])
    plt.tight_layout()
    plt.show()

def analyze_cancellations_diversions(df):
    """Analyze patterns in flight cancellations and diversions"""
    # Calculate rates
    df['cancellation_rate'] = (df['arr_cancelled'] / df['arr_flights']).fillna(0).replace([float('inf'), -float('inf')], 0)
    df['diversion_rate'] = (df['arr_diverted'] / df['arr_flights']).fillna(0).replace([float('inf'), -float('inf')], 0)
    
    # Aggregate by airport
    airport_rates = df.groupby('airport_name')[['cancellation_rate', 'diversion_rate']].mean().reset_index()
    
    # Visualize top 5 airports by cancellation rate
    top_cancelled = airport_rates.nlargest(5, 'cancellation_rate')
    plt.figure(figsize=(10, 6))
    sns.barplot(data=top_cancelled, y='airport_name', x='cancellation_rate', palette='cool')
    plt.title('Top 5 Airports by Cancellation Rate', fontsize=16)
    plt.xlabel('Cancellation Rate', fontsize=12)
    plt.ylabel('Airport Name', fontsize=12)
    
    # Add value labels
    for p in plt.gca().patches:
        plt.gca().text(p.get_width() + 0.01, p.get_y() + p.get_height() / 2, 
                      f'{p.get_width():.2f}', ha='left', va='center', fontsize=10)
    plt.tight_layout()
    plt.show()

def main():
    """Main execution function"""
    df = load_data()
    
    # Execute analysis functions
    aggregated_df = analyze_carrier_delays(df)
    visualize_carrier_delays(aggregated_df)
    analyze_seasonal_trends(df)
    top_delayed_airports = analyze_peak_months(df)
    visualize_airport_performance(df)
    analyze_weather_impact(df)
    analyze_cancellations_diversions(df)

if __name__ == "__main__":
    main()