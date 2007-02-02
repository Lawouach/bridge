#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.sax as xs
import xml.sax.saxutils as xss
from xml.parsers import expat

import StringIO
from bridge import Element as E
from bridge import Attribute as A
from bridge import Comment as C
from bridge import PI
from bridge import Document as D

__all__ = ['create_parser', 'BridgeIncrementalHandler']

class BridgeIncrementalHandler(xss.XMLGenerator):
    def __init__(self, out, encoding='UTF-8', enable_dispatching=True):
        """This handler allows the incremental parsing of an XML document
        while providing simple ways to dispatch at precise point of the
        parsing back to the caller.

        Here's an example:

        >>> from bridge.parser.incremental import create_parser
        >>> p, h, s = create_parser()
        >>> def dispatch(e):
        ...     print e.xml()
        ...
        >>> h.register_at_level(1, dispatch)
        >>> p.feed('<r')
        >>> p.feed('><b')
        >>> p.feed('/></r>')
        <?xml version="1.0" encoding="UTF-8"?>
        <b xmlns=""></b>
        
        Alternatively this can even be used as a generic parser. If you
        don't need dispatching you simply set ``enable_dispatching`` to
        False.

        >>> from bridge.parser.incremental import create_parser
        >>> p, h, s = create_parser()
        >>> h.enable_dispatching = False
        >>> p.feed('<r><b/></r>')
        >>> h.doc()
        <r element at 0xb7ca99ccL />
        >>> h.doc().xml(omit_declaration=True)
        '<r xmlns=""><b></b></r>'

        Note that this handler has limitations as it doesn't
        manage DTDs.
        
        """
        xss.XMLGenerator.__init__(self, out, encoding)
        self._current_el = self._root = D()
        self._current_level = 0
        self._as_cdata = False
        self._dispatchers = {}
        self.enable_dispatching = enable_dispatching
        
    def register_at_level(self, level, dispatcher):
        """Registers a dispatcher at a given level within the
        XML tree of elements being built.

        The ``level``, an integer, is zero-based. So the root
        element of the XML tree is 0 and its direct children
        are at level 1.

        The ``dispatcher`` is a callable object only taking
        one parameter, a bridge.Element instance.
        """
        self._dispatchers[level] = dispatcher

    def register_on_element(self, local_name, dispatcher, namespace=None):
        """Registers a dispatcher on a given element met during
        the parsing.

        The ``local_name`` is the local name of the element. This
        element can be namespaced if you provide the ``namespace``
        parameter.

        The ``dispatcher`` is a callable object only taking
        one parameter, a bridge.Element instance.
        """
        self._dispatchers[(namespace, local_name)] = dispatcher
        
    def register_on_element_per_level(self, local_name, level, dispatcher, namespace=None):
        """Registers a dispatcher at a given level within the
        XML tree of elements being built as well as for a
        specific element.

        The ``level``, an integer, is zero-based. So the root
        element of the XML tree is 0 and its direct children
        are at level 1.

        The ``local_name`` is the local name of the element. This
        element can be namespaced if you provide the ``namespace``
        parameter.

        The ``dispatcher`` is a callable object only taking
        one parameter, a bridge.Element instance.
        """
        self._dispatchers[(level, (namespace, local_name))] = dispatcher

    # see http://www.xml.com/pub/a/2003/03/10/python.html
    def _split_qname(self, qname):
        qname_split = qname.split(':')
        if len(qname_split) == 2:
            prefix, local = qname_split
        else:
            prefix = None
            local = qname_split
        return prefix, local

    def processingInstruction(self, target, data):
        PI(target, data, self._current_el)

    def startElementNS(self, name, qname, attrs):
        uri, local_name = name
        e = E(local_name, parent=self._current_el)
        
        if uri:
            e.xml_ns = uri
            e.xml_prefix = self._current_context[uri]
            
        for name, value in attrs.items():
            (namespace, local_name) = name
            qname = attrs.getQNameByName(name)
            prefix = self._split_qname(qname)[0]
            A(local_name, value, prefix, namespace, e)
        
        self._current_el = e
        self._current_level = self._current_level + 1
        
    def endElementNS(self, name, qname):
        self._current_level = self._current_level - 1
        if self.enable_dispatching:
            if self._current_level in self._dispatchers:
                self._dispatchers[self._current_level](self._current_el)
            else:
                pattern = (self._current_el.xml_ns, self._current_el.xml_name)
                if pattern in self._dispatchers:
                    self._dispatchers[pattern](self._current_el)
                else:
                    pattern = (self._current_level, pattern)
                    if pattern in self._dispatchers:
                        self._dispatchers[pattern](self._current_el)
        self._current_el = self._current_el.xml_parent

    def characters(self, content):
        self._current_el.as_cdata = self._as_cdata
        if not self._as_cdata and not self._current_el.xml_text:
            self._current_el.xml_text = content
        else:
            self._current_el.xml_children.append(content)
        self._as_cdata = False

    def comment(self, data):
        C(data, self._current_el)
        
    def startCDATA(self):
        self._as_cdata = True

    def endCDATA(self):
        pass

    def startDTD(self, name, public_id, system_id):
        pass

    def endDTD(self):
        pass
    
    def doc(self):
        """Returns the root bridge.Document instance of the parsed
        document. You have to call the close() method of the
        parser first.
        """
        return self._root

def create_parser(out=None, encoding='UTF-8'):
    """Creates a new parser using the built-in expat
    parser and sets the handler using BridgeIncrementalParser.

    If ``out`` is provided it must be a fileobject, if not
    a StringIO instance will be created and returned.

    The ``encoding`` will be passed to the handler.

    Returns a tuple of the form (parser, handler, out)
    """
    parser = xs.make_parser()
    parser.setFeature(xs.handler.feature_namespaces, True)
    if not out:
        out = StringIO.StringIO()
    handler = BridgeIncrementalHandler(out, encoding)
    parser.setContentHandler(handler)
    parser.setProperty(xs.handler.property_lexical_handler, handler)

    return parser, handler, out
