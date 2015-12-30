#!/usr/bin/env python3

# weatherBot
# Copyright 2015 Brian Mitchell under the MIT license
# See the GitHub repository: https://github.com/bman4789/weatherBot

from datetime import datetime
from datetime import timedelta
import sys
import time
import random
import logging
import os
from os.path import expanduser
import tweepy
import forecastio
import daemon
import traceback
import utils
import keys
import strings

# Constants - Configure things here
DM_ERRORS = True  # send crash logs as a direct message to the Twitter account owning the app
DEFAULT_LOCATION = {'lat': 45.585, 'lon': -95.91, 'name': 'Morris, MN'}  # Used for location, or fallback location
UNITS = 'us'  # Choose from 'us', 'ca', 'uk2', or 'si'
TWEET_LOCATION = True  # include location in tweet (Twitter location)
# HASHTAG = " #MorrisWeather"  # if no hashtag is desired, set HASHTAG to be an empty string
# VARIABLE_LOCATION = False  # whether or not to change the location based on a user's most recent tweet location
HASHTAG = ""  # if no hashtag is desired, set HASHTAG to be an empty string
VARIABLE_LOCATION = True  # whether or not to change the location based on a user's most recent tweet location
USER_FOR_LOCATION = 'bman4789'  # username for account to track location with
LOG_PATHNAME = expanduser("~") + '/weatherBot.log'  # expanduser("~") returns the path to the current user's home dir

# Global variables
last_special = datetime.now()
refresh_rate = 3  # how often to check for new weather (note, watch out for API rate limiting)
# if variable location is enabled, but no user is given, disable variable location
if VARIABLE_LOCATION and USER_FOR_LOCATION is '':
    VARIABLE_LOCATION = False


