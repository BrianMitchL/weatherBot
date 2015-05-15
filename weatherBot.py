#!/usr/bin/env python
# -*- coding: utf-8 -*-

# weatherBot
# Copyright 2015 Brian Mitchell under the MIT license
# See the GitHub repository: https://github.com/bman4789/weatherBot

from datetime import datetime
from datetime import timedelta
import sys
import time
import random
import logging
import json
import os
from os.path import expanduser
import tweepy
import daemon
from keys import set_twitter_env_vars
from keys import set_flickr_env_vars
# Python 3 imports
try:
    from urllib.request import urlopen
    from urllib.parse import urlencode
    from urllib.error import URLError
except ImportError:
    # Python 2 imports
    from urllib import urlencode
    from urllib2 import urlopen
    from urllib2 import URLError

# Constants
WOEID = '2454256'  # Yahoo! Weather location ID
UNIT = 'f'  # units. 'c' for metric, 'f' for imperial. This changes all units, not just temperature
TWEET_LOCATION = True  # include location in tweet
LOG_PATHNAME = expanduser("~") + '/weatherBot.log'  # expanduser("~") returns the path to the current user's home dir
HASHTAG = " #MorrisWeather"  # if not hashtag is desired, set HASHTAG to be an empty string
VARIABLE_LOCATION = False  # whether or not to change the location based on a user's most recent tweet location
USER_FOR_LOCATION = 'bman4789'  # username for account to track location with

# Global variables
last_special = datetime.now()
deg = "º"
if sys.version < '3':
    deg = deg.decode('utf-8')
# if UNIT has an issue, set it to metric
if UNIT != 'c' and UNIT != 'f':
    UNIT = 'c'


def initialize_logger(log_pathname):
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
    auth = tweepy.OAuthHandler(os.getenv('WEATHERBOT_CONSUMER_KEY'), os.getenv('WEATHERBOT_CONSUMER_SECRET'))
    auth.set_access_token(os.getenv('WEATHERBOT_ACCESS_KEY'), os.getenv('WEATHERBOT_ACCESS_SECRET'))
    return tweepy.API(auth)


def get_woeid_from_variable_location(woeid, username):
    api = get_tweepy_api()
    # gets the 20 most recent tweets from the given profile
    timeline = api.user_timeline(screen_name=username, include_rts=False, count=20)
    for tweet in timeline:
        # if tweet has coordinates (from a smartphone)
        if tweet.coordinates is not None:
            lat = tweet.coordinates['coordinates'][1]
            lon = tweet.coordinates['coordinates'][0]
            logging.debug('Found the coordinates of %s and %s', lat, lon)
            flickr_query = "https://api.flickr.com/services/rest/?method=flickr.places.findByLatLon&api_key=" \
                + os.getenv('WEATHERBOT_FLICKR_KEY') + "&lat=" + str(lat) + "&lon=" + str(lon) \
                + "&format=json&nojsoncallback=1"
            data = query_flickr(flickr_query)
            try:
                return data['places']['place'][0]['woeid']
            except (ValueError, KeyError) as err:
                logging.error(err)
                logging.error('Falling back to hardcoded location')
                # fallback to hardcoded location if there is no valid data
                return woeid
        # if the location is a general city or name, not coordinates
        elif tweet.place is not None:
            # YQL seems to find the right location when removing the comma
            query = 'select woeid from geo.places where text="' + tweet.place.full_name.replace(',', '') \
                    + '" | truncate(count=1)'
            result = query_yql(query)
            try:
                return result['query']['results']['place']['woeid']
            except (ValueError, KeyError) as err:
                logging.error(err)
                logging.error('Falling back to hardcoded location')
                # fallback to hardcoded location if there is no valid data
                return woeid
    # fallback to hardcoded location if there is no valid data
    logging.error('Could not find tweet with location, falling back to hardcoded location')
    return woeid


def query_yql(query):
    ybaseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_url = ybaseurl + urlencode({'q': query}) + "&format=json"
    try:
        yresult = urlopen(yql_url).read()
        return convert_to_json(yresult)
    except (URLError, IOError) as err:
        logging.error('Tried to load: %s', yql_url)
        logging.error(err)
        return ''


def query_flickr(encoded_query):
    try:
        flickr_result = urlopen(encoded_query).read()
        return convert_to_json(flickr_result)
    except (URLError, IOError) as err:
        logging.error('Tried to load: %s', encoded_query)
        logging.error(err)
        return ''


