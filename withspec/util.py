import inspect


def arg_names(func):
    args, varargs, keywords, defaults = inspect.getargspec(func)
    return args

