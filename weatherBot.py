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
from os.path import expanduser
import tweepy
import daemon
from keys import keys
# Python 2 and 3 compatibility for urllib stuff
try:
    from urllib.request import urlopen
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
    from urllib import urlopen



# Constants
WOEID = '2454256'  # Yahoo! Weather location ID
UNIT = 'f'  # units. 'c' for metric, 'f' for imperial. This changes all units, not just temperature
TWEET_LOCATION = True  # include location in tweet
LOG_PATHNAME = expanduser("~") + '/weatherBot.log'  # expanduser("~") returns the path to the current user's home dir

CONSUMER_KEY = keys['consumer_key']
CONSUMER_SECRET = keys['consumer_secret']
ACCESS_KEY = keys['access_key']
ACCESS_SECRET = keys['access_secret']

# Global variables
last_tweet = ""
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


def get_weather():
    ybaseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = "select * from weather.forecast where woeid=" + WOEID + " and u=\"" + UNIT + "\""
    yql_url = ybaseurl + urlencode({'q':yql_query}) + "&format=json"
    yresult = urlopen(yql_url).read()
    if sys.version < '3':
        return json.loads(yresult)
    else:
        return json.loads(yresult.decode('utf8'))


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
    global wind_speed, wind_direction, wind_chill, wind_speed_and_unit, humidity, temp, code, \
        condition, deg_unit, temp_and_unit, city, region, latitude, longitude, units
    units = ydata['query']['results']['channel']['units']
    # Sometimes, YQL returns empty strings for wind speed and direction
    if ydata['query']['results']['channel']['wind']['speed'] != "":
        wind_speed = float(ydata['query']['results']['channel']['wind']['speed'])
        wind_speed_and_unit = ydata['query']['results']['channel']['wind']['speed'] + " " + units['speed']
    else:
        wind_speed = 0.0
        wind_speed_and_unit = "0 " + units['speed']
    if ydata['query']['results']['channel']['wind']['direction'] != "":
        wind_direction = get_wind_direction(int(ydata['query']['results']['channel']['wind']['direction']))
    else:
        wind_direction = get_wind_direction(0)
    wind_chill = int(ydata['query']['results']['channel']['wind']['chill'])
    humidity = int(ydata['query']['results']['channel']['atmosphere']['humidity'])
    temp = int(ydata['query']['results']['channel']['item']['condition']['temp'])
    code = int(ydata['query']['results']['channel']['item']['condition']['code'])
    condition = ydata['query']['results']['channel']['item']['condition']['text']
    deg_unit = deg + units['temperature']
    temp_and_unit = ydata['query']['results']['channel']['item']['condition']['temp'] + deg + units['temperature']
    city = ydata['query']['results']['channel']['location']['city']
    region = ydata['query']['results']['channel']['location']['region']
    latitude = ydata['query']['results']['channel']['item']['lat']
    longitude = ydata['query']['results']['channel']['item']['long']


def make_normal_tweet():
    text = [
        "The weather is boring. " + temp_and_unit + " and " + condition.lower() + ".",
        "Great, it's " + condition.lower() + " and " + temp_and_unit + ".",
        "What a normal day, it's " + condition.lower() + " and " + temp_and_unit + ".",
        "Whoopie do, it's " + temp_and_unit + " and " + condition.lower() + ".",
        temp_and_unit + " and " + condition.lower() + ".",
        temp_and_unit + " and " + condition.lower() + ". What did you expect?",
        "Welcome to " + city + ", " + region + ", where it's " + condition.lower() + " and " + temp_and_unit + ".",
        "Breaking news: it's " + condition.lower() + " and " + temp_and_unit + ".",
        "We got some " + condition.lower() + " at " + temp_and_unit + " going on.",
    ]
    return random.choice(text)


