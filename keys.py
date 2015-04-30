#!/usr/bin/env python
# -*- coding: utf-8 -*-

# weatherBot keys
# Copyright 2015 Brian Mitchell under the MIT license
# See the GitHub repository: https://github.com/bman4789/weatherBot

import os

keys = dict(
    consumer_key='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    consumer_secret='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    access_key='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    access_secret='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
)


def set_env_vars():
    if os.getenv('WEATHERBOT_CONSUMER_KEY', 0) is 0 or os.getenv('WEATHERBOT_CONSUMER_SECRET', 0) is 0 \
            or os.getenv('WEATHERBOT_ACCESS_KEY', 0) is 0 or os.getenv('WEATHERBOT_ACCESS_SECRET', 0) is 0:
        os.environ['WEATHERBOT_CONSUMER_KEY'] = keys['consumer_key']
        os.environ['WEATHERBOT_CONSUMER_SECRET'] = keys['consumer_secret']
        os.environ['WEATHERBOT_ACCESS_KEY'] = keys['access_key']
        os.environ['WEATHERBOT_ACCESS_SECRET'] = keys['access_secret']