def initialize_logger(log_pathname):
    """
    :param log_pathname: straing containing the full path of where to write the log
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # global level of debug, so debug or anything less can be used
    # Console handler
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)
    # Log file handler
    log = logging.FileHandler(log_pathname, "a", encoding=None, delay="true")
    # delay="true" means file will not be created until logged to
    log.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    log.setFormatter(formatter)
    logger.addHandler(log)
    logger.info("Starting weatherBot with Python %s", sys.version)


def get_tweepy_api():
    """
    :return: tweepy api object
    """
    auth = tweepy.OAuthHandler(os.getenv('WEATHERBOT_CONSUMER_KEY'), os.getenv('WEATHERBOT_CONSUMER_SECRET'))
    auth.set_access_token(os.getenv('WEATHERBOT_ACCESS_KEY'), os.getenv('WEATHERBOT_ACCESS_SECRET'))
    return tweepy.API(auth)


def get_forecast_object(lat, lon):
    """
    :param lat: float containing latitude
    :param lon: float containing longitude
    :return:
    """
    return forecastio.load_forecast(os.getenv('WEATHERBOT_FORECASTIO_KEY'), lat, lon, units=UNITS)


def centerpoint(geolocations):
    """
    :param geolocations: array of arrays in the form of [[longitude, latitude],[longitude,latitude]]
    :return: average latitude and longitude in the form [latitude, longitude]
    """
    lats = []
    lons = []
    for lon, lat in geolocations:
        lats.append(lat)
        lons.append(lon)
    avg_lat = float(sum(lats))/len(lats)
    avg_lon = float(sum(lons))/len(lons)
    return [avg_lat, avg_lon]


def get_location_from_user_timeline(username, fallback):
    """
    :param username: the string of the twitter username to follow
    :param fallback: a dict in the form of {'lat': 45.585, 'lon': -95.91, 'name': 'Morris, MN'}
                     containing a fallback in case no location can be found
    :return: a location dict in the form of {'lat': 45.585, 'lon': -95.91, 'name': 'Morris, MN'}
    """
    api = get_tweepy_api()
    # gets the 20 most recent tweets from the given profile
    timeline = api.user_timeline(screen_name=username, include_rts=False, count=20)
    for tweet in timeline:
        # if tweet has coordinates (from a smartphone)
        if tweet.coordinates is not None:
            loc = dict()
            loc['lat'] = tweet.coordinates['coordinates'][1]
            loc['lon'] = tweet.coordinates['coordinates'][0]
            loc['name'] = tweet.place.full_name
            logging.debug('Found %s: %s, %s', loc['name'], loc['lat'], loc['lon'])
            return loc
        # if the location is a place, not coordinates
        elif tweet.place is not None:
            point = centerpoint(tweet.place.bounding_box.coordinates[0])
            loc = dict()
            loc['lat'] = point[0]
            loc['lon'] = point[1]
            loc['name'] = tweet.place.full_name
            logging.debug('Found the center of bounding box at %s: %s, %s', loc['name'], loc['lat'], loc['lon'])
            return loc
    # fallback to hardcoded location if there is no valid data
    logging.error('Could not find tweet with location, falling back to hardcoded location')
    return fallback


def get_weather_variables(forecast, location):
    """
    :param forecast: forecastio object
    :param location: location dict with 'lat', 'lon', and 'name' keys
    :return: weather_data dict containing weather information
    """
    try:
        weather_data = dict()
        weather_data['units'] = utils.get_units(UNITS)
        # forecast.io doesn't always include 'windBearing' or 'nearestStormDistance'
        if hasattr(forecast.currently(), 'windBearing'):
            weather_data['windBearing'] = utils.get_wind_direction(forecast.currently().windBearing)
        else:
            weather_data['windBearing'] = 'unknown direction'
        if hasattr(forecast.currently(), 'nearestStormDistance'):
            weather_data['nearestStormDistance'] = forecast.currently().nearestStormDistance
        else:
            weather_data['nearestStormDistance'] = 99999
        weather_data['windSpeed'] = forecast.currently().windSpeed
        weather_data['windSpeed_and_unit'] = str(round(forecast.currently().windSpeed)) + " " + \
            weather_data['units']['windSpeed']
        weather_data['apparentTemperature'] = forecast.currently().apparentTemperature
        weather_data['apparentTemperature_and_unit'] = str(round(forecast.currently().apparentTemperature)) + 'º' \
            + weather_data['units']['apparentTemperature']
        weather_data['temp'] = forecast.currently().temperature
        weather_data['temp_and_unit'] = str(round(forecast.currently().temperature)) + 'º' + \
            weather_data['units']['temperature']
        weather_data['humidity'] = round(forecast.currently().humidity * 100)
        weather_data['precipIntensity'] = forecast.currently().precipIntensity
        weather_data['summary'] = forecast.currently().summary.lower()
        weather_data['icon'] = forecast.currently().icon
        weather_data['location'] = location['name']
        weather_data['latitude'] = location['lat']
        weather_data['longitude'] = location['lon']
        weather_data['forecast'] = forecast.daily().data[0]
        weather_data['valid'] = True
        logging.debug('Weather data: %s', weather_data)
        return weather_data
    except (KeyError, TypeError) as err:
        logging.error('Found a KeyError or TypeError in get_weather_variables')
        logging.error(err)
        return {'valid': False}


def make_forecast(weather_data):
    """
    :param weather_data: weather_data dict
    :return: string containing the text for a forecast tweet
    """
    forecast = weather_data['forecast']
    units = weather_data['units']
    return "The forecast for today is " + forecast.summary.lower() + "  " + str(round(forecast.temperatureMax)) + \
           units['temperatureMax'] + "/" + str(round(forecast.temperatureMin)) + units['temperatureMin'] + \
           ". " + random.choice(strings.endings)


def do_tweet(text, weather_data, tweet_location, variable_location):
    """
    :param text: text for the tweet
    :param weather_data: weather_data dict
    :param tweet_location: boolean that determines whether or not to include Twitter location
    :param variable_location: boolean that determines whether or not to prefix the tweet with the location
    :return: a tweepy status object
    """
    api = get_tweepy_api()
    text += HASHTAG
    logging.debug('Trying to tweet: %s', text)
    if variable_location:
        text = weather_data['location'] + ': ' + text
    try:
        if tweet_location:
            status = api.update_status(status=text, lat=weather_data['latitude'], long=weather_data['longitude'])
        else:
            status = api.update_status(status=text)
        logging.info('Tweet success: %s', text)
        return status
    except tweepy.TweepError as e:
        logging.error('Tweet failed: %s', e.reason)
        logging.warning('Tweet skipped due to error: %s', text)
        return None


def tweet_logic(weather_data):
    global last_special
    now = datetime.now()
    special_event = strings.get_special_condition(weather_data)
    normal_event = strings.get_normal_condition(weather_data)
    # Standard timed tweet
    forecast_tweet(now.replace(hour=6, minute=0, second=0, microsecond=0), now, weather_data)
    timed_tweet(now.replace(hour=7, minute=0, second=0, microsecond=0), now, normal_event, weather_data)
    timed_tweet(now.replace(hour=12, minute=0, second=0, microsecond=0), now, normal_event, weather_data)
    timed_tweet(now.replace(hour=15, minute=0, second=0, microsecond=0), now, normal_event, weather_data)
    timed_tweet(now.replace(hour=18, minute=0, second=0, microsecond=0), now, normal_event, weather_data)
    timed_tweet(now.replace(hour=22, minute=0, second=0, microsecond=0), now, normal_event, weather_data)
    if special_event != "normal" and now > last_special + timedelta(minutes=20):
        # Post special weather event at any time. Do not tweet more than one special event every 20 minutes
        logging.debug("Special event")
        do_tweet(special_event, weather_data, TWEET_LOCATION, VARIABLE_LOCATION)
        last_special = now


def timed_tweet(tweet_at, now, content, weather_data):
    if tweet_at <= now < tweet_at + timedelta(minutes=refresh_rate):
        logging.debug("Timed tweet or forecast")
        do_tweet(content, weather_data, TWEET_LOCATION, VARIABLE_LOCATION)


def forecast_tweet(tweet_at, now, weather_data):
    if tweet_at <= now < tweet_at + timedelta(minutes=refresh_rate):
        logging.debug("Scheduled forecast")
        do_tweet(make_forecast(weather_data), weather_data, TWEET_LOCATION, VARIABLE_LOCATION)


def main():
    try:
        initialize_logger(LOG_PATHNAME)
        keys.set_twitter_env_vars()
        keys.set_forecastio_env_vars()
        updated_time = datetime.now() - timedelta(minutes=30)
        location = DEFAULT_LOCATION
        while True:
            # check for new location every 30 minutes
            if VARIABLE_LOCATION and updated_time + timedelta(minutes=30) < datetime.now():
                location = get_location_from_user_timeline(USER_FOR_LOCATION, location)
                updated_time = datetime.now()
            forecast = get_forecast_object(location['lat'], location['lon'])
            weather_data = get_weather_variables(forecast, location)
            if weather_data['valid'] is True:
                tweet_logic(weather_data)
            time.sleep(refresh_rate * 60)
    except Exception as err:
        logging.error(err)
        logging.error('We got an exception!', exc_info=True)
        if DM_ERRORS:
            api = get_tweepy_api()
            api.send_direct_message(screen_name=api.me().screen_name,
                                    text=str(random.randint(0, 9999)) + traceback.format_exc())

if __name__ == '__main__':
    if "-d" in sys.argv:
        with daemon.DaemonContext():
            main()
    else:
        main()
