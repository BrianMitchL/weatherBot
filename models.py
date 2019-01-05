"""
weatherBot models

Copyright 2015-2018 Brian Mitchell under the MIT license
See the GitHub repository: https://github.com/BrianMitchL/weatherBot
"""

import random
from collections import namedtuple
from copy import deepcopy
from datetime import datetime, timedelta
from hashlib import sha256

import pytz
from forecastio.utils import PropertyUnavailable

import utils

Condition = namedtuple('Condition', ['type', 'text'])


class BadForecastDataError(Exception):
    """
    Designed to be thrown when a Forecast object contains issues that would render the weather data unusable
    """


class WeatherLocation:
    """
    This is for storing a weather location. The intended use is for quickly accessing the lat, lng, and name.
    """

    # pylint: disable=too-few-public-methods
    def __init__(self, lat, lng, name):
        """
        :type lat: float
        :type lng: float
        :type name: str
        """
        self.lat = lat
        self.lng = lng
        self.name = name

    def __str__(self):
        return '<WeatherLocation: {name} at {lat},{lng}>'.format(lat=str(self.lat), lng=str(self.lng), name=self.name)

    def __eq__(self, other):
        return self.lat == other.lat and self.lng == other.lng and self.name == other.name and \
               isinstance(other, WeatherLocation)

    def __ne__(self, other):
        return self.lat != other.lat or self.lng != other.lng or self.name != other.name

    def __repr__(self):
        return self.__str__()


class WeatherAlert:
    """
    This is for storing weather alerts. The fields are very similar to a ForecastAlert.
    """
    def __init__(self, alert):
        """
        :type alert: forecastio.models.Alert
        """
        self.title = alert.title
        self.time = pytz.utc.localize(datetime.utcfromtimestamp(alert.time))
        try:
            self.expires = pytz.utc.localize(datetime.utcfromtimestamp(alert.expires))
        except PropertyUnavailable:
            pass
        self.uri = alert.uri
        self.severity = alert.severity

    def __str__(self):
        return '<WeatherAlert: {title} at {time}>'.format(title=self.title, time=self.time)

    def expired(self, now=pytz.utc.localize(datetime.utcnow())):
        """
        :type now: datetime.datetime that is timezone aware to UTC
        :return boolean
        """
        try:
            return now > self.expires
        except AttributeError:
            # most alerts are probably done after 3 days
            return now > self.time + timedelta(days=3)

    def sha(self):
        """
        :return: sha256 of alert as a string
        """
        full_alert = self.title + str(self.time)
        return sha256(full_alert.encode()).hexdigest()  # a (hopefully) unique id


class WeatherData:
    """
    This is for storing weather data as returned by the Dark Sky API via the python-forecastio library.
    """

    # pylint: disable=too-many-instance-attributes,invalid-name,too-few-public-methods
    def __init__(self, forecast, location):
        """
        :type location: WeatherLocation
        :type forecast: forecastio.models.Forecast
        """
        self.__forecast = forecast

        try:
            if 'darksky-unavailable' in forecast.json['flags']:
                raise BadForecastDataError('Darksky unavailable')
            self.units = utils.get_units(forecast.json['flags']['units'])
            # Dark Sky doesn't always include 'windBearing'
            if hasattr(forecast.currently(), 'windBearing'):
                self.windBearing = utils.get_wind_direction(forecast.currently().windBearing)
            else:
                self.windBearing = 'unknown direction'
            self.windSpeed = forecast.currently().windSpeed
            self.apparentTemperature = forecast.currently().apparentTemperature
            self.temp = forecast.currently().temperature
            self.humidity = round(forecast.currently().humidity * 100)
            self.precipIntensity = forecast.currently().precipIntensity
            self.precipProbability = forecast.currently().precipProbability
            if hasattr(forecast.currently(), 'precipType'):
                self.precipType = forecast.currently().precipType
            else:
                self.precipType = 'none'
            self.summary = forecast.currently().summary
            self.icon = forecast.currently().icon
            self.location = location
            self.timezone = forecast.json['timezone']
            self.forecast = forecast.daily().data[0]
            self.minutely = forecast.minutely()  # this will return None in many parts of the world
            self.alerts = list()
            for alert in forecast.alerts():
                self.alerts.append(WeatherAlert(alert))
            self.valid = True
        except (KeyError, TypeError, BadForecastDataError, PropertyUnavailable):
            self.valid = False

    def __str__(self):
        time = pytz.utc.localize(self.__forecast.currently().time)
        return '<WeatherData: {name}({lat},{lng}) at {time}>'.format(name=self.location.name,
                                                                     lat=self.location.lat,
                                                                     lng=self.location.lng,
                                                                     time=time)

    def json(self):
        """
        Raw JSON response from the Dark Sky API
        :return: dict
        """
        return self.__forecast.json


