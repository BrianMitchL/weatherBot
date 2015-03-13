#!/usr/bin/env python
# -*- coding: utf-8 -*-

#weatherBot
#Copyright 2015 Brian Mitchell under the MIT license
#See the GitHub repository: https://github.com/bman4789/weatherBot

import tweepy, urllib2, urllib, json

#Contants
CONSUMER_KEY = '...' #Twitter app consumer key
CONSUMER_SECRET = '...' #twitter app consumer secret
ACCESS_KEY = '...' #twitter app user access key
ACCESS_SECRET = '...' #twitter app user access secret
WOEID = '2454256' #Yahoo location ID used for the weather location


auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

#Grr unicode support in Python 2
deg = "º"
deg = deg.decode('utf-8')

def getWeather():
    ybaseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = "select * from weather.forecast where woeid=" + WOEID
    yql_url = ybaseurl + urllib.urlencode({'q':yql_query}) + "&format=json"
    yresult = urllib2.urlopen(yql_url).read()
    return json.loads(yresult)
    
def makeTweet():
    ydata = getWeather()
    windchill = int(ydata['query']['results']['channel']['wind']['chill'])
    windspeed = int(ydata['query']['results']['channel']['wind']['speed'])
    humidity = int(ydata['query']['results']['channel']['atmosphere']['humidity'])
    temp = int(ydata['query']['results']['channel']['item']['condition']['temp'])
    code = int(ydata['query']['results']['channel']['item']['condition']['code'])
    condition = ydata['query']['results']['channel']['item']['condition']['text']
    
    if (windchill <= -30):
        return "Wow, mother nature is a bitch. The windchill is " + str(windchill) + "F and the wind is blowing at " + windspeed + " mph. My face hurts."
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
    elif (temp <= -20):
        return "It's fucking " + str(temp) + deg + "F. Too fucking cold."
    elif (temp >= 100):
        return "Holy fuck it's " + str(temp) + deg + "F. I could literally (figuratively) melt."
    elif (temp == 69):
        return "Teehee, it's 69" + deg + "F."
    elif (code == 3200):
        return "Someone fucked up, apparently the current condition is \"not available\" http://www.reactiongifs.com/wp-content/uploads/2013/08/air-quotes.gif"
    else:
        return "The weather is fucking boring. " + str(temp) + deg + "F and " + condition + "."
        
# api.update_status(status=makeTweet())
print makeTweet()