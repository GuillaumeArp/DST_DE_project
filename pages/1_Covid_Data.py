import os
from urllib.error import URLError
import pandas as pd
import streamlit as st
import pydeck as pdk
from dotenv import load_dotenv
from sqlalchemy import create_engine
import plotly.express as px
import plotly.io as pio

load_dotenv()

DBHOST = os.getenv("DBHOST")
DBUSER = os.getenv("DBUSER")
DBPASS = os.getenv("DBPASS")
DBNAME = os.getenv("DBNAME")

pio.templates.default = "plotly_dark"

st.set_page_config(
    page_title="NYT Project",
    page_icon="📰",
)

# Connexion à notre base de données
engine = create_engine(f"postgresql+psycopg2://{DBUSER}:{DBPASS}@{DBHOST}/{DBNAME}", echo=False)

#On fait une jointure sur les tables pour associer les données de localisation géographiques aux données covid
df_covid_states=pd.read_sql('SELECT date,cases, deaths, latitude, longitude, name, geo_states.state FROM covid_states INNER JOIN geo_states ON covid_states.state=geo_states.name ORDER BY date', engine).tail(52)
#print(df_covid_states)

df_covid_counties=pd.read_sql('SELECT date, cases, deaths, lat, lng, name FROM covid_counties INNER JOIN geo_counties ON covid_counties.fips=geo_counties.fips_code ORDER BY date', engine).tail(3215)
df_covid_counties.dropna(inplace=True)
df_covid_us = pd.read_sql('covid_us', engine)
#print(df_covid_counties)

# On crée les containers streamlit
header =st.container()
states_data = st.container()
counties_data = st.container()
cumulative = st.container()

with header:
    st.title('Covid Dataset Visualization')

    st.markdown(
        """
        We can observe here the distribution of positive cases and the number of deaths due to covid by states and by counties.

        The graphs use live data and can be updated each time the code is executed.
        """
        )

with states_data:
    st.subheader(
        'Geographical Distribution of Cases and Deaths in the USA.')
    try:
        ALL_LAYERS = {
            "Covid Deaths per states": pdk.Layer(
                "ColumnLayer",
                data=df_covid_states,
                get_position=["longitude", "latitude"],
                get_elevation="deaths",
                radius=20000,
                elevation_scale=0.3*50,
                getFillColor = [0, 47, 167, 255]
            ),
            "Covid Cases per states": pdk.Layer(
                "ColumnLayer",
                data=df_covid_states,
                get_position=["longitude", "latitude"],
                get_elevation="cases",
                offset= [1,0],
                radius=20000,
                elevation_scale=0.3,
                getFillColor=[158, 253, 56, 255]
            ),
        }
        st.sidebar.markdown("### States")
        selected_layers = [
            layer
            for layer_name, layer in ALL_LAYERS.items()
            if st.sidebar.checkbox(layer_name, True, key=layer_name)
        ]
        if selected_layers:
            st.pydeck_chart(
                pdk.Deck(
                    map_style=None,
                    initial_view_state={
                        "latitude": 39,
                        "longitude": -98.5,
                        "zoom": 3,
                        "pitch": 45,
                    },
                    layers=selected_layers,
                )
            )
        else:
            st.error("Please choose at least one option.")
    except URLError as e:
        st.error(
            """
            **This demo requires internet access.**
            Connection error: %s
        """
            % e.reason
        )
    st.markdown(
            'Please note that the scale of the cases count is 50 times higher than the scale of the deaths count.')

with counties_data:
    try:
        ALL_LAYERS = {
            "Covid Deaths per counties": pdk.Layer(
                "ColumnLayer",
                data=df_covid_counties,
                get_position=["lng", "lat"],
                get_elevation="deaths",
                radius=20000,
                elevation_scale=50,
                getFillColor = [0, 47, 167, 255]
            ),
            "Covid Cases per counties": pdk.Layer(
                "ColumnLayer",
                data=df_covid_counties,
                get_position=["lng", "lat"],
                get_elevation="cases",
                offset= [1,0],
                radius=20000,
                #elevation_scale=1,
                getFillColor=[158, 253, 56, 255],
                extruded=True
            ),
        }
        st.sidebar.markdown("### Counties")
        selected_layers = [
            layer
            for layer_name, layer in ALL_LAYERS.items()
            if st.sidebar.checkbox(layer_name, True, key=layer_name)
        ]
        if selected_layers:
            st.pydeck_chart(
                pdk.Deck(
                    map_style=None,
                    initial_view_state={
                        "latitude": 39,
                        "longitude": -98.5,
                        "zoom": 3,
                        "pitch": 45,
                    },
                    layers=selected_layers,
                )
            )
        else:
            st.error("Please choose at least one option.")
    except URLError as e:
        st.error(
            """
            **This demo requires internet access.**
            Connection error: %s
            """
            % e.reason
        )


with cumulative:
    st.subheader(
        'Culumative Number of Cases and Deaths in the USA.')

    df_covid_us = pd.read_sql('covid_us', engine)

    fig1 = px.area(df_covid_us,
                  x='date',
                  y='cases',
                  title='Cumulative USA Cases Count',
                  color_discrete_sequence=['lightgreen'],
                  labels={'date': 'Date', 'cases': 'Cases'}
                  )
    fig1.update_layout(width=785,
                       height=550,
                       xaxis_title_font_size=18,
                       yaxis_title_font_size=18,
                       title_font_size=20)
    area_chart = st.plotly_chart(fig1)

    fig2 = px.area(df_covid_us,
                   x='date',
                   y='deaths',
                   title='Cumulative USA Deaths Count',
                   color_discrete_sequence=['darkred'],
                   labels={'date': 'Date', 'deaths': 'Deaths'}
                   )
    fig2.update_layout(width=785,
                       height=550,
                       xaxis_title_font_size=18,
                       yaxis_title_font_size=18,
                       title_font_size=20)
    area_chart = st.plotly_chart(fig2)
