#!/usr/bin/env python3

# weatherBot tests
# Copyright 2015-2016 Brian Mitchell under the MIT license
# See the GitHub repository: https://github.com/bman4789/weatherBot

import unittest
import sys
import logging
import os
import random
import tweepy
import forecastio
import pytz
import datetime
import configparser
from testfixtures import LogCapture


import weatherBot
import keys
import strings
import utils
from utils import Time

# TODO write tests


class TestUtils(unittest.TestCase):
    def test_centerpoint(self):
        """Testing finding a centerpoint from a bounding box of locations"""
        box = [[-93.207783, 44.89076], [-93.003514, 44.89076], [-93.003514, 44.992279], [-93.207783, 44.992279]]
        average = utils.centerpoint(box)
        self.assertEqual(average[0], 44.9415195)
        self.assertEqual(average[1], -93.1056485)

    def test_get_wind_direction(self):
        """Testing if wind direction conversions are successful"""
        self.assertEqual(utils.get_wind_direction(0), 'N')
        self.assertEqual(utils.get_wind_direction(338), 'N')
        self.assertEqual(utils.get_wind_direction(65), 'NE')
        self.assertEqual(utils.get_wind_direction(110), 'E')
        self.assertEqual(utils.get_wind_direction(150), 'SE')
        self.assertEqual(utils.get_wind_direction(200), 'S')
        self.assertEqual(utils.get_wind_direction(240), 'SW')
        self.assertEqual(utils.get_wind_direction(290), 'W')
        self.assertEqual(utils.get_wind_direction(330), 'NW')
        self.assertEqual(utils.get_wind_direction(400), 'N')
        self.assertEqual(utils.get_wind_direction(-4), 'N')
        self.assertEqual(utils.get_wind_direction('five'), '')

    def test_get_units(self):
        """Testing getting units from a country/unit identifier"""
        self.assertEqual(utils.get_units('us')['unit'], 'us')
        self.assertEqual(utils.get_units('us')['nearestStormDistance'], 'mph')
        self.assertEqual(utils.get_units('us')['precipIntensity'], 'in/h')
        self.assertEqual(utils.get_units('us')['precipIntensityMax'], 'in/h')
        self.assertEqual(utils.get_units('us')['precipAccumulation'], 'in')
        self.assertEqual(utils.get_units('us')['temperature'], 'F')
        self.assertEqual(utils.get_units('us')['temperatureMin'], 'F')
        self.assertEqual(utils.get_units('us')['temperatureMax'], 'F')
        self.assertEqual(utils.get_units('us')['apparentTemperature'], 'F')
        self.assertEqual(utils.get_units('us')['dewPoint'], 'F')
        self.assertEqual(utils.get_units('us')['windSpeed'], 'mph')
        self.assertEqual(utils.get_units('us')['pressure'], 'mb')
        self.assertEqual(utils.get_units('us')['visibility'], 'mi')
        self.assertEqual(utils.get_units('ca')['unit'], 'ca')
        self.assertEqual(utils.get_units('ca')['nearestStormDistance'], 'km')
        self.assertEqual(utils.get_units('ca')['precipIntensity'], 'mm/h')
        self.assertEqual(utils.get_units('ca')['precipIntensityMax'], 'mm/h')
        self.assertEqual(utils.get_units('ca')['precipAccumulation'], 'cm')
        self.assertEqual(utils.get_units('ca')['temperature'], 'C')
        self.assertEqual(utils.get_units('ca')['temperatureMin'], 'C')
        self.assertEqual(utils.get_units('ca')['temperatureMax'], 'C')
        self.assertEqual(utils.get_units('ca')['apparentTemperature'], 'C')
        self.assertEqual(utils.get_units('ca')['dewPoint'], 'C')
        self.assertEqual(utils.get_units('ca')['windSpeed'], 'km/h')
        self.assertEqual(utils.get_units('ca')['pressure'], 'hPa')
        self.assertEqual(utils.get_units('ca')['visibility'], 'km')
        self.assertEqual(utils.get_units('uk2')['unit'], 'uk2')
        self.assertEqual(utils.get_units('uk2')['nearestStormDistance'], 'mi')
        self.assertEqual(utils.get_units('uk2')['precipIntensity'], 'mm/h')
        self.assertEqual(utils.get_units('uk2')['precipIntensityMax'], 'mm/h')
        self.assertEqual(utils.get_units('uk2')['precipAccumulation'], 'cm')
        self.assertEqual(utils.get_units('uk2')['temperature'], 'C')
        self.assertEqual(utils.get_units('uk2')['temperatureMin'], 'C')
        self.assertEqual(utils.get_units('uk2')['temperatureMax'], 'C')
        self.assertEqual(utils.get_units('uk2')['apparentTemperature'], 'C')
        self.assertEqual(utils.get_units('uk2')['dewPoint'], 'C')
        self.assertEqual(utils.get_units('uk2')['windSpeed'], 'mph')
        self.assertEqual(utils.get_units('uk2')['pressure'], 'hPa')
        self.assertEqual(utils.get_units('uk2')['visibility'], 'mi')
        self.assertEqual(utils.get_units('si')['unit'], 'si')
        self.assertEqual(utils.get_units('si')['nearestStormDistance'], 'km')
        self.assertEqual(utils.get_units('si')['precipIntensity'], 'mm/h')
        self.assertEqual(utils.get_units('si')['precipIntensityMax'], 'mm/h')
        self.assertEqual(utils.get_units('si')['precipAccumulation'], 'cm')
        self.assertEqual(utils.get_units('si')['temperature'], 'C')
        self.assertEqual(utils.get_units('si')['temperatureMin'], 'C')
        self.assertEqual(utils.get_units('si')['temperatureMax'], 'C')
        self.assertEqual(utils.get_units('si')['apparentTemperature'], 'C')
        self.assertEqual(utils.get_units('si')['dewPoint'], 'C')
        self.assertEqual(utils.get_units('si')['windSpeed'], 'm/s')
        self.assertEqual(utils.get_units('si')['pressure'], 'hPa')
        self.assertEqual(utils.get_units('si')['visibility'], 'km')

    def test_precipitation_intensity(self):
        """Testing getting string description from precipitation intensity"""
        self.assertEqual(utils.precipitation_intensity(0.00, 'in/h'), 'none')
        self.assertEqual(utils.precipitation_intensity(0.002, 'in/h'), 'very-light')
        self.assertEqual(utils.precipitation_intensity(0.017, 'in/h'), 'light')
        self.assertEqual(utils.precipitation_intensity(0.1, 'in/h'), 'moderate')
        self.assertEqual(utils.precipitation_intensity(0.4, 'in/h'), 'heavy')
        self.assertEqual(utils.precipitation_intensity(0.00, 'mm/h'), 'none')
        self.assertEqual(utils.precipitation_intensity(0.051, 'mm/h'), 'very-light')
        self.assertEqual(utils.precipitation_intensity(0.432, 'mm/h'), 'light')
        self.assertEqual(utils.precipitation_intensity(2.540, 'mm/h'), 'moderate')
        self.assertEqual(utils.precipitation_intensity(5.08, 'mm/h'), 'heavy')

    def test_get_local_datetime(self):
        dt = datetime.datetime.fromtimestamp(1461731335)  # datetime.datetime(2016, 4, 26, 23, 28, 55)
        timezone_id = 'Europe/Copenhagen'
        localized_dt = utils.get_local_datetime(timezone_id, dt)
        correct_dt = datetime.datetime.fromtimestamp(1461738535)  # datetime.datetime(2016, 4, 27, 1, 28, 55)
        self.assertEqual(localized_dt, pytz.timezone('Europe/Copenhagen').localize(correct_dt))

    def test_get_utc_datetime(self):
        dt = datetime.datetime.fromtimestamp(1461738535)  # datetime.datetime(2016, 4, 27, 1, 28, 55)
        timezone_id = 'Europe/Copenhagen'
        utc_dt = utils.get_utc_datetime(timezone_id, dt)
        correct_dt = pytz.timezone('Europe/Copenhagen').localize(dt).astimezone(pytz.utc)
        self.assertEqual(utc_dt, correct_dt)

    def test_parse_time_string(self):
        self.assertEqual(utils.parse_time_string('7:00'), Time(hour=7, minute=0))
        self.assertEqual(utils.parse_time_string('0:0'), Time(hour=0, minute=0))
        self.assertEqual(utils.parse_time_string('000000001:00000'), Time(hour=1, minute=0))
        self.assertEqual(utils.parse_time_string('18:00000001'), Time(hour=18, minute=1))
        self.assertEqual(utils.parse_time_string('22:59'), Time(hour=22, minute=59))
        self.assertEqual(utils.parse_time_string('1:45'), Time(hour=1, minute=45))
        self.assertEqual(utils.parse_time_string('0000002:000003'), Time(hour=2, minute=3))
        with self.assertRaises(utils.InvalidTimeError):
            utils.parse_time_string('12')
        with self.assertRaises(utils.InvalidTimeError):
            utils.parse_time_string('1:2:3;4')
        with self.assertRaises(utils.InvalidTimeError):
            utils.parse_time_string('34:')
        with self.assertRaises(utils.InvalidTimeError):
            utils.parse_time_string(':5')
        with self.assertRaises(utils.InvalidTimeError):
            utils.parse_time_string(':')
        with self.assertRaises(utils.InvalidTimeError):
            utils.parse_time_string('not an int:but nice try')
        with self.assertRaises(utils.InvalidTimeError):
            utils.parse_time_string('34:00')
        with self.assertRaises(utils.InvalidTimeError):
            utils.parse_time_string('00:65')
        with self.assertRaises(utils.InvalidTimeError):
            utils.parse_time_string('-46:00')
        with self.assertRaises(utils.InvalidTimeError):
            utils.parse_time_string('00:-34')

    def test_get_times(self):
        raw_simple = '7:00\n12:00\n15:00\n18:00\n22:00'
        raw_complex = '0:0\n00000000001:00000\n18:00000001\n22:59\n23:00\n1:45\n00:00\n23:59\n1:01\n01:00\n01:02\n11:32'
        list_simple = [Time(hour=7, minute=0),
                       Time(hour=12, minute=0),
                       Time(hour=15, minute=0),
                       Time(hour=18, minute=0),
                       Time(hour=22, minute=0)]
        list_complex = [Time(hour=0, minute=0),
                        Time(hour=0, minute=0),
                        Time(hour=1, minute=0),
                        Time(hour=1, minute=0),
                        Time(hour=1, minute=1),
                        Time(hour=1, minute=2),
                        Time(hour=1, minute=45),
                        Time(hour=11, minute=32),
                        Time(hour=18, minute=1),
                        Time(hour=22, minute=59),
                        Time(hour=23, minute=0),
                        Time(hour=23, minute=59)]
        self.assertEqual(utils.get_times(raw_simple), list_simple)
        self.assertEqual(utils.get_times(raw_complex), list_complex)


