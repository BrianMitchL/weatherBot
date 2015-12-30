# weatherBot strings
# Copyright 2015 Brian Mitchell under the MIT license
# See the GitHub repository: https://github.com/bman4789/weatherBot

import random

# strings that will be randomly chosen to be appended to a forecast tweet
endings = ['Exciting!', 'Nice!', 'Sweet!', 'Wow!', 'I can\'t wait!', 'Nifty!',
           'Excellent!', 'What a day!', 'This should be interesting!', 'Aww yeah!']


def get_normal_condition(weather_data):
    """
    :param weather_data: weather_data dict
    :return: string containing the text of a tweet
    """
    summary = weather_data['summary']
    temp = weather_data['temp_and_unit']
    location = weather_data['location']
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
        'For Pete\'s sake, it\'s' + summary + ' and ' + temp + ' again.',
        'Holy cow, it\'s ' + temp + ' and ' + summary + '.'
        ]
    return random.choice(text)


def get_special_condition(weather_data):
    """
    :param weather_data: dict containing weather information
    :return: string containing the text of a tweet, or if no special event, return 'normal'
    """
    code = weather_data['icon']
    if (weather_data['units']['temperature'] == 'F' and weather_data['apparentTemperature'] <= -30) or \
            (weather_data['units']['temperature'] == 'C' and weather_data['apparentTemperature'] <= -34):
        return 'Wow, mother nature hates us. The windchill is ' + weather_data['apparentTemperature_and_unit'] \
               + ' and the wind is blowing at ' + weather_data['windSpeed_and_unit'] + ' from the ' \
               + weather_data['windBearing'] + '. My face hurts.'
    elif (weather_data['units']['visibility'] == 'mi' and weather_data['nearestStormDistance'] <= 2) or \
            (weather_data['units']['visibility'] == 'km' and weather_data['nearestStormDistance'] <= 3):
        return 'Watch out, there\'s a storm ' + str(weather_data['nearestStormDistance']) + ' ' + \
                weather_data['units']['visibility'] + ' away. The wind is blowing at ' + \
               weather_data['windSpeed_and_unit'] + ' from the ' \
               + weather_data['windBearing'] + ' and there is precipitation at a rate of ' + \
               str(weather_data['precipIntensity']) + ' ' + weather_data['units']['precipIntensity'] + '.'
    elif 'medium-wind' in code:
        return 'Looks like we\'ve got some medium wind at ' + weather_data['windSpeed_and_unit'] + \
               ' coming from the ' + weather_data['windBearing'] + '.'
    elif 'heavy-wind' in code or \
            (weather_data['units']['windSpeed'] == 'mph' and weather_data['windSpeed'] >= 35.0) or \
            (weather_data['units']['windSpeed'] == 'km/h' and weather_data['windSpeed'] >= 56.0) or \
            (weather_data['units']['windSpeed'] == 'm/s' and weather_data['windSpeed'] >= 15.0):
        return 'Hold onto your hats! The wind is blowing at ' + weather_data['windSpeed_and_unit'] + \
               ' coming from the ' + weather_data['windBearing'] + '.'
    elif 'heavy-rain' in code:
        return 'Run for cover and stay dry! It\'s ' + weather_data['temp_and_unit'] + ' raining heavily right now.'
    elif 'fog' in code:
        return 'Do you even fog bro?'
    elif 'mixed-precipitation' in code:
        return 'What a mix! Currently, there\'s ' + weather_data['summary'] + ' falling from the sky.'
    elif ('snow' in code or 'sleet' in code) and 'possible' not in code:
        return weather_data['summary'].capitalize() + ' and ' + weather_data['temp_and_unit'] + '. Bundle up.'
    elif 'very-light-rain':
        return 'Drizzlin\' yo.'
    elif (weather_data['units']['temperature'] == 'F' and weather_data['temp'] <= -20) or \
            (weather_data['units']['temperature'] == 'C' and weather_data['temp'] <= -28):
        return 'It\'s ' + weather_data['temp_and_unit'] + '. Too cold.'
    elif (weather_data['units']['temperature'] == 'F' and weather_data['temp'] >= 100) or \
            (weather_data['units']['temperature'] == 'C' and 37 <= weather_data['temp'] <= 50):
        return 'Holy moly it\'s ' + weather_data['temp_and_unit'] + '. I could literally (figuratively) melt.'
    elif weather_data['humidity'] <= 10:
        return 'It\'s dry as strained pasta. ' + str(weather_data['humidity']) + '% humid right now.'
    else:
        return 'normal'  # keep normal as is determines if the weather is normal (boring) or special (exciting!)
