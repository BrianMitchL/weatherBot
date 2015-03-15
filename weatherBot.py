#!/usr/bin/env python
# -*- coding: utf-8 -*-

#weatherBot
#Copyright 2015 Brian Mitchell under the MIT license
#See the GitHub repository: https://github.com/bman4789/weatherBot

from datetime import datetime
import sys, time, random, logging, urllib2, urllib, json
import tweepy, daemon
from keys import keys

#Contants
WOEID = '2454256' #Yahoo! Weather location ID

CONSUMER_KEY = keys['consumer_key']
CONSUMER_SECRET = keys['consumer_secret']
ACCESS_KEY = keys['access_key']
ACCESS_SECRET = keys['access_secret']

#global variables
last_tweet = ""

#Grr unicode support in Python 2
deg = "ºF"
deg = deg.decode('utf-8')

logging.basicConfig(filename='weatherBot.log', level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
#log to console
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
#formatting for console log
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

logger = logging.getLogger(__name__)
logging.info("Starting weatherBot")

def getWeather():
    ybaseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = "select * from weather.forecast where woeid=" + WOEID
    yql_url = ybaseurl + urllib.urlencode({'q':yql_query}) + "&format=json"
    yresult = urllib2.urlopen(yql_url).read()
    return json.loads(yresult)

def makeNormalTweet(ydata):
    temp = ydata['query']['results']['channel']['item']['condition']['temp'] + deg
    condition = ydata['query']['results']['channel']['item']['condition']['text']
    
    #List of possible tweets that will be used. A random one will be chosen every time.
    text = ["The weather is fucking boring. " + temp + " and " + condition + ".",
    "Great, it's fucking " + condition + " and " + temp + ".",
    "What a normal fucking day, it's " + condition + " and " + temp + "."]
    
    return random.choice(text)

def makeSpecialTweet(ydata):
    windchill = int(ydata['query']['results']['channel']['wind']['chill'])
    windspeed = int(ydata['query']['results']['channel']['wind']['speed'])
    humidity = int(ydata['query']['results']['channel']['atmosphere']['humidity'])
    temp = int(ydata['query']['results']['channel']['item']['condition']['temp'])
    code = int(ydata['query']['results']['channel']['item']['condition']['code'])
    condition = ydata['query']['results']['channel']['item']['condition']['text']
    
    if (windchill <= -30):
        return "Wow, mother nature is a bitch. The windchill is " + str(windchill) + deg + " and the wind is blowing at " + windspeed + " mph. My face hurts."
    elif (code == 0 or code == 1 or code == 2):
        return "HOLY SHIT, THERE'S A " + condition.upper() + "!"
    elif (code == 3):
        return "Guys, there are severe fucking thunderstorms right now."
    elif (code == 4):
        return "Meh, just a thunderstorm."
    elif (code == 17 or code == 35):
        return "IT'S FUCKIN' HAILIN'!"
    elif (code == 20):
        return "Do you even fog bro?"
    elif (code == 13 or code == 15 or code == 16 or code == 41 or code == 43):
        return condition.capitalize() + "."
    elif (code == 8 or code == 9):
        return "Drizzlin' yo."
    elif (humidity == 100 and (code != 10 or code != 11 or code != 12 or code != 37 or code != 38 or code != 39 or code != 40 or code != 45 or code != 47)):
        return "Damn, it's 100% humid. Glad I'm not a toilet so water doesn't condense on me."
    elif (humidity < 5):
        return "It's dry as fuck. " + str(humidity) + "% humid right now."
    elif (temp <= -20):
        return "It's fucking " + str(temp) + deg + ". Too fucking cold."
    elif (temp >= 100):
        return "Holy fuck it's " + str(temp) + deg + ". I could literally (figuratively) melt."
    elif (temp == 69):
        return "Teehee, it's 69" + deg + "."
    elif (code == 3200):
        return "Someone fucked up, apparently the current condition is \"not available\" http://www.reactiongifs.com/wp-content/uploads/2013/08/air-quotes.gif"
    else:
        return "normal"

def doTweet(content, latitude, longitude):
    global last_tweet
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)
    
    logging.debug('Trying to tweet: ' + content)
    try:
        api.update_status(status=content,lat=latitude,long=longitude)
        logging.info('Tweet success: ' + content)
    except tweepy.TweepError, e:
        logging.warning('Tweet failed: ' + e.reason)
    last_tweet = content

def main():
    count = 1
    while(True):
        logging.debug('loop ' + str(count))
        
        ydata = getWeather()
        contentSpecial = makeSpecialTweet(ydata)
        contentNormal = makeNormalTweet(ydata)
        latitude = ydata['query']['results']['channel']['item']['lat']
        longitude = ydata['query']['results']['channel']['item']['long']
        
        logging.debug('last tweet: ' + last_tweet)
        
        if (last_tweet == contentNormal):
            #posting tweet will fail if same as last tweet
            logging.debug('Duplicate normal tweet: ' + contentNormal)
        elif (last_tweet == contentSpecial):
            #posting tweet will fail if same as last tweet
            logging.debug('Duplicate special tweet: ' + contentSpecial)
        elif (contentSpecial != "normal"):
            #post special weather event at non-timed time
            logging.debug('special event')
            doTweet(contentSpecial, latitude, longitude)
            time.sleep(840) #sleep for 14 mins (plus the 1 minute at the end of the loop) so there aren't a ton of similar tweets in a row
        else:
            #standard timed tweet
            now = datetime.now()
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