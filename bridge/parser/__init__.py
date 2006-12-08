#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

__all__ = ['get_first_available_parser', 'encode_entity']

# stolen from ElementTree
_escape = re.compile(eval(r'u"[&<>\"\u0080-\uffff]+"'))

def encode_entity(text, pattern=_escape):
    # map reserved and non-ascii characters to numerical entities
    def escape_entities(m):
        out = []
        for char in m.group():
            out.append("&#%d;" % ord(char))
        return ''.join(out)
    return pattern.sub(escape_entities, text)

del _escape

def get_first_available_parser():
    """
    Helper function which will return the first available parser
    on your system.
    """
    try:
        from bridge.parser.bridge_amara import Parser
        return Parser
    except ImportError:
        pass

    try:
        from bridge.parser.bridge_lxml import Parser
        return Parser
    except ImportError:
        pass
    
    try:
        from bridge.parser.bridge_elementtree import Parser
        return Parser
    except ImportError:
        pass

    try:
        from bridge.parser.bridge_dotnet import Parser
        return Parser
    except ImportError:
        pass
    
    from bridge.parser.bridge_default import Parser
    return Parser