class WeatherBotString:
    """
    This is for storing and building strings based on a YAML file. The set_weather method must be used after creating
    a WeatherBotString object in order to set weather information to build alert, condition, and forecast strings.
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self, __strings):
        """
        :param __strings: dict containing fields from strings.yml file or similar
        """
        self.__template_forecasts = __strings['forecasts']
        self.__template_forecast_endings = __strings['forecast_endings']
        self.__template_normal_conditions = __strings['normal_conditions']
        self.__template_special_conditions = __strings['special_conditions']
        self.__template_expires_alerts = __strings['alerts']['expires']
        self.__template_no_expires_alerts = __strings['alerts']['no_expires']
        self.__template_precipitations = __strings['precipitations']
        self.weather_data = None
        self.language = __strings['language']
        self.forecasts = deepcopy(__strings['forecasts'])
        self.forecasts_endings = deepcopy(__strings['forecast_endings'])
        self.normal_conditions = deepcopy(__strings['normal_conditions'])
        self.special_conditions = deepcopy(__strings['special_conditions'])
        self.precipitations = deepcopy(__strings['precipitations'])

    def __dict__(self):
        return {
            'language': self.language,
            'weather_data': self.weather_data,
            'forecasts': self.forecasts,
            'forecast_endings': self.forecasts_endings,
            'normal_conditions': self.normal_conditions,
            'special_conditions': self.special_conditions,
            'precipitations': self.precipitations
        }

    def set_weather(self, weather_data):
        """
        :type weather_data: WeatherData
        """
        self.weather_data = weather_data
        self.update_forecast()
        self.update_normal()
        self.update_special()
        self.update_precipitation()

    def update_forecast(self):
        """
        updates all forecasts' replacement fields
        """
        summary = self.weather_data.forecast.summary
        summary_lower = self.weather_data.forecast.summary.lower()
        units = self.weather_data.units
        high = str(round(self.weather_data.forecast.temperatureMax)) + 'º' + units['temperatureMax']
        low = str(round(self.weather_data.forecast.temperatureMin)) + 'º' + units['temperatureMin']
        for i, forecast in enumerate(self.__template_forecasts):
            self.forecasts[i] = forecast.format(summary=summary,
                                                summary_lower=summary_lower,
                                                high=high,
                                                low=low)

    def forecast(self):
        """
        :return: random forecast string containing the text for a forecast tweet
        """
        forecast = random.choice(self.forecasts)
        if self.__template_forecast_endings:
            forecast += ' ' + random.choice(self.__template_forecast_endings)
        return forecast

    def update_normal(self):
        """
        updates all normal conditions' replacement fields
        """
        temp = str(round(self.weather_data.temp)) + 'º' + self.weather_data.units['temperature']
        summary = self.weather_data.summary
        location = self.weather_data.location.name
        for i, normal in enumerate(self.__template_normal_conditions):
            self.normal_conditions[i] = normal.format(summary=summary,
                                                      temp=temp,
                                                      location=location)

    def normal(self):
        """
        :return: random normal condition string containing the text for a normal tweet
        """
        return random.choice(self.normal_conditions)

    def update_special(self):
        """
        updates all normal conditions' replacement fields
        """
        units = self.weather_data.units
        apparent_temp = str(round(self.weather_data.apparentTemperature)) + 'º' + units['apparentTemperature']
        temp = str(round(self.weather_data.temp)) + 'º' + units['temperature']
        wind_speed = str(round(self.weather_data.windSpeed)) + ' ' + units['windSpeed']
        wind_bearing = self.weather_data.windBearing
        humidity = str(self.weather_data.humidity)
        summary = self.weather_data.summary
        location = self.weather_data.location.name
        for condition in self.__template_special_conditions:
            for i, special in enumerate(self.__template_special_conditions[condition]):
                self.special_conditions[condition][i] = special.format(apparent_temp=apparent_temp,
                                                                       temp=temp,
                                                                       wind_speed=wind_speed,
                                                                       wind_bearing=wind_bearing,
                                                                       humidity=humidity,
                                                                       summary=summary,
                                                                       location=location)

    def special(self):
        """
        :return: Condition namedtuple with random special condition string containing the text for a normal tweet
        """
        # pylint: disable=too-many-boolean-expressions
        precip = self.precipitation()
        units = self.weather_data.units
        apparent_temp = self.weather_data.apparentTemperature
        temp = self.weather_data.temp
        wind_speed = self.weather_data.windSpeed
        humidity = self.weather_data.humidity
        code = self.weather_data.icon
        weather_type = 'none'
        if (units['temperature'] == 'F' and apparent_temp <= -30) or \
                (units['temperature'] == 'C' and apparent_temp <= -34):
            weather_type = 'wind-chill'
        elif precip.type != 'none':
            return precip
        elif 'medium-wind' in code:
            weather_type = 'medium-wind'
        elif 'heavy-wind' in code or \
                (units['windSpeed'] == 'mph' and wind_speed >= 35.0) or \
                (units['windSpeed'] == 'km/h' and wind_speed >= 56.0) or \
                (units['windSpeed'] == 'm/s' and wind_speed >= 15.0):
            weather_type = 'heavy-wind'
        elif 'fog' in code:
            weather_type = 'fog'
        elif (units['temperature'] == 'F' and temp <= -20) or (units['temperature'] == 'C' and temp <= -28):
            weather_type = 'cold'
        elif (units['temperature'] == 'F' and temp >= 110) or (units['temperature'] == 'C' and temp >= 43):
            weather_type = 'super-hot'
        elif (units['temperature'] == 'F' and temp >= 100) or (units['temperature'] == 'C' and temp >= 37):
            weather_type = 'hot'
        elif humidity <= 25:
            weather_type = 'dry'

        if weather_type == 'none':
            return Condition(type='normal', text='')
        return Condition(type=weather_type, text=random.choice(self.special_conditions[weather_type]))

    def update_precipitation(self):
        """
        updates all precipitation replacement fields
        """
        rate = str(self.weather_data.precipIntensity)
        rate += self.weather_data.units['precipIntensity']
        for precip_type in self.__template_precipitations:
            for precip_intensity in self.__template_precipitations[precip_type]:
                for i, precip in enumerate(self.__template_precipitations[precip_type][precip_intensity]):
                    self.precipitations[precip_type][precip_intensity][i] = precip.format(rate=rate)

    def precipitation(self):
        """
        :return: Condition namedtuple with type and random text field names
        """
        intensity = utils.precipitation_intensity(self.weather_data.precipIntensity,
                                                  self.weather_data.units['precipIntensity'])
        probability = self.weather_data.precipProbability
        precip_type = self.weather_data.precipType
        # Consider 80% chance and above as fact
        if probability >= 0.80 and precip_type != 'none' and intensity != 'none':
            detailed_type = intensity + '-' + precip_type
            text = random.choice(self.precipitations[precip_type][intensity])
            return Condition(type=detailed_type, text=text)
        return Condition(type='none', text='')

    def alert(self, alert, timezone_id):
        """
        :param alert: WeatherAlert object
        :param timezone_id: str representing the local timezone
        :return: random alert
        """
        # https://docs.python.org/3.3/library/datetime.html#strftime-and-strptime-behavior
        str_format = '%a, %b %d at %X %Z'
        time = alert.time.astimezone(pytz.timezone(timezone_id)).strftime(str_format)
        try:
            expires = alert.expires.astimezone(pytz.timezone(timezone_id)).strftime(str_format)
            return random.choice(self.__template_expires_alerts).format(title=alert.title,
                                                                        time=time,
                                                                        expires=expires,
                                                                        uri=alert.uri)
        except AttributeError:
            return random.choice(self.__template_no_expires_alerts).format(title=alert.title,
                                                                           time=time,
                                                                           uri=alert.uri)
