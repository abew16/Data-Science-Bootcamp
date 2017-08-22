import json
import sqlite3 as sql
from contextlib import suppress
import requests
import logging
import atexit

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = 'https://api.themoviedb.org/3/'

with open(r'..\..\secrets.json') as f:
    secrets = json.load(f)

moviedb_secrets = secrets['moviedb']
API_KEY_3 = moviedb_secrets['API_KEY_3']
payload = {'api_key' : API_KEY_3}

"""
For movies, credits, and people
1. take object ID as input
2. fetch data from API
3. save data to DB
4. extract relevant IDs
  - movie -> extract credit IDs
  - credits -> extract people and movie IDs
  - people -> extract credit IDs
5. record that you've fetched this ID
"""

seen_movies = set()
seen_people = set()


# Open files and create sets from what's inside to pick up where we left off
with open(r'..\..\..\Data Science Data\Unit 3\unseen_movies.txt','r') as f:
    unseen_movie_ids = set(map(int,f.readlines()))
if not unseen_movie_ids:
    unseen_movie_ids.add(819)
with open(r'..\..\..\Data Science Data\Unit 3\unseen_people.txt', 'r') as f:
    unseen_people_ids = set(map(int, f.readlines()))

# Open files so we can write in order to pick up where we leave off
unseen_movie_file = open(r'..\..\..\Data Science Data\Unit 3\unseen_movies.txt','w')
unseen_people_file = open(r'..\..\..\Data Science Data\Unit 3\unseen_people.txt','w')

atexit.register(unseen_movie_file.close)
atexit.register(unseen_people_file.close)

db = sql.connect(r'..\..\..\Data Science Data\Unit 3\db.sqlite')
atexit.register(db.close)


def create_tables():
    logger.info('Creating Tables')
    db.execute('CREATE TABLE IF NOT EXISTS movies(movie_id integer,'
               '                    budget integer,'
               '                    release_date text, '
               '                    revenue integer,'
               '                    runtime integer,'
               '                    title text,'
               '                    collection text)')
    db.execute('CREATE UNIQUE INDEX IF NOT EXISTS movie_id_index ON movies(movie_id)')
    db.execute('CREATE TABLE IF NOT EXISTS genres(movie_id text,'
               '                    genre_name text)')
    db.execute('CREATE INDEX IF NOT EXISTS movie_id_index ON genres(movie_id)')
    db.execute('CREATE TABLE IF NOT EXISTS production_companies(movie_id text,'
               '                                  company_name text)')
    db.execute('CREATE INDEX IF NOT EXISTS movie_id_index ON production_companies(movie_id)')
    db.execute('CREATE TABLE IF NOT EXISTS cast_credit(movie_id integer,'
               '                    cast_member_id integer,'
               '                    cast_order integer)')
    db.execute('CREATE INDEX IF NOT EXISTS movie_id_index ON cast_credit(movie_id)')
    db.execute('CREATE TABLE IF NOT EXISTS cast(cast_member_id integer,'
               '                    name text,'
               '                    gender integer)')
    db.execute('CREATE INDEX IF NOT EXISTS cast_member_id ON cast(cast_member_id)')
    db.execute('CREATE TABLE IF NOT EXISTS crew(movie_id integer,'
               '                    crew_member_id integer,'
               '                    name text,'
               '                    gender integer,'
               '                    job text)')
    db.execute('CREATE INDEX IF NOT EXISTS movie_id_index ON crew(movie_id)')



def insert_cast_data(json, person_id):
    list_of_keys = ['id', 'name','gender']  # Add keys that you think are important for analysis
    row = [json.get(key) for key in list_of_keys]
    try:
        db.execute('INSERT INTO cast VALUES (?, ?, ?)', row)
    except sql.InterfaceError:
        logger.warning('Unable to insert cast credit row %r', row)


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
        if cast_member['id'] not in unseen_people_ids:
            unseen_people_ids.add(cast_member['id'])
            unseen_people_file.write('{}\n'.format(cast_member['id']))
    unseen_people_file.flush()


