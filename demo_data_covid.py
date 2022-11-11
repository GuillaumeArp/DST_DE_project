from urllib.error import URLError
import pandas as pd
import streamlit as st
import pydeck as pdk
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
import plotly.express as px



# Connexion à notre base de données
load_dotenv()

DBHOST = os.getenv("DBHOST")
DBUSER = os.getenv("DBUSER")
DBPASS = os.getenv("DBPASS")
DBNAME = os.getenv("DBNAME")

engine = create_engine(f"postgresql+psycopg2://{DBUSER}:{DBPASS}@{DBHOST}/{DBNAME}", echo=False)

#On fait une jointure sur les tables pour associer les données de localisation géographiques aux données covid
df_covid_states=pd.read_sql('SELECT date,cases, deaths, latitude, longitude, name, geo_states.state FROM covid_states INNER JOIN geo_states ON covid_states.state=geo_states.name ORDER BY date', engine).tail(52)
#print(df_covid_states)

df_covid_counties=pd.read_sql('SELECT date, cases, deaths,lat, lng, name FROM covid_counties INNER JOIN geo_counties ON covid_counties.fips=geo_counties.fips_code ORDER BY date', engine).tail(3215)
df_covid_counties.dropna(inplace=True)
#print(df_covid_counties)

# On crée les containers streamlit
header =st.container()
states_data = st.container()
counties_data = st.container()
cumulative = st.container()

with header:
    st.title('Visualisation du dataset Covid')

    st.markdown(
        'On peut observer ici la distribution des cas positifs et du nombre de morts dûs au covid par états et par cantons.'
        ' Les graphes correspondent aux données live et peuvent être mises à jour à chaque exécution')

with states_data:
    try:
        ALL_LAYERS = {
            "Covid Deaths per states": pdk.Layer(
                "ColumnLayer",
                data=df_covid_states,
                get_position=["longitude", "latitude"],
                get_elevation="deaths",
                radius=20000,
                elevation_scale=10,
                getFillColor = [0, 47, 167, 255]
            ),
            "Covid Cases per states": pdk.Layer(
                "ColumnLayer",
                data=df_covid_states,
                get_position=["longitude", "latitude"],
                get_elevation="cases",
                offset= [1,0],
                radius=20000,
                elevation_scale=0.5,
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
            'A noter que l\'échelle des cas positifs est 20 fois plus petite que l\'échelle du nombre de morts pour les états.')

with counties_data:
    try:
        ALL_LAYERS = {
            "Covid Deaths per counties": pdk.Layer(
                "ColumnLayer",
                data=df_covid_counties,
                get_position=["lng", "lat"],
                get_elevation="deaths",
                radius=20000,
                #elevation_scale=10,
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
        'Représentation du nombre de cas positifs et de morts cumulés')

    df_covid_us = pd.read_sql('covid_us', engine)

    fig1 = px.bar(df_covid_us,x='date', y='cases')
    barplot_chart = st.write(fig1)

    fig2 = px.bar(df_covid_us, x='date', y='deaths')
    barplot_chart = st.write(fig2)