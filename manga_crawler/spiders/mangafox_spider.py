"""
Call `scrapy crawl mangafox` from top directory.
Or `scrapy runspider mangafox_spider.py` for this file only.
"""
# -*- coding: utf-8 -*-
# MIT License
#
# Copyright (c) 2017 Sudipto Chandra
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from datetime import datetime
import logging
import json
import requests
import scrapy
from pymongo import MongoClient
from concurrent.futures import ThreadPoolExecutor

# Connect with mongodb server
DB = MongoClient('localhost', 27017).mangadb
# Collections where manga info are stored
META = DB.meta
INDEX = DB.mangafox_index
GENRES = DB.mangafox_genres
AUTHORS = DB.mangafox_authors

# Maximum number concurrent threads
MAX_CONCURRENT_THREAD = 100
# Interval in seconds between two successive update
UPDATE_INTERVAL_DETAILS = 2 * 24 * 3600     # 10 hours


class MangafoxSpider(scrapy.Spider):
    """
    Crawler to grab list of Manga from MangaFox
    """
    name = 'mangafox'
    allowed_domains = ['mangafox.me']
    start_urls = ['https://mangafox.me/manga/']

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


def update_details(sid):
    """Update the details of manga"""
    update = {
        'updated_at': datetime.now(),
        'details': get_details(sid)
    }
    INDEX.update({'sid': sid}, {'$set': update})
    logging.debug('Details updated: ' + sid)
# end save_details


def check_details():
    """
    Updates the details field if necessary
    """
    with ThreadPoolExecutor(100) as executor:
        for item in INDEX.find({}):
            if 'updated_at' in item:
                delta = (datetime.now() - item['updated_at'])
                if delta.total_seconds() < UPDATE_INTERVAL_DETAILS:
                    continue
                # end if
            # end if
            executor.submit(update_details, item['sid'])
        # end for
    # end with
# end def
