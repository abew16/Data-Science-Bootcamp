import sqlite3 as sql
import requests

BASE_URL = 'https://api.themoviedb.org/3/'
API_KEY_3 = '934559315e2d3148d261fe2f126755db'
API_KEY_4 = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5MzQ1NTkzMTVlMmQzMTQ4ZDI2MWZlMmYxMjY3NTVkYiIsInN1YiI6IjU5OTEwYmQ4YzNhMzY4MDZjMzAwMjQ2OSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.wFXnI4QLQckkcpYad3si4_VCqsd-ztu3pUMdrq0-K1M'

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
seen_credits = set()
unseen_people_id = []
unseen_movie_id = []

db = sql.connect(':memory:')


def create_tables():
    db.execute('CREATE TABLE movies(movie_id integer,'
               '                    budget integer,'
               '                    release_date text, '
               '                    production_companies text,'
               '                    revenue integer,'
               '                    runtime integer,'
               '                    title text)')
    db.execute('CREATE TABLE genres(movie_id text,'
               '                    genre_name text)')
    db.execute('CREATE TABLE production_companies(movie_id text,'
               '                                  company_name text)')
    db.execute('CREATE TABLE people(movie_id integer,'
               '                    name text,'
               '                    gender integer,'
               '                    order integer)')


def insert_people_data(json):
    list_of_keys = ['']  # Add keys that you think are important for analysis
    row = [json.get(key) for key in list_of_keys]
    db.execute('INSERT INTO people VALUES (?, ?, ?, ?)', row)


def insert_movie_data(json):
    # Insert flat movie data into movies table
    list_of_keys = ['move_id', 'budget', 'release_date', 'revenue', 'runtime', 'title']
    row = [json.get(key) for key in list_of_keys]
    db.execute('INSERT INTO movies VALUES (?, ?, ?, ?, ?, ?)', row)

    # Insert nested genre data into genre table
    row = [json.get(list_of_keys[0])]
    row.append([x.get('name') for x in json.get('genres')])
    db.execute('INSERT INTO genres VALUES (?, ?)', row)

    # Insert nested production company data into production_companies table
    row = [json.get(list_of_keys[0])]
    row.append([x.get('name') for x in json.get('production_companies')])
    db.execute('INSERT INTO genres VALUES (?, ?)', row)

def insert_movie_ids(json):
    list_of_keys = ['id']  # Add keys that you think are important for analysis
    row = [json.get(key) for key in list_of_keys]
    db.execute('INSERT INTO people VALUES (?, ?, ?)', row)


def save_people_credits(json):
    return


def check_if_movie_exists(movie_id):
    movie_id in seen_movies
    return True


def get_movie(movie_id):
    if check_if_movie_exists(movie_id):
        return

    # Fetch movie data
    resp = requests.get(BASE_URL + f'movie/{movie_id}')
    json = resp.json()

    # Save data
    insert_movie_data(json)

    resp = requests.get(BASE_URL + f'movie/{movie_id}/credits')
    json = resp.json()

    # Save the cast of the movie
    insert_people_data(json)

    # Mark as seen
    seen_movies.add(movie_id)


def check_if_person_exists(person_id):
    person_id in seen_people
    return True


def get_person(person_id):
    if check_if_person_exists(person_id):
        return

    resp = requests.get(BASE_URL + f'person/{person_id}/movie_credits')
    json = resp.json()

    insert_movie_ids(json)

    seen_people.add(person_id)


# DB M1 M2
# [M3 M6 M5 M7]
# [P5 P9]
# DB P1 P2 P3

while len(db) < 10000:
    while len(movie_list) > 0:
        movie_id = movie_list.pop()
        get_movie(movie_id)

    while len(person_list) > 0:
        person_id = person_list.pop()
        get_person(person_id)

