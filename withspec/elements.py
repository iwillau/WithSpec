from .util import arg_names


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
            self.name = inherit.name
            self.context = inherit.context
            self.actual = inherit.actual
            self.args = inherit.args
        else:
            self.name = kwargs.pop('name')
            self.actual = kwargs.pop('actual')
            self.context = kwargs.pop('context')
            self.args = arg_names(self.actual)

        if len(kwargs) > 0:
            raise TypeError, "%s() got an unexpected keyword argument '%s'" %\
                             (self.__class__.__name__, kwargs.keys()[0])


class UnknownElement(ContextElement):
    pass


class BeforeElement(ContextElement):
    pass


class AfterElement(ContextElement):
    pass


class AroundElement(ContextElement):
    pass


class FixtureElement(ContextElement):
    pass


class TestElement(ContextElement):
    pass


