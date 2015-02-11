import inspect 
import logging
import unittest

log = logging.getLogger('pyspec.meppo')

CONTEXT_STACK = []
TEST_STACK = []

log.error('Entering Context')


def describe(described, **kwargs):
    return Description(described, **kwargs)


def resolve_args(func, resolver):
    args, varargs, keywords, defaults = inspect.getargspec(func)
    arg_values = {}
    for arg_name in args:
        arg_values[arg_name] = resolver.resolve_fixture(arg_name)
    return arg_values


class Assertions(unittest.TestCase):
    '''A Wrapper to make all of the standard assertions available to 
    the tests. Can also be used to wrap the Test, so another framework
    (such as nose) knows how to run this test'''
    def __init__(self, test):
        unittest.TestCase.__init__(self)
        self.test = test

    def setUp(self):
        self.test.before()

    def tearDown(self):
        self.test.after()

    def runTest(self):
        self.test.run()

    def assertContains(self, container, member, msg=None):
        return self.assertIn(member, container, msg)

    def assertNotContains(self, container, member, msg=None):
        return self.assertNotIn(member, container, msg)


class Hook(object):
    def __init__(self, wrapped=None):
        self.wrapped = wrapped

    def __call__(self, wrapped):
        self.wrapped = wrapped
        return wrapped

    def run(self, resolver):
        log.debug('Running Hook %s' % self.wrapped.__name__)
        kwargs = resolve_args(self.wrapped, resolver)
        self.wrapped(**kwargs)


class Context(object):
    def __init__(self, name, parent=None, assertor=Assertions):
        self.assertor = assertor
        self.parent = parent
        self.name = name
        self.fixtures = {}
        self.hooks = {
            'before': [],
            'after': [],
        }

    def __enter__(self):
        CONTEXT_STACK.append(self)
        return self

    def __exit__(self, ext, exv, tb):
        CONTEXT_STACK.pop()

    def __call__(self, description, **kwargs):
        return self.context(description, **kwargs)

    def context(self, description, **kwargs):
        parent = CONTEXT_STACK[-1]
        return Context(description, 
                       parent=parent, 
                       assertor=parent.assertor,
                       **kwargs)

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
        self.fixtures['subject'] = described


class Test(object):
    def __init__(self, parent, func=None, name=None, **kwargs):
        self._pending = kwargs.pop('pending', False)
        self.skip = kwargs.pop('skip', False)
        self.tags = kwargs.pop('tags', [])
        if 'tag' in kwargs:
            self.tags.append(kwargs.pop('tag'))
        self.assertor = parent.assertor(self)
        self.parent = parent
        self.name = name
        if func is not None:
            self.set_func(func)

    def set_func(self, func):
        if self.name is None:
            if func.__doc__ is not None:
                self.name = func.__doc__
            else:
                self.name = func.__name__.replace('_', ' ')
        self.func = func 

    @property
    def pending(self):
        if self.func is None:
            return True
        return self._pending

    def before(self):
        self.fixtures = {}
        self.resolving_fixtures = []
        self.parent.run_hooks('before', self)

    def run(self):
        log.debug('Running Test: %s' % self.name)
        test_args = resolve_args(self.func, self)
        if 'test' in test_args and test_args['test'] is None:
            test_args['test'] = self
        if 'context' in test_args and test_args['context'] is None:
            test_args['context'] = self.parent
        if 'subject' in test_args:
            test_args['subject'] = self.subject(test_args['subject'])
        self.func(**test_args)

    def after(self):
        self.parent.run_hooks('after', self)

    def location(self):
        starting = self
        while starting.parent is not None:
            yield starting.parent
            starting = starting.parent

    def resolve_fixture(self, name):
        if name not in self.fixtures:
            if name in self.resolving_fixtures:
                raise ValueError('Circular Resolution for fixture: %s' % name)
            self.resolving_fixtures.append(name)
            self.fixtures[name] = self.parent.resolve_fixture(name, self)
            self.resolving_fixtures.pop()
        return self.fixtures[name]

    def definition(self):
        '''Return where this test is defined'''
        filename = inspect.getsourcefile(self.func)
        lines, lineno = inspect.getsourcelines(self.func)
        return '%s:%s' % (filename, lineno)

    def __call__(self, subject):
        return self.subject(subject)

    def __getattr__(self, name):
        if name.startswith('assert'):
            return getattr(self.assertor, name)
        raise AttributeError, "'Test' object has no attribute '%s'" % name

    def subject(self, subject):
        return AssertionSubject(self.assertor, subject)


class AssertionSubject(object):
    def __init__(self, wrapped, subject):
        self.wrapped = wrapped
        self.subject = subject

    def __getattr__(self, name):
        # Attempt to locate the assertion name
        # Try in order:
        #   1. name as given
        #   2. 'assert' + name
        #   3. 'assert' + Name
        #   4. 'assert' + CamelCase from camel_case
        #
        #   Conversions
        #   is_something -> is_something
        #   is_something -> assert_is_something
        #   is_something -> assertIsSomething
        #
        #   isSomething -> isSomething
        #   isSomething -> assertIsSomething
        #
        #   In -> In
        #   In -> assertIn
        #
        #   _in -> _in
        #   _in -> assert_in
        #   _in -> assertIn
        #
        #   equal -> assert_equal
        #   equal -> assertEqual

        def combinations(name, prefix='assert'):
            yield name
            if name[0] == '_':
                yield prefix + name
            if '_' in name:
                yield '%s_%s' % (prefix, name)
                yield prefix + name.title().replace('_', '')
                yield prefix + ''.join([i.capitalize() for i in name.split('_')])

            if name[0].islower():
                yield prefix + name[0].upper() + name[1:]

            yield prefix + name
            yield name  # Yield name again last for a nice error message
        
        for name in combinations(name):
            log.debug("Trying assertion method '%s'" % name)
            print("Trying assertion method '%s'" % name)
            if hasattr(self.wrapped, name):
                break

        def wrap_assertion(*args, **kwargs):
            assert_func = getattr(self.wrapped, name)
            return assert_func(self.subject, *args, **kwargs)
        return wrap_assertion

    def __enter__(self):
        return self

    def __exit__(self, ext, exv, tb):
        return False

    def __eq__(self, value):
        return self.wrapped.assertEqual(self.subject, value)

    def __ne__(self, value):
        return self.wrapped.assertNotEqual(self.subject, value)


def it(*args, **kwargs):
    '''Helper Decorator for Adding a test to the 'current' context'''
    current_context = CONTEXT_STACK[-1]
    return current_context(*args, **kwargs)

