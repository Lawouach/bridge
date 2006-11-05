#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import re

import xml.dom as xd
import xml.dom.minidom as xdm

import bridge

xml_declaration_rx = re.compile(r"^<\?xml.+?\?>")

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

    def __attrs(self, node, element):
        for attr in element.xml_attributes:
            name = attr.name
            if attr.xmlns:
                node.setAttributeNS(attr.xmlns,
                                    self.__qname(name, attr.prefix),
                                    attr.xml_text)
            else:
                node.setAttribute(name, attr.xml_text)

    def __start_element(self, doc, element):
        if element.xmlns:
            return doc.createElementNS(element.xmlns, self.__qname(element.name, element.prefix))
        else:
            return doc.createElement(element.name)

    def __serialize_element(self, root, node, element):
        self.__attrs(node, element)
        children = element.xml_children
        for child in children:
            if isinstance(child, basestring):
                node.appendChild(root.createTextNode(child))
            elif isinstance(child, bridge.Element):
                child_node = self.__start_element(root, child)
                
                if child.xml_text:
                    child_node.appendChild(root.createTextNode(child.xml_text))
                    
                self.__serialize_element(root, child_node, child)

                node.appendChild(child_node)
                
    def __start_document(self, root):
        if root.xmlns:
            return '<%s:%s xmlns:%s="%s" />' % (root.prefix, root.name,
                                                root.prefix, root.xmlns)
        return '<%s />' % (root.name, )
    
    def serialize(self, document, indent=False, encoding=bridge.ENCODING, prefixes=None, omit_declaration=False):
        doc = self.__start_document(document)
        doc = xdm.parseString(doc)
        if document.xml_text:
            doc.documentElement.appendChild(doc.createTextNode(document.xml_text))
            
        self.__serialize_element(doc, doc.documentElement, document)

        if indent:
            result = doc.toprettyxml(encoding=encoding)

        result = doc.toxml(encoding=encoding)

        if doc:
            doc.unlink()

        if omit_declaration:
            s = xml_declaration_rx.search(result)
            if s:
                result = result[s.end():]
            
        return result

    def deserialize(self, source, prefixes=None, strict=False):
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

        self.__deserialize_fragment(root, element)
        
        if doc:
            doc.unlink()

        return element
