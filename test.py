#!/usr/bin/env python3

# weatherBot tests
# Copyright 2015-2016 Brian Mitchell under the MIT license
# See the GitHub repository: https://github.com/BrianMitchL/weatherBot

import unittest
import sys
import logging
import os
import random
import pytz
import datetime
import configparser
from testfixtures import LogCapture


import weatherBot
import keys
import strings
import utils
from utils import Time
from strings import Condition

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
        """Testing localizing a plain datetime object to a pytz timezone aware object"""
        dt = datetime.datetime.fromtimestamp(1461731335)  # datetime.datetime(2016, 4, 26, 23, 28, 55)
        timezone_id = 'Europe/Copenhagen'
        localized_dt = utils.get_local_datetime(timezone_id, dt)
        correct_dt = datetime.datetime.fromtimestamp(1461738535)  # datetime.datetime(2016, 4, 27, 1, 28, 55)
        self.assertEqual(localized_dt, pytz.timezone('Europe/Copenhagen').localize(correct_dt))

    def test_get_utc_datetime(self):
        """Testing localize a normal datetime object to timezone id, then convert to UTC"""
        dt = datetime.datetime.fromtimestamp(1461738535)  # datetime.datetime(2016, 4, 27, 1, 28, 55)
        timezone_id = 'Europe/Copenhagen'
        utc_dt = utils.get_utc_datetime(timezone_id, dt)
        correct_dt = pytz.timezone('Europe/Copenhagen').localize(dt).astimezone(pytz.utc)
        self.assertEqual(utc_dt, correct_dt)

    def test_parse_time_string(self):
        """Testing parsing string representing time to a Time namedtuple"""
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
        """Testing converting a string of times into a list of Time namedtuples"""
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
            'hour_summary': 'Mostly cloudy for the hour.',
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
            'icon': 'partly-cloudy-night',
            'hour_icon': 'partly-cloudy-night',
            'precipType': 'none',
            'precipProbability': 0,
            'alerts': [],
            'timezone': 'Europe/Copenhagen'
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
            'hour_summary': 'Mostly cloudy for the hour.',
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
            'icon': 'partly-cloudy-night',
            'hour_icon': 'partly-cloudy-night',
            'precipType': 'none',
            'precipProbability': 0,
            'alerts': [],
            'timezone': 'Europe/Copenhagen'
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
            'hour_summary': 'Mostly cloudy for the hour.',
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
            'icon': 'partly-cloudy-night',
            'hour_icon': 'partly-cloudy-night',
            'precipType': 'none',
            'precipProbability': 0,
            'alerts': [],
            'timezone': 'Europe/Copenhagen'
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
            'hour_summary': 'Mostly cloudy for the hour.',
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
            'icon': 'partly-cloudy-night',
            'hour_icon': 'partly-cloudy-night',
            'precipType': 'none',
            'precipProbability': 0,
            'alerts': [],
            'timezone': 'Europe/Copenhagen'
        }

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

    def test_get_normal_condition(self):
        """Testing if normal tweet contains necessary strings"""
        returned = strings.get_normal_condition(self.wd_si)
        self.assertIn(self.wd_si['summary'], returned)
        self.assertIn(self.wd_si['temp_and_unit'], returned)
        self.assertIn(' ' + self.wd_si['hour_summary'], returned)
        self.wd_si['hour_summary'] = None
        returned = strings.get_normal_condition(self.wd_si)
        self.assertIn(self.wd_si['summary'], returned)
        self.assertIn(self.wd_si['temp_and_unit'], returned)
        self.assertNotEqual(returned[-1:], ' ')

    def test_get_alert_text(self):
        """Testing if alert contains necessary strings and converts time"""
        title = 'test alert'
        expires = pytz.utc.localize(datetime.datetime.utcfromtimestamp(1471725505))
        expires_formatted = 'Sat, Aug 20 at 20:38:25 UTC'
        uri = 'https://github.com/BrianMitchL/weatherBot'
        result = strings.get_alert_text(title, expires, uri)
        self.assertIn(title, result)
        self.assertIn(expires_formatted, result)
        self.assertIn(uri, result)

    def test_get_special_condition(self):
        """Testing if normal event is triggered"""
        cond = Condition(type='normal', text='')
        self.assertEqual(cond, strings.get_special_condition(self.wd_si))

    def test_special_wind_chill(self):
        """Testing if wind-chill type is triggered"""
        self.wd_si['apparentTemperature'] = -34
        self.wd_us['apparentTemperature'] = -30
        cond = Condition(type='wind-chill', text='test')
        self.assertEqual(cond.type, strings.get_special_condition(self.wd_si).type)
        self.assertEqual(cond.type, strings.get_special_condition(self.wd_us).type)

    def test_special_precip(self):
        """Testing if precip type is triggered"""
        self.wd_si['precipProbability'] = 0.9
        self.wd_si['precipType'] = 'rain'
        self.wd_si['precipIntensity'] = 10.0
        self.wd_us['precipProbability'] = 0.9
        self.wd_us['precipType'] = 'rain'
        self.wd_us['precipIntensity'] = 1.0
        cond = Condition(type='heavy-rain', text='test')
        self.assertEqual(cond.type, strings.get_special_condition(self.wd_si).type)
        self.assertEqual(cond.type, strings.get_special_condition(self.wd_us).type)
        self.wd_si['precipType'] = 'none'
        cond = Condition(type='normal', text='test')
        self.assertEqual(cond.type, strings.get_special_condition(self.wd_si).type)

    def test_special_medium_wind(self):
        """Testing if medium-wind type is triggered"""
        self.wd_si['icon'] = 'medium-wind'
        cond = Condition(type='medium-wind', text='test')
        self.assertEqual(cond.type, strings.get_special_condition(self.wd_si).type)

    def test_special_heavy_wind(self):
        """Testing if heavy-wind type is triggered"""
        self.wd_si['icon'] = 'heavy-wind'
        cond = Condition(type='heavy-wind', text='test')
        self.assertEqual(cond.type, strings.get_special_condition(self.wd_si).type)
        self.wd_si['icon'] = 'partly-cloudy-night'
        self.wd_si['windSpeed'] = 15.0
        self.wd_ca['windSpeed'] = 56.0
        self.wd_us['windSpeed'] = 35.0
        self.wd_uk2['windSpeed'] = 35.0
        self.assertEqual(cond.type, strings.get_special_condition(self.wd_si).type)
        self.assertEqual(cond.type, strings.get_special_condition(self.wd_ca).type)
        self.assertEqual(cond.type, strings.get_special_condition(self.wd_us).type)
        self.assertEqual(cond.type, strings.get_special_condition(self.wd_uk2).type)

    def test_special_fog(self):
        """Testing if fog type is triggered"""
        self.wd_si['icon'] = 'fog'
        cond = Condition(type='fog', text='test')
        self.assertEqual(cond.type, strings.get_special_condition(self.wd_si).type)

    def test_special_cold(self):
        """Testing if cold type is triggered"""
        cond = Condition(type='cold', text='test')
        self.wd_si['temp'] = -28.0
        self.wd_us['temp'] = -20.0
        self.assertEqual(cond.type, strings.get_special_condition(self.wd_si).type)
        self.assertEqual(cond.type, strings.get_special_condition(self.wd_us).type)

    def test_special_super_hot(self):
        """Testing if super-hot type is triggered"""
        cond = Condition(type='super-hot', text='test')
        self.wd_si['temp'] = 43.0
        self.wd_us['temp'] = 110.0
        self.assertEqual(cond.type, strings.get_special_condition(self.wd_si).type)
        self.assertEqual(cond.type, strings.get_special_condition(self.wd_us).type)

    def test_special_hot(self):
        """Testing if hot type is triggered"""
        cond = Condition(type='hot', text='test')
        self.wd_si['temp'] = 37.0
        self.wd_us['temp'] = 100.0
        self.assertEqual(cond.type, strings.get_special_condition(self.wd_si).type)
        self.assertEqual(cond.type, strings.get_special_condition(self.wd_us).type)

    def test_special_humidity(self):
        """Testing if dry type is triggered"""
        cond = Condition(type='dry', text='test')
        self.wd_si['humidity'] = 10.0
        self.assertEqual(cond.type, strings.get_special_condition(self.wd_si).type)


