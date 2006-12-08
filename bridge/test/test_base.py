#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from bridge.common import XMLNS_NS, XMLNS_PREFIX
from bridge import Document as D
from bridge import Element as E
from bridge import Attribute as A
from bridge import Comment as C
from bridge import PI

class BridgeBaseTest(unittest.TestCase):
    def assertElementEquals(self, source, other):
        if source.xml_name != other.xml_name:
            self.fail("Expected local_name '%s', got '%s'" % (source.xml_name, other.xml_name))
        if source.xml_prefix != other.xml_prefix:
            self.fail("Expected prefix '%s', got '%s'" % (source.xml_prefix, other.xml_prefix))
        if source.xml_ns != other.xml_ns:
            self.fail("Expected namespace '%s', got '%s'" % (source.xml_ns, other.xml_ns))
            
    def assertAttributesEqual(self, source, other):
        for s_attr in source.xml_attributes:
            o_attr = other.get_attribute_ns(s_attr.xml_name, s_attr.xml_ns)
            if not o_attr:
                self.fail("Missing attribute")
            if o_attr.xml_prefix != s_attr.xml_prefix:
                self.fail("Attributes prefix mismatch")

    def _common_test(self, a, e):
        self.assertEqual(len(e.xml_children), 1)
        self.assertEqual(type(e), D)
        self.assertElementEquals(e.xml_children[0], a)
        
    def test_00_basic(self):
        a = E(u'a')
        e = E.load('<a/>')
        self._common_test(a, e)

    def test_01_basic_xmlns(self):
        a = E(u'a', namespace=u"ns")
        e = E.load('<a xmlns="ns" />')
        self._common_test(a, e)

    def test_02_basic_prefix(self):
        a = E(u'a', prefix=u"p", namespace=u"ns")
        e = E.load('<p:a xmlns:p="ns" />')
        self._common_test(a, e)
    
    def test_03_basic_content(self):
        a = E(u'a', content=u"hello")
        e = E.load('<a>hello</a>')
        self._common_test(a, e)
        self.assertEqual(a.xml_text, e.xml_children[0].xml_text)

    def test_04_basic_tree(self):
        a = E(u'a')
        b = E(u'b', parent=a)
        e = E.load('<a><b/></a>')
        self._common_test(a, e)
        self.assertEqual(len(e.xml_children[0].xml_children), 1)
        self.assertElementEquals(e.xml_children[0], a)
        self.assertEqual(type(e.xml_children[0]), E)
        self.assertElementEquals(e.xml_children[0].xml_children[0], b)
        self.assertEqual(type(e.xml_children[0].xml_children[0]), E)
    
    def test_05_basic_tree_with_content(self):
        a = E(u'a')
        b = E(u'b', content=u"hello", parent=a)
        e = E.load('<a><b>hello</b></a>')
        self._common_test(a, e)
        self.assertEqual(len(e.xml_children[0].xml_children), 1)
        self.assertElementEquals(e.xml_children[0], a)
        self.assertEqual(type(e.xml_children[0]), E)
        self.assertElementEquals(e.xml_children[0].xml_children[0], b)
        self.assertEqual(type(e.xml_children[0].xml_children[0]), E)
        self.assertEqual(b.xml_text, e.xml_children[0].xml_children[0].xml_text)
    
    def test_06_tree_with_xmlns(self):
        a = E(u'a', namespace=u'u')
        b = E(u'b', prefix=u'c', namespace=u'ns', parent=a)
        e = E.load('<a xmlns="u"><c:b xmlns:c="ns"/></a>')
        self._common_test(a, e)
        self.assertEqual(len(e.xml_children[0].xml_children), 1)
        self.assertElementEquals(e.xml_children[0], a)
        self.assertEqual(type(e.xml_children[0]), E)
        self.assertElementEquals(e.xml_children[0].xml_children[0], b)
        self.assertEqual(type(e.xml_children[0].xml_children[0]), E)

    def test_07_mixed_content(self):
        a = E(u'a')
        a.xml_children.append(u'hello')
        b = E(u'b', parent=a)
        a.xml_children.append(u'there')
        e = E.load('<a>hello<b>there</b>to you</a>')
        self._common_test(a, e)
        self.assertEqual(len(e.xml_children[0].xml_children), 3)
        self.assertEqual(e.xml_children[0].xml_children[0], 'hello')
        self.assertEqual(e.xml_children[0].xml_children[1].xml_text, 'there')
        self.assertEqual(e.xml_children[0].xml_children[2], 'to you')

    def test_08_comment(self):
        d = D()
        c = C('commenting on...', parent=d)
        a = E(u'a', parent=d)
        e = E.load('<!--commenting on...--><a/>')
        self.assertEqual(len(e.xml_children), 2)
        
        a = E(u'a')
        c = C('commenting on...', parent=a)
        e = E.load('<a><!--commenting on...--></a>')
        self.assertEqual(len(e.xml_children), 1)
        self.assertEqual(type(e.xml_children[0].xml_children[0]), C)

    def test_09_processing_instruction(self):
        d = D()
        p = PI(target='sl', data='generator="some"', parent=d)
        a = E(u'a', parent=d)
        e = E.load('<?sl generator="some"?><a/>')
        self.assertEqual(len(e.xml_children), 2)
        
        a = E(u'a')
        p = PI(target='sl', data='generator="some"', parent=a)
        e = E.load('<a><?sl generator="some"?></a>')
        self.assertEqual(len(e.xml_children), 1)
        self.assertEqual(type(e.xml_children[0].xml_children[0]), PI)

    def test_10_mixed_comment_pi(self):
        d = D()
        c = C('commenting on...', parent=d)
        c = PI(target='sl', data='generator="some"', parent=d)
        a = E(u'a', parent=d)
        e = E.load('<!--commenting on...--><?sl generator="some"?><a/>')
        self.assertEqual(len(e.xml_children), 3)
        
        d = D()
        c = C('commenting on...', parent=d)
        c = PI(target='sl', data='generator="some"', parent=d)
        a = E(u'a', parent=d)
        b = E(u'b', content=u'hello there', parent=a, prefix=u'p', namespace=u'some')
        e = E.load('<!--commenting on...--><?sl generator="some"?><a><p:b xmlns:p="some">hello there</p:b></a>')
        self.assertEqual(len(e.xml_children), 3)
        self.assertElementEquals(e.xml_children[2].xml_children[0], b)
        self.assertEqual(e.xml_children[2].xml_children[0].xml_text, 'hello there')

    def test_11_attributes(self):
        attrs = {u't': u'i', u'o': u'h'}
        a = E(u'a', attributes=attrs)
        e = E.load('<a t="i" o="h"/>')
        self.assertEqual(len(e.xml_children), 1)
        self.assertEqual(len(e.xml_children[0].xml_attributes), 2)
        self.assertAttributesEqual(a, e.xml_children[0])

    def test_12_attributes_namespaces(self):
        attrs = {u't': u'i', u'o': u'h'}
        a = E(u'a', attributes=attrs)
        A(u'v', value=u'g', prefix=u'd', namespace=u'k', parent=a)
        e = E.load('<a t="i" o="h" d:v="g" xmlns:d="k"/>')
        self.assertEqual(len(e.xml_children), 1)
        self.assertEqual(len(e.xml_children[0].xml_attributes), 3)
        self.assertAttributesEqual(a, e.xml_children[0])

        attrs = {u't': u'i', u'o': u'h'}
        a = E(u'a', attributes=attrs, namespace=u'ze')
        A(u'v', value=u'g', prefix=u'd', namespace=u'k', parent=a)
        A(u'w', value=u'hj', prefix=XMLNS_PREFIX, namespace=XMLNS_NS, parent=a)
        e = E.load('<a t="i" o="h" d:v="g" xmlns:d="k" xmlns:w="hj" xmlns="ze" />')
        self.assertEqual(len(e.xml_children), 1)

        # bridge will strip unused XMLNS declaration on loading
        # from the attributes list meaning only 3 attributes will be kept
        # xmlns:w="hj" will be dropped
        self.assertEqual(len(e.xml_children[0].xml_attributes), 3)
        self.assertEqual(e.xml_children[0].xml_ns, 'ze')

    def test_13_modification(self):
        e = E.load('<a />')
        root = e.xml_root
        self.assertElementEquals(e.xml_children[0], root)
        self.assertEqual(len(e.xml_children), 1)
        self.assertEqual(len(e.xml_children[0].xml_children), 0)
        self.assertEqual(len(root.xml_attributes), 0)
        
        b = E(u'b', parent=root)
        self.assertEqual(len(e.xml_children[0].xml_children), 1)

        A(u's', value=u'bleh', parent=root)
        self.assertEqual(len(root.xml_attributes), 1)

    def test_14_encoded(self):
        text = 'Comment \xc3\xa7a va ?'.decode('UTF-8')
        a = E(u'a', text)
        e = E.load('<a>Comment \xc3\xa7a va ?</a>')
        self.assertEqual(len(e.xml_children), 1)
        self.assertEqual(e.xml_children[0].xml_text, text)

        #print a.xml(encoding='ISO 8859-1')
        #print e.xml(encoding='ISO 8859-1')
