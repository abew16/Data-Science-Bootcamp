import sqlite3 as sql
from contextlib import suppress
import atexit
import requests
import json

BASE_URL = 'https://api.themoviedb.org/3/'

with open(r'..\..\secrets.json') as f:
    secrets = json.load(f)

moviedb_secrets = secrets['moviedb']
API_KEY_3 = moviedb_secrets['API_KEY_3']
payload = {'api_key': API_KEY_3}

db = sql.connect(r'..\..\..\Data Science Data\Unit 3\db.sqlite')
atexit.register(db.close)


def insert_db_columns():
    db.execute('ALTER TABLE movies ADD COLUMN imdb_id text')
    db.execute('ALTER TABLE cast ADD COLUMN imdb_id text')


def get_imdb_movie_id(tmdb_movie_id):
    resp = requests.get(BASE_URL + f'movie/{tmdb_movie_id}', params=payload)
    movie_data = resp.json()
    return movie_data['imdb_id']


def get_imdb_person_id(tmdb_person_id):
    resp = requests.get(BASE_URL + f'person/{tmdb_person_id}', params=payload)
    person_data = resp.json()
    return person_data['imdb_id']


def update_imdb_movie_id(imdb_id, tmdb_movie_id):
    db.execute('UPDATE movies SET imdb_id = ? WHERE movie_id = ?', (imdb_id, tmdb_movie_id))


def update_imdb_person_id(imdb_id, tmdb_person_id):
    db.execute('UPDATE cast SET imdb_id = ? WHERE cast_member_id = ?', (imdb_id, tmdb_person_id))


with suppress(Exception):
    insert_db_columns()

for (movie_id,) in db.execute('SELECT movie_id FROM movies WHERE imdb_id IS NULL'):
    imdb_movie_id = get_imdb_movie_id(movie_id)
    update_imdb_movie_id(imdb_movie_id, movie_id)
    db.commit()

for (person_id,) in db.execute('SELECT cast_member_id FROM cast WHERE imdb_id IS NULL'):
    imdb_person_id = get_imdb_person_id(person_id)
    update_imdb_person_id(imdb_person_id, person_id)
    db.commit()
