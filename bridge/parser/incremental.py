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
from bridge.filter import lookup

__all__ = ['create_parser', 'BridgeIncrementalHandler']

class BridgeIncrementalHandler(xss.XMLGenerator):
    def __init__(self, out, encoding='UTF-8'):
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
        don't need dispatching you simply call ``disable_dispatching``.

        >>> from bridge.parser.incremental import create_parser
        >>> p, h, s = create_parser()
        >>> h.disable_dispatching()
        >>> p.feed('<r><b/></r>')
        >>> h.doc()
        <r element at 0xb7ca99ccL />
        >>> h.doc().xml(omit_declaration=True)
        '<r xmlns=""><b></b></r>'

        Note that this handler has limitations as it doesn't
        manage DTDs.

        Note also that this class is not thread-safe.
        """
        xss.XMLGenerator.__init__(self, out, encoding)
        self._current_el = self._root = D()
        self._current_level = 0
        self._as_cdata = False
        self._level_dispatchers = {}
        self._element_dispatchers = {}
        self._element_level_dispatchers = {}
        self._path_dispatchers = {}
        
        self.enable_level_dispatching = False
        self.enable_element_dispatching = False
        self.enable_element_by_level_dispatching = False
        self.enable_dispatching_by_path = False

        self.as_attribute = {}
        self.as_list = {}
        self.as_attribute_of_element = {}

    def disable_dispatching(self):
        self.enable_level_dispatching = False
        self.enable_element_dispatching = False
        self.enable_element_by_level_dispatching = False
        self.enable_dispatching_by_path = False

    def enable_dispatching(self):
        self.enable_level_dispatching = True
        self.enable_element_dispatching = True
        self.enable_element_by_level_dispatching = True
        self.enable_dispatching_by_path = True

    def register_at_level(self, level, dispatcher):
        """Registers a dispatcher at a given level within the
        XML tree of elements being built.

        The ``level``, an integer, is zero-based. So the root
        element of the XML tree is 0 and its direct children
        are at level 1.

        The ``dispatcher`` is a callable object only taking
        one parameter, a bridge.Element instance.
        """
        self.enable_level_dispatching = True
        self._level_dispatchers[level] = dispatcher

    def unregister_at_level(self, level):
        """Unregisters a dispatcher at a given level
        """
        if level in self._level_dispatchers:
            del self._level_dispatchers[level]
        if len(self._level_dispatchers) == 0:
            self.enable_level_dispatching = False
            
    def register_on_element(self, local_name, dispatcher, namespace=None):
        """Registers a dispatcher on a given element met during
        the parsing.

        The ``local_name`` is the local name of the element. This
        element can be namespaced if you provide the ``namespace``
        parameter.

        The ``dispatcher`` is a callable object only taking
        one parameter, a bridge.Element instance.
        """
        self.enable_element_dispatching = True
        self._element_dispatchers[(namespace, local_name)] = dispatcher

    def unregister_on_element(self, local_name, namespace=None):
        """Unregisters a dispatcher for a specific element.
        """
        key = (namespace, local_name)
        if key in self._element_dispatchers:
            del self._element_dispatchers[key]
        if len(self._element_dispatchers) == 0:
            self.enable_element_dispatching = False
            
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
        self.enable_element_by_level_dispatching = True
        self._element_level_dispatchers[(level, (namespace, local_name))] = dispatcher

    def unregister_on_element_per_level(self, local_name, level, namespace=None):
        """Unregisters a dispatcher at a given level for a specific
        element.
        """
        key = (level, (namespace, local_name))
        if key in self._element_level_dispatchers:
            del self._element_level_dispatchers[key]
        if len(self._element_level_dispatchers) == 0:
            self.enable_element_by_level_dispatching = False

    def register_by_path(self, path, dispatcher):
        self.enable_dispatching_by_path = True
        self._path_dispatchers[path] = dispatcher

    def unregister_by_path(self, path):
        if path in self._path_dispatchers:
            del self._path_dispatchers[path]
        if len(self._path_dispatchers) == 0:
            self.enable_dispatching_by_path = False

    def startDocument(self):
        self._root = D()
        self._root.as_attribute = self.as_attribute
        self._root.as_list = self.as_list
        self._root.as_attribute_of_element = self.as_attribute_of_element
        self._current_el = self._root
        self._current_level = 0
        self._as_cdata = False
        xss.XMLGenerator.startDocument(self)

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
        prefix = None
        if uri:
            prefix = self._current_context[uri]
        e = E(local_name, prefix=prefix, namespace=uri, parent=self._current_el)
        
        for name, value in attrs.items():
            (namespace, local_name) = name
            qname = attrs.getQNameByName(name)
            prefix = self._split_qname(qname)[0]
            A(local_name, value, prefix, namespace, e)
        
        self._current_el = e
        self._current_level = self._current_level + 1
        
    def endElementNS(self, name, qname):
        self._current_level = current_level = self._current_level - 1
        current_element = self._current_el
        if self.enable_level_dispatching:
            if current_level in self._level_dispatchers:
                self._level_dispatchers[current_level](current_element)
        if self.enable_element_dispatching:
            pattern = (current_element.xml_ns, current_element.xml_name)
            if pattern in self._element_dispatchers:
                self._element_dispatchers[pattern](current_element)
        if self.enable_element_by_level_dispatching:
            pattern = (current_level, (current_element.xml_ns, current_element.xml_name))
            if pattern in self._element_level_dispatchers:
                self._element_level_dispatchers[pattern](current_element)
        if self.enable_dispatching_by_path:
            for path in self._path_dispatchers:
                match_found = current_element.filtrate(lookup, path=path)
                if match_found:
                    self._path_dispatchers[path](match_found)
                    break
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
