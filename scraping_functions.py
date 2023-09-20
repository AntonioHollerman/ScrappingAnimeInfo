import psycopg2 as pg2
import requests
from bs4 import BeautifulSoup
from collections import namedtuple
from typing import List

con_info = {
    'database': 'AnimeDB',
    'user': 'postgres',
    'password': 'password'
}
db_conn = pg2.connect(**con_info)
db_cur = db_conn.cursor()
InfoRow = namedtuple('InfoRow', ['anime_id', 'name', 'description', 'rating', 'studio', 'themes',
                                 'categories', 'eps', 'mins_per_epi'])
InforScrapingIndexRow = namedtuple('InforScrapingIndexRow', ['web_id', 'category', 'page_index',
                                                             'div_index'])
UrlScrapedRow = namedtuple('UrlScrapedRow', ['web_id', 'web_url'])

map_categories = {
    'Action': '1',
    'Adventure': '2',
    'Avant_Garde': '5',
    'Award_Winning': '46',
    'Boys_Love': '28',
    'Comedy': '4',
    'Drama': '8',
    'Fantasy': '10',
    'Girls_Love': '26',
    'Gourmet': '47',
    'Horror': '14',
    'Mystery': '7',
    'Romance': '22',
    'Sci-Fi': '24',
    'Slice_of_Life': '36',
    'Sports': '30',
    'Supernatural': '37',
    'Suspense': '41'
}


class ScrapeInfo:
    def __init__(self, category: str, scraping_index: dict = None):
        self.url = f'https://myanimelist.net/anime/genre/{map_categories[category]}/{category}'
        self.current_url = f'https://myanimelist.net/anime/genre/{map_categories[category]}/{category}?page=1'
        self._category = category
        if scraping_index is None:
            self.scraping_index = extract_info_index()
        else:
            self.scraping_index = scraping_index
        self.divs_filtered = []
        self._next_page = 1
        self._next_div = 0
        if self._category in self.scraping_index:
            self._next_page = self.scraping_index[self._category]['page_index']
            self._next_div = self.scraping_index[self._category]['div_index']

    def load_page(self):
        response = requests.get(self.url, params={'page': f'{self._next_page}'})
        self.current_url = (f'https://myanimelist.net/anime/genre/{map_categories[self._category]}/{self._category}?'
                            f'page={self._next_page}')
        self._next_page += 1

        soup = BeautifulSoup(response.content, 'html.parser')
        attribute = {
            'class': ['js-anime-category-producer', 'seasonal-anime', 'js-seasonal-anime', 'js-anime-type-all',
                      'js-anime-type-1']
        }
        self.divs_filtered = soup.find_all('div', attrs=attribute)
        return response.status_code

    def get_category(self):
        return self._category

    def set_category(self, new_cat):
        self.save_index()
        self._category = new_cat
        if self._category in self.scraping_index:
            self._next_page = self.scraping_index[self._category]['page_index']
            self._next_div = self.scraping_index[self._category]['div_index']
        self.url = f'https://myanimelist.net/anime/genre/{map_categories[new_cat]}/{new_cat}'

    def save_index(self):
        if self.scraping_index is None:
            self.scraping_index = {}
        self.scraping_index[self._category] = {'page_index': self._next_page, 'div_index': self._next_div}
        row = InforScrapingIndexRow(find_url_scraped_index(self.current_url), self._category, self._next_page,
                                    self._next_div)
        insert_info_scraping_index(row)

    def extract_div(self):
        current_div = self.divs_filtered[self._next_div]
        self._next_div += 1

        title = current_div.find('a', attrs={'class': ['link-title']}).get_text().replace("'", "''")
        par = current_div.find("p", attrs={'class': ['preline']}).get_text().replace("'", "''")

        rating = current_div.find("div", attrs={'title': 'Score'})
        rating = str(rating).strip()
        index = rating.find('</i>') + 4
        try:
            rating = float(rating[index:index + 4])
        except ValueError:
            rating = 'NULL'

        studio = 'NULL'
        themes = 'NULL'

        for prop in current_div.find_all('div', attrs={'class': ['property']}):
            spans = prop.find_all('span')
            info_caption = spans[0].get_text()
            try:
                if info_caption == 'Studio':
                    studio = prop.a.get_text().replace("'", "''")
            except AttributeError:
                pass

            try:
                if info_caption == 'Themes':
                    themes = ", ".join([a.get_text() for a in prop.find_all('a')]).replace("'", "''")
            except AttributeError:
                pass

        categories = current_div.find('div', attrs={'class': ['genres-inner', 'js-genre-inner']})
        categories = ", ".join([a.get_text() for a in categories.find_all("a")]).replace("'", "''")

        info = current_div.find_all('span', attrs={'class': ['item']})
        info = info[2].find_all('span')

        eps = ''.join([val for val in info[0].get_text() if val.isdigit()])
        if not eps:
            eps = 'NULL'

        mins = ''.join([val for val in info[1].get_text() if val.isdigit()])
        if not mins:
            mins = 'NULL'

        current_anime = InfoRow(find_info_id(title), title, par, rating, studio, themes, categories, eps, mins)
        return current_anime

    def __iter__(self):
        return self

    def __next__(self):
        if self._next_div >= len(self.divs_filtered):
            stat_code = self.load_page()
            self._next_div = 0
            if stat_code == 404:
                raise StopIteration
        self.save_index()
        return self.extract_div()


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
    div_index INTEGER);"""
    db_cur.execute(sql_query)
    db_conn.commit()


def update_db(new_row: InfoRow):
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


def insert_info_scraping_index(new_row: InforScrapingIndexRow):
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
        return -1
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
    info: List[InforScrapingIndexRow] = [InforScrapingIndexRow(*row) for row in db_cur.fetchall()]
    if info:
        holding_dict = {}
        for category in info:
            holding_dict[category.category] = {'div_index': category.div_index, 'page_index': category.page_index}
        return holding_dict
    else:
        return dict()