def convert_to_json(data):
    try:
        if sys.version < '3':
            return json.loads(data)
        else:
            return json.loads(data.decode('utf8'))
    except ValueError as err:
        logging.error("Failed to convert to json: %s", err)
        return ''


def get_weather(woeid, unit):
    query = "select * from weather.forecast where woeid=" + woeid + " and u=\"" + unit + "\""
    return query_yql(query)


def get_wind_direction(degrees):
    try:
        degrees = int(degrees)
    except ValueError:
        return ''
    if degrees < 23 or degrees >= 338:
        return 'N'
    elif degrees < 68:
        return 'NE'
    elif degrees < 113:
        return 'E'
    elif degrees < 158:
        return 'SE'
    elif degrees < 203:
        return 'S'
    elif degrees < 248:
        return 'SW'
    elif degrees < 293:
        return 'W'
    elif degrees < 338:
        return 'NW'


def get_weather_variables(ydata):
    try:
        weather_data = {}
        units = ydata['query']['results']['channel']['units']
        weather_data['units'] = ydata['query']['results']['channel']['units']
        # Sometimes, YQL returns empty strings for wind speed and direction
        if ydata['query']['results']['channel']['wind']['speed'] != "":
            weather_data['wind_speed'] = float(ydata['query']['results']['channel']['wind']['speed'])
            weather_data['wind_speed_and_unit'] = ydata['query']['results']['channel']['wind']['speed'] + " " + units['speed']
        else:
            weather_data['wind_speed'] = 0.0
            weather_data['wind_speed_and_unit'] = "0 " + units['speed']
        if ydata['query']['results']['channel']['wind']['direction'] != "":
            weather_data['wind_direction'] = get_wind_direction(int(ydata['query']['results']['channel']['wind']['direction']))
        else:
            weather_data['wind_direction'] = get_wind_direction(0)
        weather_data['wind_chill'] = int(ydata['query']['results']['channel']['wind']['chill'])
        weather_data['humidity'] = int(ydata['query']['results']['channel']['atmosphere']['humidity'])
        weather_data['temp'] = int(ydata['query']['results']['channel']['item']['condition']['temp'])
        weather_data['code'] = int(ydata['query']['results']['channel']['item']['condition']['code'])
        weather_data['condition'] = ydata['query']['results']['channel']['item']['condition']['text']
        weather_data['deg_unit'] = deg + units['temperature']
        weather_data['temp_and_unit'] = ydata['query']['results']['channel']['item']['condition']['temp'] + deg + units['temperature']
        weather_data['city'] = ydata['query']['results']['channel']['location']['city']
        weather_data['region'] = ydata['query']['results']['channel']['location']['region']
        weather_data['latitude'] = ydata['query']['results']['channel']['item']['lat']
        weather_data['longitude'] = ydata['query']['results']['channel']['item']['long']
        weather_data['forecast'] = ydata['query']['results']['channel']['item']['forecast']
        weather_data['valid'] = True
        logging.debug("Weather data: %s", weather_data)
        return weather_data
    except (KeyError, TypeError) as err:
        logging.error("ydata: %s", ydata)
        logging.error(err)
        return {'valid': False}


