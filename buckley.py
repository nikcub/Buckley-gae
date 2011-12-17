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
  Buckley - buckley.py
  
  Command line client for buckley

  This source file is subject to the new BSD license that is bundled with this 
  package in the file LICENSE.txt. The license is also available online at the 
  URL: <http://nikcub.appspot.com/bsd-license.txt>

  :copyright: Copyright (C) 2011 Nik Cubrilovic and others, see AUTHORS
  :license: new BSD, see LICENSE for more details.
"""

__version__ = '0.2.1'
__author__ = 'Nik Cubrilovic <nikcub@gmail.com>'

import os
import sys

def main():
  print "Buckley v (%s)" % __version__
  init_gae()
  import buckley
  print buckley
  
def init_gae(path=None):
  if not path:
    path = '/usr/local/google_appengine'
  AE_PATH = os.path.abspath(os.path.realpath(path))

  AE_PATHS = [
    AE_PATH,
    os.path.join(AE_PATH, 'lib', 'antlr3'),
    os.path.join(AE_PATH, 'lib', 'fancy_urllib'),
    os.path.join(AE_PATH, 'lib', 'django'),
    os.path.join(AE_PATH, 'lib', 'ipaddr'),
    os.path.join(AE_PATH, 'lib', 'webob'),
    os.path.join(AE_PATH, 'lib', 'yaml', 'lib'),
  ]
  
  sys.path = sys.path + AE_PATHS

if __name__ == '__main__':
  main()