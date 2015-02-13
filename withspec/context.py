import logging
from .assertions import Assertions
from .registry import get_registry
from .elements import (
    ContextElement,
    UnknownElement, 
    BeforeElement,
    AfterElement,
    AroundElement,
    FixtureElement,
    TestElement,
)


log = logging.getLogger(__name__)


class Context(object):
    def __init__(self, name, parent=None):
        self.parent = parent
        self.name = name
        self.elements = []

    def __enter__(self):
        log.debug('Entering Context: %s', self.name)
        registry = get_registry()
        registry.add_context(self)
        return self

    def __exit__(self, ext, exv, tb):
        log.debug('<Exiting Context: %s', self.name)
        registry = get_registry()
        registry.pop_context()
        self.finalise()

    def __call__(self, description, **kwargs):
        return self.context(description, **kwargs)

    def context(self, description, **kwargs):
        registry = get_registry()
        parent = registry.current_context()
        return Context(description, 
                       parent=parent, 
                       **kwargs)

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
            'around': [],
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
                elif key == 'around':
                    element = AroundElement(element)
                elif key in self.fixture_keys:
                    element = FixtureElement(element)

            if isinstance(element, BeforeElement):
                organised['before'].append(element)
            elif isinstance(element, AfterElement):
                organised['after'].append(element)
            elif isinstance(element, AroundElement):
                organised['around'].append(element)
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

    def before_stack(self):
        return []

    def after_stack(self):
        return []

    def around_stack(self, wrapped):
        return wrapped


class Description(Context):
    def __init__(self, described, **kwargs):
        name = str(described)
        Context.__init__(self, name, **kwargs)