def make_normal_tweet(weather_data):
    text = [
        "The weather is boring. " + weather_data['temp_and_unit'] + " and " + weather_data['condition'].lower() + ".",
        "Great, it's " + weather_data['condition'].lower() + " and " + weather_data['temp_and_unit'] + ".",
        "What a normal day, it's " + weather_data['condition'].lower() + " and " + weather_data['temp_and_unit'] + ".",
        "Whoopie do, it's " + weather_data['temp_and_unit'] + " and " + weather_data['condition'].lower() + ".",
        weather_data['temp_and_unit'] + " and " + weather_data['condition'].lower() + ".",
        weather_data['temp_and_unit'] + " and " + weather_data['condition'].lower() + ". What did you expect?",
        "Welcome to " + weather_data['city'] + ", " + weather_data['region'] + ", where it's " + weather_data['condition'].lower() + " and " + weather_data['temp_and_unit'] + ".",
        "Breaking news: it's " + weather_data['condition'].lower() + " and " + weather_data['temp_and_unit'] + ".",
        "We got some " + weather_data['condition'].lower() + " at " + weather_data['temp_and_unit'] + " going on.",
        "Well, would you look at that, it's " + weather_data['temp_and_unit'] + " and " + weather_data['condition'].lower() + ".",
        "Great Scott, it's " + weather_data['condition'].lower() + " and " + weather_data['temp_and_unit'] + "!",
        "It's " + weather_data['temp_and_unit'] + " and " + weather_data['condition'].lower() + ", oh boy!",
        "Only in " + weather_data['city'] + ", " + weather_data['region'] + " would it be " + weather_data['temp_and_unit'] + " and " + weather_data['condition'].lower() + " right now.",
        "Golly gee wilikers, it's " + weather_data['temp_and_unit'] + " and " + weather_data['condition'].lower() + ".",
        "It is currently " + weather_data['condition'].lower() + " and " + weather_data['temp_and_unit'] + ".",
        "Big surprise, it's " + weather_data['condition'].lower() + " and " + weather_data['temp_and_unit'] + ".",
        "Look up, it's " + weather_data['condition'].lower() + " and " + weather_data['temp_and_unit'] + "."
    ]
    return random.choice(text)


def make_special_tweet(weather_data):
    if (weather_data['units']['temperature'] == 'F' and weather_data['wind_chill'] <= -30) or (weather_data['units']['temperature'] == 'C' and weather_data['wind_chill'] <= -34):
        return "Wow, mother nature hates us. The windchill is " + str(weather_data['wind_chill']) + weather_data['deg_unit'] + \
               " and the wind is blowing at " + weather_data['wind_speed_and_unit'] + " from the " + weather_data['wind_direction'] + ". My face hurts."
    elif weather_data['code'] == 23 or weather_data['code'] == 24:
        return "Looks like we've got some wind at " + weather_data['wind_speed_and_unit'] + " coming from the " + weather_data['wind_direction'] + "."
    elif weather_data['code'] == 0 or weather_data['code'] == 1 or weather_data['code'] == 2:
        return "HOLY SHIT, THERE'S A " + weather_data['condition'].upper() + "!"
    elif weather_data['code'] == 3:
        return "IT BE STORMIN'! Severe thunderstorms right now."
    elif weather_data['code'] == 4:
        return "Meh, just a thunderstorm."
    elif weather_data['code'] == 17 or weather_data['code'] == 35:
        return "IT'S HAILIN'!"
    elif weather_data['code'] == 20:
        return "Do you even fog bro?"
    elif weather_data['code'] == 5 or weather_data['code'] == 6 or weather_data['code'] == 7:
        return "What a mix! Currently, there's " + weather_data['condition'].lower() + " falling from the sky."
    elif weather_data['code'] == 13 or weather_data['code'] == 14 or weather_data['code'] == 15 or weather_data['code'] == 16 or weather_data['code'] == 41 or weather_data['code'] == 43:
        return weather_data['condition'].capitalize() + ". Bundle up."
    elif weather_data['code'] == 8 or weather_data['code'] == 9:
        return "Drizzlin' yo."
    elif (weather_data['units']['speed'] == 'mph' and weather_data['wind_speed'] >= 35.0) or (weather_data['units']['speed'] == 'km/h' and weather_data['wind_speed'] >= 56.0):
        return "Hold onto your hats, the wind is blowing at " + weather_data['wind_speed_and_unit'] + " coming from the " + weather_data['wind_direction'] + "."
    elif weather_data['humidity'] <= 5:
        return "It's dry as strained pasta. " + str(weather_data['humidity']) + "% humid right now."
    elif (weather_data['units']['temperature'] == 'F' and weather_data['temp'] <= -20) or (weather_data['units']['temperature'] == 'C' and weather_data['temp'] <= -28):
        return "It's " + weather_data['temp_and_unit'] + ". Too cold."
    elif (weather_data['units']['temperature'] == 'F' and weather_data['temp'] >= 100) or (weather_data['units']['temperature'] == 'C' and 37 <= weather_data['temp'] <= 50):
        return "Holy moly it's " + weather_data['temp_and_unit'] + ". I could literally (figuratively) melt."
    elif weather_data['units']['temperature'] == 'F' and weather_data['temp'] == 69:
        return "Teehee, it's 69" + weather_data['deg_unit'] + "."
    elif weather_data['code'] == 3200:
        return "Someone messed up, apparently the current condition is \"not available\" " + \
               "http://www.reactiongifs.com/wp-content/uploads/2013/08/air-quotes.gif"
    else:
        return "normal"  # keep normal as is determines if the weather is normal (boring) or special (exciting!)


