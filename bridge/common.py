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
THR_PREFIX = u'thr'

ATOM10_NS = u'http://www.w3.org/2005/Atom'
ATOMPUB_NS = u'http://purl.org/atom/app#'
THR_NS = u'http://purl.org/syndication/thread/1.0'

atom_as_attr = {ATOM10_NS: ['feed', 'id', 'title', 'updated', 'published', 'icon', 'logo', 'generator',
                            'rights', 'subtitle', 'content', 'summary', 'name', 'uri', 'email'],
                ATOMPUB_NS: ['edited', 'accept'],
                THR_NS: ['in-reply-to', 'total']}

atom_as_list = {ATOM10_NS: ['author', 'contributor', 'category', 'link', 'entry'],
                ATOMPUB_NS: ['collection', 'workspace', 'categories']}

atom_attribute_of_element = {None: ['type', 'term', 'href', 'rel', 'scheme', 'label',
                                    'title', 'length', 'hreflang' 'src', 'ref'],
                             THR_NS: ['count']}

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

odf_meta_as_attr = {ODF_META_NS: ['document-statistic', 'creation-date']}
odf_meta_as_list = {ODF_META_NS: ['keyword']}

odf_office_as_attr = {ODF_OFFICE_NS: ['meta']}
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


###########################################################
# XMPP/Jabber
###########################################################

# see http://www.xmpp.org/rfcs/rfc3920.html
XMPP_CLIENT_NS = u'jabber:client'
XMPP_CLIENT_PREFIX = u'client'

xmpp_client_as_attr = {XMPP_CLIENT_NS: ['message', 'subject', 'body', 'thread', 'presence', 'iq']}
xmpp_client_as_list = {XMPP_CLIENT_NS: ['error']}
xmpp_client_attribute_of_element = {None: ['from', 'id', 'to', 'type', 'show', 'status', 'priority']}

# see http://www.xmpp.org/extensions/xep-0004.html
XMPP_DATA_FORM_NS = u'jabber:x:data'
XMPP_DATA_FORM_PREFIX = u'xdata'

# see http://www.xmpp.org/extensions/xep-0060.html
XMPP_PUBSUB_NS = u'http://jabber.org/protocol/pubsub'
XMPP_PUBSUB_PREFIX = u'pubsub'

xmpp_pubsub_as_attr = {XMPP_PUBSUB_NS: ['pubsub', 'create']}
xmpp_pubsub_as_list = {XMPP_PUBSUB_NS: ['configure', 'subscribe', 'options', 'affiliations',
                                        'items', 'publish', 'retract', 'subscription',
                                        'subscriptions', 'unsubscribe', 'subscribe-options']}
xmpp_pubsub_attribute_of_element = {None: ['subid']}

# see http://www.xmpp.org/rfcs/rfc3920.html
XMPP_STREAM_NS = u'http://etherx.jabber.org/streams'
XMPP_STREAM_PREFIX = u'stream'

# see http://www.xmpp.org/extensions/xep-0078.html
XMPP_AUTH_NS = u'jabber:iq:auth'
XMPP_AUTH_PREFIX = u'auth'

# see http://www.xmpp.org/rfcs/rfc3920.html
XMPP_SASL_NS = u'urn:ietf:params:xml:ns:xmpp-sasl'
XMPP_SASL_PREFIX = u'sasl'

XMPP_TLS_NS = u'urn:ietf:params:xml:ns:xmpp-tls'
XMPP_TLS_PREFIX = u'starttls'

# see http://www.xmpp.org/rfcs/rfc3920.html
XMPP_BIND_NS = u'urn:ietf:params:xml:ns:xmpp-bind'
XMPP_BIND_PREFIX = u'bind'

xmpp_bind_as_attr = {XMPP_BIND_NS: ['bind', 'resource', 'jid']}

# see http://www.xmpp.org/rfcs/rfc3921.html
XMPP_SESSION_NS = u'urn:ietf:params:xml:ns:xmpp-session'
XMPP_SESSION_PREFIX = u'session'

# see http://www.xmpp.org/extensions/xep-0030.html
XMPP_DISCO_ITEMS_NS = u'http://jabber.org/protocol/disco#items'
XMPP_DISCO_ITEMS_PREFIX = u'disco'

# see http://www.xmpp.org/extensions/xep-0030.html
XMPP_DISCO_INFO_NS = u'http://jabber.org/protocol/disco#info'
XMPP_DISCO_INFO_PREFIX = u'info'

XMPP_ROSTER_NS = u'jabber:iq:roster'
XMPP_ROSTER_PREIX = u'roster'

xmpp_as_attr = {}
xmpp_as_attr.update(xmpp_client_as_attr)
xmpp_as_attr.update(xmpp_pubsub_as_attr)
xmpp_as_attr.update(xmpp_bind_as_attr)

xmpp_as_list = {}
xmpp_as_list.update(xmpp_client_as_list)
xmpp_as_list.update(xmpp_pubsub_as_list)

xmpp_attribute_of_element = {}
xmpp_attribute_of_element.update(xmpp_client_attribute_of_element)
xmpp_attribute_of_element.update(xmpp_pubsub_attribute_of_element)

###########################################################
# RDF
###########################################################

RDF_PREFIX = u'rdf'
RDF_NS = u'http://www.w3.org/1999/02/22-rdf-syntax-ns#'

RDF_IMDB_PREFIX = u'imdb'
RDF_IMDB_NS = u'http://www.csd.abdn.ac.uk/~ggrimnes/dev/imdb/IMDB#'
