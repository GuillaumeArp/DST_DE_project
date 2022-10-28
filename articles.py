import os
import json
import time
import datetime
import requests
from dotenv import load_dotenv

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()
KEY=os.getenv("APIKEY")
USERNAME=os.getenv("USERNAME")
USERPWD=os.getenv("USERPWD")
FOLDER_PATH = '/home/guillaume/Python_Projects/DST_DE_project'

client = MongoClient(
    f"mongodb+srv://{USERNAME}:{USERPWD}@nyt-de.ganwi.mongodb.net/?retryWrites=true&w=majority",
    server_api=ServerApi('1'),
    serverSelectionTimeoutMS=5000
)

db = client.nyt
col = db['articles']

def get_articles_update(filename, clean=True):
    """Requests articles about Covid-19 from the New York Times API, returns a list of dictionaries, and saves it to a json file.

    Args:
        filename (str): Name of the json file to save the articles to.
        clean (bool, optional): Toggles the cleaning of unwanted keys. Defaults to True.

    Returns:
        list: a list object containing dictionaries of articles data.
    """
    
    results_list = []
    request_headers = {"Accept": "application/json"}
    
    with open(f'{FOLDER_PATH}/src/begin_date.txt', 'r') as read_begin_date:
        begin_date = read_begin_date.read()
        
    begin_dt = datetime.datetime.strptime(read_begin_date, '%Y%m%d')
    end_dt = datetime.datetime.strptime(begin_date, '%Y%m%d')
    end_dt += datetime.timedelta(days=7)
    end_date = end_dt.strftime('%Y%m%d')
    
    for i in range(101):
        url = f"https://api.nytimes.com/svc/search/v2/articlesearch.json?begin_date={begin_date}&end_date={end_date}&fq=headline%3A(%22covid%22%20%22coronavirus%22)&page={i}&sort=oldest&api-key={KEY}"
        
        try:
            response = requests.get(url, headers=request_headers).json()
            response_list = response['response']['docs']
            
            for j in response_list:
                results_list.append(j)

            time.sleep(6.1)
            
        except:
            break
        
    new_begin_dt = begin_dt + datetime.timedelta(days=8)
    new_begin_date = new_begin_dt.strftime('%Y%m%d')
    
    with open(f'{FOLDER_PATH}/src/begin_date.txt', 'w') as outfile:
        outfile.write(new_begin_date)
            
    if clean:
        lst_clean = results_list.copy()
        for i in lst_clean:
            i.pop('multimedia', None)

        with open(f"{FOLDER_PATH}/src/{filename}", 'w') as outfile:
            json.dump(lst_clean, outfile, indent=4)

        return lst_clean
    
    else:
        with open(f"{FOLDER_PATH}/src/{filename}", 'w') as outfile:
            json.dump(results_list, outfile, indent=4)
        
        return results_list
    
def upload_articles_to_mongo(articles):
    """Uploads a list of articles to a MongoDB database.

    Args:
        articles_update (list): list of dictionaries containing articles data.
    Returns:
        None
    """
    articles = get_articles_update(f'{FOLDER_PATH}/articles_update.json')
    col.insert_many(articles)
