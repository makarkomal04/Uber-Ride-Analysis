import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import folium
from folium import plugins
import streamlit as st
import streamlit.components.v1 as components
import warnings
warnings.filterwarnings('ignore')

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title='Uber Pune Analysis Dashboard',
    page_icon='🚗',
    layout='wide',
    initial_sidebar_state='expanded'
)

# ─── Premium Dark Theme CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    .stApp { font-family: 'Inter', sans-serif; }

    .dashboard-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    .dashboard-header h1 {
        color: #ffffff; font-size: 2.2rem; font-weight: 800;
        margin: 0; letter-spacing: -0.5px;
    }
    .dashboard-header p {
        color: rgba(255,255,255,0.6); font-size: 1rem;
        margin: 0.5rem 0 0 0; font-weight: 300;
    }
    .uber-accent {
        background: linear-gradient(90deg, #00d2ff, #7b2ff7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .metric-card {
        background: linear-gradient(145deg, #1e1e2f, #252540);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.35);
    }
    .metric-value {
        font-size: 2rem; font-weight: 800;
        margin: 0.4rem 0; line-height: 1.1;
    }
    .metric-label {
        font-size: 0.78rem; color: rgba(255,255,255,0.5);
        text-transform: uppercase; letter-spacing: 1.2px; font-weight: 600;
    }
    .metric-icon { font-size: 1.5rem; margin-bottom: 0.3rem; }

    .gradient-blue { color: #00d2ff; }
    .gradient-green { color: #00e676; }
    .gradient-purple { color: #b388ff; }
    .gradient-orange { color: #ff9100; }
    .gradient-pink { color: #ff4081; }
    .gradient-cyan { color: #18ffff; }

    .section-header {
        font-size: 1.3rem; font-weight: 700; color: #ffffff;
        margin: 2rem 0 1rem 0; padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(255,255,255,0.08);
        display: flex; align-items: center; gap: 0.5rem;
    }

    .route-table {
        width: 100%; border-collapse: separate; border-spacing: 0 6px;
    }
    .route-table th {
        color: rgba(255,255,255,0.5); font-size: 0.72rem;
        text-transform: uppercase; letter-spacing: 1px;
        padding: 0.5rem 1rem; text-align: left; font-weight: 600;
    }
    .route-table td {
        padding: 0.7rem 1rem; color: #e0e0e0; font-size: 0.85rem;
    }
    .route-row { background: rgba(255,255,255,0.03); border-radius: 8px; }
    .route-row:hover { background: rgba(255,255,255,0.06); }
    .rank-badge {
        background: linear-gradient(135deg, #7b2ff7, #00d2ff);
        color: white; width: 26px; height: 26px; border-radius: 50%;
        display: inline-flex; align-items: center; justify-content: center;
        font-weight: 700; font-size: 0.75rem;
    }

    .info-badge {
        display: inline-block; background: rgba(0,210,255,0.1);
        color: #00d2ff; padding: 0.25rem 0.7rem; border-radius: 20px;
        font-size: 0.75rem; font-weight: 600;
        border: 1px solid rgba(0,210,255,0.2);
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #1e1e2f, #252540);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px; padding: 1rem 1.2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)


# ─── Constants (matplotlib-compatible RGBA tuples) ──────────────────────────
CARD_BG = '#1a1a2e'
TEXT_COLOR = '#e0e0e0'
SPINE_COLOR = (1, 1, 1, 0.15)
GRID_COLOR = (1, 1, 1, 0.08)

ACCENT_BLUE = '#00d2ff'
ACCENT_PURPLE = '#7b2ff7'
ACCENT_GREEN = '#00e676'
ACCENT_ORANGE = '#ff9100'
ACCENT_PINK = '#ff4081'
ACCENT_CYAN = '#18ffff'


def style_chart(fig, ax, title=''):
    """Apply consistent dark theme to matplotlib charts."""
    fig.patch.set_facecolor(CARD_BG)
    ax.set_facecolor(CARD_BG)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(SPINE_COLOR)
    ax.spines['bottom'].set_color(SPINE_COLOR)
    ax.tick_params(colors=TEXT_COLOR, labelsize=9)
    ax.xaxis.label.set_color(TEXT_COLOR)
    ax.yaxis.label.set_color(TEXT_COLOR)
    ax.grid(True, alpha=0.08, color='white')
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold', pad=12, color='white')
    fig.tight_layout()


# ─── Data Loading ──────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('pune_uber_rides.csv')
    df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'], errors='coerce')
    df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'], errors='coerce')
    df = df.dropna(subset=['pickup_datetime'])

    df['hour'] = df['pickup_datetime'].dt.hour
    df['day'] = df['pickup_datetime'].dt.day_name()
    df['month'] = df['pickup_datetime'].dt.month
    df['weekday'] = df['pickup_datetime'].dt.weekday
    df['is_weekend'] = df['weekday'].isin([5, 6])
    df['date'] = df['pickup_datetime'].dt.date

    if 'distance_km' not in df.columns:
        from math import radians, sin, cos, sqrt, atan2
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlat, dlon = lat2 - lat1, lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
            return R * 2 * atan2(sqrt(a), sqrt(1-a))
        df['distance_km'] = df.apply(lambda r: haversine(
            r['pickup_lat'], r['pickup_lon'], r['dropoff_lat'], r['dropoff_lon']), axis=1)

    if 'trip_duration_min' not in df.columns:
        df['trip_duration_min'] = df['distance_km'] / 20 * 60

    df['fare_amount'] = pd.to_numeric(df['fare_amount'], errors='coerce')
    df = df.dropna(subset=['fare_amount', 'pickup_lat', 'pickup_lon'])
    return df


# ─── Main ──────────────────────────────────────────────────────────────────
def main():
    df = load_data()

    # ── Sidebar Filters ──
    with st.sidebar:
        st.markdown("## 🎛️ Filters")
        st.markdown("---")

        min_date = df['pickup_datetime'].min().date()
        max_date = df['pickup_datetime'].max().date()
        date_range = st.date_input("📅 Date Range", [min_date, max_date],
                                   min_value=min_date, max_value=max_date)

        ride_types = None
        if 'ride_type' in df.columns:
            ride_types = st.multiselect(
                "🚘 Ride Type",
                options=sorted(df['ride_type'].unique()),
                default=sorted(df['ride_type'].unique()))

        payment_methods = None
        if 'payment_method' in df.columns:
            payment_methods = st.multiselect(
                "💳 Payment Method",
                options=sorted(df['payment_method'].unique()),
                default=sorted(df['payment_method'].unique()))

        hour_range = st.slider("🕐 Hour Range", 0, 23, (0, 23))

        st.markdown("---")
        st.markdown(
            f"<div class='info-badge'>📊 {len(df):,} total rides loaded</div>",
            unsafe_allow_html=True)

    # ── Apply Filters ──
    filtered = df.copy()
    if len(date_range) == 2:
        filtered = filtered[
            (filtered['pickup_datetime'].dt.date >= date_range[0]) &
            (filtered['pickup_datetime'].dt.date <= date_range[1])]
    if ride_types is not None:
        filtered = filtered[filtered['ride_type'].isin(ride_types)]
    if payment_methods is not None:
        filtered = filtered[filtered['payment_method'].isin(payment_methods)]
    filtered = filtered[
        (filtered['hour'] >= hour_range[0]) & (filtered['hour'] <= hour_range[1])]

    # ── Header ──
    st.markdown("""
    <div class="dashboard-header">
        <h1>🚗 <span class="uber-accent">Uber Rides</span> Analysis Dashboard</h1>
        <p>Comprehensive analytics of ride-hailing data across Pune, Maharashtra • Powered by 10,000+ ride records</p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI Metrics ──
    total_rides = len(filtered)
    avg_fare = filtered['fare_amount'].mean() if total_rides else 0
    avg_distance = filtered['distance_km'].mean() if total_rides else 0
    total_revenue = filtered['fare_amount'].sum() if total_rides else 0
    avg_rating = filtered['rating'].mean() if ('rating' in filtered.columns and total_rides) else 0
    avg_duration = filtered['trip_duration_min'].mean() if total_rides else 0

    cols = st.columns(6)
    metrics_data = [
        ("🚕", "Total Rides", f"{total_rides:,}", "gradient-blue"),
        ("💰", "Total Revenue", f"₹{total_revenue:,.0f}", "gradient-green"),
        ("💵", "Avg Fare", f"₹{avg_fare:.0f}", "gradient-purple"),
        ("📏", "Avg Distance", f"{avg_distance:.1f} km", "gradient-orange"),
        ("⏱️", "Avg Duration", f"{avg_duration:.0f} min", "gradient-pink"),
        ("⭐", "Avg Rating", f"{avg_rating:.1f}/5", "gradient-cyan"),
    ]
    for col, (icon, label, value, css) in zip(cols, metrics_data):
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">{icon}</div>
            <div class="metric-label">{label}</div>
            <div class="metric-value {css}">{value}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if total_rides == 0:
        st.warning("No rides match the current filters. Adjust the sidebar filters.")
        return

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 1 — Temporal Patterns
    # ════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-header">📊 Temporal Patterns</div>',
                unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        hourly = filtered['hour'].value_counts().sort_index().reindex(range(24), fill_value=0)
        fig, ax = plt.subplots(figsize=(10, 5))
        bar_colors = [ACCENT_PURPLE if h in [8, 9, 17, 18, 19] else ACCENT_BLUE for h in range(24)]
        ax.bar(range(24), hourly.values, color=bar_colors, width=0.7, alpha=0.9)
        ax.set_xlabel('Hour of Day', fontsize=11)
        ax.set_ylabel('Number of Rides', fontsize=11)
        ax.set_xticks(range(24))
        ax.set_xticklabels([f'{h:02d}' for h in range(24)], fontsize=8)
        peak_h = int(hourly.idxmax())
        ax.annotate(f'Peak: {peak_h}:00', xy=(peak_h, hourly.max()),
                    xytext=(min(peak_h + 3, 21), hourly.max() * 1.08),
                    fontsize=9, color=ACCENT_PINK, fontweight='bold',
                    arrowprops=dict(arrowstyle='->', color=ACCENT_PINK, lw=1.5))
        style_chart(fig, ax, 'Hourly Ride Distribution')
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekly = filtered['day'].value_counts().reindex(days_order, fill_value=0)
        fig, ax = plt.subplots(figsize=(10, 5))
        day_colors = [ACCENT_BLUE]*5 + [ACCENT_PINK]*2
        ax.bar(range(7), weekly.values, color=day_colors, width=0.65, alpha=0.9)
        ax.set_xticks(range(7))
        ax.set_xticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], fontsize=10)
        ax.set_xlabel('Day of Week', fontsize=11)
        ax.set_ylabel('Number of Rides', fontsize=11)
        avg_daily = weekly.mean()
        ax.axhline(y=avg_daily, color=ACCENT_GREEN, linestyle='--', alpha=0.7, lw=1.5)
        ax.text(6.4, avg_daily, f'Avg: {avg_daily:.0f}', color=ACCENT_GREEN, fontsize=9, va='center')
        style_chart(fig, ax, 'Weekly Ride Distribution')
        st.pyplot(fig)
        plt.close(fig)

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 2 — Ride Type & Payment
    # ════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-header">🚘 Ride & Payment Analytics</div>',
                unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        if 'ride_type' in filtered.columns:
            ride_counts = filtered['ride_type'].value_counts()
            fig, ax = plt.subplots(figsize=(10, 5))
            palette = [ACCENT_BLUE, ACCENT_PURPLE, ACCENT_GREEN, ACCENT_ORANGE, ACCENT_PINK]
            wedges, texts, autotexts = ax.pie(
                ride_counts.values, labels=ride_counts.index,
                autopct='%1.1f%%', startangle=90,
                colors=palette[:len(ride_counts)],
                textprops={'color': TEXT_COLOR, 'fontsize': 10},
                pctdistance=0.75,
                wedgeprops={'linewidth': 2, 'edgecolor': CARD_BG})
            for t in autotexts:
                t.set_fontweight('bold')
                t.set_fontsize(9)
            ax.add_artist(plt.Circle((0, 0), 0.50, fc=CARD_BG))
            style_chart(fig, ax, 'Ride Type Distribution')
            st.pyplot(fig)
            plt.close(fig)

    with col2:
        if 'payment_method' in filtered.columns:
            pay_counts = filtered['payment_method'].value_counts()
            fig, ax = plt.subplots(figsize=(10, 5))
            palette2 = [ACCENT_CYAN, ACCENT_GREEN, ACCENT_PURPLE, ACCENT_ORANGE, ACCENT_PINK]
            ax.barh(range(len(pay_counts)), pay_counts.values,
                    color=palette2[:len(pay_counts)], height=0.55, alpha=0.9)
            ax.set_yticks(range(len(pay_counts)))
            ax.set_yticklabels(pay_counts.index, fontsize=11)
            ax.set_xlabel('Number of Rides', fontsize=11)
            for i, val in enumerate(pay_counts.values):
                ax.text(val + max(pay_counts.values)*0.015, i, f'{val:,}',
                        va='center', fontsize=10, color=TEXT_COLOR, fontweight='600')
            style_chart(fig, ax, 'Payment Method Breakdown')
            st.pyplot(fig)
            plt.close(fig)

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 3 — Trends & Distributions
    # ════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-header">📈 Trends & Distributions</div>',
                unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        monthly = filtered.groupby(filtered['pickup_datetime'].dt.to_period('M')).size()
        monthly.index = monthly.index.astype(str)
        fig, ax = plt.subplots(figsize=(10, 5))
        x = range(len(monthly))
        ax.fill_between(x, monthly.values, alpha=0.15, color=ACCENT_BLUE)
        ax.plot(x, monthly.values, color=ACCENT_BLUE, lw=2.5,
                marker='o', markersize=5, markerfacecolor='white',
                markeredgecolor=ACCENT_BLUE, markeredgewidth=2)
        ax.set_xticks(list(x))
        ax.set_xticklabels(monthly.index, rotation=45, ha='right', fontsize=7)
        ax.set_xlabel('Month', fontsize=11)
        ax.set_ylabel('Number of Rides', fontsize=11)
        style_chart(fig, ax, 'Monthly Ride Trends')
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(filtered['fare_amount'], bins=60, color=ACCENT_PURPLE, alpha=0.7)
        med_fare = filtered['fare_amount'].median()
        mean_fare = filtered['fare_amount'].mean()
        ax.axvline(med_fare, color=ACCENT_PINK, ls='--', lw=2,
                   label=f'Median: \u20b9{med_fare:.0f}')
        ax.axvline(mean_fare, color=ACCENT_GREEN, ls='--', lw=2,
                   label=f'Mean: \u20b9{mean_fare:.0f}')
        ax.legend(fontsize=9, facecolor=CARD_BG, edgecolor='none', labelcolor=TEXT_COLOR)
        ax.set_xlabel('Fare Amount (\u20b9)', fontsize=11)
        ax.set_ylabel('Frequency', fontsize=11)
        style_chart(fig, ax, 'Fare Distribution')
        st.pyplot(fig)
        plt.close(fig)

    # ── Trip Duration + Distance ──
    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(filtered['trip_duration_min'], bins=60, color=ACCENT_ORANGE, alpha=0.7)
        med_dur = filtered['trip_duration_min'].median()
        ax.axvline(med_dur, color=ACCENT_CYAN, ls='--', lw=2,
                   label=f'Median: {med_dur:.0f} min')
        ax.legend(fontsize=9, facecolor=CARD_BG, edgecolor='none', labelcolor=TEXT_COLOR)
        ax.set_xlabel('Trip Duration (minutes)', fontsize=11)
        ax.set_ylabel('Frequency', fontsize=11)
        style_chart(fig, ax, 'Trip Duration Distribution')
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(filtered['distance_km'], bins=60, color=ACCENT_GREEN, alpha=0.7)
        med_d = filtered['distance_km'].median()
        ax.axvline(med_d, color=ACCENT_PINK, ls='--', lw=2,
                   label=f'Median: {med_d:.1f} km')
        ax.legend(fontsize=9, facecolor=CARD_BG, edgecolor='none', labelcolor=TEXT_COLOR)
        ax.set_xlabel('Distance (km)', fontsize=11)
        ax.set_ylabel('Frequency', fontsize=11)
        style_chart(fig, ax, 'Distance Distribution')
        st.pyplot(fig)
        plt.close(fig)

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 4 — Surge & Ratings
    # ════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-header">💎 Surge & Rating Insights</div>',
                unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        if 'surge_multiplier' in filtered.columns:
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                          'Friday', 'Saturday', 'Sunday']
            surge_pivot = filtered.pivot_table(
                values='surge_multiplier', index='day', columns='hour',
                aggfunc='mean')
            surge_pivot = surge_pivot.reindex(days_order)
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.heatmap(
                surge_pivot, ax=ax, cmap='YlOrRd',
                linewidths=0.5, linecolor=CARD_BG,
                cbar_kws={'label': 'Surge Multiplier'},
                xticklabels=[f'{h:02d}' for h in range(24)],
                yticklabels=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
            ax.tick_params(labelsize=8, colors=TEXT_COLOR)
            cbar = ax.collections[0].colorbar
            cbar.ax.tick_params(colors=TEXT_COLOR, labelsize=8)
            cbar.set_label('Surge Multiplier', color=TEXT_COLOR, fontsize=9)
            style_chart(fig, ax, 'Surge Pricing Heatmap (Hour x Day)')
            st.pyplot(fig)
            plt.close(fig)

    with col2:
        if 'rating' in filtered.columns:
            rating_counts = filtered['rating'].value_counts().sort_index()
            fig, ax = plt.subplots(figsize=(10, 5))
            star_colors = ['#ff1744', '#ff6d00', '#ffd600', '#76ff03', '#00e676']
            bars = ax.bar(rating_counts.index, rating_counts.values,
                          color=star_colors[:len(rating_counts)], width=0.6, alpha=0.9)
            ax.set_xticks([1, 2, 3, 4, 5])
            ax.set_xticklabels(['1 Star', '2 Star', '3 Star', '4 Star', '5 Star'], fontsize=9)
            ax.set_xlabel('Rating', fontsize=11)
            ax.set_ylabel('Number of Rides', fontsize=11)
            total_r = rating_counts.sum()
            for bar, val in zip(bars, rating_counts.values):
                pct = val / total_r * 100
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + total_r*0.005,
                        f'{pct:.1f}%', ha='center', fontsize=9, color=TEXT_COLOR, fontweight='600')
            style_chart(fig, ax, 'Ride Ratings Distribution')
            st.pyplot(fig)
            plt.close(fig)

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 5 — Fare by Ride Type (Box Plot)
    # ════════════════════════════════════════════════════════════════════════
    if 'ride_type' in filtered.columns:
        st.markdown('<div class="section-header">💵 Fare Comparison by Ride Type</div>',
                    unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(12, 5))
        ride_order = filtered.groupby('ride_type')['fare_amount'].median().sort_values().index.tolist()
        bp = ax.boxplot(
            [filtered[filtered['ride_type'] == rt]['fare_amount'].values for rt in ride_order],
            labels=ride_order, patch_artist=True, widths=0.5,
            medianprops=dict(color='white', linewidth=2),
            whiskerprops=dict(color=TEXT_COLOR, linewidth=1),
            capprops=dict(color=TEXT_COLOR, linewidth=1),
            flierprops=dict(marker='o', markerfacecolor=(1,1,1,0.3), markersize=3,
                            markeredgecolor='none'))
        box_colors = [ACCENT_BLUE, ACCENT_PURPLE, ACCENT_GREEN, ACCENT_ORANGE, ACCENT_PINK]
        for patch, color in zip(bp['boxes'], box_colors[:len(ride_order)]):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
            patch.set_edgecolor('white')
            patch.set_linewidth(0.5)
        ax.set_xlabel('Ride Type', fontsize=11)
        ax.set_ylabel('Fare Amount (\u20b9)', fontsize=11)
        style_chart(fig, ax, 'Fare Distribution by Ride Type')
        st.pyplot(fig)
        plt.close(fig)

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 6 — Top Routes
    # ════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-header">🛣️ Top 10 Popular Routes</div>',
                unsafe_allow_html=True)

    if 'pickup_area' in filtered.columns and 'dropoff_area' in filtered.columns:
        route_stats = (filtered.groupby(['pickup_area', 'dropoff_area'])
                       .agg(rides=('fare_amount', 'count'),
                            avg_fare=('fare_amount', 'mean'),
                            avg_distance=('distance_km', 'mean'),
                            avg_duration=('trip_duration_min', 'mean'))
                       .reset_index()
                       .sort_values('rides', ascending=False)
                       .head(10))

        html = '<table class="route-table"><thead><tr>'
        html += '<th>#</th><th>Pickup</th><th>Dropoff</th><th>Rides</th>'
        html += '<th>Avg Fare</th><th>Avg Distance</th><th>Avg Duration</th>'
        html += '</tr></thead><tbody>'
        for i, (_, r) in enumerate(route_stats.iterrows(), 1):
            html += (f'<tr class="route-row">'
                     f'<td><span class="rank-badge">{i}</span></td>'
                     f'<td>{r["pickup_area"]}</td>'
                     f'<td>{r["dropoff_area"]}</td>'
                     f'<td style="font-weight:700;color:{ACCENT_BLUE}">{int(r["rides"]):,}</td>'
                     f'<td>\u20b9{r["avg_fare"]:.0f}</td>'
                     f'<td>{r["avg_distance"]:.1f} km</td>'
                     f'<td>{r["avg_duration"]:.0f} min</td></tr>')
        html += '</tbody></table>'
        st.markdown(html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 7 — Geospatial Heatmap
    # ════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-header">🗺️ Pickup Heatmap — Pune</div>',
                unsafe_allow_html=True)

    map_sample = (filtered.sample(min(3000, len(filtered)), random_state=42)
                  if len(filtered) > 3000 else filtered)

    pune_map = folium.Map(location=[18.5204, 73.8567], zoom_start=12,
                          tiles='CartoDB dark_matter')

    heat_data = map_sample[['pickup_lat', 'pickup_lon']].values.tolist()
    plugins.HeatMap(heat_data, radius=12, blur=15).add_to(pune_map)

    if 'pickup_area' in filtered.columns:
        area_stats = (filtered.groupby('pickup_area')
                      .agg(count=('fare_amount', 'count'),
                           lat=('pickup_lat', 'mean'),
                           lon=('pickup_lon', 'mean'),
                           avg_fare=('fare_amount', 'mean'))
                      .reset_index()
                      .sort_values('count', ascending=False)
                      .head(10))
        for _, row in area_stats.iterrows():
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=max(6, min(20, row['count'] / 50)),
                color='#00d2ff', fill=True, fill_color='#7b2ff7',
                fill_opacity=0.7, weight=2,
                popup=folium.Popup(
                    f"<b>{row['pickup_area']}</b><br>"
                    f"Rides: {int(row['count']):,}<br>"
                    f"Avg Fare: \u20b9{row['avg_fare']:.0f}", max_width=250)
            ).add_to(pune_map)

    map_file = 'pune_map.html'
    pune_map.save(map_file)
    with open(map_file, 'r', encoding='utf-8') as f:
        components.html(f.read(), height=550)

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 8 — Weekday vs Weekend
    # ════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-header">📅 Weekday vs Weekend Comparison</div>',
                unsafe_allow_html=True)

    wd = filtered[~filtered['is_weekend']]
    we = filtered[filtered['is_weekend']]

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="metric-card"><div class="metric-label">Weekday Rides</div>'
                f'<div class="metric-value gradient-blue">{len(wd):,}</div></div>',
                unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-card"><div class="metric-label">Weekend Rides</div>'
                f'<div class="metric-value gradient-pink">{len(we):,}</div></div>',
                unsafe_allow_html=True)
    wd_f = wd['fare_amount'].mean() if len(wd) else 0
    we_f = we['fare_amount'].mean() if len(we) else 0
    c3.markdown(f'<div class="metric-card"><div class="metric-label">Weekday Avg Fare</div>'
                f'<div class="metric-value gradient-green">\u20b9{wd_f:.0f}</div></div>',
                unsafe_allow_html=True)
    c4.markdown(f'<div class="metric-card"><div class="metric-label">Weekend Avg Fare</div>'
                f'<div class="metric-value gradient-orange">\u20b9{we_f:.0f}</div></div>',
                unsafe_allow_html=True)

    # ── Footer ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align:center;padding:1.5rem;color:rgba(255,255,255,0.3);font-size:0.8rem;">'
        'Uber Rides Analysis Dashboard \u2014 Pune, Maharashtra \u2022 Built with Streamlit & Python<br>'
        f'Data contains {len(df):,} ride records across '
        f'{df["pickup_datetime"].dt.to_period("M").nunique()} months</div>',
        unsafe_allow_html=True)


if __name__ == '__main__':
    main()