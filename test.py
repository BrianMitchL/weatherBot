#!/usr/bin/env python3

"""
weatherBot tests

Copyright 2015-2018 Brian Mitchell under the MIT license
See the GitHub repository: https://github.com/BrianMitchL/weatherBot
"""

import configparser
import datetime
import logging
import os
import pickle
import sys
import unittest

import forecastio
import pytz
import tweepy
import yaml
from testfixtures import LogCapture
from testfixtures import replace

import keys
import models
import utils
import weatherBot
from test_helpers import mocked_forecastio_load_forecast
from test_helpers import mocked_forecastio_load_forecast_error
from test_helpers import mocked_get_tweepy_api
from test_helpers import mocked_tweepy_o_auth_handler
from test_helpers import mocked_requests_get


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

    def test_localize_utc_datetime(self):
        """Testing localizing a plain datetime object to a pytz timezone aware object"""
        dt = datetime.datetime.fromtimestamp(1461731335)  # datetime.datetime(2016, 4, 26, 23, 28, 55)
        timezone_id = 'Europe/Copenhagen'
        localized_dt = utils.localize_utc_datetime(timezone_id, dt)
        correct_dt = datetime.datetime.fromtimestamp(1461738535)  # datetime.datetime(2016, 4, 27, 1, 28, 55)
        self.assertEqual(localized_dt, pytz.timezone('Europe/Copenhagen').localize(correct_dt))

    def test_datetime_to_utc(self):
        """Testing localize a normal datetime object to timezone id, then convert to UTC"""
        dt = datetime.datetime.fromtimestamp(1461738535)  # datetime.datetime(2016, 4, 27, 1, 28, 55)
        timezone_id = 'Europe/Copenhagen'
        utc_dt = utils.datetime_to_utc(timezone_id, dt)
        correct_dt = pytz.timezone('Europe/Copenhagen').localize(dt).astimezone(pytz.utc)
        self.assertEqual(utc_dt, correct_dt)

    def test_parse_time_string(self):
        """Testing parsing string representing time to a Time namedtuple"""
        self.assertEqual(utils.parse_time_string('7:00'), utils.Time(hour=7, minute=0))
        self.assertEqual(utils.parse_time_string('0:0'), utils.Time(hour=0, minute=0))
        self.assertEqual(utils.parse_time_string('000000001:00000'), utils.Time(hour=1, minute=0))
        self.assertEqual(utils.parse_time_string('18:00000001'), utils.Time(hour=18, minute=1))
        self.assertEqual(utils.parse_time_string('22:59'), utils.Time(hour=22, minute=59))
        self.assertEqual(utils.parse_time_string('1:45'), utils.Time(hour=1, minute=45))
        self.assertEqual(utils.parse_time_string('0000002:000003'), utils.Time(hour=2, minute=3))
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
        list_simple = [utils.Time(hour=7, minute=0),
                       utils.Time(hour=12, minute=0),
                       utils.Time(hour=15, minute=0),
                       utils.Time(hour=18, minute=0),
                       utils.Time(hour=22, minute=0)]
        list_complex = [utils.Time(hour=0, minute=0),
                        utils.Time(hour=0, minute=0),
                        utils.Time(hour=1, minute=0),
                        utils.Time(hour=1, minute=0),
                        utils.Time(hour=1, minute=1),
                        utils.Time(hour=1, minute=2),
                        utils.Time(hour=1, minute=45),
                        utils.Time(hour=11, minute=32),
                        utils.Time(hour=18, minute=1),
                        utils.Time(hour=22, minute=59),
                        utils.Time(hour=23, minute=0),
                        utils.Time(hour=23, minute=59)]
        self.assertEqual(utils.get_times(raw_simple), list_simple)
        self.assertEqual(utils.get_times(raw_complex), list_complex)


class WeatherLocation(unittest.TestCase):
    def setUp(self):
        self.lat = 55.76
        self.lng = 12.49
        self.name = 'Lyngby-Taarbæk, Hovedstaden'
        self.location = models.WeatherLocation(self.lat, self.lng, self.name)

    def test_location(self):
        """Testing that locations are loaded correctly"""
        self.assertEqual(self.location.lat, self.lat)
        self.assertEqual(self.location.lng, self.lng)
        self.assertEqual(self.location.name, self.name)

    def test_str(self):
        """Testing that stringifying the object works correctly"""
        self.assertEqual('<WeatherLocation: Lyngby-Taarbæk, Hovedstaden at 55.76,12.49>', str(self.location))

    def test_repr(self):
        """Testing that __repr__ returns the __str__ representation of the object"""
        self.assertEqual('<WeatherLocation: Lyngby-Taarbæk, Hovedstaden at 55.76,12.49>', repr(self.location))

    def test_equality(self):
        """Testing equality comparisons"""
        location_same = models.WeatherLocation(self.lat, self.lng, self.name)
        self.assertEqual(self.location, location_same)
        location2 = models.WeatherLocation(20, 16, 'testing')
        self.assertNotEqual(self.location, location2)


