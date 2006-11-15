#!/usr/bin/env python
# -*- coding: utf-8 -*-

ATOM10_NS = u'http://www.w3.org/2005/Atom'
ATOMPUB_NS = u'http://purl.org/atom/app#'
XHTML1_NS = u'http://www.w3.org/1999/xhtml'
THR_NS = u'http://purl.org/syndication/thread/1.0'

import datetime
from bridge.lib import isodate

__all__ = ['published_after', 'updated_after',
           'published_before', 'updated_before']

def _is_before_date(node, dt_pivot, strict=True):
    dt = isodate.parse(str(node))
    dt = datetime.datetime.utcfromtimestamp(dt)
    if strict:
        return dt < dt_pivot
    else:
        return dt <= dt_pivot
    
def _is_after_date(node, dt_pivot, strict=True):
    dt = isodate.parse(str(node))
    dt = datetime.datetime.utcfromtimestamp(dt)
    if strict:
        return dt > dt_pivot
    else:
        return dt >= dt_pivot

def _cmp_date(func, name, element, dt_pivot, strict=True, recursive=False, include_feed=True):
    elements = []
    if element.name == u'feed' and element.xmlns == ATOM10_NS:
        if include_feed:
            if element.has_element(name, ATOM10_NS):
                if func(element.published, dt_pivot, strict):
                    elements.append(element)
            
        if recursive:
            for entry in element.entry:
                if entry.has_element(name, ATOM10_NS):
                    if func(entry.published, dt_pivot, strict):
                        elements.append(entry)        
    elif element.name == u'entry' and element.xmlns == ATOM10_NS:
        if element.has_element(name, ATOM10_NS):
            if func(element.published, dt_pivot, strict):
                elements.append(element) 
                
    return elements

def published_after(element, dt_pivot, strict=True, recursive=False, include_feed=True):
    """
    Returns the list of elements which have been published after the given date.

    Keyword arguments:
    element -- atom feed or entry element
    dt_pivot -- datetime instance to compare to
    strict -- if True only accepts elements which are published strictly after
    the dt_pivot. if False elmeents which published date equal dt_pivot will be included
    in the result
    recursive -- if the element is a feed and recursive is True it will iterate through
    the feed entries as well
    include_feed -- if the element is a feed, recursive is True but you don't want the
    feed element to be part of the result set this to False
    """
    return _cmp_date(_is_after_date, 'published', element, dt_pivot,
                     strict, recursive, include_feed)

def updated_after(element, dt_pivot, strict=True, recursive=False, include_feed=True):
    """
    Returns the list of elements which have been updated  after the given date.

    Keyword arguments:
    element -- atom feed or entry element
    dt_pivot -- datetime instance to compare to
    strict -- if True only accepts elements which are published strictly after
    the dt_pivot. if False elements which published date equals dt_pivot will be included
    in the result
    recursive -- if the element is a feed and recursive is True it will iterate through
    the feed entries as well
    include_feed -- if the element is a feed, recursive is True but you don't want the
    feed element to be part of the result set this to False
    """
    return _cmp_date(_is_after_date, 'updated', element, dt_pivot,
                     strict, recursive, include_feed)

def published_before(element, dt_pivot, strict=True, recursive=False, include_feed=True):
    """
    Returns the list of elements which have been published before the given date.

    Keyword arguments:
    element -- atom feed or entry element
    dt_pivot -- datetime instance to compare to
    strict -- if True only accepts elements which are published strictly before
    the dt_pivot. if False elements which published date equals dt_pivot will be included
    in the result
    recursive -- if the element is a feed and recursive is True it will iterate through
    the feed entries as well
    include_feed -- if the element is a feed, recursive is True but you don't want the
    feed element to be part of the result set this to False
    """
    return _cmp_date(_is_before_date, 'published', element, dt_pivot,
                     strict, recursive, include_feed)

def updated_before(element, dt_pivot, strict=True, recursive=False, include_feed=True):
    """
    Returns the list of elements which have been updated before the given date.

    Keyword arguments:
    element -- atom feed or entry element
    dt_pivot -- datetime instance to compare to
    strict -- if True only accepts elements which are updated strictly before
    the dt_pivot. if False elements which updated date equals dt_pivot will be included
    in the result
    recursive -- if the element is a feed and recursive is True it will iterate through
    the feed entries as well
    include_feed -- if the element is a feed, recursive is True but you don't want the
    feed element to be part of the result set this to False
    """
    return _cmp_date(_is_before_date, 'updated', element, dt_pivot,
                     strict, recursive, include_feed)


def lookup_entry(element, id):
    if element.has_element(u'entry', ATOM10_NS):
        for entry in element.entry:
            if entry.id.xml_text == id:
                return entry
                
    return None
