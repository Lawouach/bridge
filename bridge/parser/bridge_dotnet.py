#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################
# Use IronPython via the System.Xml assembly
#############################################

import os.path
import bridge

__all__ = ['Parser']

import clr
clr.AddReference('System.Xml')
import System.Xml as sx
from System import Array, Byte
from System.IO import MemoryStream, StreamReader, SeekOrigin
from System.Text import Encoding

from bridge.common import XMLNS_NS
from bridge.filter import remove_duplicate_namespaces_declaration as rdnd
from bridge.filter import remove_useless_namespaces_decalaration as rund

class Parser(object):
    def __deserialize_fragment(self, current, parent):
        if current.Attributes:
            for attr in current.Attributes:
                bridge.Attribute(unicode(attr.LocalName), unicode(attr.Value),
                                 unicode(attr.Prefix), unicode(attr.NamespaceURI), parent)
                
        children = current.ChildNodes
        for child in children:
            if child.NodeType == sx.XmlNodeType.Text:
                if children.Count == 1:
                    parent.xml_text = unicode(child.Value)
                else:
                    parent.xml_children.append(unicode(child.Value))

            else:
                element = bridge.Element(name=unicode(child.LocalName), prefix=child.Prefix,
                                         namespace=unicode(child.NamespaceURI), parent=parent)

                self.__deserialize_fragment(child, element)
    
    def __qname(self, name, prefix=None):
        if prefix:
            return "%s:%s" % (prefix, name)
        return name

    def __attrs(self, node, element):
        for attr in element.xml_attributes:
            name = attr.xml_name
            if attr.xml_ns:
                node.SetAttribute(name, attr.xml_ns, attr.xml_text)
            else:
                node.SetAttribute(name, attr.xml_text)

    def __start_element(self, doc, element):
        if element.xml_ns:
            return doc.CreateElement(element.xml_prefix, element.xml_name, element.xml_ns)
        else:
            return doc.CreateElement(element.xml_name)

    def __serialize_element(self, root, node, element):
        self.__attrs(node, element)
        children = element.xml_children
        for child in children:
            if isinstance(child, basestring):
                node.AppendChild(root.CreateTextNode(child))
            elif isinstance(child, bridge.Element):
                child_node = self.__start_element(root, child)
                
                if child.xml_text:
                    child_node.AppendChild(root.CreateTextNode(child.xml_text))
                    
                self.__serialize_element(root, child_node, child)

                node.AppendChild(child_node)
                
    def __start_document(self, root):
        if root.xml_ns:
            return '<%s:%s xmlns:%s="%s" />' % (root.xml_prefix, root.xml_name,
                                                root.xml_prefix, root.xml_ns)
        return '<%s />' % (root.xml_name, )
    
    def serialize(self, document, indent=False, encoding=bridge.ENCODING, prefixes=None, omit_declaration=False):
        doc = sx.XmlDocument()
        doc.LoadXml(self.__start_document(document))
        if document.xml_text:
            doc.DocumentElement.AppendChild(doc.CreateTextNode(document.xml_text))
        self.__serialize_element(doc, doc.DocumentElement, document)

        settings = sx.XmlWriterSettings()
        settings.Indent = indent
        settings.Encoding = Encoding.GetEncoding(encoding)
        settings.OmitXmlDeclaration = omit_declaration

        ms = MemoryStream()
        xw = sx.XmlWriter.Create(ms, settings)
        doc.Save(xw)
        sr = StreamReader(ms)
        ms.Seek(0, SeekOrigin.Begin)
        content = sr.ReadToEnd()
        ms.Close()

        return content

    def deserialize(self, source, prefixes=None, strict=False, as_attribute=None, as_list=None,
                    as_attribute_of_element=None):
        doc = sx.XmlDocument()
        if isinstance(source, basestring):
            if os.path.exists(source):
                doc.Load(source)
            else:
                doc.LoadXml(source)
        elif hasattr(source, 'read'):
            doc.LoadXml(source.read())

        root = doc.DocumentElement
        element = bridge.Element(name=root.LocalName, prefix=root.Prefix,
                                 namespace=root.NamespaceURI)

        element.as_attribute = as_attribute
        element.as_list = as_list
        element.as_attribute_of_element = as_attribute_of_element
        self.__deserialize_fragment(root, element)
        
        element.filtrate(rund)
        element.filtrate(rdnd)
        return element
