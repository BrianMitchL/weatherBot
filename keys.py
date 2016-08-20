#!/usr/bin/env python3

# weatherBot keys
# Copyright 2015-2016 Brian Mitchell under the MIT license
# See the GitHub repository: https://github.com/BrianMitchL/weatherBot

import os


keys = {
    'consumer_key': 'xxx',
    'consumer_secret': 'xxx',
    'access_token': 'xxx',
    'access_token_secret': 'xxx',
    'forecastio_key': 'xxx'
}


def set_twitter_env_vars():
    if os.getenv('WEATHERBOT_CONSUMER_KEY', 0) is 0 or os.getenv('WEATHERBOT_CONSUMER_SECRET', 0) is 0 \
            or os.getenv('WEATHERBOT_ACCESS_TOKEN', 0) is 0 or os.getenv('WEATHERBOT_ACCESS_TOKEN_SECRET', 0) is 0:
        os.environ['WEATHERBOT_CONSUMER_KEY'] = keys['consumer_key']
        os.environ['WEATHERBOT_CONSUMER_SECRET'] = keys['consumer_secret']
        os.environ['WEATHERBOT_ACCESS_TOKEN'] = keys['access_token']
        os.environ['WEATHERBOT_ACCESS_TOKEN_SECRET'] = keys['access_token_secret']


def set_forecastio_env_vars():
    if os.getenv('WEATHERBOT_FORECASTIO_KEY', 0) is 0:
        os.environ['WEATHERBOT_FORECASTIO_KEY'] = keys['forecastio_key']
