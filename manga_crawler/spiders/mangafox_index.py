# -*- coding: utf-8 -*-
"""
Call `scrapy crawl mangafox_index` from top directory.
Or `scrapy runspider mangafox_index.py` to directly run this file.
"""
from urllib.parse import parse_qs
import json
import scrapy

class MangafoxIndexSpider(scrapy.Spider):
    """
    Crawler to grab list of Manga from MangaFox
    """
    name = 'mangafox-index'
    allowed_domains = ['mangafox.me']
    start_urls = ['https://mangafox.me/manga/']

    def parse(self, response):
        """Parse list of manga"""
        self.log('Parsing index: ' + response.url)
        selector = 'div.manga_list ul li a'
        for item in response.css(selector):
            sid = int(item.css('::attr(rel)').extract_first())
            yield {
                'sid': sid,
                'title': item.css('::text').extract_first(),
                'link': response.urljoin(item.css('::attr(href)').extract_first()),
                'completed': len(item.css('.manga_close')) == 1
            }
            yield scrapy.FormRequest(
                url='http://mangafox.me/ajax/series.php',
                formdata={'sid': str(sid)},
                callback=self.parse_details)
        # end for
    # end def

    def parse_details(self, response):
        """Parse details information"""
        self.log('In parse_details(): ' + response.url)
        result = json.loads(response.text)
        query = parse_qs(response.request.body.decode("utf-8"))
        yield {
            'sid': query['sid'][0],
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
            'cover': result[10]
        }
    # end def
# end class
