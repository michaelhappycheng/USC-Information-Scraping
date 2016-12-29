from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader

import json
import time

class USCViterbi_Spider(BaseSpider):

    name = "USCViterbi"

    allowed_domains = ["http://viterbi.usc.edu/"]
    start_urls = ["http://viterbi.usc.edu/news/events/?month&date=11/01/2016&"]

    def parse(self, response):

        # Uncomment for databse
        
        # # storing in the mongo database
        # client = MongoClient(process.env.MONGODB_URI)
        # db = client.heroku_5s156rtt
        # viterbi_november = db.viterbi_november

        # #deleting all prexisting building objects in the database
        # viterbi_november.delete_many({})
        
        hxs = HtmlXPathSelector(response)

        title = []
        link = []
        date = []
        department =  []
        eventType = []

        eventTitle = hxs.xpath("//h3")
        for eventTitle in eventTitle:
            title.append(eventTitle.xpath("a/text()").extract())
            link.append(eventTitle.xpath("a/@href").extract())


        eventStats = hxs.xpath("//div[contains(@class, 'event_stats')]")
        for eventStats in eventStats:

            date.append(eventStats.xpath("p/strong/text()").extract())
            department.append(eventStats.xpath("p[2]/text()").extract())
            eventType.append(eventStats.xpath("p[3]/text()").extract())


        prefixURL = "http://viterbi.usc.edu/news/events/"

        i = 0
        while i < len(title):
            print str(title[i]).strip("[]").strip("u").strip("''")
            print prefixURL + str(link[i]).strip("[]").strip("u").strip("''")
            print str(date[i]).strip("[]").strip("u").strip("''")
            print str(department[i]).strip("[]").strip("u").strip("''")
            print str(eventType[i]).strip("[]").strip("u").strip("''")
            print
            i += 1


        # Uncomment for database

        # i = 0
        # while i < len(eventTitle):
        #     event =  { "title" : str(title[i]).strip("[]").strip("u").strip("''"), "link" : prefixURL + str(link[i]).strip("[]").strip("u").strip("''"), "date" : str(date[i]).strip("[]").strip("u").strip("''"), "department" : str(department[i]).strip("[]").strip("u").strip("''"), "eventType" : str(eventType[i]).strip("[]").strip("u").strip("''")}
        #     viterbi_november.insert(event)
        #     i += 1