def insert_crew_data(json, movie_id):
    logger.info('Insert Crew Data for Movie %d', movie_id)
    list_of_keys = ['id','name', 'gender','job']  # Add keys that you think are important for analysis
    crew = json.get('crew')
    for crew_member in crew:
        row = [crew_member.get(key) for key in list_of_keys]
        row.insert(0, movie_id)
        try:
            db.execute('INSERT INTO crew VALUES (?, ?, ?, ?, ?)', row)
        except sql.InterfaceError:
            logger.warning('Unable to insert crew data row %r', row)



def insert_movie_data(json):
    movie_id = json['id']
    logger.info('Insert Movie Data for Movie %d', movie_id)
    # Insert flat movie data into movies table
    list_of_keys = ['id', 'budget', 'release_date', 'revenue', 'runtime', 'title']
    row = [json.get(key) for key in list_of_keys]
    if json['belongs_to_collection'] is not None:
        row.append(json['belongs_to_collection']['name'])
    else:
        row.append(None)
    try:
        db.execute('INSERT INTO movies VALUES (?, ?, ?, ?, ?, ?, ?)', row)
    except sql.InterfaceError:
        logger.warning('Unable to insert movie data row %r', row)

    # Insert nested genre data into genre table
    genres = json['genres']
    production_companies = json.get('production_companies')

    for genre_list in genres:
        genre = genre_list.get('name')
        row = [movie_id, genre]
        try:
            db.execute('INSERT INTO genres VALUES (?, ?)', row)
        except sql.InterfaceError:
            logger.warning('Unable to insert genre data row %r', row)

    for company_list in production_companies:
        company = company_list.get('name')
        row = [movie_id, company]
        try:
            db.execute('INSERT INTO production_companies VALUES (?, ?)', row)
        except sql.InterfaceError:
            logger.warning('Unable to insert production company data row %r', row)


def insert_movie_ids(json):
    person_id = json['id']
    logger.info('Insert Movie IDs from person %d', person_id)
    cast = json['cast']
    for movie in cast:
        if movie['id'] not in unseen_movie_ids:
            unseen_movie_ids.add(movie['id'])
            unseen_movie_file.write('{}\n'.format(movie['id']))
    unseen_movie_file.flush()

def check_if_movie_exists(movie_id):
    # return movie_id in seen_movies
    data = db.execute('SELECT COUNT(movie_id) FROM movies WHERE movie_id = (?)', (movie_id,))
    return data.fetchone()[0] > 0

def check_if_person_exists(person_id):
    # return person_id in seen_people
    data = db.execute('SELECT COUNT(cast_member_id) FROM cast WHERE cast_member_id = (?)', (person_id,))
    return data.fetchone()[0] > 0


def get_movie_data(movie_id):
    logger.info('Fetching Movie Data for %d', movie_id)
    if check_if_movie_exists(movie_id):
        return

    # Fetch movie data
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


    # Mark as seen
    seen_movies.add(movie_id)


def get_movie_ids_from_person(person_id):
    logger.info('Fetching Movie IDs for person id %d', person_id)
    if check_if_person_exists(person_id):
        return

    resp = requests.get(BASE_URL + f'person/{person_id}/', params=payload)
    if resp.status_code == 200:
        json = resp.json()
        insert_cast_data(json, person_id)

    resp = requests.get(BASE_URL + f'person/{person_id}/movie_credits', params=payload)
    if resp.status_code == 200:
        json = resp.json()
        insert_movie_ids(json)

    seen_people.add(person_id)


# DB M1 M2
# [M3 M6 M5 M7]
# [P5 P9]
# DB P1 P2 P3

create_tables()



while True:
    with suppress(Exception):
        while len(unseen_movie_ids) > 0:
            movie_id = unseen_movie_ids.pop()
            get_movie_data(movie_id)
            db.commit()

        while len(unseen_people_ids) > 0:
            person_id = unseen_people_ids.pop()
            get_movie_ids_from_person(person_id)
            db.commit()

# Separate inserting data & queuing data
# get movie = Get movie data > Insert to database > queue people IDs (similar for get people data)
