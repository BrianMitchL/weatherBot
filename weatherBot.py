#!/usr/bin/env python3

# weatherBot
# Copyright 2015-2016 Brian Mitchell under the MIT license
# See the GitHub repository: https://github.com/bman4789/weatherBot

import hashlib
import logging
import os
import random
import sys
import time
import traceback
from datetime import datetime
from datetime import timedelta
from os.path import expanduser

import daemon
import forecastio
import googlemaps
import pytz
import tweepy

import keys
import strings
import utils

# Constants - Configure things here
DM_ERRORS = True  # send crash logs as a direct message to the Twitter account owning the app
DEFAULT_LOCATION = {'lat': 45.585, 'lng': -95.91, 'name': 'Morris, MN'}  # Used for location, or fallback location
UNITS = 'us'  # Choose from 'us', 'ca', 'uk2', or 'si'
TWEET_LOCATION = True  # include location in tweet (Twitter location)
# HASHTAG = ' #MorrisWeather'  # if no hashtag is desired, set HASHTAG to be an empty string
# VARIABLE_LOCATION = False  # whether or not to change the location based on a user's most recent tweet location
HASHTAG = ''  # if no hashtag is desired, set HASHTAG to be an empty string
VARIABLE_LOCATION = True  # whether or not to change the location based on a user's most recent tweet location
USER_FOR_LOCATION = 'bman4789'  # username for account to track location with
LOG_PATHNAME = expanduser('~') + '/weatherBot.log'  # expanduser('~') returns the path to the current user's home dir
REFRESH_RATE = 3  # how often to check for new weather (note, watch out for API rate limiting)
SPECIAL_EVENT_TIMES = {  # time in minutes to throttle each event type
    'default': 120,
    'wind-chill': 120,
    'medium-wind': 180,
    'heavy-wind': 120,
    'heavy-rain': 60,
    'fog': 180,
    'mixed-precipitation': 120,
    'snow': 120,
    'sleet': 120,
    'very-light-rain': 120,
    'drizzle': 120,
    'cold': 120,
    'hot': 120,
    'dry': 120
}

# Global variables
throttle_times = {'default': pytz.utc.localize(datetime.utcnow()).astimezone(pytz.utc)}
# if variable location is enabled, but no user is given, disable variable location
if VARIABLE_LOCATION and USER_FOR_LOCATION is '':
    VARIABLE_LOCATION = False


class BadForecastDataError(Exception):
    pass


