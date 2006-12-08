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
from xml.sax.saxutils import quoteattr

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

# see http://sourceforge.net/tracker/index.php?func=detail&aid=847665&group_id=5470&atid=105470
# although this hack is far from the one suggested in that ticket
# see also http://www.xml.com/pub/a/2003/03/12/py-xml.html for a gentl sax introduction
class XMLGeneratorFixed(xss.XMLGenerator):
    def startElementNS(self, name, qname, attrs, visited_ns=None, _set_empty_ns=False):
        element = []
        element.append('<%s' % qname)
        visited_ns = visited_ns or []
        for mapping in visited_ns:
            match = ns_mapping_rx.match(mapping)
            uri, prefix = match.groups()
            if uri and prefix:
                element.append(' xmlns:%s="%s"' % (prefix, uri))
            elif uri and not prefix:
                element.append(' xmlns="%s"' % uri)

        if _set_empty_ns:
            element.append(' xmlns=""')
        
        self._undeclared_ns_maps = []

        for ((ns, name, prefix), value) in attrs.items():
            if ns is None:
                pass
            elif ns == xd.XML_NAMESPACE:
                name = "xml:%s" % name
            elif ns == xd.XMLNS_NAMESPACE:
                # should have been handled and we do not need to take care of it here
                continue
            else:
                name = 'xmlns:%s="%s" %s:%s' % (prefix, ns, prefix, name)

            element.append(' %s=%s' % (name, quoteattr(value)))

        element.append('>')
        self._write(''.join(element))

    def endElementNS(self, name, qname):
        self._write('</%s>' % qname)

    def comment(self, content):
        self._write('<!--%s-->' % content)

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

            elif child.nodeType == xd.Node.COMMENT_NODE:
                bridge.Comment(data=unicode(child.data), parent=parent)
            elif child.nodeType == xd.Node.PROCESSING_INSTRUCTION_NODE:
                bridge.PI(target=unicode(child.target), data=unicode(child.data), parent=parent)
            elif child.nodeType == xd.Node.ELEMENT_NODE:
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
                name = attr.xml_name.encode(attr.encoding)
                attrs[(attrns, name, attr.xml_prefix)] = attr.xml_text or ''
            
        return attrs

    def __set_prefix_mapping(self, visited_ns, parent_visited_ns, prefix, ns):
        mapping = None
        if prefix and ns:
            mapping = '{%s}%s' % (ns, prefix)
        elif ns:
            mapping = '{%s}' % (ns, )

        if mapping:
            if mapping not in parent_visited_ns:
                visited_ns.append(mapping)

    def __set_visited_ns_from_attributes(self, visited_ns, parent_visited_ns, node):
        for attr in node.xml_attributes:
            if attr.xml_ns == xd.XMLNS_NAMESPACE:
                if attr.xml_text != node.xml_ns:
                    self.__set_prefix_mapping(visited_ns, parent_visited_ns, attr.xml_name, attr.xml_text)
                
    def __serialize_element(self, handler, element, visited_ns=None, set_empty_ns=False, encoding=ENCODING):
        children = element.xml_children
        for child in children:
            _visited_ns = []
            _set_empty_ns = False
            if isinstance(child, basestring):
                handler.characters(child)
            elif isinstance(child, bridge.Comment):
                handler.comment(child.data)
            elif isinstance(child, bridge.PI):
                handler.processingInstruction(child.target, child.data)
            elif isinstance(child, bridge.Element):
                prefix = ns = name = None
                if child.xml_prefix:
                    prefix = child.xml_prefix
                if child.xml_ns:
                    ns = child.xml_ns
                
                name = child.xml_name
                qname = self.__qname(name, prefix=prefix)

                if not child.xml_prefix and not child.xml_ns and not set_empty_ns:
                    _set_empty_ns = True

                attrs = self.__attrs(child)
                
                self.__set_prefix_mapping(_visited_ns, visited_ns, prefix, ns)
                self.__set_visited_ns_from_attributes(_visited_ns, visited_ns, child)
                handler.startElementNS((ns, name), qname, attrs, _visited_ns, _set_empty_ns)
            
                if child.xml_text:
                    handler.characters(child.xml_text)

                for _ in visited_ns:
                    if _ not in _visited_ns:
                        _visited_ns.append(_)
                self.__serialize_element(handler, child, _visited_ns, _set_empty_ns, encoding)
                
                handler.endElementNS((ns, name), qname)
                

    def serialize(self, document, indent=False, encoding=bridge.ENCODING, prefixes=None, omit_declaration=False):
        parser = xs.make_parser()
        parser.setFeature(xs.handler.feature_namespaces, True)
        s = StringIO.StringIO()
        handler = XMLGeneratorFixed(s, encoding=encoding)
        parser.setContentHandler(handler)

        if not isinstance(document, bridge.Document):
            root = document
            document = bridge.Document()
            document.xml_children.append(root)
            
        if not omit_declaration:
            handler.startDocument()
        visited_ns, set_empty_ns = [], False
        self.__serialize_element(handler, document, visited_ns, set_empty_ns, encoding)
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

        document = bridge.Document()
        document.as_attribute = as_attribute
        document.as_list = as_list
        document.as_attribute_of_element = as_attribute_of_element

        self.__deserialize_fragment(doc, document)
        
        if doc:
            try:
                doc.unlink()
            except KeyError:
                pass
            
        document.filtrate(rund)
        document.filtrate(rdnd)
        return document
