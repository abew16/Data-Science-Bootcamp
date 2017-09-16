import sqlite3 as sql
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = 'https://api.themoviedb.org/3/'
API_KEY_3 = '934559315e2d3148d261fe2f126755db'
API_KEY_4 = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5MzQ1NTkzMTVlMmQzMTQ4ZDI2MWZlMmYxMjY3NTVkYiIsInN1YiI6IjU5OTEwYmQ4YzNhMzY4MDZjMzAwMjQ2OSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.wFXnI4QLQckkcpYad3si4_VCqsd-ztu3pUMdrq0-K1M'
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
unseen_people_ids = set()
unseen_movie_ids = {819}

db = sql.connect(r'..\..\..\Data Science Data\Unit 3\db.sqlite')


def create_tables():
    logger.info('Creating Tables')
    db.execute('CREATE TABLE IF NOT EXISTS movies(movie_id integer,'
               '                    budget integer,'
               '                    release_date text, '
               '                    revenue integer,'
               '                    runtime integer,'
               '                    title text)')
    db.execute('CREATE TABLE IF NOT EXISTS genres(movie_id text,'
               '                    genre_name text)')
    db.execute('CREATE TABLE IF NOT EXISTS production_companies(movie_id text,'
               '                                  company_name text)')
    db.execute('CREATE TABLE IF NOT EXISTS cast(movie_id integer,'
               '                    name text,'
               '                    gender integer,'
               '                    cast_order integer)')
    db.execute('CREATE TABLE IF NOT EXISTS crew(movie_id integer,'
               '                    crew_member_id integer,'
               '                    name text,'
               '                    gender integer,'
               '                    job text)')


def insert_cast_data(json, movie_id):
    logger.info('Insert Cast Data for Movie %d', movie_id)
    list_of_keys = ['name', 'gender','order']  # Add keys that you think are important for analysis
    cast = json.get('cast')
    for cast_member in cast:
        row = [cast_member.get(key) for key in list_of_keys]
        row.insert(0, movie_id)
        db.execute('INSERT INTO cast VALUES (?, ?, ?, ?)', row)
        # unseen_people_ids.add(cast_member['id'])
        with open(r'..\..\..\Data Science Data\Unit 3\unseen_people.txt') as f:
            f.write(cast_member['id'])

def insert_crew_data(json, movie_id):
    logger.info('Insert Crew Data for Movie %d', movie_id)
    list_of_keys = ['id','name', 'gender','job']  # Add keys that you think are important for analysis
    crew = json.get('crew')
    for crew_member in crew:
        row = [crew_member.get(key) for key in list_of_keys]
        row.insert(0, movie_id)
        db.execute('INSERT INTO crew VALUES (?, ?, ?, ?, ?)', row)


def insert_movie_data(json):
    movie_id = json['id']
    logger.info('Insert Movie Data for Movie %d', movie_id)
    # Insert flat movie data into movies table
    list_of_keys = ['id', 'budget', 'release_date', 'revenue', 'runtime', 'title']
    row = [json.get(key) for key in list_of_keys]
    db.execute('INSERT INTO movies VALUES (?, ?, ?, ?, ?, ?)', row)

    # Insert nested genre data into genre table
    genres = json['genres']
    production_companies = json.get('production_companies')

    for genre_list in genres:
        genre = genre_list.get('name')
        row = [movie_id, genre]
        db.execute('INSERT INTO genres VALUES (?, ?)', row)

    for company_list in production_companies:
        company = company_list.get('name')
        row = [movie_id, company]
        db.execute('INSERT INTO production_companies VALUES (?, ?)', row)


def insert_movie_ids(json):
    person_id = json['id']
    logger.info('Insert Movie IDs from person %d', person_id)
    cast = json['cast']
    for movie in cast:
        # unseen_movie_ids.add(movie['id'])
        with open(r'..\..\..\Data Science Data\Unit 3\unseen_movies.txt') as f:
            f.write(movie)


def check_if_movie_exists(movie_id):
    return movie_id in seen_movies

def check_if_person_exists(person_id):
    return person_id in seen_people


def get_movie_data(movie_id):
    logger.info('Fetching Movie Data for %d', movie_id)
    if check_if_movie_exists(movie_id):
        return

    # Fetch movie data
    resp = requests.get(BASE_URL + f'movie/{movie_id}', params=payload)
    json = resp.json()

    # Save data
    insert_movie_data(json)

    resp = requests.get(BASE_URL + f'movie/{movie_id}/credits', params=payload)
    json = resp.json()

    # Save the cast & crew of the movie
    insert_cast_data(json, movie_id)
    insert_crew_data(json, movie_id)

    # Mark as seen
    seen_movies.add(movie_id)


def get_movie_ids_from_person(person_id):
    logger.info('Fetching Movie IDs for person id %d', person_id)
    if check_if_person_exists(person_id):
        return

    resp = requests.get(BASE_URL + f'person/{person_id}/movie_credits', params=payload)
    json = resp.json()

    insert_movie_ids(json)

    seen_people.add(person_id)


# DB M1 M2
# [M3 M6 M5 M7]
# [P5 P9]
# DB P1 P2 P3

create_tables()



while len(seen_movies) < 2:
    while len(unseen_movie_ids) > 0:
        movie_id = unseen_movie_ids.pop()
        get_movie_data(movie_id)
        db.commit()

    while len(unseen_people_ids) > 0:
        person_id = unseen_people_ids.pop()
        get_movie_ids_from_person(person_id)
        db.commit()

db.close()

# Adjust check if movie exists functions so it checks against the db
# SQLite create index
# Add code so you can pick up where you left off. Add unseen movies to db or write to file