class WeatherBotAlert(unittest.TestCase):
    @replace('requests.get', mocked_requests_get)
    def test_init(self, mock_get):
        """Test that a WeatherAlert is loaded correctly"""
        forecast = forecastio.manual(os.path.join('fixtures', 'us_alert.json'))
        alert = models.WeatherAlert(forecast.alerts()[0])
        self.assertEqual('Wind Advisory', alert.title)
        self.assertEqual(pytz.utc.localize(datetime.datetime(2016, 10, 18, 4, 4)), alert.time)
        self.assertEqual(pytz.utc.localize(datetime.datetime(2016, 10, 20, 19, 0)), alert.expires)
        self.assertEqual('https://alerts.weather.gov/cap/wwacapget.php?x=CA12561A519050.WindAdvisory.'
                         '12561A725D30CA.LOXNPWLOX.9240bcf720aae1b01b10f53f012e61bb', alert.uri)
        self.assertEqual('a6bf597275fdf063c76a42b05c3c81ed093701b2344c3c98cfde36875f7a4c3d', alert.sha())
        self.assertEqual('<WeatherAlert: Wind Advisory at 2016-10-18 04:04:00+00:00>', str(alert))

    @replace('requests.get', mocked_requests_get)
    def test_no_expires(self):
        """Test that a WeatherAlert is loaded correctly"""
        forecast = forecastio.manual(os.path.join('fixtures', 'ca_alert.json'))
        alert = models.WeatherAlert(forecast.alerts()[0])
        self.assertEqual('Snowfall Warning', alert.title)
        self.assertEqual(pytz.utc.localize(datetime.datetime(2017, 2, 4, 17, 11)), alert.time)
        self.assertEqual('https://weather.gc.ca/warnings/report_e.html?ab6', alert.uri)
        self.assertEqual('warning', alert.severity)
        self.assertEqual('d5c1870d583f95441a41d452355173bad49f60f87c2962f195bd7873f0997d4b', alert.sha())
        self.assertEqual('<WeatherAlert: Snowfall Warning at 2017-02-04 17:11:00+00:00>', str(alert))

    @replace('requests.get', mocked_requests_get)
    def test_expired(self):
        """Test that an alert is expired or active"""
        forecast = forecastio.manual(os.path.join('fixtures', 'us_alert.json'))
        alert = models.WeatherAlert(forecast.alerts()[0])
        self.assertTrue(alert.expired(pytz.utc.localize(datetime.datetime(2017, 10, 18, 4, 4))))
        self.assertFalse(alert.expired(pytz.utc.localize(datetime.datetime(2016, 10, 18, 4, 4))))
        self.assertFalse(alert.expired(pytz.utc.localize(datetime.datetime(2015, 10, 18, 4, 4))))

        forecast = forecastio.manual(os.path.join('fixtures', 'ca_alert.json'))
        alert = models.WeatherAlert(forecast.alerts()[0])
        self.assertTrue(alert.expired(pytz.utc.localize(datetime.datetime(2017, 2, 7, 17, 12))))
        self.assertFalse(alert.expired(pytz.utc.localize(datetime.datetime(2017, 2, 7, 17, 11))))
        self.assertFalse(alert.expired(pytz.utc.localize(datetime.datetime(2017, 2, 3, 17, 11))))


