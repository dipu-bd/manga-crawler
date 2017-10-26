# -*- coding: utf-8 -*-
import scrapy

class MangafoxSpider(scrapy.Spider):
    name = 'mangafox'

    start_urls = ['https://mangafox.me/manga/']

    def parse(self, response):
        selector = 'div.manga_list ul li a'
        for item in response.css(selector):
            yield {
                '_id': item.css('::attr(rel)').extract_first(),
                'title': item.css('::text').extract_first(),
                'completed': len(item.css('.manga_close')) == 1,
                'link': item.css('::attr(href)').extract_first(),
            }
        # end for
    # end def

# end class
