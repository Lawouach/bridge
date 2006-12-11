#!/usr/bin/env python
# -*- coding: utf-8 -*-

XML_NS = u'http://www.w3.org/XML/1998/namespace'
XML_PREFIX = u'xml'

XMLNS_NS = u'http://www.w3.org/2000/xmlns/'
XMLNS_PREFIX = u'xmlns'

XHTML1_NS = u'http://www.w3.org/1999/xhtml'
XHTML1_PREFIX = u'xhtml'

###########################################################
# Atom (RFC 4287, RFC 4685)
###########################################################
ATOM10_PREFIX = u'atom'
ATOMPUB_PREFIX = u'app'
THR=PREFIX = u'thr'

ATOM10_NS = u'http://www.w3.org/2005/Atom'
ATOMPUB_NS = u'http://purl.org/atom/app#'
THR_NS = u'http://purl.org/syndication/thread/1.0'

atom_as_attr = {ATOM10_NS: ['id', 'title', 'updated', 'published', 'icon', 'logo', 'generator',
                            'rights', 'subtitle', 'content', 'summary', 'name', 'uri', 'email'],
                ATOMPUB_NS: ['edited', 'accept'],
                THR_NS: ['in-reply-to', 'total']}

atom_as_list = {ATOM10_NS: ['author', 'contributor', 'category', 'link', 'entry'],
                ATOMPUB_NS: ['collection', 'workspace', 'categories']}

atom_attribute_of_element = {None: ['type', 'term', 'href', 'rel', 'scheme', 'label',
                                    'title', 'length', 'hreflang' 'src']}

###########################################################
# Dublin Core
###########################################################
DC_NS = u'http://purl.org/dc/elements/1.1/'
DC_PREFIX = u'dc'

dc_as_attr = {DC_NS: ['author', 'coverage', 'creator',
                      'date', 'description', 'format', 'identifier',
                      'language', 'publisher', 'relation', 'rights',
                      'source', 'subject', 'title', 'type']}

###########################################################
# Open Document Format
###########################################################
ODF_META_NS = u'urn:oasis:names:tc:opendocument:xmlns:meta:1.0'
ODF_META_PREFIX = u'meta'

ODF_OFFICE_NS = u'urn:oasis:names:tc:opendocument:xmlns:office:1.0'
ODF_OFFICE_PREFIX = u'office'

ODF_TEXT_NS = u'urn:oasis:names:tc:opendocument:xmlns:text:1.0'
ODF_TEXT_PREFIX = u'text'

ODF_TABLE_NS = u'urn:oasis:names:tc:opendocument:xmlns:table:1.0 '
ODF_TABLE_PREFIX = u'table'

ODF_DRAWING_NS = u'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0'
ODF_DRAWING_PREFIX = u'drawing'

ODF_PRESENTATION_NS = u'urn:oasis:names:tc:opendocument:xmlns:presentation:1.0'
ODF_PRESENTATION_PREFIX = u'presentation'

odf_meta_as_attr = {ODF_META_NS: ['document-statistic', 'creation-date',
                                  'keyword']}

odf_office_as_attr = {ODF_OFFICE_NS:['meta']}
odf_office_as_attr.update(odf_meta_as_attr)
odf_office_as_attr.update(dc_as_attr)

###########################################################
# XHTML
###########################################################
XHTML10_NS = u'http://www.w3.org/1999/xhtml'
XHTML10_PREFIX = u'xhtml'

xhtml_as_attr = {XHTML10_NS: ['html', 'head', 'body', 'title']}
xhtml_as_list = {XHTML10_NS: ['meta', 'link', 'script']}
xhtml_attribute_of_element = {None: ['content', 'name', 'lang']}
