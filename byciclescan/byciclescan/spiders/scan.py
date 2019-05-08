# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
# from scrapy.http import HtmlResponse
from bs4 import BeautifulSoup
import w3lib.html
import re

# class ScanSpider(scrapy.Spider):
class ScanSpider(CrawlSpider):
    name = 'scan'
    allowed_domains = ['trekbikes.com'] # could be an array like this ['trek.com', 'giant.com']
    # start_urls = ['https://www.trekbikes.com/us/en_US/bikes/mountain-bikes/trail-mountain-bikes/remedy/remedy-9-8/p/24477/?colorCode=teal']
    start_urls = ['https://www.trekbikes.com/us/en_US/bikes/mountain-bikes/trail-mountain-bikes/c/B330/?pageSize=72&q=%3Arelevance#']

    custom_settings = {
        'DEPTH_LIMIT': 1
    }

    rules = (
        # Extract links matching 'item.php' and parse them with the spider's method parse_item
        Rule(LinkExtractor(restrict_css=('.product-tile__link')), callback='parse_item'),
    )

    def parse_item(self, response):
        html = w3lib.html.remove_tags(
        w3lib.html.remove_tags_with_content(
            response.xpath('//body').extract()[0],
            which_ones=('script',)
        )
        ).replace('\n', ' ').replace('\r', '')

        regex = '[ ]{2,}'
        cleanedHtml = re.sub(regex, " ", html)

        title = response.css("title").select("text()").extract() 
        titleString = ''.join(title)
    
        print (titleString)   

    # def parse(self, response):

    #     # html = Selector(response=response).xpath('//div/text()').get()        
    #     # html = response.xpath('//p/text()').get()

    #     # for next_page in response.css('a.product-tile__link::attr(href)').extract_first():
    #     #     if next_page is not None:
    #     #         next_page = response.urljoin(next_page)
    #     #         yield scrapy.Request(next_page, callback=self.parse, dont_filter=True)

    #     for next_page in response.css('a.product-tile__link::attr(href)'):
    #         if next_page is not None:
    #             next_page = response.urljoin(next_page)
    #             scrapy.Request(next_page, callback=self.parse, dont_filter=True)
    #             html = w3lib.html.remove_tags(
    #                 w3lib.html.remove_tags_with_content(
    #                     response.xpath('//body').extract()[0],
    #                     which_ones=('script',)
    #                 )
    #             ).replace('\n', ' ').replace('\r', '')

    #             regex = '[ ]{2,}'
    #             cleanedHtml = re.sub(regex, " ", html)

    #             title = response.css("title").select("text()").extract() 
    #             titleString = ''.join(title)
            
    #             print (titleString)        
    #     # textFile = open(titleString + '.txt', "w")
    #     # textFile.write(cleanText)
    #     # textFile.close()

    #     pass
