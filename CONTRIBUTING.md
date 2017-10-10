# How to Contribute

Third party suggestions, additions, and edits are highly encouraged. If you have any thoughts about weatherBot, please submit an issue or contact [@BrianMitchL](https://twitter.com/BrianMitchL) on Twitter.

## Getting Started

Make sure to install all of the dependencies of weatherBot.
```shell
pip3 install -r requirements.txt
pip3 install -r requirements-dev.txt
```

Contributions must be committed in a topic branch based on `development`. `git checkout -b my_contribution development`

## Linting/Validating

### Python Code

It is required that all code will pass a lint and validation test. Some exceptions can be made, but this should be kept to a minimum.

Code must conform to [PEP8](https://www.python.org/dev/peps/pep-0008/), but ultimately the linter.
Here are the important things:

1. Lines may have up to 120 characters
2. Spaces must be used for indentation
3. Use single-quotes for strings
4. Include docstrings in every class, method, function, and file
5. Use underscores to separate variable names vs camel-case. (Yes, I know this contradicts the name _weatherBot_)

Lint your code with the following:
```sh
invoke lint
```

If you are adding a new Python file, run `invoke lint --extra=newfile.py`

### Strings.yml

Mind the 140 character limit that Twitter enforces. Anything over 140 characters will be truncated.

Emoji must be escaped until the PyYAML libary is updated (https://github.com/yaml/pyyaml/issues/25).

If you are contributing to the `strings.yml` file, you must validate the file by running:
```shell
invoke validate_yaml
```

If you are creating new strings files of your own, run `invoke validate_yaml --filename=filename.yml`.

## Testing
Tests have been written for nearly all of the non-looping/logic code. It is expected to add tests for your contributions (with the exception of adding new text to `strings.yml`). Tests must be run using environmental variables. To set the environmental variables per command, prepend the command with the following, replacing `xxxx` with your keys.

```sh
WEATHERBOT_CONSUMER_KEY=xxxx WEATHERBOT_CONSUMER_SECRET=xxxx WEATHERBOT_ACCESS_TOKEN=xxxx WEATHERBOT_ACCESS_TOKEN_SECRET=xxxx WEATHERBOT_DARKSKY_KEY=xxxx your_command_here
```

```sh
invoke test
# For a coverage report
invoke test --report
```
