# weatherBot utils
# Copyright 2015-2016 Brian Mitchell under the MIT license
# See the GitHub repository: https://github.com/bman4789/weatherBot

import pytz


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


def centerpoint(geolocations):
    """
    :param geolocations: array of arrays in the form of [[longitude, latitude],[longitude,latitude]]
    :return: average latitude and longitude in the form [latitude, longitude]
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
    :param timezone_id: string containing the timezone, ex: 'Europe/Copenhagen'
    :param dt: datetime.datetime
    :return: datetime.datetime
    """
    utc_dt = pytz.utc.localize(dt)
    return utc_dt.astimezone(pytz.timezone(timezone_id))


def get_utc_datetime(timezone_id, dt):
    """
    :param timezone_id: string containing the timezone, ex: 'Europe/Copenhagen'
    :param dt: datetime.datetime matching the timezone of timezone_id
    :return: datetime.datetime in utc timezone
    """
    tz = pytz.timezone(timezone_id)
    local_dt = tz.localize(dt)
    return local_dt.astimezone(pytz.utc)


def precipitation_intensity(precip_intensity, unit):
    """
    :param precip_intensity: float containing the currently precipIntensity
    :param unit: string of unit for precipitation rate ('in/h' or 'mm/h')
    :return: string of precipitation rate. Note: this is appended to and used in special event times
    """
    intensities = {
        'in/h': {
            'very-light': ('very-light', 0.002),
            'light': ('light', 0.017),
            'moderate': ('moderate', 0.1),
            'heavy': ('heavy', 0.4)
        },
        'mm/h': {
            'very-light':('very-light', 0.051),
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
