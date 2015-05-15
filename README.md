# weatherBot [![Python Version](https://img.shields.io/badge/python-2.7%2C%203.3%2C%203.4-blue.svg)](https://www.python.org) [![Build Status](https://travis-ci.org/bman4789/weatherBot.svg?branch=master)](https://travis-ci.org/bman4789/weatherBot) [![Coverage Status](https://coveralls.io/repos/bman4789/weatherBot/badge.svg?branch=master)](https://coveralls.io/r/bman4789/weatherBot?branch=master)
A Twitter bot for weather. Yahoo! Weather is used for weather information. A WOEID is used for the location. Metric or imperial units can be specified.

_**Note: Any language or wording suggestions are appreciated and should be submitted as an issue. Feel free to add new choices for normal tweets and submit a pull request!**_

An example bot can be found at [@MorrisMNWeather](https://twitter.com/MorrisMNWeather).

weatherBot can tweet the current weather condition and temperature at scheduled times. If a special weather event is happening, it will tweet that (outside of the scheduled times). weatherBot can also tweet the current day's forecasted condition, and high and low temperature.

## Features
* Daily current conditions at scheduled times
* Daily forecast at a scheduled time
* Special weather event tweets that go out as soon as a "special" weather condition happens
* Limiting how often the special event tweets are tweeted
* Variable location for all tweets based on the locations in a user's recent tweets
* Metric or imperial units
* Geo location in each tweet
* Python 2.7, 3.3, or 3.4 (see below for more)
* Logs to the console and a file
* Can be run as a daemon
* Weather data from Yahoo! Weather

## Install Dependencies
Run the following from the repository root directory to install the needed dependencies. If pip (or pip3 if python 3) is not installed, install it via easy_install.
```shell
pip install -r requirements.txt
```

## Use
weatherBot.py has been tested for Python 2.7 (tested with 2.7.6 and 2.7.9) and Python 3 (tested with 3.4.3). Python 3.3 should work, but 3.2 will NOT. If you are using Python 2, version 2.7.9 is highly recommended in order to use the new SSL libraries that don't throw warnings..

There are two modes in weatherBot. One is running from a console, and the other is by forking the process into a daemon. By default, the debug level is logged to the console and the info level is logged to the log file. The idea with this is that you run the script from the console to test and debug, and daemonize it to run it in "production." To run from as a daemon, pass in the `-d` flag:
```shell
python weatherBot.py -d
```
If you wish to run it in a console, just run normally:
```shell
python weatherBot.py
```

## Setting Variables and Customizing
There is a constants section near the top of the weatherBot.py file where you can set constants. The following are constants that can be set in the weatherBot.py file
* `WOEID` *defaults to 2454256 (Morris, MN)*
* `UNIT` *defaults to imperial. 'c' for metric, 'f' for imperial. This changes all units, not just temperature*
* `TWEET_LOCATION` *defaults to true*
* `LOG_PATHNAME` *defaults to '~/weatherBot.log'* **Note: The complete path name needs to be specified**
* `HASHTAG` *defaults to " #MorrisWeather". This is a string that will be added to the end of every tweet. If no hashtag or end text is desired, simply set the variable to be an empty string*
* `VARIABLE_LOCATION` *defaults to false* **See Variable Location for more**
* `USER_FOR_LOCATION` *defaults to bman4789*


The Twitter app consumer key and secret as well as the access token key and secret are located either in environmental variables or in the keys.py file. The script will pull in the keys from the environmental variables over the keys.py file. See https://apps.twitter.com to get your keys and secrets.
They names of the environmental variables are as follows: `WEATHERBOT_CONSUMER_KEY`, `WEATHERBOT_CONSUMER_SECRET`, `WEATHERBOT_ACCESS_KEY`, `WEATHERBOT_ACCESS_SECRET`, and `WEATHERBOT_FLICKR_KEY`. Entering keys into keys.py is not required if you have entered them as environmental variables. `WEATHERBOT_FLICKR_KEY` is not needed if variable location is not used.

The wording for tweets can be edited or added in the text list in `make_normal_tweet()`, `make_forecast()`, and the appropriate returns in `make_special_tweet()`. Additional special weather events can also be added as extra elif's in `make_special_tweet()`. Mind the order so more or less common ones are called when not desired.

Timing of daily scheduled current conditions and forecasts are done by setting the hour and minute in last few lines of the `timed_tweet()` method.

**Note: the times entered here are triggered by the host's time as returned by datetime. If the host machine and weather location do not match, but sure to set accordingly here.**

### Variable Location
Enable `VARIABLE_LOCATION` to have the location for weather change. The Twitter username stored in the `USER_FOR_LOCATION` constant will be used to determine this location. The specified user must tweet with location fairly regularly (at least every 20 tweets), or the manually entered location will be used. The most recent tweet with a location will be used to get the location for weather.
For example, say the given user tweets from Minneapolis, MN one day. Minneapolis will be used as the location indefinitely until a new tweet with location is posted (or that tweet is deleted, and the next newest location will be used).
In addition to the location changing, the city or neighborhood (if specific coordinates and a large enough city) and region will be added to the beginning of each tweet. For example, in the same case as earlier, "Minneapolis, MN: " would be prefixed to every tweet.

## Testing
Tests have been written for a fair amount of the code. It's hard (or I don't know how) to test tweeting and fetching weather data, so that somewhat limits what tests can be written. The JSON object that Yahoo! Weather returns is hardcoded for each test with values that would make it qualify for a given condition. Note: to make tweeting tests pass, the consumer and secret keys/tokens need to be stored as an environmental variable.
```shell
python test.py
```

## Deploying to [Heroku](https://www.heroku.com/)
weatherBot can easily be deployed to Heroku. Install the heroku-toolbelt and run the following to get started:
```shell
heroku login
heroku create
git push heroku master
```
You will need to also set the appropriate timezone of the server. For example,
```shell
heroku config:add TZ="America/Chicago"
```
To see  more timezone formats, go [here](http://en.wikipedia.org/wiki/List_of_tz_database_time_zones).
Furthermore, the twitter keys need to be added. The format to do so is:
```shell
heroku config:set WEATHERBOT_CONSUMER_KEY=xxxxx WEATHERBOT_CONSUMER_SECRET=xxxxx WEATHERBOT_ACCESS_KEY=xxxxx WEATHERBOT_ACCESS_SECRET=xxxxx WEATHERBOT_FLICKR_KEY=xxxxx
```

## Tools Used
* [Tweepy](https://github.com/tweepy/tweepy)
* [Yahoo! Weather API](https://developer.yahoo.com/weather/)
* [Flickr API](https://www.flickr.com/services/api/)
* [Yahoo Query Language](https://developer.yahoo.com/yql)
* [Python Daemon](https://pypi.python.org/pypi/python-daemon/)