#!/usr/bin/env python
# -*- coding: utf-8 -*-

import amara
from bridge import *
from bridge import ENCODING, DUMMY_URI, __version__

__all__ = ['Parser']

class Parser(object):
    def __deserialize_fragment(self, current, parent):
        for attr_key in current.attributes:
            attr = current.attributes[attr_key]
            Attribute(attr.localName, unicode(attr),
                      attr.prefix, attr.namespaceURI, parent)
            
        for child in current.xml_children:
            if isinstance(child, basestring):
                if len(current.xml_children) == 1:
                    parent.xml_text = unicode(child)
                else:
                    parent.xml_children.append(child)
            elif isinstance(child, amara.bindery.pi_base):
                PI(target=child.target, data=child.data, parent=parent)
            elif isinstance(child, amara.bindery.comment_base):
                Comment(data=child.data, parent=parent)
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
            node.xml_set_attribute((u'%s:%s' % (attr.xml_prefix, attr.xml_name), attr.xml_ns),
                                   attr.xml_text)
        else:
            node.xml_set_attribute(attr.xml_name, attr.xml_text)

    def __serialize_element(self, node, element, encoding):
        for attr in element.xml_attributes:
            self.__serialize_attribute(node, attr)

        doc = node.ownerDocument
            
        for child in element.xml_children:
            if isinstance(child, basestring):
                node.xml_append(child)
            elif isinstance(child, PI):
                child_node = amara.bindery.pi_base(child.target, child.data)
                node.xml_append(child_node)
            elif isinstance(child, Comment):
                child_node = amara.bindery.comment_base(child.data)
                node.xml_append(child_node)
            else:
                child_node = doc.xml_create_element(self.__qname(child.xml_name, prefix=child.xml_prefix),
                                                    ns=child.xml_ns, content=child.xml_text)
                node.xml_append(child_node)

                self.__serialize_element(child_node, child, encoding)
        
    def serialize(self, document, indent=True, encoding=ENCODING, prefixes=None, omit_declaration=False):
        prefixes = prefixes or {}
        if not encoding:
            encoding = ENCODING
        doc = amara.create_document()
        if not isinstance(document, Document):
            root = document
            document = Document()
            document.xml_children.append(root)
        self.__serialize_element(doc, document, encoding)

        return doc.xml(indent=indent, encoding=encoding, omitXmlDeclaration=omit_declaration)

    def deserialize(self, source, prefixes=None, strict=False, as_attribute=None, as_list=None,
                    as_attribute_of_element=None):
        prefixes = prefixes or {}
        doc = amara.parse(source, uri=DUMMY_URI, prefixes=prefixes)

        document = Document()
        document.as_attribute = as_attribute or {}
        document.as_list = as_list or {}
        document.as_attribute_of_element = as_attribute_of_element or {}
        self.__deserialize_fragment(doc, document)

        return document
