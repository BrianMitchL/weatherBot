# weatherBot strings
# Copyright 2015-2016 Brian Mitchell under the MIT license
# See the GitHub repository: https://github.com/bman4789/weatherBot

import random
import utils
from collections import namedtuple

Condition = namedtuple('Condition', ['type', 'text'])

# strings that will be randomly chosen to be appended to a forecast tweet
endings = ['Exciting!', 'Nice!', 'Sweet!', 'Wow!', 'I can\'t wait!', 'Nifty!',
           'Excellent!', 'What a day!', 'This should be interesting!', 'Aww yeah!',
           'Oh happy day!', 'Far out!', 'Groovy!', 'Fantastic!', 'I want to believe.',
           'Or maybe not, who knows.', 'Praise the sun!', 'Jolly good!']


def get_normal_condition(weather_data):
    """
    :param weather_data: weather_data dict
    :return: string containing the text of a tweet
    """
    summary = weather_data['summary']
    temp = weather_data['temp_and_unit']
    location = weather_data['location']
    hour_summary = weather_data['hour_summary']
    text = [
        'The weather is boring. ' + temp + ' and ' + summary + '.',
        'Great, it\'s ' + summary + ' and ' + temp + '.',
        'What a normal day, it\'s ' + summary + ' and ' + temp + '.',
        'Whoopie do, it\'s ' + temp + ' and ' + summary + '.',
        temp + ' and ' + summary + '.',
        temp + ' and ' + summary + '. What did you expect?',
        'Welcome to ' + location + ', where it\'s ' + summary + ' and ' + temp + '.',
        'Breaking news: it\'s ' + summary + ' and ' + temp + '.',
        'We got some ' + summary + ' at ' + temp + ' going on.',
        'Well, would you look at that, it\'s ' + temp + ' and ' + summary + '.',
        'Great Scott, it\'s ' + summary + ' and ' + temp + '!',
        'It\'s ' + temp + ' and ' + summary + ', oh boy!',
        'Only in ' + location + ' would it be ' + temp + ' and ' + summary + ' right now.',
        'Golly gee wilikers, it\'s ' + temp + ' and ' + summary + '.',
        'It is currently ' + summary + ' and ' + temp + '.',
        'Big surprise, it\'s ' + summary + ' and ' + temp + '.',
        'Look up, it\'s ' + summary + ' and ' + temp + '.',
        'Dang, it\'s ' + temp + ' and ' + summary + '.',
        'Blimey, it\'s ' + temp + ' and ' + summary + '.',
        'For Pete\'s sake, it\'s ' + summary + ' and ' + temp + ' again.',
        'Holy cow, it\'s ' + temp + ' and ' + summary + '.',
        'What a doozy, it\'s ' + temp + ' and ' + summary + '.',
        'Eh, it\'s ' + temp + ' and ' + summary + '.',
        'Woah, it\'s ' + summary + ' and ' + temp + '.'
        ]
    if hour_summary:
        return random.choice(text) + ' ' + hour_summary
    else:
        return random.choice(text)