class TestStrings(unittest.TestCase):
    def test_get_precipitation(self):
        """Testing if a precipitation condition is met"""
        # testing for 'none' with too low of a probability or precipitation type is 'none'
        self.assertEqual(strings.get_precipitation(0.3, 0.5, 'rain', utils.get_units('us')),
                         strings.Condition(type='none', text=''))
        self.assertEqual(strings.get_precipitation(0.3, 1, 'none', utils.get_units('us')),
                         strings.Condition(type='none', text=''))
        self.assertEqual(strings.get_precipitation(0, 1, 'rain', utils.get_units('us')),
                         strings.Condition(type='none', text=''))
        self.assertEqual(strings.get_precipitation(0, 1, 'none', utils.get_units('us')),
                         strings.Condition(type='none', text=''))
        # testing with a few possible conditions
        self.assertEqual(strings.get_precipitation(0.3, 1, 'rain', utils.get_units('us'))[0], 'moderate-rain')
        self.assertEqual(strings.get_precipitation(0.4, 0.85, 'snow', utils.get_units('us'))[0], 'heavy-snow')
        self.assertEqual(strings.get_precipitation(0.06, 1, 'sleet', utils.get_units('us'))[0], 'light-sleet')
        self.assertEqual(strings.get_precipitation(0.005, 1, 'rain', utils.get_units('us'))[0], 'very-light-rain')