class WeatherBotData(unittest.TestCase):
    def setUp(self):
        with open('strings.yml', 'r') as file_stream:
            self.weatherbot_strings = yaml.safe_load(file_stream)
        self.location = models.WeatherLocation(55.76, 12.49, 'Lyngby-Taarbæk, Hovedstaden')

    @replace('requests.get', mocked_requests_get)
    def test_init(self):
        """Testing that weather data is loaded correctly"""
        forecast = forecastio.manual(os.path.join('fixtures', 'us.json'))
        wd = models.WeatherData(forecast, self.location)
        self.assertEqual(wd.units, utils.get_units('us'))
        self.assertEqual(wd.windBearing, 'SW')
        self.assertEqual(wd.windSpeed, 10.81)
        self.assertEqual(wd.apparentTemperature, 50.84)
        self.assertEqual(wd.temp, 50.84)
        self.assertEqual(wd.humidity, 89)
        self.assertEqual(wd.precipIntensity, 0)
        self.assertEqual(wd.precipProbability, 0)
        self.assertEqual(wd.precipType, 'none')
        self.assertEqual(wd.summary, 'Partly Cloudy')
        self.assertEqual(wd.icon, 'partly-cloudy-day')
        self.assertEqual(wd.location, self.location)
        self.assertEqual(wd.timezone, 'Europe/Copenhagen')
        self.assertEqual(wd.alerts, [])
        self.assertTrue(wd.valid)
        self.assertEqual(str(wd),
                         '<WeatherData: Lyngby-Taarbæk, Hovedstaden(55.76,12.49) at 2016-10-01 05:56:38+00:00>')

    @replace('requests.get', mocked_requests_get)
    def test_alerts(self):
        """Testing that alerts are loaded correctly into a list"""
        location = models.WeatherLocation(34.2, -118.36, 'Los Angeles, CA')
        forecast = forecastio.manual(os.path.join('fixtures', 'us_alert.json'))
        wd = models.WeatherData(forecast, location)
        self.assertEqual(wd.alerts[0].title, 'Wind Advisory')
        self.assertEqual(wd.alerts[1].title, 'Beach Hazards Statement')
        self.assertEqual(wd.alerts[2].title, 'Red Flag Warning')

    @replace('requests.get', mocked_requests_get)
    def test_bad_data(self):
        """Testing that bad data will gracefully fail"""
        forecast = forecastio.manual(os.path.join('fixtures', 'bad_data_unavailable.json'))
        wd = models.WeatherData(forecast, self.location)
        self.assertFalse(wd.valid)
        forecast = forecastio.manual(os.path.join('fixtures', 'bad_data_temperature.json'))
        wd = models.WeatherData(forecast, self.location)
        self.assertFalse(wd.valid)
        forecast = forecastio.manual(os.path.join('fixtures', 'bad_data_summary.json'))
        wd = models.WeatherData(forecast, self.location)
        self.assertFalse(wd.valid)

    @replace('requests.get', mocked_requests_get)
    def test_optional_fields(self):
        """Testing that bad data will gracefully fail"""
        forecast = forecastio.manual(os.path.join('fixtures', 'optional_fields.json'))
        wd = models.WeatherData(forecast, self.location)
        self.assertEqual(wd.precipType, 'rain')
        self.assertEqual(wd.windBearing, 'unknown direction')

    @replace('requests.get', mocked_requests_get)
    def test_json(self):
        """Testing that json() returns a dict containing the response from the Dark Sky API"""
        forecast = forecastio.manual(os.path.join('fixtures', 'us.json'))
        wd = models.WeatherData(forecast, self.location)
        self.assertEqual(wd.json(), forecast.json)


