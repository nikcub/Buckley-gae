#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import sketch

try:
  import conf
except ImportError:
  conf = {}

from .reqhandlers import BaseController, AdminController
from .routes import routes

app = sketch.Application(config=conf, routes=routes)