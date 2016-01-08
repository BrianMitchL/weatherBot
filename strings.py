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
        'Holy cow, it\'s ' + temp + ' and ' + summary + '. ' + hour_summary
        ]
    return random.choice(text)


def get_special_condition(weather_data):
    """
    :param weather_data: dict containing weather information
    :return: string containing the text of a tweet, or if no special event, return 'normal'
    """
    # TODO add temperature to most special events
    code = weather_data['icon']
    if (weather_data['units']['temperature'] == 'F' and weather_data['apparentTemperature'] <= -30) or \
            (weather_data['units']['temperature'] == 'C' and weather_data['apparentTemperature'] <= -34):
        return 'Wow, mother nature hates us. The windchill is ' + weather_data['apparentTemperature_and_unit'] \
               + ' and the wind is blowing at ' + weather_data['windSpeed_and_unit'] + ' from the ' \
               + weather_data['windBearing'] + '. My face hurts.'
    # elif (weather_data['units']['visibility'] == 'mi' and weather_data['nearestStormDistance'] <= 2) or \
    #         (weather_data['units']['visibility'] == 'km' and weather_data['nearestStormDistance'] <= 3):
    #     return 'Watch out, there\'s a storm ' + str(weather_data['nearestStormDistance']) + ' ' + \
    #             weather_data['units']['visibility'] + ' away. The wind is blowing at ' + \
    #            weather_data['windSpeed_and_unit'] + ' from the ' \
    #            + weather_data['windBearing'] + ' and there is precipitation at a rate of ' + \
    #            str(weather_data['precipIntensity']) + ' ' + weather_data['units']['precipIntensity'] + '.'
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
