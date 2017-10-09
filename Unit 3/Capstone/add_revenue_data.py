import sqlite3 as sql
import atexit
import bs4
import requests

"""
1) Grab imdb_id for row in db if revenue is null
2) Fetch revenue & budget from imdb if available
 - imdb.com/title/[movie_id]/business
3) Insert revenue & budget into db row
"""

db = sql.connect(r'..\..\..\Data Science Data\Unit 3\db.sqlite')
atexit.register(db.close)

BASE_URL = 'http://imdb.com/title/'
END_URL = '/business'

def get_rev_bud(imdb_id):
    resp = requests.get(BASE_URL + imdb_id + END_URL)


def insert_data(revenue, budget, imdb_id):
    db.execute('UPDATE movies SET revenue = ? AND budget = ? WHERE imdb_id = ?', (revenue, budget, imdb_id))


for imdb_id in db.execute('SELECT imdb_id FROM movies WHERE revenue IS NULL AND revenue != "" AND revenue = 0'):
    money_data = get_rev_bud(imdb_id)
    insert_data(money_data)


