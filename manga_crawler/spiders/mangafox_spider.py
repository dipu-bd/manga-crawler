# -*- coding: utf-8 -*-
from datetime import datetime
import logging
import json
import requests
import scrapy
from pymongo import MongoClient
from concurrent.futures import ThreadPoolExecutor

# Connect with mongodb server
DB = MongoClient('localhost', 27017)
# Collection where manga index are stored
INDEX = DB.mangafox.index

# Interval in seconds between two successive update of manga details
UPDATE_INTERVAL = 10 * 3600     # 10 hours
# Maximum number concurrent threads
MAX_CONCURRENT_THREAD = 100


class MangafoxSpider(scrapy.Spider):
    """
    Crawler to grab list of Manga from MangaFox
    """
    name = 'mangafox'

    start_urls = [
        'https://mangafox.me/manga/'
    ]

    def parse(self, response):
        selector = 'div.manga_list ul li a'
        for item in response.css(selector):
            sid = int(item.css('::attr(rel)').extract_first())
            save_item({
                'sid': sid,
                'title': item.css('::text').extract_first(),
                'link': response.urljoin(item.css('::attr(href)').extract_first()),
                'completed': len(item.css('.manga_close')) == 1
            })
        # end for
        check_details()
    # end def
# end class


def get_details(sid):
    """
    Get details information about the manga from the sid
    """
    payload = {'sid': sid}
    url = 'http://mangafox.me/ajax/series.php'
    response = requests.post(url, data=payload)
    result = json.loads(response.text)
    return {
        'display_name': result[0],
        'alternate_names': [s.strip() for s in result[1].split(';')],
        'genres': [s.strip() for s in result[2].split(',')],
        'author': result[3],
        'artist': result[4],
        'rank': ''.join([x for x in result[5] if x.isdigit()]),
        'stars': result[6],
        'rating': result[7],
        'year': result[8],
        'description': result[9],
        'cover': result[10]
    }
# end def


def save_item(item):
    """
    Update or create a new item if does not exists
    """
    query = {'sid': item['sid']}
    update = {'$set': item}
    INDEX.update(query, update, upsert=True)
# end def


def check_details():
    """
    Updates the details field if necessary
    """
    with ThreadPoolExecutor(100) as executor:
        for item in INDEX.find({}):
            if 'updated_at' in item:
                delta = (datetime.now() - item['updated_at'])
                if delta.total_seconds() < UPDATE_INTERVAL:
                    continue
                # end if
            # end if
            executor.submit(update_details, item['sid'])
        # end for
    # end with
# end def


def update_details(sid):
    """Update the details of manga"""
    update = {
        'updated_at': datetime.now(),
        'details': get_details(sid)
    }
    INDEX.update({'sid': sid}, {'$set': update})
    logging.debug('Details updated: ' + sid)
# end save_details
