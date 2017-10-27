# -*- coding: utf-8 -*-
"""
Call `scrapy crawl mangafox_genres` from top directory.
Or `scrapy runspider mangafox_genres.py` to directly run this file.
"""
import logging
import scrapy

LOG = logging.getLogger('mangafox_index')

class MangafoxGenreSpider(scrapy.Spider):
    """
    Crawler to grab list of Manga from MangaFox
    """
    name = 'mangafox_genres'
    allowed_domains = ['mangafox.me']
    start_urls = ['https://mangafox.me/search.php']

    db_name = 'mangafox'
    primary_key = 'title'

    def parse(self, response):
        """Parse all genres"""
        items = response.css('#advoptions #searcharea ul#genres li')
        LOG.info('Parsing %d items from %s', len(items), response.url)
        for item in items:
            title = item.css('a.tips::text').extract_first()
            detail = item.css('a.tips::attr(title)').extract_first()
            yield {
                'title': title,
                'detail': detail[len(title + ' - '):],
            }
        # end for
    # end def
# end class
