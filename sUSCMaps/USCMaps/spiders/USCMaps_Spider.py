from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
from USCMaps.items import UscmapsItem
from pymongo import MongoClient

import json

class USCMaps_Spider(BaseSpider):


    name = "USCMaps"

    allowed_domains = ["fmsmaps4.usc.edu"]
    start_urls = ["http://fmsmaps4.usc.edu/usc/php/bl_list_no.php"]

    def parse(self, response):

    	# Both of these work
        hxs = HtmlXPathSelector(response)
        title = hxs.select('//a[contains(@href, "facilities")]/text()').extract()

        # storing in the mongo database
        client = MongoClient(process.env.MONGODB_URI)
        db = client.heroku_5s156rtt
        buildings = db.buildings

        #deleting all prexisting building objects in the database
        buildings.delete_many({})

        #adding each building scraped to the database
        i = 0
        while i < len(title):
            building =  { "id" : title[i+1], "name" : title[i+2], "address" : title[i+3] }
            buildings.insert(building)
            i += 4



