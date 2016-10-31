from invoke import task
from pylint import epylint as lint


@task
def clean(ctx, cache=False, bytecode=False, extra=''):
    patterns = ['build']
    if cache:
        patterns.append('cache.p')
    if bytecode:
        patterns.append('**/*.pyc')
    if extra:
        patterns.append(extra)
    for pattern in patterns:
        ctx.run("rm -rf %s" % pattern)


@task
def lint(ctx):
    pylint_options
    lint.py_run(pylint_options)