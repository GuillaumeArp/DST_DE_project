import os
from datetime import datetime
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# RDS Connection
DBHOST = os.getenv("DBHOST")
DBUSER = os.getenv("DBUSER")
DBPASS = os.getenv("DBPASS")
DBNAME = os.getenv("DBNAME")

start = datetime.now().strftime('%d/%m/%Y - %H:%M:%S')
print(f'{start} - Fetching data...')

# on se connecte à notre base de données
engine = create_engine(f"postgresql+psycopg2://{DBUSER}:{DBPASS}@{DBHOST}/{DBNAME}", echo=False)
Session = sessionmaker(bind=engine)
session = Session()

'''
# pour créer les tables SQL une première fois : lectures des fichiers csv et création des tables SQL

df_us = pd.read_csv("https://raw.githubusercontent.com/nytimes/covid-19-data/master/us.csv")
df_counties = pd.read_csv("https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties-recent.csv")
df_states = pd.read_csv("https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv")

df_us.to_sql('covid_us',engine, if_exists='replace', index=False)
df_counties.to_sql('covid_counties', engine, if_exists='replace', index=False)
df_states.to_sql('covid_states', engine, if_exists='replace', index=False)

print(datetime.now(), "Création des tables OK")
'''


try:
    # récupération automatisée des dernières données covid tous les jours avec crontab
    df_us_plus = pd.read_csv("https://raw.githubusercontent.com/nytimes/covid-19-data/master/live/us.csv")
    df_counties_plus = pd.read_csv("https://raw.githubusercontent.com/nytimes/covid-19-data/master/live/us-counties.csv")
    df_states_plus = pd.read_csv("https://raw.githubusercontent.com/nytimes/covid-19-data/master/live/us-states.csv")

    df_us_plus.to_sql('covid_us', engine, if_exists='append', index=False)
    df_counties_plus.to_sql('covid_counties', engine, if_exists='append', index=False)
    df_states_plus.to_sql('covid_states', engine, if_exists='append', index=False)
    end = datetime.now().strftime('%d/%m/%Y - %H:%M:%S')
    print(f'{end} - Data updated\n')

except:
    end = datetime.now().strftime('%d/%m/%Y - %H:%M:%S')
    print(f'{end} - A problem occured while updating data\n')

# prédictions des futures donneés avec des séries temporelles