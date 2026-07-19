import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium import plugins
import streamlit as st
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# Set light theme for plots
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_style("whitegrid")

class UberPuneAnalysis:
    def __init__(self, data_path='pune_uber_rides.csv'):
        try:
            self.df = pd.read_csv(data_path)
            self.preprocess_data()
        except FileNotFoundError:
            st.write("Data file not found. Please provide a valid file.")

    def preprocess_data(self):
        # Handle datetime columns
        self.df['pickup_datetime'] = pd.to_datetime(self.df['pickup_datetime'], errors='coerce')

        # Filter rows with valid datetime values
        self.df = self.df.dropna(subset=['pickup_datetime'])

        # Create derived columns
        self.df['hour'] = self.df['pickup_datetime'].dt.hour
        self.df['day'] = self.df['pickup_datetime'].dt.day_name()
        self.df['month'] = self.df['pickup_datetime'].dt.month
        self.df['weekday'] = self.df['pickup_datetime'].dt.weekday

        # Handle missing values in coordinates
        self.df = self.df.dropna(subset=['pickup_lat', 'pickup_lon', 'dropoff_lat', 'dropoff_lon'])

        # Calculate trip distance
        self.df['distance'] = self.calculate_distance()

        # Replace invalid fare amounts with NaN and drop them
        self.df['fare_amount'] = pd.to_numeric(self.df['fare_amount'], errors='coerce')
        self.df = self.df.dropna(subset=['fare_amount'])

    def calculate_distance(self):
        from math import radians, sin, cos, sqrt, atan2

        def haversine_distance(lat1, lon1, lat2, lon2):
            R = 6371  # Radius of the Earth in kilometers
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            return R * c

        return self.df.apply(lambda row: haversine_distance(
            row['pickup_lat'], row['pickup_lon'],
            row['dropoff_lat'], row['dropoff_lon']
        ), axis=1)

    def analyze_peak_hours(self):
        hourly_rides = self.df['hour'].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(x=hourly_rides.index, y=hourly_rides.values, ax=ax, color='#3498db')
        ax.set_title('Hourly Distribution of Uber Rides in Pune', fontsize=14)
        ax.set_xlabel('Hour of Day', fontsize=12)
        ax.set_ylabel('Number of Rides', fontsize=12)
        ax.set_xticks(range(24))
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return fig

    def analyze_weekly_pattern(self):
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekly_rides = self.df['day'].value_counts().reindex(days_order)
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(x=weekly_rides.index, y=weekly_rides.values, ax=ax, color='#2ecc71')
        ax.set_title('Weekly Distribution of Uber Rides in Pune', fontsize=14)
        ax.set_xlabel('Day of Week', fontsize=12)
        ax.set_ylabel('Number of Rides', fontsize=12)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return fig

    def analyze_popular_locations(self):
        pune_map = folium.Map(location=[18.5204, 73.8567], zoom_start=12, tiles='CartoDB positron')
        heat_data = [[row['pickup_lat'], row['pickup_lon']] for idx, row in self.df.iterrows()]
        plugins.HeatMap(heat_data, radius=15).add_to(pune_map)

        # Highlight popular pickup locations
        pickup_clusters = self.df.groupby(['pickup_lat', 'pickup_lon']).size().reset_index(name='count')
        popular_locations = pickup_clusters[pickup_clusters['count'] > 10]

        geolocator = Nominatim(user_agent="uber_pune_analysis")

        for _, row in popular_locations.iterrows():
            try:
                location = geolocator.reverse((row['pickup_lat'], row['pickup_lon']), timeout=10)
                address = location.address if location else "Unknown Location"
            except GeocoderTimedOut:
                address = "Geocoding Timed Out"

            folium.CircleMarker(
                location=[row['pickup_lat'], row['pickup_lon']],
                radius=5,
                color='red',
                fill=True,
                fill_color='red',
                popup=f"Count: {row['count']}\n{address}"
            ).add_to(pune_map)

        # Save the map to an HTML file
        map_file = 'pune_map.html'
        pune_map.save(map_file)
        return map_file

    def analyze_trip_durations(self):
        trip_durations = self.df['distance'] / 20 * 60  # Approximation: 20 km/h average speed
        self.df['trip_duration'] = trip_durations
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.histplot(self.df['trip_duration'], bins=50, kde=True, ax=ax, color='#9b59b6')
        ax.set_title('Distribution of Trip Durations', fontsize=14)
        ax.set_xlabel('Trip Duration (minutes)', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        plt.tight_layout()
        return fig

    def analyze_fare_distribution(self):
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.histplot(self.df['fare_amount'], bins=50, kde=True, ax=ax, color='#e74c3c')
        ax.set_title('Distribution of Fare Amounts', fontsize=14)
        ax.set_xlabel('Fare Amount (₹)', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        plt.tight_layout()
        return fig

    def generate_summary_stats(self):
        return {
            'total_rides': len(self.df),
            'average_fare': self.df['fare_amount'].mean(),
            'average_distance': self.df['distance'].mean(),
            'busiest_hour': self.df['hour'].mode().iloc[0],
            'busiest_day': self.df['day'].mode().iloc[0]
        }

def main():
    # Set light theme for Streamlit
    st.set_page_config(
        page_title='Uber Pune Analysis Dashboard', 
        layout='wide',
        initial_sidebar_state='collapsed'
    )
    
    # Apply custom CSS to use light theme and center content
    st.markdown("""
        <style>
        .main {
            background-color: #ffffff;
            color: #333333;
        }
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .block-container {
            max-width: 1000px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
        .stPlot {
            width: 70% !important;
            margin: 0 auto;
        }
        </style>
    """, unsafe_allow_html=True)
    
    analyzer = UberPuneAnalysis()

    st.title('Uber Rides Analysis - Pune')
    st.write('Comprehensive analysis of Uber rides data in Pune, Maharashtra')

    with st.container():
        col1, col2, col3 = st.columns(3)
        summary_stats = analyzer.generate_summary_stats()
        col1.metric('Total Rides', f"{summary_stats['total_rides']:,}")
        col2.metric('Average Fare', f"₹{summary_stats['average_fare']:.2f}")
        col3.metric('Average Distance', f"{summary_stats['average_distance']:.2f} km")

    st.subheader('Peak Hours Analysis')
    # Create a container to control width
    col1, _, _ = st.columns([7, 1.5, 1.5])
    with col1:
        st.pyplot(analyzer.analyze_peak_hours())

    st.subheader('Weekly Pattern')
    col1, _, _ = st.columns([7, 1.5, 1.5])
    with col1:
        st.pyplot(analyzer.analyze_weekly_pattern())

    st.subheader('Popular Locations')
    col1, _, _ = st.columns([7, 1.5, 1.5])
    with col1:
        map_file = analyzer.analyze_popular_locations()
        with open(map_file, 'r') as f:
            map_html = f.read()
        st.components.v1.html(map_html, height=500)

    st.subheader('Trip Duration Analysis')
    col1, _, _ = st.columns([7, 1.5, 1.5])
    with col1:
        st.pyplot(analyzer.analyze_trip_durations())

    st.subheader('Fare Distribution')
    col1, _, _ = st.columns([7, 1.5, 1.5])
    with col1:
        st.pyplot(analyzer.analyze_fare_distribution())

if __name__ == '__main__':
    main()