#!/usr/bin/env python
# -*- coding: utf-8 -*-

XML_NS = 'http://www.w3.org/XML/1998/namespace'
XML_PREFIX = u'xml'

XHTML1_NS = u'http://www.w3.org/1999/xhtml'
XHTML1_PREFIX = u'xhtml'

ATOM10_PREFIX = u'atom'
ATOMPUB_PREFIX = u'app'
THR=PREFIX = u'thr'

ATOM10_NS = u'http://www.w3.org/2005/Atom'
ATOMPUB_NS = u'http://purl.org/atom/app#'
THR_NS = u'http://purl.org/syndication/thread/1.0'

atom_as_attr = {ATOM10_NS: ['id', 'title', 'updated', 'published', 'icon', 'logo', 'generator',
                            'rights', 'subtitle', 'content', 'summary'],
                ATOMPUB_NS: ['edited'],
                THR_NS: ['in_reply_to', 'total']}

atom_as_list = {ATOM10_NS: ['author', 'contributor', 'category', 'link', 'entry'],
                ATOMPUB_NS: ['collection', 'workspace', 'categories']}

atom_attribute_of_element = {None: ['type', 'term', 'href', 'rel', 'scheme', 'label',
                                    'title', 'length', 'hreflang' 'src']}
