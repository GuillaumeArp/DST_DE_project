import os
import pandas as pd
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import plotly.express as px
import plotly.io as pio
import streamlit as st

pio.templates.default = "plotly_dark"
load_dotenv()
KEY=os.getenv("APIKEY")
USERNAME=os.getenv("USERNAME")
USERPWD=os.getenv("USERPWD")

st.set_page_config(
    page_title="NYT Project",
    page_icon="📰",
)

client = MongoClient(f"mongodb+srv://{USERNAME}:{USERPWD}@nyt-de.ganwi.mongodb.net/?retryWrites=true&w=majority", server_api=ServerApi('1'), serverSelectionTimeoutMS=5000)
db = client.nyt
col = db['articles']

results = list(col.find(projection={'pub_date': 1, 'news_desk': 1, '_id': 0}))

df_full = pd.DataFrame(results)
df = df_full.copy()
df = df[df['pub_date'] != '2021-01-27T17:00:00+0000']
df['pub_date'] = pd.to_datetime(df['pub_date']).dt.date
df['count'] = 1

df_grouped = df.groupby('pub_date').sum(numeric_only=True).reset_index()
df_category = df.groupby('news_desk').sum(numeric_only=True).reset_index()
df_category = df_category[(df_category['news_desk'] != '') & (df_category['count'] > 100)].sort_values(by='count', ascending=False).reset_index(drop=True)

st.title('New York Times Articles')

st.markdown(
    """
    We will explore here some quick insights regarding the New York Times coverage about Covid-19. In that effect, all relevant articles have been pulled and stored in a MongoDB database. The data is then cleaned and transformed into a pandas dataframe for further analysis.

    First we can look at the number of articles published per day, starting from January 2020.
    """)

def plot_articles():
    """Plots the number of articles published per day, starting from January 2020.

    Returns:
        plotly.graph_objs._figure.Figure: Line chart
    """

    fig = px.line(df_grouped,
              x='pub_date',
              y='count',
              title='Number of Covid-19 Articles Published by the New York Times Per Day',
              color_discrete_sequence=['orange'],
              labels={'pub_date': 'Date', 'count': 'Number of Articles'})

    fig.update_layout(width=785,
                      height=550,
                      xaxis_title_font_size=18,
                      yaxis_title_font_size=18,
                      title_font_size=20)

    return fig

def plot_categories():
    """Plots the number of articles published per news desk, starting from January 2020.

    Returns:
        plotly.graph_objs._figure.Figure: Bar chart
    """

    fig = px.bar(df_category,
                x='count',
                y='news_desk',
                title='Number of Covid-19 Articles Published by the New York Times Per Category',
                color='count',
                color_continuous_scale='Redor',
                orientation='h',
                labels={'news_desk': 'News Desk', 'count': 'Number of Articles'})

    fig.update_layout(width=785,
                      height=550,
                      xaxis_title_font_size=18,
                      yaxis_title_font_size=18,
                      title_font_size=20)

    return fig

st.plotly_chart(plot_articles())

st.markdown(
    """
    Here we can see that the number of articles published per day skyrocketed in earl 2020,
    when the pandemic started to spread in the US, with up to 96 articles published on April 1st 2020.
    The number of articles published per day has been slowly decreasing since then, and we don't see any significant increase,
    even at the peak of each wave.

    Another insight we can look at is the number of articles published per news desk.
    This can be useful to see the angle of the articles, and how the New York Times covered the pandemic.
    """
)

st.plotly_chart(plot_categories())

st.markdown(
    """
    The news desk that published the most articles is by far the Foreigh desk, most probably because of the early days where most news came from China and Europe.
    """
)
