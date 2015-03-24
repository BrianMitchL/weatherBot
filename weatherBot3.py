#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#weatherBot
#Copyright 2015 Brian Mitchell under the MIT license
#See the GitHub repository: https://github.com/bman4789/weatherBot

from datetime import datetime
import sys, time, random, logging, urllib.request, urllib.error, urllib.parse, urllib.request, urllib.parse, urllib.error, json
from os.path import expanduser
import tweepy, daemon
from keys import keys

#Contants
WOEID = '2454256' #Yahoo! Weather location ID
TWEET_LOCATION = True #include location in tweet
LOG_PATHNAME = expanduser("~") + '/weatherBot.log' #expanduser("~") returns the path to the current user's home dir

CONSUMER_KEY = keys['consumer_key']
CONSUMER_SECRET = keys['consumer_secret']
ACCESS_KEY = keys['access_key']
ACCESS_SECRET = keys['access_secret']

#global variables
last_tweet = ""

def initialize_logger(log_pathname):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG) #global level of debug, so debug or anything less can be used
    
    #console handler
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)
    
    #log file handler
    log = logging.FileHandler(log_pathname, "a", encoding=None, delay="true") #delay="true" means file will not be created until logged to
    log.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    log.setFormatter(formatter)
    logger.addHandler(log)
    logger.info("Starting weatherBot with Python %s", sys.version)

def getWeather():
    ybaseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = "select * from weather.forecast where woeid=" + WOEID
    yql_url = ybaseurl + urllib.parse.urlencode({'q':yql_query}) + "&format=json"
    yresult = urllib.request.urlopen(yql_url).read()
    return json.loads(yresult.decode('utf8'))

def makeNormalTweet(ydata):
    temp = ydata['query']['results']['channel']['item']['condition']['temp'] + "ºF"
    condition = ydata['query']['results']['channel']['item']['condition']['text']
    city = ydata['query']['results']['channel']['location']['city']
    region = ydata['query']['results']['channel']['location']['region']
    
    #List of possible tweets that will be used. A random one will be chosen every time.
    text = [
        "The weather is boring. " + temp + " and " + condition.lower() + ".",
        "Great, it's " + condition.lower() + " and " + temp + ".",
        "What a normal day, it's " + condition.lower() + " and " + temp + ".",
        "Whoopie do, it's " + temp + " and " + condition.lower() + ".",
        temp + " and " + condition.lower() + ".",
        temp + " and " + condition.lower() + ". What did you expect?",
        "Welcome to " + city + ", " + region + ", where it's " + condition.lower() + " and " + temp + ".",
        "Breaking news: it's " + condition.lower() + " and " + temp + ".",
        "We got some " + condition.lower() + " at " + temp + " going on.",
    ]
    
    return random.choice(text)

def makeSpecialTweet(ydata, now):
    windchill = int(ydata['query']['results']['channel']['wind']['chill'])
    windspeed = int(ydata['query']['results']['channel']['wind']['speed'])
    humidity = int(ydata['query']['results']['channel']['atmosphere']['humidity'])
    temp = int(ydata['query']['results']['channel']['item']['condition']['temp'])
    code = int(ydata['query']['results']['channel']['item']['condition']['code'])
    condition = ydata['query']['results']['channel']['item']['condition']['text']
    
    if (windchill <= -30):
        return "Wow, mother nature hates us. The windchill is " + str(windchill) + "ºF and the wind is blowing at " + windspeed + " mph. My face hurts."
    elif (code == 23 or code == 24):
        return "Looks like we've got some wind at " + windspeed + " mph."
    elif (code == 0 or code == 1 or code == 2):
        return "HOLY SHIT, THERE'S A " + condition.upper() + "!"
    elif (code == 3):
        return "IT BE STORMIN'! Severe thunderstorms right now."
    elif (code == 4):
        return "Meh, just a thunderstorm."
    elif (code == 17 or code == 35):
        return "IT'S HAILIN'!"
    elif (code == 20):
        return "Do you even fog bro?"
    elif (code == 5 or code == 6 or code == 7):
        return "What a mix! Currently, there's " + condition.lower() + " falling from the sky."
    elif (code == 13 or code == 14 or code == 15 or code == 16 or code == 41 or code == 43):
        return condition.capitalize() + ". Bundle up."
    elif (code == 8 or code == 9):
        return "Drizzlin' yo."
    elif (humidity == 100 and (code != 10 or code != 11 or code != 12 or code != 37 or code != 38 or code != 39 or code != 40 or code != 45 or code != 47) and (now.replace(hour=9, minute=0, second=0, microsecond=0) < now) and (now.replace(hour=11, minute=59, second=59, microsecond=0) > now)):
        return "Damn, it's 100% humid. Glad I'm not a toilet so water doesn't condense on me."
    elif (humidity < 5):
        return "It's dry as strained pasta. " + str(humidity) + "% humid right now."
    elif (temp <= -20):
        return "It's " + str(temp) + "ºF. Too cold."
    elif (temp >= 100):
        return "Holy moly it's " + str(temp) + "ºF. I could literally (figuratively) melt."
    elif (temp == 69):
        return "Teehee, it's 69ºF."
    elif (code == 3200):
        return "Someone messed up, apparently the current condition is \"not available\" http://www.reactiongifs.com/wp-content/uploads/2013/08/air-quotes.gif"
    else:
        return "normal" #keep normal as is determines if the weather is normal (boring) or special (exciting!)

