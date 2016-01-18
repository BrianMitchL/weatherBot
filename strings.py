# weatherBot strings
# Copyright 2015-2016 Brian Mitchell under the MIT license
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
    hour_summary = weather_data['hour_summary']
    text = [
        'The weather is boring. ' + temp + ' and ' + summary + '. ' + hour_summary,
        'Great, it\'s ' + summary + ' and ' + temp + '. ' + hour_summary,
        'What a normal day, it\'s ' + summary + ' and ' + temp + '. ' + hour_summary,
        'Whoopie do, it\'s ' + temp + ' and ' + summary + '. ' + hour_summary,
        temp + ' and ' + summary + '. ' + hour_summary,
        temp + ' and ' + summary + '. ' + hour_summary + ' What did you expect?',
        'Welcome to ' + location + ', where it\'s ' + summary + ' and ' + temp + '. ' + hour_summary,
        'Breaking news: it\'s ' + summary + ' and ' + temp + '. ' + hour_summary,
        'We got some ' + summary + ' at ' + temp + ' going on. ' + hour_summary,
        'Well, would you look at that, it\'s ' + temp + ' and ' + summary + '. ' + hour_summary,
        'Great Scott, it\'s ' + summary + ' and ' + temp + '! ' + hour_summary,
        'It\'s ' + temp + ' and ' + summary + ', oh boy! ' + hour_summary,
        'Only in ' + location + ' would it be ' + temp + ' and ' + summary + ' right now. ' + hour_summary,
        'Golly gee wilikers, it\'s ' + temp + ' and ' + summary + '. ' + hour_summary,
        'It is currently ' + summary + ' and ' + temp + '. ' + hour_summary,
        'Big surprise, it\'s ' + summary + ' and ' + temp + '. ' + hour_summary,
        'Look up, it\'s ' + summary + ' and ' + temp + '. ' + hour_summary,
        'Dang, it\'s ' + temp + ' and ' + summary + '. ' + hour_summary,
        'Blimey, it\'s ' + temp + ' and ' + summary + '. ' + hour_summary,
        'For Pete\'s sake, it\'s' + summary + ' and ' + temp + ' again. ' + hour_summary,
        'Holy cow, it\'s ' + temp + ' and ' + summary + '. ' + hour_summary,
        'What a doozy, it\'s ' + temp + ' and ' + summary + '. ' + hour_summary
        ]
    return random.choice(text)


def get_special_condition(weather_data):
    """
    :param weather_data: dict containing weather information
    :return: tuple of strings containing a short description of the event
            and the text of a tweet, or if no special event, return 'normal'
    """
    # TODO add temperature to most special events
    code = weather_data['icon']
    if (weather_data['units']['temperature'] == 'F' and weather_data['apparentTemperature'] <= -30) or \
            (weather_data['units']['temperature'] == 'C' and weather_data['apparentTemperature'] <= -34):
        text = 'Brr! The windchill is ' + weather_data['apparentTemperature_and_unit'] \
               + ' and the wind is blowing at ' + weather_data['windSpeed_and_unit'] + ' from the ' \
               + weather_data['windBearing'] + '. Stay safe out there!'
        return 'wind-chill', text
    # elif (weather_data['units']['visibility'] == 'mi' and weather_data['nearestStormDistance'] <= 2) or \
    #         (weather_data['units']['visibility'] == 'km' and weather_data['nearestStormDistance'] <= 3):
    #     return 'Watch out, there\'s a storm ' + str(weather_data['nearestStormDistance']) + ' ' + \
    #             weather_data['units']['visibility'] + ' away. The wind is blowing at ' + \
    #            weather_data['windSpeed_and_unit'] + ' from the ' \
    #            + weather_data['windBearing'] + ' and there is precipitation at a rate of ' + \
    #            str(weather_data['precipIntensity']) + ' ' + weather_data['units']['precipIntensity'] + '.'
    elif 'medium-wind' in code:
        text = 'Looks like we\'ve got some medium wind at ' + weather_data['windSpeed_and_unit'] + \
               ' coming from the ' + weather_data['windBearing'] + '.'
        return 'medium-wind', text
    elif 'heavy-wind' in code or \
            (weather_data['units']['windSpeed'] == 'mph' and weather_data['windSpeed'] >= 35.0) or \
            (weather_data['units']['windSpeed'] == 'km/h' and weather_data['windSpeed'] >= 56.0) or \
            (weather_data['units']['windSpeed'] == 'm/s' and weather_data['windSpeed'] >= 15.0):
        text = 'Hold onto your hats! The wind is blowing at ' + weather_data['windSpeed_and_unit'] + \
               ' coming from the ' + weather_data['windBearing'] + '.'
        return 'heavy-wind', text
    elif 'heavy-rain' in code:
        text = 'Run for cover and stay dry! It\'s ' + weather_data['temp_and_unit'] + ' and raining heavily right now.'
        return 'heavy-rain', text
    elif 'fog' in code:
        text = 'Do you even fog bro?'
        return 'fog', text
    elif 'mixed-precipitation' in code:
        text = 'What a mix! Currently, there\'s ' + weather_data['summary'] + ' falling from the sky.'
        return 'mixed-precipitation', text
    elif 'snow' in code and 'possible' not in code:
        text = weather_data['summary'].capitalize() + ' and ' + weather_data['temp_and_unit'] + '. Bundle up.'
        return 'snow', text
    elif 'sleet' in code and 'possible' not in code:
        text = weather_data['summary'].capitalize() + ' and ' + weather_data['temp_and_unit'] + '. Stay safe.'
        return 'sleet', text
    elif 'very-light-rain' and (weather_data['units']['temperature'] == 'F' and weather_data['temp'] >= 32) or \
            (weather_data['units']['temperature'] == 'C' and weather_data['temp'] >= 0):
        text = 'Drizzlin\' yo.'
        return 'drizzle', text
    elif (weather_data['units']['temperature'] == 'F' and weather_data['temp'] <= -20) or \
            (weather_data['units']['temperature'] == 'C' and weather_data['temp'] <= -28):
        text = 'It\'s ' + weather_data['temp_and_unit'] + '. Too cold.'
        return 'cold', text
    elif (weather_data['units']['temperature'] == 'F' and weather_data['temp'] >= 100) or \
            (weather_data['units']['temperature'] == 'C' and 37 <= weather_data['temp'] <= 50):
        text = 'Holy moly it\'s ' + weather_data['temp_and_unit'] + '. I could literally (figuratively) melt.'
        return 'hot', text
    elif weather_data['humidity'] <= 10:
        text = 'It\'s dry as strained pasta. ' + str(weather_data['humidity']) + '% humid right now.'
        return 'dry', text
    else:
        return 'normal', ''  # normal determines if the weather is normal (boring) or special (exciting!)
