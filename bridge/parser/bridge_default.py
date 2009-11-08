# -*- coding: utf-8 -*-

import os
import os.path
from StringIO import StringIO
from time import time

__all__ = ['Parser', 'IncrementalParser', 'DispatchParser']

import xml.dom as xd
import xml.dom.minidom as xdm
import xml.sax as xs
import xml.sax.handler as xsh
import xml.sax.saxutils as xss
from xml.sax.saxutils import quoteattr, escape, unescape

from bridge import Element, ENCODING, Attribute, PI, Comment, Document
from bridge.common import ANY_NAMESPACE

class Parser(object):
    def __init__(self):
        self.buffer = []
        
    def __deserialize_fragment(self, current, parent):
        if current.attributes:
            for key in iter(current.attributes.keys()):
                attr = current.attributes[key]
                Attribute(attr.localName, attr.value,
                          attr.prefix, attr.namespaceURI, parent)

        children_num = len(current.childNodes)
        children = iter(current.childNodes)
        for child in children:
            nt = child.nodeType
            if nt == xd.Node.TEXT_NODE:
                data = escape(child.data)
                if children_num == 1:
                    parent.xml_text = data
                else:
                    parent.xml_children.append(data)
            elif nt == xd.Node.CDATA_SECTION_NODE:
                parent.as_cdata = True
                data = child.data
                if children_num == 1:
                    parent.xml_text = data
                else:
                    parent.xml_children.append(data)
            elif nt == xd.Node.COMMENT_NODE:
                Comment(data=unicode(child.data), parent=parent)
            elif nt == xd.Node.PROCESSING_INSTRUCTION_NODE:
                PI(target=unicode(child.target), data=unicode(child.data), parent=parent)
            elif nt == xd.Node.ELEMENT_NODE:
                element = Element(name=child.localName, prefix=child.prefix,
                                  namespace=child.namespaceURI, parent=parent)

                self.__deserialize_fragment(child, element)

    def __qname(self, name, prefix=None):
        if prefix:
            return "%s:%s" % (prefix, name)
        return name
    
    def __attrs(self, node):
        for attr_ns, attr_name in iter(node.xml_attributes):
            if attr_ns == xd.XMLNS_NAMESPACE and attr_name == 'xmlns':
                continue
            attr = node.xml_attributes[(attr_ns, attr_name)]
            ns = attr.xml_ns
            prefix = attr.xml_prefix
            name = attr.xml_name
            yield ns, name, prefix, attr.xml_text or ''

    def __append_namespace(self, prefix, ns):
        if prefix:
            self.buffer.append(' xmlns:%s="%s"' % (prefix, ns))
        elif ns is not None:
            self.buffer.append(' xmlns="%s"' % (ns, ))
            
    def __build_ns_map(self, ns_map, element):
        for child in element.xml_children:
            if isinstance(child, Element):
                if child.xml_ns not in ns_map:
                    ns_map[child.xml_prefix] = child.xml_ns
                for attr_ns, attr_name in child.xml_attributes:
                    if attr_ns not in ns_map:
                        ns_map[attr_ns] = child.xml_attributes[(attr_ns, attr_name)].xml_prefix

    def __is_known(self, ns_map, prefix, ns):
        if prefix in ns_map and ns_map[prefix] == ns:
            return True

        ns_map[prefix] = ns
        return False

    def __append_text(self, text, as_cdata):
        if as_cdata:
            self.buffer.append('<![CDATA[')
        self.buffer.append(text)
        if as_cdata:
            self.buffer.append(']]>')
                    
    def __serialize_element(self, element, parent_ns_map=None):
        for child in iter(element.xml_children):
            if isinstance(child, basestring):
                child = child.strip().strip('\n').strip('\r\n')
                if not child:
                    continue
                self.__append_text(child, element.as_cdata)
            elif isinstance(child, Element):
                ns_map = {}
                ns_map.update(parent_ns_map or {})
                prefix = ns = name = None
                if child.xml_prefix:
                    prefix = child.xml_prefix
                if child.xml_ns:
                    ns = child.xml_ns
        
                name = child.xml_name
                qname = self.__qname(name, prefix=prefix)
                
                self.buffer.append('<%s' % qname)
                if not self.__is_known(ns_map, prefix, ns):
                    self.__append_namespace(prefix, ns)

                for ns, name, prefix, value in self.__attrs(child):
                    if ns is None:
                        pass
                    elif ns == xd.XML_NAMESPACE:
                        name = 'xml:%s' % name
                    elif ns == xd.XMLNS_NAMESPACE:
                        if not self.__is_known(ns_map, name, value):
                            self.__append_namespace(name, value)
                        continue
                    else:
                        name = '%s:%s' % (prefix, name)
                        if not self.__is_known(ns_map, prefix, ns):
                            self.__append_namespace(prefix, ns)
                        
                    self.buffer.append(' %s=%s' % (name, quoteattr(value)))

                if child.xml_text or child.xml_children:
                    self.buffer.append('>')
                
                    if child.xml_text:
                        self.__append_text(child.xml_text, child.as_cdata)

                    if child.xml_children:
                        self.__serialize_element(child, ns_map)

                    self.buffer.append('</%s>' % (qname, ))
                else:
                    self.buffer.append(' />')
            elif isinstance(child, Comment):
                self.buffer.append('<!--%s-->\n' % (child.data,))
            elif isinstance(child, PI):
                self.buffer.append('<?%s %s?>\n' % (child.target, child.data))


    def serialize(self, document, indent=False, encoding=ENCODING, prefixes=None, omit_declaration=False):
        if not isinstance(document, Document):
            root = document
            document = Document()
            document.xml_children.append(root)

        self.__serialize_element(document)

        if not omit_declaration:
            self.buffer.insert(0, '<?xml version="1.0" encoding="%s"?>%s' % (encoding, os.linesep))
            
        content = ''.join(self.buffer)
        self.buffer = []
        if indent:
            return content.rstrip(os.linesep).encode(encoding)

        return content.encode(encoding)

    def deserialize(self, source, prefixes=None, strict=False):
        doc = None
        if isinstance(source, basestring):
            if os.path.exists(source):
                doc = xdm.parse(source)
            else:
                doc = xdm.parseString(source)
        elif hasattr(source, 'read'):
            doc = xdm.parse(source)

        document = Document()

        self.__deserialize_fragment(doc, document)
        
        if doc:
            try:
                doc.unlink()
            except KeyError:
                pass
            
        return document

