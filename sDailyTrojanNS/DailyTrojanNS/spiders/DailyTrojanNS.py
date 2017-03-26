from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
import os
from pymongo import MongoClient

import json
import datetime
from dateutil import relativedelta

class DailyTrojanNS_Spider(BaseSpider):

    name = "DailyTrojanNS"
    allowed_domains = ["http://dailytrojan.com/"]

    # scraping two months
    start_urls = ["http://dailytrojan.com/news/", 
                  "http://dailytrojan.com/sports/"]

    # storing in the mongo database
    client = MongoClient(os.environ['MONGODB_URI'])
    db = client.heroku_5s156rtt
    DailyTrojanNS = db.DailyTrojanNS

    # deleting all prexisting building objects in the database
    DailyTrojanNS.delete_many({})

    # declaring json
    headline = {'headline':[]}

    def parse(self, response):

        currUrl = response.request.url
        currCategory = currUrl.replace("http://dailytrojan.com/", "").replace("/", "")
        
        # storing in the mongo database
        client = MongoClient(os.environ['MONGODB_URI'])
        db = client.heroku_5s156rtt
        DailyTrojanNS = db.DailyTrojanNS
        
        hxs = HtmlXPathSelector(response)

        title = []
        link = []
        date = []
        category = []

        # converting to standard date form
        # converting to standard date form
        def AppendDates(text):

            text = text.split('-')
            lst = iter(text)

            # standard form 12/12/12

            year = next(lst)[-2:]
            
            month = next(lst)

            day = next(lst)[:2]

            print str(month) + '/' + str(day) + '/' + str(year)

            date.append(str(month) + '/' + str(day) + '/' + str(year))

        def encodeString(text):
            
            if(text != []):
                text = text[0].encode('utf-8').strip("[]").strip("u").strip("''")
            else:
                text = "N/A"

            print text

            return text

        eventStats = hxs.xpath("//div[contains(@class, 'av-magazine-group sort_all')]/article")

        count = 0

        for eventStats in eventStats:
            
            convertTitle = eventStats.xpath("div[contains(@class, 'av-magazine-content-wrap')]/header/h3/a/text()").extract()
            title.append(encodeString(convertTitle))

            convertLink = eventStats.xpath("div[contains(@class, 'av-magazine-content-wrap')]/header/h3/a/@href").extract()
            link.append(encodeString(convertLink))

            convertDate = str(eventStats.xpath("div[contains(@class, 'av-magazine-content-wrap')]/header/time/@datetime").extract()).strip("[]").strip("u").strip("''")
            AppendDates(convertDate)

            category.append(currCategory)

            print
            count += 1

        print count

        # inserting into the mongo database
        i = 0
        while i < len(title):
            headline =  { "title" : title[i], "link" : link[i], "date" : date[i], "category" : category[i]}
            DailyTrojanNS.insert(headline)
            i += 1