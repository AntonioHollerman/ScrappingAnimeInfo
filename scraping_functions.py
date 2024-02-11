import requests
from selectolax.parser import HTMLParser
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError
import numpy as np
from db_funcs import *


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
        row = InfoScrapingIndexRow(find_url_scraped_index(self.current_url), self._category, self._next_page,
                                   self._next_div)
        insert_info_scraping_index(row)

    def extract_div(self):
        current_div = self.divs_filtered[self._next_div]
        self._next_div += 1

        title = current_div.find('a', attrs={'class': ['link-title']}).get_text().replace("'", "''")
        desc = current_div.find("p", attrs={'class': ['preline']}).get_text().replace("'", "''")

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

        current_anime = InfoRow(find_info_id(title), title, desc, rating, studio, themes, categories, eps, mins)
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


class ScrapeReviews:
    def __init__(self):
        self.divs_filtered = []
        self.page_index: int = 1

    def load_page(self, url):
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            context = browser.new_context()
            page = context.new_page()

            try:
                page.goto(url)
                page.wait_for_load_state("networkidle")

                html = page.content()
            except TimeoutError:
                return 404
            finally:
                browser.close()

        tree = HTMLParser(html)
        self.divs_filtered = tree.css("div[class='review-element js-review-element']")
        return 200

    @staticmethod
    def extract_div(div) -> ReviewRow:
        try:
            name = div.css_first("a[data-ga-click-type='review-anime-title']").text().strip()
        except AttributeError:
            name = np.nan

        try:
            username = div.css_first("div.username > a").text().strip()
        except AttributeError:
            username = np.nan

        try:
            recommendation = div.css_first("div.js-btn-label").text().strip()
        except AttributeError:
            recommendation = np.nan

        try:
            review = div.css_first("div.text").text().replace("\n", "").replace("  ", "")
        except AttributeError:
            review = np.nan

        return ReviewRow(find_info_id(name), username, recommendation, review)

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.divs_filtered) != 0:
            review_extracted = self.extract_div(self.divs_filtered.pop(0))
            insert_review_row(review_extracted)
            return review_extracted
        else:
            url = ("https://myanimelist.net/reviews.php?t=anime&filter_check=&filter_hide=&preliminary=on&spoiler=on&"
                   f"p={self.page_index}")
            self.page_index += 1
            stat_code = self.load_page(url)
            if len(self.divs_filtered) == 0 or stat_code == 404:
                raise StopIteration
            return self.__next__()

