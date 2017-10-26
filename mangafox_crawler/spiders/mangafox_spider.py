# -*- coding: utf-8 -*-
import logging
import json
import requests
import scrapy


class MangafoxSpider(scrapy.Spider):
    """
    Crawler to grab list of Manga from MangaFox
    """
    name = 'mangafox'

    start_urls = ['https://mangafox.me/manga/']

    def parse(self, response):
        selector = 'div.manga_list ul li a'
        for item in response.css(selector):
            item = response.css(selector)[0]
            sid = item.css('::attr(rel)').extract_first()
            yield {
                'sid': sid,
                'title': item.css('::text').extract_first(),
                'link': response.urljoin(item.css('::attr(href)').extract_first()),
                'completed': len(item.css('.manga_close')) == 1,
                'details': self.get_details(sid)
            }
            logging.debug('Crawled ' + sid)
        # end for
    # end def

    def get_details(self, sid):
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

# end class
