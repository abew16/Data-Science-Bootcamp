import sqlite3 as sql

import requests

BASE_URL = 'https://...'

seen_movies = set()
seen_people = set()

db = sql.connect(':memory:')

def create_tables():
    db.execute('CREATE TABLE movies(text VARCHAR(255), year INTEGER)')
    db.execute('CREATE TABLE people(text VARCHAR(255), year INTEGER)')

def check_if_movie_exists(movie_id):
    db.execute(...)

def insert(json_obj):
    row = (title, year)
    db.execute('INSERT INTO movies VALUES (?, ?, ?)', row)

person_list = []

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

def get_movie(movie_id):
    #if movie_id in seen_movies:
    if check_if_movie_exists(movie_id):
        return

    # Fetch movie data
    resp = requests.get(BASE_URL + f'movie/3/{movie_id}')
    json = resp.json()

    # Save data
    insert(json)

    # Mark as seen
    seen_movies.add(json['movie_id'])

    # Extract people
    people = json['people']
    for person in people:
        person_list.append(person)
        # save_person(person)

movie_list = []

def get_person(person_id):
    resp = requests.get(BASE_URL + f'people/3/{person_id}')
    json = resp.json()

    movies = json['movies']
    for movie in movies:
        movie_list.append(movie)

# DB M1 M2
# [M3 M6 M5 M7]
# [P5 P9]
# DB P1 P2 P3

while len(db) < 1000:
    while len(movie_list) > 0:
        movie_id = movie_list.pop()
        get_movie(movie_id)

    while len(person_list) > 0:
        person_id = person_list.pop()
        get_person(person_id)

def fib(n):
    return fib(n-1) + fib(n-2)

def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a+b
    return b

fib(30)
