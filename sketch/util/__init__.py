#!/usr/bin/env python
#
# Copyright (c) 2010-2011, Nik Cubrilovic. All rights reserved.
# <nikcub@gmail.com> <http://nikcub.appspot.com>  
#

"""Sketch Utility methods


  TODO  break up into packages  
"""

from .object import hasmethod, hasvar, getmethattr, assure_obj_child_dict, AccessibleDict, AttrDict
from .security import hash_password, gen_sha1, gen_pbkdf1, gen_salt, gen_password, file_hash, gen_password_old
from .gae import setup_gae_paths
from .dateformat import utc_mktime, datetime_to_timestamp, HTTPDate
from .unicode import to_unicode as force_unicode, to_utf8 as force_utf8
from .http import extract_dataurl

def format_string(string, context):
  """String-template format a string:

  >>> format_string('$foo and ${foo}s', dict(foo=42))
  '42 and 42s'

  This does not do any attribute lookup etc.  For more advanced string
  formattings have a look at the `werkzeug.template` module.

  :from: werkzeug.util
  :param string: the format string.
  :param context: a dict with the variables to insert.
  """
  def lookup_arg(match):
    x = context[match.group(1) or match.group(2)]
    if not isinstance(x, basestring):
      x = type(string)(x)
    return x
  return _format_re.sub(lookup_arg, string)

