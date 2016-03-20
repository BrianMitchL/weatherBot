# weatherBot [![Python Version](https://img.shields.io/badge/python-3.3+-blue.svg)](https://www.python.org) [![Build Status](https://travis-ci.org/bman4789/weatherBot.svg?branch=master)](https://travis-ci.org/bman4789/weatherBot) [![Coverage Status](https://coveralls.io/repos/bman4789/weatherBot/badge.svg?branch=master)](https://coveralls.io/r/bman4789/weatherBot?branch=master)
A Twitter bot for weather. Powered by [Forecast](https://forecast.io)

_**Note: Any language or wording suggestions are appreciated and should be submitted as an issue. Feel free to add new choices for normal tweets and submit a pull request!**_

Example bots can be found at [@MorrisMNWeather](https://twitter.com/MorrisMNWeather) and [@WeatherByBrian](https://twitter.com/WeatherByBrian).

weatherBot can tweet the current weather condition and temperature at scheduled times. If a special weather event is happening, it will tweet that (outside of the scheduled times). weatherBot can also tweet the current day's forecasted condition, and high and low temperature.

## Features
* Daily current conditions at scheduled times
* Daily forecast at a scheduled time
* Severe weather alerts issued by a governmental authority
* Special weather event tweets that go out as soon as a "special" weather condition happens
* Limiting how often the special event tweets are tweeted (at a granular level)
* Variable location for all tweets based on the locations in a user's recent tweets
* Timezone support for localizing times to the timezone of the given or found location
* US, CA, UK, or SI units
* Geo location in each tweet
* Logs to the console and a file
* Can be run as a daemon
* Weather data from Forecast.io
* Python 3.3 or higher

## Install Dependencies
Run the following from the repository root directory to install the needed dependencies.
```shell
pip3 install -r requirements.txt
```

## Use
weatherBot.py has been built for Python 3 (tested with 3.3 and above). Legacy Python is not supported. 

There are two modes in weatherBot. One is running from a console, and the other is by forking the process into a daemon. By default, the debug level is logged to the console and the info level is logged to the log file. The idea with this is that you run the script from the console to test and debug, and daemonize it to run it in "production." To run it as a daemon, pass in the `-d` flag:
```shell
python3 weatherBot.py -d
```
If you wish to run it in a console, just run normally:
```shell
python3 weatherBot.py
```

## Setting Variables and Customizing
There is a constants section near the top of the weatherBot.py file where you can set constants. The following are constants that can be set in the weatherBot.py file
* `DM_ERRORS` *defaults to True. This will send a traceback of a crash in the form of a direct message to the authenticated twitter account*
* `DEFAULT_LOCATION` *defaults to `{'lat': 45.585, 'lon': -95.91, 'name': 'Morris, MN'}` Latitude, longitude, and human readable name of the location*
* `UNITS` *defaults to 'us'. Choose from 'us', 'ca', 'uk2', or 'si'*
* `TWEET_LOCATION` *defaults to True. boolean to include location embedded in each tweet*
* `HASHTAG` *defaults to " #MorrisWeather". This is a string that will be added to the end of every tweet. If no hashtag or end text is desired, simply set the variable to be an empty string*
* `VARIABLE_LOCATION` *defaults to false* **See Variable Location for more**
* `LOG_PATHNAME` *defaults to '~/weatherBot.log'* **Note: The complete path name needs to be specified**
* `USER_FOR_LOCATION` *defaults to bman4789. Twitter username for account to track location*
* `REFRESH_RATE` *defaults to 3. How often (in minutes) to check for new weather* **Note, watch out for API rate limiting and costs per call**
* `SPECIAL_EVENT_TIMES` *dictionary of times in minutes to throttle special events*


The Twitter app consumer key and secret as well as the access token key and secret are located either in environmental variables or in the keys.py file. The script will pull in the keys from the environmental variables over the keys.py file. See https://apps.twitter.com to get your keys and secrets.
They names of the environmental variables are as follows: `WEATHERBOT_CONSUMER_KEY`, `WEATHERBOT_CONSUMER_SECRET`, `WEATHERBOT_ACCESS_KEY`, `WEATHERBOT_ACCESS_SECRET`, and `WEATHERBOT_FORECASTIO_KEY`. Entering keys into keys.py is not required if you have entered them as environmental variables.

The wording for tweets can be edited or added in strings.py. Mind the order in `get_special_condition` so more or less common ones are called when not desired.

Timing of daily scheduled current conditions and forecasts are done by setting the hour and minute in last few lines of the `timed_tweet` method.

**Note: the times entered here are triggered by the host's time as returned by datetime. If the host machine and weather location do not match, but sure to set accordingly here.**

### Variable Location
Enable `VARIABLE_LOCATION` to have the location for weather change. The Twitter username stored in the `USER_FOR_LOCATION` constant will be used to determine this location. The specified user must tweet with location fairly regularly (at least every 20 tweets), or the manually entered location will be used. The most recent tweet with a location will be used to get the location for weather.
For example, say the given user tweets from Minneapolis, MN one day. Minneapolis will be used as the location indefinitely until a new tweet with location is posted (or that tweet is deleted, and the next newest location will be used).
In addition to the location changing, the human readable Twitter location will be added to the beginning of each tweet. For example, in the same case as earlier, "Minneapolis, MN: " would be prefixed to every tweet.

## Testing
Tests have been written for a fair amount of the code. It's hard (or I don't know how) to test tweeting and fetching weather data, so that somewhat limits what tests can be written. Note: to make tweeting tests pass, the consumer and secret keys/tokens need to be stored as an environmental variable.
```shell
python3 test.py
```

## Deploying to [Heroku](https://www.heroku.com/)
weatherBot can easily be deployed to Heroku. Install the heroku-toolbelt and run the following to get started:
```shell
heroku login
heroku create
git push heroku master
```
The twitter and forecast.io keys need to be added. The format to do so is:
```shell
heroku config:set WEATHERBOT_CONSUMER_KEY=xxxxx WEATHERBOT_CONSUMER_SECRET=xxxxx WEATHERBOT_ACCESS_KEY=xxxxx WEATHERBOT_ACCESS_SECRET=xxxxx WEATHERBOT_FORECASTIO_KEY=xxxxx
```
You can also add keys/environmental variables on the Heroku project's settings page.

## Tools Used
* [Tweepy](https://github.com/tweepy/tweepy)
* [forecast.io API](https://developer.forecast.io)
* [python-forecast.io](https://github.com/ZeevG/python-forecast.io)
* [Python Daemon](https://pypi.python.org/pypi/python-daemon/)
