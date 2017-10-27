# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from datetime import datetime
from pymongo import MongoClient


class MongoPipeline(object):
    """
    All crawled items are passed through this pipeline
    """

    def __init__(self, mongo_uri, db_name, max_worker):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
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
            db_name=crawler.settings.get('MONGO_DBNAME'),
            max_worker=crawler.settings.get('MAX_WORKER'),
        )
    # end def

    def open_spider(self, spider):
        """
        Initializes db when the spider is opened
        """
        # Connect with mongodb server
        self.client = MongoClient(self.mongo_uri)
        self.dbc = self.client[self.db_name][spider.name]
    # end def

    def close_spider(self, spider):
        """
        Terminates things the spider is closed
        """
        self.client.close()
    # end df

    def process_item(self, item, spider):
        """
        Process an item produced by the spider
        """
        key = spider.primary_key
        return self.save_item(item, key)
        #return item
    # end def

    def save_item(self, item, key):
        """
        Save item to database
        """
        item.update({'last_update': datetime.now()})
        return self.dbc.update({key: item[key]}, {'$set': item}, upsert=True)
    # end def
# end class
