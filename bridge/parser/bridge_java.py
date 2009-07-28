# -*- coding: utf-8 -*-

import os
import os.path

__all__ = ['Parser', 'IncrementalParser', 'DispatchParser']

from bridge import Element
from bridge import Attribute
from bridge import PI, Comment, Document

from bridge import ENCODING
from bridge.common import ANY_NAMESPACE

from java.io import InputStream, PipedInputStream, PipedOutputStream, BufferedInputStream
from javax.xml.stream import *
from javax.xml.stream.events import *

class Parser(object): pass
class IncrementalParser(object): pass

class DispatchHandler(object):
    def __init__(self):
        """This handler allows the incremental parsing of an XML document
        while providing simple ways to dispatch at precise point of the
        parsing back to the caller.

        Here's an example:

        >>> from parser import DispatchParser
        >>> p = DispatchParser()
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

        >>> from parser import DispatchParser
        >>> p = DispatchParser()
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
        self._level_dispatchers = {}
        self._element_dispatchers = {}
        self._element_level_dispatchers = {}
        self._path_dispatchers = {}
        self.default_dispatcher = None
        self.default_dispatcher_start_element = None

        self.disable_dispatching()

    def register_default(self, handler):
        self.default_dispatcher = handler

    def unregister_default(self):
        self.default_dispatcher = None

    def register_default_start_element(self, handler):
        self.default_dispatcher_start_element = handler

    def unregister_default_start_element(self):
        self.default_dispatcher_start_element = None

    def disable_dispatching(self):
        self.default_dispatcher = None
        self.default_dispatcher_start_element = None
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
        one parameter, a Element instance.
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
        one parameter, a Element instance.
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
        one parameter, a Element instance.
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

    def startElementNS(self, name, qname, attrs):
        #print "%s: %f" % (name, time())
        IncrementalHandler.startElementNS(self, name, qname, attrs)
        if self.default_dispatcher_start_element:
            self.default_dispatcher_start_element(self._current_el)

    def endElementNS(self, name, qname):
        #print "#%s%s: %f" % (" " * self._current_level, name, time())
        self._current_level = current_level = self._current_level - 1
        if not self._current_el:
            return
        current_element = self._current_el

        dispatched = False
        
        if self.enable_element_dispatching:
            pattern = (current_element.xml_ns, current_element.xml_name)
            if pattern in self._element_dispatchers:
                self._element_dispatchers[pattern](current_element)
                dispatched = True

        if not dispatched and self.default_dispatcher:
            self.default_dispatcher(current_element)
            
        self._current_el = self._current_el.xml_parent

class DispatchParser(object):
    def __init__(self):
        self._depth = 0
        self._buffer = ''

        self._fed = PipedOutputStream()
        self._feeder = BufferedInputStream(PipedInputStream(self._fed))
        self._fed.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')

        self._ipf = XMLInputFactory.newInstance()
        self._ipf.setProperty(XMLInputFactory.IS_NAMESPACE_AWARE, True)
        self._sr = self._ipf.createXMLStreamReader(self._feeder)
        self._er = self._ipf.createXMLEventReader(self._sr)

    def __del__(self):
        self._close()
        
    def close(self):
        self._fed.close()
        self._feeder.close()
        self._er.close()
        self._sr.close()
        self._ipf = None
        
    def _parse(self, chunk, fragment=False):
        self._fed.write(chunk)
        er = self._er
        consumed = False
        while er.hasNext():
            if not fragment and self._feeder.available() == 0 and consumed:
                break
            event = er.next()
            etype = event.getEventType()
            if etype == XMLEvent.START_ELEMENT:
                consumed = True
                self._depth += 1
                element = event.asStartElement()
                print "S", element.getName(), element.getAttributes()
            elif etype == XMLEvent.END_ELEMENT:
                consumed = True
                self._depth -= 1
                element = event.asEndElement()
                print "E", element.getName()
                if self._depth == 0:
                    break
            elif etype == XMLEvent.CHARACTERS:
                consumed = False
                text = event.asCharacters().getData()
                print "C", text
            elif etype == XMLEvent.COMMENT:
                consumed = True
                pass
            elif etype == XMLEvent.PROCESSING_INSTRUCTION:
                consumed = True
                pass
            elif etype == XMLEvent.START_DOCUMENT:
                pass
            elif etype == XMLEvent.END_DOCUMENT:
                break

    def feed(self, chunk):
        if not chunk:
            return

        self._buffer = self._buffer + chunk

        pos = posa = 0
        posb = -1
        last_posb = 0
        new_buffer = ''
        while 1:
            found = False
            posa = self._buffer.find('<', pos)
            if posa > -1:
                posb = self._buffer.find('>', posa)
                if posb > -1:
                    found = True
                    pos = posb
                    self._parse(self._buffer[last_posb:posb+1])  
                    last_posb = posb+1
                
            if not found:
                break
                
        self._buffer = self._buffer[last_posb:]

    def register_default(self, handler):
        self.handler.register_default(handler)

    def unregister_default(self):
        self.handler.unregister_default()

    def register_default_start_element(self, handler):
        self.handler.register_default_start_element(handler)

    def unregister_default_start_element(self):
        self.handler.unregister_default_start_element()
          
    def reset(self):
        self.handler.reset()
        self.parser.reset()

    def disable_dispatching(self):
        self.handler.disable_dispatching()

    def enable_dispatching(self):
        self.handler.enable_dispatching()

    def register_at_level(self, level, dispatcher):
        """Registers a dispatcher at a given level within the
        XML tree of elements being built.

        The ``level``, an integer, is zero-based. So the root
        element of the XML tree is 0 and its direct children
        are at level 1.

        The ``dispatcher`` is a callable object only taking
        one parameter, a Element instance.
        """
        self.handler.register_at_level(level, dispatcher)

    def unregister_at_level(self, level):
        """Unregisters a dispatcher at a given level
        """
        self.handler.unregister_at_level(level, dispatcher)
            
    def register_on_element(self, local_name, dispatcher, namespace=None):
        """Registers a dispatcher on a given element met during
        the parsing.

        The ``local_name`` is the local name of the element. This
        element can be namespaced if you provide the ``namespace``
        parameter.

        The ``dispatcher`` is a callable object only taking
        one parameter, a Element instance.
        """
        self.handler.register_on_element(local_name, dispatcher, namespace)

    def unregister_on_element(self, local_name, namespace=None):
        """Unregisters a dispatcher for a specific element.
        """
        self.handler.unregister_on_element(local_name, namespace)
            
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
        one parameter, a Element instance.
        """
        self.handler.register_on_element_per_level(local_name, level, dispatcher, namespace)

    def unregister_on_element_per_level(self, local_name, level, namespace=None):
        """Unregisters a dispatcher at a given level for a specific
        element.
        """
        self.handler.unregister_on_element_per_level(local_name, level, namespace)

    def register_by_path(self, path, dispatcher):
        self.handler.register_by_path(path, dispatcher)

    def unregister_by_path(self, path):
        self.handler.unregister_by_path(path)
