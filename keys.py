#!/usr/bin/env python3

# weatherBot keys
# Copyright 2015-2016 Brian Mitchell under the MIT license
# See the GitHub repository: https://github.com/bman4789/weatherBot

import os


keys = dict(
    consumer_key='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    consumer_secret='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    access_key='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    access_secret='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    forecastio_key='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
)


def set_twitter_env_vars():
    if os.getenv('WEATHERBOT_CONSUMER_KEY', 0) is 0 or os.getenv('WEATHERBOT_CONSUMER_SECRET', 0) is 0 \
            or os.getenv('WEATHERBOT_ACCESS_KEY', 0) is 0 or os.getenv('WEATHERBOT_ACCESS_SECRET', 0) is 0:
        os.environ['WEATHERBOT_CONSUMER_KEY'] = keys['consumer_key']
        os.environ['WEATHERBOT_CONSUMER_SECRET'] = keys['consumer_secret']
        os.environ['WEATHERBOT_ACCESS_KEY'] = keys['access_key']
        os.environ['WEATHERBOT_ACCESS_SECRET'] = keys['access_secret']


def set_forecastio_env_vars():
    if os.getenv('WEATHERBOT_FORECASTIO_KEY', 0) is 0:
        os.environ['WEATHERBOT_FORECASTIO_KEY'] = keys['forecastio_key']