def make_special_tweet():
    if (units['temperature'] == 'F' and wind_chill <= -30) or (units['temperature'] == 'C' and wind_chill <= -34):
        return "Wow, mother nature hates us. The windchill is " + str(wind_chill) + deg_unit + \
               " and the wind is blowing at " + wind_speed_and_unit + " from the " + wind_direction + ". My face hurts."
    elif code == 23 or code == 24:
        return "Looks like we've got some wind at " + wind_speed_and_unit + " coming from the " + wind_direction + "."
    elif code == 0 or code == 1 or code == 2:
        return "HOLY SHIT, THERE'S A " + condition.upper() + "!"
    elif code == 3:
        return "IT BE STORMIN'! Severe thunderstorms right now."
    elif code == 4:
        return "Meh, just a thunderstorm."
    elif code == 17 or code == 35:
        return "IT'S HAILIN'!"
    elif code == 20:
        return "Do you even fog bro?"
    elif code == 5 or code == 6 or code == 7:
        return "What a mix! Currently, there's " + condition.lower() + " falling from the sky."
    elif code == 13 or code == 14 or code == 15 or code == 16 or code == 41 or code == 43:
        return condition.capitalize() + ". Bundle up."
    elif code == 8 or code == 9:
        return "Drizzlin' yo."
    elif (units['speed'] == 'mph' and wind_speed >= 35.0) or (units['speed'] == 'km/h' and wind_speed >= 56.0):
        return "Hold onto your hats, the wind is blowing at " + wind_speed_and_unit + " coming from the " + wind_direction + "."
    elif humidity <= 5:
        return "It's dry as strained pasta. " + str(humidity) + "% humid right now."
    elif (units['temperature'] == 'F' and temp <= -20) or (units['temperature'] == 'C' and temp <= -28):
        return "It's " + temp_and_unit + ". Too cold."
    elif (units['temperature'] == 'F' and temp >= 100) or (units['temperature'] == 'C' and 37 <= temp <= 50):
        return "Holy moly it's " + temp_and_unit + ". I could literally (figuratively) melt."
    elif units['temperature'] == 'F' and temp == 69:
        return "Teehee, it's 69" + deg_unit + "."
    elif code == 3200:
        return "Someone messed up, apparently the current condition is \"not available\" " + \
               "http://www.reactiongifs.com/wp-content/uploads/2013/08/air-quotes.gif"
    else:
        return "normal"  # keep normal as is determines if the weather is normal (boring) or special (exciting!)


def do_tweet(content):
    global last_tweet
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)
    logging.debug('Trying to tweet: %s', content)
    try:
        api.update_status(status=content, lat=latitude, long=longitude) if TWEET_LOCATION else \
            api.update_status(status=content)
        logging.info('Tweet success: %s', content)
        last_tweet = content
    except tweepy.TweepError as e:
        logging.error('Tweet failed: %s', e.reason)
        logging.warning('Tweet skipped due to error: %s', content)


def main():
    initialize_logger(LOG_PATHNAME)
    count = 1
    while True:
        logging.debug('loop %s', str(count))
        ydata = get_weather()
        logging.debug('fetched weather: %s', ydata)
        # sometimes YQL returns 'None' as the results, huh
        if ydata['query']['results'] == "None":
            logging.error('YQL error, received: %s', ydata)
        else:
            get_weather_variables(ydata)
            now = datetime.now()
            content_special = make_special_tweet()
            content_normal = make_normal_tweet()
            logging.debug('last tweet: %s', last_tweet)
            logging.debug('special tweet: %s', content_special)
            logging.debug('normal_tweet: %s', content_normal)
            if last_tweet == content_normal:
                # Posting tweet will fail if same as last tweet
                logging.debug('Duplicate normal tweet: %s', content_normal)
            elif last_tweet == content_special:
                # Posting tweet will fail if same as last tweet
                logging.debug('Duplicate special tweet: %s', content_special)
            elif content_special != "normal":
                # Post special weather event at non-timed time
                logging.debug('special event')
                do_tweet(content_special)
                time.sleep(840)
                # Sleep for 14 minutes (plus the 1 minute at the end of the loop) to limit high numbers of similar tweets
            else:
                # Standard timed tweet
                time1 = now.replace(hour=7, minute=0, second=0, microsecond=0)  # the time of the first tweet to go out
                time2 = now.replace(hour=12, minute=0, second=0, microsecond=0)
                time3 = now.replace(hour=15, minute=0, second=0, microsecond=0)
                time4 = now.replace(hour=18, minute=0, second=0, microsecond=0)
                time5 = now.replace(hour=22, minute=0, second=0, microsecond=0)
                if time5 <= now < time5.replace(minute=time5.minute + 1):
                    logging.debug('time5')
                    do_tweet(content_normal)
                elif time4 <= now < time4.replace(minute=time4.minute + 1):
                    logging.debug('time4')
                    do_tweet(content_normal)
                elif time3 <= now < time3.replace(minute=time3.minute + 1):
                    logging.debug('time3')
                    do_tweet(content_normal)
                elif time2 <= now < time2.replace(minute=time2.minute + 1):
                    logging.debug('time2')
                    do_tweet(content_normal)
                elif time1 <= now < time1.replace(minute=time1.minute + 1):
                    logging.debug('time1')
                    do_tweet(content_normal)
        time.sleep(60)
        count += 1


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
