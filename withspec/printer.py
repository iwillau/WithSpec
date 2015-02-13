import sys


COLOR_NAMES = ["grey", "red", "green", "yellow", "blue", "magenta", "cyan",
               "white"]
COLOR_CODES = dict(zip(COLOR_NAMES, list(range(30, 38))))
COLOR_FMT = "\033[{:d}m{}\033[0m"


class Printer(object):
    '''Object to manage printing formatted output to the console
        The interface is similar to a logger, with each 'level' changing
        the colour (if colour is turned on)
        yellow, red, green, cyan, blue
    '''
    def __init__(self, colour=True, detailed=True, nested=True):
        self.colour = colour
        self.output = sys.stdout
        self.nested = nested
        self.indent = '  '

    def line(self, msg, *args, **kwargs):
        colour = kwargs.pop('colour', None)
        new_line = kwargs.pop('new_line', True)
        level = kwargs.pop('level', 0)
        if self.colour and colour in COLOR_CODES:
            msg = COLOR_FMT.format(COLOR_CODES[colour], msg)
        msg = msg.format(*args, **kwargs)
        if level > 0:
            self.output.write(self.indent * level)
        self.output.write(msg)
        if new_line:
            self.output.write('\n')

    def red(self, msg, *args, **kwargs):
        kwargs['colour'] = 'red'
        self.line(msg, *args, **kwargs)

    def yellow(self, msg, *args, **kwargs):
        kwargs['colour'] = 'yellow'
        self.line(msg, *args, **kwargs)

    def green(self, msg, *args, **kwargs):
        kwargs['colour'] = 'green'
        self.line(msg, *args, **kwargs)

    def blue(self, msg, alt=False, *args, **kwargs):
        kwargs['colour'] = 'blue'
        self.line(msg, *args, **kwargs)

    def cyan(self, msg, alt=False, *args, **kwargs):
        kwargs['colour'] = 'cyan'
        self.line(msg, *args, **kwargs)

    def new_line(self, number=1):
        for i in range(number):
            self.output.write('\n')

    def status(self, test):
        self.red('.', new_line=False)

