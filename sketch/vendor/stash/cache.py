#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:expandtab
"""
  py-diffbot - cache.py

  Caching handlers with support for file, GAE memcache and python memcache

  This source file is subject to the new BSD license that is bundled with this
  package in the file LICENSE.txt. The license is also available online at the
  URL: <http://nikcub.appspot.com/bsd-license.txt>

  :copyright: Copyright (C) 2011 Nik Cubrilovic and others, see AUTHORS
  :license: new BSD, see LICENSE for more details.
"""

__version__ = '0.0.1'
__author__ = 'Nik Cubrilovic <nikcub@gmail.com>'

GLOBAL_VAR_STORE = {}

import os
import sys
import logging
import hashlib
# import pickle
try:
  import json
except ImportError:
  import simplejson as json

from types import TypeType

try:
  from google.appengine.api import memcache
  GAE = True
except ImportError:
  GAE = False
  try:
    import memcache
    LOCAL_MEMCACHE = True
  except ImportError:
    LOCAL_MEMCACHE = False

#---------------------------------------------------------------------------
#   Handler Classes
#---------------------------------------------------------------------------

class CacheHandlerException(Exception): pass

class FileCacheException(Exception): pass

class CacheHandler(object):

  options = None

  def __init__(self, options):
    """docstring for __init__"""
    self.options = options

  def wrap(self, func):
    """docstring for fname"""
    def cache(*args, **kwargs):
      logging.info("Called fetch function with")
      key = self.hash(args[0])
      cache_store = self.get(key)
      if cache_store:
        return cache_store
      val = func(*args, **kwargs)
      if val:
        self.set(key, val)
      return val
    return cache

  def hash(self, key_name):
    return hashlib.sha1(key_name).hexdigest()

class NullHandler(CacheHandler):
  """docstring for NullHandler"""
  def __init__(self, options):
    return None

  def wrap(self, func):
    return func

class GlobalVarHandler(CacheHandler):

  def __init__(self, options):
    pass

  def get(self, key):
    if GLOBAL_VAR_STORE.has_attr('key'):
      return GLOBAL_VAR_STORE[key]
    return None

  def set(self, key, value):
    GLOBAL_VAR_STORE[key] = value
    return True

class MemcacheHandler(CacheHandler):

  def fname(self):
    """docstring for fname"""
    pass

  def fname(self):
    """docstring for fname"""
    pass


class GAEMemcacheHandler(CacheHandler):
  """docstring for GAEMemcacheHandler"""

  ttl = 60 * 60 * 24 * 4

  def get(self, key):
    """docstring for get"""
    return memcache.get(key)

  def set(self, key, value):
    """docstring for set"""
    return memcache.set(key, value, self.ttl)


class FileCacheHandler(CacheHandler):
  """docstring for FileCacheHandler"""

  cache_folder = None

  def __init__(self, **kwargs):
    if kwargs.get('cache_dir'):
      self._setup_cache_folder(kwargs.get('cache_dir'))

  def _setup_cache_folder(self, cache_folder = None):
    """Set the cache folder to store the cache to by either taking user supplied
    argument or setting to a temporary directory"""
    if cache_folder:
      cache_folder = self._parse_cache_folder(cache_folder)
    else:
      try:
        import tempfile
        cache_folder = tempfile.gettempdir()
        self.cache_folder = cache_folder
      except Exception:
        self.cache_folder = '/tmp'
        # cache_folder = tempfile.TemporaryFile


  def _parse_cache_folder(self, cache_folder):
    """Take the user supplied cache folder argument and sanitize the path, check
    that it is writable and return the value.
    """

    # If it is a relative path, prepend current directory
    if not cache_folder.startswith('/'):
      cache_folder = os.path.join(os.path.dirname(__file__), cache_folder)

    # TODO check that it is writable
    if not os.path.isdir(cache_folder):
      raise FileCacheException("Not a valid cache folder: %s (got: %s)" % (cf, os.path.isdir(cf)))

    return cache_folder

  def set_cache_dir(self, cache_folder):
    """Set the cache directory to store cache to"""
    return self._setup_cache_folder(cache_folder)

  def get_filepath(self, key):
    if not self.cache_folder:
      self._setup_cache_folder()
    return os.path.join(self.cache_folder, "%s.txt" % key)

  def get(self, key):
    file_path = self.get_filepath(key)

    if not os.path.isfile(file_path):
      return None

    logging.info("CACHE HIT (%s)" % file_path)

    val = open(file_path).read()

    try:
      val = json.loads(val)
    except ValueError:
      pass
    return val

  def set(self, key, value, ttl = 60 * 60):
    # TODO set the key based on timeout
    # ie. some sort of key hash taking the filename along with a time that will
    # only make the key valid again if looked up in that time
    file_path = self.get_filepath(key)

    if type(value) != str:
      value = json.dumps(value)

    try:
      # logging.info("Writing value to key %s" % key)
      # logging.info(value)

      f = open(file_path, 'r')
      f.write(value)
    except Exception, e:
      # logging.error("(cache.py) Exception: could not write file %s" % (file_path))
      # logging.exception(e)
      return False
    return True


#---------------------------------------------------------------------------
#   Handler Class
#---------------------------------------------------------------------------



def handler(**kwargs):
  # Factory for returning a handler based on either passed options or by
  # taking a best guess based on imports that worked or failed (ie. GAE vs not)
  handler = kwargs.pop('handler', False)
  if handler:
    if type(handler) == str and handler in globals():
      handler = globals()[handler]
    if not issubclass(handler, CacheHandler):
     raise CacheHandlerException, "%s is not of type CacheHandler" % handler
    ins = handler(**kwargs)
    return ins

  # If we were not passed a handler, lets take a guess

  if GAE:
    return GAEMemcacheHandler()
  if LOCAL_MEMCACHE and kwargs.get('memcache_server', False):
    return MemcacheHandler()
  return FileCacheHandler()
