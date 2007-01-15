#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ['remove_duplicate_namespaces_declaration',
           'remove_useless_namespaces_decalaration',
           'fetch_child', 'fetch_children', 'element_children']

import bridge
from bridge.common import XMLNS_NS

def fetch_child(element, child_name, child_ns):
    """
    Returns the first child named 'child_name' with the namespace 'child_ns'

    Use it like this:
    e = Element.load('<root><id /></root>')
    child = e.filtrate(fetch_child, child_name='id', child_ns=None)

    Keyword arguments:
    element -- parent element to go through
    child_name -- name of the element to lookup
    child_ns -- namespace of the element to lookup
    """
    element_type = type(element)
    for child in element.xml_children:
        if isinstance(child, element_type):
            if child.xml_ns == child_ns:
                if child.xml_name == child_name:
                    return child

    return None

def fetch_children(element, child_name, child_ns, recursive=False):
    """
    Returns the list of children named 'child_name' with the namespace 'child_ns'

    Use it like this:
    e = Element.load('<root><node /></node /></root>')
    children = e.filtrate(fetch_children, child_name='node', child_ns=None)
    
    Keyword arguments:
    element -- parent element to go through
    child_name -- name of the element to lookup
    child_ns -- namespace of the element to lookup
    """
    children = []
    element_type = type(element)
    for child in element.xml_children:
        if isinstance(child, element_type):
            if child.xml_ns == child_ns:
                if child.xml_name == child_name:
                    children.append(child)
            if recursive:
                sub_children = fetch_children(child, child_name, child_ns, True)
                children.extend(sub_children)
            
    return children

def remove_useless_namespaces_decalaration(element):
    """
    Will recursuvely go through all the elements of a fragment
    and remove duplicate XML namespace declaration

    Keyword arguments:
    element -- root element to start from
    """
    attrs = element.xml_attributes[:]
    for attr in attrs:
        if (attr.xml_name == element.xml_prefix) and \
           (attr.xml_text == element.xml_ns):
            continue
        if attr.xml_ns == XMLNS_NS:
            element.xml_attributes.remove(attr)
    attrs = None
    for child in element_children(element):
        remove_useless_namespaces_decalaration(child)

def remove_duplicate_namespaces_declaration(element, visited_ns=None):
    """
    Will recursuvely go through all the elements of a fragment
    and remove duplicate XML namespace declaration

    Keyword arguments:
    element -- root element to start from
    visited_ns -- list of already visited namespace
    """
    if visited_ns is None:
        visited_ns = []
    _visited_ns = visited_ns[:]
    attrs = element.xml_attributes[:]
    for attr in attrs:
        if attr.xml_ns == XMLNS_NS:
            if attr.xml_text in visited_ns:
                element.xml_attributes.remove(attr)
            else:
                _visited_ns.append(attr.xml_text)
    attrs = None
    for child in element_children(element):
        remove_duplicate_namespaces_declaration(child, _visited_ns)
    _visited_ns = None

def find_by_id(element, id):
    """
    Looks for an element having the provided 'id'
    into the children recursively.

    Returns the found element or None.
    """
    result = None
    for child in element.xml_children:
        if isinstance(child, bridge.Element):
            _id = child.get_attribute('id')
            if _id is not None:
                if _id.xml_text == id:
                    result = child
                    break
            result = find_by_id(child, id)
            if result is not None:
                break
            
    return result
        

###################################################################
# For generator consumers
###################################################################

def element_children(element):
    """
    yields every direct bridge.Element child of 'element'
    """
    for child in element.xml_children:
        if isinstance(child, bridge.Element):
            yield child
    
