#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
from bridge.parser.incremental import create_parser
from bridge import Document, ENCODING
from bridge.parser.bridge_default import Parser as default_parser

__all__ = ['Parser']

class Parser(object):
    def serialize(self, document, indent=False, encoding=ENCODING, prefixes=None, omit_declaration=False):
        # For the serialization we use the default parser which instead of duplicating the code here
        parser = default_parser()
        return parser.serialize(document, indent, encoding, prefixes, omit_declaration)

    def deserialize(self, source, prefixes=None, strict=False, as_attribute=None, as_list=None,
                    as_attribute_of_element=None):
        doc = source
        if isinstance(source, basestring):
            if os.path.exists(source):
                doc = file(source, 'rb').read()
        elif hasattr(source, 'read'):
            doc = source.read()

        _parser, _handler, _output = create_parser()
        _handler.disable_dispatching()
        _handler.as_attribute = as_attribute or {}
        _handler.as_list = as_list or {}
        _handler.as_attribute_of_element = as_attribute_of_element or {}
        _parser.feed(doc)
        _parser.close()
        _output.close()

        return _handler.doc()