def doTweet(content, latitude, longitude):
    global last_tweet
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)
    
    logging.debug('Trying to tweet: %s', content)
    try:
        api.update_status(status=content,lat=latitude,long=longitude) if TWEET_LOCATION else api.update_status(status=content)
        logging.info('Tweet success: %s', content)
        last_tweet = content
    except tweepy.TweepError as e:
        logging.error('Tweet failed: %s', e.reason)
        logging.warning('Tweet skipped due to error: %s', content)

def main():
    initialize_logger(LOG_PATHNAME)
    count = 1
    while(True):
        logging.debug('loop %s', str(count))
        
        ydata = getWeather()
        now = datetime.now()
        
        contentSpecial = makeSpecialTweet(ydata, now)
        contentNormal = makeNormalTweet(ydata)
        latitude = ydata['query']['results']['channel']['item']['lat']
        longitude = ydata['query']['results']['channel']['item']['long']
        
        logging.debug('last tweet: %s', last_tweet)
        
        if (last_tweet == contentNormal):
            #posting tweet will fail if same as last tweet
            logging.debug('Duplicate normal tweet: %s', contentNormal)
        elif (last_tweet == contentSpecial):
            #posting tweet will fail if same as last tweet
            logging.debug('Duplicate special tweet: %s', contentSpecial)
        elif (contentSpecial != "normal"):
            #post special weather event at non-timed time
            logging.debug('special event')
            doTweet(contentSpecial, latitude, longitude)
            time.sleep(840) #sleep for 14 mins (plus the 1 minute at the end of the loop) so there aren't a ton of similar tweets in a row
        else:
            #standard timed tweet
            time1 = now.replace(hour=7, minute=0, second=0, microsecond=0) #the time of the first tweet to go out
            time2 = now.replace(hour=12, minute=0, second=0, microsecond=0)
            time3 = now.replace(hour=15, minute=0, second=0, microsecond=0)
            time4 = now.replace(hour=18, minute=0, second=0, microsecond=0)
            time5 = now.replace(hour=22, minute=0, second=0, microsecond=0)
            
            if (now > time5 and now < time5.replace(minute=time5.minute + 1)):
                logging.debug('time5')
                doTweet(contentNormal, latitude, longitude)
            elif (now > time4 and now < time4.replace(minute=time4.minute + 1)):
                logging.debug('time4')
                doTweet(contentNormal, latitude, longitude)
            elif (now > time3 and now < time3.replace(minute=time3.minute + 1)):
                logging.debug('time3')
                doTweet(contentNormal, latitude, longitude)
            elif (now > time2 and now < time2.replace(minute=time2.minute + 1)):
                logging.debug('time2')
                doTweet(contentNormal, latitude, longitude)
            elif (now > time1 and now < time1.replace(minute=time1.minute + 1)):
                logging.debug('time1')
                doTweet(contentNormal, latitude, longitude)
        
        time.sleep(60)
        count = count + 1    

if __name__ == '__main__':
    if "-d" in sys.argv:
        with daemon.DaemonContext():
            main()
    else:
        main()
