# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
	
from scrapy.item import Item, Field

class UscmapsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    buildingID = scrapy.Field()
    buildingName = scrapy.Field()
    buildingAddress = scrapy.Field()

    pass