class WeatherBotString(unittest.TestCase):
    def setUp(self):
        with open('strings.yml', 'r') as file_stream:
            self.weatherbot_strings = yaml.safe_load(file_stream)
        self.location = models.WeatherLocation(55.76, 12.49, 'Lyngby-Taarbæk, Hovedstaden')

    @replace('requests.get', mocked_requests_get)
    def test_forecast(self):
        """Testing that forecasts are formatted correctly"""
        forecast = forecastio.manual(os.path.join('fixtures', 'us.json'))
        wd = models.WeatherData(forecast, self.location)
        self.weatherbot_strings['forecast_endings'] = []
        wbs = models.WeatherBotString(self.weatherbot_strings)
        wbs.set_weather(wd)
        forecast_string = wbs.forecast()
        self.assertIn(forecast_string, wbs.forecasts)
        self.weatherbot_strings['forecast_endings'] = ['Test ending!']
        self.weatherbot_strings['forecasts'] = ['The forecast for today is {summary_lower} {high}/{low}.']
        wbs = models.WeatherBotString(self.weatherbot_strings)
        wbs.set_weather(wd)
        forecast_string = wbs.forecast()
        self.assertEqual(forecast_string,
                         'The forecast for today is mostly cloudy throughout the day. 66ºF/50ºF. Test ending!')

    @replace('requests.get', mocked_requests_get)
    def test_normal(self):
        """Testing that normal events are formatted"""
        forecast = forecastio.manual(os.path.join('fixtures', 'us.json'))
        wd = models.WeatherData(forecast, self.location)
        wbs = models.WeatherBotString(self.weatherbot_strings)
        wbs.set_weather(wd)
        normal_string = wbs.normal()
        self.assertIn(normal_string, wbs.normal_conditions)

    @replace('requests.get', mocked_requests_get)
    def test_special(self):
        """Testing if special events are triggered"""
        forecast_si = forecastio.manual(os.path.join('fixtures', 'si.json'))
        forecast_us = forecastio.manual(os.path.join('fixtures', 'us.json'))
        forecast_ca = forecastio.manual(os.path.join('fixtures', 'ca.json'))
        forecast_uk2 = forecastio.manual(os.path.join('fixtures', 'uk2.json'))
        wd = models.WeatherData(forecast_si, self.location)
        wbs = models.WeatherBotString(self.weatherbot_strings)
        wbs.set_weather(wd)
        self.assertEqual('normal', wbs.special().type)
        self.assertEqual('', wbs.special().text)
        """Testing if wind-chill type is triggered"""
        wd = models.WeatherData(forecast_si, self.location)
        wd.apparentTemperature = -34
        wbs = models.WeatherBotString(self.weatherbot_strings)
        wbs.set_weather(wd)
        self.assertEqual('wind-chill', wbs.special().type)
        self.assertIn(wbs.special().text, wbs.special_conditions[wbs.special().type])
        wd = models.WeatherData(forecast_us, self.location)
        wd.apparentTemperature = -30
        wbs = models.WeatherBotString(self.weatherbot_strings)
        wbs.set_weather(wd)
        self.assertEqual('wind-chill', wbs.special().type)
        self.assertIn(wbs.special().text, wbs.special_conditions[wbs.special().type])
        """Testing if precip type is triggered"""
        wd = models.WeatherData(forecast_si, self.location)
        wd.precipProbability = 0.9
        wd.precipType = 'rain'
        wd.precipIntensity = 10.0
        wbs.set_weather(wd)
        self.assertEqual('heavy-rain', wbs.special().type)
        self.assertIn(wbs.special().text, wbs.precipitations['rain']['heavy'])
        wd = models.WeatherData(forecast_us, self.location)
        wd.precipProbability = 0.9
        wd.precipType = 'rain'
        wd.precipIntensity = 1.0
        wbs.set_weather(wd)
        self.assertEqual('heavy-rain', wbs.special().type)
        self.assertIn(wbs.special().text, wbs.precipitations['rain']['heavy'])
        wd = models.WeatherData(forecast_us, self.location)
        wd.precipProbability = 0.9
        wd.precipType = 'none'
        wd.precipIntensity = 1.0
        wbs.set_weather(wd)
        self.assertEqual('normal', wbs.special().type)
        self.assertEqual('', wbs.special().text)
        """Testing if medium-wind type is triggered"""
        wd = models.WeatherData(forecast_si, self.location)
        wd.icon = 'medium-wind'
        wbs.set_weather(wd)
        self.assertEqual('medium-wind', wbs.special().type)
        """Testing if heavy-wind type is triggered"""
        wd = models.WeatherData(forecast_si, self.location)
        wd.icon = 'heavy-wind'
        wbs.set_weather(wd)
        self.assertEqual('heavy-wind', wbs.special().type)
        wd = models.WeatherData(forecast_si, self.location)
        wd.windSpeed = 15.0
        wbs.set_weather(wd)
        self.assertEqual('heavy-wind', wbs.special().type)
        wd = models.WeatherData(forecast_ca, self.location)
        wd.windSpeed = 56.0
        wbs.set_weather(wd)
        self.assertEqual('heavy-wind', wbs.special().type)
        wd = models.WeatherData(forecast_us, self.location)
        wd.windSpeed = 35.0
        wbs.set_weather(wd)
        self.assertEqual('heavy-wind', wbs.special().type)
        wd = models.WeatherData(forecast_uk2, self.location)
        wd.windSpeed = 35.0
        wbs.set_weather(wd)
        self.assertEqual('heavy-wind', wbs.special().type)
        """Testing if fog type is triggered"""
        wd = models.WeatherData(forecast_si, self.location)
        wd.icon = 'fog'
        wbs.set_weather(wd)
        self.assertEqual('fog', wbs.special().type)
        """Testing if cold type is triggered"""
        wd = models.WeatherData(forecast_si, self.location)
        wd.temp = -28.0
        wbs.set_weather(wd)
        self.assertEqual('cold', wbs.special().type)
        wd = models.WeatherData(forecast_us, self.location)
        wd.temp = -20.0
        wbs.set_weather(wd)
        self.assertEqual('cold', wbs.special().type)
        """Testing if super-hot type is triggered"""
        wd = models.WeatherData(forecast_si, self.location)
        wd.temp = 43.0
        wbs.set_weather(wd)
        self.assertEqual('super-hot', wbs.special().type)
        wd = models.WeatherData(forecast_us, self.location)
        wd.temp = 110.0
        wbs.set_weather(wd)
        self.assertEqual('super-hot', wbs.special().type)
        """Testing if hot type is triggered"""
        wd = models.WeatherData(forecast_si, self.location)
        wd.temp = 37.0
        wbs.set_weather(wd)
        self.assertEqual('hot', wbs.special().type)
        wd = models.WeatherData(forecast_us, self.location)
        wd.temp = 100.0
        wbs.set_weather(wd)
        self.assertEqual('hot', wbs.special().type)
        """Testing if dry type is triggered"""
        wd = models.WeatherData(forecast_si, self.location)
        wd.humidity = 25.0
        wbs.set_weather(wd)
        self.assertEqual('dry', wbs.special().type)

    @replace('requests.get', mocked_requests_get)
    def test_alert(self):
        """Testing that alerts are formatted"""
        wbs = models.WeatherBotString(self.weatherbot_strings)
        forecast = forecastio.manual(os.path.join('fixtures', 'ca_alert.json'))
        location = models.WeatherLocation(50.564167, -111.898889, 'Brooks, Alberta')
        wd = models.WeatherData(forecast, location)
        wbs.set_weather(wd)
        alert = wbs.alert(wd.alerts[0], wd.timezone)
        self.assertIn('Snowfall Warning', alert)
        self.assertIn('https://weather.gc.ca/warnings/report_e.html?ab6', alert)

    @replace('requests.get', mocked_requests_get)
    def test_precipitation(self):
        """Testing that precipitation conditions are met"""
        wbs = models.WeatherBotString(self.weatherbot_strings)
        forecast_us = forecastio.manual(os.path.join('fixtures', 'us.json'))
        wd = models.WeatherData(forecast_us, self.location)
        wbs.set_weather(wd)
        self.assertEqual(wbs.precipitation(), models.Condition(type='none', text=''))
        wd.precipIntensity = 0.3
        wd.precipProbability = 0.5
        wd.precipType = 'rain'
        wbs.set_weather(wd)
        self.assertEqual(wbs.precipitation(), models.Condition(type='none', text=''))
        wd.precipIntensity = 0.3
        wd.precipProbability = 1
        wd.precipType = 'none'
        wbs.set_weather(wd)
        self.assertEqual(wbs.precipitation(), models.Condition(type='none', text=''))
        wd.precipIntensity = 0
        wd.precipProbability = 1
        wd.precipType = 'rain'
        wbs.set_weather(wd)
        self.assertEqual(wbs.precipitation(), models.Condition(type='none', text=''))
        wd.precipIntensity = 0
        wd.precipProbability = 1
        wd.precipType = 'none'
        wbs.set_weather(wd)
        self.assertEqual(wbs.precipitation(), models.Condition(type='none', text=''))
        # testing with a few possible conditions
        wd.precipIntensity = 0.3
        wd.precipProbability = 1
        wd.precipType = 'rain'
        wbs.set_weather(wd)
        precip = wbs.precipitation()
        self.assertEqual(precip.type, 'moderate-rain')
        self.assertIn(precip.text, wbs.precipitations['rain']['moderate'])
        wd.precipIntensity = 0.4
        wd.precipProbability = 0.85
        wd.precipType = 'snow'
        wbs.set_weather(wd)
        precip = wbs.precipitation()
        self.assertEqual(precip.type, 'heavy-snow')
        self.assertIn(precip.text, wbs.precipitations['snow']['heavy'])
        wd.precipIntensity = 0.06
        wd.precipProbability = 1
        wd.precipType = 'sleet'
        wbs.set_weather(wd)
        precip = wbs.precipitation()
        self.assertEqual(precip.type, 'light-sleet')
        self.assertIn(precip.text, wbs.precipitations['sleet']['light'])
        wd.precipIntensity = 0.005
        wd.precipProbability = 1
        wd.precipType = 'rain'
        wbs.set_weather(wd)
        precip = wbs.precipitation()
        self.assertEqual(precip.type, 'very-light-rain')
        self.assertIn(precip.text, wbs.precipitations['rain']['very-light'])

    @replace('requests.get', mocked_requests_get)
    def test_update_weather_data(self):
        """Testing that new weather data is loaded correctly"""
        forecast1 = forecastio.manual(os.path.join('fixtures', 'us.json'))
        wd1 = models.WeatherData(forecast1, self.location)
        forecast2 = forecastio.manual(os.path.join('fixtures', 'us_cincinnati.json'))
        wd2 = models.WeatherData(forecast2, self.location)
        wbs = models.WeatherBotString(self.weatherbot_strings)
        wbs.set_weather(wd1)
        self.assertEqual(50.84, wbs.weather_data.apparentTemperature)
        self.assertIn('51', wbs.normal())
        self.assertIn('66ºF', wbs.forecast())
        self.assertEqual('normal', wbs.special().type)
        self.assertEqual(0, len(wd1.alerts))
        wbs.set_weather(wd2)
        self.assertEqual(73.09, wbs.weather_data.apparentTemperature)
        self.assertIn('73', wbs.normal())
        self.assertIn('78ºF', wbs.forecast())
        self.assertEqual('moderate-rain', wbs.special().type)
        alert = wbs.alert(wd2.alerts[0], wd2.timezone)
        self.assertIn('Severe Thunderstorm Warning', alert)
        self.assertIn('Wed, Oct 19 at 19:30:00 EDT', alert)
        self.assertIn('https://alerts.weather.gov/cap/wwacapget.php?x=OH12561A63BE38.SevereThunderstormWarning.'
                      '12561A63C2E8OH.ILNSVSILN.f17bc0b3ead1db18bf60532894d9925e', alert)

    @replace('requests.get', mocked_requests_get)
    def test_dict(self):
        """Testing that __dict__ returns the correct data"""
        forecast = forecastio.manual(os.path.join('fixtures', 'us.json'))
        wd = models.WeatherData(forecast, self.location)
        wbs = models.WeatherBotString(self.weatherbot_strings)
        wbs.set_weather(wd)
        self.assertEqual({
            'language': wbs.language,
            'weather_data': wbs.weather_data,
            'forecasts': wbs.forecasts,
            'forecast_endings': wbs.forecasts_endings,
            'normal_conditions': wbs.normal_conditions,
            'special_conditions': wbs.special_conditions,
            'precipitations': wbs.precipitations
        }, wbs.__dict__())


