# weatherBot strings
# Copyright 2015-2016 Brian Mitchell under the MIT license
# See the GitHub repository: https://github.com/BrianMitchL/weatherBot

import random
from collections import namedtuple

import utils

Condition = namedtuple('Condition', ['type', 'text'])


class WeatherBotString:
    def __init__(self, __strings):
        """
        :param __strings: dict containing fields from strings.yml file or similar
        """
        self.weather_data = dict()
        self.language = __strings['language']
        self.forecasts = __strings['forecasts']
        self.forecast_endings = __strings['forecast_endings']
        self.normal_conditions = __strings['normal_conditions']
        self.special_conditions = __strings['special_conditions']
        self.alerts = __strings['alerts']
        self.precipitations = __strings['precipitations']

    def set_weather(self, weather_data):
        """
        :param weather_data: standard weather_data dict (see weatherBot.get_weather_variables)
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
        summary = self.weather_data['forecast'].summary
        summary_lower = self.weather_data['forecast'].summary.lower()
        units = self.weather_data['units']
        high = str(round(self.weather_data['forecast'].temperatureMax)) + 'º' + units['temperatureMax']
        low = str(round(self.weather_data['forecast'].temperatureMin)) + 'º' + units['temperatureMin']
        for i, forecast in enumerate(self.forecasts):
            self.forecasts[i] = forecast.format(summary=summary,
                                                summary_lower=summary_lower,
                                                high=high,
                                                low=low)

    def forecast(self):
        """
        :return: random forecast string containing the text for a forecast tweet
        """
        forecast = random.choice(self.forecasts)
        if self.forecast_endings:
            forecast += ' ' + random.choice(self.forecast_endings)
        return forecast

    def update_normal(self):
        """
        updates all normal conditions' replacement fields
        """
        temp = self.weather_data['temp_and_unit']
        summary = self.weather_data['summary']
        hour_summary = self.weather_data['hour_summary']
        location = self.weather_data['location']
        for i, normal in enumerate(self.normal_conditions):
            self.normal_conditions[i] = normal.format(summary=summary,
                                                      hour_summary=hour_summary,
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
        units = self.weather_data['units']
        apparent_temp = str(self.weather_data['apparentTemperature']) + 'º' + units['apparentTemperature']
        temp = str(self.weather_data['temp']) + 'º' + units['apparentTemperature']
        wind_speed = str(self.weather_data['windSpeed']) + units['windSpeed']
        wind_bearing = self.weather_data['windBearing']
        humidity = str(self.weather_data['humidity'])
        summary = self.weather_data['summary']
        hour_summary = self.weather_data['hour_summary']
        location = self.weather_data['location']
        for condition in self.special_conditions:
            for i, special in enumerate(self.special_conditions[condition]):
                self.special_conditions[condition][i] = special.format(apparent_temp=apparent_temp,
                                                                       temp=temp,
                                                                       wind_speed=wind_speed,
                                                                       wind_bearing=wind_bearing,
                                                                       humidity=humidity,
                                                                       summary=summary,
                                                                       hour_summary=hour_summary,
                                                                       location=location)

    def special(self):
        """
        :return: Condition namedtuple with random special condition string containing the text for a normal tweet
        """
        precip = self.precipitation()
        units = self.weather_data['units']
        apparent_temp = self.weather_data['apparentTemperature']
        temp = self.weather_data['temp']
        wind_speed = self.weather_data['windSpeed']
        humidity = self.weather_data['humidity']
        code = self.weather_data['icon']
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
        elif humidity <= 30:
            weather_type = 'dry'

        if weather_type == 'none':
            return Condition(type='normal', text='')
        else:
            return Condition(type=weather_type, text=random.choice(self.special_conditions[weather_type]))

    def update_precipitation(self):
        """
        updates all precipitation replacement fields
        """
        rate = str(self.weather_data['precipIntensity'])
        rate += self.weather_data['units']['precipIntensity']
        for precipType in self.precipitations:
            for precipIntensity in self.precipitations[precipType]:
                for i, precip in enumerate(self.precipitations[precipType][precipIntensity]):
                    self.precipitations[precipType][precipIntensity][i] = precip.format(rate=rate)

    def precipitation(self):
        """
        :return: Condition namedtuple with type and random text field names
        """
        intensity = utils.precipitation_intensity(self.weather_data['precipIntensity'],
                                                  self.weather_data['units']['precipIntensity'])
        probability = self.weather_data['precipProbability']
        precip_type = self.weather_data['precipType']
        # Consider 80% chance and above as fact
        if probability >= 0.80 and precip_type != 'none' and intensity != 'none':
            detailed_type = intensity + '-' + precip_type
            text = random.choice(self.precipitations[precip_type][intensity])
            return Condition(type=detailed_type, text=text)
        else:
            return Condition(type='none', text='')

    def alert(self, title, expires, uri):
        """
        :param title: string of weather alert title
        :param expires: a datetime.datetime object containing the expiration time
        :param uri: a uri encoded link to view more information about the alert
        :return: random alert
        """
        # https://docs.python.org/3.3/library/datetime.html#strftime-and-strptime-behavior
        expires_formatted = expires.strftime('%a, %b %d at %X %Z')
        return random.choice(self.alerts).format(title=title, expires=expires_formatted, uri=uri)
