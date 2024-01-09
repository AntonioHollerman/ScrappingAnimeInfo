import scrapy


class AnimeInfoSpider(scrapy.Spider):
    name = "anime-info"
    allowed_domains = ["myanimelist.net"]
    start_urls = ["https://myanimelist.net"]

    def parse(self, response):
        pass
