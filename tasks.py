from invoke import task


@task(help={
    'bytecode': 'Remove bytecode files matching the pattern \'**/*.pyc\'.',
    'cache': 'Remove the \'.wbcache.p\' file.',
    'extra': 'Remove any extra files passed in here.'
})
def clean(ctx, cache=False, bytecode=False, extra=''):
    """
    Clean (delete) files. If passed with no arguments, nothing is deleted.
    """
    patterns = []
    if cache:
        patterns.append('.wbcache.p')
    if bytecode:
        patterns.append('**/*.pyc')
    if extra:
        patterns.append(extra)
    for pattern in patterns:
        ctx.run('rm -rf %s' % pattern)


@task(help={
    'pylintrc': 'Path to a pylintrc file for configuring PyLint.',
    'extra': 'Extra Python files to lint in addition to the default.'
})
def lint(ctx, pylintrc='.pylintrc', extra=''):
    """
    Use PyLint to check for errors and enforce a coding standard.
    This will, by default, use the PyLint configuration found in '.pylintrc',
    but can accept a different path.
    """
    from pylint.lint import Run
    args = ['--reports=no', '--rcfile=' + pylintrc]
    files = ['weatherBot.py', 'utils.py', 'models.py', 'keys.py']
    if extra:
        files.append(extra)
    Run(args + files)


@task(help={
    'yamllintrc': 'Path to a yamllintrc file for configuring PyLint.',
    'filename': 'Path to the strings YAML file to validate.'
})
def validateyaml(ctx, yamllintrc='.yamllint', filename='strings.yml'):
    """
    Use yamllint to check for errors and enforce a markup standard for the strings YAML file.
    By default this will use the '.yamllint' config file to validate 'strings.yml'.
    """
    ctx.run('yamllint --config-file %s %s' % (yamllintrc, filename))


@task(help={
    'report': 'Flag to print a coverage report'
})
def test(ctx, report=False):
    """
    Runs tests and reports on code coverage.
    Keys need to be entered in 'keys.py' or set as environmental variables.
    """
    ctx.run('coverage run --source=weatherBot,models,utils,keys test.py')
    if report:
        ctx.run('coverage report -m')
