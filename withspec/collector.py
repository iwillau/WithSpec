import os
import sys
import logging
import inspect
from .registry import get_registry
from .elements import TestElement, UnknownElement

log = logging.getLogger(__name__)


class WithSpecCatcher(dict):
    def __init__(self, collector, *args, **kwargs):
        self.registry = get_registry()
        self.collector = collector
        self.elements = []
        dict.__init__(self, *args, **kwargs)
        self.module = self['__name__']
        self['__withspec_catcher__'] = self

    def __setitem__(self, name, value):
        dict.__setitem__(self, name, value)
        if not name.startswith('__'):
            context = self.registry.current_context()
            if value.__module__ != self.module:
                return
            if context is None:
                return
            log.debug('Caught `%s`', name)
            self.elements.append(context.add_element(name, value))


class WithSpecCollector(object):
    def __init__(self, random=False, seed=None):
        self.random = random
        self.seed = seed
        self.module = '__spec__'
        self.tests = []

    def collect(self, location):
        log.info('Browsing for tests in {}'.format(location))
        if os.path.isdir(location):
            return self.collect_from_dir(location)
        if os.path.isfile(location):
            return self.collect_from_file(location)
        if ':' in location:
            # Try to see if there is a line number reference
            filename, line_no = location.rsplit(':', 1)
            if os.path.isfile(filename):
                return self.collect_from_file(filename, int(line_no))
        raise ValueError('No such file or directory: {}'.format(location))

    def collect_from_dir(self, dirname):
        log.debug('Walking over {}'.format(dirname))
        valid_files = []
        for root, dirs, files in os.walk(dirname, followlinks=True):
            for filename in files:
                if filename.endswith('.py'):
                    valid_files.append(os.path.join(root, filename))
        for filename in valid_files:
            self.collect_from_file(filename)

    def collect_from_file(self, filepath, line=None):
        abspath = os.path.abspath(filepath)
        cwd = os.getcwd()
        log.debug('Collecting from file {}'.format(filepath))
        dirname, filename = os.path.split(abspath)
        os.chdir(dirname)
        sys.path.insert(0, dirname)
        
        try:
            with open(filename, 'r') as fh:
                 file_globals = WithSpecCatcher(
                     collector=self,
                     __name__=self.module,
                     __file__=filepath,
                     __package__=None,
                 )
                 code = compile(fh.read(), filepath, 'exec')
                 exec(code, file_globals)
        finally:
            os.chdir(cwd)
            try:
                sys.path.remove(dirname)
            except ValueError:
                pass
        # Allow each Captured Element a chance to Resolve its args.
        # This allows the Contexts to determine what args have been
        # called, which lets them decide if a function is a fixture 
        # or a test (if not labeled as such).
        if line is None:
            self.resolve_and_build(file_globals.elements)
            return

        # Locate a test on that line number
        for element in file_globals.elements:
            lines, lineno = inspect.getsourcelines(element.actual)
            if lineno <= line <= (lineno + len(lines) - 1):
                self.resolve_and_build([element])
                return

        # Locate a the first test after the given line and then catch
        # all the test in that context
        context = None
        for element in file_globals.elements:
            lines, lineno = inspect.getsourcelines(element.actual)
            if lineno > line:
                context = element.context
                break
        if context is None:
            return
        elements = []
        for element in file_globals.elements:
            if element.context == context:
                elements.append(element)
        self.resolve_and_build(elements)

    def resolve_and_build(self, elements):
        for element in elements:
            element.resolve_fixtures()

        for element in elements:
            test = element.build()
            if test is not None:
                self.tests.append(test)


