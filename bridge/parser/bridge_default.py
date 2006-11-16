#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import re

import xml.dom as xd
import xml.dom.minidom as xdm
import xml.sax as xs
import xml.sax.handler as xsh
import xml.sax.saxutils as xss
from xml.sax.saxutils import quoteattr

import bridge

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

xml_declaration_rx = re.compile(r"^<\?xml.+?\?>")

# see http://sourceforge.net/tracker/index.php?func=detail&aid=847665&group_id=5470&atid=105470
class XMLGeneratorFixed(xss.XMLGenerator):
    def startElementNS(self, name, qname, attrs):
        if name[0] is None or self._current_context[name[0]] is None:
            # if the name was not namespace-scoped, use the unqualified part
            name = name[1]
        else:
            # else try to restore the original prefix from the namespace
            name = "%s:%s" % (self._current_context[name[0]], name[1])
        self._out.write('<' + name)

        for prefix, uri in self._undeclared_ns_maps:
            if prefix:
                self._out.write(' xmlns:%s="%s"' % (prefix, uri))
            else:
                self._out.write(' xmlns="%s"' % uri)
        self._undeclared_ns_maps = []

        for (name, value) in attrs.items():
            if name[0] is None:
                name = name[1]
            elif name[0] == xd.XML_NAMESPACE:
                name = "xml:%s" % name[1]
            elif name[0] == xd.XMLNS_NAMESPACE:
                name = "xmlns:%s" % name[1]
            else:
                name = "%s:%s" % (self._current_context[name[0]], name[1])
            self._out.write(' %s=%s' % (name, quoteattr(value)))
        self._out.write('>')

    def endElementNS(self, name, qname):
        if name[0] is None or self._current_context[name[0]] is None:
            name = name[1]
        else:
            name = self._current_context[name[0]] + ":" + name[1]
        self._out.write('</%s>' % name)

class Parser(object):
    def __deserialize_fragment(self, current, parent):
        if current.attributes:
            for key in current.attributes.keys():
                attr = current.attributes[key]
                bridge.Attribute(attr.localName, attr.value,
                                 attr.prefix, attr.namespaceURI, parent)
                
        children = current.childNodes
        for child in children:
            if child.nodeType == xd.Node.TEXT_NODE:
                if len(children) == 1:
                    parent.xml_text = child.data
                else:
                    parent.xml_children.append(child.data)

            else:
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
            if attrns:
                attrns = attrns.encode(attr.encoding)
            name = attr.xml_name.encode(attr.encoding)
            attrs[(attrns, name)] = attr.xml_text or ''

        return attrs

    def __serialize_element(self, handler, element):
        children = element.xml_children
        for child in children:
            if isinstance(child, basestring):
                handler.characters(child)
            elif isinstance(child, bridge.Element):
                prefix = ns = name = None
                if child.xml_prefix:
                    prefix = child.xml_prefix.encode(child.encoding)
                if child.xml_ns:
                    ns = child.xml_ns.encode(child.encoding)
                
                name = child.xml_name.encode(child.encoding)
                qname = self.__qname(name, prefix=prefix)

                attrs = self.__attrs(child)
                if ns and ns != child.xml_root.xml_ns:
                    handler.startPrefixMapping(prefix, ns)
                handler.startElementNS((ns, name), qname, attrs)
            
                if child.xml_text:
                    handler.characters(str(child))
                    
                self.__serialize_element(handler, child)
                
                handler.endElementNS((ns, name), qname)
                if ns and ns != child.xml_root.xml_ns:
                    handler.endPrefixMapping(prefix)

    def __start_root_element(self, handler, root):
        attrs = self.__attrs(root)
        if root.xml_ns:
            handler.startPrefixMapping(root.xml_prefix, root.xml_ns)
        handler.startElementNS((root.xml_ns, root.xml_name), self.__qname(root.xml_name, root.xml_prefix), attrs)
        if root.xml_text:
            handler.characters(str(root.xml_text))
            
    def __end_root_element(self, handler, root):
        handler.endElementNS((root.xml_ns, root.xml_name), self.__qname(root.xml_name, root.xml_prefix))
        if root.xml_ns:
            handler.endPrefixMapping(root.xml_prefix)

    def serialize(self, document, indent=False, encoding=bridge.ENCODING, prefixes=None, omit_declaration=False):
        parser = xs.make_parser()
        parser.setFeature(xs.handler.feature_namespaces, True)
        s = StringIO.StringIO()
        handler = XMLGeneratorFixed(s)
        parser.setContentHandler(handler)

        if not omit_declaration:
            handler.startDocument()
        self.__start_root_element(handler, document)
        self.__serialize_element(handler, document)
        self.__end_root_element(handler, document)
        if not omit_declaration:
            handler.endDocument()

        content = s.getvalue()
        s.close()
        return content

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

        root = doc.documentElement
        element = bridge.Element(name=root.localName, prefix=root.prefix,
                                 namespace=root.namespaceURI)
        element.as_attribute = as_attribute
        element.as_list = as_list
        element.as_attribute_of_element = as_attribute_of_element

        self.__deserialize_fragment(root, element)
        
        if doc:
            doc.unlink()

        return element
