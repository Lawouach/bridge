#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import re

__all__ = ['Parser']

from StringIO import StringIO

# Sadly we can't count on Python 2.5 because it doesn't have the complete
# ElementTree package (it misses SimpleXMLWriter) *sigh*
import elementtree.ElementTree as ET
from elementtree.ElementTree import XMLTreeBuilder
from elementtree.SimpleXMLWriter import XMLWriter, escape_cdata
from elementtree.ElementTree import _ElementInterface

import xml.dom as xd

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
    return None, qcname

def _get_prefix(namespaces, searched_uri):
    for (prefix, uri) in namespaces:
        if searched_uri == uri:
            return prefix
    return None

class TreeBuilder:
    def __init__(self, element_factory=None, document=None):
        self._data = [] # data collector
        if element_factory is None:
            element_factory = _ElementInterface
        self._factory = element_factory

        # bridge stuff
        self._current = self.document = document
        self.nsmap = []

    def close(self):
        return self.document

    def __split_qname(self, tag):
        uri, local_name = _split_qcname(tag)
        for (prefix, _uri) in self.nsmap:
            if prefix and (uri == _uri):
                return local_name, prefix, uri
            elif (uri == _uri):
                return local_name, None, uri

        return unicode(local_name), None, None

    def __attrs(self, element, attrs):
        for qname in attrs:
            local_name, prefix, uri = self.__split_qname(qname)
            Attribute(local_name, value=unicode(attrs[qname]),
                      prefix=prefix, namespace=uri, parent=element)

        for (prefix, _uri) in self.nsmap:
            Attribute(unicode(prefix), value=unicode(_uri),
                      prefix=XMLNS_PREFIX, namespace=XMLNS_NS, parent=element)

    def data(self, data):
        assert self._current != None, "element not set yet"
        if self._current.xml_children:
            self._current.xml_children.append(data)
        else:
            self._current.xml_text = data

    def start(self, tag, attrs):
        elem = self._factory(tag, attrs)

        # bridge stuff here
        local_name, prefix, uri = self.__split_qname(elem.tag)
        self._current = Element(local_name, prefix=prefix,
                                namespace=uri, parent=self._current)
        self.__attrs(self._current, elem.attrib)
        
    def end(self, tag):
        if self._current.xml_children:
            if self._current.xml_text:
                self._current.xml_children.insert(0, self._current.xml_text)
                self._current.xml_text = None
        self._current = self._current.xml_parent

    def comment(self, data):
        Comment(data, parent=self._current)

    def pi(self, target, data):
        PI(target=target, data=data, parent=self._current)

# see http://effbot.org/zone/elementsoap-3.htm
# although we have to tweak it a little for our purpose
class BridgeTreeBuilder(XMLTreeBuilder):
    def __init__(self, document):
        self.tree_builder = TreeBuilder(document=document)
        XMLTreeBuilder.__init__(self, target=self.tree_builder)
        self._parser.StartNamespaceDeclHandler = self._start_ns
        self._parser.EndNamespaceDeclHandler = self._end_ns
        self._parser.CommentHandler = self._comment
        self._parser.ProcessingInstructionHandler = self._processing_instruction
        self.namespaces = []

    def _start_ns(self, prefix, value):
        self.tree_builder.nsmap.insert(0, (prefix, value))

    def _end_ns(self, prefix):
        assert self.tree_builder.nsmap.pop(0)[0] == prefix, "implementation confused"
        
    def _comment(self, data):
         self.tree_builder.comment(data)

    def _processing_instruction(self, target, data):
         self.tree_builder.pi(target, data)
        
class BridgeXMLWriter(XMLWriter):
    def __init__(self, file, encoding="UTF-8"):
        XMLWriter.__init__(self, file, encoding)
        self._encoding = encoding
        
    # By default ET adds spaces when it should not
    def comment(self, data):
        # ugly hack to access private attributes (not proud of it...)
        flush = getattr(self, '_XMLWriter__flush')
        flush()
        write = getattr(self, '_XMLWriter__write')
        write("<!--%s-->" % escape_cdata(data, self._encoding))

    # The default writer does not support processing instruction
    def pi(self, target, data):
        flush = getattr(self, '_XMLWriter__flush')
        flush()
        write = getattr(self, '_XMLWriter__write')
        write("<?%s %s?>" % (target, escape_cdata(data, self._encoding)))
        
    def declaration(self):
        write = getattr(self, '_XMLWriter__write')
        write('<?xml version="1.0" encoding="%s"?>' % self._encoding)

class Parser(object):
    def __qname(self, element):
        if element.xml_prefix:
            return "%s:%s" % (element.xml_prefix, element.xml_name)
        return element.xml_name

    def __qname_attr(self, attr):
        if attr.xml_ns == xd.XMLNS_NAMESPACE:
            if not attr.xml_name:
                return "xmlns"
            
        if attr.xml_prefix:
            return "%s:%s" % (attr.xml_prefix, attr.xml_name)
        
        return attr.xml_name

    def __attrs(self, node):
        attrs = {}
        for attr in node.xml_attributes:
            qname = self.__qname_attr(attr)
            attrs[qname] = attr.xml_text or ''
            if attr.xml_ns != xd.XMLNS_NAMESPACE:
                if attr.xml_prefix and attr.xml_ns:
                    attrs['xmlns:%s' % attr.xml_prefix] = attr.xml_ns or ''
                elif attr.xml_ns:
                    attrs['xmlns'] = attr.xml_ns or ''
                
        return attrs

    def __update_visited_ns(self, node, qname, attrs, visited_ns, _visited_ns):
        if node.xml_ns not in visited_ns:
            _visited_ns.append(node.xml_ns)
            if node.xml_prefix:
                attrs['xmlns:%s' % node.xml_prefix] = node.xml_ns or ''
            else:
                attrs['xmlns'] = node.xml_ns or ''
            
    def __serialize_element(self, current, writer, visited_ns, encoding):
        for child in current.xml_children:
            _visited_ns = []
            if isinstance(child, Comment):
                writer.comment(child.data)
            elif isinstance(child, PI):
                writer.pi(child.target, child.data)
            elif isinstance(child, basestring):
                writer.data(child)
            elif isinstance(child, Element):              
                qname = self.__qname(child)
                attrs = self.__attrs(child)
                self.__update_visited_ns(child, qname, attrs, visited_ns, _visited_ns)
                writer.start(qname, attrib=attrs)
                
                if child.xml_text:
                    writer.data(child.xml_text.encode(encoding))
                self.__serialize_element(child, writer, _visited_ns, encoding)
                writer.end(qname)
           
    def serialize(self, document, indent=True, encoding=ENCODING, prefixes=None, omit_declaration=False):
        if not encoding:
            encoding = ENCODING
        prefixes = prefixes or {}

        if not isinstance(document, Document):
            root = document
            document = Document()
            document.xml_children.append(root)
        
        result = StringIO()
        w = BridgeXMLWriter(result, encoding)
        if not omit_declaration:
            w.declaration()
        if indent:
            w.data('\n')
        _visited_ns = []
        self.__serialize_element(document, w, _visited_ns, encoding)

        return result.getvalue()

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

        # cleanup XML ns declaration within the tree
        document.filtrate(rund)
        document.filtrate(rdnd)
        return document
