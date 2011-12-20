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

def autoretry_datastore_timeouts(attempts=5.0, interval=0.1, exponent=2.0):
    """
    Copyright (C)  2009  twitter.com/rcb
    
    Permission is hereby granted, free of charge, to any person
    obtaining a copy of this software and associated documentation
    files (the "Software"), to deal in the Software without
    restriction, including without limitation the rights to use,
    copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following
    conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
    OTHER DEALINGS IN THE SOFTWARE.
    
    ======================================================================
    
    This function wraps the AppEngine Datastore API to autoretry 
    datastore timeouts at the lowest accessible level.  

    The benefits of this approach are:

    1. Small Footprint:  Does not monkey with Model internals 
                         which may break in future releases.
    2. Max Performance:  Retrying at this lowest level means 
                         serialization and key formatting is not 
                         needlessly repeated on each retry.
    At initialization time, execute this:
    
    >>> autoretry_datastore_timeouts()
    
    Should only be called once, subsequent calls have no effect.
    
    >>> autoretry_datastore_timeouts() # no effect
    
    Default (5) attempts: .1, .2, .4, .8, 1.6 seconds
    
    Parameters can each be specified as floats.
    
    :param attempts: maximum number of times to retry.
    :param interval: base seconds to sleep between retries.
    :param exponent: rate of exponential back-off.
    """
    
    import time, logging
    from google.appengine.api import apiproxy_stub_map
    from google.appengine.runtime import apiproxy_errors
    from google.appengine.datastore import datastore_pb
    
    attempts = float(attempts)
    interval = float(interval)
    exponent = float(exponent)
    wrapped = apiproxy_stub_map.MakeSyncCall
    errors = {datastore_pb.Error.TIMEOUT:'Timeout',
        datastore_pb.Error.CONCURRENT_TRANSACTION:'TransactionFailedError'}
    
    def wrapper(*args, **kwargs):
        count = 0.0
        while True:
            try:
                return wrapped(*args, **kwargs)
            except apiproxy_errors.ApplicationError, err:
                errno = err.application_error
                if errno not in errors: raise
                sleep = (exponent ** count) * interval
                count += 1.0
                if count > attempts: raise
                msg = "Datastore %s: retry #%d in %s seconds.\n%s"
                vals = ''
                if count == 1.0:
                    vals = '\n'.join([str(a) for a in args])
                logging.warning(msg % (errors[errno], count, sleep, vals))
                time.sleep(sleep)

    setattr(wrapper, '_autoretry_datastore_timeouts', False)
    if getattr(wrapped, '_autoretry_datastore_timeouts', True):
        apiproxy_stub_map.MakeSyncCall = wrapper