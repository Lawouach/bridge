#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import re

__all__ = ['Parser']

import xml.dom as xd
import xml.dom.minidom as xdm
import xml.sax as xs
import xml.sax.handler as xsh
import xml.sax.saxutils as xss
from xml.sax.saxutils import quoteattr, escape

import bridge
from bridge import ENCODING
from bridge.filter import remove_duplicate_namespaces_declaration as rdnd
from bridge.filter import remove_useless_namespaces_decalaration as rund

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

xml_declaration_rx = re.compile(r"^<\?xml.+?\?>")
ns_mapping_rx =  re.compile('\{(.*)\}(.*)')

class Parser(object):
    def __deserialize_fragment(self, current, parent):
        if current.attributes:
            for key in current.attributes.keys():
                attr = current.attributes[key]
                bridge.Attribute(attr.localName, attr.value,
                                 attr.prefix, attr.namespaceURI, parent)
                
        children = current.childNodes
        for child in children:
            nt = child.nodeType
            if nt == xd.Node.TEXT_NODE:
                data = escape(child.data)
                if len(children) == 1:
                    parent.xml_text = data
                else:
                    parent.xml_children.append(data)
            elif nt == xd.Node.CDATA_SECTION_NODE:
                parent.as_cdata = True
                data = escape(child.data)
                if len(children) == 1:
                    parent.xml_text = data
                else:
                    parent.xml_children.append(data)
            elif nt == xd.Node.COMMENT_NODE:
                bridge.Comment(data=unicode(child.data), parent=parent)
            elif nt == xd.Node.PROCESSING_INSTRUCTION_NODE:
                bridge.PI(target=unicode(child.target), data=unicode(child.data), parent=parent)
            elif nt == xd.Node.ELEMENT_NODE:
                element = bridge.Element(name=child.localName, prefix=child.prefix,
                                         namespace=child.namespaceURI, parent=parent)

                self.__deserialize_fragment(child, element)

    def __qname(self, name, prefix=None):
        if prefix:
            return "%s:%s" % (prefix, name)
        return name
    
    def __attrs(self, node):
        attrs = {}
        for attr in node.xml_attributes:
            attrns = attr.xml_ns
            if attrns != xd.XMLNS_NAMESPACE:
                if attrns:
                    attrns = attrns.encode(attr.encoding)
                name = attr._local_name.encode(attr.encoding)
                attrs[(attrns, name, attr.xml_prefix)] = attr.xml_text or ''
            
        return attrs

    def __set_prefix_mapping(self, visited_ns, parent_visited_ns, prefix, ns):
        mapping = None
        if prefix and ns:
            mapping = '{%s}%s' % (ns, prefix)
        elif ns:
            mapping = '{%s}' % (ns, )

        if mapping:
            if mapping not in visited_ns:
                if mapping not in parent_visited_ns:
                    visited_ns.append(mapping)

    def __serialize_element(self, element, buf, visited_ns=None, encoding=ENCODING):
        children = element.xml_children
        for child in children:
            _visited_ns = []
            if isinstance(child, basestring):
                if element.as_cdata:
                    buf.append('<![CDATA[')
                buf.append(child)
                if element.as_cdata:
                    buf.append(']]>')
            elif isinstance(child, bridge.Comment):
                buf.append('<!--%s-->' % child.data)
            elif isinstance(child, bridge.PI):
                buf.append('<?%s %s?>' % (child.target, child.data))
            elif isinstance(child, bridge.Element):
                prefix = ns = name = None
                if child.xml_prefix:
                    prefix = child.xml_prefix
                if child.xml_ns:
                    ns = child.xml_ns
                self.__set_prefix_mapping(_visited_ns, visited_ns, prefix, ns)
                
                name = child._local_name
                qname = self.__qname(name, prefix=prefix)
                elmt = ['<%s' % qname]
                attrs = self.__attrs(child)
                
                for ((ns, name, prefix), value) in attrs.items():
                    if ns is None:
                        pass
                    elif ns == xd.XML_NAMESPACE:
                        name = 'xml:%s' % name
                    elif ns == xd.XMLNS_NAMESPACE:
                        _visited_ns[name] = value
                        self.__set_prefix_mapping(_visited_ns, visited_ns, name, value)
                    else:
                        name = '%s:%s' % (prefix, name)
                        self.__set_prefix_mapping(_visited_ns, visited_ns, prefix, ns)
                        
                    elmt.append(' %s=%s' % (name, quoteattr(value)))

                for token in _visited_ns:
                    match = ns_mapping_rx.match(token)
                    uri, prefix = match.groups()
                    if prefix:
                        elmt.append(' xmlns:%s="%s"' % (prefix, uri))
                    else:
                        elmt.append(' xmlns="%s"' % (uri, ))
                        
                if child.xml_text or child.xml_children:
                    elmt.append('>')
                
                    if child.xml_text:
                        elmt.append(child.xml_text)

                    _visited_ns.extend(visited_ns)
                    buf.extend(elmt)
                    self.__serialize_element(child, buf, _visited_ns, encoding)
                    buf.extend('</%s>' % qname)
                else:
                    elmt.append(' />')
                    buf.extend(elmt)
              
    def serialize(self, document, indent=False, encoding=bridge.ENCODING, prefixes=None, omit_declaration=False):

        if not isinstance(document, bridge.Document):
            root = document
            document = bridge.Document()
            document.xml_children.append(root)

        buf = []
        if not omit_declaration:
            buf.append('<?xml version="1.0" encoding="%s"?>' % encoding)
        visited_ns = []
        self.__serialize_element(document, buf, visited_ns, encoding)

        content = ''.join(buf)
        return content.encode(encoding)

    def deserialize(self, source, prefixes=None, strict=False, as_attribute=None, as_list=None,
                    as_attribute_of_element=None):
        doc = None
        if isinstance(source, basestring):
            if os.path.exists(source):
                doc = xdm.parse(source)
            else:
                doc = xdm.parseString(source)
        elif hasattr(source, 'read'):
            doc = xdm.parse(source)

        document = bridge.Document()
        document.as_attribute = as_attribute or {}
        document.as_list = as_list or {}
        document.as_attribute_of_element = as_attribute_of_element or {}

        self.__deserialize_fragment(doc, document)
        
        if doc:
            try:
                doc.unlink()
            except KeyError:
                pass

        document.filtrate(rund)
        document.filtrate(rdnd)
        return document
