import sqlite3 as sql
from .Crawler import insert_movie_data, insert_cast_data, insert_crew_data, insert_cast_credit
import requests
import json
import atexit

BASE_URL = 'https://api.themoviedb.org/3/'

with open(r'..\..\secrets.json') as f:
    secrets = json.load(f)

moviedb_secrets = secrets['moviedb']
API_KEY_3 = moviedb_secrets['API_KEY_3']
payload = {'api_key': API_KEY_3}

db = sql.connect(r'..\..\..\Data Science Data\Unit 3\db.sqlite')
atexit.register(db.close)

def get_collection_id(movie_id):
    resp = requests.get(BASE_URL + f'movie/{movie_id}', params=payload)
    resp = resp.json()
    return resp['belongs_to_collection']['id']

def get_movie_ids_from_collection(collection_id):
    resp = requests.get(BASE_URL + f'collection/{collection_id}', params=payload)
    resp = resp.json()
    unadded_movie_ids = []
    for dictionary in resp['parts']:
        unadded_movie_ids.append(dictionary['id'])
    return unadded_movie_ids

def insert_cast_credit(json, movie_id):
    logger.info('Insert cast IDs for Movie %d', movie_id)
    list_of_keys = ['id','order']
    cast = json.get('cast')
    for cast_member in cast:
        row = [cast_member.get(key) for key in list_of_keys]
        row.insert(0, movie_id)
        try:
            db.execute('INSERT INTO cast_credit VALUES (?, ?, ?)', row)
        except sql.InterfaceError:
            logger.warning('Unable to insert cast credit row %r', row)




def get_movie_data(movie_id):
    # logger.info('Fetching Movie Data for %d', movie_id)

    resp = requests.get(BASE_URL + f'movie/{movie_id}', params=payload)
    if resp.status_code == 200:
        json = resp.json()
        # Save data
        insert_movie_data(json)

    resp = requests.get(BASE_URL + f'movie/{movie_id}/credits', params=payload)
    if resp.status_code == 200:
        json = resp.json()
        insert_crew_data(json, movie_id)
        insert_cast_credit(json, movie_id)

"""
for movie_id in query:
    get collection id
    use collection id to get movie ids
    for movie in collection:
        get movie data
        save movie data
        get cast ids
        for cast member in cast:
            get cast data
            save cast data
"""



for movie_id in db.execute('SELECT movie_id FROM movies WHERE collection IS NOT NULL GROUP BY collection'):
    collection_id = get_collection_id(movie_id)
    movie_ids = get_movie_ids_from_collection(collection_id)
    for id in movie_ids:
        get_movie_data(id)
            for person_id in