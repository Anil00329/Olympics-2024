import streamlit as st
st.set_page_config(page_title='Olympics 2024 Visualization', layout='wide')
# Import functions from olympics_2024_deep_dive
from olympics_2024_deep_dive import (
    load_data,
    clean_noc_and_add_flags,
    plot_top_countries,
    plot_medal_buckets,
    plot_medal_distribution,
    plot_top_countries_per_competition,
    plot_participation_count
)

# Load data
olympics = load_data()
# olympics = clean_noc_and_add_flags(olympics)

# # Sidebar settings
# st.sidebar.header('Settings')
# TOP_N = st.sidebar.slider('Select Top N Countries', min_value=5, max_value=20, value=10, step=1)
TOP_N=10
# Main title
st.title('Olympics 2024 Data Visualization App 🏅')

# Dataset Overview
st.subheader('Dataset Overview')
st.write(f"Rows: {olympics.shape[0]:,}, Columns: {olympics.shape[1]:,}")
st.write(olympics.head(5))

# Visualization: Top Countries by Total Medals
st.subheader(f'Top {TOP_N} Countries by Total Medals')
plot_top_countries()

# Visualization: Medal Buckets
st.subheader('🪣 Medal Buckets')
plot_medal_buckets()

# Medal Distribution by Competition
st.subheader('📊 Medal Distribution by Competition')
plot_medal_distribution()

# Top Countries by Competition
st.subheader('🏆 Top Performing Countries by Competition')
plot_top_countries_per_competition()

# Competitions with Most Participation
st.subheader('👥 Competitions with Most Participation')
plot_participation_count()
