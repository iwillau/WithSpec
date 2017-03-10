import logging
from .assertions import Assertions
from .registry import get_registry
from .elements import (
    ContextElement,
    UnknownElement, 
    BeforeElement,
    AfterElement,
    FixtureElement,
    TestElement,
)


log = logging.getLogger(__name__)


class Context(object):
    is_shared = False
    def __init__(self, name, parent=None):
        self.parent = parent
        self.name = name
        self.elements = []
        self.behaves_like_names = []

    def __enter__(self):
        log.debug('Entering Context: %s', self.name)
        registry = get_registry()
        registry.add_context(self)
        return Assertions()

    def __exit__(self, ext, exv, tb):
        log.debug('Exiting Context: %s', self.name)
        registry = get_registry()
        registry.pop_context()
        self.finalise()

    def context(self, description, **kwargs):
        registry = get_registry()
        parent = registry.current_context()
        return Context(description, 
                       parent=parent, 
                       **kwargs)

    def shared(self):
        # Any parent at all being shared makes _us_ shared
        if self.is_shared is True:
            return self.name
        elif self.parent is not None:
            return self.parent.shared()
        else:
            return None

    def behaves_like(self, name):
        # Add a shared 'group' to this context for processing later
        self.behaves_like_names.append(name)

    def pop_behaviours(self):
        while self.behaves_like_names:
            yield self.behaves_like_names.pop()

    def add_element(self, key, element):
        if not isinstance(element, ContextElement):
            if element.__doc__ is not None and len(element.__doc__) > 0:
                name = element.__doc__
            else:
                name = key.replace('_', ' ')
            element = UnknownElement(key=key, name=name, 
                                     actual=element, context=self)
        self.elements.append(element)
        return element

    def finalise(self):
        organised = {
            'before': [],
            'after': [],
            'fixtures': {},
            'tests': []
        }
        # Build a set of an arguments referenced locally
        # Used to determine the 'easy' fixture's, ie, the ones
        # referenced locally or in our parent chain
        arguments = set()
        for element in self.elements:
            arguments.update(element.args)
        self.fixture_keys = frozenset(arguments)

        for element in self.elements:
            key = element.key
            if isinstance(element, UnknownElement):
                # Identify the explicit elements
                if key == 'before':
                    element = BeforeElement(element)
                elif key == 'after':
                    element = AfterElement(element)
                elif key in self.fixture_keys:
                    element = FixtureElement(element)

            if isinstance(element, BeforeElement):
                organised['before'].append(element)
            elif isinstance(element, AfterElement):
                organised['after'].append(element)
            elif isinstance(element, FixtureElement):
                organised['fixtures'][element.key] = element
            else:
                organised['tests'].append(element)
        self.elements = organised

    def resolve_fixtures(self, fixture_keys):
        '''Given a set of fixture keys that may be referenced, check that
        any test aren't being referenced, and if they are, change them to
        a fixture'''
        fixture = None
        for test in self.elements['tests']:
            if test.key in fixture_keys:
                fixture = FixtureElement(test)
                break

        if fixture is not None:
            self.elements['tests'].remove(test)
            self.elements['fixtures'][fixture.key] = fixture

    def fixture_resolver(self):
        found = set()
        def resolve(arg):
            '''Given a single argument name, traverse the context stack for
            a fixture with the correct name.
            Only return the fixture
            '''
            if arg in found:
                return
            context = self
            while context is not None:
                fixture = context.elements['fixtures'].get(arg, None)
                if fixture is not None:
                    found.add(fixture.name)  # Stop the double recursion
                    for arg in fixture.args:
                        for sub_fixture in resolve(arg):
                            yield sub_fixture
                    yield fixture
                    break
                context = context.parent

        return resolve

    def before_stack(self, resolver):
        if self.parent is not None:
            for element in self.parent.before_stack(resolver):
                yield element
        for element in self.elements['before']:
            for arg in element.args:
                for fixture in resolver(arg):
                    yield fixture
            yield element

    def after_stack(self, resolver):
        if self.parent is not None:
            for element in self.parent.after_stack(resolver):
                yield element
        for element in self.elements['after']:
            for arg in element.args:
                for fixture in resolver(arg):
                    yield fixture
            yield element


class Description(Context):
    def __init__(self, described, **kwargs):
        name = str(described)
        Context.__init__(self, name, **kwargs)
        def subject():
            if callable(described):
                return described()
            return described

        self.elements.append(FixtureElement(key='subject',
                                            name='subject',
                                            actual=subject,
                                            context=self))


class SharedExamples(Context):
    '''A special Context that doesn't get executed but can be included
    in other contexts
    '''
    is_shared = True

    def create_context(self, parent):
        context = Context(self.name, parent)
        context.elements = self.elements


