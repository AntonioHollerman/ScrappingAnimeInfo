from typing import Iterable

import scrapy
import requests
from scrapy import Request
from scrapy.loader import ItemLoader
from AnimeCrawlers.items import InfoCrawlerItem


def check_link(url):
    try:
        response = requests.get(url)
        # if the get request is successful, the status code will be 200
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.ConnectionError:
        # if the get request failed, it might mean the url does not exist
        return False


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


class InfoSpider(scrapy.Spider):
    name = "InfoSpider"
    allowed_domains = ['myanimelist.net']
    start_url = []
    all_genres = ['Action', 'Avant_Garde', 'Award_Winning', 'Boys_Love', 'Comedy', 'Drama', 'Fantasy', 'Girls_Love',
                  'Gourmet', 'Mystery', 'Romance', 'Sci-Fi', 'Slice_of_Life', 'Sports', 'Supernatural', 'Suspense',
                  'Adventure']

    def start_requests(self) -> Iterable[Request]:
        for genre in self.all_genres:
            index = 1
            url = f'https://myanimelist.net/anime/genre/{map_categories[genre]}/{genre}?page={index}'
            while check_link(url):
                index += 1
                yield scrapy.Request(url, self.parse)
                url = f'https://myanimelist.net/anime/genre/{map_categories[genre]}/{genre}?page={index}'

    def parse(self, response):
        divs = response.css(
            'div.js-anime-category-producer.seasonal-anime.js-seasonal-anime.js-anime-type-all.js-anime-type-1')
        for anime in divs:
            item = ItemLoader(item=InfoCrawlerItem(), selector=anime)
            item.add_css('title', 'a.link-title')
            item.add_css('description', 'p.preline')
            item.add_css('rating', 'div.[title= "Score"]')
            item.add_css('studio', "div.property")
            item.add_css('themes', "div.property")
            item.add_css('categories', "div.genres-inner.js-genre-inner")
            item.add_css('eps', 'span.item:nth-of-type(3) span')
            item.add_css('mins_per_epi', 'span.item:nth-of-type(3) span')
            yield item
