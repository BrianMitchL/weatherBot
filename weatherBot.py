#!/usr/bin/env python
# -*- coding: utf-8 -*-

# weatherBot
# Copyright 2015 Brian Mitchell under the MIT license
# See the GitHub repository: https://github.com/bman4789/weatherBot

from datetime import datetime
import sys
import time
import random
import logging
import json
import os
from os.path import expanduser
import tweepy
import daemon
from keys import set_env_vars
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

# Global variables
last_tweet = ""
deg = "º "
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


def get_weather():
    ybaseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = "select * from weather.forecast where woeid=" + WOEID + " and u=\"" + UNIT + "\""
    yql_url = ybaseurl + urlencode({'q': yql_query}) + "&format=json"
    try:
        yresult = urlopen(yql_url).read()
        if sys.version < '3':
            return json.loads(yresult)
        else:
            return json.loads(yresult.decode('utf8'))
    except (URLError, IOError) as err:
        logging.error('Tried to load: %s', yql_url)
        logging.error(err)


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


def do_tweet(content, weather_data):
    global last_tweet
    auth = tweepy.OAuthHandler(os.environ.get('WEATHERBOT_CONSUMER_KEY'), os.environ.get('WEATHERBOT_CONSUMER_SECRET'))
    auth.set_access_token(os.environ.get('WEATHERBOT_ACCESS_KEY'), os.environ.get('WEATHERBOT_ACCESS_SECRET'))
    api = tweepy.API(auth)
    logging.debug('Trying to tweet: %s', content)
    try:
        if TWEET_LOCATION:
            status = api.update_status(status=content, lat=weather_data['latitude'], long=weather_data['longitude'])
        else:
            status = api.update_status(status=content)
        logging.info('Tweet success: %s', content)
        last_tweet = content
        return status
    except tweepy.TweepError as e:
        logging.error('Tweet failed: %s', e.reason)
        logging.warning('Tweet skipped due to error: %s', content)


def tweet_logic(weather_data):
    now = datetime.now()
    content_special = make_special_tweet(weather_data)
    content_normal = make_normal_tweet(weather_data)
    logging.debug('last tweet: %s', last_tweet)
    logging.debug('special tweet: %s', content_special)
    logging.debug('normal tweet: %s', content_normal)
    if last_tweet == content_normal:
        # Posting tweet will fail if same as last tweet
        logging.debug('Duplicate normal tweet: %s', content_normal)
    elif last_tweet == content_special:
        # Posting tweet will fail if same as last tweet
        logging.debug('Duplicate special tweet: %s', content_special)
    elif content_special != "normal":
        # Post special weather event at non-timed time
        logging.debug('special event')
        do_tweet(content_special, weather_data)
        time.sleep(840)
        # Sleep for 14 minutes (plus the 1 minute at the end of the loop) to limit high numbers of similar tweets
    else:
        # Standard timed tweet
        timed_tweet(now.replace(hour=7, minute=0, second=0, microsecond=0), now, content_normal, weather_data)
        timed_tweet(now.replace(hour=12, minute=0, second=0, microsecond=0), now, content_normal, weather_data)
        timed_tweet(now.replace(hour=15, minute=0, second=0, microsecond=0), now, content_normal, weather_data)
        timed_tweet(now.replace(hour=18, minute=0, second=0, microsecond=0), now, content_normal, weather_data)
        timed_tweet(now.replace(hour=22, minute=0, second=0, microsecond=0), now, content_normal, weather_data)


def timed_tweet(time, now, content_normal, weather_data):
    if time <= now < time.replace(minute=time.minute + 1):
        do_tweet(content_normal, weather_data)


def main():
    initialize_logger(LOG_PATHNAME)
    if os.environ.get('WEATHERBOT_CONSUMER_KEY') is 'None' \
            or os.environ.get('WEATHERBOT_CONSUMER_SECRET') is 'None' \
            or os.environ.get('WEATHERBOT_ACCESS_KEY') is 'None' \
            or os.environ.get('WEATHERBOT_ACCESS_SECRET') is 'None':
        set_env_vars()  # set keys and secrets if not in env variables
    while True:
        weather_data = get_weather_variables(get_weather())
        if weather_data['valid'] is True:
            tweet_logic(weather_data)
            do_tweet('testing', weather_data)
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