def get_special_condition(weather_data):
    """
    :param weather_data: dict containing weather information
    :return: Condition namedtuple with type and text field names
    """
    precip = get_precipitation(weather_data['precipIntensity'], weather_data['precipProbability'],
                               weather_data['precipType'], weather_data['units'])
    code = weather_data['icon']
    if (weather_data['units']['temperature'] == 'F' and weather_data['apparentTemperature'] <= -30) or \
            (weather_data['units']['temperature'] == 'C' and weather_data['apparentTemperature'] <= -34):
        text = 'Brr! The windchill is ' + weather_data['apparentTemperature_and_unit'] \
               + ' and the wind is blowing at ' + weather_data['windSpeed_and_unit'] + ' from the ' \
               + weather_data['windBearing'] + '. Stay safe out there!'
        return Condition(type='wind-chill', text=text)
    # elif (weather_data['units']['visibility'] == 'mi' and weather_data['nearestStormDistance'] <= 2) or \
    #         (weather_data['units']['visibility'] == 'km' and weather_data['nearestStormDistance'] <= 3):
    #     return 'Watch out, there\'s a storm ' + str(weather_data['nearestStormDistance']) + ' ' + \
    #             weather_data['units']['visibility'] + ' away. The wind is blowing at ' + \
    #            weather_data['windSpeed_and_unit'] + ' from the ' \
    #            + weather_data['windBearing'] + ' and there is precipitation at a rate of ' + \
    #            str(weather_data['precipIntensity']) + ' ' + weather_data['units']['precipIntensity'] + '.'
    elif precip.type != 'none':
        return precip
    elif 'medium-wind' in code:
        text = 'Looks like we\'ve got some medium wind at ' + weather_data['windSpeed_and_unit'] + \
               ' coming from the ' + weather_data['windBearing'] + '.'
        return Condition(type='medium-wind', text=text)
    elif 'heavy-wind' in code or \
            (weather_data['units']['windSpeed'] == 'mph' and weather_data['windSpeed'] >= 35.0) or \
            (weather_data['units']['windSpeed'] == 'km/h' and weather_data['windSpeed'] >= 56.0) or \
            (weather_data['units']['windSpeed'] == 'm/s' and weather_data['windSpeed'] >= 15.0):
        text = 'Hold onto your hats! The wind is blowing at ' + weather_data['windSpeed_and_unit'] + \
               ' coming from the ' + weather_data['windBearing'] + '.'
        return Condition(type='heavy-wind', text=text)
    elif 'fog' in code:
        text = 'Do you even fog bro? 🌫'
        return Condition(type='fog', text=text)
    elif (weather_data['units']['temperature'] == 'F' and weather_data['temp'] <= -20) or \
            (weather_data['units']['temperature'] == 'C' and weather_data['temp'] <= -28):
        text = 'It\'s ' + weather_data['temp_and_unit'] + '. Too cold.'
        return Condition(type='cold', text=text)
    elif (weather_data['units']['temperature'] == 'F' and weather_data['temp'] >= 110) or \
            (weather_data['units']['temperature'] == 'C' and 43 <= weather_data['temp']):
        text = 'Wowowowowowowowow, it\'s ' + weather_data['temp_and_unit'] + '. I need some A/C ASAP.'
        return Condition(type='super-hot', text=text)
    elif (weather_data['units']['temperature'] == 'F' and weather_data['temp'] >= 100) or \
            (weather_data['units']['temperature'] == 'C' and 37 <= weather_data['temp'] <= 50):
        text = 'Holy moly it\'s ' + weather_data['temp_and_unit'] + '. I could literally (figuratively) melt.'
        return Condition(type='hot', text=text)
    elif weather_data['humidity'] <= 10:
        text = 'It\'s dry as strained pasta. ' + str(weather_data['humidity']) + '% humid right now.'
        return Condition(type='dry', text=text)
    else:
        # normal determines if the weather is normal (boring) or special (exciting!)
        return Condition(type='normal', text='')


def get_alert_text(title, expires, uri):
    """
    :param title: dict containing weather information
    :param expires: a datetime.datetime object containing the expiration time
    :param uri: a uri encoded link to view more information about the alert
    :return: string: the text of a tweet
    """
    # https://docs.python.org/3.3/library/datetime.html#strftime-and-strptime-behavior
    expires_formatted = expires.strftime('%a, %b %d at %X %Z')
    text = [
        'Oh goody, a weather alert! ' + title + ' until ' + expires_formatted + '. ' + uri,
        'Weather alert: ' + title + ' until ' + expires_formatted + '. ' + uri,
        'It\'s official now! ' + title + ' until ' + expires_formatted + '. ' + uri
        ]
    return random.choice(text)


def get_precipitation(precip_intensity, precip_probability, precip_type, units):
    """
    :param precip_intensity: float containing the currently precipIntensity
    :param precip_probability: float containing the currently precipProbability
    :param precip_type: float containing the currently precipType
    :param units: dict of units as returned by get_units
    :return: Condition namedtuple with type and text field names
    """

    text = {
        'rain': {
            'heavy': ['Run for cover and stay dry! Heavy rain!',
                      'Heavy rain detected, I hope your windows are closed.'],
            'moderate': ['Alert: there is water falling from the sky.',
                         'It\'s raining 🌧',
                         'Grab your umbrella, it\'s raining! ☔️',
                         '☔️'],
            'light': ['Light rain!'],
            'very-light': ['Drizzlin\' yo.',
                           'Very light rain detected.']
        },
        'snow': {
            'heavy': ['Heavy snow, bundle up.',
                      'Heavy snow detected, good luck with that.'],
            'moderate': ['Alert: there are flakes of crystalline water ice falling from the clouds.',
                         'It\'s snowing. ❄️',
                         'It\'s snowing. 🌨',
                         '🌨',
                         '❄️'],
            'light': ['Light snow!',
                      'It\'s lightly snowing.'],
            'very-light': ['Flurries.',
                           'Flurries detected.']
        },
        'sleet': {
            'heavy': ['Heavy sleet.'],
            'moderate': ['Sleet.'],
            'light': ['Light sleet.'],
            'very-light': ['Very light sleet.']
        },
        'hail': {
            'heavy': ['Heavy hail, run for cover!'],
            'moderate': ['Hail, watch out.'],
            'light': ['Light hail.'],
            'very-light': ['Very light hail.']
        }
    }

    intensity = utils.precipitation_intensity(precip_intensity, units['precipIntensity'])

    # Consider 80% chance and above as fact
    if precip_probability >= 0.80 and precip_type != 'none' and intensity != 'none':
        detailed_type = intensity + '-' + precip_type
        text = random.choice(text[precip_type][intensity])
        return Condition(type=detailed_type, text=text)
    else:
        return Condition(type='none', text='')
