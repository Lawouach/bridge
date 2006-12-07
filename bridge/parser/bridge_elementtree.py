#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import re

__all__ = ['Parser']

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import elementtree.ElementTree as ET
from elementtree.ElementTree import ElementTree as ETTX
from elementtree.ElementTree import XMLTreeBuilder
from elementtree.ElementTree import Element as ETX
from elementtree.ElementTree import Comment as CX
from elementtree.ElementTree import PI as PIX
from elementtree.ElementTree import SubElement as SETX
import xml.dom as xd

_default_nsmap = {xd.XMLNS_NAMESPACE: u'xmlns', xd.XML_NAMESPACE: u'xml'}

from bridge import Document, Attribute, Comment, PI, Element
from bridge.common import XMLNS_NS, XMLNS_PREFIX
from bridge import ENCODING, DUMMY_URI, __version__
from bridge.filter import remove_duplicate_namespaces_declaration as rdnd
from bridge.filter import remove_useless_namespaces_decalaration as rund

_qcrx = re.compile('{(.*)}(.*)')

def _split_qcname(qcname):
    m = _qcrx.match(qcname)
    if m and len(m.groups()) == 2:
        return unicode(m.group(1)), unicode(m.group(2))
    return None, unicode(qcname)

def _get_prefix(namespaces, searched_uri):
    for (prefix, uri) in namespaces:
        if searched_uri == uri:
            return unicode(prefix)
    return None

class TreeBuilder(XMLTreeBuilder):
    def __init__(self):
        XMLTreeBuilder.__init__(self, 0)
    

# see http://effbot.org/zone/elementsoap-3.htm
# although we have to tweak it a little for our purpose
class BridgeTreeBuilder(TreeBuilder):
    def __init__(self, document):
        TreeBuilder.__init__(self)
        self._parser.StartNamespaceDeclHandler = self._start_ns
        self._parser.EndNamespaceDeclHandler = self._end_ns
        self._parser.CommentHandler = self._comment
        self._parser.ProcessingInstructionHandler = self._processing_instruction
        self.document = document
        self._current = document
        self.namespaces = []
        #print dir(self._parser)

    def __split_qname(self, tag):
        uri, local_name = _split_qcname(tag)
        for (prefix, _uri) in self.namespaces:
            if prefix and (uri == _uri):
                return unicode(local_name), unicode(prefix), unicode(uri)
            elif (uri == _uri):
                return unicode(local_name), None, unicode(uri)

        return unicode(local_name), None, None

    def __attrs(self, element, attrs):
        for qname in attrs:
            local_name, prefix, uri = self.__split_qname(qname)
            Attribute(local_name, value=unicode(attrs[local_name]),
                      prefix=prefix, namespace=uri, parent=element)

        for (prefix, _uri) in self.namespaces:
            Attribute(unicode(prefix), value=unicode(_uri),
                      prefix=XMLNS_PREFIX, namespace=XMLNS_NS, parent=element)

    def _start(self, tag, attrib_in):
        elem = TreeBuilder._start(self, tag, attrib_in)
        elem._stack = []
        elem._visited_ns = []
        elem._parent = self._current
            
        self.start(elem)
        
    def _start_list(self, tag, attrib_in):
        elem = TreeBuilder._start_list(self, tag, attrib_in)
        elem._stack = []
        elem._visited_ns = []
        elem._parent = self._current
        self.start(elem)

    def _end(self, tag):
        elem = TreeBuilder._end(self, tag)
        self.end(elem)

    def _start_ns(self, prefix, value):
        self.namespaces.insert(0, (prefix, value))

    def _end_ns(self, prefix):
        assert self.namespaces.pop(0)[0] == prefix, "implementation confused"

    def start(self, element):
        local_name, prefix, uri = self.__split_qname(element.tag)
    
        self._current = Element(local_name, prefix=prefix,
                                namespace=uri, parent=element._parent)
        self.__attrs(self._current, element.attrib)
        element._stack.append(self._current)

    def end(self, element):
        if not self._current.xml_children and element.text:
            self._current.xml_text = unicode(element.text)
        elif element.text:
            for child in self._current.xml_children:
                if isinstance(child, Element):
                    pos = self._current.xml_children.index(child)
                    self._current.xml_children.insert(pos, unicode(element.text))
                    break
        if element.tail:
            self._current.xml_children.append(unicode(element.tail))
        self._current = element._parent

    def _comment(self, data):
        Comment(unicode(data), parent=self._current)

    def _processing_instruction(self, target, data):
        PI(target=unicode(target), data=unicode(data), parent=self._current)
        

# ElementTree namespace handling is not the friendliest one
# when you use ElementTree to write XML it will use a module attribute (_namespace_map)
# to map namespace URIs to prefix. Because I'd like to avoid such method
# I will slightly change the ElementTree behavior
class BridgeElementTree(ET.ElementTree):
    def write(self, file, encoding="utf-8", namespaces=None):
        assert self._root is not None
        namespaces = namespaces or {}
        self._write(file, self._root, encoding, namespaces)

