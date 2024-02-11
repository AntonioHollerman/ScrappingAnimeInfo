from typing import Iterable

import scrapy
import requests
from scrapy import Request
from scrapy.loader import ItemLoader
from AnimeCrawlers.items import InfoCrawlerItem
from time import sleep


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

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Cookie": "MALSESSIONID=vvmkjke8o1nvfo705ttbdvhnn7; MALHLOGSESSID=66e8424db3dc09b246c5cc6562df7225; _ga=GA1.1.103422331.1694030452; usprivacy=1Y--; __gads=ID=8913c5d54c700222-22aab9c36f800079:T=1694030452:RT=1699187471:S=ALNI_MZERs6DSJ-4RAcU8TLfvfYwDaDSwA; __gpi=UID=000009fc826acb58:T=1694030452:RT=1699187471:S=ALNI_MaGyMOon5bbi1M3eEGqcHPPYI_ccQ; _ga_26FEP9527K=GS1.1.1703428089.36.1.1703428123.26.0.0; _rdt_uuid=1694030453193.416504aa-b848-4e6d-8732-c5027f0d81d5; _fbp=fb.1.1694030453489.560777383; cto_bundle=zHwt_19vdVM0MWdJYUlqajdEV01TYnRvVXh6VDNsbFFzNWZrJTJCcTJ4cExUeTlyRkdBdG80NFVnNjJpbmM2bU9RNTR4TDFOSWJkcyUyRjhGRENVMTFVJTJGWElIc2VRTzBHNnM2dGpJVk5jMThCdmlkM2gxQndIWXY5Rjg0OEFidmc1QzM3bzlSZWtBR3NGVHZTQk92Y043eUh4TnQ5eHclM0QlM0Q; cto_bidid=2cySkF9qaTVuOWFmbms5NW1sNndXTEdwT0dsZjRudWJQZWZoazdvYnFSODdLUzNNNXdqVktRVGJzMndscmRaQWQlMkZtOWZQdjVtbm82TVMxSW0lMkJmajlGSGM2dTMyU0NhNVF0NEZsQnI2N01xQ1lDRHlOcDdjZnZOejVKYVEwaXdmNEpmbmc; cto_dna_bundle=HC2Mgl9vdVM0MWdJYUlqajdEV01TYnRvVXg3SUpGWXJTb0xINnBVUnQ3TGlHTkdiMko2dSUyRlpmN1hneXU1QmdmSWp2T3RGdkklMkZzM1pHNiUyQnA4YW1yUmolMkZhRzZBJTNEJTNE; m_gdpr_mdl_20230227=1; _cc_id=1eab999868ae7f59118d633777c7d938; trc_cookie_storage=taboola^%^2520global^%^253Auser-id^%^3D4722d937-fee1-46a6-908d-6bbc1d49b447-tuctbff302d; _ga_26FEP9527K=deleted; _gcl_au=1.1.2071912563.1701820867; _pbjs_userid_consent_data=3524755945110770; mal_cache_key=5cbc87e5ea66d6dfd0c62485404f9a85; _gid=GA1.2.1044159869.1703428081",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Content-Length": "0",
    "TE": "trailers"
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
                sleep(1)
                yield scrapy.Request(url, self.parse, headers=headers)
                url = f'https://myanimelist.net/anime/genre/{map_categories[genre]}/{genre}?page={index}'

    def parse(self, response):
        divs = response.css(
            'div.js-anime-category-producer.seasonal-anime.js-seasonal-anime.js-anime-type-all.js-anime-type-1')
        for anime in divs:
            item = ItemLoader(item=InfoCrawlerItem(), selector=anime)
            item.add_css('title', 'a.link-title')
            item.add_css('description', 'p.preline')
            item.add_css('rating', 'div[title="Score"]')
            item.add_css('studio', "div.property")
            item.add_css('themes', "div.property")
            item.add_css('categories', "div.genres-inner.js-genre-inner")
            item.add_css('eps', 'span.item:nth-of-type(3) span')
            item.add_css('mins_per_epi', 'span.item:nth-of-type(3) span')
            yield item.load_item()
