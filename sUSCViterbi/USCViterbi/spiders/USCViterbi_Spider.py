from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
import os
from pymongo import MongoClient

import json
import time

class USCViterbi_Spider(BaseSpider):

    name = "USCViterbi"

    allowed_domains = ["http://viterbi.usc.edu/"]
    start_urls = ["http://viterbi.usc.edu/news/events/?month&date=11/01/2016&"]


    def parse(self, response):

        # storing in the mongo database
        client = MongoClient(os.environ['MONGODB_URI'])
        db = client.heroku_5s156rtt
        viterbiCalendar = db.viterbiCalendar

        #deleting all prexisting building objects in the database
        viterbiCalendar.delete_many({})

        #declaring json
        event = {'event':[]}
        
        hxs = HtmlXPathSelector(response)

        title = []
        link = []
        date = []
        time = []
        department =  []
        eventType = []

        # converting to standard date function
        def AppendDates(text):

            text = text.split()
            lst = iter(text)

            # ignore dis!
            next(lst)

            month = ConvertMonth(next(lst))
            day = next(lst)[:2]
            year = next(lst)[2:]

            date.append(str(month) + '/' + str(day) + '/' + str(year))

            if(len(text) == 10):

                # ignore dis!
                next(lst)

                times = next(lst) + next(lst) + next(lst) + next(lst) + next(lst)

                time.append(times)

            # edge case without the time
            else:

                time.append('N/A')

        def ConvertMonth(x):
            return {
                
                'Jan': 1,
                'Feb': 2,
                'Mar': 3, 
                'Apr': 4, 
                'May': 5,
                'Jun': 6, 
                'Jul': 7, 
                'Aug': 8, 
                'Sep': 9, 
                'Oct': 10, 
                'Nov': 11, 
                'Dec': 12,

            }[x]

        eventTitle = hxs.xpath("//h3")
        for eventTitle in eventTitle:
            title.append(eventTitle.xpath("a/text()").extract())
            link.append(eventTitle.xpath("a/@href").extract())


        eventStats = hxs.xpath("//div[contains(@class, 'event_stats')]")

        for eventStats in eventStats:

            parseDate = str(eventStats.xpath("p/strong/text()").extract()).strip("[]").strip("u").strip("''")
            AppendDates(parseDate)
            department.append(eventStats.xpath("p[2]/text()").extract())
            eventType.append(eventStats.xpath("p[3]/text()").extract())


        prefixURL = "http://viterbi.usc.edu/news/events/"

        i = 0
        while i < len(eventTitle):
            event =  { "title" : str(title[i]).strip("[]").strip("u").strip("''"), "link" : prefixURL + str(link[i]).strip("[]").strip("u").strip("''"), "date" : date[i], "time" : time[i], "department" : str(department[i]).strip("[]").strip("u").strip("''"), "eventType" : str(eventType[i]).strip("[]").strip("u").strip("''")}
            viterbiCalendar.insert(event)
            i += 1

        # debugging purposes
        i = 0
        while i < len(title):
            print str(title[i]).strip("[]").strip("u").strip("''")
            print prefixURL + str(link[i]).strip("[]").strip("u").strip("''")
            print date[i]
            print time[i]
            print str(department[i]).strip("[]").strip("u").strip("''")
            print str(eventType[i]).strip("[]").strip("u").strip("''")
            print
            i += 1
       