import xml.sax as xs
import xml.sax.saxutils as xss
from xml.parsers import expat
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
from time import time

class IncrementalHandler(xss.XMLGenerator):
    def __init__(self, out, encoding=ENCODING):
        xss.XMLGenerator.__init__(self, out, encoding) 
        self._root = Document()
        self._current_el = self._root
        self._current_level = 0
        self._as_cdata = False

    def reset(self):
        if self._root:
            self._root.forget()
            self._root = None
        if self._current_el:
            self._current_el.forget()
            self._current_el = None
        self._root = Document()
        self._current_el = self._root
        self._current_level = 0

    def startDocument(self):
        self._root = Document()
        self._current_el = self._root
        self._current_level = 0
        self._as_cdata = False

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
        #print "$%s%s: %f" % (" " * self._current_level, name, time())
        uri, local_name = name
        prefix = None
        if uri and uri in self._current_context:
            prefix = self._current_context[uri]
        #print "$$%s%s: %f" % (" " * self._current_level, name, time())
        e = Element(local_name, prefix=prefix, namespace=uri, parent=self._current_el)
        #print "$$$%s%s: %f" % (" " * self._current_level, name, time())
        
        for name, value in iter(attrs.items()):
            (namespace, local_name) = name
            qname = attrs.getQNameByName(name)
            prefix = self._split_qname(qname)[0]
            Attribute(local_name, value, prefix, namespace, e)
        #print "$$$$%s%s: %f" % (" " * self._current_level, name, time())
        
        self._current_el = e
        self._current_level = self._current_level + 1
        #print "$$$$$%s%s: %f" % (" " * self._current_level, name, time())
        
    def endElementNS(self, name, qname):
        self._current_level = current_level = self._current_level - 1
        self._current_el = self._current_el.xml_parent

    def characters(self, content):
        self._current_el.as_cdata = self._as_cdata
        if not self._as_cdata and not self._current_el.xml_text:
            self._current_el.xml_text = content
        else:
            self._current_el.xml_children.append(content)
        self._as_cdata = False

    def comment(self, data):
        Comment(data, self._current_el)
        
    def startCDATA(self):
        self._as_cdata = True

    def endCDATA(self):
        pass

    def startDTD(self, name, public_id, system_id):
        pass

    def endDTD(self):
        pass
    
    def doc(self):
        """Returns the root Document instance of the parsed
        document. You have to call the close() method of the
        parser first.
        """
        return self._root

class IncrementalParser(object):
    def __init__(self, out=None, encoding=ENCODING):
        self.parser = xs.make_parser()
        self.parser.setFeature(xs.handler.feature_namespaces, True)
        if not out:
            out = StringIO.StringIO()
        self.out = out
        self.handler = IncrementalHandler(self.out, encoding)
        self.parser.setContentHandler(self.handler)
        self.parser.setProperty(xs.handler.property_lexical_handler, self.handler)

    def feed(self, chunk):
        self.parser.feed(chunk)
        
    def reset(self):
        self.handler.reset()
        self.parser.reset()

class DispatchHandler(IncrementalHandler):
    def __init__(self, out, encoding='UTF-8'):
        IncrementalHandler.__init__(self, out=None, encoding=ENCODING)
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
        self._current_level = current_level = self._current_level - 1
        if not self._current_el:
            return
        current_element = self._current_el
        parent_element = self._current_el.xml_parent

        dispatched = False
        
        if self.enable_element_dispatching:
            pattern = (current_element.xml_ns, current_element.xml_name)
            if pattern in self._element_dispatchers:
                self._element_dispatchers[pattern](current_element)
                dispatched = True
                
        if not dispatched and self.default_dispatcher:
            self.default_dispatcher(current_element)
            
        self._current_el = parent_element

class DispatchParser(object):
    def __init__(self, out=None, encoding=ENCODING):
        self.parser = xs.make_parser()
        self.parser.setFeature(xs.handler.feature_namespaces, True)
        if not out:
            out = StringIO.StringIO()
        self.out = out
        self.handler = DispatchHandler(self.out, encoding)
        self.parser.setContentHandler(self.handler)
        self.parser.setProperty(xs.handler.property_lexical_handler, self.handler)
    
    def feed(self, chunk):
        self.parser.feed(chunk)

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
