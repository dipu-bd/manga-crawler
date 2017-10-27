# -*- coding: utf-8 -*-
"""
Call `scrapy crawl mangafox_genres` from top directory.
Or `scrapy runspider mangafox_genres.py` to directly run this file.
"""
import logging
import scrapy
from ..utils import formatter as F

LOG = logging.getLogger('mangafox_latest')

class MangafoxGenreSpider(scrapy.Spider):
    """
    Crawler to grab latest manga list from MangaFox
    """
    name = 'mangafox_latest'
    allowed_domains = ['mangafox.me']
    start_urls = [
        'https://mangafox.me/releases/0.html',
        'https://mangafox.me/releases/1.html',
        'https://mangafox.me/releases/2.html',
        'https://mangafox.me/releases/3.html',
        'https://mangafox.me/releases/4.html',
        'https://mangafox.me/releases/5.html',
    ]

    primary_key = 'sid'

    def parse(self, response):
        """Parse all genres"""
        div_content = response.css('div#content.left')
        items = div_content.css('ul#updates li')
        LOG.info('Parsing %d items from %s', len(items), response.url)

        for item in items:
            releases = []
            for chapter in item.css('dt'):
                date = chapter.css('em::text').extract_first()
                number = item.css('a.chapter::text').extract_first()
                link = item.css('a.chapter::attr(href)').extract_first()
                releases.append({
                    'date': F.parseDate(date),
                    'chapter': number.strip().split()[-1],
                    'link': response.urljoin(link)
                })
            # end for

            series = item.css('a.series_preview')
            title = series.css('::text').extract_first()
            sid = series.css('::attr(rel)').extract_first()
            link = series.css('::attr(href)').extract_first()
            yield {
                'sid': F.parseInt(sid),
                'title': title,
                'link': response.urljoin(link),
                'releases': releases,
            }
        # end for
    # end def
# end class
