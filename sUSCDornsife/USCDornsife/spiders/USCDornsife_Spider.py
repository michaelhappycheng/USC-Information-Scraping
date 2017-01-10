from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
import os
from pymongo import MongoClient

import json
import datetime

class USCDornsife_Spider(BaseSpider):

    name = "USCDornsife"
    allowed_domains = ["https://dornsife.usc.edu/events/calendar/all/dornsife"]

    # scraping up to the first three pages of events
    start_urls = ["https://dornsife.usc.edu/events/calendar/all/dornsife/1/",
                  "https://dornsife.usc.edu/events/calendar/all/dornsife/2/",
                  "https://dornsife.usc.edu/events/calendar/all/dornsife/3/"]

    # storing in the mongo database
    client = MongoClient(os.environ['MONGODB_URI'])
    db = client.heroku_5s156rtt
    dornsifeCalendar = db.dornsifeCalendar

    #deleting all prexisting building objects in the database
    dornsifeCalendar.delete_many({})

    #declaring json
    event = {'event':[]}

    def parse(self, response):
        # storing in the mongo database
        client = MongoClient(os.environ['MONGODB_URI'])
        db = client.heroku_5s156rtt
        dornsifeCalendar = db.dornsifeCalendar

        hxs = HtmlXPathSelector(response)

        title = []
        link = []
        date = []
        time = []
        location = []

        # converting to standard date form
        def AppendDates(text):

            text = text.split()
            lst = iter(text)

            month = ConvertMonth(next(lst))
            if(month < 10):
                month = "0" + str(month)

            # exclude the last two months
            day = int(next(lst)[:-1])
            if(day < 10):
                day = "0" + str(day)

            year = next(lst)[2:]

            print str(month) + '/' + str(day) + '/' + str(year)

            date.append(str(month) + '/' + str(day) + '/' + str(year))

        def ConvertMonth(x):
            return {

                'January': 1,
                'February': 2,
                'March': 3,
                'April': 4,
                'May': 5,
                'June': 6,
                'July': 7,
                'August': 8,
                'September': 9,
                'October': 10,
                'November': 11,
                'December': 12,

            }[x]

        def AppendTimes(text):

            text = (encodeString(text))

            text = text.replace("to", "-")
            text = text.replace(" ", "")

            time.append(text)

        def encodeString(text):

            if(text != []):
                text = text[0].encode('utf-8').strip("[]").strip("u").strip("''")
            else:
                text = "N/A"

            print text

            return text

        eventLink = hxs.xpath("//a[contains(@class, 'event-item article cf')]")
        for eventLink in eventLink:
            convertLink = eventLink.xpath("@href").extract()
            link.append(encodeString(convertLink))

        eventStats = hxs.xpath("//div[contains(@class, 'article-has-img')]")

        for eventStats in eventStats:

            convertTitle = eventStats.xpath("h3[contains(@class, 'article-title event-title')]/text()").extract()
            title.append(encodeString(convertTitle))

            convertDate = str(eventStats.xpath("time[contains(@class, 'event-detail ico-cal')]/text()").extract()).strip("[]").strip("u").strip("''")
            AppendDates(convertDate)

            convertTime = eventStats.xpath("time[contains(@class, 'event-detail ico-clock')]/text()").extract()
            AppendTimes(convertTime)


            location.append(eventStats.xpath("time[contains(@class, 'event-detail ico-location')]/text()").extract())

        prefixURL = "https://dornsife.usc.edu/"

        i = 0
        while i < len(title):
            event =  { "title" : str(title[i]).strip("[]").strip("u").strip("''"), "link" : prefixURL + str(link[i]).strip("[]").strip("u").strip("''"), "date" : date[i], "time" : time[i], "location" : str(location[i]).strip("[]").strip("u").strip("''")}
            dornsifeCalendar.insert(event)
            i += 1