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
    def __init__(self, colour=True, detailed=True):
        self.colour = colour
        self.output = sys.stdout
        self.detailed = detailed
        self.indent = '  '
        self.nesting = []

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

    def success(self, test):
        if self.detailed:
            level = self.print_nested(test.parents())
            self.green(test.name, level=level)
        else:
            self.green('.', new_line=False)

    def warn(self, test):
        if self.detailed:
            level = self.print_nested(test.parents())
            self.yellow(test.name, level=level)
        else:
            self.yellow('*', new_line=False)

    def error(self, test, info=None):
        if self.detailed:
            level = self.print_nested(test.parents())
            if info is not None:
                self.red('%s (%s)' % (test.name, info), level=level)
            else:
                self.red(test.name, level=level)
        else:
            self.red('F', new_line=False)

    def print_nested(self, nesting):
        if self.nesting == nesting:
            return len(nesting) 
        deviated = False
        i = 0
        for i, new in enumerate(nesting):
            if i >= len(self.nesting):
                deviated = True
            elif new != self.nesting[i]:
                deviated = True
            if deviated:
                if i == 0:
                    self.new_line()
                self.line(new.name, level=i)
        self.nesting = nesting
        return i + 1

