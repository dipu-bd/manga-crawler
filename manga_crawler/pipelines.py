# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from datetime import datetime
from pymongo import MongoClient
from concurrent.futures import ThreadPoolExecutor

# Spider names
MANGAFOX_INDEX = 'mangafox-index'
MANGAFOX_GENRES = 'mangafox-genres'

# Connect with mongodb server
DB = MongoClient('localhost', 27017)

# Maximum number concurrent threads
MAX_WORKER = 100
EXECUTOR = ThreadPoolExecutor(MAX_WORKER)



class MangaCrawlerPipeline(object):
    """
    All crawled items are passed through this pipeline
    """

    def process_item(self, item, spider):
        """
        Process an item produced by the spider
        """
        if spider.name == MANGAFOX_INDEX:
            EXECUTOR.submit(save_item, 'mangafox', 'index', item)
        elif spider.name == MANGAFOX_GENRES:
            EXECUTOR.submit(save_genre, 'mangafox', 'genres', item)
        else:
            return item
        # end if
    # end def
# end class


def save_item(dbname, collection, item):
    """
    Update or create a new item if does not exists
    """
    item.update('last_update', datetime.now())
    DB[dbname][collection].update({'sid': item['sid']}, {'$set': item}, upsert=True)
# end def


def save_genre(dbname, collection, item):
    """
    Update or create a new item if does not exists
    """
    item.update('last_update', datetime.now())
    DB[dbname][collection].update({'title': item['title']}, {'$set': item}, upsert=True)
# end def
