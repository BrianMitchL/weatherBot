"""
weatherBot keys

Copyright 2015-2016 Brian Mitchell under the MIT license
See the GitHub repository: https://github.com/BrianMitchL/weatherBot
"""

import os


KEYS = {
    'consumer_key': 'xxx',
    'consumer_secret': 'xxx',
    'access_token': 'xxx',
    'access_token_secret': 'xxx',
    'darksky_key': 'xxx'
}


def set_twitter_env_vars():
    """
    If no Twitter environmental variables are set, set them based on the keys dict
    """
    if os.getenv('WEATHERBOT_CONSUMER_KEY', 0) is 0 or os.getenv('WEATHERBOT_CONSUMER_SECRET', 0) is 0 \
            or os.getenv('WEATHERBOT_ACCESS_TOKEN', 0) is 0 or os.getenv('WEATHERBOT_ACCESS_TOKEN_SECRET', 0) is 0:
        os.environ['WEATHERBOT_CONSUMER_KEY'] = KEYS['consumer_key']
        os.environ['WEATHERBOT_CONSUMER_SECRET'] = KEYS['consumer_secret']
        os.environ['WEATHERBOT_ACCESS_TOKEN'] = KEYS['access_token']
        os.environ['WEATHERBOT_ACCESS_TOKEN_SECRET'] = KEYS['access_token_secret']


def set_darksky_env_vars():
    """
    If no Dark Sky environmental variable is set, set it based on the keys dict
    """
    if os.getenv('WEATHERBOT_DARKSKY_KEY', 0) is 0:
        os.environ['WEATHERBOT_DARKSKY_KEY'] = KEYS['darksky_key']
