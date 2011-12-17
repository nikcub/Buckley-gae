#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=2:sw=2:expandtab
#
# Copyright (c) 2011, Nik Cubrilovic. All rights reserved.
#
# <nikcub@gmail.com> <http://nikcub.appspot.com>  
#
# Licensed under a BSD license. You may obtain a copy of the License at
#
#     http://nikcub.appspot.com/bsd-license
#
"""
  Sketch - TM_FILENAME}

  desc

"""
class HtmlEscapeCache(dict):
  def __missing__(self, c):
    s = "&#" + str(ord(c)) + ";"
    self[c] = s
    return s
            
WHITELIST = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
 
def escape_engine(s, on_whitelist, on_ascii, on_unicode):
    pieces = []
    for char in s:
        if char in WHITELIST:
            pieces.append(on_whitelist(char))
        elif ord(char) < 256:
            pieces.append(on_ascii(char))
        else:
            pieces.append(on_unicode(char))
    return "".join(pieces)
 
def html1(s):
    """
   Escapes a string for inclusion into tag contents in HTML.
 
   Do *not* use for including a string into an HTML attribute; use
   escape.attr() for that.
   """
 
    # Ensure we deal with strings
    s = unicode(s)
 
    escaped = escape_engine(s,
        on_whitelist = lambda c: c,
        on_ascii = lambda c: "&#%02x;" % ord(c),
        on_unicode = lambda c: "&#%02x;" % ord(c),
    )
 
    return UNSAFE_bless(escaped) # Now it’s escaped, so should be safe

def force_int(val, default=False):
  if isinstance(val, (int)):
    return val
  try:
    val = int(val)
    return val
  except TypeError:
    return default
    
def python_websafe(text):
  return text.replace('&', "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def python_websafe_json(text):
  return text.replace('&', "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def escape(s, quote=False):
  """Replace special characters "&", "<" and ">" to HTML-safe sequences.  If
  the optional flag `quote` is `True`, the quotation mark character (") is
  also translated.

  There is a special handling for `None` which escapes to an empty string.

  :param s: the string to escape.
  :param quote: set to true to also escape double quotes.
  """
  if s is None:
    return ''
  elif hasattr(s, '__html__'):
    return s.__html__()
  elif not isinstance(s, basestring):
    s = unicode(s)
  s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
  if quote:
    s = s.replace('"', "&quot;")
  return s