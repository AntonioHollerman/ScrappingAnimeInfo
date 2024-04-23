from typing import List
from collections import namedtuple
import psycopg2 as pg2
from db_keys import db_config

# Connects to PostgreSQL Database
db_conn = pg2.connect(**db_config)
db_cur = db_conn.cursor()

# animeinfo table attributes
InfoRow = namedtuple('InfoRow', ['anime_id', 'name', 'description', 'rating', 'studio', 'themes',
                                 'categories', 'eps', 'mins_per_epi'])

InfoScrapingIndexRow = namedtuple('InfoScrapingIndexRow', ['web_id', 'category', 'page_index',
                                                           'div_index'])
UrlScrapedRow = namedtuple('UrlScrapedRow', ['web_id', 'web_url'])
ReviewRow = namedtuple('ReviewRow', ['anime_id', 'username', 'recommendation', 'review'])


def create_tables():
    """
    Creates the following tables if they do not exist in the database. Tables names: animeinfo,
    Returns: None

    """
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
    """
    Adds a new row to the animeinfo table in the database. Updates row information instead if the anime name already
    in the table.
    Args:
        new_row: A named tuple holding the information to be added

    Returns: None

    """

    # Extracts the name for each anime
    db_cur.execute("SELECT name FROM animeinfo")
    names_in_db = set(map(lambda x: x[0], db_cur.fetchall()))

    # Checks if the anime to be added into the database exists already
    if new_row.name in names_in_db:
        # Updates anime row of information if it exists already
        db_cur.execute("UPDATE animeinfo SET "
                       "description = '{}',".format(new_row.description.replace("'", "''")) +
                       "rating = {},".format(new_row.rating) +
                       "studio = '{}',".format(new_row.studio.replace("'", "''")) +
                       "themes = '{}',".format(new_row.themes.replace("'", "''")) +
                       "categories = '{}',".format(new_row.categories.replace("'", "''")) +
                       "eps = {}, ".format(new_row.eps) +
                       "mins_per_epi = {} ".format(new_row.mins_per_epi) +
                       "WHERE name = '{}'".format(new_row.name.replace("'", "''")))
    else:
        # Inserts a new row of information if anime not in database already
        format1 = (new_row.name.description.replace("'", "''"),
                   new_row.description.description.replace("'", "''"),
                   new_row.rating,
                   new_row.studio.description.replace("'", "''"))

        format2 = (new_row.themes.description.replace("'", "''"),
                   new_row.categories.description.replace("'", "''"),
                   new_row.eps,
                   new_row.mins_per_epi)
        db_cur.execute("INSERT INTO "
                       "animeinfo(name, description, rating, studio, themes, categories, eps, mins_per_epi) "
                       "VALUES "
                       "('{}', '{}', {}, '{}', ".format(*format1) +
                       "'{}', '{}', {}, {})".format(*format2))
    db_conn.commit()


def insert_url_scraped(url):
    """
    Inserts a new url scrapped if it does not exist already
    Args:
        url: The hyperlink scrapped from

    Returns: None

    """
    query = "SELECT DISTINCT web_url FROM url_scraped"
    db_cur.execute(query)
    urls_stored = set(map(lambda x: x[0], db_cur.fetchall()))
    if url not in urls_stored:
        db_cur.execute("INSERT INTO url_scraped(web_url) VALUES ('{}')".format(url.replace("'", "''")))
        db_conn.commit()


def insert_info_scraping_index(new_row: InfoScrapingIndexRow):
    """
    Updates information in the info_scrapping_index table to save what pages were scrapped already
    Args:
        new_row: Row to be inserted or updated if it exists already

    Returns: None

    """

    # Gets all the categories of anime to scrape
    db_cur.execute("SELECT DISTINCT category FROM info_scraping_index")
    categories_stored = set(map(lambda x: x[0], db_cur.fetchall()))

    if new_row.category in categories_stored:
        # Updates category if it exists
        db_cur.execute("UPDATE info_scraping_index SET "
                       "web_id = {}, ".format(new_row.web_id) +
                       "category = '{}', ".format(new_row.category.replace("'", "''")) +
                       "page_index = {}, ".format(new_row.page_index) +
                       "div_index = {} ".format(new_row.div_index) +
                       "WHERE category = '{}'".format(new_row.category.replace("'", "''")))
    else:
        # Inserts new category if it does not exist
        db_cur.execute("INSERT INTO info_scraping_index(web_id, category, page_index, div_index) VALUES "
                       "({}, '{}', {}, {})".format(new_row.web_id,
                                                   new_row.category.replace("'", "''"),
                                                   new_row.page_index,
                                                   new_row.div_index))
    db_conn.commit()


def find_info_id(name: str) -> int:
    """
    Uses anime name to retrieve its id
    Args:
        name: The anime name of id wanted

    Returns: The anime id

    """
    db_cur.execute("SELECT anime_id FROM animeinfo WHERE name = '{}'".format(name.replace("'", "''")))
    id_ = db_cur.fetchall()
    if len(id_) == 0:
        db_cur.execute("INSERT INTO animeinfo(name) VALUES ('{}')".format(name.replace("'", "''")))
        db_conn.commit()
        return find_info_id(name)
    else:
        return id_[0][0]


def find_url_scraped_index(url: str) -> int:
    """
    Fetches the id that belongs to the url
    Args:
        url: Hyper link saved or to be added id wanted

    Returns: The hyperlink id

    """
    db_cur.execute("SELECT web_id FROM url_scraped WHERE web_url = '{}'".format(url.replace("'", "''")))
    id_ = db_cur.fetchall()
    if len(id_) == 0:
        insert_url_scraped(url)
        db_cur.execute("SELECT web_id FROM url_scraped WHERE web_url = '{}'".format(url.replace("'", "''")))
        id_ = db_cur.fetchall()
        return id_[0][0]
    else:
        return id_[0][0]


def extract_info_index() -> dict:
    """
    Converts the info_scraping_index table into a python dictionary
    Returns: A dictionary of categories and pages scrapped

    """
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
    """

    Args:
        new_row:(Don't kill yourself<3 - Love Kathyad S.S)

    Returns:

    """
    id_, name, recommended, review = new_row
    db_cur.execute("INSERT INTO reviews(anime_id, username, recommendation, review) "
                   "VALUES ({}, '{}', '{}', '{}')".format(id_,
                                                          name.replace("'", "''"),
                                                          recommended.replace("'", "''"),
                                                          review.replace("'", "''")))
    db_conn.commit()


def check_review_null():
    db_cur.execute("UPDATE reviews SET "
                   "username = NULL "
                   "WHERE username = 'NULL'")

    db_cur.execute("UPDATE reviews SET "
                   "recommendation = NULL "
                   "WHERE recommendation = 'NULL'")

    db_cur.execute("UPDATE reviews SET "
                   "review = NULL "
                   "WHERE review = 'NULL'")
    db_conn.commit()


def check_info_null():
    db_cur.execute("UPDATE animeinfo SET "
                   "description = NULL "
                   "WHERE description = 'NULL'")

    db_cur.execute("UPDATE animeinfo SET "
                   "studio = NULL "
                   "WHERE studio = 'NULL'")

    db_cur.execute("UPDATE animeinfo SET "
                   "themes = NULL "
                   "WHERE themes = 'NULL'")

    db_cur.execute("UPDATE animeinfo SET "
                   "categories = NULL "
                   "WHERE categories = 'NULL'")
    db_conn.commit()
