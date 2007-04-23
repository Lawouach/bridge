#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import re

__all__ = ['Parser']

import xml.dom as xd
import xml.dom.minidom as xdm
import xml.sax as xs
import xml.sax.handler as xsh
import xml.sax.saxutils as xss
from xml.sax.saxutils import quoteattr, escape, unescape

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
    def __init__(self):
        self.buffer = []
        
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
                data = child.data
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
            prefix = attr.xml_prefix
            if attrns:
                attrns = attrns.encode(attr.encoding)
            name = attr._local_name.encode(attr.encoding)
            if attrns == xd.XMLNS_NAMESPACE and name == 'xmlns':
                continue
            attrs[(attrns, name, prefix)] = attr.xml_text or ''

        return attrs

    def __append_namespace(self, prefix, ns):
        if prefix:
            self.buffer.append(' xmlns:%s="%s"' % (prefix, ns))
        elif ns is not None:
            self.buffer.append(' xmlns="%s"' % (ns, ))
            
    def __build_ns_map(self, ns_map, element):
        for child in element.xml_children:
            if isinstance(child, bridge.Element):
                if child.xml_ns not in ns_map:
                    ns_map[child.xml_prefix] = child.xml_ns
                for attr in child.xml_attributes:
                    if attr.xml_ns not in ns_map:
                        ns_map[attr.xml_ns] = attr._xml_prefix

    def __is_known(self, ns_map, prefix, ns):
        if prefix in ns_map:
            if ns_map[prefix] == ns:
                return True

        ns_map[prefix] = ns
        return False

    def __append_text(self, text, as_cdata):
        if as_cdata:
            self.buffer.append('<![CDATA[')
        self.buffer.append(text)
        if as_cdata:
            self.buffer.append(']]>')
                    
    def __serialize_element(self, element, parent_ns_map=None):
        children = element.xml_children
        for child in children:
            if isinstance(child, basestring):
                child = child.strip()
                child = child.strip('\n')
                child = child.strip('\r\n')
                if not child:
                    continue
                self.__append_text(child, element.as_cdata)
            elif isinstance(child, bridge.Comment):
                self.buffer.append('<!--%s-->' % (child.data,))
            elif isinstance(child, bridge.PI):
                self.buffer.append('<?%s %s?>' % (child.target, child.data))
            elif isinstance(child, bridge.Element):
                ns_map = {}
                ns_map.update(parent_ns_map or {})
                prefix = ns = name = None
                if child.xml_prefix:
                    prefix = child.xml_prefix
                if child.xml_ns:
                    ns = child.xml_ns
        
                name = child._local_name
                qname = self.__qname(name, prefix=prefix)
                self.buffer.append('<%s' % qname)
                if not self.__is_known(ns_map, prefix, ns):
                    self.__append_namespace(prefix, ns)
                    
                attrs = self.__attrs(child)
                
                for ((ns, name, prefix), value) in attrs.items():
                    if ns is None:
                        pass
                    elif ns == xd.XML_NAMESPACE:
                        name = 'xml:%s' % name
                    elif ns == xd.XMLNS_NAMESPACE:
                        if not self.__is_known(ns_map, name, value):
                            self.__append_namespace(name, value)
                        continue
                    else:
                        name = '%s:%s' % (prefix, name)
                        if not self.__is_known(ns_map, prefix, ns):
                            self.__append_namespace(prefix, ns)
                        
                    self.buffer.append(' %s=%s' % (name, quoteattr(value)))

                if child.xml_text or child.xml_children:
                    self.buffer.append('>')
                
                    if child.xml_text:
                        self.__append_text(child.xml_text, child.as_cdata)

                    if child.xml_children:
                        self.__serialize_element(child, ns_map)

                    self.buffer.extend('</%s>' % (qname, ))
                else:
                    self.buffer.append(' />')


    def serialize(self, document, indent=False, encoding=bridge.ENCODING, prefixes=None, omit_declaration=False):

        if not isinstance(document, bridge.Document):
            root = document
            document = bridge.Document()
            document.xml_children.append(root)

        self.__serialize_element(document)

        end_of_line = ''
        if indent:
            end_of_line = os.linesep
        if not omit_declaration:
            self.buffer.insert(0, '<?xml version="1.0" encoding="%s"?>%s' % (encoding, end_of_line))
            
        content = ''.join(self.buffer)
        return content.rstrip(end_of_line).encode(encoding)

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
            
        return document