def initialize_logger(log_pathname):
    """
    :param log_pathname: string containing the full path of where to write the log
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
    log = logging.FileHandler(log_pathname, 'a')
    log.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    log.setFormatter(formatter)
    logger.addHandler(log)
    logger.info('Starting weatherBot with Python {0}'.format(sys.version))


def get_tweepy_api():
    """
    :return: tweepy api object
    """
    auth = tweepy.OAuthHandler(os.getenv('WEATHERBOT_CONSUMER_KEY'), os.getenv('WEATHERBOT_CONSUMER_SECRET'))
    auth.set_access_token(os.getenv('WEATHERBOT_ACCESS_KEY'), os.getenv('WEATHERBOT_ACCESS_SECRET'))
    return tweepy.API(auth)


def get_forecast_object(lat, lng):
    """
    :param lat: float containing latitude
    :param lng: float containing longitude
    :return:
    """
    return forecastio.load_forecast(os.getenv('WEATHERBOT_FORECASTIO_KEY'), lat, lng, units=UNITS)


def get_timezone(location, timestamp=datetime.utcnow()):
    """
    :param location: dict containing the keys 'lat' and 'lng' representing a latitude and longitude
    :param timestamp: datetime object used to determine if daylight savings should be applied
    :return: googlemaps.client.Client object
    """
    gmaps = googlemaps.Client(key=os.getenv('WEATHERBOT_GOOGLEMAPS_KEY'))
    res = gmaps.timezone(location=location, timestamp=timestamp, language='en')
    if 'timeZoneId' in res:
        return res['timeZoneId']
    else:
        'UTC'  # fallback to UTC


def get_location_from_user_timeline(username, fallback):
    """
    :param username: the string of the twitter username to follow
    :param fallback: a dict in the form of {'lat': 45.585, 'lng': -95.91, 'name': 'Morris, MN'}
                     containing a fallback in case no location can be found
    :return: a location dict in the form of {'lat': 45.585, 'lng': -95.91, 'name': 'Morris, MN'}
    """
    api = get_tweepy_api()
    # gets the 20 most recent tweets from the given profile
    timeline = api.user_timeline(screen_name=username, include_rts=False, count=20)
    for tweet in timeline:
        # if tweet has coordinates (from a smartphone)
        if tweet.coordinates is not None:
            loc = dict()
            loc['lat'] = tweet.coordinates['coordinates'][1]
            loc['lng'] = tweet.coordinates['coordinates'][0]
            loc['name'] = tweet.place.full_name
            logging.debug('Found {0}: {1}, {2}'.format(loc['name'], loc['lat'], loc['lng']))
            return loc
        # if the location is a place, not coordinates
        elif tweet.place is not None:
            point = utils.centerpoint(tweet.place.bounding_box.coordinates[0])
            loc = dict()
            loc['lat'] = point[0]
            loc['lng'] = point[1]
            loc['name'] = tweet.place.full_name
            logging.debug('Found the center of bounding box at {0}: {1}, {2}'
                          .format(loc['name'], loc['lat'], loc['lng']))
            return loc
    # fallback to hardcoded location if there is no valid data
    logging.warning('Could not find tweet with location, falling back to hardcoded location')
    return fallback


def get_weather_variables(forecast, location):
    """
    :param forecast: forecastio object
    :param location: location dict with 'lat', 'lng', and 'name' keys
    :return: weather_data dict containing weather information
    """
    try:
        weather_data = dict()
        if 'darksky-unavailable' in forecast.json['flags']:
            raise BadForecastDataError('Darksky unavailable')
        if not forecast.currently().temperature:
            raise BadForecastDataError('Temp is none')
        if not forecast.currently().summary:
            raise BadForecastDataError('Hour summary is none')
        if not forecast.minutely().summary:
            raise BadForecastDataError('Minutely (hour) summary is none')
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
        weather_data['windSpeed_and_unit'] = str(round(forecast.currently().windSpeed)) + ' ' + \
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
        weather_data['longitude'] = location['lng']
        weather_data['forecast'] = forecast.daily().data[0]
        weather_data['hour_icon'] = forecast.minutely().icon
        weather_data['hour_summary'] = forecast.minutely().summary
        weather_data['alerts'] = forecast.alerts()
        weather_data['valid'] = True
        logging.debug('Weather data: {0}'.format(weather_data))
        return weather_data
    except (KeyError, TypeError, BadForecastDataError) as err:
        logging.error('Found an error in get_weather_variables')
        logging.error(err)
        return {'valid': False}


def make_forecast(weather_data):
    """
    :param weather_data: weather_data dict
    :return: string containing the text for a forecast tweet
    """
    forecast = weather_data['forecast']
    units = weather_data['units']
    return 'The forecast for today is ' + forecast.summary.lower() + '  ' + str(round(forecast.temperatureMax)) + \
           units['temperatureMax'] + '/' + str(round(forecast.temperatureMin)) + units['temperatureMin'] + \
           '. ' + random.choice(strings.endings)


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
    logging.debug('Trying to tweet: {0}'.format(text))
    if variable_location:
        text = weather_data['location'] + ': ' + text
    try:
        if tweet_location:
            status = api.update_status(status=text, lat=weather_data['latitude'], long=weather_data['longitude'])
        else:
            status = api.update_status(status=text)
        logging.info('Tweet success: {0}'.format(text))
        return status
    except tweepy.TweepError as e:
        logging.error('Tweet failed: {0}'.format(e.reason))
        logging.warning('Tweet skipped due to error: {0}'.format(text))
        return None


def alert_logic(weather_data, timezone_id, now_utc):
    """
    :param weather_data: dict containing weather information
    :param timezone_id: string containing a datetime timezone id
    :param now_utc: datetime.datetime in utc timezone
    :return: list of text to use for alert tweets, can be an empty list
    """
    global throttle_times
    alerts = weather_data['alerts']
    tweets = list()
    if alerts:
        for i in alerts:
            full_alert = alerts[i].title \
                         + alerts[i].expires \
                         + alerts[i].description \
                         + alerts[i].uri
            sha256 = hashlib.sha256(full_alert.encode()).hexdigest()  # a (hopefully) unique id on each alert

            # if the alert has not been tweeted, and the expiration is older than the current time
            expires = pytz.utc.localize(datetime.fromtimestamp(alerts[i].expires))
            if sha256 not in throttle_times and expires <= now_utc:
                local_expires_time = utils.get_local_datetime(timezone_id, expires)
                throttle_times[sha256] = expires
                tweets.append(strings.get_alert_text(alerts[i].title, local_expires_time, alerts[i].uri))
    return tweets


def tweet_logic(weather_data, timezone_id):  # TODO document arguments and returns
    global throttle_times
    special_description, special_text = strings.get_special_condition(weather_data)
    normal_text = strings.get_normal_condition(weather_data)

    now = datetime.utcnow()
    now_utc = utils.get_utc_datetime('UTC', now)
    now_local = utils.get_local_datetime(timezone_id, now)

    # weather alerts
    for alert in alert_logic(weather_data, timezone_id, now_utc):
        do_tweet(alert, weather_data, TWEET_LOCATION, VARIABLE_LOCATION)

    # forecast
    forecast_dt = now_local.replace(hour=6, minute=0, second=0, microsecond=0).astimezone(pytz.utc)
    forecast_tweet(forecast_dt, now_utc, weather_data)

    # standard timed tweet
    times = list()
    # all times are local to the timezone that is found from the coordinates used for location
    times.append(now_local.replace(hour=7, minute=0, second=0, microsecond=0).astimezone(pytz.utc))
    times.append(now_local.replace(hour=12, minute=0, second=0, microsecond=0).astimezone(pytz.utc))
    times.append(now_local.replace(hour=15, minute=0, second=0, microsecond=0).astimezone(pytz.utc))
    times.append(now_local.replace(hour=18, minute=0, second=0, microsecond=0).astimezone(pytz.utc))
    times.append(now_local.replace(hour=22, minute=0, second=0, microsecond=0).astimezone(pytz.utc))
    for dt in times:
        timed_tweet(dt, now_utc, normal_text, weather_data)

    # special condition
    if special_description != 'normal':
        logging.debug('Special event')
        try:
            next_allowed = throttle_times[special_description]
        except KeyError:
            next_allowed = throttle_times['default']

        if now_utc >= next_allowed:
            try:
                minutes = SPECIAL_EVENT_TIMES[special_description]
            except KeyError:
                minutes = SPECIAL_EVENT_TIMES['default']
            do_tweet(special_text, weather_data, TWEET_LOCATION, VARIABLE_LOCATION)
            throttle_times[special_description] = now_utc + timedelta(minutes=minutes)
        logging.debug(throttle_times)


def timed_tweet(tweet_at, now, content, weather_data):
    if tweet_at <= now < tweet_at + timedelta(minutes=REFRESH_RATE):
        logging.debug('Timed tweet or forecast')
        do_tweet(content, weather_data, TWEET_LOCATION, VARIABLE_LOCATION)


def forecast_tweet(tweet_at, now, weather_data):
    if tweet_at <= now < tweet_at + timedelta(minutes=REFRESH_RATE):
        logging.debug('Scheduled forecast')
        do_tweet(make_forecast(weather_data), weather_data, TWEET_LOCATION, VARIABLE_LOCATION)


def main():
    try:
        initialize_logger(LOG_PATHNAME)
        keys.set_twitter_env_vars()
        keys.set_forecastio_env_vars()
        keys.set_googlemaps_env_vars()

        location = DEFAULT_LOCATION
        timezone_id = get_timezone(location)
        updated_time = utils.get_utc_datetime('UTC', datetime.utcnow()) - timedelta(minutes=30)
        while True:
            # check for new location every 30 minutes
            now_utc = utils.get_utc_datetime('UTC', datetime.utcnow())
            if VARIABLE_LOCATION and updated_time + timedelta(minutes=30) < now_utc:
                location = get_location_from_user_timeline(USER_FOR_LOCATION, location)
                timezone_id = get_timezone(location)
                updated_time = now_utc
            forecast = get_forecast_object(location['lat'], location['lng'])
            weather_data = get_weather_variables(forecast, location)
            if weather_data['valid'] is True:
                tweet_logic(weather_data, timezone_id)
            time.sleep(REFRESH_RATE * 60)
    except Exception as err:
        logging.error(err)
        logging.error('We got an exception!', exc_info=True)
        if DM_ERRORS:
            api = get_tweepy_api()
            api.send_direct_message(screen_name=api.me().screen_name,
                                    text=str(random.randint(0, 9999)) + traceback.format_exc())

if __name__ == '__main__':
    if '-d' in sys.argv:
        with daemon.DaemonContext():
            main()
    else:
        main()
