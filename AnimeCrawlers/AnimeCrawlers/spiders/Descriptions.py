from typing import Iterable
from scrapy.loader import ItemLoader

import scrapy
from AnimeCrawlers.items import DescCrawlerItem
from scrapy import Request
SCRAPE_PAGES = 100


class DescriptionsSpider(scrapy.Spider):
    name = "Descriptions"
    allowed_domains = ["myanimelist.net"]
    start_urls = ["https://myanimelist.net"]

    def start_requests(self) -> Iterable[Request]:
        for i in range(1, SCRAPE_PAGES + 1):
            url = ("https://myanimelist.net/reviews.php?t=anime&filter_check=&filter_hide=&preliminary=on&spoiler=on&"
                   f"p={i}")
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        review_divs = response.css("div[class='review-element js-review-element']")
        for review_div in review_divs:
            item = ItemLoader(item=DescCrawlerItem, selector=review_div)
            item.add_css('title', "a[data-ga-click-type='review-anime-title']")
            item.add_css('username', "div.username > a")
            item.add_css('recommendation', "div.js-btn-label")
            item.add_css('review', "div.text")
            yield item

