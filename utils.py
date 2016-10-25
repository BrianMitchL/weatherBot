"""
weatherBot utils

Copyright 2015-2016 Brian Mitchell under the MIT license
See the GitHub repository: https://github.com/BrianMitchL/weatherBot
"""

import pytz

from models import InvalidTimeError


def get_units(unit):
    """
    Return a dict of units based on the unit format code.
    :type unit: str
    :param unit: unit format
    :return dict containing units for weather measurements
    """
    if unit == 'us':
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
    elif unit == 'ca':
        return {
            'unit': 'ca',
            'nearestStormDistance': 'km',
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
    elif unit == 'uk2':
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
            'nearestStormDistance': 'km',
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
    Return the shorthand direction based on the given degrees.
    :type degrees: str, float
    :param degrees: integer for degrees of wind
    :type: str
    :return: wind direction in shorthand form
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


def centerpoint(geolocations):
    """
    Find the average centerpoint in a quadrilateral shape. geolocations matches the format used in the Twitter API.
    :type geolocations: list
    :param geolocations: list of lists in the form of [[longitude, latitude],[longitude,latitude]]
    :return: list: average latitude and longitude in the form [latitude, longitude]
    """
    lats = []
    lngs = []
    for lon, lat in geolocations:
        lats.append(lat)
        lngs.append(lon)
    avg_lat = float(sum(lats)) / len(lats)
    avg_lng = float(sum(lngs)) / len(lngs)
    return [avg_lat, avg_lng]


def get_local_datetime(timezone_id, dt):
    """
    Convert a timezone unaware datetime object in the UTC timezone to a timezone aware datetime object based on the
    inputted timezone_id.
    :type timezone_id: str
    :param timezone_id: timezone id, ex: 'Europe/Copenhagen'
    :type dt: datetime.datetime
    :param dt: timezone unaware datetime object but in UTC time
    :return: datetime.datetime
    """
    utc_dt = pytz.utc.localize(dt)
    return utc_dt.astimezone(pytz.timezone(timezone_id))


def get_utc_datetime(timezone_id, dt):
    """
    Convert a timezone unaware datetime object at the timezone_id timezone
    to a timezone aware datetime object in the UTC timezone.
    :type timezone_id: str
    :param timezone_id: timezone id, ex: 'Europe/Copenhagen'
    :type dt: datetime.datetime
    :param dt: timezone unaware datetime
    :return: datetime.datetime in utc timezone
    """
    tz = pytz.timezone(timezone_id)
    local_dt = tz.localize(dt)
    return local_dt.astimezone(pytz.utc)


def precipitation_intensity(precip_intensity, unit):
    """
    Return the precipitation intensity str based on the unit of precipIntensity and precip_intensity.
    If no rate is found, return 'none'
    :type precip_intensity: float
    :param precip_intensity: currently precipIntensity
    :type unit: str
    :param unit: unit for precipIntensity rate ('in/h' or 'mm/h')
    :return: str of precipitation rate. Note: this is appended to and used in special event times
    """
    intensities = {
        'in/h': {
            'very-light': ('very-light', 0.002),
            'light': ('light', 0.017),
            'moderate': ('moderate', 0.1),
            'heavy': ('heavy', 0.4)
        },
        'mm/h': {
            'very-light': ('very-light', 0.051),
            'light': ('light', 0.432),
            'moderate': ('moderate', 2.540),
            'heavy': ('heavy', 5.08)
        }
    }

    if precip_intensity >= intensities[unit]['heavy'][1]:
        return intensities[unit]['heavy'][0]
    elif precip_intensity >= intensities[unit]['moderate'][1]:
        return intensities[unit]['moderate'][0]
    elif precip_intensity >= intensities[unit]['light'][1]:
        return intensities[unit]['light'][0]
    elif precip_intensity >= intensities[unit]['very-light'][1]:
        return intensities[unit]['very-light'][0]
    else:
        return 'none'


def parse_time_string(raw_string):
    """
    This will parse raw_string and return it in the Time namedtuple form.
    If any errors exist, an InvalidTimeError will be raised.
    :type raw_string: str
    :param raw_string: time in the format of '6:00'
    :return: Time namedtuple with an hour and minute field
    """
    tmp_time = raw_string.split(':')
    if len(tmp_time) != 2:
        raise InvalidTimeError('time ({0}) is not formatted as \'int:int\''.format(raw_string))
    if tmp_time[0] == '' or tmp_time[1] == '':
        raise InvalidTimeError('time ({0}) is not formatted as \'int:int\''.format(raw_string))
    try:
        time_tuple = Time(hour=int(tmp_time[0]), minute=int(tmp_time[1]))
    except ValueError as err:
        raise InvalidTimeError('time ({0}) is not formatted as \'int:int\''.format(raw_string)) from err
    if time_tuple.hour < 0:
        raise InvalidTimeError('hour field ({0}) is negative'.format(time_tuple.hour))
    if time_tuple.hour > 23:
        raise InvalidTimeError('hour field ({0}) is larger than 23'.format(time_tuple.hour))
    if time_tuple.minute < 0:
        raise InvalidTimeError('minute field ({0}) is negative'.format(time_tuple.minute))
    if time_tuple.minute > 59:
        raise InvalidTimeError('minute field ({0}) is larger than 59'.format(time_tuple.minute))
    return time_tuple


def get_times(raw_string_list):
    """
    This will return a list of Time namedtuples from the raw_string_list str.
    The str is split on new lines and each time is passed into parse_time_string() for parsing.
    :type raw_string_list: str
    :param raw_string_list: string as returned from ConfigParser in the format of '7:00\n12:00\n15:00\n18:00\n22:00'
    :return: list of Time namedtuples with an hour and minute field
    """
    string_times = list(filter(None, (x.strip() for x in raw_string_list.splitlines())))
    tuple_times = list()
    for time in string_times:
        tuple_times.append(parse_time_string(time))
    tuple_times.sort()
    return tuple_times
