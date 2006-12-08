#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import test_base

from bridge import Element as E
from bridge.parser.bridge_default import Parser

class TestDefault(test_base.BridgeBaseTest):
    def setUp(self):
        E.parser = Parser

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDefault)
    unittest.TextTestRunner(verbosity=2).run(suite)
