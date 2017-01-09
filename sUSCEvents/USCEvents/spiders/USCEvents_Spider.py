from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
import os
from pymongo import MongoClient

import json
import datetime
from dateutil import relativedelta

class USCEvents_Spider(BaseSpider):

    name = "USCEvents"
    allowed_domains = ["https://calendar.usc.edu/"]

    today = datetime.date.today()
    nextMonth = today + relativedelta.relativedelta(months=1)

    start_urls = ["https://calendar.usc.edu/calendar/month/" + datetime.datetime.strftime(today,"%Y") + "/" + datetime.datetime.strftime(today,"%m") + "/" + "01", 
                  "https://calendar.usc.edu/calendar/month/" + datetime.datetime.strftime(nextMonth,"%Y") + "/" + datetime.datetime.strftime(nextMonth,"%m") + "/" + "01"]

    # storing in the mongo database
    client = MongoClient(os.environ['MONGODB_URI'])
    db = client.heroku_5s156rtt
    eventsCalendar = db.eventsCalendar

    # deleting all prexisting building objects in the database
    eventsCalendar.delete_many({})

    # declaring json
    event = {'event':[]}

    def parse(self, response):
        
        # # storing in the mongo database
        client = MongoClient(os.environ['MONGODB_URI'])
        db = client.heroku_5s156rtt
        eventsCalendar = db.eventsCalendar
        
        hxs = HtmlXPathSelector(response)

        title = []
        link = []
        categories = []
        date = []
        time = []
        location = []
        description = []

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

        def AppendTimes(text):

            text = text.replace("', u'", "").replace("\\n","").replace(" ", "")

            text = text.replace("pm", "PM")
            text = text.replace("am", "AM")
            
            print text

            time.append(text) 

        def AppendLocation(text):

            text = text[1:]

            print text

            location.append(text)

        eventStats = hxs.xpath("//div[contains(@class, 'item event_item vevent')]")

        count = 0

        for eventStats in eventStats:
            
            title.append(str(eventStats.xpath("div/div/h3[contains(@class, 'summary')]/a/text()").extract()).strip("[]").strip("u").strip("''"))
            link.append(str(eventStats.xpath("div/div/h3[contains(@class, 'summary')]/a/@href").extract()).strip("[]").strip("u").strip("''"))
            
            convertCategories = str(eventStats.xpath("div/div[contains(@class, 'event_filters')]/h6/a/text()").extract()).strip("[]").strip("u").strip("''")
            convertCategories = convertCategories.split("', u'")
            convertCategories = convertCategories[0]
            categories.append(convertCategories)

            convertDate = str(eventStats.xpath("div/div[contains(@class, 'actionbar grid_container')]/div[contains(@class, 'left')]/div[contains(@class, 'dateright')]/abbr[contains(@class, 'dtstart')]/@title").extract()).strip("[]").strip("u").strip("''")
            AppendDates(convertDate)

            convertTime = str(eventStats.xpath("div/div[contains(@class, 'actionbar grid_container')]/div[contains(@class, 'left')]/div[contains(@class, 'dateright')]/abbr[contains(@class, 'dtstart')]/text()").extract()).strip("[]").strip("u").strip("''")
            AppendTimes(convertTime)

            convertLocation = str(eventStats.xpath("div/div[contains(@class, 'actionbar grid_container')]/div[contains(@class, 'left')]/div[contains(@class, 'location')]/a[contains(@class, 'event_item_venue')]/text()").extract()).strip("[]").strip("u").strip("''")
            AppendLocation(convertLocation)

            description.append(str(eventStats.xpath("div/h4[contains(@class, 'description')]/text()").extract()).strip("[]").strip("u").strip("''"))

            count += 1

        print count

        # inserting into the mongo database
        i = 0
        while i < len(title):
            event =  { "title" : title[i], "link" : link[i], "date" : date[i], "time" : time[i], "location" : location[i], "description" : description[i], "categories" : categories[i]}
            eventsCalendar.insert(event)
            i += 1