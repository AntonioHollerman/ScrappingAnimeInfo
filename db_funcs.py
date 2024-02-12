from typing import List
from collections import namedtuple
import psycopg2 as pg2
from db_keys import db_config

db_conn = pg2.connect(**db_config)
db_cur = db_conn.cursor()
InfoRow = namedtuple('InfoRow', ['anime_id', 'name', 'description', 'rating', 'studio', 'themes',
                                 'categories', 'eps', 'mins_per_epi'])
InfoScrapingIndexRow = namedtuple('InfoScrapingIndexRow', ['web_id', 'category', 'page_index',
                                                           'div_index'])
UrlScrapedRow = namedtuple('UrlScrapedRow', ['web_id', 'web_url'])
ReviewRow = namedtuple('ReviewRow', ['anime_id', 'username', 'recommendation', 'review'])


def create_tables():
    sql_query = """
CREATE TABLE IF NOT EXISTS animeinfo(
    anime_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    rating DECIMAL CHECK ( rating >= 0 AND rating <= 10 ),
    studio TEXT,
    themes TEXT,
    categories TEXT,
    eps INTEGER,
    mins_per_epi INTEGER);
CREATE TABLE IF NOT EXISTS url_scraped(
    web_id SERIAL PRIMARY KEY,
    web_url TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS info_scraping_index(
    web_id INTEGER REFERENCES url_scraped(web_id),
    category TEXT,
    page_index INTEGER,
    div_index INTEGER);
CREATE TABLE IF NOT EXISTS reviews(
    anime_id INTEGER REFERENCES animeinfo(anime_id), 
    username TEXT,
    recommendation TEXT,
    review TEXT);"""
    db_cur.execute(sql_query)
    db_conn.commit()


def insert_info_row(new_row: InfoRow):
    db_cur.execute("SELECT name FROM animeinfo")
    names_in_db = set(map(lambda x: x[0], db_cur.fetchall()))
    if new_row.name in names_in_db:
        db_cur.execute(f"UPDATE animeinfo SET "
                       f"description = '{new_row.description}',"
                       f"rating = {new_row.rating},"
                       f"studio = '{new_row.studio}',"
                       f"themes = '{new_row.themes}',"
                       f"categories = '{new_row.categories}',"
                       f"eps = {new_row.eps},"
                       f"mins_per_epi = {new_row.mins_per_epi} "
                       f"WHERE name = '{new_row.name}'")
    else:
        db_cur.execute("INSERT INTO "
                       "animeinfo(name, description, rating, studio, themes, categories, eps, mins_per_epi) "
                       "VALUES "
                       f"('{new_row.name}', '{new_row.description}', {new_row.rating}, '{new_row.studio}', "
                       f"'{new_row.themes}', '{new_row.categories}', {new_row.eps}, {new_row.mins_per_epi})")
    db_conn.commit()


def insert_url_scraped(url):
    query = "SELECT DISTINCT web_url FROM url_scraped"
    db_cur.execute(query)
    urls_stored = set(map(lambda x: x[0], db_cur.fetchall()))
    if url not in urls_stored:
        db_cur.execute(f"INSERT INTO url_scraped(web_url) VALUES ('{url}')")
        db_conn.commit()


def insert_info_scraping_index(new_row: InfoScrapingIndexRow):
    db_cur.execute("SELECT DISTINCT category FROM info_scraping_index")
    categories_stored = set(map(lambda x: x[0], db_cur.fetchall()))
    if new_row.category in categories_stored:
        db_cur.execute("UPDATE info_scraping_index SET "
                       f"web_id = {new_row.web_id}, "
                       f"category = '{new_row.category}', "
                       f"page_index = {new_row.page_index}, "
                       f"div_index = {new_row.div_index} "
                       f"WHERE category = '{new_row.category}'")
    else:
        db_cur.execute("INSERT INTO info_scraping_index(web_id, category, page_index, div_index) VALUES "
                       f"({new_row.web_id}, '{new_row.category}', {new_row.page_index}, {new_row.div_index})")
    db_conn.commit()


def find_info_id(name):
    db_cur.execute(f"SELECT anime_id FROM animeinfo WHERE name = '{name}'")
    id_ = db_cur.fetchall()
    if len(id_) == 0:
        db_cur.execute(f"INSERT INTO animeinfo(name) VALUES ('{name}')")
        db_conn.commit()
        return find_info_id(name)
    else:
        return id_[0][0]


def find_url_scraped_index(url: str):
    db_cur.execute(f"SELECT web_id FROM url_scraped WHERE web_url = '{url}'")
    id_ = db_cur.fetchall()
    if len(id_) == 0:
        insert_url_scraped(url)
        db_cur.execute(f"SELECT web_id FROM url_scraped WHERE web_url = '{url}'")
        id_ = db_cur.fetchall()
        return id_[0][0]
    else:
        return id_[0][0]


def extract_info_index():
    db_cur.execute('SELECT web_id, category, page_index, div_index FROM info_scraping_index')
    info: List[InfoScrapingIndexRow] = [InfoScrapingIndexRow(*row) for row in db_cur.fetchall()]
    if info:
        holding_dict = {}
        for category in info:
            holding_dict[category.category] = {'div_index': category.div_index, 'page_index': category.page_index}
        return holding_dict
    else:
        return dict()


def insert_review_row(new_row: ReviewRow):
    id_, name, recommended, review = new_row
    db_cur.execute("INSERT INTO reviews(anime_id, username, recommendation, review) "
                   f"VALUES ({id_}, '{name}', '{recommended}', '{review}')")
    db_conn.commit()
