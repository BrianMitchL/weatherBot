# weatherBot [![GitHub release](https://img.shields.io/github/release/BrianMitchL/weatherBot.svg?maxAge=86400)](https://github.com/BrianMitchL/weatherBot/releases/latest) [![Python Version](https://img.shields.io/badge/python-3.4+-blue.svg)](https://www.python.org) [![Build Status](https://travis-ci.org/BrianMitchL/weatherBot.svg?branch=master)](https://travis-ci.org/BrianMitchL/weatherBot) [![Coverage Status](https://coveralls.io/repos/github/BrianMitchL/weatherBot/badge.svg?branch=master)](https://coveralls.io/github/BrianMitchL/weatherBot?branch=master) [![Dependency Status](https://gemnasium.com/badges/github.com/BrianMitchL/weatherBot.svg)](https://gemnasium.com/github.com/BrianMitchL/weatherBot)

A Twitter bot for weather. [Powered by Dark Sky](https://darksky.net/poweredby/).

<img src="https://darksky.net/dev/img/attribution/poweredby-oneline.png" alt="Powered by Dark Sky" width="200">

_**Note: Any language or wording suggestions are appreciated and should be submitted as an issue or pull request.**_

Example bots can be found at [@MorrisMNWeather](https://twitter.com/MorrisMNWeather) and [@WeatherByBrian](https://twitter.com/WeatherByBrian).

weatherBot tweets the current weather condition at scheduled times. If a special weather event is happening, it will tweet that (outside of the scheduled times). weatherBot can also tweet the current day's forecast.

## Features
* Current conditions at scheduled times
* Daily forecast at a scheduled time
* Severe weather alerts issued by a governmental authority
* Real time "special" events (precipitation, fog, extreme temperatures, wind, etc.)
* Granular throttling of special events
* Variable location for all tweets based on the locations of a user's recent tweets
* Fully customizable text for tweets via a YAML file
* International support for timezones, units, and languages
* Twitter geolocation in each tweet
* Console and file based logging
* Send the traceback of a crash as a direct message
* Cache runtime information to a file for easy resuming
* Configuration file
* Deploy via Heroku or Docker

## Install Dependencies
Run the following from the repository root directory to install the needed dependencies.
```shell
# The minimum dependencies needed to run weatherBot
pip3 install -r requirements.txt
# Additional dependencies needed for testing, linting, and validating
pip3 install -r requirements-dev.txt
```

## Use
weatherBot.py has been built for Python 3 (tested with 3.4 and above). Legacy Python is not supported. 

1. Set your location and other settings in `weatherBot.conf`
2. Set your API keys and secrets as environmental variables (recommended) or in `keys.py`

```shell
python3 weatherBot.py weatherBot.conf
```
You're all set!

## Settings and Customizing

### Configuration File
Many features of weatherBot can be customized in a conf file. This ships with a file named `weatherBot.conf`, but can be called whatever you'd like. Each option has a comment above it describing its purpose.
If you want a clean conf file, feel free to remove all but the settings you set, they are all optional. The section headers must remain in the file.

### API Keys
The Twitter app consumer key and secret as well as the access token and token secret are located either in environmental variables (recommended) or in the `keys.py` file. The script will pull in the keys from the environmental variables over the keys.py file. See https://apps.twitter.com to get your keys and secrets.
The names of the environmental variables are as follows: `WEATHERBOT_CONSUMER_KEY`, `WEATHERBOT_CONSUMER_SECRET`, `WEATHERBOT_ACCESS_TOKEN`, `WEATHERBOT_ACCESS_TOKEN_SECRET`, and `WEATHERBOT_DARKSKY_KEY`. Entering keys into keys.py is not required if you have entered them as environmental variables.

### Strings
The language as well as the text used for all tweets can be edited or added in `strings.yml`. Remember to set the units and path/filename (defaults to `strings.yml`) in the configuration file.

### Variable Location
Enable variable location to have the location for weather change. The Twitter username in the variable location user setting will be used to determine this location. The specified user must tweet with location fairly regularly (at least every 20 tweets, not including retweets), or the manually entered location will be used. The most recent tweet with a location will be used to get the location for weather.
For example, say the given user tweets from Minneapolis, MN one day. Minneapolis will be used as the location indefinitely until a new tweet with location is posted or if 20 new tweets have been posted that do not contain a location. weatherBot checks the user's timeline every 30 minutes for updates in location.
The human readable Twitter location will also be added to the beginning of each tweet. For example, in the same case as earlier, "Minneapolis, MN: " would be prefixed to every tweet.

## Deploying to [Heroku](https://www.heroku.com/)
weatherBot can easily be deployed to Heroku. Install the heroku-toolbelt and run the following to get started:
```shell
heroku login
heroku create
git push heroku master
```
The Twitter and Dark Sky keys need to be added. The format to do so is:
```shell
heroku config:set \
WEATHERBOT_CONSUMER_KEY=xxx \
WEATHERBOT_CONSUMER_SECRET=xxx \
WEATHERBOT_ACCESS_TOKEN=xxx \
WEATHERBOT_ACCESS_TOKEN_SECRET=xxx \
WEATHERBOT_DARKSKY_KEY=xxx
```
You can also add keys/environmental variables on the Heroku project's settings page.

## Deploying with Docker

weatherBot can easily be deployed using Docker.

### weatherBot from Docker Hub

To download the image, run:
```shell
docker pull brianmitchl/weatherbot
```
Start the bot with the following, replacing the API keys and secrets with the correct strings. You will also need to add your conf file to the container (I use the `-v` flag).
```shell
docker run --name weatherBot -d \
-v /home/brianmitchell/weatherBot/dist/custom.conf:/src/custom.conf \
-e WEATHERBOT_CONSUMER_KEY=xxx \
-e WEATHERBOT_CONSUMER_SECRET=xxx \
-e WEATHERBOT_ACCESS_TOKEN=xxx \
-e WEATHERBOT_ACCESS_TOKEN_SECRET=xxx \
-e WEATHERBOT_DARKSKY_KEY=xxx \
brianmitchl/weatherbot python weatherBot.py custom.conf
```

### Building Your Own weatherBot

Alternatively, if you wish to build the Docker image yourself, run:
```shell
docker build -t weatherbot .
```
Start the bot using the same run command as above, while replacing the image name with what you call yours.

## Tools Used
* [Tweepy](https://github.com/tweepy/tweepy)
* [Dark Sky API](https://darksky.net/poweredby/)
* [python-forecast.io](https://github.com/ZeevG/python-forecast.io)
