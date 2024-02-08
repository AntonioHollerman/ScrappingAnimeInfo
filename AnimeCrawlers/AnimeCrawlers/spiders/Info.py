import scrapy


class InfoSpider(scrapy.Spider):
    name = "InfoSpider"
    allowed_domains = ["myanimelist.net"]
    start_urls = ["https://myanimelist.net"]

    def parse(self, response):
        pass
