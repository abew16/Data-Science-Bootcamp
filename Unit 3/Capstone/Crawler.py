import sqlite3 as sql
import requests

BASE_URL = 'https://api.themoviedb.org/3/'
api_key_3 = '934559315e2d3148d261fe2f126755db'
api_key_4 = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5MzQ1NTkzMTVlMmQzMTQ4ZDI2MWZlMmYxMjY3NTVkYiIsInN1YiI6IjU5OTEwYmQ4YzNhMzY4MDZjMzAwMjQ2OSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.wFXnI4QLQckkcpYad3si4_VCqsd-ztu3pUMdrq0-K1M
'

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

db = sql.connect(':memory:')

def create_tables():
    db.execute('CREATE TABLE movies(text VARCHAR(255)), year INTEGER)')
    db.execute('CREATE TABLE people(text VARCHAR(255), year INTEGER)')

def check_if_movie_exists(movie_id):
    db.execute(...)

def save_movie(json):
    list_of_keys = [''] #Add keys that you think are important for analysis
    row = [json.get(key) for key in list_of_keys]
    db.execute('INSERT INTO movies VALUES (?, ?, ?)', row)

def save_person(json):

def save_movie_credits(json):

def save_people_credits(json):



def check_if_movie_exists(movie_id):
        select_movie = db.execute('SELECT COUNT(*) FROM movie_table WHERE movie_id=?', movie_id)
        count_of_movies = select_movie.fetchone()
        return count_of_movies > 0


def get_movie(movie_id):
    #if movie_id in seen_movies:
    if check_if_movie_exists(movie_id):
        return

    # Fetch movie data
    resp = requests.get(BASE_URL + f'movie/{movie_id}')
    json = resp.json()

    # Save data
    insert_movie(json)

    resp = requests.get(BASE_URL + f'movie/{movie_id}/credits')
    json = resp.json()

    save_movie_credits(json)

    # Mark as seen
    seen_movies.add(movie_id)



def get_credits(credit_id):
    if check_if_credit_exists(credit_id):
        return

    resp = requests.get(BASE_URL + f'credits/{credit_id}')
    json = resp.json()

    save_credits(json)

    seen_credits.add(credit_id)

def get_person(person_id):
    if check_if_person_exists(person_id):
        return

    resp = requests.get(BASE_URL + f'person/{person_id}')
    json = resp.json()

    save_person(json)

    resp = requests.get(BASE_URL + f'person/{person_id}/movie_credits')
    json = resp.json()

    save_people_credits(json)

    seen_people.add(person_id)



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
