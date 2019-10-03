#!/usr/bin/env python3

"""
weatherBot

Copyright 2015-2019 Brian Mitchell under the MIT license
See the GitHub repository: https://github.com/BrianMitchL/weatherBot
"""
# pylint: disable=global-statement,invalid-name
# invalid-name is to mute the 'weatherBot' module name from erring, unfortunately this has to be done file-wide
import argparse
import configparser
import logging
import os
import pickle
import sys
import textwrap
import time
import traceback
from datetime import datetime
from datetime import timedelta

import forecastio
import pytz
import requests.exceptions
import tweepy
import yaml

import keys
import models
import utils

# Global variables
CACHE = {'throttles': {}}
CONFIG = {}


def load_config(path):
    """
    Load the configuration file from path and set defaults if not given.
    The configuration is set to the CONFIG global variable.
    :type path: str
    :param path: path to the conf file
    """
    global CONFIG
    conf = configparser.ConfigParser()
    conf.read(path)
    CONFIG = {
        'basic': {
            'dm_errors': conf['basic'].getboolean('dm_errors', True),
            'units': conf['basic'].get('units', 'us'),
            'tweet_location': conf['basic'].getboolean('tweet_location', True),
            'hashtag': conf['basic'].get('hashtag', '#MorrisWeather'),
            'refresh': conf['basic'].getint('refresh', 3),
            'strings': conf['basic'].get('strings', 'strings.yml')
        },
        'scheduled_times': {
            'forecast': utils.parse_time_string(conf['scheduled times'].get('forecast', '6:00')),
            'conditions': utils.get_times(conf['scheduled times'].get('conditions',
                                                                      '7:00\n12:00\n15:00\n18:00\n22:00'))
        },
        'default_location': models.WeatherLocation(lat=conf['default location'].getfloat('lat', 45.585),
                                                   lng=conf['default location'].getfloat('lng', -95.91),
                                                   name=conf['default location'].get('name', 'Morris, MN')),
        'variable_location': {
            'enabled': conf['variable location'].getboolean('enabled', False),
            'user': conf['variable location'].get('user', 'BrianMitchL'),
            'unnamed_location_name': conf['variable location'].get('unnamed_location_name', 'The Wilderness')
        },
        'log': {
            'enabled': conf['log'].getboolean('enabled', True),
            'log_path': conf['log'].get('log_path', os.path.expanduser('~') + '/weatherBot.log')
        },
        'throttles': {
            'default': conf['throttles'].getint('default', 120),
            'wind-chill': conf['throttles'].getint('wind-chill', 120),
            'medium-wind': conf['throttles'].getint('medium-wind', 180),
            'heavy-wind': conf['throttles'].getint('heavy-wind', 120),
            'fog': conf['throttles'].getint('fog', 180),
            'cold': conf['throttles'].getint('cold', 120),
            'hot': conf['throttles'].getint('hot', 120),
            'dry': conf['throttles'].getint('dry', 120),
            'heavy-rain': conf['throttles'].getint('heavy-rain', 60),
            'moderate-rain': conf['throttles'].getint('moderate-rain', 60),
            'light-rain': conf['throttles'].getint('light-rain', 90),
            'very-light-rain': conf['throttles'].getint('very-light-rain', 120),
            'heavy-snow': conf['throttles'].getint('heavy-snow', 60),
            'moderate-snow': conf['throttles'].getint('moderate-snow', 60),
            'light-snow': conf['throttles'].getint('light-snow', 90),
            'very-light-snow': conf['throttles'].getint('very-light-snow', 120),
            'heavy-sleet': conf['throttles'].getint('heavy-sleet', 45),
            'moderate-sleet': conf['throttles'].getint('moderate-sleet', 60),
            'light-sleet': conf['throttles'].getint('light-sleet', 90),
            'very-light-sleet': conf['throttles'].getint('very-light-sleet', 120),
            'heavy-hail': conf['throttles'].getint('heavy-hail', 15),
            'moderate-hail': conf['throttles'].getint('moderate-hail', 15),
            'light-hail': conf['throttles'].getint('light-hail', 20),
            'very-light-hail': conf['throttles'].getint('very-light-hail', 30)
        }
    }


