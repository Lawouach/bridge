import unittest
import test_base

from bridge import Element as E
from bridge.parser.bridge_elementtree import Parser

class TestElementTree(test_base.BridgeBaseTest):
    def setUp(self):
        E.parser = Parser

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestElementTree)
    unittest.TextTestRunner(verbosity=2).run(suite)