class TestWB(unittest.TestCase):
    def setUp(self):
        self.location = {'lat': 55.76, 'lng': 12.49, 'name': 'Lyngby-Taarbæk, Hovedstaden'}
        self.wd_us = {
            'windBearing': 'SW',
            'temp_and_unit': '44ºF',
            'apparentTemperature_and_unit': '38ºF',
            'latitude': 55.76,
            'units': {
                'unit': 'us',
                'temperatureMin': 'F',
                'pressure': 'mb',
                'precipIntensityMax': 'in/h',
                'temperatureMax': 'F',
                'visibility': 'mi',
                'apparentTemperature': 'F',
                'dewPoint': 'F',
                'precipAccumulation': 'in',
                'nearestStormDistance': 'mph',
                'precipIntensity': 'in/h',
                'windSpeed': 'mph',
                'temperature': 'F'
            },
            'summary': 'mostly cloudy',
            'apparentTemperature': 38.35,
            'longitude': 12.49,
            'location': 'Lyngby-Taarbæk, Hovedstaden',
            'valid': True,
            'forecast': {},
            'windSpeed_and_unit': '12 mph',
            'humidity': 95,
            'nearestStormDistance': 99999,
            'precipIntensity': 0,
            'windSpeed': 11.77,
            'temp': 44.32,
            'icon': 'partly-cloudy-night'
        }
        self.wd_ca = {
            'windBearing': 'SW',
            'temp_and_unit': '7ºC',
            'apparentTemperature_and_unit': '3ºC',
            'latitude': 55.76,
            'units': {
                'unit': 'ca',
                'temperatureMin': 'C',
                'pressure': 'hPa',
                'precipIntensityMax': 'mm/h',
                'temperatureMax': 'C',
                'visibility': 'km',
                'apparentTemperature': 'C',
                'dewPoint': 'C',
                'precipAccumulation': 'cm',
                'nearestStormDistance': 'km/h',
                'precipIntensity': 'mm/h',
                'windSpeed': 'km/h',
                'temperature': 'C'
            },
            'summary': 'mostly cloudy',
            'apparentTemperature': 3.46,
            'longitude': 12.49,
            'location': 'Lyngby-Taarbæk, Hovedstaden',
            'valid': True,
            'forecast': {},
            'windSpeed_and_unit': '19 km/h',
            'humidity': 95,
            'nearestStormDistance': 99999,
            'precipIntensity': 0,
            'windSpeed': 18.94,
            'temp': 6.78,
            'icon': 'partly-cloudy-night'
        }
        self.wd_uk2 = {
            'windBearing': 'SW',
            'temp_and_unit': '7ºC',
            'apparentTemperature_and_unit': '3ºC',
            'latitude': 55.76,
            'units': {
                'unit': 'uk2',
                'temperatureMin': 'C',
                'pressure': 'hPa',
                'precipIntensityMax': 'mm/h',
                'temperatureMax': 'C',
                'visibility': 'mi',
                'apparentTemperature': 'C',
                'dewPoint': 'C',
                'precipAccumulation': 'cm',
                'nearestStormDistance': 'mi',
                'precipIntensity': 'mm/h',
                'windSpeed': 'mph',
                'temperature': 'C'
            },
            'summary': 'mostly cloudy',
            'apparentTemperature': 3.43,
            'longitude': 12.49,
            'location': 'Lyngby-Taarbæk, Hovedstaden',
            'valid': True,
            'forecast': {},
            'windSpeed_and_unit': '12 mph',
            'humidity': 95,
            'nearestStormDistance': 99999,
            'precipIntensity': 0,
            'windSpeed': 11.77,
            'temp': 6.76,
            'icon': 'partly-cloudy-night'
        }
        self.wd_si = {
            'windBearing': 'SW',
            'temp_and_unit': '7ºC',
            'apparentTemperature_and_unit': '3ºC',
            'latitude': 55.76,
            'units': {
                'unit': 'si',
                'temperatureMin': 'C',
                'pressure': 'hPa',
                'precipIntensityMax': 'mm/h',
                'temperatureMax': 'C',
                'visibility': 'km',
                'apparentTemperature': 'C',
                'dewPoint': 'C',
                'precipAccumulation': 'cm',
                'nearestStormDistance': 'km/h',
                'precipIntensity': 'mm/h',
                'windSpeed': 'm/s',
                'temperature': 'C'
            },
            'summary': 'mostly cloudy',
            'apparentTemperature': 3.41,
            'longitude': 12.49,
            'location': 'Lyngby-Taarbæk, Hovedstaden',
            'valid': True,
            'forecast': {},
            'windSpeed_and_unit': '5 m/s',
            'humidity': 94,
            'nearestStormDistance': 99999,
            'precipIntensity': 0,
            'windSpeed': 5.26,
            'temp': 6.74,
            'icon': 'partly-cloudy-night'
        }

    def test_config(self):
        """Testing config file handling"""
        equal = {
            'basic': {
                'dm_errors': False,
                'units': 'si',
                'tweet_location': False,
                'hashtag': '',
                'refresh': 300
            },
            'scheduled_times': {
                'forecast': Time(hour=6, minute=0),
                'conditions': [Time(hour=7, minute=0),
                               Time(hour=12, minute=0),
                               Time(hour=15, minute=0),
                               Time(hour=18, minute=0),
                               Time(hour=22, minute=0)]
            },
            'default_location': {
                'lat': -79,
                'lng': 12,
                'name': 'Just a Test'
            },
            'variable_location': {
                'enabled': True,
                'user': 'test_user'
            },
            'log': {
                'enabled': False,
                'log_path': '/tmp/weatherBotTest.log'
            },
            'throttles': {
                'default': 24,
                'wind-chill': 23,
                'medium-wind': 22,
                'heavy-wind': 21,
                'fog': 20,
                'cold': 19,
                'hot': 18,
                'dry': 17,
                'heavy-rain': 16,
                'moderate-rain': 15,
                'light-rain': 14,
                'very-light-rain': 13,
                'heavy-snow': 12,
                'moderate-snow': 11,
                'light-snow': 10,
                'very-light-snow': 9,
                'heavy-sleet': 8,
                'moderate-sleet': 7,
                'light-sleet': 6,
                'very-light-sleet': 5,
                'heavy-hail': 4,
                'moderate-hail': 3,
                'light-hail': 2,
                'very-light-hail': 1
            }
        }

        conf = configparser.ConfigParser()
        conf['basic'] = {
            'dm_errors': 'off',
            'units': 'si',
            'tweet_location': 'no',
            'hashtag': '',
            'refresh': '300'
        }
        conf['scheduled times'] = {
            'forecast': '6:00',
            'conditions': '7:00\n12:00\n15:00\n18:00\n22:00'
        }
        conf['default location'] = {
            'lat': '-79',
            'lng': '12',
            'name': 'Just a Test'
        }
        conf['variable location'] = {
            'enabled': 'yes',
            'user': 'test_user'
        }
        conf['log'] = {
            'enabled': '0',
            'log_path': '/tmp/weatherBotTest.log'
        }
        conf['throttles'] = {
            'default': '24',
            'wind-chill': '23',
            'medium-wind': '22',
            'heavy-wind': '21',
            'fog': '20',
            'cold': '19',
            'hot': '18',
            'dry': '17',
            'heavy-rain': '16',
            'moderate-rain': '15',
            'light-rain': '14',
            'very-light-rain': '13',
            'heavy-snow': '12',
            'moderate-snow': '11',
            'light-snow': '10',
            'very-light-snow': '9',
            'heavy-sleet': '8',
            'moderate-sleet': '7',
            'light-sleet': '6',
            'very-light-sleet': '5',
            'heavy-hail': '4',
            'moderate-hail': '3',
            'light-hail': '2',
            'very-light-hail': '1'
        }
        with open(os.getcwd() + '/weatherBotTest.conf', 'w') as configfile:
            conf.write(configfile)
        weatherBot.load_config(os.getcwd() + '/weatherBotTest.conf')
        self.assertEqual(weatherBot.CONFIG, equal)
        os.remove(os.getcwd() + '/weatherBotTest.conf')

    def test_logging(self):
        """Testing if the system version is in the log and log file"""
        with LogCapture() as l:
            logger = logging.getLogger()
            logger.info('info')
            weatherBot.initialize_logger(True, os.getcwd() + '/weatherBotTest.log')
            logger.debug('debug')
            logger.warning('uh oh')
        l.check(('root', 'INFO', 'info'), ('root', 'INFO', 'Starting weatherBot with Python ' + sys.version),
                ('root', 'DEBUG', 'debug'), ('root', 'WARNING', 'uh oh'))
        path = os.path.join(os.getcwd(), 'weatherBotTest.log')
        with open(path, 'rb') as path:
            data = path.read()
        self.assertTrue(bytes(sys.version, 'UTF-8') in data)
        self.assertFalse(bytes('debug', 'UTF-8') in data)
        self.assertTrue(bytes('uh oh', 'UTF-8') in data)
        os.remove(os.getcwd() + '/weatherBotTest.log')

    def test_get_location_from_user_timeline(self):
        """Testing getting a location from twitter account's recent tweets"""
        fallback = {'lat': 55.76, 'lng': 12.49, 'name': 'Lyngby-Taarbæk, Hovedstaden'}
        morris = {'lat': 45.585, 'lng': -95.91, 'name': 'Morris, MN'}
        loc = weatherBot.get_location_from_user_timeline('MorrisMNWeather', fallback)
        self.assertTrue(type(loc) is dict)
        self.assertEqual(loc, morris)
        self.assertEqual(weatherBot.get_location_from_user_timeline('twitter', fallback), fallback)

    def test_get_forecast_object(self):
        """Testing getting the forecastio object"""
        forecast = weatherBot.get_forecast_object(self.location['lat'], self.location['lng'], 'us')
        self.assertEqual(forecast.response.status_code, 200)
        bad_forecast = weatherBot.get_forecast_object(345.5, 123.45, 'us')
        self.assertEqual(bad_forecast, None)

    # def test_get_normal_weather_variables(self):
    #     """Testing if weather data fields copied successfully"""
    #     weather_data = weatherBot.get_weather_variables(ydataNorm)
    #     self.assertEqual(weather_data['windSpeed'], 9.0)
    #     self.assertEqual(weather_data['wind_direction'], 'NW')
    #     self.assertEqual(weather_data['apparentTemperature'], 37)
    #     self.assertEqual(weather_data['windSpeed_and_unit'], '9 mph')
    #     self.assertEqual(weather_data['humidity'], 70)
    #     self.assertEqual(weather_data['temp'], 43)
    #     self.assertEqual(weather_data['code'], 33)
    #     self.assertEqual(weather_data['condition'], 'fair')
    #     self.assertEqual(weather_data['deg_unit'], deg + 'F')
    #     self.assertEqual(weather_data['temp_and_unit'], '43' + deg + 'F')
    #     self.assertEqual(weather_data['city'], 'Morris')
    #     self.assertEqual(weather_data['region'], 'MN')
    #     self.assertEqual(weather_data['latitude'], '45.59')
    #     self.assertEqual(weather_data['longitude'], '-95.9')
    #     self.assertEqual(weather_data['forecast'], [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}])
    #     self.assertTrue(weather_data['valid'])
    #
    # def test_get_empty_weather_variables(self):
    #     """Testing if variables with a fallback are set correctly"""
    #     ydata = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '43', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '33', 'text': 'Fair'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'mph', 'temperature': 'F', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '37', 'direction': '', 'speed': ''}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data = weatherBot.get_weather_variables(ydata)
    #     self.assertEqual(weather_data['windSpeed'], 0.0)
    #     self.assertEqual(weather_data['wind_direction'], 'N')
    #     self.assertEqual(weather_data['apparentTemperature'], 37)
    #     self.assertEqual(weather_data['windSpeed_and_unit'], '0 mph')
    #     self.assertEqual(weather_data['humidity'], 70)
    #     self.assertEqual(weather_data['temp'], 43)
    #     self.assertEqual(weather_data['code'], 33)
    #     self.assertEqual(weather_data['condition'], 'fair')
    #     self.assertEqual(weather_data['deg_unit'], deg + 'F')
    #     self.assertEqual(weather_data['temp_and_unit'], '43' + deg + 'F')
    #     self.assertEqual(weather_data['city'], 'Morris')
    #     self.assertEqual(weather_data['region'], 'MN')
    #     self.assertEqual(weather_data['latitude'], '45.59')
    #     self.assertEqual(weather_data['longitude'], '-95.9')
    #     self.assertEqual(weather_data['forecast'], [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}])
    #     self.assertTrue(weather_data['valid'])
    #
    # def test_get_weather_variables_error(self):
    #     """Testing if getting weather variables with a malformed input is valid"""
    #     ydata = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {}, 'count': 1}}}
    #     weather_data = weatherBot.get_weather_variables(ydata)
    #     self.assertFalse(weather_data['valid'])
    #
    # def test_normal_tweet(self):
    #     """Testing if normal tweet contains the condition and temperature"""
    #     weather_data = weatherBot.get_weather_variables(ydataNorm)
    #     returned = weatherBot.make_normal_tweet(weather_data)
    #     self.assertTrue('fair' in returned)
    #     self.assertTrue('43' + deg + 'F' in returned)
    #
    # def test_make_special_tweet_normal(self):
    #     """Testing if normal event is triggered"""
    #     weather_data = weatherBot.get_weather_variables(ydataNorm)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data), 'normal')
    #
    # def test_make_special_tweet_error3200(self):
    #     """Testing if weather code is 3200/an error event is triggered"""
    #     ydata = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '43', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '3200', 'text': 'Fair'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'mph', 'temperature': 'F', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '37', 'direction': '310', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data = weatherBot.get_weather_variables(ydata)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data), 'Someone messed up, apparently the current condition is \"not available\" http://www.reactiongifs.com/wp-content/uploads/2013/08/air-quotes.gif')
    #
    # def test_make_special_tweet_very_hot(self):
    #     """Testing if very hot temperatures event is triggered"""
    #     ydata_f = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '100', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '33', 'text': 'Fair'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'mph', 'temperature': 'F', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '95', 'direction': '310', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data_f = weatherBot.get_weather_variables(ydata_f)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data_f), 'Holy moly it\'s 100' + deg + 'F. I could literally (figuratively) melt.')
    #     ydata_c = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '37', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '33', 'text': 'Fair'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'km/h', 'temperature': 'C', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '35', 'direction': '310', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data_c = weatherBot.get_weather_variables(ydata_c)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data_c), 'Holy moly it\'s 37' + deg + 'C. I could literally (figuratively) melt.')
    #     ydata_c2 = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '52', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '33', 'text': 'Fair'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'km/h', 'temperature': 'C', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '35', 'direction': '310', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data_c2 = weatherBot.get_weather_variables(ydata_c2)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data_c2), 'normal')
    #
    # def test_make_special_tweet_cold(self):
    #     """Testing if cold temperatures event is triggered"""
    #     ydata_f = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '-22', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '33', 'text': 'Fair'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'mph', 'temperature': 'F', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '-26', 'direction': '310', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data_f = weatherBot.get_weather_variables(ydata_f)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data_f), 'It\'s -22' + deg + 'F. Too cold.')
    #     ydata_c = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '-30', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '33', 'text': 'Fair'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'km/h', 'temperature': 'C', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '-33', 'direction': '310', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data_c = weatherBot.get_weather_variables(ydata_c)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data_c), 'It\'s -30' + deg + 'C. Too cold.')
    #
    # def test_make_special_tweet_low_humidity(self):
    #     """Testing if low humidity event is triggered"""
    #     ydata = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '4', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '43', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '3200', 'text': 'Fair'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'mph', 'temperature': 'F', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '37', 'direction': '310', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data = weatherBot.get_weather_variables(ydata)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data), 'It\'s dry as strained pasta. 4% humid right now.')
    #
    # def test_make_special_tweet_high_wind(self):
    #     """Testing if high wind event is triggered"""
    #     ydata_f = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '43', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '33', 'text': 'Fair'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'mph', 'temperature': 'F', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '-26', 'direction': '310', 'speed': '35'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data_f = weatherBot.get_weather_variables(ydata_f)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data_f),
    #                      'Hold onto your hats, the wind is blowing at 35 mph coming from the NW.')
    #     ydata_c = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '8', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '33', 'text': 'Fair'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'km/h', 'temperature': 'C', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '-33', 'direction': '310', 'speed': '56'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data_c = weatherBot.get_weather_variables(ydata_c)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data_c),
    #                      'Hold onto your hats, the wind is blowing at 56 km/h coming from the NW.')
    #
    # def test_make_special_tweet_drizzle(self):
    #     """Testing if drizzle event is triggered"""
    #     ydata1 = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '43', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '8', 'text': 'Fair'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'mph', 'temperature': 'F', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '-26', 'direction': '310', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data1 = weatherBot.get_weather_variables(ydata1)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data1), 'Drizzlin\' yo.')
    #     ydata2 = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '8', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '9', 'text': 'Fair'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'km/h', 'temperature': 'C', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '-33', 'direction': '310', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data2 = weatherBot.get_weather_variables(ydata2)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data2), 'Drizzlin\' yo.')
    #
    # def test_make_special_tweet_snow(self):
    #     """Testing if snow event is triggered"""
    #     ydata1 = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '43', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '13', 'text': 'Snow Flurries'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'mph', 'temperature': 'F', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '-26', 'direction': '310', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data1 = weatherBot.get_weather_variables(ydata1)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data1), 'Snow flurries. Bundle up.')
    #     ydata2 = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '8', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '14', 'text': 'Light Snow Showers'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'km/h', 'temperature': 'C', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '-33', 'direction': '310', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data2 = weatherBot.get_weather_variables(ydata2)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data2), 'Light snow showers. Bundle up.')
    #     ydata3 = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '43', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '15', 'text': 'Blowing Snow'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'mph', 'temperature': 'F', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '-26', 'direction': '310', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data3 = weatherBot.get_weather_variables(ydata3)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data3), 'Blowing snow. Bundle up.')
    #     ydata4 = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '8', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '16', 'text': 'Snow'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'km/h', 'temperature': 'C', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '-33', 'direction': '310', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data4 = weatherBot.get_weather_variables(ydata4)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data4), 'Snow. Bundle up.')
    #     ydata5 = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '43', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '41', 'text': 'Heavy Snow'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'mph', 'temperature': 'F', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '-26', 'direction': '310', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data5 = weatherBot.get_weather_variables(ydata5)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data5), 'Heavy snow. Bundle up.')
    #     ydata6 = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '8', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '43', 'text': 'Heavy Snow'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'km/h', 'temperature': 'C', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '-33', 'direction': '310', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data6 = weatherBot.get_weather_variables(ydata6)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data6), 'Heavy snow. Bundle up.')
    #
    # def test_make_special_tweet_mixes(self):
    #     """Testing if mixes event is triggered"""
    #     ydata1 = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '43', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '5', 'text': 'Mixed Rain and Snow'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'mph', 'temperature': 'F', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '-26', 'direction': '310', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data1 = weatherBot.get_weather_variables(ydata1)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data1),
    #                      'What a mix! Currently, there\'s mixed rain and snow falling from the sky.')
    #     ydata2 = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '8', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '6', 'text': 'Mixed Rain and Sleet'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'km/h', 'temperature': 'C', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '-33', 'direction': '310', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data2 = weatherBot.get_weather_variables(ydata2)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data2),
    #                      'What a mix! Currently, there\'s mixed rain and sleet falling from the sky.')
    #     ydata3 = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '43', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '6', 'text': 'Mixed Snow and Sleet'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'mph', 'temperature': 'F', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '-26', 'direction': '310', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data3 = weatherBot.get_weather_variables(ydata3)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data3),
    #                      'What a mix! Currently, there\'s mixed snow and sleet falling from the sky.')
    #
    # def test_make_special_tweet_fog(self):
    #     """Testing if fog event is triggered"""
    #     ydata = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '4', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '43', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '20', 'text': 'Fog'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'mph', 'temperature': 'F', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '37', 'direction': '310', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data1 = weatherBot.get_weather_variables(ydata)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data1), 'Do you even fog bro?')
    #
    # def test_make_special_tweet_hail(self):
    #     """Testing if hail event is triggered"""
    #     ydata1 = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '43', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '17', 'text': 'Hail'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'mph', 'temperature': 'F', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '-26', 'direction': '310', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data1 = weatherBot.get_weather_variables(ydata1)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data1), 'IT\'S HAILIN\'!')
    #     ydata2 = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '8', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '35', 'text': 'Mixed Rain and Hail'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'km/h', 'temperature': 'C', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '-33', 'direction': '310', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data2 = weatherBot.get_weather_variables(ydata2)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data2), 'IT\'S HAILIN\'!')
    #
    # def test_make_special_tweet_thunderstorms(self):
    #     """Testing if thunderstorm event is triggered"""
    #     ydata = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '4', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '43', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '4', 'text': 'Thunderstorms'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'mph', 'temperature': 'F', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '37', 'direction': '310', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data = weatherBot.get_weather_variables(ydata)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data), 'Meh, just a thunderstorm.')
    #
    # def test_make_special_tweet_severe_thunderstorms(self):
    #     """Testing if severe thunderstorm event is triggered"""
    #     ydata = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '4', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '43', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '3', 'text': 'Severe Thunderstorms'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'mph', 'temperature': 'F', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '37', 'direction': '310', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data = weatherBot.get_weather_variables(ydata)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data),
    #                      'IT BE STORMIN\'! Severe thunderstorms right now.')
    #
    # def test_make_special_tweet_very_severe_storms(self):
    #     """Testing if very severe thunderstorm event is triggered"""
    #     ydata1 = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '43', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '0', 'text': 'Tornado'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'mph', 'temperature': 'F', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '-26', 'direction': '310', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data1 = weatherBot.get_weather_variables(ydata1)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data1), 'HOLY SHIT, THERE\'S A TORNADO!')
    #     ydata2 = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '8', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '1', 'text': 'Tropical Storm'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'km/h', 'temperature': 'C', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '-33', 'direction': '310', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data2 = weatherBot.get_weather_variables(ydata2)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data2), 'HOLY SHIT, THERE\'S A TROPICAL STORM!')
    #     ydata3 = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '43', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '2', 'text': 'Hurricane'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'mph', 'temperature': 'F', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '-26', 'direction': '310', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data3 = weatherBot.get_weather_variables(ydata3)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data3), 'HOLY SHIT, THERE\'S A HURRICANE!')
    #
    # def test_make_special_tweet_wind_condition(self):
    #     """Testing if wind event is triggered"""
    #     ydata1 = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '43', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '23', 'text': 'Blustery'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'mph', 'temperature': 'F', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '-26', 'direction': '310', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data1 = weatherBot.get_weather_variables(ydata1)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data1),
    #                      'Looks like we\'ve got some wind at 9 mph coming from the NW.')
    #     ydata2 = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '8', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '24', 'text': 'Windy'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'km/h', 'temperature': 'C', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '-33', 'direction': '310', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data2 = weatherBot.get_weather_variables(ydata2)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data2),
    #                      'Looks like we\'ve got some wind at 9 km/h coming from the NW.')
    #
    # def test_make_special_tweet_windchill(self):
    #     """Testing if windchill event is triggered"""
    #     ydata_f = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '-22', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '33', 'text': 'Fair'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'mph', 'temperature': 'F', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '-34', 'direction': '15', 'speed': '9'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data1 = weatherBot.get_weather_variables(ydata_f)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data1),
    #                      'Wow, mother nature hates us. The windchill is -34' + deg +
    #                      'F and the wind is blowing at 9 mph from the N. My face hurts.')
    #     ydata_c = {'query': {'lang': 'en-US', 'created': '2015-04-02T05:49:55Z', 'results': {'channel': {'image': {'link': 'http://weather.yahoo.com', 'width': '142', 'url': 'http://l.yimg.com/a/i/brand/purplelogo//uh/us/news-wea.gif', 'height': '18', 'title': 'Yahoo! Weather'}, 'atmosphere': {'rising': '1', 'visibility': '10', 'humidity': '70', 'pressure': '29.67'}, 'item': {'lat': '45.59', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'forecast': [{'low': '40', 'text': 'Partly Cloudy', 'high': '73', 'day': 'Wed', 'date': '1 Apr 2015', 'code': '29'}, {'low': '23', 'text': 'Partly Cloudy/Wind', 'high': '59', 'day': 'Thu', 'date': '2 Apr 2015', 'code': '24'}, {'low': '28', 'text': 'Partly Cloudy', 'high': '46', 'day': 'Fri', 'date': '3 Apr 2015', 'code': '30'}, {'low': '32', 'text': 'Mostly Sunny', 'high': '57', 'day': 'Sat', 'date': '4 Apr 2015', 'code': '34'}, {'low': '29', 'text': 'Partly Cloudy', 'high': '52', 'day': 'Sun', 'date': '5 Apr 2015', 'code': '30'}], 'description': '\n<img src="http://l.yimg.com/a/i/us/we/52/33.gif"/><br />\n<b>Current Conditions:</b><br />\nFair, 43 F<BR />\n<BR /><b>Forecast:</b><BR />\nWed - Partly Cloudy. High: 73 Low: 40<br />\nThu - Partly Cloudy/Wind. High: 59 Low: 23<br />\nFri - Partly Cloudy. High: 46 Low: 28<br />\nSat - Mostly Sunny. High: 57 Low: 32<br />\nSun - Partly Cloudy. High: 52 Low: 29<br />\n<br />\n<a href="http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html">Full Forecast at Yahoo! Weather</a><BR/><BR/>\n(provided by <a href="http://www.weather.com" >The Weather Channel</a>)<br/>\n', 'guid': {'isPermaLink': 'false', 'content': 'USMN0518_2015_04_05_7_00_CDT'}, 'condition': {'temp': '-30', 'date': 'Thu, 02 Apr 2015 12:33 am CDT', 'code': '33', 'text': 'Fair'}, 'long': '-95.9', 'title': 'Conditions for Morris, MN at 12:33 am CDT', 'pubDate': 'Thu, 02 Apr 2015 12:33 am CDT'}, 'location': {'country': 'United States', 'city': 'Morris', 'region': 'MN'}, 'units': {'speed': 'km/h', 'temperature': 'C', 'pressure': 'in', 'distance': 'mi'}, 'wind': {'chill': '-38', 'direction': '163', 'speed': '42'}, 'ttl': '60', 'link': 'http://us.rd.yahoo.com/dailynews/rss/weather/Morris__MN/*http://weather.yahoo.com/forecast/USMN0518_f.html', 'lastBuildDate': 'Thu, 02 Apr 2015 12:33 am CDT', 'description': 'Yahoo! Weather for Morris, MN', 'astronomy': {'sunrise': '7:03 am', 'sunset': '7:49 pm'}, 'title': 'Yahoo! Weather - Morris, MN', 'language': 'en-us'}}, 'count': 1}}
    #     weather_data2 = weatherBot.get_weather_variables(ydata_c)
    #     self.assertEqual(weatherBot.make_special_tweet(weather_data2),
    #                      'Wow, mother nature hates us. The windchill is -38' + deg +
    #                      'C and the wind is blowing at 42 km/h from the S. My face hurts.')
    #
    # def test_make_forecast(self):
    #     """Testing if forecast contains the conditions, high, and low temperatures"""
    #     weather_data = weatherBot.get_weather_variables(ydataNorm)
    #     now = datetime.now().replace(year=2015, month=4, day=2)
    #     returned = weatherBot.make_forecast(now, weather_data)
    #     self.assertTrue('partly cloudy/wind' in returned)
    #     self.assertTrue('23' + deg + 'F' in returned)
    #     self.assertTrue('59' + deg + 'F' in returned)
    #
    # def test_make_forecast_error(self):
    #     """Testing if error condition tweet is returned"""
    #     weather_data = weatherBot.get_weather_variables(ydataNorm)
    #     now = datetime.now().replace(year=2015, month=4, day=10)
    #     returned = weatherBot.make_forecast(now, weather_data)
    #     self.assertTrue('not available' in returned)
    #
    # def test_do_tweet(self):
    #     """Testing tweeting a test tweet using keys from env variables"""
    #     tweet_location = False
    #     variable_location = False
    #     weather_data = {'region': 'MN', 'code': 33, 'humidity': 70, 'units': {'distance': 'mi', 'pressure': 'in', 'speed': 'mph', 'temperature': 'F'}, 'wind_direction': 'NW', 'city': 'Morris', 'latitude': '45.59', 'temp': 43, 'temp_and_unit': '43ºF', 'condition': 'Fair', 'valid': True, 'deg_unit': 'º F', 'longitude': '-95.9', 'windSpeed': 9.0, 'windSpeed_and_unit': '9 mph', 'apparentTemperature': 37}
    #     content = 'Just running unit tests, this should disappear...  %i' % random.randint(0, 1000)
    #     tweet_content = content + weatherBot.HASHTAG
    #     status = weatherBot.do_tweet(content, weather_data, tweet_location, variable_location)
    #     self.assertEqual(status.text, tweet_content)
    #     # test destroy
    #     api = weatherBot.get_tweepy_api()
    #     deleted = api.destroy_status(id=status.id)
    #     self.assertEqual(deleted.id, status.id)
    #
    # def test_do_tweet_with_location(self):
    #     """Testing tweeting a test tweet with location using keys from env variables"""
    #     tweet_location = True
    #     variable_location = False
    #     weather_data = {'region': 'MN', 'code': 33, 'humidity': 70, 'units': {'distance': 'mi', 'pressure': 'in', 'speed': 'mph', 'temperature': 'F'}, 'wind_direction': 'NW', 'city': 'Morris', 'latitude': '45.59', 'temp': 43, 'temp_and_unit': '43ºF', 'condition': 'Fair', 'valid': True, 'deg_unit': 'º F', 'longitude': '-95.9', 'windSpeed': 9.0, 'windSpeed_and_unit': '9 mph', 'apparentTemperature': 37}
    #     content = 'Just running unit tests, this should disappear...  %i' % random.randint(0, 1000)
    #     tweet_content = content + weatherBot.HASHTAG
    #     status = weatherBot.do_tweet(content, weather_data, tweet_location, variable_location)
    #     self.assertEqual(status.text, tweet_content)
    #     # test destroy
    #     api = weatherBot.get_tweepy_api()
    #     deleted = api.destroy_status(id=status.id)
    #     self.assertEqual(deleted.id, status.id)
    #
    # def test_do_tweet_with_variable_location(self):
    #     """Testing tweeting a test tweet using keys from env variables"""
    #     tweet_location = True
    #     variable_location = True
    #     weather_data = {'region': 'MN', 'code': 33, 'humidity': 70, 'units': {'distance': 'mi', 'pressure': 'in', 'speed': 'mph', 'temperature': 'F'}, 'wind_direction': 'NW', 'city': 'Morris', 'latitude': '45.59', 'temp': 43, 'temp_and_unit': '43ºF', 'condition': 'Fair', 'valid': True, 'deg_unit': 'º F', 'longitude': '-95.9', 'windSpeed': 9.0, 'windSpeed_and_unit': '9 mph', 'apparentTemperature': 37}
    #     content = 'Just running unit tests, this should disappear...  %i' % random.randint(0, 1000)
    #     tweet_content = weather_data['city'] + ", " + weather_data['region'] + ": " + content + weatherBot.HASHTAG
    #     status = weatherBot.do_tweet(content, weather_data, tweet_location, variable_location)
    #     self.assertEqual(status.text, tweet_content)
    #     # test destroy
    #     api = weatherBot.get_tweepy_api()
    #     deleted = api.destroy_status(id=status.id)
    #     self.assertEqual(deleted.id, status.id)

if __name__ == '__main__':
    keys.set_twitter_env_vars()
    keys.set_forecastio_env_vars()
    unittest.main()
