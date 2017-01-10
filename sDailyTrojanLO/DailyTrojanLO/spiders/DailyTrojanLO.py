from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
import os
from pymongo import MongoClient

import json

class DailyTrojanLO_Spider(BaseSpider):

    name = "DailyTrojanLO"
    allowed_domains = ["http://dailytrojan.com/"]

    # scraping two months
    start_urls = ["http://dailytrojan.com/category/lifestyle/", 
                  "http://dailytrojan.com/category/opinion/",]

    # storing in the mongo database
    client = MongoClient(os.environ['MONGODB_URI'])
    db = client.heroku_5s156rtt
    DailyTrojanLO = db.DailyTrojanLO

    # deleting all prexisting objects in the database
    DailyTrojanLO.delete_many({})

    # declaring json
    headline = {'headline':[]}

    def parse(self, response):

        currUrl = response.request.url
        currCategory = currUrl.replace("http://dailytrojan.com/category/", "").replace("/", "")

        print currCategory
        
        # storing in the mongo database
        client = MongoClient(os.environ['MONGODB_URI'])
        db = client.heroku_5s156rtt
        DailyTrojanLO = db.DailyTrojanLO
        
        hxs = HtmlXPathSelector(response)

        title = []
        link = []
        date = []
        description = []
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

            return text

        eventStats = hxs.xpath("//article")

        count = 0

        for eventStats in eventStats:
            
            # title
            convertTitle = eventStats.xpath("h2[contains(@class, 'post-title entry-title')]/a/@title").extract()
            convertTitle = encodeString(convertTitle)
            convertTitle = convertTitle.replace("Permanent Link: ", "")
            title.append(convertTitle)

            # link 
            convertLink = eventStats.xpath("h2[contains(@class, 'post-title entry-title')]/a/@href").extract()
            link.append(encodeString(convertLink))

            # date
            convertDate = eventStats.xpath("div[contains(@class, 'entry-content-wrapper clearfix standard-content')]/header/span/time/@datetime").extract()
            convertDate = convertDate[0].encode('utf-8')
            AppendDates(convertDate)

            # description
            convertDescription = eventStats.xpath("div[contains(@class, 'entry-content-wrapper clearfix standard-content')]/div[contains(@class, 'entry-content')]/text()").extract()
            description.append(encodeString(convertDescription))

            category.append(currCategory)

            print ""

            count += 1

        print count

        # inserting into the mongo database
        i = 0
        while i < len(title):
            headline =  { "title" : title[i], "link" : link[i], "date" : date[i], "description" : description[i], "category" : category[i]}
            DailyTrojanLO.insert(headline)
            i += 1