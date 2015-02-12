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
    def __init__(self, name, parent=None, assertor=Assertions):
        self.assertor = assertor
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
                       assertor=parent.assertor,
                       **kwargs)

    def add_element(self, name, element):
        if not isinstance(element, ContextElement):
            if element.__doc__ is not None and len(element.__doc__) > 0:
                name = element.__doc__
            element = UnknownElement(name=name, actual=element, context=self)
        self.elements.append(element)

    def finalise(self):
        organised = {
            'before': [],
            'after': [],
            'around': [],
            'fixtures': {},
            'tests': []
        }
        arguments = set()
        for element in self.elements:
            arguments.update(element.args)
        self.arguments = frozenset(arguments)

        for element in self.elements:
            name = element.name
            if isinstance(element, UnknownElement):
                if name == 'before':
                    element = BeforeElement(element)
                elif name == 'after':
                    element = AfterElement(element)
                elif name == 'around':
                    element = AroundElement(element)
                elif name in arguments:
                    element = FixtureElement(element)
                # Else: Still Unknown
            if isinstance(element, BeforeElement):
                organised['before'].append(element)
            elif isinstance(element, AfterElement):
                organised['after'].append(element)
            elif isinstance(element, AroundElement):
                organised['around'].append(element)
            elif isinstance(element, FixtureElement):
                organised['fixtures'][element.name] = element
            else:
                organised['tests'].append(element)
        self.elements = organised

    @property
    def it(self):
        return self.test

    @property
    def test(self):
        context = CONTEXT_STACK[-1]
        def decorator(*args, **kwargs):
            if len(args) > 2:
                raise TypeError, 'test() takes at most 2 positional ' \
                                 'arguments (%d given)' % len(args)
            for arg in args:
                if inspect.isfunction(arg): 
                    kwargs['func'] = arg
                else:
                    kwargs['name'] = arg

            if 'func' not in kwargs:  # Decorating
                def wrap(wrapped):
                    context.add_test(func=wrapped, **kwargs)
                    return wrapped
                return wrap
            else:
                return context.add_test(**kwargs)
        return decorator

    def add_test(self, func=None, name=None, **kwargs):
        test = Test(self, func, name, **kwargs)
        TEST_STACK.append(test)
        return test

    @property
    def let(self):
        context = CONTEXT_STACK[-1]
        def wrap_decorator(first_arg, value=None):
            if inspect.isfunction(first_arg):
                context.define(first_arg.__name__, first_arg)
                return first_arg
            elif value is not None:
                context.define(first_arg, value)
                return None
            else:
                def wrap(wrapped):
                    context.define(first_arg, wrapped)
                    return wrapped
                return wrap
        return wrap_decorator

    def define(self, name, func):
        if name in self.fixtures:
            log.debug('Overwriting Fixture: %s' % name)
        self.fixtures[name] = func

    @property
    def before(self):
        return self.__hook_decorator('before')

    @property
    def after(self):
        return self.__hook_decorator('after')

    def __hook_decorator(self, hook_type):
        context = CONTEXT_STACK[-1]
        def wrap(first_arg, **kwargs):
            if inspect.isfunction(first_arg):
                context.hook(hook_type, first_arg)
                return first_arg
            else:
                return context.hook(hook_type, None, **kwargs)
        return wrap

    def hook(self, hook_type, hook_callable, **kwargs):
        if hook_type not in self.hooks:
            raise ValueError('Invalid Hook Name')
        hook = Hook(wrapped=hook_callable, **kwargs)
        self.hooks[hook_type].append(hook)
        return hook

    def run_hooks(self, hook_type, resolver):
        if hook_type not in self.hooks:
            raise ValueError('Invalid Hook Name')
        if self.parent is not None:
            self.parent.run_hooks(hook_type, resolver)
        for hook in self.hooks[hook_type]:
            hook.run(resolver)

    def resolve_fixture(self, name, resolver):
        if name not in self.fixtures:
            if self.parent is None:
                return None
            return self.parent.resolve_fixture(name, resolver)
        log.debug('Calling Fixture: %s' % name)
        fixture = self.fixtures[name]
        if callable(fixture):
            kwargs = resolve_args(fixture, resolver)
            return fixture(**kwargs)
        return fixture


class Description(Context):
    def __init__(self, described, **kwargs):
        name = str(described)
        Context.__init__(self, name, **kwargs)


