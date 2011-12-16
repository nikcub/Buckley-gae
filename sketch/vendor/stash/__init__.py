#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:expandtab
"""
  stash

  A python object persistance and caching module

  This source file is subject to the new BSD license that is bundled with this
  package in the file LICENSE.txt. The license is also available online at the
  URL: <http://nikcub.appspot.com/bsd-license.txt>

  :copyright: Copyright (C) 2011 Nik Cubrilovic and others, see AUTHORS
  :license: new BSD, see LICENSE for more details.
"""

import os
import sys
import logging
import time
import functools
import inspect
from types import TypeType

try:
  import hashlib
except ImportError:
  raise Exception('python 2.5+ required')

try:
  import json
except ImportError:
  # python <2.6, simplejson is now a requirement
  try:
    import simplejson as json
  except ImportError:
    try:
      from django.utils import simplejson
    except ImportError:
      logging.exception('stash requires simplejson')
      raise Exception('json is required')

try:
  from google.appengine.api import memcache
  from google.appengine.ext import db
  GAE = True

  class _StashGAEStore(db.Model):
    skey = db.StringProperty(required = True)
    sval = db.TextProperty()
    sttl = db.IntegerProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    expired = db.BooleanProperty(default = False)

except ImportError:
  GAE = False
  db = {}
  try:
    import memcache
    LOCAL_MEMCACHE = True
  except ImportError:
    LOCAL_MEMCACHE = False

__version__ = '0.0.1'
__author__ = 'Nik Cubrilovic <nikcub@gmail.com>'


#---------------------------------------------------------------------------
#   Misc Module Data
#---------------------------------------------------------------------------

GLOBAL_VAR_STORE = {}

_startTime = time.time()

counter = 0

def increment():
  global counter
  counter += 1
  return counter
    
#---------------------------------------------------------------------------
#   Module Exceptions
#---------------------------------------------------------------------------

class StorageHandlerException(Exception): pass

class FileCacheException(Exception): pass


#---------------------------------------------------------------------------
#   Storage Handlers
#---------------------------------------------------------------------------

class StorageHandler(object):

  options = None

  def __init__(self, options = None):
    """docstring for __init__"""
    if options:
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

class NullHandler(StorageHandler):
  """docstring for NullHandler"""
  def __init__(self, options):
    return None

  def wrap(self, func):
    return func

class GlobalVarHandler(StorageHandler):

  def __init__(self, options):
    pass

  def get(self, key):
    if GLOBAL_VAR_STORE.has_attr('key'):
      return GLOBAL_VAR_STORE[key]
    return None

  def set(self, key, value):
    GLOBAL_VAR_STORE[key] = value
    return True

class MemcacheHandler(StorageHandler):

  _config_default = {
    'host': ':127.0.0.1:11211'
  }
  def __init__(self, options):
    pass

  def fname(self):
    """docstring for fname"""
    pass

  def fname(self):
    """docstring for fname"""
    pass


class FileStorage(StorageHandler):
  """docstring for FileCacheHandler"""

  cache_folder = None
  file_extension = 'txt'

  def __init__(self, **kwargs):
    """Initialize FileStorageHandler"""

    if kwargs.get('cache_dir'):
      self._setup_cache_folder(kwargs.get('cache_dir'))

  def _setup_cache_folder(self, cache_folder = None):
    """Set the cache folder to store the cache to by either taking user supplied
    argument or setting to a temporary directory"""
    if cache_folder:
      cache_folder = self._parse_cache_folder(cache_folder)
    else:
      import tempfile
      cache_folder = tempfile.gettempdir()

    self.cache_folder = cache_folder

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
      logging.info("Writing value to key %s" % key)
      logging.info(value)

      f = open(file_path, 'w')
      f.write(value)
    except Exception, e:
      logging.error("Exception: could not write file %s" % (file_path))
      logging.exception(e)
      return False
    return True



class GAEMemcacheHandler(StorageHandler):
  """docstring for GAEMemcacheHandler"""

  ttl = 60 * 60 * 24 * 4

  def get(self, key):
    """docstring for get"""
    return memcache.get(key)

  def set(self, key, value):
    """docstring for set"""
    return memcache.set(key, value, self.ttl)

  def delete(self, key):
    return memcache.delete(key)


