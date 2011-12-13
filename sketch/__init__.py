#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
  Sketch
  =======

  A simple and portable python web application framework for Google App Engine

  :homepage: <http://bitbucket.org/nik/sketch>
  :author: Nik Cubrilovic <nikcub@gmail.com>
  :copyright: (c) 2011 by Nik Cubrilovic and others, see AUTHORS for more details.
  :license: 3-clause BSD, see LICENSE for more details.
"""

__version__ = '0.1'
__author__ = "Nik Cubrilovic <nikcub@gmail.com>"
__license__ = "BSD 3-clause"

import sys
import os
import logging

VENDOR_DIR = os.path.join(os.path.dirname(__file__), 'vendor')
if os.path.isdir(VENDOR_DIR):
  sys.path.insert(0, VENDOR_DIR)
else:
  logging.exception("Error: %s" % VENDOR_DIR)

import exception
import util
from templating import jinja
import db

from .webapp import Request, Response, RequestHandler, RedirectHandler
from .router import BaseRoute, SimpleRoute, Route, Router
from .config import Config
from .controllers import BaseController, AdminController
from .session import Session
from .application import Application

