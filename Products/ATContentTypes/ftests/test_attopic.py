"""
"""

__author__ = 'Christian Heimes'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase

tests = []

class TestATTopicFunctional(atcttestcase.ATCTFuncionalTestCase):

    def afterSetUp(self):
        # adding topics is restricted
        self.setRoles(['Manager', 'Member',])
        atcttestcase.ATCTFuncionalTestCase.afterSetUp(self)
    
    portal_type = 'ATTopic'
    views = ('atct_topic_view', )

tests.append(TestATTopicFunctional)

if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        for test in tests:
            suite.addTest(unittest.makeSuite(test))
        return suite