class TestWB(unittest.TestCase):
    def setUp(self):
        self.location = models.WeatherLocation(55.76, 12.49, 'Lyngby-Taarbæk, Hovedstaden')

    def test_config(self):
        """Testing config file handling"""
        equal = {
            'basic': {
                'dm_errors': False,
                'units': 'si',
                'tweet_location': False,
                'hashtag': '',
                'refresh': 300,
                'strings': 'fake_path.yml'
            },
            'scheduled_times': {
                'forecast': utils.Time(hour=6, minute=0),
                'conditions': [utils.Time(hour=7, minute=0),
                               utils.Time(hour=12, minute=0),
                               utils.Time(hour=15, minute=0),
                               utils.Time(hour=18, minute=0),
                               utils.Time(hour=22, minute=0)]
            },
            'default_location': models.WeatherLocation(-79.0, 12.0, 'Just a Test'),
            'variable_location': {
                'enabled': True,
                'user': 'test_user',
                'unnamed_location_name': 'Somewhere in deep space'
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
            'refresh': '300',
            'strings': 'fake_path.yml'
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
            'user': 'test_user',
            'unnamed_location_name': 'Somewhere in deep space'
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
        weatherBot.load_config(os.path.abspath('weatherBotTest.conf'))
        self.assertDictEqual(weatherBot.CONFIG, equal)
        os.remove(os.path.abspath('weatherBotTest.conf'))

    def test_logging(self):
        """Testing if the system version is in the log and log file"""
        with LogCapture() as l:
            logger = logging.getLogger()
            logger.info('info')
            weatherBot.initialize_logger(True, os.path.abspath('weatherBotTest.log'))
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
        os.remove(os.path.abspath('weatherBotTest.log'))

    @replace('tweepy.OAuthHandler', mocked_tweepy_o_auth_handler)
    def test_get_tweepy_api(self):
        """Testing getting a tweepy API object"""
        api = weatherBot.get_tweepy_api()
        self.assertTrue(type(api) is tweepy.API)

    @replace('forecastio.load_forecast', mocked_forecastio_load_forecast)
    def test_get_forecast_object(self):
        """Testing getting the forecastio object"""
        forecast = weatherBot.get_forecast_object(self.location.lat, self.location.lng, units='us', lang='de')
        self.assertEqual(forecast.response.status_code, 200)
        self.assertEqual(forecast.json['flags']['units'], 'us')

    @replace('forecastio.load_forecast', mocked_forecastio_load_forecast_error)
    def test_get_forecast_object_error(self):
        """Testing getting the forecastio object"""
        bad_forecast = weatherBot.get_forecast_object(45.5, 123.45)
        self.assertEqual(bad_forecast, None)

    @replace('weatherBot.get_tweepy_api', mocked_get_tweepy_api)
    def test_get_location_from_user_timeline_coordinates(self):
        """Testing getting a location from twitter account's recent tweets using the coordinates property"""
        fallback_loc = models.WeatherLocation(4, 3, 'test')
        test_loc = models.WeatherLocation(2, 1, 'test')
        loc = weatherBot.get_location_from_user_timeline('MorrisMNWeather', fallback_loc)
        self.assertTrue(type(loc) is models.WeatherLocation)
        self.assertEqual(loc, test_loc)

    @replace('weatherBot.get_tweepy_api', mocked_get_tweepy_api)
    def test_get_location_from_user_timeline_coordinates_no_place_full_name(self):
        """Testing getting a location from twitter account's recent tweets using the coordinates property
         when a place does not exist for that location"""
        fallback_loc = models.WeatherLocation(4, 3, 'test')
        test_loc = models.WeatherLocation(2.5, 1.5, 'unnamed location')
        weatherBot.CONFIG['variable_location']['unnamed_location_name'] = 'unnamed location'
        loc = weatherBot.get_location_from_user_timeline('coordsnoplace', fallback_loc)
        self.assertTrue(type(loc) is models.WeatherLocation)
        self.assertEqual(loc, test_loc)

    @replace('weatherBot.get_tweepy_api', mocked_get_tweepy_api)
    def test_get_location_from_user_timeline_place(self):
        """Testing getting a location from twitter account's recent tweets using the place bounding box"""
        fallback_loc = models.WeatherLocation(4, 3, 'test')
        test_loc = models.WeatherLocation(5.0, 4.0, 'cool place')
        loc = weatherBot.get_location_from_user_timeline('nocoords', fallback_loc)
        self.assertTrue(type(loc) is models.WeatherLocation)
        self.assertEqual(loc, test_loc)

    @replace('weatherBot.get_tweepy_api', mocked_get_tweepy_api)
    def test_get_location_from_user_timeline_empty(self):
        """Testing getting a location from twitter account's recent tweets when there are none"""
        fallback_loc = models.WeatherLocation(4, 3, 'test')
        self.assertEqual(weatherBot.get_location_from_user_timeline('no tweets', fallback_loc), fallback_loc)

    @replace('weatherBot.get_tweepy_api', mocked_get_tweepy_api)
    def test_get_location_from_user_timeline_error(self):
        """Testing getting a location from twitter account's recent tweets when there is an error"""
        fallback_loc = models.WeatherLocation(4, 3, 'test')
        self.assertEqual(weatherBot.get_location_from_user_timeline('error', fallback_loc), fallback_loc)

    @replace('weatherBot.get_tweepy_api', mocked_get_tweepy_api)
    def test_do_tweet(self):
        """Testing tweeting a test tweet"""
        tweet_location = False
        variable_location = False
        content = 'Just running unit tests, this should disappear...'
        hashtag = '#testing'
        tweet_content = content + ' ' + hashtag
        status = weatherBot.do_tweet(content, self.location, tweet_location, variable_location, hashtag=hashtag)
        self.assertEqual(status.text, tweet_content)

    @replace('weatherBot.get_tweepy_api', mocked_get_tweepy_api)
    def test_do_tweet_long(self):
        """Testing tweeting a test tweet that is over 280 characters"""
        tweet_location = False
        variable_location = False
        content = 'This tweet is over 280 characters.\n' \
                  'This tweet is over 280 characters.\n' \
                  'This tweet is over 280 characters.\n' \
                  'This tweet is over 280 characters.\n' \
                  'This tweet is over 280 characters.\n' \
                  'This tweet is over 280 characters.\n' \
                  'This tweet is over 280 characters.\n' \
                  'This tweet is over 280 characters.\n' \
                  'This tweet is over 280 characters.\n' \
                  'This tweet is over 280 characters.'
        hashtag = '#testing'
        status = weatherBot.do_tweet(content, self.location, tweet_location, variable_location, hashtag=hashtag)
        expected_text = 'This tweet is over 280 characters. ' \
                        'This tweet is over 280 characters. ' \
                        'This tweet is over 280 characters. ' \
                        'This tweet is over 280 characters. ' \
                        'This tweet is over 280 characters. ' \
                        'This tweet is over 280 characters. ' \
                        'This tweet is over 280 characters. ' \
                        'This tweet is over 280… #testing'

        self.assertEqual(status.text, expected_text)

    @replace('weatherBot.get_tweepy_api', mocked_get_tweepy_api)
    def test_do_tweet_with_locations(self):
        """Testing tweeting a test tweet with location and variable location"""
        tweet_location = True
        variable_location = True
        content = 'Just running unit tests, this should disappear...'
        weatherBot.CONFIG['basic']['hashtag'] = ''
        tweet_content = self.location.name + ': ' + content
        status = weatherBot.do_tweet(content, self.location, tweet_location, variable_location)
        self.assertEqual(status.text, tweet_content)

    @replace('weatherBot.get_tweepy_api', mocked_get_tweepy_api)
    def test_do_tweet_error(self):
        """Testing tweeting a test tweet that should throw and error using keys from env variables"""
        tweet_location = False
        variable_location = False
        content = 'error'
        status = weatherBot.do_tweet(content, self.location, tweet_location, variable_location)
        self.assertEqual(None, status)

    def test_cleanse_throttles(self):
        """Testing that an expired, non-default key will be removed from a dict"""
        now = pytz.utc.localize(datetime.datetime(2016, 10, 14, hour=14, minute=42)).astimezone(pytz.utc)
        base = {'default': now - datetime.timedelta(hours=2)}
        a = base
        a['snow-light'] = now + datetime.timedelta(minutes=20)
        self.assertDictEqual(a, weatherBot.cleanse_throttles(a, now))
        b = base
        b['dummy'] = now - datetime.timedelta(hours=3)
        self.assertDictEqual(base, weatherBot.cleanse_throttles(b, now))
        self.assertDictEqual({}, weatherBot.cleanse_throttles({}, now))

    def test_set_cache(self):
        """Testing that set_cache properly saves a dict"""
        a = {'test': 123, 'more testing': 'look, a string!'}
        weatherBot.set_cache(a, file='testsetcache.p')
        with open('testsetcache.p', 'rb') as handle:
            self.assertEqual(pickle.load(handle), a)
            os.remove('testsetcache.p')

    def test_get_cache(self):
        """Testing that get_cache properly gets a cache,
        or returns the weatherBot.cache global variable if no cahe file exists"""
        a = {'test': 123, 'more testing': 'look, a string!'}
        self.assertEqual(weatherBot.get_cache('testgetcache.p'), weatherBot.CACHE)
        with open('testgetcache.p', 'wb') as handle:
            pickle.dump(a, handle)
        self.assertEqual(weatherBot.get_cache('testgetcache.p'), a)
        os.remove('testgetcache.p')


class TestKeys(unittest.TestCase):
    def setUp(self):
        self.WEATHERBOT_CONSUMER_KEY = os.environ['WEATHERBOT_CONSUMER_KEY']
        self.WEATHERBOT_CONSUMER_SECRET = os.environ['WEATHERBOT_CONSUMER_SECRET']
        self.WEATHERBOT_ACCESS_TOKEN = os.environ['WEATHERBOT_ACCESS_TOKEN']
        self.WEATHERBOT_ACCESS_TOKEN_SECRET = os.environ['WEATHERBOT_ACCESS_TOKEN_SECRET']
        self.WEATHERBOT_DARKSKY_KEY = os.environ['WEATHERBOT_DARKSKY_KEY']

    def tearDown(self):
        os.environ['WEATHERBOT_CONSUMER_KEY'] = self.WEATHERBOT_CONSUMER_KEY
        os.environ['WEATHERBOT_CONSUMER_SECRET'] = self.WEATHERBOT_CONSUMER_SECRET
        os.environ['WEATHERBOT_ACCESS_TOKEN'] = self.WEATHERBOT_ACCESS_TOKEN
        os.environ['WEATHERBOT_ACCESS_TOKEN_SECRET'] = self.WEATHERBOT_ACCESS_TOKEN_SECRET
        os.environ['WEATHERBOT_DARKSKY_KEY'] = self.WEATHERBOT_DARKSKY_KEY

    def test_set_twitter_env_vars(self):
        """Test that Twitter environmental variables are set to values in keys.py"""
        keys.set_twitter_env_vars()
        self.assertIsNotNone(os.environ['WEATHERBOT_CONSUMER_KEY'])
        self.assertIsNotNone(os.environ['WEATHERBOT_CONSUMER_SECRET'])
        self.assertIsNotNone(os.environ['WEATHERBOT_ACCESS_TOKEN'])
        self.assertIsNotNone(os.environ['WEATHERBOT_ACCESS_TOKEN_SECRET'])
        del os.environ['WEATHERBOT_CONSUMER_KEY']
        del os.environ['WEATHERBOT_CONSUMER_SECRET']
        del os.environ['WEATHERBOT_ACCESS_TOKEN']
        del os.environ['WEATHERBOT_ACCESS_TOKEN_SECRET']
        keys.set_twitter_env_vars()
        self.assertEqual(os.getenv('WEATHERBOT_CONSUMER_KEY'), 'xxx')
        self.assertEqual(os.getenv('WEATHERBOT_CONSUMER_SECRET'), 'xxx')
        self.assertEqual(os.getenv('WEATHERBOT_ACCESS_TOKEN'), 'xxx')
        self.assertEqual(os.getenv('WEATHERBOT_ACCESS_TOKEN_SECRET'), 'xxx')

    def test_set_darksky_env_vars(self):
        """Test that the Dark Sky environmental variable is set to value in keys.py"""
        keys.set_darksky_env_vars()
        self.assertIsNotNone(os.environ['WEATHERBOT_DARKSKY_KEY'])
        del os.environ['WEATHERBOT_DARKSKY_KEY']
        keys.set_darksky_env_vars()
        self.assertEqual(os.getenv('WEATHERBOT_DARKSKY_KEY'), 'xxx')


if __name__ == '__main__':
    keys.set_twitter_env_vars()
    keys.set_darksky_env_vars()
    unittest.main()
