import scrapy


class AnimeReviewsSpider(scrapy.Spider):
    name = "anime-reviews"
    allowed_domains = ["myanimelist.net"]
    start_urls = ["https://myanimelist.net"]

    def parse(self, response):
        pass
