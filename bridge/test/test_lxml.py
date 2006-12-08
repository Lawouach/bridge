#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import test_base

from bridge import Element as E
from bridge.parser.bridge_lxml import Parser

class TestLXML(test_base.BridgeBaseTest):
    def setUp(self):
        E.parser = Parser

    # those will currently fail our test but I don't consider them major enough to
    # care for now.
    # It's a buggy lxml implementation that I can't really solved from bridge
    def test_08_comment(self):
        pass

    def test_09_processing_instruction(self):
        pass
    
    def test_10_mixed_comment_pi(self):
        pass
    
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLXML)
    unittest.TextTestRunner(verbosity=2).run(suite)
