#!/usr/bin/env python
# -*- coding: utf-8 -*-

# weatherBot tests
# Copyright 2015 Brian Mitchell under the MIT license
# See the GitHub repository: https://github.com/bman4789/weatherBot

import unittest
import sys
from datetime import datetime

from weatherBot import get_wind_direction
from weatherBot import make_special_tweet
from weatherBot import get_weather_variables
import weatherBot


class TestWB(unittest.TestCase):
    
    def setUp(self):
        global ydataNorm, ydataEmpty, now, deg
        
        deg = 'º'
        if sys.version < '3':
            deg = deg.decode('utf-8')
        
        now = datetime.now()
        ydataNorm = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '43', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '33', 'text': 'Fair'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'mph', 'temperature': 'F', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '37', 'direction': '310', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
        ydataEmpty = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '43', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '33', 'text': 'Fair'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'mph', 'temperature': 'F', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '37', 'direction': '', 'speed': ''}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
        pass
        
    def test_make_special_tweet(self):
        get_weather_variables(ydataNorm)
        self.assertEqual(make_special_tweet(now), 'normal')
        
    def test_get_wind_direction(self):
        self.assertEqual(get_wind_direction(0), 'N')
        self.assertEqual(get_wind_direction(338), 'N')
        self.assertEqual(get_wind_direction(65), 'NE')
        self.assertEqual(get_wind_direction(110), 'E')
        self.assertEqual(get_wind_direction(150), 'SE')
        self.assertEqual(get_wind_direction(200), 'S')
        self.assertEqual(get_wind_direction(240), 'SW')
        self.assertEqual(get_wind_direction(290), 'W')
        self.assertEqual(get_wind_direction(330), 'NW')
        self.assertEqual(get_wind_direction(400), 'N')
        self.assertEqual(get_wind_direction(-4), 'N')
        
    def test_get_normal_weather_variables(self):
        get_weather_variables(ydataNorm)
        self.assertEqual(weatherBot.wind_speed, 9.0)
        self.assertEqual(weatherBot.wind_direction, 'NW')
        self.assertEqual(weatherBot.wind_chill, 37)
        self.assertEqual(weatherBot.wind_speed_and_unit, '9 mph')
        self.assertEqual(weatherBot.humidity, 70)
        self.assertEqual(weatherBot.temp, 43)
        self.assertEqual(weatherBot.code, 33)
        self.assertEqual(weatherBot.condition, 'Fair')
        self.assertEqual(weatherBot.deg_unit, deg + 'F')
        self.assertEqual(weatherBot.temp_and_unit, '43' + deg + 'F')
        self.assertEqual(weatherBot.city, 'Morris')
        self.assertEqual(weatherBot.region, 'MN')
        self.assertEqual(weatherBot.latitude, '45.59')
        self.assertEqual(weatherBot.longitude, '-95.9')
        
    def test_get_empty_weather_variables(self):
        get_weather_variables(ydataEmpty)
        self.assertEqual(weatherBot.wind_speed, 0.0)
        self.assertEqual(weatherBot.wind_direction, 'N')
        self.assertEqual(weatherBot.wind_chill, 37)
        self.assertEqual(weatherBot.wind_speed_and_unit, '0 mph')
        self.assertEqual(weatherBot.humidity, 70)
        self.assertEqual(weatherBot.temp, 43)
        self.assertEqual(weatherBot.code, 33)
        self.assertEqual(weatherBot.condition, 'Fair')
        self.assertEqual(weatherBot.deg_unit, deg + 'F')
        self.assertEqual(weatherBot.temp_and_unit, '43' + deg + 'F')
        self.assertEqual(weatherBot.city, 'Morris')
        self.assertEqual(weatherBot.region, 'MN')
        self.assertEqual(weatherBot.latitude, '45.59')
        self.assertEqual(weatherBot.longitude, '-95.9')
        
if __name__ == '__main__':
    unittest.main()