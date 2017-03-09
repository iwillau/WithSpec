import unittest
import logging

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
            if hasattr(self.wrapped, name):
                break

        def wrap_assertion(*args, **kwargs):
            assert_func = getattr(self.wrapped, name)
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


