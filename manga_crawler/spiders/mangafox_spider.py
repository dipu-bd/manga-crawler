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
DB = MongoClient('localhost', 27017)
# Collections where manga info are stored
INDEX = DB.mangafox.index
GENRE = DB.mangafox.genres

# Maximum number concurrent threads
MAX_WORKER = 250
EXECUTOR = ThreadPoolExecutor(MAX_WORKER)


class MangafoxSpider(scrapy.Spider):
    """
    Crawler to grab list of Manga from MangaFox
    """
    name = 'mangafox'
    allowed_domains = ['mangafox.me']
    start_urls = [
        'https://mangafox.me/manga/',
        'https://mangafox.me/search.php'
    ]

    def parse(self, response):
        # Store list of manga
        selector = 'div.manga_list ul li a'
        for item in response.css(selector):
            data = {
                'sid': int(item.css('::attr(rel)').extract_first()),
                'title': item.css('::text').extract_first(),
                'link': response.urljoin(item.css('::attr(href)').extract_first()),
                'completed': len(item.css('.manga_close')) == 1
            }
            save_item(data)                         # save item to databasae
            EXECUTOR.submit(update_details, data)   # run update details task
        # end for

        # Store genres
        selector = '#advoptions #searcharea ul#genres li'
        for item in response.css(selector):
            title = item.css('a.tips::text').extract_first()
            detail = item.css('a.tips::attr(title)').extract_first()
            data = {
                'title': title,
                'detail': detail[len(title + ' - '):]
            }
            EXECUTOR.submit(save_genre, item)
        # end for
    # end def
# end class


def save_item(item):
    """
    Update or create a new item if does not exists
    """
    INDEX.update({'sid': item['sid']}, {'$set': item}, upsert=True)
# end def


def save_genre(item):
    """
    Update or create a new item if does not exists
    """
    GENRE.update({'title': item['title']}, {'$set': item}, upsert=True)
# end def


def update_details(item):
    """Update the details of manga"""
    details = get_details(item['sid'])  # get details
    item.update(details)                # merge details with item
    save_item(item)                     # save item
    logging.debug('Item processed: ' + item['sid'])
# end save_details


def get_details(sid):
    """
    Get details information about the manga from the sid
    """
    payload = {'sid': sid}
    url = 'http://mangafox.me/ajax/series.php'
    response = requests.post(url, data=payload)
    result = json.loads(response.text)
    return {
        'name': result[0],
        'alternate_names': [s.strip() for s in result[1].split(';')],
        'genres': [s.strip() for s in result[2].split(',')],
        'author': result[3],
        'artist': result[4],
        'rank': int(''.join([x for x in result[5] if x.isdigit()])),
        'stars': int(result[6]),
        'rating': float(result[7]),
        'year': int(result[8]),
        'description': result[9],
        'cover': result[10],
        'last_update': datetime.now()
    }
# end def