# TODO  implement datastore cache
class GAEDatastoreHandler(StorageHandler):

  def get(self, key):
    q = db.GqlQuery("SELECT * FROM _StashGAEStore WHERE skey = :1", key)
    if not q:
      return None
    return json.loads(q.sval)


  def set(self, key, value):
    val = json.dumps(value)
    r = _StashGAEStore(
      skey = key,
      sval = val,
    )
    r.put()

  def delete(self, key):
    return None

#---------------------------------------------------------------------------
#   Serializers
#---------------------------------------------------------------------------

class Serializer(object):

  def __init__(self):
    """docstring for __init__"""
    pass

  def dumps(self):
    """docstring for dumps"""
    pass

  def load(self, str):
    pass

#---------------------------------------------------------------------------
#   Stash Object
#---------------------------------------------------------------------------

class Stash(object):
  """Base and root stash object"""

  def __init__(self, **kwargs):
    """Initialize"""
    self.handlers = []
    handler = kwargs.pop('handler', False)
    if handler:
      self._add_handler(handler)

  def _add_handler(self, handler, **kwargs):
    if type(handler) == str and handler in globals():
      handler = globals()[handler]
    if not issubclass(handler, StorageHandler):
     raise StorageHandlerException, "%s is not of type StorageHandler" % handler
    ins = handler(**kwargs)
    self.handlers.append(ins)

  def get(self, key):
    for h in self.handlers:
      # logging.info("Stash: get(%s) with %s" % (key, h))
      r = h.get(key)
      if r:
        return r
      return None

  def set(self, key, val):
    for h in self.handlers:
      # logging.info("Stash: set(%s, %s) with %s" % (key, val, h))
      h.set(key, val)

  def delete(self, key):
    for h in self.handlers:
      # logging.info("Stash: del(%s) with %s" % (key, h))
      h.delete(key)

_stash = Stash()

#---------------------------------------------------------------------------
#   Handler Class
#---------------------------------------------------------------------------

def autoConf(**kwargs):
  """Attepts to auto configure a core Stash cache object based on capabilities
  discovered through imports and default attempts. Detect if we are on AppEngine
  either dev or production, detect if memcache is present and active, etc.

  Falls back on providing a FileStorage handler and a single root Stash
  """
  if GAE:
    _stash._add_handler(GAEMemcacheHandler)
    _stash._add_handler(GAEDatastoreHandler)
  else:
    _stash._add_handler(FileStorage)
    logging.info('Stash: not on google appengine')

  # OLD VERSION - single handler only support
  #
  # if len(_stash.handlers) == 0:
  #   handler = kwargs.get('handler')
  #
  # else:
  #   if GAE:
  #     return GAEMemcacheHandler()
  #   if LOCAL_MEMCACHE and kwargs.get('memcache_server', False):
  #     return MemcacheHandler()
  #   return FileStorage()



def handler(**kwargs):
  # Factory for returning a handler based on either passed options or by
  # taking a best guess based on imports that worked or failed (ie. GAE vs not)



  # If we were not passed a handler, lets take a guess

  if GAE:
    return GAEMemcacheHandler()
  if LOCAL_MEMCACHE and kwargs.get('memcache_server', False):
    return MemcacheHandler()
  return FileStorage()

# cache decorator
class Cache(object):
  """
    cache decorator
  """
  
  def __init__(self, func):
    self.func = func
    logging.info(func.__name__)
    self.cache = {}
    
  def __call__(self, *args):
    try:
      logging.info('cache:')
      logging.info(args)
      val = self.func(*args)
      return val
    except:
      return None
      return self.func(*args)
  
  def __repr__(self):
    return self.func.__doc__
  
  
  def __get__(self, obj, objtype):
    return functools.partial(self.__call__, obj)


def get(key):
  if len(_stash.handlers) == 0:
    autoConf()
  return _stash.get(key)

def set(key, val, ttl = 60 * 60 * 24):
  if len(_stash.handlers) == 0:
    autoConf()
  return _stash.set(key, val)

def delete(key):
  if len(_stash.handlers) == 0:
    autoConf()
  return _stash.delete(key)

