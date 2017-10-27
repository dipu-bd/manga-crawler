# -*- coding: utf-8 -*-
"""
Call `scrapy crawl mangafox_index` from top directory.
Or `scrapy runspider mangafox_index.py` to directly run this file.
"""
import scrapy
import utils.formatter as F

class MangafoxIndexSpider(scrapy.Spider):
    """
    Crawler to grab list of Manga from MangaFox
    """
    name = 'mangafox_index'
    allowed_domains = ['mangafox.me']
    start_urls = ['https://mangafox.me/manga/']

    db_name = 'mangafox'
    primary_key = 'sid'

    def parse(self, response):
        """Parse list of manga"""
        self.log('Parsing index: ' + response.url)
        selector = 'div.manga_list ul li a'
        for item in response.css(selector):
            sid = item.css('::attr(rel)').extract_first()
            link = item.css('::attr(href)').extract_first()
            yield {
                'sid': F.parseInt(sid),
                'title': item.css('::text').extract_first(),
                'link': response.urljoin(link),
                'completed': len(item.css('.manga_close')) == 1
            }
            yield scrapy.FormRequest(
                url='http://mangafox.me/ajax/series.php',
                formdata={'sid': sid},
                callback=self.parse_details)
        # end for
    # end def

    def parse_details(self, response):
        """Parse details information"""
        self.log('In parse_details(): ' + response.url)
        result = F.parseJson(response.text)
        query = F.parseQuery(response.request.body)
        yield {
            'sid': F.parseInt(query['sid']),
            'name': F.cleanStr(result[0]),
            'alternate_names': F.splitStr(result[1], ';'),
            'genres': F.splitStr(result[2], ','),
            'author': F.cleanStr(result[3]),
            'artist': F.cleanStr(result[4]),
            'rank': F.parseOrdinal(result[5]),
            'stars': F.parseInt(result[6]),
            'rating': F.parseFloat(result[7]),
            'year': F.parseInt(result[8]),
            'description': F.cleanStr(result[9]),
            'cover': F.cleanStr(result[10])
        }
    # end def
# end class