class TestWB(unittest.TestCase):
    def setUp(self):
        self.location = {'lat': 55.76, 'lng': 12.49, 'name': 'Lyngby-Taarbæk, Hovedstaden'}

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
        self.assertDictEqual(weatherBot.CONFIG, equal)
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
        morris = {'lat': 45.58605, 'lng': -95.91405, 'name': 'Morris, MN'}
        loc = weatherBot.get_location_from_user_timeline('MorrisMNWeather', fallback)
        self.assertTrue(type(loc) is dict)
        self.assertEqual(loc, morris)
        self.assertEqual(weatherBot.get_location_from_user_timeline('twitter', fallback), fallback)

    def test_get_forecast_object(self):
        """Testing getting the forecastio object"""
        forecast = weatherBot.get_forecast_object(self.location['lat'], self.location['lng'], units='us')
        self.assertEqual(forecast.response.status_code, 200)
        self.assertEqual(forecast.json['flags']['units'], 'us')
        bad_forecast = weatherBot.get_forecast_object(345.5, 123.45)
        self.assertEqual(bad_forecast, None)
        alt_forecast = weatherBot.get_forecast_object(self.location['lat'], self.location['lng'], units='si', lang='de')
        self.assertEqual(forecast.response.status_code, 200)
        self.assertEqual(alt_forecast.json['flags']['units'], 'si')

    def test_do_tweet(self):
        """Testing tweeting a test tweet using keys from env variables"""
        tweet_location = False
        variable_location = False
        wd_si = {
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
            'hour_summary': 'Mostly cloudy for the hour.',
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
            'icon': 'partly-cloudy-night',
            'hour_icon': 'partly-cloudy-night',
            'precipType': 'none',
            'precipProbability': 0,
            'alerts': [],
            'timezone': 'Europe/Copenhagen'
        }
        content = 'Just running unit tests, this should disappear... {0}'.format(random.randint(0, 9999))
        tweet_content = content + weatherBot.CONFIG['basic']['hashtag']
        status = weatherBot.do_tweet(content, wd_si, tweet_location, variable_location)
        self.assertEqual(status.text, tweet_content)
        # test destroy
        api = weatherBot.get_tweepy_api()
        deleted = api.destroy_status(id=status.id)
        self.assertEqual(deleted.id, status.id)

    def test_do_tweet_with_location(self):
        """Testing tweeting a test tweet with location using keys from env variables"""
        tweet_location = True
        variable_location = False
        wd_si = {
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
            'hour_summary': 'Mostly cloudy for the hour.',
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
            'icon': 'partly-cloudy-night',
            'hour_icon': 'partly-cloudy-night',
            'precipType': 'none',
            'precipProbability': 0,
            'alerts': [],
            'timezone': 'Europe/Copenhagen'
        }
        content = 'Just running unit tests, this should disappear... {0}'.format(random.randint(0, 9999))
        tweet_content = content + weatherBot.CONFIG['basic']['hashtag']
        status = weatherBot.do_tweet(content, wd_si, tweet_location, variable_location)
        self.assertEqual(status.text, tweet_content)
        # test destroy
        api = weatherBot.get_tweepy_api()
        deleted = api.destroy_status(id=status.id)
        self.assertEqual(deleted.id, status.id)

    def test_do_tweet_with_variable_location(self):
        """Testing tweeting a test tweet with location and variable location using keys from env variables"""
        tweet_location = True
        variable_location = True
        wd_si = {
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
            'hour_summary': 'Mostly cloudy for the hour.',
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
            'icon': 'partly-cloudy-night',
            'hour_icon': 'partly-cloudy-night',
            'precipType': 'none',
            'precipProbability': 0,
            'alerts': [],
            'timezone': 'Europe/Copenhagen'
        }
        content = 'Just running unit tests, this should disappear... {0}'.format(random.randint(0, 9999))
        tweet_content = wd_si['location'] + ': ' + content + weatherBot.CONFIG['basic']['hashtag']
        status = weatherBot.do_tweet(content, wd_si, tweet_location, variable_location)
        self.assertEqual(status.text, tweet_content)
        # test destroy
        api = weatherBot.get_tweepy_api()
        deleted = api.destroy_status(id=status.id)
        self.assertEqual(deleted.id, status.id)

    def test_do_tweet_error(self):
        """Testing tweeting a test tweet that should throw and error using keys from env variables"""
        tweet_location = False
        variable_location = False
        wd_si = {
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
            'hour_summary': 'Mostly cloudy for the hour.',
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
            'icon': 'partly-cloudy-night',
            'hour_icon': 'partly-cloudy-night',
            'precipType': 'none',
            'precipProbability': 0,
            'alerts': [],
            'timezone': 'Europe/Copenhagen'
        }
        content = 'This tweet is over 140 characters.\n' \
                  'This tweet is over 140 characters.\n' \
                  'This tweet is over 140 characters.\n' \
                  'This tweet is over 140 characters.\n' \
                  'This tweet is over 140 characters.\n' \
                  '{0}'.format(random.randint(0, 9999))
        status = weatherBot.do_tweet(content, wd_si, tweet_location, variable_location)
        self.assertEqual(None, status)

if __name__ == '__main__':
    keys.set_twitter_env_vars()
    keys.set_forecastio_env_vars()
    unittest.main()
