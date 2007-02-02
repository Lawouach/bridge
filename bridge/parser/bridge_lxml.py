#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import re

__all__ = ['Parser']

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from lxml import etree
from lxml import sax

from lxml.etree import ElementTree as ETTX
from lxml.etree import Element as ETX
from lxml.etree import Comment as CX
from lxml.etree import ProcessingInstruction as PIX
from lxml.etree import SubElement as SETX
from lxml.etree import QName as QX
import xml.dom as xd

from bridge import Attribute, Element, PI, Comment, Document
from bridge import ENCODING, DUMMY_URI, __version__

_qcrx = re.compile('{(.*)}(.*)')

def _ln(elt):
    if elt.prefix:
        return unicode(elt.tag[len('{%s}' % elt.nsmap[elt.prefix]):])
    return unicode(elt.tag)

def _split_qcname(qcname):
    m = _qcrx.match(qcname)
    if m and len(m.groups()) == 2:
        return unicode(m.group(1)), unicode(m.group(2))
    return None, unicode(qcname)

def _get_prefix(elt, ns):
    for _ in elt.nsmap:
        if elt.nsmap[_] == ns:
            return _
    return None

def _ns(elt):
    if elt.prefix:
        return unicode(elt.nsmap[elt.prefix])
    return None

class Parser(object):
    def __set_attrs(self, current, parent, encoding):
        for attr_key in current.attrib:
            ns, local_name = _split_qcname(attr_key)
            prefix = _get_prefix(current, ns)
            value = current.attrib[attr_key].decode(encoding)
            Attribute(name=local_name, value=value,
                      prefix=prefix, namespace=ns, parent=parent)
        
    def __deserialize_fragment(self, current, parent, encoding):
        self.__set_attrs(current, parent, encoding)
        children = current.getchildren()
        
        content = current.text
        if children and content:
            parent.xml_children.append(content)
        elif content:
            parent.xml_text = content
                           
        for child in children:
            if isinstance(child, etree._Comment):
                Comment(data=child.text, parent=parent)
                if child.tail:
                    parent.xml_children.append(child.tail)
            elif isinstance(child, etree._ProcessingInstruction):
                PI(target=child.target, data=child.text, parent=parent)
                if child.tail:
                    parent.xml_children.append(child.tail)
            else:
                uri, ln = _split_qcname(child.tag)
                prefix = _get_prefix(child, uri)
                element = Element(name=ln, prefix=prefix,
                                  namespace=uri, parent=parent)

                self.__deserialize_fragment(child, element, encoding)
                tail = child.tail
                if tail:
                    parent.xml_children.append(tail)

    def __qname(self, element):
        if element.xml_ns:
            return "{%s}%s" % (element.xml_ns, element.xml_name)
        return element.xml_name
    
    def __attrs(self, node):
        attrs = {}
        for attr in node.xml_attributes:
            attrns = attr.xml_ns
            if attrns is not None:
                attrns = attrns.encode(attr.encoding)
            name = attr.xml_name
            if name is not None:
                name = attr.xml_name.encode(attr.encoding)
            if attrns:
                attrs["{%s}%s" % (attrns, name)] = attr.xml_text or ''
            else:
                attrs[name] = attr.xml_text or ''
                
        return attrs

    def __serialize_element(self, current, parent, encoding):
        previous_sibling = None
        for child in current.xml_children:
            if isinstance(child, Comment):
                element = CX(child.data)
                parent.append(element)
                previous_sibling = element
            elif isinstance(child, PI):
                element = PIX(child.target, child.data)
                parent.append(element)
                previous_sibling = element
            elif isinstance(child, basestring):
                #if current.as_cdata:
                #    child = '<![CDATA[%s]]>' % child
                if previous_sibling is not None:
                    previous_sibling.tail = child
                else:
                    parent.text = child
                previous_sibling = None
            elif isinstance(child, Element):                
                qname = self.__qname(child)
                attrs = self.__attrs(child)
                nsmap = {}
                if child.xml_ns:
                    nsmap[child.xml_prefix] = child.xml_ns
                for attr in child.xml_attributes:
                    if attr.xml_prefix:
                        nsmap[attr.xml_name] = attr.xml_text
                element = SETX(parent, qname, attrib=attrs, nsmap=nsmap)

                if child.xml_text:
                    element.text = child.xml_text
                previous_sibling = element
                
                self.__serialize_element(child, element, encoding)
                
    def serialize(self, document, indent=True, encoding=ENCODING, prefixes=None, omit_declaration=False):
        prefixes = prefixes or {}
        if not encoding:
            encoding = ENCODING
        prefixes = prefixes or {}
        root = document.xml_root
        
        qname = self.__qname(root)
        attrs = self.__attrs(root)

        nsmap = {}
        if root.xml_ns:
            nsmap[root.xml_prefix] = root.xml_ns
        for attr in root.xml_attributes:
            if attr.xml_prefix is not None:
                nsmap[attr.xml_prefix] = attr.xml_ns
        element = ETX(qname, attrib=attrs, nsmap=nsmap)
            
        if root.xml_text:
            element.text = root.xml_text

        doc = ETTX(element)
        self.__serialize_element(root, element, encoding)
        
        return etree.tostring(doc, xml_declaration=not omit_declaration,
                              pretty_print=indent, encoding=encoding)

    def deserialize(self, source, prefixes=None, strict=False, as_attribute=None, as_list=None,
                    as_attribute_of_element=None):
        autoclose = False
        if isinstance(source, basestring):
            autoclose = True
            if os.path.exists(source):
                source = file(source, 'rb')
            else:
                source = StringIO(source)

        parser = etree.XMLParser(ns_clean=True, no_network=True)
        parser.setElementClassLookup(etree.ElementNamespaceClassLookup())

        doc = etree.parse(source, parser)
        
        if autoclose:
            source.close()

        document = Document()
        document.as_attribute = as_attribute or {}
        document.as_list = as_list or {}
        document.as_attribute_of_element = as_attribute_of_element or {}

        root = doc.getroot()
        uri, ln = _split_qcname(root.tag)

        prefix = _get_prefix(root, uri)
        element = Element(name=ln, prefix=prefix,
                          namespace=uri, parent=document)
        self.__deserialize_fragment(root, element, encoding=ENCODING)
        
        return document

