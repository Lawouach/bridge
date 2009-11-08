#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = []

ANY_NAMESPACE = 1

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
ATOMPUB_NS = u'http://www.w3.org/2007/app'
THR_NS = u'http://purl.org/syndication/thread/1.0'

###########################################################
# Dublin Core
###########################################################
DC_NS = u'http://purl.org/dc/elements/1.1/'
DC_PREFIX = u'dc'

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

###########################################################
# XHTML
###########################################################
XHTML10_NS = u'http://www.w3.org/1999/xhtml'
XHTML10_PREFIX = u'xhtml'

###########################################################
# XMPP/Jabber
###########################################################

# see http://www.xmpp.org/rfcs/rfc3920.html
XMPP_CLIENT_NS = u'jabber:client'
XMPP_CLIENT_PREFIX = u'client'

# see http://www.xmpp.org/extensions/xep-0004.html
XMPP_DATA_FORM_NS = u'jabber:x:data'
XMPP_DATA_FORM_PREFIX = u'xdata'

# see http://www.xmpp.org/extensions/xep-0060.html
XMPP_PUBSUB_NS = u'http://jabber.org/protocol/pubsub'
XMPP_PUBSUB_PREFIX = u'pubsub'

XMPP_PUBSUB_OWNER_NS = u'http://jabber.org/protocol/pubsub#owner'
XMPP_PUBSUB_OWNER_PREFIX = u'pubsub'

XMPP_PUBSUB_NODE_CONFIG_NS = u'http://jabber.org/protocol/pubsub#node_config'
XMPP_PUBSUB_NODE_CONFIG_PREFIX = u'pubsub'

XMPP_PUBSUB_EVENT_NS = u'http://jabber.org/protocol/pubsub#event'
XMPP_PUBSUB_EVENT_PREFIX = u'pubsub'

XMPP_OFFLINE_NS = u'http://jabber.org/protocol/offline'
XMPP_OFFLINE_PREFIX = None

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

# see http://www.xmpp.org/extensions/xep-0009.html
XMPP_RPC_NS = u'jabber:iq:rpc'
XMPP_RPC_PREFIX = None

# see http://www.xmpp.org/rfcs/rfc3920.html
XMPP_STANZA_ERROR_NS = u'urn:ietf:params:xml:ns:xmpp-stanzas'
XMPP_STANZA_ERROR_PREFIX = None

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

# see http://www.xmpp.org/rfcs/rfc3921.html
XMPP_ROSTER_NS = u'jabber:iq:roster'
XMPP_ROSTER_PREIX = u'roster'

# see http://www.xmpp.org/rfcs/rfc3921.html
XMPP_PRIVACY_LIST_NS = u'jabber:iq:privacy'
XMPP_PRIVACY_LIST_PREFIX = None

# see http://www.xmpp.org/extensions/xep-0071.html
XMPP_XHTML_IM_NS = u'http://jabber.org/protocol/xhtml-im'
XMPP_XHTML_IM_PREFIX = None

# see http://www.xmpp.org/extensions/xep-0022.html
XMPP_EVENT_NS = u'jabber:x:event'
XMPP_EVENT_PREFIX = None

# see http://www.xmpp.org/extensions/xep-0012.html
XMPP_LAST_NS = u'jabber:iq:last'
XMPP_LAST_PREFIX = None

# see http://xmpp.org/extensions/xep-0092.html
XMPP_VERSION_NS = u'jabber:iq:version'
XMPP_VERSION_PREFIX = None

# see http://www.xmpp.org/extensions/xep-0095.html
XMPP_SI_NS = u'http://jabber.org/protocol/si'
XMPP_SI_PREFIX = None

# see http://www.xmpp.org/extensions/xep-0096.html
XMPP_SI_FILE_TRANSFER_NS = u'http://jabber.org/protocol/si/profile/file-transfer'
XMPP_SI_FILE_TRANSFER_PREFIX = None

# see http://www.xmpp.org/extensions/xep-0020.html
XMPP_FEATURE_NEG_NS = u'http://jabber.org/protocol/feature-neg'
XMPP_FEATURE_NEG_PREFIX = None

# see http://www.xmpp.org/extensions/xep-0066.html
XMPP_OOB_NS = u'jabber:iq:oob'
XMPP_OOB_PPREFIX = None
XMPP_XOOB_NS = u'jabber:x:oob'
XMPP_XOOB_PPREFIX = None

# see http://www.xmpp.org/extensions/xep-0077.html
XMPP_IBR_NS = u'jabber:iq:register'
XMPP_IBR_PREFIX = None

# see http://www.xmpp.org/extensions/xep-0065.html
XMPP_BYTESTREAMS_NS = u'http://jabber.org/protocol/bytestreams'
XMPP_BYTESTREAMS_PREFIX = None

# see http://www.xmpp.org/extensions/xep-0092.html
XMPP_VERSION_NS = u'jabber:iq:version'
XMPP_VERSION_PREFIX = None

# see http://www.xmpp.org/extensions/xep-0054.html
XMPP_VCARD_NS = u'vcard-temp'
XMPP_VCARD_PREFIX = u'vcard'

XMPP_USER_PROFILE_NS = u'urn:xmpp:tmp:profile'
XMPP_USER_PROFILE_PREFIX = None

XMPP_SHIM_NS = u'http://jabber.org/protocol/shim'
XMPP_SHIM_PREFIX = None

XMPP_COMPONENT_ACCEPT_NS = u"jabber:component:accept"
XMPP_COMPONENT_ACCEPT_PREFIX = None

XMPP_COMPONENT_CONNECT_NS = u"jabber:component:connect"
XMPP_COMPONENT_CONNECT_PREFIX = None

###########################################################
# RDF
###########################################################

RDF_PREFIX = u'rdf'
RDF_NS = u'http://www.w3.org/1999/02/22-rdf-syntax-ns#'

RDF_IMDB_PREFIX = u'imdb'
RDF_IMDB_NS = u'http://www.csd.abdn.ac.uk/~ggrimnes/dev/imdb/IMDB#'

###########################################################
# LLUP http://dev.llup.org/
###########################################################
LLUP_NS = u"http://www.x2x2x.org/llup"
LLUP_PREFIX = u'llup'

###########################################################
# http://trac.defuze.org/ns
###########################################################
DEFUZE_QS_NS = u"http://purl.oclc.org/DEFUZE/qs"
DEFUZE_QS_PREFIX = None

###########################################################
# AWS http://aws.amazon.com/sqs
###########################################################
AWS_SQS_20070501_NS = u'http://queue.amazonaws.com/doc/2007-05-01/'
AWS_SQS_20070501_PREFIX = None
