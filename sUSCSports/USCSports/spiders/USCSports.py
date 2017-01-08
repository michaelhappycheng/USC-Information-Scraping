from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
import os
from pymongo import MongoClient

import json

class USCSports_Spider(BaseSpider):

    name = "USCSports"
    allowed_domains = ["http://www.usctrojans.com/calendar/usc-calendar.html"]

    # scraping two months
    start_urls = ["http://www.usctrojans.com/sports/m-basebl/sched/usc-m-basebl-sched.html",
                  "http://www.usctrojans.com/sports/m-baskbl/sched/usc-m-baskbl-sched.html",
                  "http://www.usctrojans.com/sports/m-footbl/sched/usc-m-footbl-sched.html", 
                  "http://www.usctrojans.com/sports/m-tennis/sched/usc-m-tennis-sched.html", 
                  "http://www.usctrojans.com/sports/c-track/sched/usc-c-track-sched.html", 
                  "http://www.usctrojans.com/sports/m-volley/sched/usc-m-volley-sched.html", 
                  "http://www.usctrojans.com/sports/m-wpolo/sched/usc-m-wpolo-sched.html", 
                  "http://www.usctrojans.com/sports/w-baskbl/sched/usc-w-baskbl-sched.html", 
                  "http://www.usctrojans.com/sports/w-soccer/sched/usc-w-soccer-sched.html", 
                  "http://www.usctrojans.com/sports/w-tennis/sched/usc-w-tennis-sched.html", 
                  "http://www.usctrojans.com/sports/w-volley/sched/usc-w-volley-sched.html",
                  "http://www.usctrojans.com/sports/w-wpolo/sched/usc-w-wpolo-sched.html"]

    # storing in the mongo database
    client = MongoClient(os.environ['MONGODB_URI'])
    db = client.heroku_5s156rtt
    sportsCalendar = db.sportsCalendar

    # deleting all prexisting objects in the database
    sportsCalendar.delete_many({})

    # declaring json
    event = {'headline':[]}

    def parse(self, response):

        # storing in the mongo database
        client = MongoClient(os.environ['MONGODB_URI'])
        db = client.heroku_5s156rtt
        sportsCalendar = db.sportsCalendar

        currUrl = response.request.url
        curr = currUrl.replace("http://www.usctrojans.com/sports/", "").split("/")
        curr = curr[0]

        print curr

        if curr == "m-basebl":
            currSex = "Men"
            currSport = "Baseball"
        elif curr == "m-baskbl":
            currSex = "Men"
            currSport = "Basketball"
        elif curr == "m-footbl":
            currSex = "Men"
            currSport = "Football"
        elif curr == "m-tennis":
            currSex = "Men"
            currSport = "Tennis"
        elif curr == "c-track":
            currSex = "Both"
            currSport = "Track"
        elif curr == "m-volley":
            currSex = "Men"
            currSport = "Volleyball"
        elif curr == "m-wpolo":
            currSex = "Men"
            currSport = "Water polo"
        elif curr == "w-baskbl":
            currSex = "Women"
            currSport = "Basketball"
        elif curr == "w-soccer":
            currSex = "Women"
            currSport = "Soccer"
        elif curr == "w-tennis":
            currSex = "Women"
            currSport = "Tennis"
        elif curr == "w-volley":
            currSex = "Women"
            currSport = "Volleyball"
        elif curr == "w-wpolo":
            currSex = "Women"
            currSport = "Water polo"

        print currSex
        print currSport
        
        hxs = HtmlXPathSelector(response)

        record = []

        title = []
        link = []
        date = []
        timeOrScore = []
        location = []
        sport = []
        gender = []

        stats = hxs.xpath("//tr[contains(@class, 'event-listing')]")

        count = 0

        for stats in stats:
            
            # date
            convertDate = stats.xpath("td[contains(@class, 'sch-col-1')]/text()").extract()
            convertDate = convertDate[0].encode('utf-8')
            date.append(convertDate)

            print convertDate

            # time

            convertTimeOrScore = stats.xpath("td[contains(@class, 'sch-col-4')]/text()").extract()
            convertTimeOrScore = convertTimeOrScore[0].encode('utf-8')
            convertTimeOrScore = convertTimeOrScore.upper().replace(".", "").replace("0 P", "0P").replace("0 A", "0A")

            timeOrScore.append(convertTimeOrScore)
           
            print convertTimeOrScore

            # title 
            convertTitle = stats.xpath("td[contains(@class, 'sch-col-2')]/text()").extract()
            convertTitle = convertTitle[0].encode('utf-8')
            convertTitle = convertTitle.strip(" ").replace("*", "")

            if(currSex == "Both"):
                convertTitle = currSport + " vs. " + convertTitle

            else:
                convertTitle = currSex + "'s " + currSport + " vs. " + convertTitle

            title.append(convertTitle)

            print convertTitle

            # location
            convertLocation = stats.xpath("td[contains(@class, 'sch-col-3')]/text()").extract()
            convertLocation = convertLocation[0].encode('utf-8')

            location.append(convertLocation)

            print convertLocation
            
            sport.append(currSport)
            gender.append(currSex)

            print ""

            count += 1

        print count

        # inserting into the mongo database
        i = 0
        while i < len(title):
            event =  { "title" : title[i], "date" : date[i], "timeOrScore" : timeOrScore[i] , "location" : location[i], "sport" : sport[i], "gender" : gender[i]}
            sportsCalendar.insert(event)
            i += 1