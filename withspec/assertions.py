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
            # Try different variations of calling the assert function
            # This is potentially dangerous and possibly needs re-implementing
            # to be explicit (we may be _too_ magical here)
            #
            # 1. An Assert style function may legimately return TypeError
            # 2. We're hiding the actual function signature error, makes it
            #    difficult to debug the assert
            #
            # TODO: Perhaps a decorator preventing this behaviour?
            try:
                return assert_func(self.subject, *args, **kwargs)
            except TypeError as original_error:
                if len(args) == 0:
                    raise
                else:
                    try:
                        return assert_func(args[0], self.subject, 
                                           *args[1:], **kwargs)
                    except TypeError:
                        if len(args) == 1:
                            raise original_error
                        else:
                            try:
                                return assert_func(args[0], args[1], self.subject, 
                                                   *args[2:], **kwargs)
                            except TypeError:
                                raise original_error
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

    #def raises(self, exception, *args, **kwargs):
    #    return self.wrapped.assertRaises(exception, self.subject, *args, **kwargs)
