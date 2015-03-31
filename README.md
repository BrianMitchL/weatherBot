# weatherBot [![Python Version](https://img.shields.io/badge/python-2.7%2C%203.4-blue.svg)](https://www.python.org)
A Twitter bot for weather. Yahoo! Weather is used for weather information. A WOEID is used for the location. Metic or imperial units can be specified.

_**Note: Any language or wording suggestions are appreciated and should be submitted as an issue. Feel free to add new choices for normal tweets and submit a pull request!**_

An example bot can be found at [@MorrisMNWeather](https://twitter.com/MorrisMNWeather).

## Install Dependencies
Run the following from the repository root directory to install the needed dependencies. If pip (or pip3 if python 3) is not installed, install it via yum, apt-get, homebrew, or whatever works on your system.
```shell
pip install -r requirements.txt
```

## Use
weatherBot.py has been tested for Python 2.7 (tested with 2.7.6) and Python 3 (tested with 3.4.3).

There are two modes in weatherBot. One is running from a console, and the other is by forking the process into a daemon. By default, the debug level is logged to the console and the info level is logged to the log file. The idea with this is that you run the script from the console to test and debug, and daemonize it to run it in "production." To run from as a daemon, pass in the `-d` flag:
```shell
python weatherBot.py -d
```
If you wish to run it in a console, just run normally:
```shell
python weatherBot.py
```

### Setting Variables and Customizing
There is a constants section near the top of the weatherBot.py file where you can set constants. The following are constants that can be set in the weatherBot.py file
* `WOEID` *defaults to 2454256 (Morris, MN)*
* `UNIT` *defaults to imperial. 'c' for metric, 'f' for imperial. This changes all units, not just temperature*
* `TWEET_LOCATION` *defaults to true*
* `LOG_PATHNAME` *defaults to '~/weatherBot.log'* **Note: The complete path name needs to be specified**

The keys.py file is where the Twitter app consumer key and secret as well as the access token key and secret are entered so tweets can be posted. See https://apps.twitter.com to get your keys and secrets.

The wording for tweets can be edited or added in the text list in `makeNormalTweet()` and the appropriate returns in `makeSpecialTweet()`. Additional special weather events can also be added as extra elif's in `makeSpecialTweet()`. Mind the order so more or less common ones are called when not desired.

Timing of daily scheduled tweets are done by setting the hour and minute in the else condition of the while loop in `main()`. *Note: if a tweet is set to go out when minute=59, set the .replace in the appropriate if statement below it to roll over the next minute to the hour. The minute field only accepts 0..59*

## Tools Used
* [Tweepy](https://github.com/tweepy/tweepy)
* [Yahoo! Weather](https://developer.yahoo.com/weather/)
