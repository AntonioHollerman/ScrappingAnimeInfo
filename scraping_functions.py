import psycopg2 as pg2
import requests
from bs4 import BeautifulSoup
import pandas as pd

con_info = {
    'database': 'AnimeDB',
    'user': 'postgres',
    'password': 'password'
}
db_conn = pg2.connect(**con_info)
db_cur = db_conn.cursor()


def create_table():
    sql_query = """CREATE TABLE animeinfo(
    anime_id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    review VARCHAR(5000000),
    rating DECIMAL CHECK ( rating >= 0 AND rating <= 10 ),
    studio VARCHAR(5000000),
    category VARCHAR(5000000))"""
    db_cur.execute(sql_query)


def scrape_page(url: str):
    pass


def update_db(data: pd.DataFrame):
    pass
