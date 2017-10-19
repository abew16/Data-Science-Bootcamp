import sqlite3 as sql
import atexit
from contextlib import suppress
import logging
from bs4 import BeautifulSoup
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""
1) Grab imdb_id for row in db if revenue is null
2) Fetch revenue & budget from imdb if available
 - imdb.com/title/[movie_id]/business
3) Insert revenue & budget into db row
"""

db = sql.connect(r'..\..\..\Data Science Data\Unit 3\db.sqlite')
atexit.register(db.close)


# Make new columns in db

def insert_db_columns():
    db.execute('ALTER TABLE movies ADD COLUMN imdb_budget integer')
    db.execute('ALTER TABLE movies ADD COLUMN imdb_revenue integer')


BASE_URL = 'http://imdb.com/title/'
END_URL = '/business'


def get_rev_bud(imdb_id):
    logger.info('Get data for movie %s', imdb_id)
    resp = requests.get(BASE_URL + imdb_id[0] + END_URL)

    resp_text = resp.text
    soup = BeautifulSoup(resp_text, 'lxml')
    content = soup.find(id='tn15content')

    if content is None:
        logger.warning('imdb_id %s does not have a properly formatted page')
        return None, None
    budget = revenue = None

    next_is_budget = False
    next_is_revenue = False
    for item in content:
        if next_is_budget:
            budget_raw = item.split()[0]
            budget = budget_raw.translate({ord(c): None for c in '$,'})
            next_is_budget = False
        if getattr(item, 'text', '') == 'Budget':
            next_is_budget = True
        if next_is_revenue:
            revenue_raw = item.split()[0]
            revenue = revenue_raw.translate({ord(c): None for c in '$,'})
            next_is_revenue = False
        if getattr(item, 'text', '') == 'Gross':
            next_is_revenue = True
    return budget, revenue


def insert_data(imdb_id, budget, revenue):
    logger.info('Inserting data for %s', imdb_id)
    db.execute('UPDATE movies SET imdb_revenue = ?, imdb_budget = ? WHERE imdb_id = ?', (revenue, budget, imdb_id[0]))


with suppress(Exception):
    insert_db_columns()

for imdb_id in db.execute('SELECT imdb_id FROM movies WHERE (revenue IS NULL OR revenue = "" OR revenue = 0) AND (imdb_revenue IS NULL)'):
    try:
        budget, revenue = get_rev_bud(imdb_id)
        insert_data(imdb_id, budget, revenue)
        db.commit()
    except TypeError:
        logger.error('Error in main loop', exc_info=True)
