

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
        raise AttributeError("'Test' object has no attribute '%s'" % name)

    def subject(self, subject):
        return AssertionSubject(self.assertor, subject)


