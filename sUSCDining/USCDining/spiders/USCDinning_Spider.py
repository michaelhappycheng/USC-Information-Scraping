from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
from pymongo import MongoClient
import os

import json
import datetime

class USCDining_Spider(BaseSpider):

    name = "USCDining"

    allowed_domains = ["http://hospitality.usc.edu/residential-dining-menus/"]

    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)

    # grabs the current day
    start_urls = ["http://hospitality.usc.edu/residential-dining-menus/?menu_venue=venue-507&menu_date=" + (datetime.datetime.strftime(today,"%m")+"%2F") + (datetime.datetime.strftime(today,"%d")+"%2F") + datetime.datetime.strftime(today,"%Y"),
                  "http://hospitality.usc.edu/residential-dining-menus/?menu_venue=venue-514&menu_date=" + (datetime.datetime.strftime(today,"%m")+"%2F") + (datetime.datetime.strftime(today,"%d")+"%2F") + datetime.datetime.strftime(today,"%Y"),
                  "http://hospitality.usc.edu/residential-dining-menus/?menu_venue=venue-518&menu_date=" + (datetime.datetime.strftime(today,"%m")+"%2F") + (datetime.datetime.strftime(today,"%d")+"%2F") + datetime.datetime.strftime(today,"%Y"),
                  "http://hospitality.usc.edu/residential-dining-menus/?menu_venue=venue-507&menu_date=" + (datetime.datetime.strftime(tomorrow,"%m")+"%2F") + (datetime.datetime.strftime(tomorrow,"%d")+"%2F") + datetime.datetime.strftime(tomorrow,"%Y"),
                  "http://hospitality.usc.edu/residential-dining-menus/?menu_venue=venue-514&menu_date=" + (datetime.datetime.strftime(tomorrow,"%m")+"%2F") + (datetime.datetime.strftime(tomorrow,"%d")+"%2F") + datetime.datetime.strftime(tomorrow,"%Y"),
                  "http://hospitality.usc.edu/residential-dining-menus/?menu_venue=venue-518&menu_date=" + (datetime.datetime.strftime(tomorrow,"%m")+"%2F") + (datetime.datetime.strftime(tomorrow,"%d")+"%2F") + datetime.datetime.strftime(tomorrow,"%Y")]

    # storing in the mongo database
    client = MongoClient(os.environ['MONGODB_URI'])
    db = client.heroku_5s156rtt
    dininghalls = db.dininghalls
    # deleting all prexisting dining hall objects in the database
    dininghalls.delete_many({})

    def parse(self, response):
      # storing in the mongo database
      client = MongoClient(os.environ['MONGODB_URI'])
      db = client.heroku_5s156rtt
      dininghalls = db.dininghalls

      currUrl = response.request.url
      currDate = currUrl.replace("http://hospitality.usc.edu/residential-dining-menus/?menu_venue=venue-518&menu_date=", "")

      # Both of these work
      hxs = HtmlXPathSelector(response)

      #declaring json
      dininghall = {'stations':[]}

      cafeTitle = hxs.xpath("//h2[contains(@class, 'fw-accordion-title ui-state-active')]/text()").extract()
      print cafeTitle[0].encode('utf-8')

      differentSections = hxs.xpath("//div[contains(@class, 'col-sm-6 col-md-4')]")

      for differentSections in differentSections:

          mealTimes = differentSections.xpath("h3/text()").extract()
          stations = differentSections.xpath("h4/text()").extract()

          print (mealTimes[0].encode('utf-8')).strip("[]").strip('u\'').strip('\'')
          dininghall.update({'mealtype': (mealTimes[0].encode('utf-8')).strip("[]").strip('u\'').strip('\'')})

          dininghall.update({'date': currDate})

          # if datetime.datetime.strftime(datetime.date.today(), '%d') in cafeTitle[0]:
          #   dininghall.update({'date': datetime.datetime.strftime(datetime.date.today(), '%x')})
          # if datetime.datetime.strftime(datetime.date.today() + datetime.timedelta(days=1), '%d') in cafeTitle[0]:
          #   dininghall.update({'date': datetime.datetime.strftime(datetime.date.today() + datetime.timedelta(days=1), '%x')})
          if "Kitchen" in cafeTitle[0]:
            dininghall.update({'name': 'EVK'})
          if "Parkside" in cafeTitle[0]:
            dininghall.update({'name': 'Parkside'})
          if "84" in cafeTitle[0]:
            dininghall.update({'name': 'Cafe 84'})

          foodItemSections = differentSections.xpath("ul[contains(@class, 'menu-item-list')]")

          i = 0
          for foodItemSections in foodItemSections:
              foodItems = foodItemSections.xpath("li/text()").extract()

              print stations[i].encode('utf-8')
              stationMiniJSON = {'name': (stations[i].encode('utf-8')).strip("[]").strip('u\'').strip('\''), 'options':[]}

              for foodItems in foodItems:
                print foodItems.encode('utf-8')
                if "\"" in foodItems:
                  individualFoodItemsWrapper = foodItemSections.xpath("li[contains(., '" + foodItems + "')]")
                else:
                  individualFoodItemsWrapper = foodItemSections.xpath("li[contains(., \"" + foodItems + "\")]")
                foodItemsTags = individualFoodItemsWrapper.xpath("span/i/span/text()").extract()
                foodMiniJSON = {'name': foodItems.encode('utf-8'), 'tags': []}
                for foodItemsTags in foodItemsTags:
                  foodMiniJSON['tags'].append((foodItemsTags.encode('utf-8')).strip("[]").strip('u\'').strip('\''))
                stationMiniJSON['options'].append(foodMiniJSON)
              dininghall['stations'].append(stationMiniJSON)
              i+=1
          print dininghall
          dininghalls.insert(dininghall)
          dininghall = {'stations':[]}
