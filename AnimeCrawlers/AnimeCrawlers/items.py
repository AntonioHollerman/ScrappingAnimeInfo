# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose
from w3lib.html import remove_tags
from selectolax.parser import HTMLParser


def format_string(string: str):
    return string.strip().replace("  ", "").replace("\n", "")


def return_float(string: str):
    try:
        return float(string)
    except ValueError:
        return "NULL"


def extract_themes(values: list):
    for node in values:
        if "Theme" in remove_tags(node):
            div = HTMLParser(node)
            themes = [a.text() for a in div.css('a')]
            if not themes:
                return "NULL"
            return ', '.join(themes)

    return "NULL"


def extract_studio(values: list):
    for node in values:
        if "Studio" in remove_tags(node):
            div = HTMLParser(node)
            a_tag = div.css_first('a')
            if a_tag is None:
                return "NULL"
            return a_tag.text()

    return "NULL"


def extract_categories(string: str):
    node = HTMLParser(string)
    categories = [a.text() for a in node.css('a')]
    return ", ".join(categories)


def extract_eps(string: str):
    eps = ''.join([val for val in string if val.isdigit()])
    try:
        return int(eps)
    except ValueError:
        return "NULL"


def take_second(values):
    for val in values[1:]:
        if isinstance(val, int):
            return val
    return "NULL"


class InfoCrawlerItem(scrapy.Item):
    title = scrapy.Field(
        input_processor=MapCompose(remove_tags, format_string),
        output_processor=TakeFirst()
    )
    description = scrapy.Field(
        input_processor=MapCompose(remove_tags, format_string),
        output_processor=TakeFirst()
    )
    rating = scrapy.Field(
        input_processor=MapCompose(remove_tags, format_string, return_float),
        output_processor=TakeFirst()
    )
    studio = scrapy.Field(
        output_processor=extract_studio
    )
    themes = scrapy.Field(
        output_processor=extract_themes
    )
    categories = scrapy.Field(
        input_processor=MapCompose(extract_categories),
        output_processor=TakeFirst()
    )
    eps = scrapy.Field(
        input_processor=MapCompose(remove_tags, extract_eps),
        output_processor=TakeFirst()
    )
    mins_per_epi = scrapy.Field(
        input_processor=MapCompose(remove_tags, extract_eps),
        output_processor=take_second
    )


class DescCrawlerItem(scrapy.Item):
    title = scrapy.Field(
        input_processor=MapCompose(remove_tags, format_string),
        output_processor=TakeFirst()
    )
    username = scrapy.Field(
        input_processor=MapCompose(remove_tags, format_string),
        output_processor=TakeFirst()
    )
    recommendation = scrapy.Field(
        input_processor=MapCompose(remove_tags, format_string),
        output_processor=TakeFirst()
    )
    review = scrapy.Field(
        input_processor=MapCompose(remove_tags, format_string),
        output_processor=TakeFirst()
    )
