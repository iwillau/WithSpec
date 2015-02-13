import sys
import time
import logging
import textwrap
import ConfigParser
import random
from StringIO import StringIO
from argparse import ArgumentParser
from .collector import WithSpecCollector
from .wrappers import StdOutWrapper, LogWrapper, TraceBackWrapper
from .runner import WithSpecRunner
from .printer import Printer

log = logging.getLogger(__name__)

truthy = ('1', 'true', 't', 'y', 'yes', 'on')

LOG_FORMAT = '[1;31m%(levelname)-5.6s [0m%(message)s'


def asbool(value):
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    value = str(value).strip().lower()
    return value in truthy


def process_argv(argv, config):
    usage = '''Runs all Specs that it has been configured to find. '''
    parser = ArgumentParser(
        prog='withspec',
        description=textwrap.dedent(usage),
        usage='withspec [options] [files or directories]',
        )
    parser.add_argument(
        '-d', '--debug',
        action='count',
        default=0,
        help="Increase WithSpec's own debugging. Use multiple times to keep " \
             "increasing the level of debugging."
        )
    format = parser.add_mutually_exclusive_group()
    format.add_argument(
        '--format',
        action='store',
        choices=['progress', 'detailed'],
        default=config.pop('format', 'progress'),
        help="Format the output as detailed or progress.",
        )
    format.add_argument(
        '-f',
        action='store',
        choices={'p': 'progress', 'd': 'detailed'},
        default='p',
        help="Synonym for --format",
        dest='format',
        )
    parser.add_argument(
        '-o', '--order',
        action='store',
        choices=['defined', 'random'],
        default=config.pop('order', 'random'),
        help='Run the tests in random order, or the order in which they ' \
             'were defined.',
    )
    parser.add_argument(
        '--seed',
        action='store',
        type=int,
        default=config.pop('seed', random.randint(10000, 99999)),
        help='Provide the seed to the random orderer. This is provided ' \
             'whenever a test is run in random order, and can be provided ' \
             'to run them in the same order',
    )
    parser.add_argument(
        '-ff', '--fail-fast',
        action='store_true',
        default=config.pop('fail_fast', False),
        help='Exit the run as soon as a test has failed',
    )
    colour = parser.add_mutually_exclusive_group()
    colour.add_argument(
        '-c', '--colour', '--color',
        action='store_true',
        help='format output in colour',
        default=config.pop('colour', True),
    )
    colour.add_argument(
        '-nc', '--no-colour', '--no-color',
        action='store_false',
        help="don't format output in colour",
        dest='colour',
    )
    parser.add_argument(
        '-s', '--no-stdout', '--no-stderr',
        action='store_true',
        default=config.pop('no_stdout', False),
        help="Don't capture stdout or stderr",
    )
    parser.add_argument(
        '-l', '--no-logs',
        action='store_true',
        default=config.pop('no_logs', False),
        help="Don't capture logs",
    )
    parser.add_argument(
        '--dryrun', '--dry-run',
        action='store_true',
        default=config.pop('dryrun', False),
        help="Don't run any tests, simply collect them and output as if " \
             "they had been run",
    )
    parser.add_argument(
        '-b', '--backtrace', '--full-backtrace',
        action='store_true',
        default=config.pop('backtrace', False),
        help="Show the full backtrace to exceptions, without filtering " \
             "WithSpec internals",
    )
    parser.add_argument(
        'locations',
        nargs='*',
        default=config.pop('locations', ['spec']),
        help='The files or directories to search for tests.',
    )
    config.update(vars(parser.parse_args(argv)))
    return config


def run(argv=sys.argv[1:]):
    # Config Files in order of priority
    config_files = [
        'setup.cfg',
        'withspec.cfg',
        'withspec.ini',
        '~/.withspec',
    ]
    bools = ['colour', 'dryrun', 'fail_fast', 
             'no_logs', 'no_stdout', 'backtrace']
    lists = ['locations']
    aliases = {'color': 'colour'}
    config = {}

    file_parser = ConfigParser.SafeConfigParser()
    file_parser.read(config_files)
    if file_parser.has_section('withspec'):
        # Tidy up values and keys
        for key, value in file_parser.items('withspec'):
            key = key.strip().replace('-', '_').replace(' ', '_')
            key = aliases.get(key, key)
            if key in bools:
                value = asbool(value)
            if key in lists:
                value = value.strip().splitlines()
            config[key] = value
    
    config = process_argv(argv, config)
    if config['format'] == 'd':
        config['format'] = 'detailed'

    # WithSpec Logging
    # TODO: Let this be configured via ini file
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger = logging.getLogger('withspec')
    logger.addHandler(handler)
    logger.propagate = False
    if config['debug'] > 3:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel((4 - config['debug']) * 10)

    collector = WithSpecCollector()
    time_start = time.time()
    for location in config['locations']:
        collector.collect(location)
    time_loading = time_start - time.time()
    log.info('Collected %s tests in %.4f seconds' % (len(collector.tests),
                                                     time_loading))

    # Wrappers are built in this order deliberately
    # In the future these should be configurable, so you
    # could write a wrapper/plugin
    wrappers = []
    if not config['no_stdout']:
        wrappers.append(StdOutWrapper())
    if not config['no_logs']:
        wrappers.append(LogWrapper())
    exception_exclude = []
    if not config['backtrace']:
        exception_exclude.append('withspec')
    wrappers.append(TraceBackWrapper(exclude=exception_exclude))

    printer = Printer(colour=config['colour'],
                      detailed=config['format'] == 'detailed')

    runner = WithSpecRunner(dryrun=config['dryrun'], 
                            fail_fast=config['fail_fast'],
                            wrappers=wrappers)

    if config['order'] == 'random':
        random.seed(config['seed'])
        random.shuffle(collector.tests)

    time_start = time.time()
    runner.run(collector.tests, printer)
    time_testing = time_start - time.time()

    printer.new_line()
    printer.line('Finished in {:.3f} seconds (specs took {:.3f} seconds to ' \
                  'load)', time_testing, time_loading)
    printer.red('{total:d} tests, {pending:d} pending, ' \
                '{failed:d} failures, {skipped:d} skipped',
                total=len(collector.tests),
                pending=len(runner.pending),
                failed=len(runner.failed),
                skipped=len(runner.skipped),
                )
    printer.new_line()
    if config['order'] == 'random':
        printer.line('Randomized with seed {:d}'.format(config['seed']))
        printer.new_line()

