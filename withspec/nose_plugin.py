import logging
import os
import unittest
from withspec.collector import WithSpecCollector
from nose.plugins import Plugin

log = logging.getLogger('nose.plugins.withspec')


class WithSpecWrapper(unittest.TestCase):
    def __init__(self, test):
        unittest.TestCase.__init__(self)
        self.test = test
        self.responses = {}
        self.after = []
        self.actual = []

    def setUp(self):
        if 'pending' in self.test.tags:
            self.skipTest('Test is pending')
        if 'skip' in self.test.tags:
            self.skipTest('Test is marked to skip')
        self.test.build()

    def runTest(self):
        self.test.run()


class NosePlugin(Plugin):
    """
    Include and run tests using WithSpec
    """
    name = 'withspec'

    def options(self, parser, env=os.environ):
        super(NosePlugin, self).options(parser, env)
        parser.add_option("--withspec", action="append",
                          default=env.get('NOSE_WITHSPEC'),
                          metavar="LOCATION",
                          dest="withspec_locations",
                          help="Collect WithSpec tests from location " 
                          "[NOSE_WITHSPEC]")  

    def configure(self, options, conf):
        super(NosePlugin, self).configure(options, conf)
        self.locations = []
        self.files = []
        locations = options.withspec_locations
        if locations is None:
            locations = ['spec']
        if self.enabled:
            log.debug('Looking for Specs in %s', ','.join(self.locations))
            for location in locations:
                if location.startswith('/'):
                    self.locations.append(location)
                else:
                    self.locations.append(os.path.join(conf.workingDir,
                                                       location))

    def wantFile(self, filename):
        if filename in self.locations:
            self.files.append(filename)
            return True
        
        for location in self.locations:
            if filename.startswith(location) and filename.endswith('.py'):
                self.files.append(filename)
                return True

    def wantDirectory(self, dirname):
        if dirname in self.locations:
            return True
        for location in self.locations:
            if dirname.startswith(location):
                return True
            if location.startswith(dirname):
                return True

    def loadTestsFromName(self, filename, module):
        if filename not in self.files:
            return
        log.debug("Loading WithSpec tests from %s", filename)

        collector = WithSpecCollector()
        collector.collect(filename)
        for test in collector.tests:
            yield WithSpecWrapper(test)

    def testName(self, test):
        if isinstance(test.test, WithSpecWrapper):
            return '%s (%s)' % (test.test.test.name,
                                test.test.test.context.name)

