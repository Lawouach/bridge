#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "0.4.0"
__authors__ = ["Sylvain Hellegouarch (sh@defuze.org)"]
__contributors__ = ['David Turner']
__date__ = "2009/07/10"
__copyright__ = """
Copyright (c) 2006, 2007, 2008, 2009 Sylvain Hellegouarch
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
__docformat__ = "restructuredtext en"

ENCODING = 'UTF-8'
DUMMY_URI = u'http://dummy.com'

from bridge.filter import fetch_child, fetch_children
from bridge.common import  XML_NS, XMLNS_NS 

__all__ = ['Attribute', 'Element', 'PI', 'Comment', 'Document']

class PI(object):
    """
    Represents a XML processing instruction.
    
    :Parameters:
      - `target`: The PI target value
      - `data`: The PI value itself
      - `parent`: Parent to which attach this PI

    """
    def __init__(self, target, data, parent=None):
        self.target = target
        self.data = data
        self.xml_parent = parent
    
        if self.xml_parent:
            self.xml_parent.xml_children.append(self)

class Comment(object):
    """
    Represents a XML comment
    
    :Parameters:
      - `data`: The comment value
      - `parent`: Parent to which attach this comment

    """
    def __init__(self, data, parent=None):
        self.data = data
        self.xml_parent = parent

        if self.xml_parent:
            self.xml_parent.xml_children.append(self)
          
class Attribute(object):
    """
    Maps the attribute of an XML element to a simple Python object.

    Note that names containing dot will see those replaced by underscores.

    :Parameters:
      - `name`: attribute's name`(unicode)
      - `value`: content of the attribute (unicode)
      - `prefix`: XML prefix of the element (unicode)
      - `namespace`: XML namespace defining the prefix (unicode)
      - `parent`: element which this attribute belongs to.
    """

    encoding = ENCODING
    def __init__(self, name=None, value=None, prefix=None, namespace=None, parent=None):
        self.xml_parent = parent
        self.xml_ns = namespace
        self.xml_name = name
        self.xml_text = value
        self.xml_prefix = prefix

        if self.xml_parent:
            self.xml_parent.xml_attributes[(self.xml_ns, self.xml_name)] = self

    def __unicode__(self):
        if self.xml_text:
            return self.xml_text
        return unicode(self.xml_text)
    
    def __str__(self):
        if self.xml_text:
            return self.xml_text.encode(self.encoding)
        return str(self.xml_text)
    
    def __repr__(self):
        value = self.xml_text or ''
        return '{%s}%s="%s" attribute at %s' % (self.xml_ns or '', self.xml_name, value, hex(id(self)))
  
class Element(object):
    """
    Maps an XML element to a Python object.
    
    If `parent` is not None, `self` will be added to the `parent.xml_children` list.
    
    If `Element.as_list` is set and if (name, namespace) belongs to it
    then we will add a list to parent with the name of the element
    
    If `Element.as_attribute` is set and if (name, namespace) belongs to it
    then we will add an attribute to parent with the name of the element
    
    :Parameters:
      - `name` -- Name of the XML element (unicode)
      - `content`: Content of the element (unicode)
      - `attributes`: dictionary of the form {local_name: value}
      - `prefix`:  XML prefix of the element (unicode)
      - `namespace`: XML namespace attached to that element (unicode)
      - `parent`: Parent element of this element.
    """
    encoding = ENCODING
    
    def __init__(self, name=None, content=None, attributes=None, prefix=None, namespace=None, parent=None):
        self._root = None
        self.xml_parent = parent
        self.xml_prefix = prefix
        self.xml_ns = namespace
        self.xml_name = name
        self.xml_text = content
        self.xml_children = []
        self.xml_attributes = {}
        self.as_cdata = False

        if self.xml_parent:
            self.xml_parent.xml_children.append(self)

        if attributes and isinstance(attributes, dict):
            for name in iter(attributes):
                Attribute(name, attributes[name], parent=self)

    def __repr__(self):
        prefix = self.xml_prefix
        xmlns = self.xml_ns
        if (prefix not in ('', None)) and xmlns:
            return '<%s:%s xmlns:%s="%s" element at %s />' % (prefix, self.xml_name,
                                                              prefix, xmlns, hex(id(self)),)
        else:
            return "<%s element at %s />" % (self.xml_name, hex(id(self)))

    def __unicode__(self):
        if self.xml_text:
            return self.xml_text
        return unicode(None)
    
    def __str__(self):
        if self.xml_text:
            return self.xml_text.encode(self.encoding)
        return str(None)

    def __iter__(self):
        return iter(self.xml_children)

    def __copy__(self):
        return Element.load(self.xml(encoding=self.encoding, omit_declaration=True))

    def clone(self):
        """
        Creates a new instance of the current element. The entire subtree is cloned as well.
        """
        return Element.load(self.xml(encoding=self.encoding, omit_declaration=True))
        
    def get_root(self):
        if self._root is not None:
            return self._root

        if isinstance(self.xml_parent, Document):
            self._root = self
            return self
        
        if self.xml_parent is None:
            self._root = self
            return self
        return self.xml_parent.get_root()
    xml_root = property(get_root, doc="Retrieve the top level element")

    def get_attribute_value(self, qname, default=None):
        if qname in self.xml_attributes:
            return unicode(self.xml_attributes[qname])
        elif (None, qname) in self.xml_attributes:
            return unicode(self.xml_attributes[(None, qname)])
        return default

    def set_attribute_value(self, qname, value):
        """
        Sets the attribute value. If the attribute does not
        exist it is created and set with `name`and `value`.

        Returns the set attribute instance.
        """
        if isinstance(qname, str):
            qname = (None, qname)
        name = qname[1]
        for attr_ns, attr_name in self.xml_attributes:
            if attr_name == name:
                attr = self.xml_attributes[qname]                    
                attr.xml_text = value
                return attr

        return Attribute(name, value, namespace=qname[0], parent=self)
            
    def has_child(self, name, ns=None):
        """
        Checks if this element has a child named 'name' in its children elements

        :Parameters:
          - `name`: local name of the element
          - `ns`: namespace of the element
        """
        for child in self.xml_children:
            if child.xml_name == name and child.xml_ns == ns:
                return True

        return False
    
    def get_child(self, name, ns=None):
        """
        Returns the child element named 'name', None if not found.

        :Parameters:
          -`name`: local name of the element
          - `ns`: namespace of the element
        """
        for child in self.xml_children:
            if child.xml_name == name and child.xml_ns == ns:
                return child
    
    def get_children(self, name, ns=None):
        """
        Yields all children of this element named 'name'
        
        :Parameters:
          - `name`: local name of the element
          - `ns`: namespace of the element
        """
        for child in self.xml_children:
            if child.xml_name == name and child.xml_ns == ns:
                yield child

    def get_children_without(self, types=None):
        """
        Returns a list of children not belonging to the types passed in
        ``types`` which must be a list or None. If None is passed
        then returns self.xml_children.

        >>> feed.get_children_without(types=[str, Comment])

        This will return all the children which are not of type string or bridge.Comment.
        """
        if not types:
            return self.xml_children

        children = []
        for child in self.xml_children:
            keep = True
            for t in types:
                if isinstance(child, t):
                    keep = False
                    break

            if keep:
                children.append(child)

        return children
    
    def get_children_with(self, types=None):
        """
        Returns a list of children belonging only to the `types` passed in
        `types` which must be a list or None. If None is passed
        then returns `self.xml_children`.

        >>> feed.get_children_with(types=[Element])

        This will return all the children which are of type bridge.Element
        """
        if not types:
            return self.xml_children

        children = []
        for child in self.xml_children:
            keep = False
            for t in types:
                if isinstance(child, t):
                    keep = True
                    break

            if keep:
                children.append(child)

        return children
    
    def forget(self):
        """
        Deletes this instance of Element. It will also removes it
        from its parent children and attributes.
        """
        self._root = None

        for key in iter(self.xml_attributes):
            self.xml_attributes[key].xml_parent = None
        self.xml_attributes = {}

        for child in self.xml_children:
            if isinstance(child, Element):
                child.forget()

        if self.xml_parent:            
            self.remove_from(self.xml_parent)

        self.xml_text = None
        self.xml_parent = None
        self.xml_children = []

    def remove_from(self, element):
        """
        Removes the instance from the element parameter provided.
        """
        if self in element.xml_children:
            element.xml_children.remove(self)
        
    def insert_before(self, before_element, element):
        """
        Inserts `element` right before `before_element`.
        This only inserts the new element in `self.xml_children`.

        :Parameters:
          - `before_element`: element pivot
          - `element`: new element to insert
        """
        self.xml_children.insert(self.xml_children.index(before_element), element)

    def insert_after(self, after_element, element):
        """
        Insert `element` right after `after_element`.
        This only inserts the new element in `self.xml_children`.

        :Parameters:
          - `after_element`: element pivot
          - `element`: new element to insert
        """
        self.xml_children.insert(self.xml_children.index(after_element) + 1, element)

    def replace(self, current_element, new_element):
        """
        Replaces the current element with a new element in the list
        of children.
        
        :Parameters:
          - `current_element`: element pivot
          - `new_element`: new element to insert
        """
        self.xml_children[self.xml_children.index(current_element)] = new_element

    def collapse(self, separator='\n'):
        """
        Collapses all content of this element and its entire subtree.
        """
        text = [self.xml_text or '']
        for child in self.xml_children:
            if isinstance(child, unicode) or isinstance(child, str):
                text.append(child)
            elif isinstance(child, Element):
                text.append(child.collapse(separator))

        return separator.join(text)

    def is_mixed_content(self):
        """
        Returns `True` if the direct children of this element makes are
        in mixed content.
        """
        for child in self.xml_children:
            if isinstance(child, unicode) or isinstance(child, str):
                return True

        return False

    def xml(self, indent=True, encoding=ENCODING, prefixes=None, omit_declaration=False):
        """
        Serializes this element as a string.

        :Parameters:
          - `indent`: pretty print the XML string (defaut: True)
          - `encoding`: encoding to use during the serialization process
          - `prefixes`: dictionnary of prefixes of the form {'prefix': 'ns'}
          - `omit_declaration`: prevent the result to start with the XML declaration

        :Returns:
          The XML string representing the current element.
        """
        from bridge.parser import get_first_available_parser
        parser = get_first_available_parser()()
        result = parser.serialize(self, indent=indent, encoding=encoding,
                                 prefixes=prefixes, omit_declaration=omit_declaration)
        del parser
        return result

    def load(self, source, prefixes=None):
        """
        Load source into an Element instance

        :Parameters:
          - `source`: an XML string, a file path or a file object
          - `prefixes`: dictionnary of prefixes of the form {'prefix': 'ns'}
        """
        from bridge.parser import get_first_available_parser
        parser = get_first_available_parser()()
        result = parser.deserialize(source, prefixes=prefixes)
        del parser
        return result
    load = classmethod(load)

    def __update_prefixes(self, element, dst, srcns, dstns, update_attributes):
        if update_attributes:
            for attr in element.xml_attributes:
                if attr.xml_ns == srcns:
                    attr.xml_prefix = dst
                    attr.xml_ns = dstns
                elif attr.xml_ns == XMLNS_NS:
                    attr.xml_name = dst

        if element.xml_ns == srcns:
            element.xml_prefix = dst
            if element.xml_ns and not dstns:
                element.xml_ns = None
            elif not element.xml_ns:
                element.xml_ns = dstns
        
        for child in element.xml_children:
            if isinstance(child, Element):
                self.__update_prefixes(child, dst, srcns, dstns, update_attributes)
                
    def update_prefix(self, dst, srcns, dstns, update_attributes=True):
        """
        Updates prefixes of all the element of document matching (src, srcns)

        :Parameters:
          - `dst`: new prefix to be used
          - `srcns`: source namespace
          - `dstns`: destination namespace
          - `update_attributes`: update attributes' namespace as well (default: True)
        """
        self.__update_prefixes(self, dst, srcns, dstns, update_attributes)

    def filtrate(self, some_filter, **kwargs):
        """
        Applies a filter to this element. Returns what is returned from
        some_filter.

        :Parameters:
          - `some_filter`: a callable
          - `kwargs`: any additional data to pass to `some_filter`
        """
        return some_filter(element=self, **kwargs)

    def validate(self, validator, **kwargs):
        """
        Applies a validator on this element
        """
        validator(self, **kwargs)

class Document(Element):
    def __init__(self):
        Element.__init__(self)
        
    def get_root(self):
        if self._root is None:
            for child in self.xml_children:
                if isinstance(child, Element):
                    self._root = child
                    break
        return self._root
    xml_root = property(get_root)

    def __repr__(self):
        return "document at %s" % hex(id(self))
