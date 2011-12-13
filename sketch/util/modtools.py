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
  Sketch - util - modtools

  desc

"""

import os
import sys
import logging

def add_to_path(path):
  """Adds an entry to sys.path if it's not already there.  This does
  not append it but moves it to the front so that we can be sure it
  is loaded.
  """
  if not os.path.isdir(path):
    raise RuntimeError('Tried to add nonexisting path')

  def _samefile(x, y):
    try:
      return os.path.samefile(x, y)
    except (IOError, OSError):
      return False
  sys.path[:] = [x for x in sys.path if not _samefile(path, x)]
  sys.path.insert(0, path)


def import_string(import_name, silent=False):
  """Imports an object based on a string.  This is useful if you want to
  use import paths as endpoints or something similar.  An import path can
  be specified either in dotted notation (``xml.sax.saxutils.escape``)
  or with a colon as object delimiter (``xml.sax.saxutils:escape``).

  If `silent` is True the return value will be `None` if the import fails.

  from werkzeug.util

  :param import_name: the dotted name for the object to import.
  :param silent: if set to `True` import errors are ignored and
                               `None` is returned instead.
  :return: imported object
  """
  # force the import name to automatically convert to strings
  if isinstance(import_name, unicode):
    import_name = str(import_name)
  try:
    if ':' in import_name:
      module, obj = import_name.split(':', 1)
    elif '.' in import_name:
      module, obj = import_name.rsplit('.', 1)
    else:
      return __import__(import_name)
    # __import__ is not able to handle unicode strings in the fromlist
    # if the module is a package
    if isinstance(obj, unicode):
      obj = obj.encode('utf-8')
    return getattr(__import__(module, None, None, [obj]), obj)
  except (ImportError, AttributeError):
    logging.info('Import Error: Could not load module %s' % import_name)
    if not silent:
      raise

def set_package(self, package_dir):
  """Find all packages in a directory and add them to import paths so that 
  they can be imported by the application
  
  :param package_dir: the package directory
  """
  for filename in os.listdir(package_dir):
    if filename.endswith((".zip", ".egg")):
      sys.path.insert(0, "%s/%s" % (package_dir, filename))


def clear_path(self):
  sys.path = [path for path in sys.path if 'site-packages' not in path]


def iter_modules(path):
  """Iterate over all modules in a package.
  :from: werkzeug._internal
  """
  import os
  import pkgutil
  if hasattr(pkgutil, 'iter_modules'):
    for importer, modname, ispkg in pkgutil.iter_modules(path):
      yield modname, ispkg
    return
  from inspect import getmodulename
  from pydoc import ispackage
  found = set()
  for path in path:
    for filename in os.listdir(path):
      p = os.path.join(path, filename)
      modname = getmodulename(filename)
      if modname and modname != '__init__':
        if modname not in found:
          found.add(modname)
          yield modname, ispackage(modname)


def find_modules(import_path, include_packages=False, recursive=False):
  """Find all the modules below a package.    This can be useful to
  automatically import all views / controllers so that their metaclasses /
  function decorators have a chance to register themselves on the
  application.

  Packages are not returned unless `include_packages` is `True`.  This can
  also recursively list modules but in that case it will import all the
  packages to get the correct load path of that module.

  :param import_name: the dotted name for the package to find child modules.
  :param include_packages: set to `True` if packages should be returned, too.
  :param recursive: set to `True` if recursion should happen.
  :return: generator
  """
  module = import_string(import_path)
  path = getattr(module, '__path__', None)
  if path is None:
    raise ValueError('%r is not a package' % import_path)
  basename = module.__name__ + '.'
  for modname, ispkg in _iter_modules(path):
    modname = basename + modname
    if ispkg:
      if include_packages:
        yield modname
      if recursive:
        for item in find_modules(modname, include_packages, True):
          yield item
    else:
      yield modname


def import_object(name):
  """Imports an object by name.

  import_object('x.y.z') is equivalent to 'from x.y import z'.

  >>> import tornado.escape
  >>> import_object('tornado.escape') is tornado.escape
  True
  >>> import_object('tornado.escape.utf8') is tornado.escape.utf8
  True
  """
  parts = name.split('.')
  obj = __import__('.'.join(parts[:-1]), None, None, [parts[-1]], 0)
  return getattr(obj, parts[-1])

def import_string_two(import_name, silent=False):
  """Imports an object based on a string. If *silent* is True the return
  value will be None if the import fails.

  Simplified version of the function with same name from `Werkzeug`_.

  :param import_name:
    The dotted name for the object to import.
  :param silent:
    If True, import errors are ignored and None is returned instead.
  :returns:
    The imported object.
  """
  import_name = to_utf8(import_name)
  try:
    if '.' in import_name:
      module, obj = import_name.rsplit('.', 1)
      return getattr(__import__(module, None, None, [obj]), obj)
    else:
      return __import__(import_name)
  except (ImportError, AttributeError):
    if not silent:
      raise