# modified version of the original tostring
def _tostring(element, encoding=None, namespaces=None):
    class dummy:
        pass
    data = []
    # clever hack ET does.
    file = dummy()
    file.write = data.append
    BridgeElementTree(element).write(file, encoding, namespaces)
    return ''.join(data)

class Parser(object):
    def __qname(self, element):
        if element.xml_ns and element.xml_prefix:
            self.__update_prefixes(element.xml_prefix, element.xml_ns)
            return "{%s}%s" % (element.xml_ns, element.xml_name)
        if element.xml_ns:
            self.__update_prefixes(None, element.xml_ns)
            return "{%s}" % element.xml_ns
        return element.xml_name

    def __qname_attr(self, attr):
        qname = None
        if attr.xml_ns == xd.XMLNS_NAMESPACE:
            if not attr.xml_name:
                return "xmlns"

        if not qname and attr.xml_ns and attr.xml_prefix:
            return "{%s}%s" % (attr.xml_ns, attr.xml_name)

        return attr.xml_name

    def __attrs(self, node):
        attrs = {}
        for attr in node.xml_attributes:
            qname = self.__qname_attr(attr)
            attrs[qname] = attr.xml_text or ''
            if attr.xml_ns == xd.XMLNS_NAMESPACE:
                self.__update_prefixes(attr.xml_name, attr.xml_text)

        return attrs

    def __update_prefixes(self, prefix, uri):
        # this is quite a hack...
        if uri:
            self.nsmap[uri] = prefix

    def __update_visited_ns(self, node, qname, attrs, visited_ns, _visited_ns):
        if node.xml_ns not in visited_ns:
            if node.xml_prefix and node.xml_ns:
                attrs[qname] = node.xml_ns
                _visited_ns.append(node.xml_ns)
            elif node.xml_ns:
                attrs[qname] = node.xml_ns
                _visited_ns.append(node.xml_ns)
            
    def __serialize_element(self, current, parent, visited_ns):
        previous_sibling = None
        for child in current.xml_children:
            _visited_ns = []
            if isinstance(child, Comment):
                element = CX(child.data)
                parent.append(element)
                previous_sibling = element
            elif isinstance(child, PI):
                element = PIX(child.target, child.data)
                parent.append(element)
                previous_sibling = element
            elif isinstance(child, basestring):
                if previous_sibling is not None:
                    previous_sibling.tail = child
                else:
                    parent.text = child
                previous_sibling = None
            elif isinstance(child, Element):                
                qname = self.__qname(child)
                attrs = self.__attrs(child)
                self.__update_visited_ns(child, qname, attrs, visited_ns, _visited_ns)
                element = SETX(parent, qname, attrib=attrs)
                if child.xml_text:
                    element.text = child.xml_text
                previous_sibling = element
                
                self.__serialize_element(child, element, _visited_ns)
           
    def serialize(self, document, indent=True, encoding=ENCODING, prefixes=None, omit_declaration=False):
        if not encoding:
            encoding = ENCODING
        self.nsmap = {xd.XMLNS_NAMESPACE: u'xmlns', xd.XML_NAMESPACE: u'xml'}
        prefixes = prefixes or {}
        self.nsmap.update(prefixes)
        root = document
        if isinstance(document, Document):
            for child in document.xml_children:
                if isinstance(child, Element):
                    root = child
                    break
        
        if root.xml_ns:
            self.nsmap[root.xml_ns] = root.xml_prefix
        qname = self.__qname(root)
        self.__update_prefixes(root.xml_prefix, root.xml_ns)
        attrs = self.__attrs(root)
        _visited_ns = []
        self.__update_visited_ns(root, qname, attrs, [], _visited_ns)

        element = ETX(qname, attrib=attrs)
        if root.xml_text:
            element.text = root.xml_text

        doc = ETTX(element)
        self.__serialize_element(root, element, _visited_ns)

        result = _tostring(element, encoding=encoding, namespaces=self.nsmap)

        if indent:
            indent = '\n'
        else:
            indent = ''
        _prelude = ''
        if isinstance(document, Document):
            for child in document.xml_children:
                if isinstance(child, PI):
                    _prelude = "%s<?%s %s?>%s" % (_prelude, child.target, child.data, indent)
                elif isinstance(child, Comment):
                    _prelude = "%s<!--%s-->%s" % (_prelude, child.data, indent)

        result = '%s%s' % (_prelude, result)
        if not omit_declaration:
            result = '<?xml version="1.0" encoding="%s"?>%s%s' % (encoding, indent, result)

        return result

    def deserialize(self, source, prefixes=None, strict=False, as_attribute=None, as_list=None,
                    as_attribute_of_element=None):
        autoclose = False
        if isinstance(source, basestring):
            autoclose = True
            if os.path.exists(source):
                source = file(source, 'rb')
            else:
                source = StringIO(source)

        document = Document()
        document.as_attribute = as_attribute
        document.as_list = as_list
        document.as_attribute_of_element = as_attribute_of_element
        doc = ET.parse(source, parser=BridgeTreeBuilder(document))
        
        if autoclose:
            source.close()

        document.filtrate(rund)
        document.filtrate(rdnd)
        return document
