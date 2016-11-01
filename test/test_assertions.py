import unittest
from withspec.assertions import AssertionSubject


class TestAssertionSubject(unittest.TestCase):

    def setUp(self):
        self.subject = AssertionSubject(None, None)

    def test_names_plain(self):
        names = [i for i in self.subject.assert_names('moron')]
        self.assertEqual(names, ['moron',
                                 'assert_moron',
                                 'assertMoron',
                                 'moron'])

    def test_names_underscore(self):
        names = [i for i in self.subject.assert_names('_moron')]
        self.assertEqual(names, ['_moron',
                                 'assert_moron',
                                 '_assert_moron',
                                 '_moron'])

    def test_names_uppercase(self):
        names = [i for i in self.subject.assert_names('Moron')]
        self.assertEqual(names, ['Moron',
                                 'assertMoron',
                                 'Moron'])

    def test_names_prefix(self):
        names = [i for i in self.subject.assert_names('moron', 'other')]
        self.assertEqual(names, ['moron',
                                 'other_moron',
                                 'otherMoron',
                                 'moron'])
