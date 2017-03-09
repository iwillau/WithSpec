import unittest
import logging
from .registry import get_registry

log = logging.getLogger(__name__)


class Assertions(unittest.TestCase):
    '''A Wrapper to make all of the standard assertions available to 
    the tests. This is the default Assertor. '''
    def __init__(self):
        unittest.TestCase.__init__(self)

    def runTest(self):
        # Unittest requires this method to exist
        raise TypeError('Assertions is not a Test')

    def assertContains(self, container, member, msg=None):
        return self.assertIn(member, container, msg)

    def assertNotContains(self, container, member, msg=None):
        return self.assertNotIn(member, container, msg)

    def assertLength(self, container, length, msg=None):
        return self.assertEqual(len(container), length, msg)

    def assertMethodReturns(self, obj, name, response, msg=None):
        self.assertEqual(getattr(obj, name)(), response)

    def __call__(self, subject):
        return AssertionSubject(self, subject)

    def assertRaises(self, callable, exception, *args, **kwargs):
        return unittest.TestCase.assertRaises(self, exception, callable, 
                                             *args, **kwargs)

    def assertRaises(self, callable, exception, *args, **kwargs):
        regex = kwargs.pop('regex', None)
        if regex is None:
            return unittest.TestCase.assertRaises(self, exception, 
                                                  callable, *args, **kwargs)
        else:
            return unittest.TestCase.assertRaisesRegex(self, exception, 
                                                       callable, regex,
                                                       *args, **kwargs)

    # Used as a context manager
    def raises(self, *args, **kwargs):
        if len(args) == 1:
            regex = kwargs.pop('regex', None)
            #We're being called directly, expecting a context
            if regex is None:
                return unittest.TestCase.assertRaises(self, *args, **kwargs)
            else:
                return unittest.TestCase.assertRaisesRegex(self, args[0],
                                                           regex, **kwargs)
        else:
            # We being called by AssertionSubject 
            return self.assertRaises(*args, **kwargs)

    def it_behaves_like(self, shared_name):
        registry = get_registry()
        context = registry.current_context()
        def my_func():
            print('MYYYFUNC')
            pass
        context.add_element('boooger', my_func)


class AssertionSubject(object):
    def __init__(self, wrapped, subject):
        self.wrapped = wrapped
        self.subject = subject
        self.to = ExpectationSyntaxWrapper(wrapped, subject)

    def __getattr__(self, name):
        # Attempt ao locate the assertion name
        # Try in order:
        #   1. name as given
        #   2. 'assert' + name
        #   3. 'assert' + Name
        #   4. 'assert' + CamelCase from camel_case
        #
        #   Conversions
        #   is_something -> is_something
        #   is_something -> assert_is_something
        #   is_something -> assert_something
        #   is_something -> assertIsSomething
        #   is_something -> assertSomething
        #
        #   isSomething -> isSomething
        #   isSomething -> assertIsSomething
        #   isSomething -> assertSomething
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

        for name in self.assert_names(name):
            log.debug("Trying assertion method '%s'" % name)
            # Reference: https://hynek.me/articles/hasattr/
            # 'hasattr' executes anyway and is no quicker than getattr
            assert_func = getattr(self.wrapped, name, None)
            if assert_func is not None:
                break

        def wrap_assertion(*args, **kwargs):
            return assert_func(self.subject, *args, **kwargs)
        return wrap_assertion

    def assert_names(self, name, prefix='assert'):
        yield name

        if name[0] == '_':
            yield prefix + name
            yield '_' + prefix + name
        elif '_' in name:
            yield '%s_%s' % (prefix, name)
            # Strip the 'is' from the start
            first, *rest = [i for i in name.split('_')]
            if first == 'is':
                yield prefix + '_' + ''.join(rest)
                yield prefix + 'Is' + ''.join([i.title() for i in rest])
                yield prefix + ''.join([i.title() for i in rest])
            else:
                yield prefix + first.title() + ''.join([i.title() for i in rest])
        elif name[0:2] == 'is':
            yield prefix + name[0].upper() + name[1:]
            yield prefix + name[2:]
        else:
            yield prefix + '_' + name
            yield prefix + name[0].upper() + name[1:]

        yield name  # Yield name again last for a nice error message
        
    def __enter__(self):
        return self

    def __exit__(self, ext, exv, tb):
        return False

    def __eq__(self, value):
        return self.wrapped.assertEqual(self.subject, value)

    def __ne__(self, value):
        return self.wrapped.assertNotEqual(self.subject, value)


class ExpectationSyntaxWrapper():
    def __init__(self, wrapped, subject):
        self.wrapped = wrapped
        self.subject = subject

    def be_true(self):
        return self.wrapped.assertTrue(self.subject)
