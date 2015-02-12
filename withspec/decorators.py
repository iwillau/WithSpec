from context import (
    Description,
    Context,
)


from test import (
    Test,
)


def describe(described, **kwargs):
    return Description(described, **kwargs)


def context(description, **kwargs):
    return Context(description, **kwargs)


def it(*args, **kwargs):
    '''Helper Decorator for Adding a test to the 'current' context'''
    return 'ShouldBeATest'

