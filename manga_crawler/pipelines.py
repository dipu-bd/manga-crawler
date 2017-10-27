# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging
from datetime import datetime
from pymongo import MongoClient
from concurrent.futures import ThreadPoolExecutor


class MangaCrawlerPipeline(object):
    """
    All crawled items are passed through this pipeline
    """

    def __init__(self, mongo_uri, max_worker):
        self.mongo_uri = mongo_uri
        self.max_worker = max_worker
        self.pool = None
        self.client = None
        self.dbc = None
    # end def

    @classmethod
    def from_crawler(cls, crawler):
        """
        Passes settings to the class constructor
        """
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            max_worker=crawler.settings.get('MAX_WORKER'),
        )
    # end def

    def open_spider(self, spider):
        """
        Initializes db when the spider is opened
        """
        # Create thread pool
        self.pool = ThreadPoolExecutor(self.max_worker)
        # Connect with mongodb server
        self.client = MongoClient(self.mongo_uri)
        self.dbc = self.client[spider.db_name][spider.name]
    # end def

    def close_spider(self, spider):
        """
        Terminates things the spider is closed
        """
        self.pool.shutdown()
        self.client.close()
    # end df

    def process_item(self, item, spider):
        """
        Process an item produced by the spider
        """
        key = spider.primary_key
        self.pool.submit(self.save_item, item, key).add_done_callback(self.on_item_saved)
        return item
    # end def

    def save_item(self, item, key):
        """
        Save item to database
        """
        item.update({'last_update': datetime.now()})
        return self.dbc.update({key: item[key]}, {'$set': item}, upsert=True)
    # end def

    def on_item_saved(self, future):
        """
        Process result after storing item in the database
        """
        logging.getLogger('item save callback').debug(future.result())
    # end def
# end class
