import json

import tweepy
import requests


def mocked_get_tweepy_api():
    class API:
        """
        Class mocking a tweepy API
        """

        def me(self):
            """
            get the current user's screen name
            :return: str
            """
            return 'test'

        def send_direct_message(self):
            """
            send a direct message
            """

        def update_status(self, status, lat=None, long=None):
            """
            Update status
            :return: Status
            """

            class Status:
                """
                Class mocking a tweepy Status
                """

                def __init__(self, text):
                    """
                    :param text: str
                    """
                    self.text = text

            if status == 'error':
                raise tweepy.TweepError('error on purpose')
            else:
                return Status(status)

        def user_timeline(self, screen_name, include_rts, count):
            """
            Get a user's timeline
            :return: list
            """

            class Box:
                def __init__(self):
                    self.coordinates = [[[1.0, 2.0], [3.0, 4.0], [5.0, 6.0], [7.0, 8.0]]]

            class Place:
                def __init__(self, place_name):
                    self.full_name = place_name
                    self.bounding_box = Box()

            class Tweet:
                def __init__(self):
                    if screen_name == 'nocoords':
                        self.coordinates = None
                        self.place = Place('cool place')
                    elif screen_name == 'coordsnoplace':
                        self.coordinates = {
                            'coordinates': [1.5, 2.5]
                        }
                        self.place = None
                    else:
                        self.coordinates = {
                            'coordinates': [1, 2]
                        }
                        self.place = Place('test')

            if screen_name == 'error':
                raise tweepy.TweepError('uh oh')
            elif screen_name != 'no tweets':
                return [Tweet()]
            else:
                return []

    return API()


def mocked_requests_get(*args, **kwargs):
    """
    Mocked requests.get
    :return: MockResponse
    """

    class MockResponse:
        """
        Class mocking the response of calling request.get in the python-forecastio library
        """

        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
            self.headers = None

        def raise_for_status(self):
            """
            This method is used to check for errors, but none will (should) exist in a mocked response
            """
            pass

        def json(self):
            """
            :return: dict
            """
            return self.json_data

    with open(args[0], 'r', encoding='utf-8') as file_stream:
        return MockResponse(json.load(file_stream), 200)


def mocked_forecastio_manual(url):
    class Response:
        def __init__(self, status_code):
            self.status_code = status_code

    class Forecast:
        """
        Class mocking a Forecast
        """

        def __init__(self):
            self.response = Response(200)
            self.json = {
                'flags': {
                    'units': 'us'
                }
            }

    return Forecast()


def mocked_forecastio_manual_error(url):
    raise requests.exceptions.HTTPError


def mocked_tweepy_o_auth_handler(key, secret):
    class Auth:
        def set_access_token(self, token, secret):
            pass

    return Auth()
