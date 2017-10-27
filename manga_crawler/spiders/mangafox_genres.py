# -*- coding: utf-8 -*-
"""
Call `scrapy crawl mangafox_genres` from top directory.
Or `scrapy runspider mangafox_genres.py` to directly run this file.
"""
import scrapy

class MangafoxGenreSpider(scrapy.Spider):
    """
    Crawler to grab list of Manga from MangaFox
    """
    name = 'mangafox_genres'
    allowed_domains = ['mangafox.me']
    start_urls = ['https://mangafox.me/search.php']

    def parse(self, response):
        """Parse all genres"""
        self.log('Parsing genres: ' + response.url)
        selector = '#advoptions #searcharea ul#genres li'
        for item in response.css(selector):
            title = item.css('a.tips::text').extract_first()
            detail = item.css('a.tips::attr(title)').extract_first()
            yield {
                'title': title,
                'detail': detail[len(title + ' - '):],
            }
        # end for
    # end def
# end class
