#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bridge.commin import XHTML1_NS, XHTML1_PREFIX

import datetime
from bridge.lib import isodate

__all__ = ['extract_meta']

def extract_meta(element):
    """
    Extracts meta elements from an XHTML document and return them
    as a dictionnary of the form name: content

    Keyword argument:
    element -- Element instance to start with
    """
    metas = element.get_children('meta', XHTML1_NS)
    result = {}
    for meta in metas:
        name = meta.get_attribute('name')
        content = meta.get_attribute('content')
        result[name] = content

    return result
