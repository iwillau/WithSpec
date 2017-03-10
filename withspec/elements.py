import inspect
import logging
from .util import arg_names
from .assertions import Assertions, AssertionSubject

log = logging.getLogger(__name__)


class ContextElement(object):
    '''Wrapper Class for any type of 'thing' a Context may need
    
    An element can be one of the following:
        before
        after
        around
        test
        fixture/let
    And can wrap either a function/class/method.
    '''
    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError('%s() cannot take more than one positional ' \
                             'argument. (%d given)' % \
                             (self.__class__.__name__, len(args)))

        if len(args) == 1:
            inherit = args[0]
            # ???: self.__dict__.update(inherit.__dict__)
            self.key = inherit.key
            self.name = inherit.name
            self.context = inherit.context
            self.actual = inherit.actual
            self.args = inherit.args
            inherit.became = self  # should really only do this to Unknowns
                                   # But we don't 'know' about them here
        else:
            self.key = kwargs.pop('key')
            self.name = kwargs.pop('name')
            self.actual = kwargs.pop('actual')
            self.context = kwargs.pop('context')
            if self.actual is not None:
                self.args = arg_names(self.actual)
            else:
                self.args = []

        self.became = None

        if len(kwargs) > 0:
            raise TypeError("%s() got an unexpected keyword argument '%s'" % \
                             (self.__class__.__name__, kwargs.keys()[0]))

    def fullname(self, spacer=' '):
        parents = spacer.join([i.name for i in self.parents()])
        return '%s%s%s' % (parents, spacer, self.name)

    def parents(self):
        location = []
        context = self.context
        while context is not None:
            location.append(context)
            context = context.parent
        location.reverse()
        return location

    def resolve_fixtures(self):
        fixture_keys = set()
        for context in self.parents():
            fixture_keys.update(context.fixture_keys)
        for context in self.parents():
            context.resolve_fixtures(fixture_keys)

    def build(self):
        return None

    def definition(self):
        '''Return where this element is defined'''
        lines, lineno = inspect.getsourcelines(self.actual)
        return '%s:%s' % (self.filename(), lineno)

    def filename(self):
        return inspect.getsourcefile(self.actual)

    def shared(self):
        return self.context.shared()


class BeforeElement(ContextElement):
    def execute(self, arguments):
        kwargs = {}
        for arg in self.args:
            kwargs[arg] = arguments.get(arg, None)
        return self.actual(**kwargs)


class AfterElement(ContextElement):
    def execute(self, arguments):
        kwargs = {}
        for arg in self.args:
            kwargs[arg] = arguments.get(arg, None)
        return self.actual(**kwargs)


class FixtureElement(ContextElement):
    def execute(self, arguments):
        kwargs = {}
        for arg in self.args:
            kwargs[arg] = arguments.get(arg, None)
        return self.actual(**kwargs)


class TestElement(ContextElement):
    def __init__(self, *args, **kwargs):
        self.tags = set()
        for tag in kwargs.pop('tags', []):
            self.tags.add(tag)
        super(TestElement, self).__init__(*args, **kwargs)

    def execute(self, arguments):
        # Run just the single executable.
        # Arguments should have been gathered and provided
        # (Generally by `run` below)

        log.info('Executing Test %s' % self.name)
        kwargs = {}
        assertor = Assertions()
        if 'test' in self.args and 'test' not in arguments:
            arguments['test'] = assertor

        for arg in self.args:
            value = arguments.get(arg, None)
            if value is None:
                log.warn('Could not resolve argument `%s` for `%s`', 
                         arg, self.name)
            kwargs[arg] = value

        if 'result' in self.args:
            kwargs['result'] = AssertionSubject(assertor, kwargs['result'])

        return self.actual(**kwargs)

    def run(self):
        # Used to 'run' this test within its build
        responses = {}
        for element in self.stack:
            responses[element.key] = element.execute(responses)

    def build(self):
        log.info('Building %s', self.fullname('->'))
        # Get ourselves ready to run
        if len(self.args) == 0:
            self.tags.add('pending')
            return self
        resolver = self.context.fixture_resolver()
        stack = []
        stack += self.context.before_stack(resolver)

        for arg in self.args:
            for fixture in resolver(arg):
                stack.append(fixture)

        stack.append(self)
        stack += self.context.after_stack(resolver)
        self.stack = stack
        return self


class UnknownElement(ContextElement):
    def build(self):
        if self.became is not None:
            return self.became.build()
        return TestElement(self).build()