def initialize_logger(log_enabled, log_pathname):
    """
    Initialize and start the logger. Logs to console, and if enabled, to a file at the given path.
    :type log_enabled: bool
    :param log_enabled: whether or not to write a log file
    :type log_pathname: str
    :param log_pathname: full path of where to write the log
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # global level of debug, so debug or anything less can be used
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    # Console handler
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    logger.addHandler(console)
    # Log file handler
    if log_enabled:
        log = logging.FileHandler(log_pathname, 'a')
        log.setLevel(logging.INFO)
        log.setFormatter(formatter)
        logger.addHandler(log)
    logger.info('Starting weatherBot with Python %s', sys.version)


def get_tweepy_api():
    """
    Return a tweepy.API object using environmental variables for keys/tokens/secrets
    :return: tweepy api object
    """
    auth = tweepy.OAuthHandler(os.getenv('WEATHERBOT_CONSUMER_KEY'), os.getenv('WEATHERBOT_CONSUMER_SECRET'))
    auth.set_access_token(os.getenv('WEATHERBOT_ACCESS_TOKEN'), os.getenv('WEATHERBOT_ACCESS_TOKEN_SECRET'))
    return tweepy.API(auth)


def get_forecast_object(lat, lng, units='us', lang='en'):
    """
    Using the 'WEATHERBOT_DARKSKY_KEY' environmental variable, get the weather from Dark Sky at the given location.
    If there is an error, log it and return None.
    :type lat: float
    :param lat: latitude
    :type lng: float
    :param lng: longitude
    :type units: str
    :param units: units standard, ex 'us', 'ca', 'uk2', 'si', 'auto'
    :type lang: str
    :param lang: language, ex: 'en', 'de'. See https://darksky.net/dev/docs/forecast for more
    :return: Forecast object or None if HTTPError or ConnectionError
    """
    try:
        return forecastio.load_forecast(os.getenv('WEATHERBOT_DARKSKY_KEY'), lat, lng, units=units, lang=lang)
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as err:
        logging.error(err)
        logging.error('Error when getting Forecast object', exc_info=True)
        return None


def get_location_from_user_timeline(username, fallback):
    """
    Load the 20 most recent tweets of a given twitter handle and return a models.WeatherLocation object of the most
    recent location. This function will find a tweet with coordinates or a place, preferring coordinates. If a location
    is not found in the most recent 20 tweets, the given fallback location will be returned.
    :type username: str
    :param username: twitter username to follow
    :type fallback: models.WeatherLocation
    :param fallback: a fallback in case no location can be found
    :return: models.WeatherLocation
    """
    api = get_tweepy_api()
    # gets the 20 most recent tweets from the given profile
    try:
        timeline = api.user_timeline(screen_name=username, include_rts=False, count=20)
        for tweet in timeline:
            # if tweet has coordinates (from a smartphone)
            if tweet.coordinates is not None:
                lat = tweet.coordinates['coordinates'][1]
                lng = tweet.coordinates['coordinates'][0]
                name = CONFIG['variable_location']['unnamed_location_name']
                # sometimes a tweet contains a coordinate, but is not in a Twitter place
                # for example, https://twitter.com/BrianMitchL/status/982664157857271810 has coordinates, but no place
                if tweet.place is not None:
                    name = tweet.place.full_name
                logging.debug('Found %s: %f, %f', name, lat, lng)
                return models.WeatherLocation(lat=lat, lng=lng, name=name)
            # if the location is a place, not coordinates
            if tweet.place is not None:
                point = utils.centerpoint(tweet.place.bounding_box.coordinates[0])
                lat = point[0]
                lng = point[1]
                name = tweet.place.full_name
                logging.debug('Found the center of bounding box at %s: %f, %f', name, lat, lng)
                return models.WeatherLocation(lat=lat, lng=lng, name=name)
        # fallback to hardcoded location if there is no valid data
        logging.warning('Could not find tweet with location, falling back to hardcoded location')
        return fallback
    except tweepy.TweepError as err:
        logging.error(err)
        logging.warning('Could not find tweet with location, falling back to hardcoded location')
        return fallback


def do_tweet(text, weather_location, tweet_location, variable_location, hashtag=None):
    """
    Post a tweet.
    If set in the config, a hashtag will be applied to the end of the tweet.
    If variable_location is True, prepend the tweet with the location name.
    If tweet_location is True, the coordinates of the the location will be embedded in the tweet.
    If successful, the status id is returned, otherwise None.
    :type text: str
    :param text: text for the tweet
    :type weather_location: models.WeatherLocation
    :param weather_location: location information used for the tweet location and inline location name
    :type tweet_location: bool
    :param tweet_location: determines whether or not to include Twitter location
    :type variable_location: bool
    :param variable_location: determines whether or not to prefix the tweet with the location
    :type hashtag: str
    :param hashtag:
    :return: a tweepy status object
    """
    api = get_tweepy_api()
    body = text
    # account for space before hashtag
    max_length = 279 - len(hashtag) if hashtag else 280

    if variable_location:
        body = weather_location.name + ': ' + body

    logging.debug('Trying to tweet: %s', body)
    if len(body) > max_length:
        # horizontal ellipsis
        body = textwrap.shorten(body, width=max_length, placeholder='\u2026')
        logging.warning('Status text is too long, tweeting the following instead: %s', body)

    if hashtag:
        body += ' ' + hashtag
    try:
        if tweet_location:
            status = api.update_status(status=body, lat=weather_location.lat, long=weather_location.lng)
        else:
            status = api.update_status(status=body)
        logging.info('Tweet success: %s', body)
        return status
    except tweepy.TweepError as err:
        logging.error('Tweet failed: %s', err.reason)
        logging.warning('Tweet skipped due to error: %s', body)
        return None


def timed_tweet(tweet_at, now, content, weather_location):
    """
    If the current time falls within the given time and given time plus the refresh rate, post a tweet using the
    do_tweet function.
    :type tweet_at: datetime.datetime
    :param tweet_at: when a tweet is supposed to be tweeted in UTC
    :type now: datetime.datetime
    :param now: current time in UTC
    :type content: str
    :param content: text for tweet
    :type weather_location: models.WeatherLocation
    """
    if tweet_at <= now < tweet_at + timedelta(minutes=CONFIG['basic']['refresh']):
        logging.debug('Timed tweet or forecast')
        do_tweet(content,
                 weather_location,
                 CONFIG['basic']['tweet_location'],
                 CONFIG['variable_location']['enabled'],
                 hashtag=CONFIG['basic']['hashtag'])


def cleanse_throttles(throttles, now):
    """
    If the expiration time of a throttle has passed, remove it from the throttles dict, then return the throttles dict.
    :type throttles: dict
    :param throttles: throttles, throttle type as the key, datetime as the value
    :type now: datetime.datetime
    :param now: the current time to check against a throttle expirey time
    :return: throttles dictionary with expired keys deleted
    """
    to_delete = [key for key, expires in throttles.items() if expires <= now]
    for key in to_delete:
        if key != 'default':
            del throttles[key]
    return throttles


def set_cache(new_cache, file='.wbcache.p'):
    """
    This will write new_cache to the given file using pickle.
    :type new_cache: object
    :param new_cache: object to save as a cache
    :type file: str
    :param file: path to file to write cache to
    """
    with open(file, 'wb') as handle:
        pickle.dump(new_cache, handle)


def get_cache(file='.wbcache.p'):
    """
    This will return the object at the given path, or if the file does not exist, return the cache global variable
    :type file: str
    :param file: path to file to access for loading a cache
    """
    if os.path.isfile(file):
        with open(file, 'rb') as handle:
            return pickle.load(handle)
    else:
        return CACHE


def tweet_logic(weather_data, wb_string):
    """
    Core logic for tweets once initialization and configuration has been set and weather data fetched.
    :type weather_data: models.WeatherData
    :type wb_string: models.WeatherBotString
    """
    # pylint: disable=global-variable-not-assigned
    # CACHE is being modified here, pylint doesn't see that
    global CACHE
    wb_string.set_weather(weather_data)
    special = wb_string.special()
    normal_text = wb_string.normal()

    now = datetime.utcnow()
    now_utc = utils.datetime_to_utc('UTC', now)
    now_local = utils.localize_utc_datetime(weather_data.timezone, now)

    # weather alerts
    for alert in weather_data.alerts:
        if alert.sha() not in CACHE['throttles'] and not alert.expired(now_utc):
            try:
                CACHE['throttles'][alert.sha()] = alert.expires
            except AttributeError:
                # most alerts are probably done after 3 days
                CACHE['throttles'][alert.sha()] = alert.time + timedelta(days=3)
            do_tweet(wb_string.alert(alert, weather_data.timezone),
                     weather_data.location,
                     CONFIG['basic']['tweet_location'],
                     CONFIG['variable_location']['enabled'],
                     hashtag=CONFIG['basic']['hashtag'])

    # forecast
    forecast_dt = now_local.replace(hour=CONFIG['scheduled_times']['forecast'].hour,
                                    minute=CONFIG['scheduled_times']['forecast'].minute,
                                    second=0, microsecond=0).astimezone(pytz.utc)
    timed_tweet(forecast_dt, now_utc, wb_string.forecast(), weather_data.location)

    # scheduled tweet
    for scheduled_time in CONFIG['scheduled_times']['conditions']:
        scheduled_dt = now_local.replace(hour=scheduled_time.hour,
                                         minute=scheduled_time.minute,
                                         second=0, microsecond=0).astimezone(pytz.utc)
        timed_tweet(scheduled_dt, now_utc, normal_text, weather_data.location)

    # special condition
    if special.type != 'normal':
        logging.debug('Special event')
        try:
            next_allowed = CACHE['throttles'][special.type]
        except KeyError:
            next_allowed = CACHE['throttles']['default']

        if now_utc >= next_allowed:
            try:
                minutes = CONFIG['throttles'][special.type]
            except KeyError:
                minutes = CONFIG['throttles']['default']
            do_tweet(special.text,
                     weather_data.location,
                     CONFIG['basic']['tweet_location'],
                     CONFIG['variable_location']['enabled'],
                     hashtag=CONFIG['basic']['hashtag'])
            CACHE['throttles'][special.type] = now_utc + timedelta(minutes=minutes)
        logging.debug(CACHE)


def main(path):
    """
    Main function called when starting weatherBot. The path is to the configuration file.
    :type path: str
    :param path: path to configuration file
    """
    # pylint: disable=broad-except,no-member
    global CACHE
    load_config(os.path.abspath(path))
    initialize_logger(CONFIG['log']['enabled'], CONFIG['log']['log_path'])
    logging.debug(CONFIG)
    keys.set_twitter_env_vars()
    keys.set_darksky_env_vars()
    CACHE['throttles']['default'] = pytz.utc.localize(datetime.utcnow()).astimezone(pytz.utc)
    with open(CONFIG['basic']['strings'], 'r') as file_stream:
        try:
            weatherbot_strings = yaml.safe_load(file_stream)
            logging.debug(weatherbot_strings)
            wb_string = models.WeatherBotString(weatherbot_strings)
        except yaml.YAMLError as err:
            logging.error(err, exc_info=True)
            logging.error('Could not read YAML file, please correct, run yamllint, and try again.')
            sys.exit()

    location = CONFIG['default_location']
    updated_time = utils.datetime_to_utc('UTC', datetime.utcnow()) - timedelta(minutes=30)
    try:
        while True:
            # check for new location every 30 minutes
            now_utc = utils.datetime_to_utc('UTC', datetime.utcnow())
            if CONFIG['variable_location']['enabled'] and updated_time + timedelta(minutes=30) < now_utc:
                location = get_location_from_user_timeline(CONFIG['variable_location']['user'], location)
                updated_time = now_utc
            forecast = get_forecast_object(location.lat, location.lng, CONFIG['basic']['units'],
                                           wb_string.language)
            if forecast is not None:
                weather_data = models.WeatherData(forecast, location)
                if weather_data.valid:
                    CACHE = get_cache()
                    tweet_logic(weather_data, wb_string)
                CACHE['throttles'] = cleanse_throttles(CACHE['throttles'], now_utc)
                set_cache(CACHE)
                time.sleep(CONFIG['basic']['refresh'] * 60)
            else:
                time.sleep(60)
    except Exception as err:
        logging.error(err)
        logging.error('We got an exception!', exc_info=True)
        if CONFIG['basic']['dm_errors']:
            api = get_tweepy_api()
            api.send_direct_message(recipient_id=api.me().id,
                                    text=datetime.utcnow().isoformat() + '\n' + traceback.format_exc())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='weatherBot')
    parser.add_argument('conf', metavar='conf', type=str, help='The configuration file')
    args = parser.parse_args()
    if os.path.isfile(args.conf):
        main(sys.argv[1])
    else:
        print('The file `' + sys.argv[1] + '` is not a file or does not exist. Try again.')
