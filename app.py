import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the data
@st.cache_data
def load_data():
    # Replace 'path_to_your_csv_file.csv' with the actual path to your dataset
    return pd.read_csv('C:\Users\acer\Downloads\Project\Olympics_2024.csv')

# Load data
data = load_data()

# Streamlit app layout
st.title("🇫🇷 Olympics 2024 Deep-Dive 🏅")
st.markdown("""
This app explores data from the **2024 Summer Olympics** hosted in Paris, France. 
""")

# Top Countries by Medals Won
st.header("⛰️ Top Countries by Medals Won")
top_countries = data.groupby('Country')['Medals'].sum().sort_values(ascending=False).head(10)
st.bar_chart(top_countries)

# Medal Buckets
st.header("🪣 Medal Buckets")
medal_buckets = data.groupby('Country')['Medals'].sum().value_counts()
st.bar_chart(medal_buckets)

# Specific competition analysis
st.header("🔬 Investigating Competitions")
selected_competition = st.selectbox("Select a Competition", data['Competition'].unique())
competition_data = data[data['Competition'] == selected_competition]
st.write(competition_data)

# Displaying more detailed analysis
st.subheader("📊 Medal Distribution by Competition")
fig, ax = plt.subplots()
sns.countplot(x='Medal', data=competition_data, ax=ax)
st.pyplot(fig)

# Footer
st.markdown("Data source: [Kaggle Olympics 2024 Dataset](https://www.kaggle.com/datasets/x1akshay/olympics-2024)")
