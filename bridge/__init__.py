#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "0.1.0"
__authors__ = ["Sylvain Hellegouarch (sh@defuze.org)"]
__date__ = "2006/11/03"
__copyright__ = """
Copyright (c) 2006 Sylvain Hellegouarch
All rights reserved.
"""
__license__ = """
Redistribution and use in source and binary forms, with or without modification, 
are permitted provided that the following conditions are met:
 
     * Redistributions of source code must retain the above copyright notice, 
       this list of conditions and the following disclaimer.
     * Redistributions in binary form must reproduce the above copyright notice, 
       this list of conditions and the following disclaimer in the documentation 
       and/or other materials provided with the distribution.
     * Neither the name of Sylvain Hellegouarch nor the names of his contributors 
       may be used to endorse or promote products derived from this software 
       without specific prior written permission.
 
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE 
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

ENCODING = 'UTF-8'
DUMMY_URI = u'http://dummy.com'

import bridge.parser.bridge_default

class Attribute(object):
    """
    Maps the attribute of an XML element to a simple Python object.
    """

    encoding = ENCODING
    as_attribute_of_element = None
    
    def __init__(self, name=None, value=None, prefix=None, namespace=None, parent=None):
        """
        Maps the attribute of an XML element to a simple Python object.

        Keyword arguments:
        name -- Name of the attribute
        value -- content of the attribute
        prefix -- XML prefix of the element
        namespace -- XML namespace defining the prefix
        parent -- element which this attribute belongs to
        """
        if value and not isinstance(value, unicode):
            raise TypeError, "Attribute's value must be an unicode object or None"
        
        self.parent = parent
        self.name = name
        self.xml_text = value
        self.prefix = prefix
        self.xmlns = namespace

        if self.parent:
            self.parent.xml_attributes.append(self)

            attr_of_element = self.as_attribute_of_element or {}
            attrs = attr_of_element.get(self.xmlns, [])
            if self.name in attrs:
                setattr(self.parent, self.name, self.xml_text)

    def __unicode__(self):
        return self.xml_text
    
    def __str__(self):
        return self.xml_text.encode(self.encoding)

    def __repr__(self):
        value = self.xml_text or ''
        return '%s="%s" attribute at %s' % (self.name, value, hex(id(self)))

class Element(object):
    """
    Maps an XML element to a Python object.
    """

    parser = bridge.parser.bridge_default.Parser
    encoding = ENCODING
    as_list = None
    as_attribute = None
    
    def __init__(self, name=None, content=None, attributes=None, prefix=None, namespace=None, parent=None):
        """
        Maps an XML element to a Python object.
        
        Keyword arguments:
        name -- Name of the XML element
        content -- Content of the element
        attributes -- dictionary of the form {local_name: value}
        prefix -- XML prefix of the element
        namespace -- XML namespace attached to that element
        parent -- Parent element of this element.
        
        If 'parent' is not None, 'self' will be added to the parent.xml_children

        If 'Element.as_list' is set and if (name, namespace) belongs to it
        then we will add a list to parent with the name of the element
        
        If 'Element.as_attribute' is set and if (name, namespace) belongs to it
        then we will add an attribute to parent with the name of the element 
        """
        if content and not isinstance(content, unicode):
            raise TypeError, "Element's content must be an unicode object or None"
        
        self.parent = parent
        self.prefix = prefix
        self.xmlns = namespace
        self.name = name
        self.xml_text = content
        self.xml_children = []
        self.xml_attributes = []

        if self.parent:
            self.parent.xml_children.append(self)

            as_attr_elts = self.as_attribute or {}
            as_list_elts = self.as_list or {}
            
            as_attr_elts = as_attr_elts.get(self.xmlns, [])
            as_list_elts = as_list_elts.get(self.xmlns, [])

            if self.name in as_attr_elts:
                setattr(self.parent, name, self)
            elif self.name in as_list_elts:
                if not hasattr(self.parent, name):
                    setattr(self.parent, name, [])
                els = getattr(self.parent, name)
                els.append(self)

        if attributes and isinstance(attributes, dict):
            for name in attributes:
                Attribute(name, attributes[name], parent=self)

    def __repr__(self):
        prefix = self.prefix
        xmlns = self.xmlns
        if (prefix not in ('', None)) and xmlns:
            return '<%s:%s xmlns:%s="%s" element at %s />' % (prefix, self.name,
                                                              prefix, xmlns, hex(id(self)),)
        else:
            return "<%s element at %s />" % (self.name, hex(id(self)))

    def __unicode__(self):
        return self.xml_text
    
    def __str__(self):
        return self.xml_text.encode(self.encoding)

    def __iter__(self):
        return iter(self.xml_children)

    def __del__(self):
        """
        deletes this instance of Element. It will also removes it
        from its parent children and attributes.
        """
        if self.parent:
            if self in self.parent.xml_children:
                self.parent.xml_children.remove(self)
            if hasattr(self.parent, self.name):
                obj = getattr(self.parent, self.name)
                if isinstance(obj, list):
                    obj.remove(self)
                elif isinstance(obj, Element):
                    del obj

    def get_root(self):
        if self.parent is None:
            return self
        return self.parent.get_root()
    xml_root = property(get_root, doc="Retrieve the top level element")

    def get_attribute(self, name):
        for attr in self.xml_attributes:
            if attr.name == name:
                return attr
            
    def get_attribute_ns(self, name, namespace):
        for attr in self.xml_attributes:
            if (attr.name == name) and (attr.xmlns == namespace):
                return attr

    def has_element(self, name, ns=None):
        """
        Checks if this element has 'name' attribute

        Keyword arguments:
        name -- local name of the element
        ns -- namespace of the element
        """
        obj = getattr(self, name, None)
        if obj:
            return obj.xmlns == ns
        return False
    
    def xml(self, indent=True, encoding=ENCODING, prefixes=None, omit_declaration=False):
        """
        Serializes as a string this element

        Keyword arguments
        indent -- pretty print the XML string (defaut: True)
        encoding -- encoding to use during the serialization process
        prefixes -- dictionnary of prefixes of the form {'prefix': 'ns'}
        omit_declaration -- prevent the result to start with the XML declaration
        """
        ser = self.parser()
        return ser.serialize(self, indent=indent, encoding=encoding,
                             prefixes=prefixes, omit_declaration=omit_declaration)

    def load(self, source, prefixes=None):
        """
        Load source into an Element instance

        Keyword arguments:
        source -- an XML string, a file path or a file object
        prefixes -- dictionnary of prefixes of the form {'prefix': 'ns'}
        """
        ser = self.parser()
        return ser.deserialize(source, prefixes=prefixes)
    load = classmethod(load)

    def __update_prefixes(self, element, dst, srcns, dstns, update_attributes):
        if update_attributes:
            for attr in element.xml_attributes:
                if attr.xmlns == srcns:
                    attr.prefix = dst
                    attr.xmlns = dstns

        if element.xmlns == srcns:
            element.prefix = dst
            if element.xmlns and not dstns:
                element.xmlns = None
            elif not element.xmlns:
                element.xmlns = dstns
        
        for child in element.xml_children:
            if not isinstance(child, basestring):
                self.__update_prefixes(child, dst, srcns, dstns, update_attributes)
                
    def update_prefix(self, dst, srcns, dstns, update_attributes=True):
        """
        Updates prefixes of all the element of document matching (src, srcns)

        Keyword arguments:
        dst -- new prefix to be used
        srcns -- source namespace
        dstns -- destination namespace
        update_attributes -- update attributes' namespace as well (default: True)
        """
        self.__update_prefixes(self, dst, srcns, dstns, update_attributes)

    def filtrate(self, some_filter, **kwargs):
        """
        Applies a filter to this element. Returns what is returned from
        some_filter.

        Keyword arguments:
        some_filter -- a callable(**kwargs)
        """
        return some_filter(element=self, **kwargs)

    def validate(self, validator, **kwargs):
        """
        Applies a validator on this element
        """
        validator(self, **kwargs)
