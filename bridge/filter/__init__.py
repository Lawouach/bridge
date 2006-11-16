#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
