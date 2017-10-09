import sqlite3 as sql
from Crawler import insert_movie_data, insert_crew_data, check_if_movie_exists, db
import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = 'https://api.themoviedb.org/3/'

with open(r'..\..\secrets.json') as f:
    secrets = json.load(f)

moviedb_secrets = secrets['moviedb']
API_KEY_3 = moviedb_secrets['API_KEY_3']
payload = {'api_key': API_KEY_3}


def get_collection_id(movie_id):
    logger.info('Get collection id for %d', movie_id)
    resp = requests.get(BASE_URL + f'movie/{movie_id}', params=payload)
    resp = resp.json()
    return resp['belongs_to_collection']['id']


def get_movie_ids_from_collection(collection_id):
    resp = requests.get(BASE_URL + f'collection/{collection_id}', params=payload)
    resp = resp.json()
    return [item['id'] for item in resp['parts']]


def create_cast_id_list(movie_id):
    resp = requests.get(BASE_URL + f'movie/{movie_id}/credits', params=payload)
    json = resp.json()
    cast = json.get('cast')
    return [person.get('id') for person in cast]


def insert_cast_credit(json, movie_id):
    logger.info('Insert cast IDs for Movie %d', movie_id)
    list_of_keys = ['id', 'order']
    cast = json.get('cast')
    for cast_member in cast:
        row = [cast_member.get(key) for key in list_of_keys]
        row.insert(0, movie_id)
        try:
            db.execute('INSERT INTO cast_credit VALUES (?, ?, ?)', row)
        except sql.InterfaceError:
            logger.warning('Unable to insert cast credit row %r', row)


def insert_cast_data(person_id):
    logger.info('Insert cast data for %d', person_id)
    list_of_keys = ['id', 'name', 'gender', 'imdb_id']  # Add keys that you think are important for analysis
    resp = requests.get(BASE_URL + f'person/{person_id}/', params=payload)
    if resp.status_code == 200:
        json = resp.json()
        row = [json.get(key) for key in list_of_keys]
        try:
            db.execute('INSERT INTO cast VALUES (?, ?, ?, ?)', row)
        except sql.InterfaceError:
            logger.warning('Unable to insert cast credit row %r', row)


def get_movie_data(movie_id):
    logger.info('Fetching Movie Data for %d', movie_id)
    resp = requests.get(BASE_URL + f'movie/{movie_id}', params=payload)
    if resp.status_code == 200:
        json = resp.json()
        insert_movie_data(json)

    resp = requests.get(BASE_URL + f'movie/{movie_id}/credits', params=payload)
    if resp.status_code == 200:
        json = resp.json()
        insert_crew_data(json, movie_id)
        insert_cast_credit(json, movie_id)
        return json


"""
for movie_id in query:
    get collection id
    use collection id to get movie ids
    for movie in collection:
        get/save movie data
        get cast ids
        for cast member in cast:
            get cast data
            save cast data
"""

for (movie_id,) in db.execute('SELECT movie_id FROM movies WHERE collection IS NOT NULL AND collection != "" GROUP BY collection'):
    collection_id = get_collection_id(movie_id)
    movie_ids = get_movie_ids_from_collection(collection_id)
    for movie in movie_ids:
        if check_if_movie_exists(movie):
            continue
        get_movie_data(movie)
        cast_ids = create_cast_id_list(movie)
        for person in cast_ids:
            insert_cast_data(person)
