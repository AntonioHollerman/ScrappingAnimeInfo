# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
hi = ['anime_id', 'name', 'description', 'rating', 'studio', 'themes',
      'categories', 'eps', 'mins_per_epi']


class InfoCrawlerItem(scrapy.Item):
    title = scrapy.Field()
    description = scrapy.Field()
    rating = scrapy.Field()
    studio = scrapy.Field()
    themes = scrapy.Field()
    categories = scrapy.Field()
    eps = scrapy.Field()
    mins_per_epi = scrapy.Field()


class DescCrawlerItem(scrapy.Item):
    name = scrapy.Field()
    username = scrapy.Field()
    recommendation = scrapy.Field()
    review = scrapy.Field()
