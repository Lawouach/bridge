#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import re
try:
    from cStringIO import StringIO as StringIO
except ImportError:
    from StringIO import StringIO

from lxml import etree
from lxml import objectify
import lxml.sax
from lxml.objectify import fromstring, StringElement, ObjectifiedElement

_parser = etree.XMLParser()
_lookup = objectify.ObjectifyElementClassLookup()
_parser.setElementClassLookup(_lookup)
_lookup = etree.ElementNamespaceClassLookup(objectify.ObjectifyElementClassLookup())
_parser.setElementClassLookup(_lookup)

from bridge import Attribute, Element
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
            return unicode(_)
    return None

def _ns(elt):
    if elt.prefix:
        return unicode(elt.nsmap[elt.prefix])
    return None

class Parser(object):
    def __deserialize_fragment(self, current, parent):
        for child in current.iterchildren():
            content = value = tail = None
            if type(child) != ObjectifiedElement:
                content = child.text
                if content:
                    content = unicode(content)

            element = Element(name=_ln(child), content=content,
                              prefix=child.prefix, namespace=_ns(child),
                              parent=parent)
            
            for attr_key in child.attrib:
                ns, local_name = _split_qcname(attr_key)
                prefix = _get_prefix(child, ns)
                value = unicode(child.attrib[attr_key])
                Attribute(name=local_name, value=value,
                          prefix=prefix, namespace=ns, parent=element)
                
            if type(child) == ObjectifiedElement:
                children = child.getchildren()
                content = child.text
                if content:
                    element.xml_children.append(unicode(content))
                self.__deserialize_fragment(child, element)
                if children:
                    tail = children[-1].tail
                    if tail:
                        element.xml_children.append(unicode(tail))

    def __qname(self, name, prefix=None):
        if prefix:
            return "%s:%s" % (prefix, name)
        return name

    def __attrs(self, node):
        attrs = {}
        for attr in node.xml_attributes:
            attrns = attr.xmlns
            if attrns:
                attrns = attrns.encode(attr.encoding)
            name = attr.name.encode(attr.encoding)
            attrs[(attrns, name)] = self.__qname(name, attr.prefix)

        return attrs

    def __serialize_element(self, handler, element):
        children = element.xml_children
        for child in children:
            if isinstance(child, basestring):
                handler.characters(child)
            elif isinstance(child, Element):
                prefix = ns = name = None
                if child.prefix:
                    prefix = child.prefix.encode(child.encoding)
                if child.xmlns:
                    ns = child.xmlns.encode(child.encoding)
                
                name = child.name.encode(child.encoding)
                qname = self.__qname(name, prefix=prefix)

                attrs = self.__attrs(child)
                if ns:
                    handler.startPrefixMapping(prefix, ns)
                handler.startElementNS((ns, name), qname, attrs)
            
                if child.xml_text:
                    handler.characters(str(child))
                    
                self.__serialize_element(handler, child)
                
                handler.endElementNS((ns, name), qname)
                if ns:
                    handler.endPrefixMapping(prefix)

    def __start_root_element(self, handler, root):
        attrs = self.__attrs(root)
        if root.xmlns:
            handler.startPrefixMapping(root.prefix, root.xmlns)
        handler.startElementNS((root.xmlns, root.name), self.__qname(root.name, root.prefix), attrs)
        if root.xml_text:
            handler.characters(str(root.xml_text))
            
    def __end_root_element(self, handler, root):
        handler.endElementNS((root.xmlns, root.name), self.__qname(root.name, root.prefix))
        if root.xmlns:
            handler.endPrefixMapping(root.prefix)

    def serialize(self, document, indent=True, encoding=ENCODING, prefixes=None, omit_declaration=False):
        prefixes = prefixes or {}
        handler = lxml.sax.ElementTreeContentHandler()
        if not omit_declaration:
            handler.startDocument()
        self.__start_root_element(handler, document)
        self.__serialize_element(handler, document)
        self.__end_root_element(handler, document)
        if not omit_declaration:
            handler.endDocument()

        return etree.tostring(handler.etree.getroot(), pretty_print=indent, encoding=encoding)

    def deserialize(self, source, prefixes=None, strict=False):
        autoclose = False
        if isinstance(source, basestring):
            autoclose = True
            if os.path.exists(source):
                source = file(source, 'rb')
            else:
                source = StringIO(source)

        doc = etree.parse(source, _parser)
        
        if autoclose:
            source.close()

        root = doc.getroot()
        content = None
        children = root.getchildren()
        if root.text and not children:
            content = unicode(root.text)
                
        element = Element(name=_ln(root), prefix=root.prefix,
                          namespace=_ns(root), content=content)
        
        if root.text and children:
            element.xml_children.append(unicode(root.text))
            
        self.__deserialize_fragment(root, element)
        
        if children:
            tail = children[-1].tail
            if tail:
                element.xml_children.append(unicode(tail))
            
        return element

