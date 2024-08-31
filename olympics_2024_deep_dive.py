import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import pycountry
from fuzzywuzzy import process

# Set Seaborn style
sns.set(style="white")

# Load the Olympics dataset
@st.cache_data
def load_data():
    return pd.read_csv('C:/Users/acer/Downloads/Project/Olympics_2024.csv')

olympics = load_data()

# Clean NOC column and add country flags
def clean_noc_and_add_flags(df):
    df['NOC'] = df['NOC'].str.strip().str.replace(r'[^\w\s]', '', regex=True)
    df['Country_Flag'] = df['NOC'].apply(lambda country: pycountry.countries.get(name=country).flag if pycountry.countries.get(name=country) else None)

    # Apply fuzzy matching to find the flag for each country
    no_flag_rows = df[df['Country_Flag'].isnull()]
    all_countries = [country.name for country in pycountry.countries]

    def get_closest_country_name(noc_name):
        best_match, score = process.extractOne(noc_name, all_countries)
        return best_match if score >= 30 else None

    df.loc[df['Country_Flag'].isnull(), 'Country_Flag'] = no_flag_rows['NOC'].apply(
        lambda noc_name: pycountry.countries.get(name=get_closest_country_name(noc_name)).flag
    )
    return df

olympics = clean_noc_and_add_flags(olympics)

# # Sidebar: Top N countries selection
# st.sidebar.header('Settings')
# TOP_N = st.sidebar.slider('Select Top N Countries', min_value=5, max_value=20, value=10, step=1)
TOP_N=10

# Medal summary

medal_summary = olympics.groupby('NOC').agg(
    Total_Medals=('Total', 'sum'),
    Gold_Medals=('Gold', 'sum'),
    Silver_Medals=('Silver', 'sum'),
    Bronze_Medals=('Bronze', 'sum')
).reset_index()

medal_summary = medal_summary.sort_values(by='Total_Medals', ascending=False).reset_index(drop=True)
medal_summary = pd.merge(medal_summary, olympics[['NOC', 'Country_Flag']].drop_duplicates(subset=['NOC']), on='NOC', how='left')

# Visualization: Top N countries by medals

temp = medal_summary.head(TOP_N)
remaining_medals = medal_summary.iloc[TOP_N:].Total_Medals.sum()
others_df = pd.DataFrame({'NOC': ['Others'], 'Total_Medals': [remaining_medals]})
temp = pd.concat([temp, others_df], ignore_index=True)

total_medals = temp.Total_Medals.sum()
temp['Percentage'] = (temp.Total_Medals / total_medals) * 100

def plot_top_countries():
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=temp, y='NOC', x='Total_Medals', palette='Paired', edgecolor='black', ax=ax)
    ax.set_title(f'Top {TOP_N} Countries by Total Medals', fontsize=16, weight='bold')
    ax.set_xlabel('Total Medals', fontsize=12)
    ax.set_ylabel('Country', fontsize=12)
    plt.yticks(rotation=0)
    plt.xlim((0, 510))

    ax.grid(axis='x', linestyle='--', alpha=0.7)

    for index, row in temp.iterrows():
        ax.text(row.Total_Medals + 5, index, f'{row.Percentage:.1f}%', va='center', fontsize=10)

    plt.figtext(0.5, -0.05, 'Percentage reflects the share of total medals won by each country.', wrap=True, horizontalalignment='center', fontsize=10)
    plt.tight_layout()
    st.pyplot(fig)


# Medal buckets

bins = [0, 5, 10, 15, 20, 25, 30, 35, 40, 50, 60, 70, 80, 90, 100]
labels = ['0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30-34', '35-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90-100']

medal_summary['Medal_Range'] = pd.cut(medal_summary['Total_Medals'], bins=bins, labels=labels, right=False)
medal_count_summary = medal_summary.groupby('Medal_Range').size().reset_index(name='Number_of_Countries')
medal_count_summary['Share_of_Countries'] = round(100 * medal_count_summary['Number_of_Countries'] / medal_count_summary['Number_of_Countries'].sum(), 3)
medal_count_summary['Cumulative_Share'] = medal_count_summary['Share_of_Countries'].cumsum()

def plot_medal_buckets():
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=medal_count_summary, y='Medal_Range', x='Number_of_Countries', palette='Greens', edgecolor='black', ax=ax)
    ax.set_title('Number of Countries by Medal Range', fontsize=16, weight='bold')
    ax.set_xlabel('Number of Countries', fontsize=12)
    ax.set_ylabel('Medal Range', fontsize=12)
    plt.yticks(rotation=0)
    plt.xlim((0, 50))

    for index, row in medal_count_summary.iterrows():
        ax.text(row['Number_of_Countries'] + 2.0, index, f"{row['Share_of_Countries']:.1f}%", fontsize=10, color='black', ha="center", va="center")

    plt.figtext(0.5, -0.05, 'Percentage reflects the share of countries who won are in the medal range.', wrap=True, horizontalalignment='center', fontsize=10)
    plt.tight_layout()
    st.pyplot(fig)

# Competitions section


# Medal distribution by competition

competition_medals = olympics.groupby('Competitions')[['Gold', 'Silver', 'Bronze']].sum()
competition_medals['Total'] = competition_medals.sum(axis=1)
competition_medals = competition_medals.sort_values(by='Total', ascending=False)
competition_medals = competition_medals.drop(columns='Total')

def plot_medal_distribution():
    fig, ax = plt.subplots(figsize=(10, 5))
    competition_medals.plot(kind='bar', stacked=True, figsize=(10, 5), color=['gold', 'silver', 'brown'], ax=ax)
    ax.set_title('Medal Distribution by Competition', fontsize=16, weight='bold')
    ax.set_xlabel('Competitions', fontsize=12)
    ax.set_ylabel('Number of Medals', fontsize=12)
    plt.xticks(rotation=90)
    plt.tight_layout()
    st.pyplot(fig)

# Top countries by competition

top_countries_per_competition = olympics.groupby(['Competitions', 'NOC'])['Total'].sum().reset_index()
top_countries_per_competition = top_countries_per_competition.sort_values(['Competitions', 'Total'], ascending=[True, False])
top_countries_per_competition = top_countries_per_competition.drop_duplicates(subset=['Competitions'], keep='first')

def plot_top_countries_per_competition():
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(y='Competitions', x='Total', hue='NOC', data=top_countries_per_competition, dodge=False, palette='tab20', ax=ax)
    ax.set_title('Top Countries by Medals per Competition', fontsize=16, weight='bold')
    ax.set_xlabel('Number of Medals', fontsize=12)
    ax.set_ylabel('Competitions', fontsize=12)
    plt.legend(title='Country', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    st.pyplot(fig)


# Competitions with most participation

participation_count = olympics.groupby('Competitions')['NOC'].nunique().reset_index()
participation_count.columns = ['Competitions', 'Number_of_Countries']
participation_count = participation_count.sort_values(by='Number_of_Countries', ascending=False)

def plot_participation_count():
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x='Competitions', y='Number_of_Countries', data=participation_count, ax=ax)
    plt.title('Number of Countries Participating by Competition')
    plt.ylabel('Number of Countries')
    plt.xlabel('Competitions')
    plt.xticks(rotation=90)
    fig.tight_layout()
    st.pyplot(fig)
