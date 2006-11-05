#!/usr/bin/env python
# -*- coding: utf-8 -*-

import amara
from bridge import Attribute, Element
from bridge import ENCODING, DUMMY_URI, __version__

class Parser(object):
    def __deserialize_fragment(self, current, parent):
        for attr_key in current.attributes:
            attr = current.attributes[attr_key]
            Attribute(attr.localName, unicode(attr),
                      attr.prefix, attr.namespaceURI, parent)
            
        for child in current.xml_children: 
            if isinstance(child, basestring):
                if not parent.xml_text:
                    parent.xml_text = unicode(child)
                else:
                    parent.xml_children.append(child)
            else:
                element = Element(name=child.localName,
                                  prefix=child.prefix, namespace=child.namespaceURI,
                                  parent=parent)
                
                self.__deserialize_fragment(child, element)

    def __qname(self, name, prefix=None):
        if prefix:
            return "%s:%s" % (prefix, name)
        return name

    def __serialize_attribute(self, node, attr):
        if attr.xml_prefix and attr.xml_ns:
            if attr.xml_ns not in node.rootNode.xml_namespaces:
                ns = amara.bindery.namespace(attr.xml_ns, attr.xml_prefix)
                node.rootNode.xml_namespaces[attr.xml_ns] = ns
            node.xml_set_attribute((u'%s:%s' % (attr.xml_prefix, attr.xml_name), attr.xml_ns),
                                   attr.xml_text)
        else:
            node.xml_set_attribute(attr.xml_name, attr.xml_text)

    def __serialize_element(self, node, element):
        for attr in element.xml_attributes:
            self.__serialize_attribute(node, attr)

        doc = node.ownerDocument
            
        for child in element.xml_children:
            if isinstance(child, basestring):
                node.xml_append(child)
            else:
                child_node = doc.xml_create_element(self.__qname(child.xml_name, prefix=child.xml_prefix),
                                                    ns=child.xml_ns, content=child.xml_text)
                node.xml_append(child_node)

                self.__serialize_element(child_node, child)
            
    def __serialize_root_element(self, root):
        if root.xml_ns:
            return '<%s:%s xmlns:%s="%s" />' % (root.xml_prefix, root.xml_name,
                                                root.xml_prefix, root.xml_ns)
        return '<%s />' % (root.xml_name, )

    def serialize(self, document, indent=True, encoding=ENCODING, prefixes=None, omit_declaration=False):
        prefixes = prefixes or {}
        t = self.__serialize_root_element(document)
        doc = amara.parse(t.encode(encoding),
                          uri=DUMMY_URI, prefixes=prefixes)
        root = getattr(doc, document.xml_name)
        self.__serialize_element(root, document)

        return doc.xml(indent=indent, encoding=encoding, omitXmlDeclaration=omit_declaration)
    
    def deserialize(self, source, prefixes=None, strict=False):
        prefixes = prefixes or {}
        doc = amara.parse(source, uri=DUMMY_URI, prefixes=prefixes)

        root = doc.xml_children[0]
        element = Element(name=root.localName, prefix=root.prefix,
                          namespace=root.namespaceURI)
        self.__deserialize_fragment(root, element)
        
        return element
