#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=2:sw=2:expandtab
#
# Copyright (c) 2010-2011, Nik Cubrilovic. All rights reserved.
#
# <nikcub@gmail.com> <http://nikcub.appspot.com>  
#
# Licensed under a BSD license. You may obtain a copy of the License at
#
#     http://nikcub.appspot.com/bsd-license
#
"""
  Sketch - gae.py

  Google App Engine utils

  This source file is subject to the new BSD license that is bundled with this 
  package in the file LICENSE.txt. The license is also available online at the 
  URL: <http://nikcub.appspot.com/bsd-license.txt>

  :copyright: Copyright (C) 2011 Nik Cubrilovic and others, see AUTHORS
  :license: new BSD, see LICENSE for more details.
"""

import os
import sys

def setup_gae_paths(gae_base_dir=None):
  if not gae_base_dir:
    gae_base_dir = '/Applications/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine'

  if not os.path.isdir(gae_base_dir):
    return False

  ae_path = os.path.abspath(os.path.realpath(gae_base_dir))

  AE_PATHS = [
    ae_path,
    os.path.join(ae_path, 'lib', 'antlr3'),
    os.path.join(ae_path, 'lib', 'django'),
    os.path.join(ae_path, 'lib', 'fancy_urllib'),
    os.path.join(ae_path, 'lib', 'ipaddr'),
    os.path.join(ae_path, 'lib', 'webob'),
    os.path.join(ae_path, 'lib', 'yaml', 'lib'),
  ]
  
  sys.path = sys.path + AE_PATHS
  return True

def enable_ctypes():
  """Enable ctypes in Google App Engine development server
  
  """
  return enable_dev_module(['_ctypes', 'gestalt'])

def enable_dev_module(modules=[]):
  """In Google App Engine development server whitelist a C module or other module
  that has been disabled to assist with local development.
  
  for eg. Enable _ctypes so that Jinja rendering error messages are sane
  Should only run if on development server.
  
  :param modules: Modules to enable in dev server
  :return List: List of modules that have been whitelisted 
  """
  try:
    from google.appengine.tools.dev_appserver import HardenedModulesHook
  except ImportError:
    return False
  if type(modules) == type([]) and len(modules) > 0:
    HardenedModulesHook._WHITE_LIST_C_MODULES += modules
    return HardenedModulesHook._WHITE_LIST_C_MODULES
  return False
  