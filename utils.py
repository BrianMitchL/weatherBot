# weatherBot utils
# Copyright 2015 Brian Mitchell under the MIT license
# See the GitHub repository: https://github.com/bman4789/weatherBot


def get_units(unit):
    if unit is 'us':
        return {
            'unit': 'us',
            'nearestStormDistance': 'mph',
            'precipIntensity': 'in/h',
            'precipIntensityMax': 'in/h',
            'precipAccumulation': 'in',
            'temperature': 'F',
            'temperatureMin': 'F',
            'temperatureMax': 'F',
            'apparentTemperature': 'F',
            'dewPoint': 'F',
            'windSpeed': 'mph',
            'pressure': 'mb',
            'visibility': 'mi'
        }
    elif unit is 'ca':
        return {
            'unit': 'ca',
            'nearestStormDistance': 'km/h',
            'precipIntensity': 'mm/h',
            'precipIntensityMax': 'mm/h',
            'precipAccumulation': 'cm',
            'temperature': 'C',
            'temperatureMin': 'C',
            'temperatureMax': 'C',
            'apparentTemperature': 'C',
            'dewPoint': 'C',
            'windSpeed': 'km/h',
            'pressure': 'hPa',
            'visibility': 'km'
        }
    elif unit is 'uk2':
        return {
            'unit': 'uk2',
            'nearestStormDistance': 'mi',
            'precipIntensity': 'mm/h',
            'precipIntensityMax': 'mm/h',
            'precipAccumulation': 'cm',
            'temperature': 'C',
            'temperatureMin': 'C',
            'temperatureMax': 'C',
            'apparentTemperature': 'C',
            'dewPoint': 'C',
            'windSpeed': 'mph',
            'pressure': 'hPa',
            'visibility': 'mi'
        }
    else:  # si
        return {
            'unit': 'si',
            'nearestStormDistance': 'km/h',
            'precipIntensity': 'mm/h',
            'precipIntensityMax': 'mm/h',
            'precipAccumulation': 'cm',
            'temperature': 'C',
            'temperatureMin': 'C',
            'temperatureMax': 'C',
            'apparentTemperature': 'C',
            'dewPoint': 'C',
            'windSpeed': 'm/s',
            'pressure': 'hPa',
            'visibility': 'km'
        }


def get_wind_direction(degrees):
    """
    :param degrees: integer for degrees of wind
    :return: string of the wind direction in shorthand form
    """
    try:
        degrees = int(degrees)
    except ValueError:
        return ''
    if degrees < 23 or degrees >= 338:
        return 'N'
    elif degrees < 68:
        return 'NE'
    elif degrees < 113:
        return 'E'
    elif degrees < 158:
        return 'SE'
    elif degrees < 203:
        return 'S'
    elif degrees < 248:
        return 'SW'
    elif degrees < 293:
        return 'W'
    elif degrees < 338:
        return 'NW'
