# 🚗 Uber Rides Analysis Dashboard (Pune)

An interactive, data-driven dashboard that analyzes spatial and temporal patterns of Uber rides in Pune, Maharashtra. Built with Streamlit, Python, and Folium to uncover peak travel times, popular routes, and fare dynamics.

---

## 🌟 Key Features

- 📊 **Key Metrics Overview**: Real-time summary of total trip volume, average fares, and average trip distance.
- 🕒 **Peak Hours Analysis**: Discover the busiest times of the day with hourly distributions.
- 📅 **Weekly Travel Patterns**: Visual analysis of weekday vs. weekend travel patterns.
- 🗺️ **Interactive Geospatial Map**: Leaflet-based heatmap and location markers using Folium to pinpoint peak pickup areas and reverse-geocode addresses.
- ⏱️ **Trip Duration Analytics**: Histograms illustrating approximated trip duration frequencies based on routing.
- 💸 **Fare Distribution**: Analysis of fare amounts to understand typical spending behavior.

---

## 🛠️ Tech Stack & Libraries

- **Dashboard Framework**: [Streamlit](https://streamlit.io/) (highly responsive, custom-styled light theme layout)
- **Data Wrangling & Processing**: [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
- **Visualizations**: [Matplotlib](https://matplotlib.org/), [Seaborn](https://seaborn.pydata.org/)
- **Geospatial Mapping**: [Folium](https://python-visualization.github.io/folium/)
- **Reverse Geocoding**: [Geopy](https://geopy.readthedocs.io/) (Nominatim OpenStreetMap engine)

---

## 🚀 Quick Start & Installation

### 1. Prerequisites
Ensure you have **Python 3.8+** installed on your system.

### 2. Clone the Repository
```bash
git clone https://github.com/makarkomal04/Uber-Ride-Analysis.git
cd Uber_Ride_Data_Analysis-
```

### 3. Install Dependencies
Install all required libraries via pip:
```bash
pip install pandas numpy matplotlib seaborn folium geopy streamlit
```

### 4. Run the Application
Start the Streamlit dashboard server:
```bash
streamlit run app.py
```
Open your browser and navigate to:
👉 **[http://localhost:8501](http://localhost:8501)**

---

## 📁 Repository Structure

```tree
├── app.py                      # Main Streamlit application and layout engine
├── pune_uber_rides.csv         # Cleaned trip dataset for Pune rides
├── pune_map.html               # Auto-generated interactive Folium map
├── DS-project 1.pdf            # Project assignment description/brief
├── Project Report Uber Rides.pdf # Final analytical report
└── README.md                   # Project documentation
```

---

## 📊 Key Data Insights Highlighted
- **Busiest Hours**: Demand spikes during evening rush hours (5 PM - 8 PM) and morning commute times.
- **Popular Routes**: High concentration of pickups clustered around IT Parks, commercial hubs, and transport terminals in Pune.
- **Average Fare**: Typical trips average around **₹250**, showing a healthy balance of short and medium-range commutes.

---
*Developed for data science research and optimization of urban mobility patterns.*
