# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
import sys
sys.path.append('../')
from db_funcs import *


class FilterPipeline:
    def process_item(self, item, spider):
        return item


class InfoToDb:
    def __init__(self):
        db_conn.set_session(autocommit=True)

    def open_spider(self, spider):
        create_tables()

    def process_item(self, item, spider):
        row = InfoRow(find_info_id(item['title']), item['title'], item['description'], item['rating'], item['studio'],
                      item['themes'], item['categories'], item['eps'], item['mins_per_epi'])
        insert_info_row(row)
        return item

    def close_spider(self, spider):
        db_cur.close()
        db_conn.close()


class DescToDb:
    def __init__(self):
        db_conn.set_session(autocommit=True)

    def open_spider(self, spider):
        create_tables()

    def process_item(self, item, spider):
        row = ReviewRow(find_info_id(item["title"]), item['username'], item['recommendation'], item['review'])
        insert_review_row(row)
        return item

    def close_spider(self, spider):
        db_cur.close()
        db_conn.close()