def make_forecast(dt, weather_data):
    # Could use '%-d', but it does not work on all platforms (*cough *cough Windows *cough)
    date = dt.strftime('X%d %b %Y').replace('X0', '').replace('X', '')
    endings = ["Exciting!", "Nice!", "Sweet!", "Wow!", "I can't wait!", "Nifty!",
               "Excellent!", "What a day!", "This should be interesting!"]
    for day in weather_data['forecast']:
        if day['date'] == date:
            logging.debug('Found a forecast: %s', day)
            return "The forecast for today is " + day['text'].lower() + " with a high of " + day['high'] + \
                   weather_data['deg_unit'] + " and a low of " + day['low'] + weather_data['deg_unit'] + \
                   ". " + random.choice(endings)
    return "Sorry, today's forecast is \"not available\" " \
           "http://www.reactiongifs.com/wp-content/uploads/2013/08/air-quotes.gif Go yell at @bman4789"


def do_tweet(content, weather_data, tweet_location, variable_location):
    api = get_tweepy_api()
    content += HASHTAG
    logging.debug('Trying to tweet: %s', content)
    # Add the current city to tweet if variable location is enabled
    if variable_location:
        content = weather_data['city'] + ", " + weather_data['region'] + ": " + content
    try:
        if tweet_location:
            status = api.update_status(status=content, lat=weather_data['latitude'], long=weather_data['longitude'])
        else:
            status = api.update_status(status=content)
        logging.info('Tweet success: %s', content)
        return status
    except tweepy.TweepError as e:
        logging.error('Tweet failed: %s', e.reason)
        logging.warning('Tweet skipped due to error: %s', content)


def tweet_logic(weather_data):
    global last_special
    now = datetime.now()
    content_special = make_special_tweet(weather_data)
    content_normal = make_normal_tweet(weather_data)
    # Standard timed tweet
    timed_tweet(now.replace(hour=6, minute=0, second=0, microsecond=0), now, make_forecast(now, weather_data), weather_data)
    timed_tweet(now.replace(hour=7, minute=0, second=0, microsecond=0), now, content_normal, weather_data)
    timed_tweet(now.replace(hour=12, minute=0, second=0, microsecond=0), now, content_normal, weather_data)
    timed_tweet(now.replace(hour=15, minute=0, second=0, microsecond=0), now, content_normal, weather_data)
    timed_tweet(now.replace(hour=18, minute=0, second=0, microsecond=0), now, content_normal, weather_data)
    timed_tweet(now.replace(hour=22, minute=0, second=0, microsecond=0), now, content_normal, weather_data)
    if content_special != "normal" and now > last_special + timedelta(minutes=30):
        # Post special weather event at any time. Do not tweet more than one special event every 30 minutes
        logging.debug("Special event")
        do_tweet(content_special, weather_data, TWEET_LOCATION, VARIABLE_LOCATION)
        last_special = now


def timed_tweet(tweet_at, now, content, weather_data):
    if tweet_at <= now < tweet_at + timedelta(minutes=1):
        logging.debug("Timed tweet or forecast")
        do_tweet(content, weather_data, TWEET_LOCATION, VARIABLE_LOCATION)


def main():
    initialize_logger(LOG_PATHNAME)
    set_twitter_env_vars()
    if VARIABLE_LOCATION:
        set_flickr_env_vars()
    updated_time = datetime.now()
    woeid = WOEID
    while True:
        # check for new location every 30 minutes
        if VARIABLE_LOCATION and updated_time + timedelta(minutes=30) > datetime.now():
            woeid = get_woeid_from_variable_location(woeid, USER_FOR_LOCATION)
        weather_data = get_weather_variables(get_weather(woeid, UNIT))
        if weather_data['valid'] is True:
            tweet_logic(weather_data)
        time.sleep(60)


def run():
    try:
        main()
    except Exception as err:
        logging.error(err)
        logging.error('We got an exception!', exc_info=True)

if __name__ == '__main__':
    if "-d" in sys.argv:
        with daemon.DaemonContext():
            run()
    else:
        run()
