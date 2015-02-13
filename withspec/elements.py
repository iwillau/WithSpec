import logging
from .util import arg_names

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
            raise TypeError, '%s() cannot take more than one positional ' \
                             'argument. (%d given)' % \
                             (self.__class__.__name__, len(args))

        if len(args) == 1:
            inherit = args[0]
            # ???: self.__dict__.update(inherit.__dict__)
            self.name = inherit.name
            self.context = inherit.context
            self.actual = inherit.actual
            self.args = inherit.args
            inherit.became = self  # should really only do this to Unknowns
        else:
            self.name = kwargs.pop('name')
            self.actual = kwargs.pop('actual')
            self.context = kwargs.pop('context')
            self.args = arg_names(self.actual)

        self.became = None

        if len(kwargs) > 0:
            raise TypeError, "%s() got an unexpected keyword argument '%s'" % \
                             (self.__class__.__name__, kwargs.keys()[0])

    def fullname(self):
        return '%s:%s' % (':'.join(self.location()), self.name)

    def parents(self):
        location = []
        context = self.context
        while context is not None:
            location.append(context)
            context = context.parent
        location.reverse()
        return location

    def resolve_fixtures(self):
        fixture_names = set()
        for context in self.parents():
            fixture_names.update(context.fixture_names)
        for context in self.parents():
            context.resolve_fixtures(fixture_names)

    def build(self):
        return None


class BeforeElement(ContextElement):
    pass


class AfterElement(ContextElement):
    pass


class AroundElement(ContextElement):
    pass


class FixtureElement(ContextElement):
    pass


class TestElement(ContextElement):
    def run(self, arguments):
        # Run just the single executable.
        # Arguments should have been gathered and provided
        # (Generally by execute below)
        pass 

    def execute(self):
        # Used to 'run' this test within its build
        responses = {}
        for element in self.stack:
            responses[element.name] = element.run(responses)

    def build(self):
        # Get ourselves ready to run
        self.tags = {'pending': False,
                     'skip': False}
        if len(self.args) == 0:
            self.tags['pending'] = True

        stack = []
        stack += self.context.before_stack()
        stack.append(self.context.around_stack(self))
        stack += self.context.after_stack()
        self.stack = stack
        return self


class UnknownElement(ContextElement):
    def build(self):
        if self.became is not None:
            return self.became.build()
        return TestElement(self).build()


