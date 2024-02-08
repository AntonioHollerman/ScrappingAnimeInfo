import scrapy


class DescriptionsSpider(scrapy.Spider):
    name = "Descriptions"
    allowed_domains = ["myanimelist.net"]
    start_urls = ["https://myanimelist.net"]

    def parse(self, response):
        pass
