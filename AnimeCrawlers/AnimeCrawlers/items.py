# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose
from w3lib.html import remove_tags


def clear_white_space(string: str):
    return string.strip().replace("  ", "").replace("\n", "")


class InfoCrawlerItem(scrapy.Item):
    title = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )
    description = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )
    rating = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )
    studio = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )
    themes = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )
    categories = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )
    eps = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )
    mins_per_epi = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst()
    )


class DescCrawlerItem(scrapy.Item):
    title = scrapy.Field(
        input_processor=MapCompose(remove_tags, clear_white_space),
        output_processor=TakeFirst()
    )
    username = scrapy.Field(
        input_processor=MapCompose(remove_tags, clear_white_space),
        output_processor=TakeFirst()
    )
    recommendation = scrapy.Field(
        input_processor=MapCompose(remove_tags, clear_white_space),
        output_processor=TakeFirst()
    )
    review = scrapy.Field(
        input_processor=MapCompose(remove_tags, clear_white_space),
        output_processor=TakeFirst()
    )
